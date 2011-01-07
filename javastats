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


# Usage: javastats -c <config_file> [other options]
#
# All the required settings are encoded in the configuration file. 
# It has the following obligatory sections:
# [general]
# [stats]
# 
# Other sections provide information for the virtual machine, and benchmarks
#
# The following benchmark suites are currently supported:
# - SPECjvm98
# - DaCapo (settings for version 2006-10-MR2)
# - SPECjbb2000
# - PseudoJBB2000

# It should not be hard to add support for a new benchmark set. You simply add
# a section detailing the benchmark setup, and add the section name to the list
# in the general section, called 'benchmark suites'.

# When no other options are provided, javastats will run all the benchmarks on
# all the virtual machines given in the configuration file in startup
# configuration. If you wish to limit the execution to certain VMs, or
# benchmark sets, use the --suites, --vms or --benchmarks option and the
# execution will be limited to those configurations you list. If you decide on
# detailing specific benchmarks to execute, you should tag each benchmark with
# the suite it belongs to, e.g., --benchmarks specjvm98:_213_javac

import sys
import os
import subprocess
from optparse import OptionParser, make_option
import ConfigParser 
import math
import scipy.stats as stats
import scipy.stats.distributions as distributions


program_name = "javastats"

def usage(name):
  return "Usage: %s -c config [options]"%(name)


def parse_varargs_callback(option, opt, value, parser):
  # code taken from http://docs.python.org/lib/optparse-callback-example-6.html
  assert value is None
  values = []
  rargs = parser.rargs
  while rargs:
    arg = rargs[0]
    if (arg[:2] == '--' and len(arg) >= 2) or (arg[:1] == '-' and len(arg) > 1 and arg[1] != '-'):
      break
    else:
      values.append(arg)
      del rargs[0]

  setattr(parser.values, option.dest, values)


def define_options():
  from optparse import make_option
  optConfig = make_option("-c", "--config", dest="config", help="The name of the configuration file to use", default=os.path.expanduser("~/.%s.conf"%(program_name)))
  optSuites = make_option("-s", "--suites", dest="suites", help="The benchmark suites you wish to run. There should be a section [suite] in the configuration file for each suite you specify here.", action="callback", callback=parse_varargs_callback)
  optVMS    = make_option("-m", "--vms", dest="vms", help="The virtual machines you wish to use. There should be a section [vm] in the configuration file for each vm you specify here. For example [jikesrvm] if you use --vms jikesrvm.", action="callback", callback=parse_varargs_callback)
  optBenchmarks = make_option("-b", "--benchmarks", dest="benchmarks", help="The benchmarks you wish to run, if you decide not to run all those present in the given suites. Each benchmark must be tagged with the suite name, i.e., <suite>:<benchmark>", action="callback", callback=parse_varargs_callback)
  optInputs  = make_option("-i", "--inputs", dest="inputs", help="The input sets you wish to run, if you decide not to run all those present in the configuration file for each suite. Each input set must either be tagged with a suite name or a benchmark name. The latter overrides the former.", action="callback", callback=parse_varargs_callback) 
  optStartup = make_option("", "--startup", dest="startup", action="store_true", default=True)
  optSteady  = make_option("", "--steady", dest="steady", action="store_true", default=False)
  optPerformance = make_option("-p", "--performance", dest="performance", help="The performance class that provides the measurent (e.g., /usr/bin/time) and the trace file analysis methods.") 
  optSimulate = make_option("", "--simulate", dest="simulate", help="Simulate a run by using a predetermined list of performance data, i.e., no parsing will be done using the performance class")

  return [optConfig, optSuites, optVMS, optBenchmarks, optInputs, optStartup, optSteady, optPerformance, optSimulate]


def determine_vms(options, config):
  if options.vms is not None:
    vms = options.vms
  else:
    vms = config.get('general', 'virtual machines').split(" ")
  return vms

def determine_suites(options, config):
  if options.suites is not None:
    suites = options.suites
  else:
    suites = config.get('general', 'benchmark suites').split(" ")
  return suites

def add_to_list(d, k, v):
  try:
    l = d[k]
  except KeyError, e:
    l = []
  l.append(v)
  d[k] = l

def determine_benchmarks(options, config, suites):
  # The benchmarks are given with a suite tag, e.g., dacapo:antlr
  benchmarks = dict()
  if options.benchmarks is not None:
    for (t, b) in [tuple(c.split(":")) for c in options.benchmarks]:
      add_to_list(benchmarks, t, b)
  else:
    for suite in suites:
      benchmarks[suite] = config.get(suite, 'benchmarks').split(" ")
  return benchmarks

