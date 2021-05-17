#
# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
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

import cotyledon
from conductor.conductor.common.music.messaging import message
from conductor.conductor.common.music.model import base
from conductor.conductor.i18n import _LE, _LI  # pylint: disable=W0212
import futurist
import inspect
from oslo_config import cfg
from oslo_log import log
from oslo_messaging._drivers import common as rpc_common
import socket
import sys
import time


LOG = log.getLogger(__name__)

CONF = cfg.CONF

MESSAGING_SERVER_OPTS = [
    cfg.StrOpt('keyspace',
               default='conductor_rpc',
               help='Music keyspace for messages'),
    cfg.IntOpt('check_interval',
               default=1,
               min=1,
               help='Wait interval while checking for a message response. '
                    'Default value is 1 second.'),
    cfg.IntOpt('response_timeout',
               default=120,
               min=1,
               help='Overall message response timeout. '
                    'Default value is 120 seconds.'),
    cfg.IntOpt('timeout',
               default=300,
               min=1,
               help='Timeout for detecting a VM is down, and other VMs can pick the plan up. '
                    'Default value is 5 minutes. (integer value)'),
    cfg.IntOpt('workers',
               default=1,
               min=1,
               help='Number of workers for messaging service. '
                    'Default value is 1.'),
    cfg.IntOpt('polling_interval',
               default=1,
               min=1,
               help='Time between checking for new messages. '
                    'Default value is 1.'),
    cfg.BoolOpt('debug',
                default=False,
                help='Log debug messages. '
                     'Default value is False.'),
]

CONF.register_opts(MESSAGING_SERVER_OPTS, group='messaging_server')

# Some class/method descriptions taken from this Oslo Messaging
# RPC API Tutorial/Demo: https://www.youtube.com/watch?v=Bf4gkeoBzvA

RPCSVRNAME = "Music-RPC Server"


class Target(object):
    """Returns a messaging target.

    A target encapsulates all the information to identify where a message
    should be sent or what messages a server is listening for.
    """
    _topic = None
    _topic_class = None

    def __init__(self, topic):
        """Set the topic and topic class"""
        self._topic = topic

        # Because this is Music-specific, the server is
        # built-in to the API class, stored as the transport.
        # Thus, unlike oslo.messaging, there is no server
        # specified for a target. There also isn't an
        # exchange, namespace, or version at the moment.

        # Dynamically create a message class for this topic.
        self._topic_class = base.create_dynamic_model(
            keyspace=CONF.messaging_server.keyspace,
            baseclass=message.Message, classname=self.topic)

        if not self._topic_class:
            raise RuntimeError("Error setting the topic class for the messaging layer.")

    @property
    def topic(self):
        """Topic Property"""
        return self._topic

    @property
    def topic_class(self):
        """Topic Class Property"""
        return self._topic_class


class RPCClient(object):
    """Returns an RPC client using Music as a transport.

    The RPC client is responsible for sending method invocations
    to remote servers via a messaging transport.

    A method invocation consists of a request context dictionary
    a method name, and a dictionary of arguments. A cast() invocation
    just sends the request and returns immediately. A call() invocation
    waits for the server to send a return value.
    """

    def __init__(self, conf, transport, target):
        """Set the transport and target"""
        self.conf = conf
        self.transport = transport
        self.target = target
        self.RPC = self.target.topic_class

        # introduced as a quick means to cache messages
        # with the aim of preventing unnecessary communication
        # across conductor components.
        # self.message_cache = dict()

    def __check_rpc_status(self, rpc_id, rpc_method):
        """Check status for a given message id"""
        # Wait check_interval seconds before proceeding
        check_interval = self.conf.messaging_server.check_interval
        time.sleep(check_interval)
        if self.conf.messaging_server.debug:
            LOG.debug("Checking status for message {} method {} on "
                      "topic {}".format(rpc_id, rpc_method, self.target.topic))
        rpc = self.RPC.query.one(rpc_id)
        return rpc

    def cast(self, ctxt, method, args):
        """Asynchronous Call"""
        rpc = self.RPC(action=self.RPC.CAST,
                       ctxt=ctxt, method=method, args=args)
        assert(rpc.enqueued)

        rpc_id = rpc.id
        topic = self.target.topic
        LOG.info(
            _LI("Message {} on topic {} enqueued").format(rpc_id, topic))
        if self.conf.messaging_server.debug:
            LOG.debug("Casting method {} with args {}".format(method, args))

        return rpc_id

    def call(self, ctxt, method, args):
        """Synchronous Call"""
        # # check if the call has a message saved in cache
        # # key: string concatenation of ctxt + method + args
        # # value: rpc response object
        # key = ""
        # for k, v in ctxt.items():
        #     key += str(k)
        #     key += '#' + str(v) + '#'
        # key += '|' + str(method) + '|'
        # for k, v in args.items():
        #     key += str(k)
        #     key += '#' + str(v) + '#'
        #
        # # check if the method has been called before
        # # and cached
        # if key in self.message_cache:
        #     LOG.debug("Retrieved method {} with args "
        #               "{} from cache".format(method, args))
        #     return self.message_cache[key]

        rpc_start_time = time.time()

        rpc = self.RPC(action=self.RPC.CALL,
                       ctxt=ctxt, method=method, args=args)

        # TODO(jdandrea): Do something if the assert fails.
        assert(rpc.enqueued)

        rpc_id = rpc.id
        topic = self.target.topic
        LOG.info(
            _LI("Message {} on topic {} enqueued.").format(rpc_id, topic))
        if self.conf.messaging_server.debug:
            LOG.debug("Calling method {} with args {}".format(method, args))

        # Check message status within a thread
        executor = futurist.ThreadPoolExecutor()
        started_at = time.time()
        while (time.time() - started_at) <= self.conf.messaging_server.response_timeout:
            fut = executor.submit(self.__check_rpc_status, rpc_id, method)
            rpc = fut.result()
            if rpc and rpc.finished:
                if self.conf.messaging_server.debug:
                    LOG.debug("Message {} method {} response received".
                              format(rpc_id, method))
                break
        executor.shutdown()

        # Get response, delete message, and return response
        if not rpc or not rpc.finished:
            LOG.error(_LE("Message {} on topic {} timed out at {} seconds").
                      format(rpc_id, topic,
                             self.conf.messaging_server.response_timeout))
        elif not rpc.ok:
            LOG.error(_LE("Message {} on topic {} returned an error").
                      format(rpc_id, topic))
        response = rpc.response
        failure = rpc.failure
        rpc.delete()  # TODO(jdandrea): Put a TTL on the msg instead?
        # self.message_cache[key] = response

        LOG.debug("Elapsed time: {0:.3f} sec".format(
            time.time() - rpc_start_time)
        )
        # If there's a failure, raise it as an exception
        allowed = []
        if failure is not None and failure != '':
            # TODO(jdandrea): Do we need to populate allowed(_remote_exmods)?
            raise rpc_common.deserialize_remote_exception(failure, allowed)
        return response


