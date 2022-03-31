# -*- coding: UTF-8 -*-

from pythonic_testcase import *

from schwarz.filtering_proxy import Configuration, Domainlist


class ConfigurationTest(PythonicTestCase):
    def test_can_decide_if_domain_is_allowed(self):
        cfg = Configuration(config={}, config_path='/foo.cfg')
        cfg.allowed = [Domainlist(domains=('foo.example',))]
        cfg.blocked = [Domainlist(domains=('bar.example',))]

        assert_true(cfg.is_allowed('foo.example'))
        assert_false(cfg.is_allowed('bar.example'))

        assert_true(cfg.is_allowed('baz.example'))
        cfg.config['default_rule'] = 'block'
        assert_false(cfg.is_allowed('baz.example'))

