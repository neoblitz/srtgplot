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
import threading
from collections import deque
from gnuplot import Gnuplot
from plotconfig import PlotConfig

class Plot(Thread):
    """
        Plotter thread for every section specified in the configuration file.
        Specified command is run with the frequency specified, command output 
        is logged to a file under the specified log directory (default: /tmp) 
        and a gnuplot window plots real-time values collected.    
    """
    
    # Gnuplot options
    GP_OPTIONS = """ 
set xdata time;
set timefmt \"%s\";
set tics nomirror;
set yrange [%s:%s];
set style line 1 linetype 1 linewidth 1 pointtype 2;
set title \"%s\" font "Sans Serif,14"; """

    def __init__(self, conffile, secname, logdir):
        Thread.__init__(self)
        self.secname = secname
        self.time_to_leave = False
        self.off_filehandle = None
        self.logdir = logdir
        
        # Read and initialize from the config file
        self.config = PlotConfig(conffile)

        # Initialize attributes for the given secname
        self.config.init_attributes(secname)

        if not self.config.is_enabled():
            print "Skipping plot for section '%s'" % (secname)
            return

        # plotbuffer is a dynamic buffer that holds data points over the specified 
        # plotwindow. A deque() is favoured over a [] because deques have O(1)
        # performance for popleft() and append() operations over O(n) of lists. 
        self.plotbuffer = deque()

        # Windowstart and windowend control the plotwindow . 
        self.windowstart = 0
        self.windowend = 0

        # Get the offline filename if any
        self.offline_file = self.config.get_offline()
        self.offline_filehandle = None
        if(self.offline_file):
            try:
                self.offline_filehandle = open(self.offline_file, "r")
                #xreadline reads big files efficiently in memory and returns
                # a file object to iterate over.
                self.file_in_mem = self.offline_filehandle.xreadlines()
            except IOError:
                raise Exception("Could not open logfile %s !" % (filename))


        # Create a temporary file for logging the command output
        if(self.config.get_logfile() is None):
            (self.handle, self.fnameout) = \
                tempfile.mkstemp(prefix="rtplot_" + self.secname + "_",
                          dir=self.logdir);
        else:
            # Open the specified logfile in write mode
            self.fnameout = self.config.get_logfile()
            try:
                self.handle = os.open(self.fnameout, os.O_CREAT | os.O_WRONLY)
            except IOError:
                raise Exception("Could not open logfile %s!" % (self.fnameout))

        # Initialize gnuplot
        if(self.config.get_showplot()):
            self.gp = Gnuplot()
            self.gp.write(self.GP_OPTIONS % (self.config.get_timefmt(),
                           self.config.get_miny(),
                           self.config.get_maxy(),
                           self.config.get_title()));

        if(self.offline_file is not None):
           print "\nOffline plotting for '%s' using logfile: '%s'" % \
            (self.secname, self.config.get_offline())
        else:
           print "\nRealtime plotting for '%s' and output to logfile '%s'" % \
            (self.secname, self.fnameout)
        self.config.print_config()
        self.start()


    def get_curr_timewindow(self, datapoint):
        timestr = datapoint.split()[0]
        if(self.windowstart == 0):
            self.windowstart = dateutil.parser.parse(timestr)

        # Advance the windowend pointer
        self.windowend = dateutil.parser.parse(timestr)
        return(self.windowend - self.windowstart)

    def adjust_plotwindow(self, dp):
        if(self.offline_file is None):
            timediff = self.get_curr_timewindow(dp)
            if(timediff >= self.config.get_plotwindow()):
                self.plotbuffer.popleft()

    def process_reld(self, dp):
        '''
            Diffs the current value with previous value
        '''
        (timestr, currval) = dp.split()
        currval = float(currval)
        if(len(self.plotbuffer) == 0):
            self.prevvalue = currval
        diff = currval - self.prevvalue
        newdp = timestr + " " + str(diff) + "\n"
        self.plotbuffer.append(newdp)
        self.prevvalue = currval


    def process_data(self, dp):
        procopt = self.config.get_processdata()
        if(procopt == 'reld'):
            self.process_reld(dp)
        else:
            self.plotbuffer.append(str(dp) + "\n")

    def set_ttl(self):
        self.time_to_leave = True

    def data_generator(self):
        '''
            This is a generator function (due to use of the yield keyword)
            that will return a line of data each time it is called.
        '''
        if(self.offline_file):
            for line in self.file_in_mem:
                yield line
        else:
            # Execute the command
            # data returned is a list of strings in the format 
            # <time value>
            # The while loop makes sure that the generator 
            # reruns the command repeatedly
            while True:
                cmd = self.config.get_command()
                (status, data) = utils.execute_command(cmd)
                if(status):
                    raise Exception("Error while executing %s\n Error output %s" % \
                                 (cmd, data))
                else:
                    for line in data:
                        yield line

    def log_data(self, data):
        if(not self.config.get_offline()):
            os.write(self.handle, str(data) + "\n")


    def run(self):
        cmd = self.config.get_command()
        if not cmd:
            print "'command' option for section %s is empty !" % (cmd)
            return
        freq = self.config.get_frequency()

        # Create the data_generator. Note that this does not 
        # actually run the function but just creates the generator object
        datagen = self.data_generator()
        
        try:
            # Collect data according to frequency and plot accordingly
            for data in datagen:
                loopstart = time.clock()
                if(self.time_to_leave):
                    break
                else:
                    # Log output to the file
                    self.log_data(data)
                    print threading.current_thread() , data
    
                    # Update display if necessary
                    if(self.config.get_showplot()):
                        self.adjust_plotwindow(data)
                        self.process_data(data)
                        # Redraw all the points in the data buffer
                        self.gp.simple_plot(self.plotbuffer,
                                            1, # x column  
                                            2, # y column
                                            "linespoints ls 1") # Style
    
                    # Sleep for the remaining time in realtime mode
                    if(not self.offline_file):
                        loopruntime = time.clock() - loopstart
                        remaining_time = freq - loopruntime
                        if(remaining_time > 0.0):
                            time.sleep(remaining_time)
        except Exception as ex:
            print "ERROR: %s" %(ex)
            return
        
        print "No more data for '%s'! " % (self.secname)

        # Wait for user confirmation before exiting the thread
        # in offline mode as this would close the gnuplot window
        if(self.offline_file):
            try:
                raw_input("Hit ENTER to close the gnuplot window for '%s'!" % \
                           (self.secname))
            except:
                pass
        os.close(self.handle)
