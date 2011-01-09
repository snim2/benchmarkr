#!/usr/bin/env python

"""
Benchmarkr.
#TODO Write this and a README.

Copyright (C) Sarah Mount, 2010.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import ConfigParser
import math
import os
import subprocess
import sys

from optparse import OptionParser
from optparse import OptionGroup

import scipy.stats as stats
import scipy.stats.distributions as distributions


__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__credits__ = 'Andy Georges'
__date__ = 'Jan 2011'


def configurator():
    """Set up command-line parser.
    """
    parser = OptionParser()

    parser.add_option('-e', '--command',
                      dest='cmd', 
                      action='store',
                      type='string',
                      help='command to be benchmarked')

    interpreter = OptionGroup(parser,
                              'Interpreter options',
                              'Configure the Python interpreter')
    interpreter.add_option('-r', '--recursion',
                           dest='recursionlimit', 
                           action='store',
                           default=sys.getrecursionlimit(),
                           type='int',
                           help='set the recursion limit on the Python interepreter')
    interpreter.add_option('-c', '--checkinterval',
                           dest='checkinterval', 
                           action='store',
                           default=sys.getcheckinterval(),
                           type='int',
                           help='set the check interval on the Python interepreter')
    parser.add_option_group(interpreter)
    
    repetitions = OptionGroup(parser,
                              'Repetition options',
                              'Control the number of times the benchmark is executed.')
    repetitions.add_option('-i', '--interval',
                           dest='interval', 
                           action='store',
                           default=0.95,
                           type='float',
                           help=('run benchmark until a given confidence interval ' +
                                 'has been obtained (must be between 0.0 and 1.0)'))
    repetitions.add_option('-n', '--num',
                           dest='num', 
                           default=1000000,
                           action='store',
                           type='int',
                           help='exact number of times to run the benchmark')
    parser.add_option_group(repetitions)
    
    return parser


def main():
    # Deal with command-line arguments
    parser = configurator()
    (options, args) = parser.parse_args()
    if options.cmd is None and args is None:
        print 'You must specify a command to benchmark.\n'
        parser.print_help()
        sys.exit(1)
    elif options.cmd is not None:
        cmd = options.cmd
    else:
        cmd = ' '.join(args)
    print 'You want to benchmark:', cmd
    
    # Configure interpreter
    sys.setrecursionlimit(options.recursionlimit)
    sys.setcheckinterval(options.checkinterval)
    
    parser.destroy()
    return


def confidence(samples, confidence_level):
    """This function determines the confidence interval for a given set of samples, 
    as well as the mean, the standard deviation, and the size of the confidence 
    interval as a percentage of the mean.

    From javastats by Andy Georges.
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
    """From javastats by Andy Georges.
    """
    values = [float(x.strip()) for x in lines]
    for k in range(stats_information['minimum vm invocations'], stats_information['maximum vm invocations'] + 1):
        ((low, high), mean, sdev, interval_percentage) = confidence(values, stats_information['confidence level'])
        if interval_percentage < stats_information['confidence level']:
            break

    print "Confidence interval for %d values %f +/- %f (= %f%%) = [%f; %f]"%(k, mean, (high - low)/2, interval_percentage, low, high)


def confidence_reached(stats_information, values):
    """From javastats by Andy Georges.
    """
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



if __name__ == '__main__':
    main()
