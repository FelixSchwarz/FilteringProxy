# -*- coding: UTF-8 -*-

from proxy import sleep_loop, Proxy


__all__ = ['run_filtering_proxy']

def run_filtering_proxy(argv):
    proxy_args = argv[1:]
    proxy_opts = {
        'plugins': ['schwarz.filtering_proxy.DomainFilterPlugin'],
    }
    with Proxy(proxy_args, **proxy_opts):
        sleep_loop()

