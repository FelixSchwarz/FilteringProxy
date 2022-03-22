# -*- coding: UTF-8 -*-

from proxy.http import httpStatusCodes as StatusCode
from proxy.http.exception import HttpRequestRejected
from proxy.http.proxy import HttpProxyBasePlugin

from .config import init_config


__all__ = ['DomainFilterPlugin']

_config = None


class DomainFilterPlugin(HttpProxyBasePlugin):
    def before_upstream_connection(self, request):
        global _config
        try:
            domain = request.host.decode("ASCII")
        except:
            # LATER: support non-ascii domains
            pass
        else:
            if _config is None:
                _config = init_config()
            if _config.is_allowed(domain):
                return request
        return reject_request()



def reject_request():
    raise HttpRequestRejected(
        status_code = StatusCode.FORBIDDEN,
        reason      = b'Domain not allowed',
        headers     = {
            b'Connection': b'close',
        }
    )

