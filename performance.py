#!/usr/bin/env python

# JavaStats is a toolkit designed to get a 
# statistically rigorous performance evaluation for a 
# given (Java) application
#
# Copyright (C) 2007 Andy Georges
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# This file implements several useful example snippets that can be used to
# return a desired performance number to the main JavaStats monitor. Basically,
# you need to implement two methods given in the Performance base class: 
# acquire_command and get_performance_data. The former will adjust the java
# run command and set it up to gather the desired data. The latter will examine
# the resulting trace file and fetch the desired data. 

import re

class Performance:
  """Performance is the base class for determining the performance
     according to some criterion (e.g., time, executed instruction,
     etc.) of a Java execution.
  """
  # regular expression that check if an error occured during a run
  # as well as the regex for the runtime in startup mode
  re_exception  = re.compile("[Ee]xception")
  re_error      = re.compile("Error")
  re_deadlock   = re.compile("deadlock")
  re_terminated = re.compile("terminated by") 
  re_non_zero   = re.compile("non_zero_status")
  re_stack      = re.compile("-- Stack --")
  re_failed     = re.compile("FAILED")
  re_not_valid  = re.compile("NOT VALID")

  def acquire_command(self, commmand):
    pass

  def get_performance_data(self, trace_filename):
    pass

  def sweep_line_for_error(self, line):
    """The sweep_line_for_error function will try to find selected regular 
       expressions in the line that indicate an error or unexpected situation
       occurred during the execution. If that is the case, the experiment
       should be discarded.
    """
    if self.re_exception.search(line):
      return True
    if self.re_error.search(line):
      return True
    if self.re_deadlock.search(line):
      return True
    if self.re_terminated.search(line):
      return True
    if self.re_non_zero.search(line):
      return True
    if self.re_stack.search(line):
      return True
    if self.re_failed.search(line):
      return True
    if self.re_not_valid.search(line):
      return True
  
    return False


class TimePerformance(Performance):
  
  re_realtime  = re.compile("^real")

  def acquire_command(self, java_command):
    return "/usr/bin/time -p %s"%(java_command)

  def get_performance_data(self, trace_filename):

    f = file(trace_filename, 'r')
    for line in f.readlines():
      if self.sweep_line_for_error(line):
        return None
      if self.re_realtime.search(line):
        return float(line.strip().split(" ")[-1])


class PerfexPerformance(Performance):
  re_perfctr_cycles       = re.compile("^event 0x00430076")

  def acquire_command(self, java_command):
    return "/home/ageorges/bin/perfex -e 0x00430076 %s"%(java_command)

  def get_performance_data(self, trace_filename):
    instruction = 0
    cycles = 0
    f = file(trace_filename, 'r')
    for line in f.readlines():
      if self.sweep_line_for_error(line):
        return None
      if self.re_perfctr_cycles.search(line):
        cycles = float(line.strip().split(" ")[-1])

    return cycles




