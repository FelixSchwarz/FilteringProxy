# -*- coding: UTF-8 -*-

from configparser import ConfigParser

from proxy.common.utils import build_http_request
from proxy.http.parser import HttpParser


__all__ = [
    'create_cfg_dirs',
    'create_config',
    'create_rule',
    'fake_request',
    'setup_configparser',
]

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
    print(f'created {rulefile_path}')

def fake_request(host):
    url = b'https://' + host + b'/foo'
    request_bytes = build_http_request(b'GET', url)
    request = HttpParser.request(request_bytes, enable_proxy_protocol=False)
    return request

