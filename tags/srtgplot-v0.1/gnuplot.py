# gnuplot.py 
#      Wrapper for plotting using gnuplot
#
# Copyright (C) 2010 Arun Viswanathan (arunv@arunviswanathan.com)
#This software is licensed under the GPLv3 license, included in
#./GPLv3-LICENSE.txt in the source distribution
#-------------------------------------------------------------------------------

import subprocess
from exceptions import Exception
from utils import which

class Gnuplot:
    '''
        Class for creating realtime graphs using gnuplot
    '''
    GNUPLOT = 'gnuplot'

    def __init__(self):
        path = which(self.GNUPLOT)
        if path is None:
            raise Exception("Cannot find gnuplot on your system!")

        # Create a input pipe to gnuplot for sending gnuplot commands.
        # Create a stderr pipe to capture warnings/errors output by gnuplot. 
        # Currently the errors are not processed but may need to be if 
        # additional gnuplot functionality is introduced.
        # shell = true makes sure that the commands are executed as if they 
        # were being executed using a shell.
        self.gp = subprocess.Popen([self.GNUPLOT],
                                   stdin=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=True);

    def write(self, data):
        self.gp.stdin.write(data);

    def set_options(self, options):
        self.write(options)

    def simple_plot(self, datalist, xcolno, ycolno, style):
        '''
            Plots the xcolno and ycolno in the datalist using 
            specified style 
        '''
        plotstr = """plot "-" using %d:%d notitle w %s\n""" % \
                         (xcolno, ycolno, style)

        # plot command with the - argument reads lines 
        # from stdin until 'e\n' is input                          
        self.write(plotstr)
        for d in datalist:
            self.write(d)
        self.write("e\n")
