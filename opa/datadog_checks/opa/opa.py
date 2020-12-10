# (C) Datadog, Inc. 2020
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
from datadog_checks.base import ConfigurationError, OpenMetricsBaseCheck
from typing import Any

METRIC_MAP = {
    'http_request_duration_seconds': 'request.duration',
}

class OpaCheck(OpenMetricsBaseCheck):
    DEFAULT_METRIC_LIMIT = 0


    def __init__(self, name, init_config, instances=None):
        default_instances = {'opa': {'metrics': [METRIC_MAP], 'send_distribution_sums_as_monotonic': 'true', 'send_distribution_counts_as_monotonic': 'true'}}

        super(OpaCheck, self).__init__(
            name, init_config, instances, default_instances=default_instances, default_namespace='opa'
        )


    def _http_check(self, url, check_name):
        try:
            response = self.http.get(url)
            response.raise_for_status()
        except Exception as e:
            self.service_check(check_name, self.CRITICAL, message=str(e))
        else:
            if response.status_code == 200:
                self.service_check(check_name, self.OK)
            else:
                self.service_check(check_name, self.WARNING)


    def check(self, instance):
        health_url = instance.get("health_url")
        if health_url is None:
            raise ConfigurationError("Each instance must have a url to the health service")

        plugins_url = health_url + "?plugins"
        bundles_url = health_url + "?bundles"

        # General service health
        self._http_check(health_url, 'opa.health')
        # Bundles activation status
        self._http_check(bundles_url, 'opa.bundles_health')
        # Plugins status
        self._http_check(plugins_url, 'opa.plugins_health')

        super(OpaCheck, self).check(instance)
