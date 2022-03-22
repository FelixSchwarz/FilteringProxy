# -*- coding: UTF-8 -*-

from pythonic_testcase import *

from schwarz.filtering_proxy import Domainlist


class DomainlistMatchingTest(PythonicTestCase):
    def test_can_match_domain(self):
        dl = Domainlist(domains=('foo.example',))
        assert_true(dl.matches('foo.example'))
        assert_false(dl.matches('baz.example'))

    def test_can_match_with_wildcards(self):
        dl = Domainlist(domains=('*.foo.example', 'bar.example'))
        assert_false(dl.matches('foo.example'))
        assert_true(dl.matches('www.foo.example'))
        assert_true(dl.matches('bar.example'))
        assert_false(dl.matches('www.bar.example'))

