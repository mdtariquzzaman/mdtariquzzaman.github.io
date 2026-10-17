"""Content and progressive-enhancement checks without rewriting build output."""
import ast
from copy import deepcopy
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
VOID_TAGS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
             'link', 'meta', 'param', 'source', 'track', 'wbr'}


class Element:
    def __init__(self, tag='', attrs=()):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []

    def text(self):
        return ''.join(child if isinstance(child, str) else child.text()
                       for child in self.children)

    def find(self, tag=None, cls=None, **attrs):
        found = []
        for child in self.children:
            if isinstance(child, str):
                continue
            if ((tag is None or child.tag == tag)
                    and (cls is None or cls in child.attrs.get('class', '').split())
                    and all(child.attrs.get(key) == value for key, value in attrs.items())):
                found.append(child)
            found.extend(child.find(tag, cls, **attrs))
        return found


class TreeParser(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = Element()
        self.stack = [self.root]
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        element = Element(tag, attrs)
        self.stack[-1].children.append(element)
        if tag not in VOID_TAGS:
            self.stack.append(element)

    def handle_endtag(self, tag):
        if tag not in VOID_TAGS:
            for index in range(len(self.stack) - 1, 0, -1):
                if self.stack[index].tag == tag:
                    del self.stack[index:]
                    break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def parse(html):
    return TreeParser(html).root


def builder_context(**overrides):
    """Execute source preparation only, stopping before output generation."""
    path = ROOT / 'scripts' / 'build.py'
    tree = ast.parse(path.read_text(), filename=str(path))
    preparation = []
    for node in tree.body:
        names = [target.id for target in node.targets if isinstance(target, ast.Name)] if isinstance(node, ast.Assign) else []
        if 'schemas' in names:
            break
        for name in names:
            if name in overrides:
                node.value = ast.parse(repr(overrides[name]), mode='eval').body
        preparation.append(node)
    else:
        raise AssertionError('The builder output boundary must be explicit.')
    module = ast.fix_missing_locations(ast.Module(body=preparation, type_ignores=[]))
    namespace = {'__file__': str(path), '__name__': 'build_content_test'}
    exec(compile(module, str(path), 'exec'), namespace)
    return namespace


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build = builder_context()

    def test_news_keeps_three_recent_and_all_older_updates_in_native_details(self):
        tree = parse(self.build['news_html'])
        recent = tree.children[0]
        archive = tree.find('details', 'news-archive')[0]
        ordered = sorted(self.build['news'], key=lambda item: datetime.strptime(item['date'], '%b %Y'), reverse=True)
        self.assertEqual([node.text() for node in recent.find('dt')], [item['date'] for item in ordered[:3]])
        self.assertEqual([node.text() for node in archive.find('dt')], [item['date'] for item in ordered[3:]])
        self.assertEqual(len(archive.find('summary')), 1)
        self.assertNotIn('open', archive.attrs)
        self.assertNotIn('hidden', archive.attrs)

    def test_long_author_lists_show_through_site_owner_then_et_al(self):
        for count in (10, 11):
            paper = deepcopy(self.build['papers'][0])
            paper['authors'] = [f'Author {index}' for index in range(count)]
            paper['authors'][4] = self.build['ME']
            tree = parse(self.build['publication'](paper, 'C1'))
            authors = tree.find(cls='authors')[0]
            with self.subTest(count=count):
                self.assertEqual(authors.tag, 'p')
                expected = ', '.join(paper['authors'] if count == 10 else paper['authors'][:5])
                if count > 10: expected += ', et al.'
                self.assertEqual(authors.text(), expected)
                self.assertEqual(authors.find('strong')[0].text(), self.build['ME'])
                self.assertFalse(tree.find('details', 'author-details'))
                self.assertEqual(len(paper['authors']), count)

    def test_publications_preserve_metadata_resources_and_figure_sequence(self):
        for paper in self.build['papers']:
            tree = parse(self.build['publication'](paper, 'TEST'))
            with self.subTest(paper=paper['id']):
                authors = tree.find(cls='authors')[0]
                shown = paper['authors']
                if len(shown) > 10:
                    cutoff = shown.index(self.build['ME']) + 1 if self.build['ME'] in shown else 1
                    shown = shown[:cutoff]
                expected_authors = ', '.join(shown) + (', et al.' if len(shown) < len(paper['authors']) else '')
                self.assertEqual(authors.tag, 'p')
                self.assertEqual(authors.text(), expected_authors)
                self.assertEqual(len(self.build['publication_schema'](paper)['author']), len(paper['authors']))
                self.assertEqual(tree.find('h3')[0].text(), paper['title'])
                self.assertEqual(tree.find('h3')[0].find('a')[0].attrs['href'], self.build['paper_url'](paper))
                self.assertFalse(tree.find(cls='pub-status'))
                self.assertEqual(len(tree.find('a', **{'data-kind': 'paper'})), 1)
                self.assertEqual(tree.find('code', id=f'{paper["id"]}-bibtex')[0].text(),
                                 '\n'.join(line.rstrip() for line in paper['bibtex'].strip().splitlines()))
                self.assertTrue(tree.find('details', id=f'{paper["id"]}-overview'))
                links = {**paper.get('links', {}), **paper.get('page', {}).get('links', {})}
                for labels, kind in [(('Website',), 'monitor'), (('Video',), 'video'),
                                     (('Dataset',), 'dataset'), (('Code', 'Code & Data'), 'code')]:
                    buttons = tree.find('a', **{'data-kind': kind})
                    self.assertEqual([button.attrs['href'] for button in buttons], [links[label] for label in labels if label in links])
                    self.assertEqual([button.text() for button in buttons], [label for label in labels if label in links])
                expected_figures = self.build['paper_figures'](paper)
                self.assertEqual([image.attrs['src'] for image in tree.find('img')], [figure['src'] for figure in expected_figures])
                self.assertEqual(len(tree.find('a', 'figure-zoom')), len(expected_figures))

    def test_nonlinear_entry_includes_combined_repository_and_all_published_figures(self):
        paper = next(p for p in self.build['papers'] if p['id'] == 'nonlinear-narrative')
        tree = parse(self.build['publication'](paper, 'TEST'))
        code = tree.find('a', **{'data-kind': 'code'})
        self.assertEqual(len(code), 1)
        self.assertEqual(code[0].text(), 'Code & Data')
        self.assertEqual(code[0].attrs['href'], 'https://github.com/Starscream-11813/LLM-nonlinear-storytelling')
        figures = self.build['paper_figures'](paper)
        self.assertEqual([figure['src'] for figure in figures],
                         [f'files/papers/nonlinear-narrative/figure-{number:02}.webp' for number in range(1, 14)])
        for number, figure in enumerate(figures, 1):
            with self.subTest(figure=number):
                self.assertTrue((ROOT / figure['src']).is_file())
                self.assertTrue(figure['caption'].startswith(f'Figure {number}. '))
                self.assertTrue(figure['alt'])
        self.assertEqual(len(tree.find('figure', 'carousel-slide')), 13)
        self.assertEqual(len(tree.find('button', 'carousel-dot')), 13)
        self.assertEqual(tree.find('span', 'carousel-status')[0].text(), '1 / 13')
        self.assertNotIn('open', tree.find('details', 'paper-abstract')[0].attrs)

    def test_preprints_never_receive_accepted_band(self):
        for paper in self.build['papers']:
            tree = parse(self.build['publication'](paper, 'TEST'))
            if self.build['is_preprint'](paper):
                self.assertFalse(tree.find(cls='accepted-venue'))
                self.assertEqual(tree.find('p', 'venue')[0].text(), paper['venue'])
            else:
                self.assertEqual(tree.find(cls='accepted-name')[0].find('a')[0].attrs['href'], paper['venue_url'])
        arxiv_only = deepcopy(self.build['papers'][0])
        arxiv_only.update(type='conference', venue='arXiv preprint', status='Accepted')
        tree = parse(self.build['publication'](arxiv_only, 'TEST'))
        self.assertFalse(tree.find(cls='accepted-venue'))
        self.assertFalse(tree.find(cls='pub-status'))

    def test_news_rejects_acceptance_claim_for_preprint(self):
        preprint = next(paper for paper in self.build['papers'] if self.build['is_preprint'](paper))
        news = [{'date': 'Jan 2026', 'text': f'<a href="publications.html#{preprint["id"]}">Paper</a> accepted.'}]
        with self.assertRaisesRegex(SystemExit, 'calls preprint.*accepted'):
            builder_context(news=news)

    def test_zero_metrics_remain_zero_and_null_metrics_are_unavailable(self):
        for value in (0, None):
            metrics = deepcopy(self.build['metrics'])
            metrics.update(citations=value, h_index=value, i10_index=value)
            context = builder_context(metrics=metrics)
            tree = parse(context['metric_html'])
            values = [node.text() for node in tree.find('dd')]
            with self.subTest(value=value):
                self.assertEqual(values, [str(len(context['papers']))] + [('0' if value == 0 else '—')] * 3)
                self.assertEqual(len(tree.find('span', **{'aria-label': 'Unavailable'})), 0 if value == 0 else 3)

    def test_publications_mix_types_in_one_reverse_chronological_catalogue(self):
        tree = parse(self.build['pub_body'])
        sections = tree.find('section', 'publication-group')
        expected_order = ['guise', 'nonlinear-narrative', 'scenario-bias',
                          'sign-parameters', 'bda', 'informal-bangla']
        self.assertEqual(len(sections), 1)
        catalogue = sections[0]
        self.assertEqual(catalogue.attrs['id'], 'publication-list')
        self.assertEqual(catalogue.attrs['aria-labelledby'], 'publication-key')
        self.assertIn('publication-catalogue', catalogue.attrs['class'].split())
        self.assertEqual(len(catalogue.find('h2')), 1)
        heading = catalogue.find('h2', 'publication-key', id='publication-key')[0]
        self.assertEqual(' '.join(heading.text().split()),
                         'C: Conference · J: Journal · W: Workshop · P: Preprint')
        self.assertFalse(catalogue.find('section'))
        self.assertFalse(catalogue.find('span', 'group-count'))
        self.assertEqual([paper['id'] for paper in self.build['ordered']], expected_order)
        self.assertEqual([article.attrs['id'] for article in catalogue.find('article', 'publication')],
                         expected_order)

    def test_publications_omit_contents_and_offer_a_native_back_to_top_link(self):
        tree = parse(self.build['pub_body'])
        self.assertFalse(tree.find('nav', 'page-contents'))
        self.assertFalse(tree.find(cls='reading-layout'))
        self.assertTrue(tree.find('div', 'publication-sections'))
        document = parse(self.build['render']('publications', 'Publications', 'Description',
                                             self.build['SITE'] + 'publications.html',
                                             self.build['pub_body'], current='publications'))
        links = document.find('a', 'back-to-top')
        self.assertEqual(len(links), 1)
        link = links[0]
        self.assertEqual(link.attrs['href'], '#main')
        self.assertEqual(link.attrs['aria-label'], 'Back to top')
        self.assertEqual(link.attrs['title'], 'Back to top')
        self.assertTrue(link.find('svg'))
        self.assertNotIn('hidden', link.attrs)
        self.assertEqual(len(document.find(id='main')), 1)
        self.assertEqual(len(document.find('header', 'site-header')[0].find('a', 'back-to-top')), 1)
        for slug in ('index', 'cv', 'personal'):
            other = parse(self.build['render'](slug, 'Title', 'Description', self.build['SITE'],
                                              '<p>Body</p>', current=slug))
            with self.subTest(page=slug):
                self.assertFalse(other.find('a', 'back-to-top'))

    def test_chronological_order_uses_dates_before_type_and_falls_back_to_year(self):
        template = self.build['papers'][0]
        records = [
            ('older-conference', 'conference', '2025', '2025-12-31'),
            ('undated-journal', 'journal', '2026', None),
            ('midyear-conference', 'conference', '2026', '2026-03-01'),
            ('latest-preprint', 'preprint', '2026', '2026-08-01'),
            ('older-workshop', 'workshop', '2025', None),
            ('midyear-workshop', 'workshop', '2026', '2026-05-01'),
        ]
        papers = []
        for identifier, kind, year, date in records:
            paper = deepcopy(template)
            paper.update(id=identifier, type=kind, year=year)
            paper.pop('date', None)
            if date:
                paper['date'] = date
            papers.append(paper)
        context = builder_context(papers=papers)
        self.assertEqual([paper['id'] for paper in context['ordered']], [
            'latest-preprint', 'midyear-workshop', 'midyear-conference',
            'undated-journal', 'older-conference', 'older-workshop',
        ])
        self.assertEqual(context['labels_by_id'], {
            'latest-preprint': 'P1', 'midyear-workshop': 'W2', 'midyear-conference': 'C2',
            'undated-journal': 'J1', 'older-conference': 'C1', 'older-workshop': 'W1',
        })

    def test_same_day_preprints_use_arxiv_order_independently_of_source_order(self):
        papers = [deepcopy(next(paper for paper in self.build['papers'] if paper['id'] == identifier))
                  for identifier in ('nonlinear-narrative', 'guise')]
        context = builder_context(papers=papers)
        self.assertEqual([paper['id'] for paper in context['ordered']], ['guise', 'nonlinear-narrative'])
        self.assertEqual(context['labels_by_id'], {'guise': 'P2', 'nonlinear-narrative': 'P1'})

    def test_publication_type_counters_and_legacy_anchors_survive_combined_catalogue(self):
        expected_labels = {'guise': 'P3', 'nonlinear-narrative': 'P2', 'scenario-bias': 'C1',
                           'sign-parameters': 'W2', 'bda': 'P1', 'informal-bangla': 'W1'}
        self.assertEqual(self.build['labels_by_id'], expected_labels)
        tree = parse(self.build['pub_body'])
        for identifier, label in expected_labels.items():
            article = tree.find('article', 'publication', id=identifier)[0]
            self.assertEqual(article.find('div', 'pub-year')[0].text(), label)
        legacy = {'conference-papers': 'scenario-bias', 'workshop-papers': 'sign-parameters',
                  'preprints': 'guise', 'peer-reviewed': 'scenario-bias',
                  'year-2026': 'guise', 'year-2025': 'sign-parameters',
                  'year-2024': 'bda', 'year-2023': 'informal-bangla'}
        for anchor, identifier in legacy.items():
            with self.subTest(anchor=anchor):
                self.assertEqual(len(tree.find(id=anchor)), 1)
                self.assertLess(self.build['pub_body'].index(f'id="{anchor}"'),
                                self.build['pub_body'].index(f'id="{identifier}"'))
                self.assertFalse(tree.find('section', id=anchor))
        self.assertFalse(tree.find(id='journal-articles'))

    def test_new_journal_joins_the_catalogue_without_a_standalone_type_group(self):
        journal = deepcopy(self.build['papers'][0])
        journal.update(type='journal', id='test-journal', date='2026-01-01')
        context = builder_context(papers=self.build['papers'] + [journal])
        tree = parse(context['pub_body'])
        section = tree.find('section', id='publication-list')[0]
        self.assertEqual([article.attrs['id'] for article in section.find('article', 'publication')],
                         ['guise', 'nonlinear-narrative', 'scenario-bias', 'test-journal',
                          'sign-parameters', 'bda', 'informal-bangla'])
        self.assertEqual(len(tree.find('section', 'publication-group')), 1)
        self.assertEqual(context['labels_by_id']['test-journal'], 'J1')
        self.assertEqual(len(tree.find(id='journal-articles')), 1)
        self.assertFalse(tree.find('section', id='journal-articles'))
        self.assertFalse(tree.find('nav', 'page-contents'))

    def test_favorites_retain_every_entry_in_one_wikipedia_list_row(self):
        tree = parse(self.build['expand_icons'](self.build['personal_body']))
        for category, entries in self.build['personal_data'].items():
            section = tree.find('section', id=category)[0]
            rows = section.find('li', 'favorite-row')
            with self.subTest(category=category):
                self.assertEqual(len(rows), len(entries))
                self.assertEqual(section.find('span', 'group-count')[0].text(), str(len(entries)))
                for index, (row, entry) in enumerate(zip(rows, entries), 1):
                    links = row.find('a')
                    self.assertEqual(len(links), 1)
                    link = links[0]
                    self.assertEqual(link.attrs['href'], entry['url'])
                    self.assertTrue(link.attrs['href'].startswith('https://en.wikipedia.org/wiki/'))
                    self.assertEqual(link.find('h3')[0].text(), entry['title'])
                    self.assertEqual(link.find('span', 'favorite-order')[0].text(), f'{index:02}')
                    self.assertFalse(link.find('span', 'favorite-initial'))
                    if entry.get('author'):
                        self.assertEqual(link.find('p', 'favorite-author')[0].text(), entry['author'])

    def test_section_navigation_keeps_native_anchors_for_mobile_enhancement(self):
        expected = {
            'cv': ['Education', 'Research experience', 'Technical skills', 'Teaching experience',
                   'Industry experience', 'Awards', 'Certifications', 'Languages'],
            'personal': ['Anime', 'Movies', 'TV shows', 'Books', 'Sports'],
        }
        for slug, labels in expected.items():
            tree = parse((ROOT / f'{slug}.html').read_text())
            nav = tree.find('nav', 'page-contents')[0]
            self.assertEqual([link.text() for link in nav.find('a')], labels)
            self.assertFalse(nav.find('p', 'contents-current'))
            for link in nav.find('a'):
                section = tree.find('section', id=link.attrs['href'].removeprefix('#'))[0]
                self.assertTrue(section.find('h2'))
                self.assertNotIn('hidden', link.attrs)

    def test_generated_main_pages_match_current_sources_and_keep_cv_actions(self):
        build = self.build
        schemas = {'index': build['ld']({'@context': 'https://schema.org', **build['PERSON']}),
                   'publications': build['ld']({'@context': 'https://schema.org', '@graph': [build['PERSON']] + [build['publication_schema'](paper) for paper in build['papers']]})}
        for slug, title, description, body in build['pages']:
            canonical = build['SITE'] + ('' if slug == 'index' else slug + '.html')
            page_title = 'Md. Tariquzzaman · Junior Lecturer & NLP Researcher at IUT' if slug == 'index' else title + ' · Md. Tariquzzaman'
            expected = build['render'](slug, page_title, description, canonical, body, current=slug, head_extra=schemas.get(slug, ''))
            with self.subTest(page=slug):
                self.assertEqual((ROOT / f'{slug}.html').read_text(), expected)
                self.assertNotIn('{{', expected)
                tree = parse(expected)
                self.assertEqual(len(tree.find('h1')), 1)
                self.assertEqual(len(tree.find('meta', name='google-site-verification')), 1)
                self.assertEqual(len(tree.find('meta', name='msvalidate.01')), 1)
                for action in tree.find('a', **{'data-kind': 'cv'}):
                    self.assertEqual(action.attrs['href'], 'files/cv/tariq.pdf')
                    self.assertEqual(action.attrs['target'], '_blank')
                    self.assertIn('noopener', action.attrs['rel'].split())
                    self.assertNotIn('download', action.attrs)
                    self.assertEqual(action.find('span')[0].text(), 'Download CV')
        header = parse(build['render']('index', 'Home', 'Description', build['SITE'], '<p>Body</p>', current='index'))
        site_header = header.find('header', 'site-header')[0]
        self.assertEqual([link.text() for link in site_header.find('nav')[0].find('a')], ['Home', 'Publications', 'CV', 'Personal'])
        self.assertEqual(site_header.find('nav')[0].find('a')[0].attrs['aria-current'], 'page')
        self.assertEqual(len(site_header.find('div', 'header-title-strip')[0].find('button', 'theme-toggle-mobile')), 1)
        self.assertEqual(len(site_header.find('div', 'header-inner')[0].find('button', 'theme-toggle-desktop')), 1)
        self.assertFalse(site_header.find('a', 'home-link'))
        cv = parse((ROOT / 'cv.html').read_text())
        for anchor in ('experience', 'appointments', 'teaching'):
            self.assertTrue(cv.find(id=anchor))
        source = parse(build['expand_icons']((ROOT / 'content' / 'cv.html').read_text()))
        self.assertEqual(cv.find('main')[0].text(), source.text())


if __name__ == '__main__':
    unittest.main()
