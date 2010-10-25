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
    logdir = None
    # Process options
    for option, arg in opts:
        if option == '--conf':
          conf = arg
        elif option == '--help':
          help = True
        elif option == '--logdir':
          logdir = arg

    if not conf:
        print "Usage: %s --conf <config_file> [--help] [--logdir <logdirectory>]"\
                     % sys.argv[0]
        sys.exit()

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
        tp = Plot(config, secname)
        threadlist.append(tp)

    for tp in threadlist:
        # Join with timeout allows threads to be interrupted
        # Refer to this discussion 
        # http://stackoverflow.com/questions/631441/interruptible-thread-join-in-python
        while(tp.isAlive()):
            tp.join(100)

if __name__ == '__main__':
        main()



