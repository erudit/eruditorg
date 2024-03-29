import datetime as dt
from typing import Sequence

import structlog
import re

from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.db import transaction
from eruditarticle.utils import remove_xml_namespaces
import lxml.etree as et
import sentry_sdk

from ...conf import settings as erudit_settings
from ...fedora.objects import JournalDigitalObject
from ...fedora.objects import PublicationDigitalObject
from ...fedora.utils import get_pids
from ...fedora.utils import (
    get_unimported_issues_pids,
    get_journal_issue_pids_to_sync,
    localidentifier_from_pid,
)
from ...fedora.repository import api
from ...models import Collection
from ...models import Issue
from ...models import Journal

logger = structlog.getLogger(__name__)


class Command(BaseCommand):
    """Imports journal objects from a Fedora Commons repository.

    The command is able to import a journal object and its issues from
    a Fedora Commons repository. To do so, the command assumes that some journal collections
    (:py:class`Collection <erudit.models.core.Collection>` instances) are already created in the
    database.

    By default the command will try to import the journal objects that have been modified since the
    latest journal modification date stored in the database. If no journals can be found in the
    database or the `full` switch is passed, the command will perform a full import.

    If an `issue_pid` argument is passed, then the command will try and import this particular
    issue.

    If the `import_missing` switch is passed, then the command will compare the list of issues
    present in the database with the list of issues present in Fedora. It will then import
    all those issues that are in Fedora but not in the database.

    If a `journal_pid` argument is passed, a single journal will be handled. Using Fedora data,
    it will be created in the database if it doesn't exist, or updated if it already exists. Every
    issue of that journal missing from the database will then be imported.
    """

    help = "Import journals from Fedora"

    modification_date = None

    def add_arguments(self, parser):
        parser.add_argument(
            "--full", action="store_true", dest="full", default=False, help="Perform a full import."
        )

        parser.add_argument(
            "--pid", action="store", dest="journal_pid", help="Journal PID to manually import."
        )

        parser.add_argument(
            "--issue-pid", action="store", dest="issue_pid", help="Issue PID to manually import."
        )

        parser.add_argument(
            "--import-missing",
            action="store_true",
            dest="import_missing",
            help="Import missing issues.",
        )
        parser.add_argument(
            "--mdate",
            action="store",
            dest="mdate",
            help="Modification date to use to retrieve journals to import (iso format).",
        )

    def handle(self, *args, **options):
        full_import = options.get("full", False)
        journal_pid = options.get("journal_pid", None)
        modification_date = options.get("mdate", None)
        self.journal_precedence_relations = []
        issue_pid = options.get("issue_pid", None)
        import_missing = options.get("import_missing", None)
        logger.info("import.started", **options)

        with sentry_sdk.configure_scope() as scope:
            scope.fingerprint = ["import-journals-from-fedora"]

        # Handles a potential modification date option
        try:
            if modification_date is not None:
                self.modification_date = dt.datetime.strptime(modification_date, "%Y-%m-%d").date()
        except ValueError:
            logger.error(
                "invalid_argument",
                msg="A modification date has been specified, but it cannot be parsed by strptime",
                modification_date=modification_date,
            )
            return

        if issue_pid or import_missing:
            if issue_pid:
                logger.info("import.started", issue_pid=issue_pid)
                unimported_issues_pids = [issue_pid]
                if not re.match(r"^\w+:\w+\.\w+\.\w+$", issue_pid):
                    raise CommandError(f"Invalid argument issue_pid: " f"{issue_pid} is not valid")
            else:
                unimported_issues_pids = get_unimported_issues_pids()
                logger.info(
                    "import.started",
                    issues_count=len(unimported_issues_pids),
                    msg="Importing missing issues",
                )
            self.import_issues(unimported_issues_pids)
            return

        # Imports a journal PID manually
        if journal_pid:
            logger.info("journal.import.start", journal_pid=journal_pid)
            if not re.match(r"^\w+:\w+\.\w+$", journal_pid):
                raise CommandError(f"Invalid argument journal_pid: " f"{journal_pid} is not valid")

            collection_localidentifier = journal_pid.split(":")[1].split(".")[0]
            try:
                collection = Collection.objects.get(localidentifier=collection_localidentifier)
            except Collection.DoesNotExist:
                raise CommandError(
                    f"Invalid argument: " f"collection {collection_localidentifier} doesn't exist"
                )

            self.import_journal(journal_pid, collection)
            self.import_journal_precedences(self.journal_precedence_relations)
            return

        # Default path: imports each collection
        journal_count, journal_errored_count = 0, 0
        issue_count, issue_errored_count = 0, 0
        for collection_config in erudit_settings.JOURNAL_PROVIDERS.get("fedora"):
            collection_code = collection_config.get("collection_code")
            try:
                collection = Collection.objects.get(code=collection_code)
            except Collection.DoesNotExist:
                collection = Collection.objects.create(
                    code=collection_code,
                    name=collection_config.get("collection_title"),
                    localidentifier=collection_config.get("localidentifier"),
                )
            _jc, _jec, _ic, _iec = self.import_collection(collection, full_import)
            journal_count += _jc
            journal_errored_count += _jec
            issue_count += _ic
            issue_errored_count += _iec

        logger.info(
            "import.finished",
            journal_count=journal_count,
            journal_errored=journal_errored_count,
            issue_count=issue_count,
            issue_errored_count=issue_errored_count,
        )

    def import_collection(self, collection: Collection, full_import: bool):
        """ Imports all the journals of a specific collection. """

        self.journal_precedence_relations = []

        latest_update_date = self.modification_date
        if not full_import and latest_update_date is None:
            # Tries to fetch the date of the Journal instance with the more recent update date.
            latest_journal_update = Journal.objects.order_by("-fedora_updated").first()
            latest_update_date = (
                latest_journal_update.fedora_updated.date() if latest_journal_update else None
            )

        latest_issue_update_date = self.modification_date
        if not full_import and latest_issue_update_date is None:
            # Tries to fetch the date of the Issue instance with the more recent update date.
            latest_issue_update = Issue.objects.order_by("-fedora_updated").first()
            latest_issue_update_date = (
                latest_issue_update.fedora_updated.date() if latest_issue_update else None
            )

        # STEP 1: fetches the PIDs of the journals that will be imported
        # --

        base_fedora_query = "pid~erudit:{collectionid}.* label='Series Erudit'".format(
            collectionid=collection.localidentifier
        )
        if full_import or latest_update_date is None:
            modification_date = None
            full_import = True
            journal_pids = get_pids(base_fedora_query)
        else:
            modification_date = latest_update_date.isoformat()
            full_import = False
            # Fetches the PIDs of all the journals that have been update since the latest
            # modification date.
            journal_pids = get_pids(
                base_fedora_query + " mdate>{}".format(latest_update_date.isoformat())
            )
        logger.info(
            "import.started",
            collection_code=collection.code,
            full_import=full_import,
            modification_date=modification_date,
        )

        # STEP 2: import each journal using its PID
        # --

        issue_pids_to_sync = set()
        journal_count, journal_errored_count = 0, 0
        for jpid in journal_pids:
            try:
                self.import_journal(jpid, collection, False)
                journal = Journal.objects.get(localidentifier=localidentifier_from_pid(jpid))
                journal_erudit_object = journal.get_erudit_object()
                issue_pids_to_sync.update(
                    get_journal_issue_pids_to_sync(
                        journal,
                        journal_erudit_object.get_published_issues_pids(),
                    )
                )
            except Exception as e:
                journal_errored_count += 1
                logger.exception(
                    "journal.import.error",
                    journal_pid=jpid,
                    msg=repr(e),
                )
            else:
                journal_count += 1

        # STEP 3: associates Journal instances with other each other
        # --

        self.import_journal_precedences(self.journal_precedence_relations)

        # STEP 4: fetches the PIDs of the issues that will be imported
        # --
        issue_fedora_query = "pid~erudit:{collectionid}.*.* label='Publication Erudit'".format(
            collectionid=collection.localidentifier
        )
        if full_import or latest_update_date is None:
            issue_pids = get_pids(issue_fedora_query)
        else:
            # Fetches the PIDs of all the issues that have been update since the latest
            # modification date.
            issue_pids = get_pids(
                issue_fedora_query + " mdate>{}".format(latest_issue_update_date.isoformat())
            )

        # STEP 5: import each issue using its PID
        # --

        issue_count, issue_errored_count = 0, 0

        for ipid in set(issue_pids) | issue_pids_to_sync:
            journal_localidentifier = ipid.split(":")[1].split(".")[1]
            try:
                journal = Journal.objects.get(localidentifier=journal_localidentifier)
            except Journal.DoesNotExist:
                issue_errored_count += 1
                logger.exception(
                    "issue.import.error",
                    msg="Journal does not exist",
                    issue_pid=ipid,
                    journal_pid=journal_localidentifier,
                )
            else:
                try:
                    self._import_issue(ipid, journal)
                except Exception as e:
                    issue_errored_count += 1
                    logger.exception(
                        "issue.import.error",
                        issue_pid=ipid,
                        msg=repr(e),
                    )
                else:
                    issue_count += 1

        return journal_count, journal_errored_count, issue_count, issue_errored_count

    def import_journal_precedences(self, precedences_relations):
        """ Associates previous/next Journal instances with each journal. """
        for r in precedences_relations:
            localid = r["journal_localid"]
            previous_localid = r["previous_localid"]
            next_localid = r["next_localid"]
            if previous_localid is None and next_localid is None:
                continue
            try:
                j = Journal.objects.get(localidentifier=localid)
                previous_journal = (
                    Journal.objects.get(localidentifier=previous_localid)
                    if previous_localid
                    else None
                )
                next_journal = (
                    Journal.objects.get(localidentifier=next_localid) if next_localid else None
                )
            except Journal.DoesNotExist:
                logger.exception(
                    "journal.import.error",
                    journal_pid=localid,
                    msg="Unable to import precedences for journal",
                )
            else:
                j.previous_journal = previous_journal
                j.next_journal = next_journal
                j.save()

    @transaction.atomic
    def import_journal(self, journal_pid, collection, import_issues=True):
        """ Imports a journal using its PID. """
        logger.info("journal.import.start", journal=journal_pid)
        # STEP 1: fetches the full Journal fedora object
        # --

        fedora_journal = JournalDigitalObject(api, journal_pid)
        if not fedora_journal.exists:
            msg = f'The journal with PID "{journal_pid}" seems to be inexistant in Fedora'
            logger.exception(
                "journal.import.error",
                msg=msg,
            )
            return  # We return here in order to try to import the other journals of the collection

        # STEP 2: creates or updates the journal object
        # --
        oaiset_info_tree = (
            remove_xml_namespaces(et.fromstring(fedora_journal.oaiset_info.content.serialize()))
            if fedora_journal.oaiset_info.exists
            else None
        )
        rels_ext_tree = (
            remove_xml_namespaces(et.fromstring(fedora_journal.rels_ext.content.serialize()))
            if fedora_journal.rels_ext.exists
            else None
        )
        publications_tree = remove_xml_namespaces(
            et.fromstring(fedora_journal.publications.content.serialize())
        )
        # Set the proper values on the Journal instance
        xml_name = (
            oaiset_info_tree.find(".//title")
            if oaiset_info_tree
            else rels_ext_tree.find(".//setName")
        )

        # Fetches the Journal instance... or creates a new one
        journal_localidentifier = localidentifier_from_pid(journal_pid)
        xml_issue = publications_tree.xpath(
            './/numero[starts-with(@pid, "{0}")]'.format(journal_pid)
        )
        try:
            journal = Journal.objects.get(localidentifier=journal_localidentifier)
        except Journal.DoesNotExist:
            code = xml_issue[0].get("revAbr") if xml_issue is not None else None
            code = code if code else re.sub(r"\d", "", journal_localidentifier)
            # If there is no journal with the localidentifier, try getting it by code.
            # We can safely assume that code is unique for new journal.
            try:
                journal = Journal.objects.get(code=code)
            except Journal.DoesNotExist:
                journal = Journal()

            journal.localidentifier = journal_localidentifier
            journal.code = code
            journal.collection = collection
            journal.fedora_created = fedora_journal.created
            journal.name = xml_name.text if xml_name is not None else None

        journal_erudit_object = journal.get_erudit_object()
        journal.first_publication_year = journal_erudit_object.first_publication_year
        journal.last_publication_year = journal_erudit_object.last_publication_year

        issues = publications_tree.xpath(".//numero")
        current_journal_localid_found = False
        precedences_relation = {
            "journal_localid": journal.localidentifier,
            "previous_localid": None,
            "next_localid": None,
        }
        # In the publications datastream, the issues are sorted in descending publication date
        # order. We use this fact to search if the journal's localidentifier has changed over
        # time. If it has, we want the last localid it held before the current one
        # and/or the first localid it'll hold after the current one.
        for issue in issues:
            issue_pid = issue.get("pid")
            journal_localid = issue_pid.split(".")[-2]
            if journal_localid != journal.localidentifier and not current_journal_localid_found:
                precedences_relation["next_localid"] = journal_localid
            elif journal_localid != journal.localidentifier and current_journal_localid_found:
                precedences_relation["previous_localid"] = journal_localid
            elif journal_localid == journal.localidentifier:
                current_journal_localid_found = True
        self.journal_precedence_relations.append(precedences_relation)

        journal_created = journal.id is None

        journal.fedora_updated = fedora_journal.modified
        journal.save()

        if journal_created:
            logger.info("journal.created", journal_name=journal.name)
        else:
            logger.debug("journal.updated", journal_name=journal.name)

        # STEP 3: imports all the issues associated with the journal
        # --
        if import_issues is False:
            return 0, 0

        issue_count = 0

        issue_fedora_query = "pid~erudit:{collectionid}.{journalid}.* label='Publication Erudit'"
        issue_fedora_query = issue_fedora_query.format(
            collectionid=journal.collection.localidentifier, journalid=journal.localidentifier
        )
        # pids for all issues found in Fedora for this journal
        issue_pids = get_pids(issue_fedora_query)
        # pids for all issues that are either in fedora or the db (but not in both)
        issue_pids_to_sync = get_journal_issue_pids_to_sync(
            journal,
            journal_erudit_object.get_published_issues_pids(),
        )
        # TODO: what's the point of this since we union both sets and we never delete issues ?
        for ipid in set(issue_pids) | issue_pids_to_sync:
            if ipid.startswith(journal_pid):
                # Imports the issue only if its PID is prefixed with the PID of the journal object.
                # In any other case this means that the issue is associated with another journal and
                # it will be imported later.
                self._import_issue(ipid, journal)
                issue_count += 1

        return issue_count

    @transaction.atomic
    def _import_issue(self, issue_pid, journal):
        """ Imports an issue using its PID. """

        # STEP 1: fetches the full Issue fedora object
        # --

        fedora_issue = PublicationDigitalObject(api, issue_pid)
        if not fedora_issue.exists:
            logger.error(
                "issue.import.error",
                issue_pid=issue_pid,
                msg="The issue with the given pid does not exist in Fedora",
            )
            raise CommandError(f"The issue with the pid {issue_pid} does not exist in Fedora")

        # STEP 2: creates or updates the issue object
        # --

        # Fetches the Issue instance... or creates a new one
        issue_localidentifier = localidentifier_from_pid(issue_pid)
        try:
            issue = Issue.objects.get(localidentifier=issue_localidentifier)
        except Issue.DoesNotExist:
            issue = Issue()
            issue.localidentifier = issue_localidentifier
            issue.journal = journal
            issue.fedora_created = fedora_issue.created

        # Set the proper values on the Issue instance
        issue_erudit_object = issue.get_erudit_object()
        issue.sync_with_erudit_object(erudit_object=issue_erudit_object)
        issue.fedora_updated = fedora_issue.modified
        journal_erudit_object = journal.get_erudit_object()
        issue.is_published = issue_pid in journal_erudit_object.get_published_issues_pids()
        issue.save()

        # STEP 4: patches the journal associated with the issue
        # --

        # Journal name
        if journal.name is None:
            journal.name = issue_erudit_object.get_journal_title(formatted=True)
        journal.save()

    def import_issues(self, unimported_issues_pids: Sequence[str]):
        for issue_pid in unimported_issues_pids:
            journal_localidentifier = issue_pid.split(":")[1].split(".")[1]
            try:
                journal = Journal.objects.get(localidentifier=journal_localidentifier)
            except (Journal.DoesNotExist, Journal.MultipleObjectsReturned) as e:
                logger.error(
                    "journal.import.error",
                    journal_pid=journal_localidentifier,
                    msg=repr(e),
                )
                return
            try:
                self._import_issue(issue_pid, journal)
            except Exception as e:
                logger.exception(
                    "issue.import.error",
                    issue_pid=issue_pid,
                    error=e,
                )
