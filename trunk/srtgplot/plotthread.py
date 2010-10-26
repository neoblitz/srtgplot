# plotthread.py
#    Plotter thread for every section specified in the configuration file.
#    Specified command is run with the frequency specified, command output 
#    is logged to a file under the specified log directory (default: /tmp) 
#    and a gnuplot window plots real-time values collected.             
#
# Copyright (C) 2010 Arun Viswanathan (arunv@arunviswanathan.com)
#This software is licensed under the GPLv3 license, included in
#./GPLv3-LICENSE.txt in the source distribution
#------------------------------------------------------------------------------


import sys
import os
import tempfile
import time, datetime
import utils

import dateutil.parser
from threading import Thread
from collections import deque
from gnuplot import Gnuplot

class Plot(Thread):
    # Gnuplot options
    GP_OPTIONS = """ 
set xdata time;
set timefmt \"%s\";
set tics nomirror;
set yrange [%s:%s];
set autoscale x;
set title \"%s\" font "Sans Serif,14"; """

    def __init__(self, config, secname):
        Thread.__init__(self)
        self.secname = secname
        self.windowstart = 0
        self.windowend = 0
        self.config = config
        self.time_to_leave = False
        self.off_filehandle = None

        # Initialize attributes for the given secname
        self.config.init_attributes(secname)

        if not self.config.is_enabled():
            return

        # data is a dynamic buffer that holds data points over the specified 
        # plotwindow. A deque() is favoured over a [] because deques have O(1)
        # performance for popleft() and append() operations over O(n) of lists. 
        self.data = deque()

        # Create a temporary file for logging the command output
        (self.handle, self.fnameout) = \
         tempfile.mkstemp(prefix="rtplot_" + self.secname + "_",
                          dir=self.config.get_logdir());

        if(self.config.get_showplot()):
            self.gp = Gnuplot()
            self.gp.write(self.GP_OPTIONS % (self.config.get_timefmt(),
                           self.config.get_miny(),
                           self.config.get_maxy(),
                           self.config.get_title()));
        print "Plotting initialized for '%s' (logfile: '%s', frequency: %d)" % \
            (self.secname, self.fnameout, self.config.get_frequency())
        self.start()


    def get_curr_timewindow(self, datapoint):
        timestr = datapoint.split()[0]
        if(self.windowstart == 0):
            self.windowstart = dateutil.parser.parse(timestr)

        # Advance the windowend pointer
        self.windowend = dateutil.parser.parse(timestr)
        return(self.windowend - self.windowstart)

    def adjust_plotwindow(self, dp):
        if(not self.config.get_offline()):
            timediff = self.get_curr_timewindow(dp)
            if(timediff >= self.config.get_plotwindow()):
                self.data.popleft()

    def process_data(self, dp):
        procopt = self.config.get_processdata()
        if(procopt == 'reld'):
            (timestr, currval) = dp.split()
            currval = float(currval)
            if(len(self.data) == 0):
                self.prevvalue = currval
            diff = currval - self.prevvalue
            newdp = timestr + " " + str(diff) + "\n"
            self.data.append(newdp)
            self.prevvalue = currval
        else:
            self.data.append(dp)

    def set_ttl(self):
        self.time_to_leave = True

    def get_data(self):
        '''
            Return the data to be plotted 
        '''
        filename = self.config.get_offline()
        if(filename):
            if(self.off_filehandle == None):
                self.off_filehandle = open(filename, "r")
            return self.off_filehandle.xreadlines()
        else:
            # Execute the command
            cmd = self.config.get_command()
            (status, data) = utils.execute_command(cmd)
            if(status):
                raise Exception("Error while executing %s\n" % (cmd))
            else:
                return data, len(data)

    def log_data(self, data):
        if(not self.config.get_offline()):
            for d in data:
                os.write(self.handle, d + "\n")


    def run(self):
        print "Processing %s" % (self.secname)
        cmd = self.config.get_command()
        if not cmd:
            print "'command' option for section %s is empty !" % (cmd)
            return
        freq = self.config.get_frequency()


        # Collect data according to frequency and plot accordingly
        while True:
            loopstart = time.clock()
            if(self.time_to_leave):
                break
            else:
                # Get data
                data = self.get_data()
                if(not data):
                    break

                # Log output to the file
                self.log_data(data)

                # Update display if necessary
                if(self.config.get_showplot()):
                    # Redraw all the points in the data buffer
                    for dp in data:
                        self.adjust_plotwindow(dp)
                        self.process_data(dp)
                        self.gp.simple_plot(self.data, 1, 2, "lines")

                # Sleep for the remaining time
                if(not self.config.get_offline()):
                    loopruntime = time.clock() - loopstart
                    if(freq - loopruntime > 0):
                        time.sleep(freq - loopruntime)
        os.close(self.handle)
