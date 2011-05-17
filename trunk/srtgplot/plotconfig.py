# plotconfig.py
#    Class for handling configuration file
#
# Copyright (C) 2010 Arun Viswanathan (arunv@arunviswanathan.com)
#This software is licensed under the GPLv3 license, included in
#./GPLv3-LICENSE.txt in the source distribution
#------------------------------------------------------------------------------
import ConfigParser
import datetime

# Configuration defaults
DEFAULT_MINY = 0
DEFAULT_MAXY = "*"
DEFAULT_TITLE = "Real-time plot"
DEFAULT_FREQ = 1
DEFAULT_SHOWPLOT = 1
DEFAULT_TIMEFMT = "%H:%M:%S"
DEFAULT_PLOTWINDOW = 100
DEFAULT_LOGDIR = "/tmp"
DEFAULT_PROCESSDATA = 'raw'
DEFAULT_OFFLINE = None
DEFAULT_ENABLED = 1

class PlotConfig:

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

        self.freq = float(kvhash.get("frequency", DEFAULT_FREQ))
        self.miny = kvhash.get("miny", DEFAULT_MINY)
        self.maxy = kvhash.get("maxy", DEFAULT_MAXY)
        self.title = kvhash.get("title", DEFAULT_TITLE)
        self.showplot = int(kvhash.get("showplot", DEFAULT_SHOWPLOT))
        self.plotwindow_secs = kvhash.get("plotwindow", DEFAULT_PLOTWINDOW)
        self.plotwindow = datetime.timedelta(seconds=int(self.plotwindow_secs))
        self.timefmt = kvhash.get("timeformat", DEFAULT_TIMEFMT)
        self.command = kvhash.get("command", '')
        self.logdir = logdir or DEFAULT_LOGDIR
        self.processdata = kvhash.get("processdata", DEFAULT_PROCESSDATA)
        self.offline = kvhash.get("offline", DEFAULT_OFFLINE)
        self.enabled = int(kvhash.get("enabled", DEFAULT_ENABLED))
        self.logfile = kvhash.get("logfile", None)

    def print_config(self):
        print "Configuration:"
        print "\t command    : %s" % (self.get_command())
        print "\t title      : %s" % (self.get_title())
        print "\t frequency  : %s secs" % (self.get_frequency())
        print "\t miny-maxy  : %s-%s" % (self.get_miny(), self.get_maxy())
        print "\t showplot   : %s" % (self.get_showplot())
        print "\t plotwindow : %s secs (%s hrs)" % (self.plotwindow_secs,
                                                    self.get_plotwindow())
        print "\t timeformat : %s" % (self.get_timefmt())
        print "\t logdir     : %s" % (self.get_logdir())
        print "\t logfile    : %s" % (self.get_logfile())
        print "\t processdata: %s" % (self.get_processdata())
        print "\t offline    : %s" % (self.get_offline())
        print "------------------------------------"

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

    def get_offline(self):
        return self.offline

    def get_logfile(self):
        return self.logfile

    def is_enabled(self):
        if self.enabled:
            return True
        return False


def print_directives():
    print "List of available directives and their defaults"
    print "================================================"
    print "(For details see README)\n"
    print " command    : Command to run (mandatory option)"
    print " timefmt    : Format of input time (default: %s)" % (DEFAULT_TIMEFMT)
    print " frequency  : Frequency (in seconds) for running command (default: %s)" % (DEFAULT_FREQ)
    print " title      : Title of the plot (default: %s)" % (DEFAULT_TITLE)
    print " miny       : Minimum y value (default: %s)" % (DEFAULT_MINY)
    print " maxy       : Minimum y value (default: %s)" % (DEFAULT_MAXY)
    print " plotwindow : Window size (in secs) of amount of data to buffer (default: %s)" % (DEFAULT_PLOTWINDOW)
    print " logdir     : Directory to log data (default: %s)" % (DEFAULT_LOGDIR)
    print " logfile    : File to log data (default: %s)" % ("rtplot_<sectionname>_<randomstr>")
    print " processdata: Data preprocessor to use (default: %s)" % (DEFAULT_PROCESSDATA)
    print " offline    : Offline file to read data from (default: %s)" % (DEFAULT_OFFLINE)
    print " showplot   : Launch realtime plot window (default: %s)" % (DEFAULT_SHOWPLOT)
    print " enabled    : Enable/disable this plot (default: %s)" % (DEFAULT_ENABLED)



