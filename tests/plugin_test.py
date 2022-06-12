# -*- coding: UTF-8 -*-

from pathlib import Path

from proxy.http.exception import HttpRequestRejected
from pythonic_testcase import *
from schwarz.fakefs_helpers import FakeFS

from schwarz.filtering_proxy import DomainFilterPlugin
import schwarz.filtering_proxy.plugin
from schwarz.filtering_proxy.test_helpers import *


class PluginTest(PythonicTestCase):
    def setUp(self):
        self.fs = FakeFS.set_up(test=self)
        self.base_path = Path(self.fs.create_dir('data').path)
        create_cfg_dirs(self.base_path)
        self.config_path = self.base_path/'cfg'/'proxy.cfg'
        schwarz.filtering_proxy.plugin._config = None

    def tearDown(self):
        schwarz.filtering_proxy.plugin._config = None

    def test_can_allow_or_deny_based_on_configuration(self):
        create_config(self.config_path, rule_basedir=self.base_path, default_rule='block')
        create_rule('good-site.example', allow=True, rule_basedir=self.base_path)

        plugin = self._plugin()
        assert_false(self._is_domain_allowed(plugin, b'bad-site.example'))
        assert_true(self._is_domain_allowed(plugin, b'good-site.example'))

    # --- internal helpers ----------------------------------------------------
    def _plugin(self):
        class Flags:
            config = str(self.config_path)

        uid = None
        plugin = DomainFilterPlugin(uid, flags=Flags(), client=None, event_queue=None)
        return plugin

    def _is_domain_allowed(self, plugin, host):
        request = fake_request(host)
        try:
            plugin.before_upstream_connection(request)
        except HttpRequestRejected:
            return False
        return True
