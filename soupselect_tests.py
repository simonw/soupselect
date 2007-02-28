import unittest
from BeautifulSoup import BeautifulSoup

from soupselect import select, monkeypatch, unmonkeypatch

class BaseTest(unittest.TestCase):
    
    def setUp(self):
        self.soup = BeautifulSoup(HTML)
    
    def assertSelects(self, selector, expected_ids):
        el_ids = [el['id'] for el in select(self.soup, selector)]
        el_ids.sort()
        expected_ids.sort()
        self.assertEqual(expected_ids, el_ids,
            "Selector %s, expected [%s], got [%s]" % (
                selector, ', '.join(expected_ids), ', '.join(el_ids)
            )
        )
    
    assertSelect = assertSelects
    
    def assertSelectMultiple(self, *tests):
        for selector, expected_ids in tests:
            self.assertSelect(selector, expected_ids)

class TestBasicSelectors(BaseTest):
    
    def test_one_tag_one(self):
        els = select(self.soup, 'title')
        self.assertEqual(len(els), 1)
        self.assertEqual(els[0].name, 'title')
        self.assertEqual(els[0].contents, [u'The title'])
    
    def test_one_tag_many(self):
        els = select(self.soup, 'div')
        self.assertEqual(len(els), 3)
        for div in els:
            self.assertEqual(div.name, 'div')
    
    def test_tag_in_tag_one(self):
        els = select(self.soup, 'div div')
        self.assertSelects('div div', ['inner'])
    
    def test_tag_in_tag_many(self):
        for selector in ('html div', 'html body div', 'body div'):
            self.assertSelects(selector, ['main', 'inner', 'footer'])
    
    def test_tag_no_match(self):
        self.assertEqual(len(select(self.soup, 'del')), 0)
    
    def test_invalid_tag(self):
        self.assertEqual(len(select(self.soup, 'tag%t')), 0)

    def test_header_tags(self):
        self.assertSelectMultiple(
            ('h1', ['header1']),
            ('h2', ['header2', 'header3']),
        )

    def test_class_one(self):
        for selector in ('.onep', 'p.onep', 'html p.onep'):
            els = select(self.soup, selector)
            self.assertEqual(len(els), 1)
            self.assertEqual(els[0].name, 'p')
            self.assertEqual(els[0]['class'], 'onep')
        
    def test_class_mismatched_tag(self):
        els = select(self.soup, 'div.onep')
        self.assertEqual(len(els), 0)

    def test_one_id(self):
        for selector in ('div#inner', '#inner', 'div div#inner'):
            self.assertSelects(selector, ['inner'])
    
    def test_bad_id(self):
        els = select(self.soup, '#doesnotexist')
        self.assertEqual(len(els), 0)

    def test_items_in_id(self):
        els = select(self.soup, 'div#inner p')
        self.assertEqual(len(els), 3)
        for el in els:
            self.assertEqual(el.name, 'p')
        self.assertEqual(els[1]['class'], 'onep')
        self.assert_(not els[0].has_key('class'))

    def test_a_bunch_of_emptys(self):
        for selector in ('div#main del', 'div#main div.oops', 'div div#main'):
            self.assertEqual(len(select(self.soup, selector)), 0)

    def test_multi_class_support(self):
        for selector in ('.class1', 'p.class1', '.class2', 'p.class2',
            '.class3', 'p.class3', 'html p.class2', 'div#inner .class2'):
            self.assertSelects(selector, ['pmulti'])

