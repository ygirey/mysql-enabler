from com.datasynapse.fabric.admin.info import AllocationInfo
from com.datasynapse.fabric.util import GridlibUtils, ContainerUtils
from com.datasynapse.fabric.common import RuntimeContextVariable, ActivationInfo
from subprocess import call, Popen
import os
import time
import socket
import fnmatch

zipdir = "mysql-5.5.30-linux2.6-x86_64"

def prepareWorkDirectory():
    print "this is aw3som3"
    proxy.prepareWorkDirectory()
  
def doInit(additionalVariables):
    # create the data, mysqld, and run directories
    workdir = proxy.getContainer().getRuntimeContext().getVariable('CONTAINER_WORK_DIR').getValue() 
    ContainerUtils.getLogger(proxy).info("Creating data, mysql, tmp, and run directories in " + workdir)
    os.mkdir(os.path.join(workdir, "data") )
    os.mkdir(os.path.join(workdir, "mysqld") )
    os.mkdir(os.path.join(workdir, "tmp") )
    os.mkdir(os.path.join(workdir, "run") )
    additionalVariables.add(RuntimeContextVariable("MYSQL_BASEDIR", os.path.join(workdir, zipdir), RuntimeContextVariable.STRING_TYPE))
    additionalVariables.add(RuntimeContextVariable("MYSQL_PORT", "3306", RuntimeContextVariable.STRING_TYPE, "MySQL Listen Port", True, RuntimeContextVariable.NUMERIC_INCREMENT))
    proxy.doInit(additionalVariables)

def doStart():
    workdir = proxy.getContainer().getRuntimeContext().getVariable('CONTAINER_WORK_DIR').getValue() 
    basedir = proxy.getContainer().getRuntimeContext().getVariable('MYSQL_BASEDIR').getValue() 
    port = proxy.getContainer().getRuntimeContext().getVariable('MYSQL_PORT').getValue() 
    base = os.path.join(workdir, zipdir)
    bindir = os.path.join(basedir, "bin")
    scriptdir = os.path.join(basedir, "scripts")
    ContainerUtils.getLogger(proxy).info("Initializing MySQL database " + os.path.join(workdir, "data"))
    call(["chmod", "-fR", "+x", bindir])
    call(["chmod", "-fR", "+x", scriptdir])
    call(["sh", os.path.join(scriptdir, "mysql_install_db"), "--basedir=" + basedir, "--datadir=" + os.path.join(workdir, "data"), "--user=egoodman"])
    ContainerUtils.getLogger(proxy).info("Running mysqld")
    Popen([os.path.join(bindir, "mysqld"), "--defaults-file=" + os.path.join(workdir, "my.cnf")])
    time.sleep(20)
    ContainerUtils.getLogger(proxy).info("Setting local password")
    call([os.path.join(bindir, "mysqladmin"), "--socket=" + os.path.join(workdir, "mysqld", "mysqld.sock"), "-u", "root", "password", "datasynapse"])
    host = socket.gethostname()
    ContainerUtils.getLogger(proxy).info("Setting network password")
    call([os.path.join(bindir, "mysqladmin"), "--port=" + port, "-h", host, "-u", "root", "password", "datasynapse"])
   
def doInstall(info):
    archiveinfo = features.get("Archive Support")
    enginedir = proxy.getContainer().getRuntimeContext().getVariable('ENGINE_WORK_DIR').getValue()
    workdir = proxy.getContainer().getRuntimeContext().getVariable('CONTAINER_WORK_DIR').getValue()
    basedir = proxy.getContainer().getRuntimeContext().getVariable('MYSQL_BASEDIR').getValue() 
    tmpdir = os.path.join(workdir, "tmp") 
    bindir = os.path.join(basedir, "bin")
    if archiveinfo:
        for i in range(archiveinfo.getArchiveCount()):
            archive = archiveinfo.getArchiveInfo(i)
            archname = archive.getArchiveFilename()
            ContainerUtils.getLogger(proxy).info("Installing archive " + archive.getArchiveFilename())
            if (fnmatch.fnmatch(archname, "*.sql.zip")):
                sqlfile = archname.rsplit(".", 1)[0]
                database = sqlfile.rsplit(".", 1)[0]
                call(["unzip", "-d", tmpdir, os.path.join(enginedir, archiveinfo.getArchiveDirectory(), archname)])     
                call([os.path.join(bindir, "mysqladmin"), "--socket=" + os.path.join(workdir, "mysqld", "mysqld.sock"), "--user=root", "--password=datasynapse", "create", database])
                call([os.path.join(bindir, "mysql"), "--user=root", "--password=datasynapse", "--socket=" + os.path.join(workdir, "mysqld", "mysqld.sock"), database], stdin=open(os.path.join(tmpdir, sqlfile), "r"))

def doUninstall():
    print "doUninstall"	
 
def doShutdown():
    workdir = proxy.getContainer().getRuntimeContext().getVariable('CONTAINER_WORK_DIR').getValue()
    port = proxy.getContainer().getRuntimeContext().getVariable('MYSQL_PORT').getValue() 
    pidfile = open(os.path.join(workdir, "mysqld", "mysqld.pid"), "r")
    pids = pidfile.readlines()
    pidfile.close()
    os.kill(int(pids[0]), 15)
    
# running condition
def getContainerRunningConditionPollPeriod():
    return 5000

def isContainerRunning():
    port = proxy.getContainer().getRuntimeContext().getVariable('MYSQL_PORT').getValue() 
    basedir = proxy.getContainer().getRuntimeContext().getVariable('MYSQL_BASEDIR').getValue() 
    bindir = os.path.join(basedir, "bin")
    host = socket.gethostname()
    status = call([os.path.join(bindir, "mysqladmin"), "--port=" + port, "-h", host, "--user=root", "--password=datasynapse", "ping"])
    ContainerUtils.getLogger(proxy).info("mysqladmin ping returns " + str(status))
    if status == 0:
        return True
    else:
        return False
#    
def getComponentRunningConditionErrorMessage():
    return "mysqladmin ping failure"

   
  

