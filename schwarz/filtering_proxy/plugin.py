# -*- coding: UTF-8 -*-

from proxy.common.flag import flags
from proxy.http import httpStatusCodes as StatusCode
from proxy.http.exception import HttpRequestRejected
from proxy.http.proxy import HttpProxyBasePlugin

from .config import init_config


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
        if _config is None:
            _config = init_config(cfg_path=self.config_path)
            _config.log.info('loading config from file %s', _config.config_path)

        try:
            domain = request.host.decode("ASCII")
        except:
            # LATER: support non-ascii domains
            _config.log.warn('exception when decoding request host name %r, rejecting request', request.host)
            return reject_request()

        if _config is None:
            _config = init_config(config_path=self.config_path)
        _config.reload_if_necessary()
        host_str = str(request.host)[1:]
        if _config.is_allowed(domain):
            _config.log.debug(f'{domain} OK')
            return request
        _config.log.info(f'{domain} BLOCKED')
        return reject_request()


    @property
    def config_path(self):
        return getattr(self.flags, 'config', None)



def reject_request():
    raise HttpRequestRejected(
        status_code = StatusCode.FORBIDDEN,
        reason      = b'Domain not allowed',
        headers     = {
            b'Connection': b'close',
        }
    )

