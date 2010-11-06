#!/usr/bin/python
# Simple real-time plotter using gnuplot
#  
# Usage: 
# ./srtgplot.py --conf <conf_file>
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
from plotconfig import PlotConfig, print_directives

VERSION = "0.2b"
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
    print "Copyright (C) 2010 Arun Viswanathan (arunv@arunviswanathan.com)"

def usage():
    copyright()
    print "\nUsage: %s --conf <config_file> [--logdir <dir>] [--list] [--help]"\
             % sys.argv[0]
    print "where"
    print "\t--conf <config_file> : Configuration file. See README for format."

    print "\t[--logdir <dir>] : Directory where captured data is stored unless"
    print "\t\t\toverridden using the 'logdir' directive in the config."
    print "\t\t\tBy default, log files created will be of the format"
    print "\t\t\trtplot_<section_name_from_conf_file>_<randomstring>)"
    print "\t\t\tunless overridden using the 'logfile' directive\n"

    print "\t[--list]        : Lists all available configuration directives with defaults."
    print "\t[--help]        : Print this help."

def main():
    fn = ''
    # Parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   '',
                                  ['conf=', 'logdir=', 'help', 'list'])
    except getopt.error, msg:
        usage()
        sys.exit(2)

    conf = None
    help = None
    listdirec = None
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
        elif option == '--list':
            print_directives()
            sys.exit(0)

    if not conf:
        usage()
        sys.exit()

    copyright()
    print "\nIMPORTANT: Use Ctrl-C to exit...."
    print "\nGlobal Configs:"
    print "\tConfiguration File : %s" % (conf)
    print "\tLog Directory      : %s" % (logdir)

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



