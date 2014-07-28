'''
This requires GDA 'metashop' object to be defined in Spring configuration on the server as:
<bean id="metashop" class="gda.data.metadata.NXMetaDataProvider" />

Created on 20 Mar 2014

@author: fy65
'''
from gda.jython.commands.GeneralCommands import alias

from gdascripts.metadata.metadata_commands import meta_add, meta_ll, meta_ls, meta_rm  # @UnusedImport
from gda.configuration.properties import LocalProperties

alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")
from gda.data.scan.datawriter import NexusDataWriter
LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME,"metashop")