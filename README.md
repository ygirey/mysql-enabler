==========================================================================
MySQL 5.6.12 Server Enabler Guide
==========================================================================
Introduction
--------------------------------------
A Silver Fabric Enabler allows an external application or application platform, 
such as a J2EE application server to run in a TIBCO Silver Fabric software 
environment. In Silver Fabric 4.1, we introduced the **Scripting Container** feature
to accelerate the development of new enablers and enable customers to customize
existing enablers for site-specific requirements.  This document describes what is
involved in developing a reasonably full-featured MySQL enabler using python.

Installation
--------------------------------------
The MySQL Server Enabler consists of an Enabler Runtime Grid Library and a Distribution 
Grid Library. The Enabler Runtime contains information specific to a Silver Fabric 
version that is used to integrate the Enabler, and the Distribution contains a binary 
distribution of MySQL used for the Enabler. Installation of the MySQL Server 
Enabler involves copying these Grid Libraries to the 
SF_HOME/webapps/livecluster/deploy/resources/gridlib directory on the Silver Fabric Broker. 

Creating the MySQL Enabler
--------------------------------------
The Enabler Runtime Grid Library is created by building the maven project.
```bash
mvn package
```

Creating the Distribution Grid Library
--------------------------------------
The Distribution Grid Library is created by performing the following steps:
* Download the MySQL binaries from http://downloads.mysql.com/archives/mysql-5.6/mysql-5.6.12-linux-glibc2.5-x86_64.tar.gz.
* Build the maven project with the location of the archive, the archive's base name, the archive type, the 
      operating system target and optionally the version. 
       

*****************************************************************************
NOTE: as of now, only 64-bit linux is supported. 
******************************************************************************
```bash
mvn package -Ddistribution.location=/home/you/Downloads/ \
-Ddistribution.basename=mysql-5.6.12-linux-glibc2.5-x86_64 \
-Ddistribution.type=tar.gz \
-Ddistribution.version=5.6.12 -Ddistribution.os=linux64

The distribution.location path should end in the appropriate path-separator for your operating system (either "/" or "\\")
If running maven on Windows, make sure to to double-escape the backslash path separators for the 
distribution.location property: -Ddistribution.location=C:\\Users\you\Downloads\\


Runtime Context Variables
--------------------------------------
Below are some notable Runtime Context Variables associated with this Enabler.
Take a look at the container.xml file in the src/main/resources/runtime/ subdirectory

---- Common Variables (Change as Desired)

 MYSQL_DATA_DIR - path where the database files are located; 
				NOTE: for persistence across engine hosts, it is recommended you
                 specify a network-mounted directory for this variable.
                 Changing this will also affect other variables (e.g, CAPTURE_INCLUDES)              

 MYSQL_PORT - port where this database listens for connections

 MYSQL_USER - the MySQL user account the enabler will use

 MYSQL_PW - the password for MYSQL_USER


---- Power Variables (Change If You Know What You're Doing)

 CAPTURE_INCLUDES - common capture stuff, currently it includes everything
                    under the default data directory

 MYSQL_LANGUAGE - the language for error messages, such as "en_US"

 MYSQL_LANG_MESSAGES_DIR - error message language location, passed to 
                             -lc-messages-dir parameter


---- Internal Variables (Don't Change Unless Absolutely Needed)

 MYSQL_BASE_DIR - path where MySQL resides after installation - change
                  CONTAINER_WORK_DIR instead

 MYSQL_HOST_IP - IP address where this database listens for connections

 MYSQL_SOCKET - socket file for localhost communications; mainly between
                mysqladmin and mysqld



