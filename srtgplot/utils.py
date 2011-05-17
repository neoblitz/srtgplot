# utils.py 
#      Utility functions
#
# Copyright (C) 2010 Arun Viswanathan (arunv@arunviswanathan.com)
#This software is licensed under the GPLv3 license, included in
#./GPLv3-LICENSE.txt in the source distribution
#-------------------------------------------------------------------------------

import commands
import os, sys

def which(program):
    '''
        Checks if the specified 'program' exists in the PATH
        and is executable. Returns the path or None.
    '''
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def execute_command(cmd):
    '''
        Executes a shell command and returns status and output returned after
        execution
    '''
    (status, output) = commands.getstatusoutput("""%s""" % (cmd))
    if((output.find("error") >= 0) or 
       (output.find("ERROR") >= 0) or
       (output.find("Error") >= 0)):
        status = 1   
    
    if (status > 0):
        return (status, output)
    return (0, output.split("\n"))

    
