#!/usr/bin/python
# Simple realtime plotter using gnuplot
#  
# Usage: 
# ./simplertplot.py --conf <config_file_name> [--nrt <plotfile>] 
#                   [--logdir <dir>]  
#
# Copyright (c) Arun Viswanathan
#-------------------------------------------------------------------------------

import sys
import os
import tempfile
import subprocess
import time
import commands
import signal
import ConfigParser

from threading import Thread
from utils import which

GNUPLOT = 'gnuplot'
DEFAULT_MINY = 0
DEFAULT_MAXY = "*"
DEFAULT_TITLE = "Real-time plot"
DEFAULT_FREQ = 1
DEFAULT_SHOWPLOT = 1

# Gnuplot options
GP_OPTIONS = """ 
set xdata time;
set timefmt \"%%H:%%M:%%S\";
set tics nomirror;
set yrange [%s:%s];
set autoscale x;
set title \"%s\" font "Sans Serif,14"; """

DEPLIST = ["gnuplot"]
TIME_TO_LEAVE = False
MAX_POINTS = 100

class plotoutput(Thread):

    def __init__(self, secname, options):
        Thread.__init__(self)
        self.secname = secname
        self.options = options

    def run(self):
        print "Processing %s" % (self.secname)
        kvhash = {}
        for k, v in self.options:
            kvhash[k] = v

        freq = float(kvhash.get("frequency", DEFAULT_FREQ))
        miny = kvhash.get("miny", DEFAULT_MINY)
        maxy = kvhash.get("maxy", DEFAULT_MAXY)
        title = kvhash.get("title", DEFAULT_TITLE)
        showplot = int(kvhash.get("showplot", DEFAULT_SHOWPLOT))
        command = kvhash.get("command", '')
        if not command:
            print "'command' option for section %s is empty !" % (cmd)
            return

        (handle, fnameout) = tempfile.mkstemp(prefix="rtplot_" + self.secname);
        print "Collected plot data for '%s' saved in '%s' (frequency: %d) " % \
             (self.secname, fnameout, freq)

        # Open a pipe to gnuplot
        if(showplot):
            gp = subprocess.Popen([GNUPLOT], stdin=subprocess.PIPE, shell=True);
            gp.stdin.write(GP_OPTIONS % (miny, maxy, title));

        data = []
        while True:
            global TIME_TO_LEAVE
            if(TIME_TO_LEAVE):
                os.close(handle)
                break
            else:
                (status, output) = commands.getstatusoutput("""%s""" % \
                                                             (command));
                if(TIME_TO_LEAVE):
                    break
                if (status > 0):
                    print "Error while executing %s!" % (command)
                    print "Error Code: %d\n Output: %s" % (status, output)
                    break
                os.write(handle, output + "\n")

                if(showplot):
                    data.append(output + "\n")
                    gp.stdin.write("plot \"-\" using 1:2 notitle w lines\n");
                    start_index = len(data) - MAX_POINTS
                    if(start_index < 0):
                        start_index = 0
                    else:
                        del data[0:start_index - 1]

                    for d in data[start_index:]:
                        gp.stdin.write(d)
                    gp.stdin.write("e\n")
                time.sleep(freq)


def handler(signum, frame):
    global TIME_TO_LEAVE
    print "Got signal %d. Exiting ...\n" % (signum)
    TIME_TO_LEAVE = True

def main():
    fn = ''
    if len(sys.argv) < 2 or sys.argv[1] == "-h":
        print "Usage: %s <config_file> " % sys.argv[0]
        sys.exit()
    else:
        fn = sys.argv[1]

    if(not os.path.exists(fn)):
        print  "Error: Filename '", fn, "' does not exist ! Aborting !!"
        sys.exit(2)

    # Set the signal handlers
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGABRT, handler)

    # Test all required dependencies
    for program in DEPLIST:
        path = which(program)
        if path is None:
            print "Required dependency " + program + " not found in PATH!"
            sys.exit(1)

    # Read the configuration file
    config = ConfigParser.RawConfigParser()
    # The following option is important to prevent configparser 
    # from converting everything to lowercase
    config.optionxform = str
    config.read(fn)

    # Spawn a thread for each section in the INI file
    sections = config.sections()
    threadlist = []
    for secname in sections:
        tp = plotoutput(secname, config.items(secname))
        threadlist.append(tp)
        tp.start()

    for tp in threadlist:
        # Join with timeout allows threads to be interrupted
        # Refer to this discussion 
        # http://stackoverflow.com/questions/631441/interruptible-thread-join-in-python
        while(tp.isAlive()):
            tp.join(100)

if __name__ == '__main__':
        main()



