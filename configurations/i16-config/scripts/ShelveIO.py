## @file ShelveIO.py  contains the class providing general methods
# to archive and retrieve variables
# Nota Bene: this class will exist in multiple instances.
# in each istance self.SettingsFileName and paths
# can be different!!
# @author Alessandro Bombardi
# @version 1.0 (alpha release)
# Please report bugs to Alessandro.Bombardi@diamond.ac.uk
# Diamond Light Source Ltd.


import java
import shelve
import os

ShelvePath="C:\\temp\\"

## The class uses shelve to provide general methods to archive
# and retrieve variables.
class ShelveIO(java.lang.Object):

   ## The constructor
   #
   def __init__(self):

      self.SettingsFileName='BLSettings'
      self.path=ShelvePath+'settings'
      try:
         os.mkdir(os.path.abspath(os.path.join(os.curdir,self.path)))
      except:
         pass #"The directory already exists"
      self.cname=os.path.join(os.path.abspath(os.path.join(os.curdir,self.path,self.SettingsFileName)))

   def rebuildPath(self):
      self.cname=os.path.join(os.path.abspath(os.path.join(os.curdir,self.path,self.SettingsFileName)))
   ## public void setSettingsFileName(string fname)
   #
   def setSettingsFileName(self,fname):
      self.SettingsFileName=fname
      try:
         os.mkdir(os.path.abspath(os.path.join(os.curdir,self.path)))
      except:
         pass
      self.cname=os.path.join(os.path.abspath(os.path.join(os.curdir,self.path,self.SettingsFileName)))
      return

   ## public string getSettingsFileName()
   #
   def getSettingsFileName(self):
      return self.SettingsFileName

   ## public void setNewValue(string key, value)
   #
   def setNewValue(self,key,value):
      key = self.possiblyUnicodeToString(key)
      d=shelve.open(self.cname)
      flag = d.has_key(key)
      flag=0
      if flag==1:
         print "The key already exists, use ChangeValue() or change key"
      else:
         d[key]=value
      d.close()
      return

   ## public void delkey(string key)
   #  Delete the string and the content associated to it
   def delkey(self,key):
      d=shelve.open(self.cname)
      flag = d.has_key(key)
      if flag==1:
         del d[key]
      d.close()
      return

   ## public void ChangeValue(string key,value)
   #  Change the value associated to a given string
   def ChangeValue(self,key,value):
      key = self.possiblyUnicodeToString(key)
      d=shelve.open(self.cname)
      flag = d.has_key(key)
      if flag==1:
         del d[key]
      d[key]=value
      d.close()
      return

   ## public getValue(string key)
   #  Return the value associated to the given string
   def getValue(self,key):
      key = self.possiblyUnicodeToString(key)
      d=shelve.open(self.cname)
      a=d[key]
      d.close()
      return a

   ## public getAllKeys()
   #  Return the existing strings in the default filename
   def getAllKeys(self):
      d=shelve.open(self.cname)
      a=d.keys()
      d.close()
      return a

   def importFile(self):
      d=shelve.open(self.cname)
      d.close()
      return d


   ## Throws an error message
   #
   def __repr__(self):
      
      s = "SettingsFileName: %s\n" % self.SettingsFileName
      s+= "path: %s\n" % self.path
      s+= "cname: %s\n" % self.cname
      s+= "ShelveIO.ShelvePath: %s\n" % ShelvePath
      s+= "\n"
      keys = self.getAllKeys()
      keys.sort()
      for key in keys:
          s+= key + " : " + `self.getValue(key)` +"\n"
      return s
  
   def getAsDict(self):
      d = {}
      for key in self.getAllKeys():
          d[key] = self.getValue(key)
      return d    
    
   def possiblyUnicodeToString(self, s):
      if type(s) == unicode:
          print "WARNING: shelf '%s' received the unicode key '%s'" % (self.cname, s)
          return str(s)
      else:
          print "INFO:    shelf '%s' received the normal  key '%s'" % (self.cname, s)
      return s


