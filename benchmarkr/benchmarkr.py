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

import sys
import os
import subprocess
from optparse import OptionParser, make_option
import ConfigParser 
import math
import scipy.stats as stats
import scipy.stats.distributions as distributions


__author__ = 'Sarah Mount <s.mount@wlv.ac.uk>'
__credits__ = 'Andy Georges'
__date__ = 'Jan 2011'


def main():
    return


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



if __name__ == '__main__':
    main()
