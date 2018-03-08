#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#################################################################
#
# ProActive Parallel Suite(TM): The Java(TM) library for
#    Parallel, Distributed, Multi-Core Computing for
#    Enterprise Grids & Clouds
#
# Copyright (C) 1997-2011 INRIA/University of
#                 Nice-Sophia Antipolis/ActiveEon
# Contact: proactive@ow2.org or contact@activeeon.com
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; version 3 of
# the License.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
# USA
#
# If needed, contact us to obtain a release under GPL Version 2 or 3
# or a different license than the AGPL.
#
#  Initial developer(s):               The ProActive Team
#                        http://proactive.inria.fr/team_members.htm
#  Contributor(s):
#
#################################################################
# $$ACTIVEEON_INITIAL_DEV$$
#################################################################

import tempfile

class ConfigElement(object):
    def __init__(self):
        self.proactive_home = None
        self.java_home      = None
        self.jvm_parameters = []
        self.memory_limit   = 0
        self.nb_runtimes    = 1
        self.protocol       = "rmi"
        self.port_range     = (1024, 65534)
        self.on_runtime_exit_script = None

class EventStartElement(object):
    def __init__(self, day, hour, minute, second):
        self.day    = day
        self.hour   = hour
        self.minute = minute
        self.second = second


class EventDurationElement(object):
    def __init__(self, days, hours, minutes, seconds):
        self.days    = days
        self.hours   = hours
        self.minutes = minutes
        self.seconds = seconds

        
class EventElement(object):
    def __init__(self, start = None, duration = None, config = None):
        self.start    = start
        self.duration = duration
        self.config   = config
        


class CustomConnectionElement(object):
    def __init__(self):
        self.respawn_increment  = 1
        self.java_starter_class = None 
        self.java_args          = []


def write_config_file(config, events, connection, file=tempfile.mktemp()):
    assert config is not None
    assert events is not None
    assert connection is not None
    
    output = open(file, "w")
    _write_header(output)
    _write_config(output, config)
    _write_events(output, events)
    _write_custom_connection(output, connection)
    _write_footer(output)
    output.close()
    return file

def _write_header(output):
    output.write('<?xml version="1.0"?>\n')
    output.write('<agent\n')
    output.write('xmlns="urn:proactive:agent:1.1:linux"\n')
    output.write('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n')
    output.write('xsi:schemaLocation="urn:proactive:agent:1.1:linux http://www.activeeon.com/public_content/schemas/proactive/agent/1.1/agent-linux.xsd">\n')

def _write_config(output, config):
    output.write('<config>\n')
    
    if config.proactive_home is not None:
        output.write('<proactiveHome>%s</proactiveHome>\n' % config.proactive_home)
    if config.java_home is not None:
        output.write('<javaHome>%s</javaHome>\n' % config.java_home)
    if len(config.jvm_parameters) > 0:
        output.write('<jvmParameters>\n')
        for param in config.jvm_parameters:
            output.write('<param>%s</param>\n' % param)
        output.write('<jvmParameters>\n')
    output.write('<nbRuntimes>%s</nbRuntimes>\n' % config.nb_runtimes)
    output.write('<protocol>%s</protocol>\n' % config.protocol)
    output.write('<portRange first="%s" last="%s" />\n' % (config.port_range[0], config.port_range[1]))
    if config.on_runtime_exit_script is not None:
        output.write('<onRuntimeExitScript>%s</onRuntimeExitScript>\n' % config.on_runtime_exit_script)

    output.write('</config>\n')

def _write_events(output, events):
    output.write('<events>\n')
    for event in events:
        output.write('<event>\n')
        output.write('<start    day="%s"  hour="%s"  minute="%s"  second="%s"/>\n' %  (event.start.day, event.start.hour, event.start.minute, event.start.second))
        output.write('<duration days="%s" hours="%s" minutes="%s" seconds="%s"/>\n' % (event.duration.days, event.duration.hours, event.duration.minutes, event.duration.seconds))
        if event.config is not None:
            _write_config(output, event.config)
        output.write('</event>\n')
    output.write('</events>\n')
    
def _write_custom_connection(output, connection):
    output.write('<connections>\n')
    output.write('<customConnection enabled="true">\n')
    output.write('<respawnIncrement>%s</respawnIncrement>\n' % connection.respawn_increment)
    output.write('<javaStarterClass>%s</javaStarterClass>\n' % connection.java_starter_class)
    if len(connection.java_args) > 0:
        output.write('<args>\n')
        for arg in connection.java_args:
            output.write('<arg>%s</arg>\n' % arg)
        output.write('</args>\n')
    output.write('</customConnection>\n')
    output.write('</connections>\n')

def _write_footer(output):
    output.write("</agent>\n")