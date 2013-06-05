################################################################################
# mysql-enaber.py - 0.5
#
# A simple enabler that starts/stops MySQL server on a SF node
#
# 
################################################################################

from threading import Thread
from subprocess import Popen
from subprocess import PIPE
from subprocess import STDOUT
from time import sleep

# writes msg int the engine log
def logInfo(msg):
  logger.info(msg)
  
# executes an OS command and returns its output
def execute(cmd):
  std=Popen(cmd,stdout=PIPE,stderr=STDOUT,close_fds=True)
  out=std.stdout.read()
  return out
    
# change the permissions of a file so it can be executed
def makeRunnable(cmd):
  exec(["/bin/chmod","a+x",cmd])
    
# prepends the right path and appends the standard arguments for all mysql commands
def buildCommand(exe):
  pdh=runtimeContext.getVariable("MYSQL_ROOT_DIR").getValue()
  sck=runtimeContext.getVariable("MYSQL_SOCKET").getValue()
  cmd=[pdh+"/bin/"+exe]
  cmd.append("--user=root")
  cmd.append("--socket="+sck)
  return cmd
  
# tries to ping the database server and returns the resulting output 
def pingDaemon():
  cmd=buildCommand("mysqladmin")
  cmd.append("ping")
  return execute(cmd)
 
# runs the database server in the current thread *and blocks!* just be careful
def runDaemon():
  nls=runtimeContext.getVariable("MYSQL_LANGUAGE").getValue()
  dta=runtimeContext.getVariable("MYSQL_DATA_DIR").getValue()
  prt=runtimeContext.getVariable("MYSQL_PORT").getValue()
  cmd=buildCommand("mysqld")
  cmd.append("--language="+nls)
  cmd.append("--datadir="+dta)
  cmd.append("--port="+prt)
  return execute(cmd)
  
# issues the shutdown command to the database server
def stopDaemon():
  cmd=buildCommand("mysqladmin")
  cmd.append("shutdown")
  return execute(cmd)
  
# a class used to run the database server in a different thread so we don't block forever
class DaemonThread(Thread):
  # definition that gets executed when the underlying Thread is run
  def run(self):
    out=runDaemon()
    
# checks if the database server is running by pinging it
def isRunning():
  out=pingDaemon()
  if out.find("is alive")==-1:
    return False
  return True

# starts the MySQL Enabler
def doStart():
  logInfo("Starting MySQL Enabler")
  # make sure needed executables have the right permissions
  pdh=runtimeContext.getVariable("MYSQL_ROOT_DIR").getValue()
  execute(["/bin/chmod","a+x",pdh+"/bin/mysql"])
  execute(["/bin/chmod","a+x",pdh+"/bin/mysqladmin"])
  execute(["/bin/chmod","a+x",pdh+"/bin/mysqld"])
  # first check if database is already running
  if isRunning():
    raise Exception("MySQL Already Running")
  # start the database server in a different thread
  dt=DaemonThread()
  dt.start()
  
# stops the MySQL Enabler
def doShutdown():
  logInfo("Shutting down MySQL Enabler")
  stopDaemon()
  
# checks if the MySQL Enabler has been sucessfully started
def hasContainerStarted():
  if not isRunning():
    logInfo("MySQL Server not yet running")
    return False
  logInfo("MySQL Server started")
  return True
  
# checks if the MySQL Enabler is still running; if not it will try to restart it at least once
# to avoid shutting down other dependent components
def isContainerRunning():
  if isRunning():
    return True
  logInfo("MySQL Server is not running, trying to restart it")
  dt=DaemonThread()
  dt.start()
  sleep(10)
  if isRunning():
    logInfo("MySQL Server restarted successfully")
    return True
  logInfo("MySQL Server didn't restart, notifying broker")
  return False
  
# returns the value of the named statistic; mysqladmin extended-status returns a table with the
# following format, and we extract the value from it in the best way we found at the time ;)
# +-----------------------+------------+
# | HEADER                | HEADER     |
# +-----------------------+------------+
# | statName              | value      |
# | statName              | value      |
# | statName              | value      |
# | statName              | value      |
# | statName              | value      |
# | statName              | value      |
# ...
# | statName              | value      |
# +-----------------------+------------+
def getStatistic(statName):
  logInfo("Fetching MySQL Statistic "+statName)
  # execute the command to gather statistics
  cmd=buildCommand("mysqladmin")
  cmd.append("extended-status")
  out=execute(cmd)
  # find the corresponding line, take into account the beautified names used by the Enabler
  idx=out.find("| "+statName.replace(" ","_").capitalize()+" ")
  if idx==-1:
    # we got an unkown name!
    logInfo("MySQL doesn't provide "+statName)
    return 0
  # isolate the line we need
  lne=out[idx:].splitlines()[0]
  # return the value from the second column
  return float(lne.split("|")[2])

   
  

