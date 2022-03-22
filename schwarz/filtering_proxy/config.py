# -*- coding: UTF-8 -*-

from pathlib import Path
from typing import Iterable

from .domainlist import parse_domainlists_from_directory, Domainlist


__all__ = ['init_config']

class Configuration:
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.allowed = None
        self.blocked = None

    def is_allowed(self, domain: str):
        allowed = self._get_dl(allowed=True)
        if self.matches(domain, allowed):
            return True
        blocked = self._get_dl(blocked=True)
        if self.matches(domain, blocked):
            return False
        return None

    def _get_dl(self, *, allowed=None, blocked=None):
        assert (allowed is not None) ^ (blocked is not None)
        attr_name = 'allowed' if allowed else 'blocked'
        dls = getattr(self, attr_name)
        if dls is not None:
            return dls

        dir_path = self.config_dir / f'{attr_name}.d'
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



def init_config() -> Configuration:
    config_dir = Path('.').absolute()
    return Configuration(config_dir)

