
from gda.jython.commands.ScannableCommands import add_default;

from Metadata import MetadataScannable

fileHeader = MetadataScannable("fileHeader");

ringList = [ringEnergy, ringCurrent] #@UndefinedVariable
idList = [igap, jgap]; #@UndefinedVariable
energyList = [dcmenergy, pgmenergy]; #@UndefinedVariable
dcmList = []
pgmList = []
slitList = [];

fileHeader.add(ringList);
fileHeader.add(idList);
fileHeader.add(energyList);
fileHeader.add(dcmList);
fileHeader.add(pgmList);
fileHeader.add(slitList)

add_default([fileHeader]);