def determine_inputs(options, config, suites):
  # The inputs can be tagged with a suite tag, e.g., dacapo:default or a benchmark tag, 
  # e.g., _227_mtrt:s100
  inputs = dict()
  if options.inputs is not None:
    for (t,i) in [tuple(c.split(":")) for c in options.inputs]:
      add_to_list(inputs, t, i)
  for suite in suites:
    if not inputs.has_key(suite):
      inputs[suite] = config.get(suite, 'input sizes').split(" ")
  return inputs

def determine_run_information(options, config):

  # Performance measurement information
  performance_information = dict()
  performance_information['class'] = config.get('performance','class')
  if options.performance is not None:
    performance_information['class'] = options.performance

  trace_information = dict()
  trace_information['machine']  = config.get('trace','machine')
  trace_information['location'] = config.get('trace','location')
  trace_information['prefix']   = config.get('trace','prefix')

  stats_information = dict()
  stats_information['minimum vm invocations'] = int(config.get('stats', 'minimum vm invocations'))
  stats_information['maximum vm invocations'] = int(config.get('stats', 'maximum vm invocations'))
  stats_information['confidence level'] = float(config.get('stats', 'confidence level'))


  # By default, we will execute everything in the configuration file, i.e., 
  # all benchmarks, for all input sets, on all vms.

  # The vms are independent of the benchmarks
  vms        = determine_vms(options, config)

  # The suites limit the further possibilities
  suites     = determine_suites(options, config)

  # The benchmarks are stored first into a dictionary with the suite as the key
  benchmarks = determine_benchmarks(options, config, suites)

  # The inputs are stored into a dictionary with either the suite or benchmark as the key
  inputs = determine_inputs(options, config, suites)
  
  print "DEBUG: suites     ->", suites
  print "DEBUG: vms        ->", vms
  print "DEBUG: benchmarks ->", benchmarks
  print "DEBUG: inputs     ->", inputs

  # Given the benchmarks and inputs dictionaries, we can assemble the information required for each run
  benchmark_information = []
  for suite in benchmarks.keys():
    bs = benchmarks[suite]
    suite_input = inputs[suite]
    suite_location = config.get(suite, 'location')
    suite_ulimit = config.get(suite, 'ulimit threshold')  

    if options.steady:
      command = config.get(suite, 'steady command', True)
    else:
      command = config.get(suite, 'startup command', True)

    for b in bs:
      if inputs.has_key(b):
        b_input = inputs[b]
      else:
        b_input = suite_input

      for input in b_input:
        benchmark_information.append((b, suite, input, command, suite_location, suite_ulimit))

  vm_information = []
  for vm in vms:
    vm_location = config.get(vm, 'binary location')
    vm_binary = config.get(vm, 'binary name')
    vm_information.append((vm, vm_binary, vm_location))

  return (vm_information, benchmark_information, performance_information, trace_information, stats_information)


def stop_experiment(reason):
  print "Exepriments have been aborted. Reason:", reason
  sys.exit(-2)

#def determine_confidence_startup(filename, confidence_level = 0.95, percentage=1.0, provide_width = False, provide_count=False):

  ## read data
  #samples = map(lambda x: float(x), file(filename, 'r').readlines()[1:])
#
  ## the filename also happens to indicate which benchmark we're using with with GC and heapsize
  #fields = filename.split('_')
  #config = fields[0].replace('FastAdaptive','')
  #heap   = fields[1]
  #benchmark = "_".join(fields[2:]).replace('.parsed', '')
#
  #if provide_count:
    #(((interval_low, interval_high), mean, sdev, interval_percentage), n) = techniques.confidence_iteration_break_on_percentage(samples, confidence_level, percentage)
    #print "sample count %f %f %s %s %s %d"%(confidence_level, percentage, benchmark, config, heap, n)
#
  #if provide_width:
    #percentages = []
    #for k in range(2,len(samples)+1):
      #(i, m, s, p) = techniques.confidence_of_k(samples, confidence_level, k)
      #print "DEBUG: %d -> %lf"%(k, p)
      #percentages.append(p)
    #print "sample width %f %s %s %s %s"%(confidence_level, benchmark, config, heap, " ".join(map(lambda x: str(x), percentages)))



