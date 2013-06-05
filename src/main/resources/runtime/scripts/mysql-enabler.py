#
# Copyright (c) 2013 TIBCO Software Inc. All Rights Reserved.
# 
# Use is subject to the terms of the TIBCO license terms accompanying the download of this code. 
# In most instances, the license terms are contained in a file named license.txt.
#

from com.datasynapse.fabric.admin.info import AllocationInfo
from com.datasynapse.fabric.util import GridlibUtils, ContainerUtils
from com.datasynapse.fabric.common import RuntimeContextVariable, ActivationInfo
import java.lang.System
from subprocess import call, Popen
import os
import platform
import time
import socket
import fnmatch

# writes the message in the engine log
def logInfo(msg):
  logger.info(msg)

def prepareWorkDirectory():
    proxy.prepareWorkDirectory()
  
def doInit(additionalVariables):
    # create the data, tmp, and mysqld directories
    workdir = runtimeContext.getVariable('CONTAINER_WORK_DIR').getValue() 
    datadir = runtimeContext.getVariable('MYSQL_DATA_DIR').getValue()
    logInfo("Creating data, tmp, and mysqdd directories in " + workdir)
    if (not os.path.exists(datadir)) :
        os.mkdir(datadir)
    os.mkdir(os.path.join(workdir, "mysqld") )
    os.mkdir(os.path.join(workdir, "tmp") )
    proxy.doInit(additionalVariables)

def doStart():
    workdir = runtimeContext.getVariable('CONTAINER_WORK_DIR').getValue() 
    basedir = runtimeContext.getVariable('MYSQL_BASE_DIR').getValue() 
    datadir = runtimeContext.getVariable('MYSQL_DATA_DIR').getValue()
    port = runtimeContext.getVariable('MYSQL_PORT').getValue() 
    user = runtimeContext.getVariable('MYSQL_USER').getValue()
    pw = runtimeContext.getVariable('MYSQL_PW').getValue()
    msgdir = runtimeContext.getVariable('MYSQL_LANG_MESSAGES_DIR').getValue()
    lang = runtimeContext.getVariable('MYSQL_LANGUAGE').getValue()
    socket = runtimeContext.getVariable('MYSQL_SOCKET').getValue()
    bindir = os.path.join(basedir, "bin")
    scriptdir = os.path.join(basedir, "scripts")
    
    logInfo("Initializing MySQL database " + os.path.join(workdir, "data"))
    call(["chmod", "-fR", "+x", bindir])
    call(["chmod", "-fR", "+x", scriptdir])
    
    scriptname="mysql_install_db"
    if (platform.system() == "Windows"):
        scriptname+=".pl"
    call([os.path.join(scriptdir, scriptname), "--basedir=" + basedir, "--datadir=" + datadir])
    
    logInfo("Running mysqld")
    Popen([os.path.join(bindir, "mysqld"), "--socket=" + socket, "--datadir=" + datadir, "--lc-messages-dir=" + msgdir, "--lc-messages=" + lang, "--pid-file=" + os.path.join(workdir, "mysqld", "mysqld.pid")])
    time.sleep(20)
    
    logInfo("Setting local password")
    call([os.path.join(bindir, "mysqladmin"), "--socket=" + socket, "-u", user, "password", pw])
    
    host = socket.gethostname()
    logInfo("Setting network password")
    call([os.path.join(bindir, "mysqladmin"), "--port=" + port, "-h", host, "-u", user, "password", pw])
   
def doInstall(info):
    archiveinfo = features.get("Archive Support")
    enginedir = runtimeContext.getVariable('ENGINE_WORK_DIR').getValue()
    workdir = runtimeContext.getVariable('CONTAINER_WORK_DIR').getValue()
    basedir = runtimeContext.getVariable('MYSQL_BASE_DIR').getValue() 
    user = runtimeContext.getVariable('MYSQL_USER').getValue()
    pw = runtimeContext.getVariable('MYSQL_PW').getValue()
    socket = runtimeContext.getVariable('MYSQL_SOCKET').getValue()
    tmpdir = os.path.join(workdir, "tmp") 
    bindir = os.path.join(basedir, "bin")
    if archiveinfo:
        for i in range(archiveinfo.getArchiveCount()):
            archive = archiveinfo.getArchiveInfo(i)
            archname = archive.getArchiveFilename()
            logInfo("Installing archive " + archive.getArchiveFilename())
            if (fnmatch.fnmatch(archname, "*.sql.zip")):
                sqlfile = archname.rsplit(".", 1)[0]
                database = sqlfile.rsplit(".", 1)[0]
                call(["unzip", "-d", tmpdir, os.path.join(enginedir, archiveinfo.getArchiveDirectory(), archname)])     
                call([os.path.join(bindir, "mysqladmin"), "--socket=" + socket, "--user=" + user, "--password="+pw, "create", database])
                call([os.path.join(bindir, "mysql"), "--user=" + user, "--password=" + pw, "--socket=" + socket, database], stdin=open(os.path.join(tmpdir, sqlfile), "r"))

def doUninstall():
    print "doUninstall"    
 
def doShutdown():
    workdir = runtimeContext.getVariable('CONTAINER_WORK_DIR').getValue()
    port = runtimeContext.getVariable('MYSQL_PORT').getValue() 
    pidfile = open(os.path.join(workdir, "mysqld", "mysqld.pid"), "r")
    pids = pidfile.readlines()
    pidfile.close()
    os.kill(int(pids[0]), 15)
    
# running condition
def getContainerRunningConditionPollPeriod():
    return 5000

def isContainerRunning():
    port = runtimeContext.getVariable('MYSQL_PORT').getValue() 
    basedir = runtimeContext.getVariable('MYSQL_BASE_DIR').getValue()
    user = runtimeContext.getVariable('MYSQL_USER').getValue()
    pw = runtimeContext.getVariable('MYSQL_PW').getValue() 
    bindir = os.path.join(basedir, "bin")
    host = socket.gethostname()
    status = call([os.path.join(bindir, "mysqladmin"), "--port=" + port, "-h", host, "--user=" + user, "--password=" + pw, "ping"])
    ContainerUtils.getLogger(proxy).info("mysqladmin ping returns " + str(status))
    if status == 0:
        return True
    else:
        return False
#    
def getComponentRunningConditionErrorMessage():
    return "mysqladmin ping failure"
