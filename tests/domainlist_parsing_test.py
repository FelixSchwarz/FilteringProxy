# -*- coding: UTF-8 -*-

from io import StringIO

from pythonic_testcase import *

from schwarz.filtering_proxy import parse_domainlist


class DomainlistParsingTest(PythonicTestCase):
    def test_can_parse_domains(self):
        list_str = (
            'foo.example\n'
            'bar.example'
        )
        dl = parse_domainlist(StringIO(list_str))
        assert_true(dl.matches('foo.example'))
        assert_true(dl.matches('bar.example'))
        assert_false(dl.matches('baz.example'))

    def test_skips_empty_lines(self):
        list_str = (
            'foo.example\n'
            '\n'
        )
        dl = parse_domainlist(StringIO(list_str))
        assert_true(dl.matches('foo.example'))
        assert_false(dl.matches(''))

    def test_skips_comments(self):
        list_str = (
            '#foo.example'
        )
        dl = parse_domainlist(StringIO(list_str))
        assert_false(dl.matches('#foo.example'))
