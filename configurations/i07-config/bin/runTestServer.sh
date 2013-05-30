#!/bin/sh

FITNESSE_HOME=/usr/local/JavaPackages/fitnesse
GDA_ROOT=/home/xr56/Dev/gdaDev/gda-trunk/plugins
GDA_CONFIG=/home/xr56/Dev/gdaDev/gda-config-local/localBase
GDA_USERS=/home/xr56/Dev/gdaDev/gda-config-local/localBase/users
TEST_SERVER=diamrl5068.diamond.ac.uk
TEST_PORT=1300

#export GDA_ROOT
#export GDA_CONFIG
#export GDA_USERS
#export TEST_SERVER
#export TEST_PORT

#StartUp
java -cp ${FITNESSE_HOME}/fitnesse.jar fitnesse.FitNesse -p ${TEST_PORT} -d ${GDA_CONFIG}/testing -r DiamondFitnesse -l ${GDA_USERS}/logs -e 365 &

#ShutDown manually over URL by http://hostname:prot?responder=shutdown, or:
#java -cp ${FITNESSE_HOME}/fitnesse.jar fitnesse.Shutdown -p ${TEST_PORT}


#-Dgda.root=/home/xr56/Dev/gdaDev/gda-trunk/plugins', '-Dgda.users=/home/xr56/Dev/gdaDev/gda-config-local/localBase/users', '-Djacorb.config.dir=/home/xr56/Dev/gdaDev/gda-config-local/localBase/properties', '-Dgda.propertiesFile=/home/xr56/Dev/gdaDev/gda-config-local/localBase/properties/java.properties', '-Dgda.config=/home/xr56/Dev/gdaDev/gda-config-local/localBase', '-Dgov.aps.jca.JCALibrary.properties=/home/xr56/Dev/gdaDev/gda-config-local/localBase/properties/JCALibrary.properties'
