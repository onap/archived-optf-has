#
# -------------------------------------------------------------------------
#   Copyright (c) 2018 Intel Corporation Intellectual Property
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------
#

''' Prometheus metrics '''
from oslo_config import cfg
from oslo_log import log
from prometheus_client import Counter
from prometheus_client import start_http_server

LOG = log.getLogger(__name__)

CONF = cfg.CONF

METRICS_OPTS = [
    cfg.ListOpt('metrics_port',
               default=[8000, 8001, 8002, 8003, 8004],
               help='Prometheus Metrics Endpoint')
]

CONF.register_opts(METRICS_OPTS, group='prometheus')

MUSIC_VERSION = Counter('oof_music_version', 'Music Version', ['version'])

VNF_COMPUTE_PROFILES = Counter(
    'vnf_compute_profile',
    'Compute Profiles used by VNFs over time',
    ['customer_name', 'service_name', 'vnf_name', 'vnfc_name', 'flavor',
     'cloud_region']
)

VNF_FAILURE = Counter(
    'vnf_no_solution',
    'No Homing solution',
    ['customer_name', 'service_name']
)

VNF_SUB_OPTIMUM = Counter(
    'vnf_sub_optimum_solution',
    'VNFs with sub-optimum solution',
    ['customer_name', 'service_name', 'vnf_name', 'vnfc_name']
)

VNF_SCORE = Counter(
    'vnf_scores',
    'HPA Scores of vnf',
    ['customer_name', 'service_name', 'vnf_name', 'vnfc_name', 'hpa_score']
)

# HPA Matching stats
# TODO (dileep)
# Customer name is set as ONAP in R3.
# General rule of thumb - if label not available. Label=N/A
# Service name will be set as N/A for HPA metrics in R3.
# vnf_name and vnfc_name will be N/A.
# Currently this needs lots of changes. R4 will take care of this.
HPA_FLAVOR_MATCH_SUCCESSFUL = Counter(
    'flavor_match_successful',
    'Number of times there is successful flavor match',
    ['customer_name', 'service_name', 'vnf_name', 'vnfc_name', 'cloud_region',
     'flavor']
)

HPA_FLAVOR_MATCH_UNSUCCESSFUL = Counter(
    'flavor_match_unsuccessful',
    'Number of times there is unsuccessful flavor match',
    ['customer_name', 'service_name', 'vnf_name', 'vnfc_name', 'cloud_region',
     'flavor']
)

HPA_CLOUD_REGION_SUCCESSFUL = Counter(
    'cloud_region_successful',
    'Number of times cloud region is selected successfully',
    ['customer_name', 'service_name', 'cloud_region']
)

HPA_CLOUD_REGION_UNSUCCESSFUL = Counter(
    'cloud_region_unsuccessful',
    'Number of times no cloud region is selected',
    ['customer_name', 'service_name', 'cloud_region']
)


def _init_metrics(port_index):
    '''
    Method to start Prometheus metrics endpoint http server
    :param port_index: Used by splver, data, api, contorller
    services to start metrics endpoint without conflicting
    :return:
    '''
    start_http_server(int(CONF.prometheus.metrics_port[port_index]))
    LOG.info("Prometheus metrics endpoint started at {}".format(
        CONF.prometheus.metrics_port[port_index]))
