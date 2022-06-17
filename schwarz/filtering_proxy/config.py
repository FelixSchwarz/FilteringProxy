# -*- coding: UTF-8 -*-

from configparser import ConfigParser
import logging
from logging import Logger
import os
from pathlib import Path
import time
from typing import Iterable

from .domainlist import parse_domainlists_from_directory, Domainlist


__all__ = ['init_config', 'Configuration']

CACHE_MAX_AGE = 10

class Configuration:
    def __init__(self, config, config_path: str):
        self.config = config
        self.config_path = Path(config_path)
        if self.config_path.exists():
            config_mtime = self.config_path.stat().st_mtime
        else:
            config_mtime = None
        self.config_mtime = config_mtime
        self.allowed = None
        self.blocked = None
        self.ruledir_cache = {'allowed': set(), 'blocked': set()}
        self.time_last_cache_check = None

    @classmethod
    def with_ini(cls, cfg_path: str):
        cfg = parse_config(cfg_path)
        return cls(config=cfg, config_path=cfg_path)

    @property
    def rule_basedir(self):
        basedir = self.config.get('rule_basedir', '/etc/filtering-proxy')
        path_basedir = Path(basedir)
        if path_basedir.is_absolute():
            return path_basedir
        return Path(self.config_path).parent / basedir

    @property
    def log(self):
        path_logfile = self.config.get('log_file')
        logger = Logger(__name__, level=logging.INFO)
        if not path_logfile:
            return logger
        file_ = logging.FileHandler(path_logfile)
        file_.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        logger.addHandler(file_)
        return logger

    def reload_if_necessary(self, *, force=False):
        config_path = Path(self.config_path)
        try:
            mtime = config_path.stat().st_mtime
        except FileNotFoundError:
            return
        if (not force) and mtime <= self.config_mtime:
            return
        self.log.info('config file "%s" was modified, reloading config', self.config_path)
        self.config = parse_config(self.config_path)
        self.config_mtime = mtime

    def is_allowed(self, domain: str):
        allowed = self._get_dl(allowed=True)
        if self.matches(domain, allowed):
            return True
        blocked = self._get_dl(blocked=True)
        if self.matches(domain, blocked):
            return False
        default_rule = self.config.get('default_rule', 'allow')
        return (default_rule.lower() == 'allow')

    def _get_dl(self, *, allowed=None, blocked=None):
        assert (allowed is not None) ^ (blocked is not None)
        attr_name = 'allowed' if allowed else 'blocked'
        dir_path = self.rule_basedir / f'{attr_name}.d'
        dls = getattr(self, attr_name)
        if dls is not None:
            cache = self.ruledir_cache[attr_name]
            if not self._is_cache_expired(cache, dir_path):
                return dls
            self.log.info('cache expired, reloading domain lists')

        if not dir_path.exists():
            return None
        self.ruledir_cache[attr_name] = self._build_cache_key_for_directory(dir_path)
        dls = parse_domainlists_from_directory(dir_path)
        setattr(self, attr_name, dls)
        return dls

    def _is_cache_expired(self, cache, path_rulesdir):
        if self.time_last_cache_check is not None:
            cache_age = time.time() - self.time_last_cache_check
            if cache_age < CACHE_MAX_AGE:
                return False
        current = self._build_cache_key_for_directory(path_rulesdir)
        return (current != cache)

    def _build_cache_key_for_directory(self, path_rulesdir):
        self.time_last_cache_check = time.time()
        try:
            with os.scandir(path_rulesdir) as dir_iter:
                current = {(entry.name, entry.stat().st_mtime) for entry in dir_iter}
        except FileNotFoundError:
            current = set()
        return current

    def matches(self, domain: str, dls: Iterable[Domainlist]):
        if not dls:
            return False
        for _dl in dls:
            if _dl.matches(domain):
                return True
        return False


def parse_config(cfg_path: str):
    if not cfg_path:
        return {
            'default_rule': 'allow',
            'reload_rules': 'false',
            'rule_basedir': '/etc/filtering-proxy',
        }
    config = ConfigParser()
    config.read(cfg_path)
    cfg_section = config['proxy']
    cfg = {
        'reload_rules': parse_bool(cfg_section.get('reload_rules', 'false')),
        'rule_basedir': cfg_section['rule_basedir'],
        'default_rule': cfg_section.get('default_rule'),
        'log_file': cfg_section.get('log_file'),
    }
    return cfg

def parse_bool(value_str):
    assert (value_str.lower() in ('true', 'false'))
    return (value_str.lower() == 'true')

def init_config(cfg_path: str) -> Configuration:
    return Configuration.with_ini(cfg_path)

