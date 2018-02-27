import json
import logging
from conductor.common.music import api

class LoggerFilter(logging.Filter):
    transaction_id = None
    plan_id = None
    def filter(self, record):
        record.transaction_id = self.transaction_id
        record.plan_id = self.plan_id
        return True

def getTransactionId(keyspace, plan_id):
    """ get transaction id from a pariticular plan in MUSIC """
    rows = api.API().row_read(keyspace, "plans", "id", plan_id)
    for row_id, row_value in rows.items():
        template = row_value['template']
        if template:
            data = json.loads(template)
            if "transaction-id" in data:
                return data["transaction-id"]

def setLoggerFilter(logger, keyspace, plan_id):

    #formatter = logging.Formatter('%(asctime)s %(transaction_id)s %(levelname)s %(name)s: [-] %(plan_id)s %(message)s')
    generic_formatter = logging.Formatter('%(asctime)s|%(transaction_id)s|%(thread)d|%(levelname)s|%(module)s|%(name)s: [-] plan id: %(plan_id)s [-] %(message)s')
    audit_formatter = logging.Formatter('%(asctime)s|%(asctime)s|%(transaction_id)s||%(thread)d||Conductor|N/A|COMPLETE|200|sucessful||%(levelname)s|||0|%(module)s|||||||||%(name)s : [-] plan id: %(plan_id)s [-] %(message)s')
    metric_formatter = logging.Formatter('%(asctime)s|%(asctime)s|%(transaction_id)s||%(thread)d||Conductor|N/A|N/A|N/A|COMPLETE|200|sucessful||%(levelname)s|||0|%(module)s||||||||||%(name)s : [-] plan id: %(plan_id)s [-] %(message)s')
    error_formatter = logging.Formatter('%(asctime)s|%(transaction_id)s|%(thread)d|Conductor|N/A|N/A|N/A|ERROR|500|N/A|%(name)s : [-] plan id: %(plan_id)s [-] %(message)s')

    logger_filter = LoggerFilter()
    logger_filter.transaction_id = getTransactionId(keyspace, plan_id)
    logger_filter.plan_id = plan_id

    for handler in logger.logger.parent.handlers:
        if hasattr(handler, 'baseFilename') and "audit" in handler.baseFilename:
            handler.setFormatter(audit_formatter)
        elif hasattr(handler, 'baseFilename') and "metric" in handler.baseFilename:
            handler.setFormatter(metric_formatter)
        elif hasattr(handler, 'baseFilename') and "error" in handler.baseFilename:
            handler.setFormatter(error_formatter)
        else:
            handler.setFormatter(generic_formatter)
        handler.addFilter(logger_filter)