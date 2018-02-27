#!/bin/python
import os

from oslo_config import cfg
from oslo_log import log

from conductor import __file__ as conductor_root
from conductor import service
# from conductor.solver.optimizer import decision_path as dpath
from conductor.solver.optimizer import optimizer
from conductor.solver.request import request_simulator  # for simulation

LOG = log.getLogger(__name__)

CONF = cfg.CONF

SOLVER_OPTS = [
    cfg.StrOpt('template_file',
               default='template.json',
               help='Input template'),
    cfg.StrOpt('data_file',
               default='data.json',
               help='Input data'),
]

for opt in SOLVER_OPTS:
    CONF.register_cli_opt(opt, 'solver')


def main():
    path = os.path.abspath(conductor_root)
    dir_path = os.path.dirname(path)
    template_file = dir_path + '/tests/data/template1.json'
    data_file = dir_path + '/tests/data/data1.json'
    CONF.set_override('template_file', template_file, 'solver')
    CONF.set_override('data_file', data_file, 'solver')

    # Prepare service-wide components (e.g., config)
    conf = service.prepare_service()

    req_sim = request_simulator.RequestSimulator(conf)

    """for simulation"""
    req_sim.generate_requests(template=conf.solver.template_file,
                              data=conf.solver.data_file)
    opt = optimizer.Optimizer(conf, _requests=req_sim.requests)
    # opt.search.search()
    opt.get_solution()


if __name__ == "__main__":
    main()
