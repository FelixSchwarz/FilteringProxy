# -*- coding: UTF-8 -*-

from configparser import ConfigParser
from pathlib import Path
from typing import Iterable

from .domainlist import parse_domainlists_from_directory, Domainlist


__all__ = ['init_config', 'Configuration']

class Configuration:
    def __init__(self, config, config_path: str):
        self.config = config
        # just stored so the proxy can reload its configuration automatically
        # sometime in the future
        self.config_path = config_path
        self.allowed = None
        self.blocked = None

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
        dls = getattr(self, attr_name)
        if dls is not None:
            return dls

        dir_path = self.rule_basedir / f'{attr_name}.d'
        if not dir_path.exists():
            return None
        dls = parse_domainlists_from_directory(dir_path)
        setattr(self, attr_name, dls)
        return dls

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
            'rule_basedir': '/etc/filtering-proxy',
        }
    config = ConfigParser()
    config.read(cfg_path)
    cfg_section = config['proxy']
    cfg = {
        'rule_basedir': cfg_section['rule_basedir'],
        'default_rule': cfg_section['default_rule'],
    }
    return cfg

def init_config(cfg_path: str) -> Configuration:
    return Configuration.with_ini(cfg_path)

