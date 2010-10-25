# plotconfig.py
#    Class for handling configuration file
#
# Copyright (C) 2010 Arun Viswanathan (arunv@arunviswanathan.com)
#This software is licensed under the GPLv3 license, included in
#./GPLv3-LICENSE.txt in the source distribution
#------------------------------------------------------------------------------
import ConfigParser
import datetime

class PlotConfig:

    DEFAULT_MINY = 0
    DEFAULT_MAXY = "*"
    DEFAULT_TITLE = "Real-time plot"
    DEFAULT_FREQ = 1
    DEFAULT_SHOWPLOT = 1
    DEFAULT_TIMEFMT = "%H:%M:%S"
    DEFAULT_PLOTWINDOW = 100
    DEFAULT_LOGDIR = "/tmp"
    DEFAULT_PROCESSDATA = 'raw'

    def __init__(self, filename):
        # Read the configuration file
        self.config = ConfigParser.RawConfigParser()
        # The following option is important to prevent configparser 
        # from converting everything to lowercase
        self.config.optionxform = str
        self.config.read(filename)
        self.sections = self.config.sections()

    def get_sections(self):
        return self.config.sections()

    def init_attributes(self, secname, logdir=None):
        options = self.config.items(secname)
        kvhash = {}
        for k, v in options:
            kvhash[k] = v

        self.freq = float(kvhash.get("frequency", self.DEFAULT_FREQ))
        self.miny = kvhash.get("miny", self.DEFAULT_MINY)
        self.maxy = kvhash.get("maxy", self.DEFAULT_MAXY)
        self.title = kvhash.get("title", self.DEFAULT_TITLE)
        self.showplot = int(kvhash.get("showplot", self.DEFAULT_SHOWPLOT))
        self.plotwindow = datetime.timedelta(seconds=int((kvhash.get("plotwindow",
                                                         self.DEFAULT_PLOTWINDOW))))
        self.timefmt = kvhash.get("timeformat", self.DEFAULT_TIMEFMT)
        self.command = kvhash.get("command", '')
        self.logdir = logdir or self.DEFAULT_LOGDIR
        self.processdata = kvhash.get("processdata", self.DEFAULT_PROCESSDATA)

    def get_frequency(self):
        return self.freq

    def get_miny(self):
        return self.miny

    def get_maxy(self):
        return self.maxy

    def get_title(self):
        return self.title

    def get_showplot(self):
        return self.showplot

    def get_timefmt(self):
        return self.timefmt

    def get_command(self):
        return self.command

    def get_plotwindow(self):
        return self.plotwindow

    def get_logdir(self):
        return self.logdir

    def get_processdata(self):
        return self.processdata