class RPCService(cotyledon.Service):
    """Listener for the RPC service.

    An RPC Service exposes a number of endpoints, each of which contain
    a set of methods which may be invoked remotely by clients over a
    given transport. To create an RPC server, you supply a transport,
    target, and a list of endpoints.

    Start the server with server.run()
    """

    # This will appear in 'ps xaf'
    name = RPCSVRNAME

    def __init__(self, worker_id, conf, **kwargs):
        """Initializer"""
        super(RPCService, self).__init__(worker_id)
        if conf.messaging_server.debug:
            LOG.debug("%s" % self.__class__.__name__)
        self._init(conf, **kwargs)
        self.running = True

    def _init(self, conf, **kwargs):
        """Prepare to process requests"""
        self.conf = conf
        self.rpc_listener = None
        self.transport = kwargs.pop('transport')
        self.target = kwargs.pop('target')
        self.endpoints = kwargs.pop('endpoints')
        self.flush = kwargs.pop('flush')
        self.kwargs = kwargs
        self.RPC = self.target.topic_class
        self.name = "{}, topic({})".format(RPCSVRNAME, self.target.topic)

        self.messaging_owner_condition = {
            "owner": socket.gethostname()
        }

        self.enqueued_status_condition = {
            "status": message.Message.ENQUEUED
        }

        self.working_status_condition = {
            "status": message.Message.WORKING
        }

        if self.flush:
            self._flush_enqueued()

    def _flush_enqueued(self):
        """Flush all messages with an enqueued status.

        Use this only when the parent service is not running concurrently.
        """

        msgs = self.RPC.query.all()
        for msg in msgs:
            if msg.enqueued:
                if 'plan_name' in list(msg.ctxt.keys()):   # Python 3 Conversion -- dict object to list object
                    LOG.info('Plan name: {}'.format(msg.ctxt['plan_name']))
                elif 'plan_name' in list(msg.args.keys()):    # Python 3 Conversion -- dict object to list object
                    LOG.info('Plan name: {}'.format(msg.args['plan_name']))
                msg.delete()

    def _log_error_and_update_msg(self, msg, error_msg):
        LOG.error(error_msg)
        msg.response = {
            'error': {
                'message': error_msg
            }
        }
        msg.status = message.Message.ERROR
        msg.update(condition=self.messaging_owner_condition)

    def current_time_seconds(self):
        """Current time in milliseconds."""
        return int(round(time.time()))

    def millisec_to_sec(self, millisec):
        """Convert milliseconds to seconds"""
        return millisec / 1000

    def __check_for_messages(self):
        """Wait for the polling interval, then do the real message check."""

        # Wait for at least poll_interval sec
        polling_interval = self.conf.messaging_server.polling_interval
        time.sleep(polling_interval)
        if self.conf.messaging_server.debug:
            LOG.debug("Topic {}: Checking for new messages".format(
                self.target.topic))
        self._do()
        return True

    # FIXME(jdandrea): Better name for this, please, kthx.
    def _do(self):
        """Look for a new RPC call and serve it"""
        # Get all the messages in queue
        msgs = self.RPC.query.all()
        for msg in msgs:
            # Find the first msg marked as enqueued.

            if msg.working and \
                    (self.current_time_seconds() - self.millisec_to_sec(msg.updated))\
                    > self.conf.messaging_server.response_timeout:
                msg.status = message.Message.ENQUEUED
                msg.update(condition=self.working_status_condition)

            if not msg.enqueued:
                continue
            if 'plan_name' in list(msg.ctxt.keys()):   # Python 3 Conversion -- dict object to list object
                LOG.info('Plan name: {}'.format(msg.ctxt['plan_name']))
            elif 'plan_name' in list(msg.args.keys()):    # Python 3 Conversion -- dict object to list object
                LOG.info('Plan name: {}'.format(msg.args['plan_name']))

            # Change the status to WORKING (operation with a lock)
            msg.status = message.Message.WORKING
            msg.owner = socket.gethostname()
            # All update should have a condition (status == enqueued)
            _is_updated = msg.update(condition=self.enqueued_status_condition)

            if not _is_updated or 'FAILURE' in _is_updated:
                continue

            # RPC methods must not start/end with an underscore.
            if msg.method.startswith('_') or msg.method.endswith('_'):
                error_msg = _LE("Method {} must not start or end"
                                "with underscores").format(msg.method)
                self._log_error_and_update_msg(msg, error_msg)
                return

            # The first endpoint that supports the method wins.
            method = None
            for endpoint in self.endpoints:
                if msg.method not in dir(endpoint):
                    continue
                endpoint_method = getattr(endpoint, msg.method)
                if callable(endpoint_method):
                    method = endpoint_method
                    if self.conf.messaging_server.debug:
                        LOG.debug("Message {} method {} is "
                                  "handled by endpoint {}".
                                  format(msg.id, msg.method,
                                         method.__str__.__name__))
                    break
            if not method:
                error_msg = _LE("Message {} method {} unsupported "
                                "in endpoints.").format(msg.id, msg.method)
                self._log_error_and_update_msg(msg, error_msg)
                return

            # All methods must take a ctxt and args param.
            if inspect.getfullargspec(method).args != ['self', 'ctx', 'arg']:
                error_msg = _LE("Method {} must take three args: "
                                "self, ctx, arg").format(msg.method)
                self._log_error_and_update_msg(msg, error_msg)
                return

            LOG.info(_LI("Message {} method {} received").format(
                msg.id, msg.method))
            if self.conf.messaging_server.debug:
                LOG.debug(
                    _LI("Message {} method {} context: {}, args: {}").format(
                        msg.id, msg.method, msg.ctxt, msg.args))

            failure = None
            try:

                # Add the template to conductor.plan table
                # Methods return an opaque dictionary
                result = method(msg.ctxt, msg.args)

                # FIXME(jdandrea): Remove response/error and make it opaque.
                # That means this would just be assigned result outright.
                msg.response = result.get('response', result)
            except Exception:
                # Current sys.exc_info() content can be overridden
                # by another exception raised by a log handler during
                # LOG.exception(). So keep a copy and delete it later.
                failure = sys.exc_info()

                # Do not log details about the failure here. It will
                # be returned later upstream.
                LOG.exception(_LE('Exception during message handling'))

            try:
                if failure is None:
                    msg.status = message.Message.COMPLETED
                else:
                    msg.failure = \
                        rpc_common.serialize_remote_exception(failure)
                    msg.status = message.Message.ERROR
                LOG.info(_LI("Message {} method {}, status: {}").format(
                    msg.id, msg.method, msg.status))
                if self.conf.messaging_server.debug:
                    LOG.debug("Message {} method {}, response: {}".format(
                        msg.id, msg.method, msg.response))

                _is_success = 'FAILURE'
                while 'FAILURE' in _is_success and (self.current_time_seconds() - self.millisec_to_sec(msg.updated)) <= self.conf.messaging_server.response_timeout:
                    _is_success = msg.update()
                    LOG.info(_LI("updating the message status from working to {}, "
                                 "atomic update response from MUSIC {}").format(msg.status, _is_success))

            except Exception:
                LOG.exception(_LE("Can not send reply for message {} "
                                  "method {}").
                              format(msg.id, msg.method))
            finally:
                # Remove circular object reference between the current
                # stack frame and the traceback in exc_info.
                del failure

    def _gracefully_stop(self):
        """Gracefully stop working on things"""
        pass

    def _restart(self):
        """Prepare to restart the RPC Server"""
        pass

    def run(self):
        """Run"""
        # The server listens for messages and calls the
        # appropriate methods. It also deletes messages once
        # processed.
        if self.conf.messaging_server.debug:
            LOG.debug("%s" % self.__class__.__name__)

        # Listen for messages within a thread
        executor = futurist.ThreadPoolExecutor()
        while self.running:
            fut = executor.submit(self.__check_for_messages)
            fut.result()
        executor.shutdown()

    def terminate(self):
        """Terminate"""
        if self.conf.messaging_server.debug:
            LOG.debug("%s" % self.__class__.__name__)
        self.running = False
        self._gracefully_stop()
        super(RPCService, self).terminate()

    def reload(self):
        """Reload"""
        if self.conf.messaging_server.debug:
            LOG.debug("%s" % self.__class__.__name__)
        self._restart()
