# -*- coding: UTF-8 -*-

import fnmatch
import re


__all__ = [
    'parse_domainlist',
    'parse_domainlists_from_directory',
    'Domainlist',
]

class Domainlist:
    def __init__(self, domains):
        self.domains = domains
        self._domain_regex = None

    def __repr__(self):
        return f'{self.__class__.__name__}({repr(self.domains)})'

    @property
    def domain_regex(self):
        # empty "self.domains" -> empty regex (which always matches)
        if (self._domain_regex is None) and self.domains:
            re_patterns = map(fnmatch.translate, self.domains)
            domain_patterns = '|'.join(re_patterns)
            self._domain_regex = re.compile(domain_patterns)
        return self._domain_regex

    def matches(self, domain):
        regex = self.domain_regex
        if not regex:
            return False
        return (self.domain_regex.match(domain) is not None)


def parse_domainlist(fp):
    domains = []
    for line_str in fp.readlines():
        domain_str = line_str.strip()
        if not domain_str:
            continue
        is_comment = re.search('^\s*#', domain_str)
        if is_comment:
            continue
        domains.append(domain_str)
    return Domainlist(domains)

def parse_domainlists_from_directory(dir_path):
    domainlists = []
    for dl_path in dir_path.glob('*.domains'):
        try:
            with dl_path.open('r') as dl_fp:
                dl = parse_domainlist(dl_fp)
        except FileNotFoundError:
            # e.g. dangling symlink
            continue
        domainlists.append(dl)
    return domainlists