class TestAttributeSelectors(BaseTest):

    def test_attribute_equals(self):
        self.assertSelectMultiple(
            ('p[class="onep"]', ['p1']),
            ('p[id="p1"]', ['p1']),
            ('[class="onep"]', ['p1']),
            ('[id="p1"]', ['p1']),
            ('link[rel="stylesheet"]', ['l1']),
            ('link[type="text/css"]', ['l1']),
            ('link[href="blah.css"]', ['l1']),
            ('link[href="no-blah.css"]', []),
            ('[rel="stylesheet"]', ['l1']),
            ('[type="text/css"]', ['l1']),
            ('[href="blah.css"]', ['l1']),
            ('[href="no-blah.css"]', []),
            ('p[href="no-blah.css"]', []),
            ('[href="no-blah.css"]', []),        
        )
    
    def test_attribute_tilde(self):
        self.assertSelectMultiple(
            ('p[class~="class1"]', ['pmulti']),
            ('p[class~="class2"]', ['pmulti']),
            ('p[class~="class3"]', ['pmulti']),
            ('[class~="class1"]', ['pmulti']),
            ('[class~="class2"]', ['pmulti']),
            ('[class~="class3"]', ['pmulti']),
            ('a[rel~="friend"]', ['bob']),
            ('a[rel~="met"]', ['bob']),
            ('[rel~="friend"]', ['bob']),
            ('[rel~="met"]', ['bob']),
        )

    def test_attribute_startswith(self):
        self.assertSelectMultiple(
            ('[rel^="style"]', ['l1']),
            ('link[rel^="style"]', ['l1']),
            ('notlink[rel^="notstyle"]', []),
            ('[rel^="notstyle"]', []),
            ('link[rel^="notstyle"]', []),
            ('link[href^="bla"]', ['l1']),
            ('a[href^="http://"]', ['bob', 'me']),
            ('[href^="http://"]', ['bob', 'me']),
            ('[id^="p"]', ['pmulti', 'p1']),
            ('[id^="m"]', ['me', 'main']),
            ('div[id^="m"]', ['main']),
            ('a[id^="m"]', ['me']),
        )
    
    def test_attribute_endswith(self):
        self.assertSelectMultiple(
            ('[href$=".css"]', ['l1']),
            ('link[href$=".css"]', ['l1']),
            ('link[id$="1"]', ['l1']),
            ('[id$="1"]', ['l1', 'p1', 'header1']),
            ('div[id$="1"]', []),
            ('[id$="noending"]', []),
        )
    
    def test_attribute_contains(self):
        self.assertSelectMultiple(
            # From test_attribute_startswith
            ('[rel*="style"]', ['l1']),
            ('link[rel*="style"]', ['l1']),
            ('notlink[rel*="notstyle"]', []),
            ('[rel*="notstyle"]', []),
            ('link[rel*="notstyle"]', []),
            ('link[href*="bla"]', ['l1']),
            ('a[href*="http://"]', ['bob', 'me']),
            ('[href*="http://"]', ['bob', 'me']),
            ('[id*="p"]', ['pmulti', 'p1']),
            ('div[id*="m"]', ['main']),
            ('a[id*="m"]', ['me']),
            # From test_attribute_endswith
            ('[href*=".css"]', ['l1']),
            ('link[href*=".css"]', ['l1']),
            ('link[id*="1"]', ['l1']),
            ('[id*="1"]', ['l1', 'p1', 'header1']),
            ('div[id*="1"]', []),
            ('[id*="noending"]', []),
            # New for this test
            ('[href*="."]', ['bob', 'me', 'l1']),
            ('a[href*="."]', ['bob', 'me']),
            ('link[href*="."]', ['l1']),
            ('div[id*="n"]', ['main', 'inner']),
            ('div[id*="nn"]', ['inner']),
        )
    
    def test_attribute_exact_or_hypen(self):
        self.assertSelectMultiple(
            ('p[lang|="en"]', ['lang-en', 'lang-en-gb', 'lang-en-us']),
            ('[lang|="en"]', ['lang-en', 'lang-en-gb', 'lang-en-us']),
            ('p[lang|="fr"]', ['lang-fr']),
            ('p[lang|="gb"]', []),
        )

    def test_attribute_exists(self):
        self.assertSelectMultiple(
            ('[rel]', ['l1', 'bob', 'me']),
            ('link[rel]', ['l1']),
            ('a[rel]', ['bob', 'me']),
            ('[lang]', ['lang-en', 'lang-en-gb', 'lang-en-us', 'lang-fr']),
            ('p[class]', ['p1', 'pmulti']),
            ('[blah]', []),
            ('p[blah]', []),
        )

class TestMonkeyPatch(BaseTest):
    
    def assertSelectMultipleExplicit(self, soup, *tests):
        for selector, expected_ids in tests:
            el_ids = [el['id'] for el in soup.findSelect(selector)]
            el_ids.sort()
            expected_ids.sort()
            self.assertEqual(expected_ids, el_ids,
                "Selector %s, expected [%s], got [%s]" % (
                    selector, ', '.join(expected_ids), ', '.join(el_ids)
                )
            )
    
    def test_monkeypatch_explicit(self):
        soup = BeautifulSoup(HTML)
        self.assertRaises(TypeError, soup.findSelect, '*')
        
        monkeypatch(BeautifulSoup)
        
        self.assert_(soup.findSelect('*'))
        self.assertSelectMultipleExplicit(soup,
            ('link', ['l1']),
            ('div#main', ['main']),
            ('div div', ['inner']),
        )
        
        unmonkeypatch(BeautifulSoup)
        
        self.assertRaises(TypeError, soup.findSelect, '*')

    def test_monkeypatch_implicit(self):
        soup = BeautifulSoup(HTML)
        self.assertRaises(TypeError, soup.findSelect, '*')

        monkeypatch()

        self.assert_(soup.findSelect('*'))
        self.assertSelectMultipleExplicit(soup,
            ('link', ['l1']),
            ('div#main', ['main']),
            ('div div', ['inner']),
        )
        
        unmonkeypatch()
        
        self.assertRaises(TypeError, soup.findSelect, '*')


HTML = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
    "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
  <title>The title</title>
  <link rel="stylesheet" href="blah.css" type="text/css" id="l1">
</head>
<body>

<div id="main">
    <div id="inner">
        <h1 id="header1">An H1</h1>
        <p>Some text</p>
        <p class="onep" id="p1">Some more text</p>
        <h2 id="header2">An H2</h2>
        <p class="class1 class2 class3" id="pmulti">Another</p>
        <a href="http://bob.example.org/" rel="friend met" id="bob">Bob</a>
        <h2 id="header3">Another H2</h2>
        <a id="me" href="http://simonwillison.net/" rel="me">me</a>
    </div>
    <p lang="en" id="lang-en">English</p>
    <p lang="en-gb" id="lang-en-gb">English UK</p>
    <p lang="en-us" id="lang-en-us">English US</p>
    <p lang="fr" id="lang-fr">French</p>
</div>

<div id="footer">
</div>

</body>
</html>
"""

if __name__ == '__main__':
    unittest.main()