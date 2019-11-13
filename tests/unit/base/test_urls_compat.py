import pytest

from django.urls import reverse, resolve
from django.urls.exceptions import Resolver404


@pytest.mark.django_db
class TestLegacyJournalUrlPatterns:

    @pytest.mark.parametrize('journal_code, year, volume, number, expected_url', [
        ('foo', '2000', '1', '3', '/revue/foo/2000/v1/n3'),
        ('foo-1', '2000', '1-2', '3-4', '/revue/foo-1/2000/v1-2/n3-4'),
        ('foo', '2000', '1', '', '/revue/foo/2000/v1/n'),
        ('foo-1', '2000', '1-2', '', '/revue/foo-1/2000/v1-2/n'),
        ('foo', '2000', '', '3', '/revue/foo/2000/v/n3'),
        ('foo-1', '2000', '', '3-4', '/revue/foo-1/2000/v/n3-4'),
        ('foo', '2000', '', '', '/revue/foo/2000/v/n'),
        ('foo-1', '2000', '', '', '/revue/foo-1/2000/v/n'),
    ])
    def test_legacy_issue_detail(self, journal_code, year, volume, number, expected_url):
        url = reverse('legacy_journal:legacy_issue_detail', args=[
            journal_code,
            year,
            volume,
            number,
        ])
        assert url == expected_url

    @pytest.mark.parametrize('journal_code, year, volume, number, expected_url', [
        ('foo', '2000', '1', '3', '/revue/foo/2000/v1/n3/index.htm'),
        ('foo-1', '2000', '1-2', '3-4', '/revue/foo-1/2000/v1-2/n3-4/index.htm'),
        ('foo', '2000', '1', '', '/revue/foo/2000/v1/n/index.htm'),
        ('foo-1', '2000', '1-2', '', '/revue/foo-1/2000/v1-2/n/index.htm'),
        ('foo', '2000', '', '3', '/revue/foo/2000/v/n3/index.htm'),
        ('foo-1', '2000', '', '3-4', '/revue/foo-1/2000/v/n3-4/index.htm'),
        ('foo', '2000', '', '', '/revue/foo/2000/v/n/index.htm'),
        ('foo-1', '2000', '', '', '/revue/foo-1/2000/v/n/index.htm'),
    ])
    def test_legacy_issue_detail_index(self, journal_code, year, volume, number, expected_url):
        url = reverse('legacy_journal:legacy_issue_detail_index', args=[
            journal_code,
            year,
            volume,
            number,
        ])
        assert url == expected_url

    @pytest.mark.parametrize('journal_code, year, volume, local_id, expected_url', [
        ('foo', '2000', '1', 'bar', '/culture/foo/2000/v1/bar'),
        ('foo-1', '2000', '1-2', 'bar-1', '/culture/foo-1/2000/v1-2/bar-1'),
        ('foo', '2000', '', 'bar', '/culture/foo/2000/v/bar'),
    ])
    def test_legacy_issue_detail_culture_year_volume(self, journal_code, year, volume, local_id, expected_url):
        url = reverse('legacy_journal:legacy_issue_detail_culture_year_volume', args=[
            journal_code,
            year,
            volume,
            local_id,
        ])
        assert url == expected_url

    @pytest.mark.parametrize('journal_code, year, volume, local_id, expected_url', [
        ('foo', '2000', '1', 'bar', '/culture/foo/2000/v1/bar/x.htm'),
        ('foo-1', '2000', '1-2', 'bar-1', '/culture/foo-1/2000/v1-2/bar-1/x.htm'),
        ('foo', '2000', '', 'bar', '/culture/foo/2000/v/bar/x.htm'),
    ])
    def test_legacy_issue_detail_culture_year_volume_index(self, journal_code, year, volume, local_id, expected_url):
        url = reverse('legacy_journal:legacy_issue_detail_culture_year_volume_index', args=[
            journal_code,
            year,
            volume,
            local_id,
        ])
        assert url == expected_url

    @pytest.mark.parametrize('journal_code, local_id, expected_url', [
        ('foo', 'bar', '/culture/foo/bar'),
        ('foo-1', 'bar-1', '/culture/foo-1/bar-1'),
    ])
    def test_legacy_issue_detail_culture(self, journal_code, local_id, expected_url):
        url = reverse('legacy_journal:legacy_issue_detail_culture', args=[
            journal_code,
            local_id,
        ])
        assert url == expected_url

    @pytest.mark.parametrize('journal_code, local_id, expected_url', [
        ('foo', 'bar', '/culture/foo/bar/index.htm'),
        ('foo-1', 'bar-1', '/culture/foo-1/bar-1/index.htm'),
    ])
    def test_legacy_issue_detail_culture_index(self, journal_code, local_id, expected_url):
        url = reverse('legacy_journal:legacy_issue_detail_culture_index', args=[
            journal_code,
            local_id,
        ])
        assert url == expected_url

    @pytest.mark.parametrize('journal_code, year, volume, number, local_id, format_id, expected_url', [
        ('foo', '2000', '1', '3', 'bar', 'html', '/revue/foo/2000/v1/n3/bar.html'),
        ('foo-1', '2000', '1-2', '3-4', 'bar-2', 'pdf', '/revue/foo-1/2000/v1-2/n3-4/bar-2.pdf'),
        ('foo', '2000', '1', '', 'bar', 'html', '/revue/foo/2000/v1/n/bar.html'),
        ('foo-1', '2000', '1-2', '', 'bar-2', 'pdf', '/revue/foo-1/2000/v1-2/n/bar-2.pdf'),
        ('foo', '2000', '', '3', 'bar', 'html', '/revue/foo/2000/v/n3/bar.html'),
        ('foo-1', '2000', '', '3-4', 'bar-2', 'pdf', '/revue/foo-1/2000/v/n3-4/bar-2.pdf'),
        ('foo', '2000', '', '', 'bar', 'html', '/revue/foo/2000/v/n/bar.html'),
        ('foo-1', '2000', '', '', 'bar-2', 'pdf', '/revue/foo-1/2000/v/n/bar-2.pdf'),
    ])
    def test_legacy_article_detail(self, journal_code, year, volume, number, local_id, format_id, expected_url):
        url = reverse('legacy_journal:legacy_article_detail', args=[
            journal_code,
            year,
            volume,
            number,
            local_id,
            format_id,
        ])
        assert url == expected_url

    @pytest.mark.parametrize('journal_code, year, volume, number, local_id, format_id, expected_url', [
        ('foo', '2000', '1', '3', 'bar', 'html', '/culture/foo/2000/v1/n3/bar.html'),
        ('foo-1', '2000', '1-2', '3-4', 'bar-2', 'pdf', '/culture/foo-1/2000/v1-2/n3-4/bar-2.pdf'),
        ('foo', '2000', '1', '', 'bar', 'html', '/culture/foo/2000/v1/n/bar.html'),
        ('foo-1', '2000', '1-2', '', 'bar-2', 'pdf', '/culture/foo-1/2000/v1-2/n/bar-2.pdf'),
        ('foo', '2000', '', '3', 'bar', 'html', '/culture/foo/2000/v/n3/bar.html'),
        ('foo-1', '2000', '', '3-4', 'bar-2', 'pdf', '/culture/foo-1/2000/v/n3-4/bar-2.pdf'),
        ('foo', '2000', '', '', 'bar', 'html', '/culture/foo/2000/v/n/bar.html'),
        ('foo-1', '2000', '', '', 'bar-2', 'pdf', '/culture/foo-1/2000/v/n/bar-2.pdf'),
    ])
    def test_legacy_article_detail_culture(self, journal_code, year, volume, number, local_id, format_id, expected_url):
        url = reverse('legacy_journal:legacy_article_detail_culture', args=[
            journal_code,
            year,
            volume,
            number,
            local_id,
            format_id,
        ])
        assert url == expected_url

    @pytest.mark.parametrize('journal_code, issue_id, local_id, format_id, expected_url', [
        ('foo', 'bar', 'baz', 'html', '/culture/foo/bar/baz.html'),
        ('foo-1', 'bar-2', 'baz-3', 'pdf', '/culture/foo-1/bar-2/baz-3.pdf'),
    ])
    def test_legacy_article_detail_culture_localidentifier(self, journal_code, issue_id, local_id, format_id, expected_url):
        url = reverse('legacy_journal:legacy_article_detail_culture_localidentifier', args=[
            journal_code,
            issue_id,
            local_id,
            format_id,
        ])
        assert url == expected_url

    @pytest.mark.parametrize('url, expected_url_name', [
        # legacy_journals
        ('/revue/', 'legacy_journals'),
        # legacy_journals_index
        ('/revue/index.html', 'legacy_journals_index'),
        # legacy_journals
        ('/culture/', 'legacy_journals_culture'),
        # legacy_journals_index
        ('/culture/index.html', 'legacy_journals_culture_index'),
        # legacy_journal_search
        ('/recherche/journal_code/', 'legacy_journal_search'),
        # legacy_journal_detail
        ('/revue/journal_code/', 'legacy_journal_detail'),
        # legacy_journal_authors
        ('/revue/journal_code/auteurs.html', 'legacy_journal_authors'),
        # legacy_journal_detail_index
        ('/revue/journal_code/index.html', 'legacy_journal_detail_index'),
        ('/revue/journal_code/apropos.html', 'legacy_journal_detail_index'),
        ('/revue/journal_code/thematique.html', 'legacy_journal_detail_index'),
        # legacy_journal_rss
        ('/revue/journal_code/rss.xml', 'legacy_journal_rss'),
        # legacy_journal_detail_culture
        ('/culture/journal_code/', 'legacy_journal_detail_culture'),
        # legacy_journal_authors_culture
        ('/culture/journal_code/auteurs.html', 'legacy_journal_authors_culture'),
        # legacy_journal_detail_culture_index
        ('/culture/journal_code/index.html', 'legacy_journal_detail_culture_index'),
        ('/culture/journal_code/apropos.html', 'legacy_journal_detail_culture_index'),
        ('/culture/journal_code/thematique.html', 'legacy_journal_detail_culture_index'),
        # legacy_journal_rss_culture
        ('/culture/journal_code/rss.xml', 'legacy_journal_rss_culture'),
    ])
    def test_resolve_journal_urls_compat(self, url, expected_url_name):
        if expected_url_name:
            resolver = resolve(url)
            assert resolver.url_name == expected_url_name
        else:
            with pytest.raises(Resolver404):
                resolver = resolve(url)
