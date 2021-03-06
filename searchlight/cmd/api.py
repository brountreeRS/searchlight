#!/usr/bin/env python

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Searchlight API Server
"""

import os
import sys

import eventlet
from oslo_utils import encodeutils


# Monkey patch socket, time, select, threads
eventlet.patcher.monkey_patch(socket=True, time=True, select=True,
                              thread=True, os=True)

# If ../searchlight/__init__.py exists, add ../ to Python search path, so that
# it will override what happens to be installed in /usr/(local/)lib/python...
possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                   os.pardir,
                                   os.pardir))
if os.path.exists(os.path.join(possible_topdir, 'searchlight', '__init__.py')):
    sys.path.insert(0, possible_topdir)

from oslo_config import cfg
from oslo_log import log as logging
import osprofiler.notifier
import osprofiler.web

from searchlight.common import config
from searchlight.common import exception
from searchlight.common import utils
from searchlight.common import wsgi
from searchlight import notifier
from searchlight import service_policies

CONF = cfg.CONF
CONF.import_group("profiler", "searchlight.common.wsgi")
CONF.import_group("api", "searchlight.common.wsgi")
logging.register_options(CONF)

KNOWN_EXCEPTIONS = (RuntimeError,
                    exception.WorkerCreationFailure)


def fail(e):
    global KNOWN_EXCEPTIONS
    return_code = KNOWN_EXCEPTIONS.index(type(e)) + 1
    sys.stderr.write("ERROR: %s\n" % encodeutils.exception_to_unicode(e))
    sys.exit(return_code)


def configure_wsgi():
    config.parse_args()
    config.set_config_defaults()
    logging.setup(CONF, 'searchlight')
    utils.register_plugin_opts()

    # Fail fast if service policy files aren't found
    service_policies.check_policy_files()

    if CONF.profiler.enabled:
        _notifier = osprofiler.notifier.create("Messaging",
                                               notifier.messaging, {},
                                               notifier.get_transport(),
                                               "searchlight", "search",
                                               CONF.api.bind_host)
        osprofiler.notifier.set(_notifier)
    else:
        osprofiler.web.disable()


def main():
    try:
        configure_wsgi()
        wsgi.set_eventlet_hub()
        server = wsgi.Server(workers=CONF.api.workers)
        server.start(config.load_paste_app('searchlight'),
                     default_port=9393)
        server.wait()
    except KNOWN_EXCEPTIONS as e:
        fail(e)


if __name__ == '__main__':
    main()
