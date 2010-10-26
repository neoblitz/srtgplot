#!/usr/bin/python
# Simple real-time plotter using gnuplot
#  
# Usage: 
# ./srtgplot.py <conf_file>
#
# Copyright (C) 2010 Arun Viswanathan (arunv@arunviswanathan.com)
#This software is licensed under the GPLv3 license, included in
#./GPLv3-LICENSE.txt in the source distribution
#-------------------------------------------------------------------------------

import sys
import os
import time
import signal
import getopt
from threading import Thread
from plotthread import Plot
from plotconfig import PlotConfig

VERSION = "0.1"
DEFAULT_LOGDIR = "/tmp"
threadlist = []

def handler(signum, frame):
    '''
        Catch SIGTERM, SIGABRT and SIGINT signals
        and signal threads to cleanup and exit
    '''
    print "Got signal %d. Exiting ...\n" % (signum)
    for t in threadlist:
        if(t.isAlive()):
            t.set_ttl()

def copyright():
    print "srtgplot v%s" % (VERSION)
    print "Copyright (C) 2010 Arun Viswanathan"

def usage():
    copyright()
    print "\nUsage: ./%s --conf <config_file> [--help] [--logdir <logdirectory>]"\
                 % sys.argv[0]
    print """
        where
        config_file   : Configuration file in the format explained below.
        log_directory : Directory where captured data is stored. Files under
                        this directory will be of the format 
                        rtplot_<section_name_from_conf_file>_<randomstring>      
    """
    print "Use Ctrl-C to exit...."


def main():
    fn = ''
    # Parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   '',
                                  ['conf=', 'logdir=', 'help'])
    except getopt.error, msg:
        usage()
        sys.exit(2)

    conf = None
    help = None
    logdir = DEFAULT_LOGDIR
    # Process options
    for option, arg in opts:
        if option == '--conf':
          conf = arg
        elif option == '--help':
          usage()
          sys.exit(0)
        elif option == '--logdir':
          logdir = arg

    if not conf:
        usage()
        sys.exit()

    copyright()
    print "\nConfiguration File : %s" % (conf)
    print "Log Directory      : %s" % (logdir)
    print "\nUse Ctrl-C to exit...."

    if(not os.path.exists(conf)):
        print  "Error: Filename '", conf, "' does not exist ! Aborting !!"
        sys.exit(2)

    # Set the signal handlers
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGABRT, handler)

    # Read and initialize from the config file
    config = PlotConfig(conf)

    # Spawn a thread for each section in the INI file
    sections = config.get_sections()
    for secname in sections:
        tp = Plot(config, secname, logdir)
        threadlist.append(tp)

    for tp in threadlist:
        # Join with timeout allows threads to be interrupted
        # Refer to this discussion 
        # http://stackoverflow.com/questions/631441/interruptible-thread-join-in-python
        while(tp.isAlive()):
            tp.join(100)

if __name__ == '__main__':
        main()



