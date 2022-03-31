# -*- coding: UTF-8 -*-

from configparser import ConfigParser
from pathlib import Path

from pythonic_testcase import *
from schwarz.fakefs_helpers import FakeFS

from schwarz.filtering_proxy import init_config, Configuration, Domainlist


class ConfigurationTest(PythonicTestCase):
    def setUp(self):
        self.fs = FakeFS.set_up(test=self)
        self.base_path = Path(self.fs.create_dir('data').path)
        create_cfg_dirs(self.base_path)
        self.config_path = self.base_path/'cfg'/'proxy.cfg'

    def test_can_decide_if_domain_is_allowed(self):
        cfg = Configuration(config={}, config_path=str(self.config_path))
        cfg.allowed = [Domainlist(domains=('foo.example',))]
        cfg.blocked = [Domainlist(domains=('bar.example',))]

        assert_true(cfg.is_allowed('foo.example'))
        assert_false(cfg.is_allowed('bar.example'))

        assert_true(cfg.is_allowed('baz.example'))
        cfg.config['default_rule'] = 'block'
        assert_false(cfg.is_allowed('baz.example'))

    def test_can_init_config_from_file(self):
        create_config(self.config_path, rule_basedir=self.base_path, default_rule='block')
        cfg = init_config(self.config_path)

        create_rule(domain='foo.example', allow=True, rule_basedir=self.base_path)
        assert_true(cfg.is_allowed('foo.example'))
        assert_false(cfg.is_allowed('bar.example'))



def create_cfg_dirs(rule_basedir):
    (rule_basedir/'allowed.d').mkdir()
    (rule_basedir/'blocked.d').mkdir()

def create_config(config_path, rule_basedir, *, default_rule=None):
    config = ConfigParser()
    config['proxy'] = {}
    cfg_section = config['proxy']
    cfg_section['rule_basedir'] = str(rule_basedir)
    if default_rule:
        cfg_section['default_rule'] = default_rule
    config_dir = config_path.parent
    config_dir.mkdir(exist_ok=True)
    with config_path.open('x') as config_fp:
        config.write(config_fp)

def create_rule(domain, *, allow=True, rule_basedir):
    dirname = 'allowed.d' if allow else 'blocked.d'
    path_rulesdir = rule_basedir / dirname
    path_rulesdir.mkdir(exist_ok=True)
    rulefile_path = path_rulesdir / f'{domain}.domains'
    with rulefile_path.open('x') as fp:
        fp.write(f'{domain}\n')