def confidence(samples, confidence_level):
  """This function determines the confidence interval for a given set of samples, 
  as well as the mean, the standard deviation, and the size of the confidence 
  interval as a percentage of the mean.
  """
  mean = stats.mean(samples)
  sdev = stats.std(samples)
  n    = len(samples)
  df   = n - 1
  t    = distributions.t.ppf((1+confidence_level)/2.0, df)
  interval = (interval_low, interval_high) = ( mean - t * sdev / math.sqrt(n) , mean + t * sdev / math.sqrt(n) )
  interval_size = interval_high - interval_low
  interval_percentage = interval_size / mean * 100.0
  return (interval, mean, sdev, interval_percentage) 


def simulate(stats_information, lines):
  
  values = [float(x.strip()) for x in lines]
  for k in range(stats_information['minimum vm invocations'], stats_information['maximum vm invocations'] + 1):
    ((low, high), mean, sdev, interval_percentage) = confidence(values, stats_information['confidence level'])
    if interval_percentage < stats_information['confidence level']:
      break

  print "Confidence interval for %d values %f +/- %f (= %f%%) = [%f; %f]"%(k, mean, (high - low)/2, interval_percentage, low, high)


def confidence_reached(stats_information, values):
  print "DEBUG: len(values): %d, min runs: %d, max runs: %d"%(len(values), int(stats_information['minimum vm invocations']), int(stats_information['maximum vm invocations']))
  if len(values) < int(stats_information['minimum vm invocations']):
    return False

  if len(values) >= int(stats_information['maximum vm invocations']):
    return True

  #print "DEBUG: values = ", values
  (interval, mean, sdev, interval_percentage) = confidence(values, stats_information['confidence level'])
  print "DEBUG: mean = %f, percentage = %f"%(mean, interval_percentage)
  if interval_percentage < stats_information['confidence level']:
    return True
  else:
    return False

def execute_run(vm_information, benchmark_information, performance_information, trace_information, stats_information):
 
  exec "from performance import %s as P"%(performance_information['class'])
  import os.path as path

  performance = P()

  (benchmark, suite, input, benchmark_command, benchmark_location, ulimit) = benchmark_information
  (vm, vm_binary, vm_location) = vm_information

  benchmark_command = benchmark_command%(dict(input=input, benchmark=benchmark))

  tracefile = path.join(trace_information['location'], trace_information['prefix']) 

  print "DEBUG: tracefile ->", tracefile

  command = ""
  command += "cd %s;"%(benchmark_location)
  command += "ulimit -t %s;"%(ulimit)
  command += performance.acquire_command("%s/%s %s"%(vm_location, vm_binary, benchmark_command))
  command += "> %s 2>&1;"%(tracefile)

  print "DEBUG: command = ", command

  performance_data = []
  erroneous_runs = 0
  consequent_erroneous_runs = 0
  termination_condition = False
  while not termination_condition:
    os.system(command)
    value = performance.get_performance_data(tracefile)
    if value is not None:
      performance_data.append(value)
      consequent_erroneous_runs = 0
    else:
      erroneous_runs += 1
      consequent_erroneous_runs += 1

    if consequent_erroneous_runs >= 3:
      stop_experiment('3 consequent erroneous runs')
    if erroneous_runs > len(performance_data) / 2:
      stop_experiment('over a third of all runs failed')

    print "DEBUG: value found = ", value
    termination_condition = confidence_reached(stats_information, performance_data)




def main(argv = None):
  if argv is None:
    argv = sys.argv


  # The single obligatory option is the config option, whose argument points to the 
  # configuration file. The other options can be used to pick selected items from the 
  # configuration file
  options, args = OptionParser(usage(argv[0]), define_options()).parse_args(argv[1:])
 
  print options
  print args

  if options.config is None:
    print usage(argv[0])
    return -1

  # Parse the configuration file
  config = ConfigParser.SafeConfigParser()
  config.read(options.config)

  (vms, benchmarks, performance, trace, stats) = determine_run_information(options, config)
 
  if options.simulate is not None:
    # do not execute any runs, but use a list of performance numbers to
    # determine the number of desired executions. the maximum is still
    # dependent on the stats section declared in the configuration file.
    f = file(options.simulate, 'r')
    simulate(stats, f.readlines())
    return 0


  for vm in vms:
    for benchmark in benchmarks:
      execute_run(vm, benchmark, performance, trace, stats)


  return 0


  determine_confidence_startup(options['--file'], confidence, percentage, provide_width, provide_count)
  determine_confidence_steady(options['--file'], confidence, percentage, provide_width, provide_count)


if __name__ == "__main__":
    sys.exit(main())
