# -*- coding: UTF-8 -*-

from proxy.http import httpStatusCodes as StatusCode
from proxy.http.exception import HttpRequestRejected
from proxy.http.proxy import HttpProxyBasePlugin

from .config import init_config
from proxy.common.flag import flags


__all__ = ['DomainFilterPlugin']

_config = None

flags.add_argument(
    'config',
    type=str,
    default=None,
    help='path of config file used to configure the filtering proxy',
)

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
                _config = init_config(self.flags.config)
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

