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
        cfg = self._create_config(default_rule='block')

        create_rule(domain='foo.example', allow=True, rule_basedir=self.base_path)
        assert_true(cfg.is_allowed('foo.example'))
        assert_false(cfg.is_allowed('bar.example'))

    def test_can_detect_new_files(self):
        cfg = self._create_config(default_rule='block')

        assert_false(cfg.is_allowed('foo.example'))
        assert_false(cfg.is_allowed('bar.example'))

        create_rule(domain='foo.example', allow=True, rule_basedir=self.base_path)
        assert_true(cfg.is_allowed('foo.example'))
        assert_false(cfg.is_allowed('bar.example'))

        create_rule(domain='bar.example', allow=True, rule_basedir=self.base_path)
        assert_true(cfg.is_allowed('bar.example'))

    def test_can_detect_changed_configuration(self):
        cfg = self._create_config(default_rule='block')
        assert_false(cfg.is_allowed('foo.example'))

        self._update_config(default_rule='allow')
        cfg.reload_if_necessary(force=True)
        assert_true(cfg.is_allowed('foo.example'))

    def test_can_load_logging_configuration(self):
        log_path = str(self.base_path / 'proxy.log')
        cfg = self._create_config(log_file=log_path)

        cfg.log.info('foo bar')
        assert_path_exists(log_path)
        with open(log_path, 'r') as log_fp:
            logged_lines = tuple(log_fp.readlines())
        line, = logged_lines
        assert_contains('foo bar', line)

    def _create_config(self, **cfg_options):
        create_config(self.config_path, rule_basedir=self.base_path, **cfg_options)
        cfg = init_config(self.config_path)
        return cfg

    def _update_config(self, **cfg_options):
        config = setup_configparser(self.base_path, **cfg_options)
        with self.config_path.open('w') as config_fp:
            config.write(config_fp)


def create_cfg_dirs(rule_basedir):
    (rule_basedir/'allowed.d').mkdir()
    (rule_basedir/'blocked.d').mkdir()

def setup_configparser(rule_basedir, **cfg_options):
    config = ConfigParser()
    config['proxy'] = {}
    cfg_section = config['proxy']
    cfg_section['rule_basedir'] = str(rule_basedir)
    for cfg_key, cfg_value in cfg_options.items():
        cfg_section[cfg_key] = cfg_value
    return config

def create_config(config_path, rule_basedir, **cfg_options):
    config = setup_configparser(rule_basedir, **cfg_options)
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

