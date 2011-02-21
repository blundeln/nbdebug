#
# Copyright (C) 2006-2011 Nick Blundell.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# 
# The GNU GPL is contained in /usr/doc/copyright/GPL on a Debian
# system and in the file COPYING in the Linux kernel source.
# 
# Author: Nick Blundell <blundeln [AT] gmail [DOT] com>
# Organisation: www.nickblundell.org.uk
# 

import os, sys, inspect, pdb

# Apply environment variables.
DEBUG_ENABLED = "NBDEBUG"  in os.environ
IN_DEBUG_MODE = DEBUG_ENABLED

debugFilters = []
try :
  for filter in os.environ["NBDEBUG_FILTER"].split(",") :
    if filter : debugFilters.append(filter);
except : pass
  
EXIT_ON_WARNINGS = False

# Alias of set_trace
breakpoint = pdb.set_trace


#
# Description:
#   Adds a debug filter.
# Parameters:
#   debugFilter - string to filter in the debug messages.
#
def debugDontFilter(debugFilter) :
  debugFilters.append(debugFilter)

def debugSetExitOnWarnings(exitOnWarnings) :
  global EXIT_ON_WARNINGS
  EXIT_ON_WARNINGS = exitOnWarnings

# Gets the location of the calling frame, returning it as a string.
def getCallerLocation(callerFrame) :

  location = ""

  callerFrameObject = None
  functionName = callerFrame.f_code.co_name

  # Get the name of the calling class.
  if "self" in callerFrame.f_locals :
    callerFrameObject = callerFrame.f_locals["self"]
    if hasattr(callerFrameObject, "__instance_name__") :
      object_name = callerFrameObject.__instance_name__()
    elif hasattr(callerFrameObject, "__class__") :
      object_name = callerFrameObject.__class__.__name__
    else :
      object_name = callerFrameObject.__name__

    if object_name :
      location += object_name + "."
  
  location += functionName + "()"

  # Give a name to the function that calls all.
  location = location.replace("?","main")

  return location

# Allow a function to be set that computes and indent level for the debug message.
indent_function = None

def set_indent_function(f) :
  global indent_function
  indent_function = f

def get_indent() :
  if not indent_function:
    return ""
  else :
    return indent_function()

#
# Description:
#   Prints the debug message if it matches a filter, or if no filers are specified.
# Parameters:
#   message - message to print.
#
def logMessage(message, enableFiltering=True, filter=None, time=None, newLine=True, prefix=None, exitAfterPrint=False, display=True, callerLevel=1) :

  if not DEBUG_ENABLED :
    return

  # Convert message to string.
  message = str(message)

  indent = get_indent()

  # Prepend the caller's location to the message.
  callerFrame = inspect.currentframe()
  for i in range(0, callerLevel) :
    callerFrame = callerFrame.f_back
  location = getCallerLocation(callerFrame)
  message = indent + location+": " + message
  
  # Check if the message should be printed.
  if enableFiltering and len(debugFilters) > 0 :
  
    # If there is no explicit filter, use the message.
    if not filter :
      filter = message
  
    foundMatch = False
    for debugFilter in debugFilters :
      if filter.find(debugFilter) == 0 :
        foundMatch = True
        break
        
    if not foundMatch :
      # Decide whether to exit.
      if exitAfterPrint :
        sys.exit(1)
      return None

  # Add prefixes to the message.
  if prefix :
    message = prefix + " - " + message
  if time :
    message = "["+str(time)+"]: "+message

  # Add suffix.
  if newLine :
    message = message+"\n"

  if display :
    sys.stdout.write(message)
    sys.stdout.flush()
        
  # Decide whether to exit.
  if exitAfterPrint :
    sys.exit(1)

  return message.strip("\n")

def debugOutput(message, time=None, filter=None, newLine=True, display=True, callerLevel=2) :
  return logMessage(message, time=time, filter=filter, enableFiltering=True, newLine=newLine, display=display, callerLevel=callerLevel)

def d(message, time=None, filter=None, newLine=True, display=True, callerLevel=2) :
  return logMessage(message, time=time, filter=filter, enableFiltering=True, newLine=newLine, display=display, callerLevel=callerLevel)

#
# Description:
#   Prints a warning message.
# Parameters:
#   message - message to print.
#
def debugWarning(message, time=None, callerLevel=2, display=True) : 
  return logMessage(message, enableFiltering=False, exitAfterPrint=EXIT_ON_WARNINGS, prefix="WARNING", time=time, callerLevel=callerLevel, display=display)



#
# Description:
#   Prints an error message.
# Parameters:
#   message - message to print.
#
def debugError(message, time=None, callerLevel=2, display=True) :
  return logMessage(message, enableFiltering=False, exitAfterPrint=True, prefix="ERROR", time=time, callerLevel=callerLevel, display=display)
