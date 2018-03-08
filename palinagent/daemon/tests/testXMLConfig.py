#! /usr/bin/env python
# -*- coding: UTF-8 -*-
#################################################################
#
# ProActive Parallel Suite(TM): The Java(TM) library for
#    Parallel, Distributed, Multi-Core Computing for
#     Enterprise Grids & Clouds
#
# Copyright (C) 1997-2010 ActiveEon 
# Contact: proactive@ow2.org or contact@activeeon.com
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 3 of
# the License.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
# USA
#
# If needed, contact us to obtain a release under GPL Version 2 
# or a different license than the GPL.
#
#  Initial developer(s):               The ActiveEon Team
#  Contributor(s):
#
#################################################################
# $$ACTIVEEON_INITIAL_DEV$$
#################################################################
import unittest
import os
import subprocess
import tempfile
import random
import sys

import helpers
import palinagent.daemon.main
import palinagent.daemon.action
from palinagent.daemon.errors import AgentConfigFileError


class TestValideAllXMLInProject(unittest.TestCase):
    '''
    Check that all XML files in the project validate against the agent schema
    '''
    def test_validate_all_xml(self):
        def must_check(fname):
            if fname.find('invalid') != -1:
                return False
            if fname.find("TEST-") != -1:
                return False
            if fname.endswith("coverage.xml"):
                return False
            return True
            
        
        invalid_files = []
        for root, dirs, files in os.walk(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../../")):
            for file in files:
                if file.endswith(".xml") and  must_check(file) :
                    try:
                        _check_validity_with_xmllint(os.path.join(root, file))
                    except (Exception):
                        invalid_files.append(os.path.join(root, file))
         
            for dir in ['.git', '.svn', 'doc', 'build', 'dist', '.idea', 'blackbox']:
                if dir in dirs:
                    dirs.remove(dir)

        if len(invalid_files) != 0:
            self.fail("Some XML files are invalid: %s" % invalid_files)


class TestHelpersXMLFile(unittest.TestCase):
    '''
    Generate various XML configuration files:
      - Check they are valid
      - Check the daemon is able to parse them
    '''    
    def setUp(self):
        self.file = None
    
    def test_simple_config_file(self):
        (config, events, connection) = _get_simplest_config()
        self.file = helpers.write_config_file(config, events, connection)
        _check_validity_with_xmllint(self.file)
        palinagent.daemon.main._parse_config_file(self.file)

    def test_several_events_config_file(self):
        config = helpers.ConfigElement()
        config.java_home = "invalid"
        config.proactive_home = "invalid"
      
        event = helpers.EventElement()
        event.start    = helpers.EventStartElement("Monday", '0', "0", "0")
        event.duration = helpers.EventDurationElement(0, 0, 0, 1)
        events = [event, event, event, event]
        
        connection = helpers.CustomConnectionElement()
        connection.java_starter_class = "invalid"
        
        self.file = helpers.write_config_file(config, events, connection)
        _check_validity_with_xmllint(self.file)
        palinagent.daemon.main._parse_config_file(self.file)

    def test_wrong_namespace_config_file(self):
        (config, events, connection) = _get_simplest_config()
        self.file = helpers.write_config_file(config, events, connection)
            
        # Change the namespace
        updated_fname = tempfile.mktemp()
        updated = open(updated_fname, 'w')
        orig = open(self.file, 'r')
        for line in orig.readlines():
            updated.write(line.replace(palinagent.daemon.main.xmlns, "invalid:name:space"))
        orig.close()
        updated.close()
        os.remove(self.file)
        self.file = updated_fname
        
        self.assertRaises(AgentConfigFileError, palinagent.daemon.main._parse_config_file, self.file)

    def test_malformed_config_file(self):
        (config, events, connection) = _get_simplest_config()
        self.file = helpers.write_config_file(config, events, connection)
            
        # Randomly removed some lines
        updated_fname = tempfile.mktemp()
        updated = open(updated_fname, 'w')
        orig = open(self.file, 'r')
        for line in orig.readlines():
            if random.randint(0, 10) < 9:
                updated.write(line.replace(palinagent.daemon.main.xmlns, "invalid:name:space"))
        orig.close()
        updated.close()
        os.remove(self.file)
        self.file = updated_fname
        
        self.assertRaises(AgentConfigFileError, palinagent.daemon.main._parse_config_file, self.file)

    def test_non_existant_config_xml(self):
        self.assertRaises(AgentConfigFileError, palinagent.daemon.main._parse_config_file, "/very/invalid/path/")
  
    
    def test_no_enabled(self):
        ''' Checks that an exception is thrown when no connection is enabled'''
        
        (config, events, connection) = _get_simplest_config()
        self.file = helpers.write_config_file(config, events, connection)
            
        # Randomly removed some lines
        updated_fname = tempfile.mktemp()
        updated = open(updated_fname, 'w')
        orig = open(self.file, 'r')
        for line in orig.readlines():
            updated.write(line.replace('enabled="true"' , 'enabled="false"'))
        orig.close()
        updated.close()
        os.remove(self.file)
        self.file = updated_fname
        
        tree = palinagent.daemon.main._parse_config_file(self.file)
        self.assertRaises(palinagent.daemon.errors.AgentConfigFileError, palinagent.daemon.action.parse, tree)

    def test_too_many_enabled(self):
        ''' Checks that an exception is thrown when several connections are enabled '''
        (config, events, connection) = _get_simplest_config()
        self.file = helpers.write_config_file(config, events, connection)
            
        # Randomly removed some lines
        updated_fname = tempfile.mktemp()
        updated = open(updated_fname, 'w')
        orig = open(self.file, 'r')
        for line in orig.readlines():
            updated.write(line.replace('</connections>' , '<localBind enabled="true"/></connections>'))
        orig.close()
        updated.close()
        os.remove(self.file)
        self.file = updated_fname
        
        tree = palinagent.daemon.main._parse_config_file(self.file)
        self.assertRaises(palinagent.daemon.errors.AgentConfigFileError, palinagent.daemon.action.parse, tree)
        
    def tearDown(self):
        try:
            if self.file is not None:
                os.remove(self.file)
        except (OSError), e:
            print e
        
        
    

def _get_simplest_config():
    config = helpers.ConfigElement()
    config.java_home = "invalid"
    config.proactive_home = "invalid"
  
    event = helpers.EventElement()
    event.start    = helpers.EventStartElement("Monday", '0', "0", "0")
    event.duration = helpers.EventDurationElement(0, 0, 0, 1)
    events = [event]
    
    connection = helpers.CustomConnectionElement()
    connection.java_starter_class = "invalid"
    
    return (config, events, connection)
            
def _check_validity_with_xmllint(file):
    argv = []
    argv.append('xmllint')
    argv.append('--noout')
    argv.append('--schema')
    argv.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../xsd/1.1/agent-linux.xsd"))
    argv.append(file)
    p = subprocess.Popen(argv, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    print stdout
    print >> sys.stderr, stderr
    if p.returncode != 0:
        raise Exception("XML file %s is not valid" % file)

if __name__ == '__main__':
    unittest.main()