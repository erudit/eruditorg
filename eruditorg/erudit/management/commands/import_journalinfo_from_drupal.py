from django.core.management.base import BaseCommand

from erudit.models.core import Journal, JournalInformation


class Command(BaseCommand):

    help = """Import 'apropos' sections from our Drupal BD into JournalInformation"""

    def add_arguments(self, parser):
        parser.add_argument('dbhost', help="Host of the Drupal MySQL DB")
        parser.add_argument('dbuser', help="User of the Drupal MySQL DB")
        parser.add_argument('dbpass', help="Password of the Drupal MySQL DB")
        parser.add_argument(
            '--journal', help="Import only a specific journal (specify the shortname)"
        )
        parser.add_argument(
            '--overwrite', action='store_true', help="Import even when destinations are not empty."
        )

    def handle(self, *args, **options):
        try:
            import pymysql.cursors
        except ImportError:
            print("PyMySQL is required. Do 'pip install pymysql' and try again")
            return

        def get_drupal_contents(connection, drupal_tablename, lang):
            with connection.cursor() as cur:
                sql = """
                    select n.title, f.field_{0}_value
                    from node as n join field_data_field_{0} as f on n.nid = f.entity_id
                    where n.status = 1 and n.language = %s
                """.format(drupal_tablename)
                cur.execute(sql, (lang, ))
                rows = cur.fetchall()
            if rows:
                def fix_encoding(s):
                    # some titles in the DB have wrong encodings.
                    return s.replace('\x92', '’')

                def get_row_html(title, contents):
                    return '<h4>{}</h4>{}'.format(fix_encoding(title), contents)

                return '\n'.join(get_row_html(title, contents) for title, contents in rows)
            else:
                return ''

        def import_section(connection, journal, django_fieldname, drupal_tablename, lang):
            dest_fieldname = '{}_{}'.format(django_fieldname, lang)
            if not options['overwrite'] and getattr(journal.information, dest_fieldname):
                print("Skipping {} (not empty)".format(dest_fieldname))
                return False
            print("Setting {}".format(dest_fieldname))
            full_html = '\n'.join(
                get_drupal_contents(connection, tn, lang) for tn in drupal_tablenames
            )
            if full_html.strip():
                setattr(journal.information, dest_fieldname, full_html)
                journal.information.save()
            else:
                print("No content was found for {}".format(dest_fieldname))

        connection = pymysql.connect(
            host=options['dbhost'],
            user=options['dbuser'],
            password=options['dbpass'],
        )
        SECTION_NAMES = [
            # (django fieldname, [drupal table names])
            ('about', ('obligatoire_texte', 'optionnelle_texte')),
            ('editorial_policy', ('auxauteurs_texte', )),
            ('subscriptions', ('text', )),
            ('team', ('comite_texte', )),
            ('contact', ('contact_texte', )),
            ('partners', ('partenaire', )),
        ]
        with connection.cursor() as cur:
            sql = 'show databases'
            cur.execute(sql)
            all_dbnames = {dbname for (dbname, ) in cur.fetchall()}
        qs = Journal.objects
        if options['journal'] is not None:
            qs = qs.filter(code=options['journal'])
        if not qs.exists():
            print("No Journal found.")
            return
        for journal in qs.all():
            try:
                # ensure that JournalInformation exists
                journal.information
            except JournalInformation.DoesNotExist:
                JournalInformation.objects.create(journal=journal)
            dbname = 'drupalerudit_{}'.format(journal.code)
            if dbname not in all_dbnames:
                print("Skipping journal {} (not in drupal)".format(journal.code))
                continue
            print("Importing journal {}".format(journal.code))
            connection.select_db(dbname)
            for django_fieldname, drupal_tablenames in SECTION_NAMES:
                for lang in ('fr', 'en'):
                    import_section(
                        connection,
                        journal,
                        django_fieldname,
                        drupal_tablenames,
                        lang,
                    )
