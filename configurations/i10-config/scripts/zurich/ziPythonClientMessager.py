'''
A socket communication message encoder to support Zurich Instrument operations using ziPython API.
It converts method call to string message before sending to a connected socket server which in turn 
control Zurich instrument.

Messages format implemented here is <Method_Name> followed by pickle serialised arguments with a specified 
separator in between items.
 
Created on 5 Jun 2019

@author: fy65
'''

from python2_socket.SocketClient import SocketClient
import pickle

class ZiDAQServerMessager():
    '''
    A message composer which translates method call into message string to be sent to a socket server connected to Zurich Instrument.
    '''

    MODULES_SUPPORTED=[ 'awg','dataAcquisition','deviceSettings','impedance','multiDeviceSync','pidAdvisor','record','scope','sweep','zoomFFT']
    METHOD_NOT_RELEVENT=('awg', 'deviceSettings', 'impedance', 'multiDeviceSync')
    
    def __init__(self, name, serverIPAddress, serverPort, terminator='\r\n', separator=' '):
        '''
        Constructor
        '''
        self.name=name
        self.host=serverIPAddress
        self.port=serverPort
        self.terminator=terminator
        self.separator=separator
        self.flat_dictionary_key=False
        self.socket=SocketClient(self.host, self.port, self.terminator, self)
    
### ziDAQServer interface API  
    def connect(self):
        '''connect with a Zurich Instruments data server.
        '''
        self.socket.send("connect")
        
    def disconnect(self):
        '''disconnect from a Zurich Instruments data server.
        '''
        self.socket.send("disconnect")
        
    def set(self, args=[]):
        '''Set multiple nodes.
        @param args: A list of path/value pairs
        '''
        self.socket.send("set"+self.separator+pickle.dumps(args))
        
    def setDouble(self, path, value):
        self.socket.send("setDouble"+self.separator + pickle.dumps(path) + self.separator + pickle.dumps(value))
        
    def setInt(self, path, value):
        self.socket.send("setInt"+self.separator+pickle.dumps(path)+self.separator+pickle.dumps(value))
        
    def setString(self, path, value):
        self.socket.send("setString"+self.separator+pickle.dumps(path)+self.separator+pickle.dumps(value))
        
    def flush(self):
        '''Flush all data in the socket connection and API buffers.
          Call this function before a subscribe with subsequent poll
          to get rid of old streaming data that might still be in
          the buffers
         '''
        self.socket.send("flush")
         
    def get(self, path, flat_dictionary_key=True):
        '''Return a dict with all nodes from the specified sub-tree.
           High-speed streaming nodes (e.g. /devN/demods/0/sample) are not returned.
           @param path: Path string of the node. Use wild card to select all.
           @param flat_dictionary_key [optional]: Specify which type of data structure to return.
                    Return data either as a flat dict (True) or as a nested
                    dict tree (False). Default = False.
         '''
        reply=self.socket.send("get"+self.separator+pickle.dumps(path)+self.separator+pickle.dumps(flat_dictionary_key))
        return pickle.loads(reply)
    
    def setDebugLevel(self, level):
        '''log levels are defined as following:
            trace:0, info:1, debug:2, warning:3, error:4, fatal:5, status:6
        '''
        self.socket.send("setDebugLevel"+self.separator+pickle.dumps(level))
        
    def subscribe(self, path):
        '''Subscribe to one or several nodes. Fetch data with the poll
          command. In order to avoid fetching old data that is still in the
          buffer this method executes a flush command before subscribing to data streams.
          @param path: Path string of the node. Use wild card to select all. 
                  Alternatively also a list of path strings can be specified
        '''
        self.socket.send("flush")
        self.socket.send("subscribe"+self.separator+pickle.dumps(path))
        
    def unsubscribe(self, path):
        '''Unsubscribe data streams. Use this command after recording to avoid
          buffer overflows that may increase the latency of other command.
          @param path: Path string of the node. Use wild card to select all. 
                  Alternatively also a list of path strings can be specified.
        '''
        self.socket.send("unsubscribe"+self.separator+pickle.dumps(path))
        
    def poll(self, record_time_sec, poll_timeout_ms, poll_flag_int, flat_dictionary_key):
        '''Continuously check for value changes (by calling pollEvent) in all
          subscribed nodes for the specified duration and return the data. If
          no value change occurs in subscribed nodes before duration + timeout,
          poll returns no data. This function call is blocking (it is
          synchronous). However, since all value changes are returned since
          either subscribing to the node or the last poll (assuming no buffer
          overflow has occurred on the Data Server), this function may be used
          in a quasi-asynchronous manner to return data spanning a much longer
          time than the specified duration. The timeout parameter is only
          relevant when communicating in a slow network. In this case it may be
          set to a value larger than the expected round-trip time in the
          network.
          Poll returns a dict tree containing the recorded data (see arg4)
          @param record_time_sec: Recording time in [s]. The function will block during that time.
          @param poll_timeout_ms: : Poll timeout in [ms]. Recommended value is 500ms.
          @param poll_flag_int [optional]: Poll flags.
                  FILL   = 0x0001: Fill holes (only possible in combination with FILL).
                  THROW  = 0x0004: Throw EOFError exception if sample loss is detected.
                  DETECT = 0x0008: Detect data loss holes.
          @param flat_dictionary_key [optional]: Specify which type of data structure to return.
                 Return data either as a flat dict (True) or as a nested dict tree (False). Default = False
        '''
        reply=self.socket.send("poll"+self.separator+pickle.dumps(record_time_sec)+self.separator+pickle.dumps(poll_timeout_ms)+self.separator+pickle.dumps(poll_flag_int)+self.separator+pickle.dumps(flat_dictionary_key))
        return pickle.loads(reply)
        
    def checkModuleNameValid(self, moduleName):
        if not moduleName in ZiDAQServerMessager.MODULES_SUPPORTED:
            raise Exception("Module name is not recognised. Acceptable module are %s" % ZiDAQServerMessager.MODULES_SUPPORTED)

    def loadModule(self, moduleName):
        '''start a thread to run the named Module, register it, and return the started module object
        @param moduleName: name of the sub-Module, one of 
        [ 'awg','dataAcquisition','deviceSettings','impedance','multiDeviceSync','pidAdvisor','record','scope','sweep','zoomFFT']
        @return: the module object
        '''
        self.checkModuleNameValid(moduleName)
        self.socket.send("loadModule"+self.separator+pickle.dumps(moduleName))
        
    def revision(self):
        '''Get the revision number of the Python interface of Zurich Instruments
        '''
        reply=self.socket.send("revision")
        return pickle.loads(reply)
    
    def version(self):
        '''Get version string of the Python interface of Zurich Instruments
        '''
        return self.socket.send("version")
        
    def sync(self):
        '''Synchronize all data path. Ensures that get and poll
          commands return data which was recorded after the
          setting changes before the sync command.
        '''
        self.socket.send("sync")

### sub-Module API
    def unloadModule(self,moduleName):
        '''end module running thread
        @param moduleName: the name of module 
        '''
        self.checkModuleNameValid(moduleName)
        self.socket.send("unloadModule"+self.separator+pickle.dumps(moduleName))
        
    def getValueFromModule(self, moduleName, path, flat=True): 
        '''Return a dict with all nodes from the specified path of specified module
        @param moduleName: the name of sub-Module object from which to get data
        @param path: Path string of the node of the Module,Use wild card to select all. 
        @param flat [optional]: Specify which type of data structure to return.
                    Return data either as a flat dict (True) or as a nested
                    dict tree (False). Default = True
        '''
        self.checkModuleNameValid(moduleName)
        reply=self.socket.send("getValueFromModule"+self.separator+pickle.dumps(moduleName)+self.separator+pickle.dumps(path)+self.separator+pickle.dumps(flat))
        return pickle.loads(reply)
    
    def setValueToModule(self, moduleName, path, value):
        '''set value to the specified path node of the specified module
        @param moduleName: the name of the sub-Module to which to set value
        @param path: the Path string of node in specified module
        @param value: the value to set to   
        '''
        self.checkModuleNameValid(moduleName)
        self.socket.send("setValueToModule"+self.separator+pickle.dumps(moduleName)+self.separator+pickle.dumps(path)+self.separator+pickle.dumps(value))
   
    def stopModuleCommandExecution(self, moduleName):
        '''stop command execution in the given module
        @param moduleName: the name of the execution module 
        '''
        self.checkModuleNameValid(moduleName)
        self.socket.send("stopModuleCommandExecution"+self.separator+pickle.dumps(moduleName))
    
    def isModuleCommandExecutionFinished(self, moduleName):
        '''Check if the command execution in the specified module has finished. Returns True if finished.
        @param moduleName: the name of the execution module 
        '''
        self.checkModuleNameValid(moduleName)
        reply=self.socket.send("isModuleCommandExecutionFinished"+self.separator+pickle.dumps(moduleName))
        return pickle.loads(reply)
    
    def execute(self, moduleName):
        '''starts execution of the given module if not yet running
        @param moduleName: the name of the sub-Module object 
        '''
        self.checkModuleNameValid(moduleName)
        self.socket.send("execute"+self.separator+pickle.dumps(moduleName))
        
    def progress(self, moduleName):
        '''Reports the progress of execution in given module with a number between 0 and 1
        @param moduleName: the name of the execution module to check progress 
        '''
        self.checkModuleNameValid(moduleName)
        reply=self.socket.send("progress"+self.separator+pickle.dumps(moduleName))
        return pickle.loads(reply)
    
    def subscribeToModule(self, moduleName, path):
        '''Subscribe to one or several nodes of the specified module. After subscription the 
          process can be started with the 'execute' command. During the
          process paths can not be subscribed or unsubscribed.
          @param moduleName: the name of the sub-Module object  
          @param path: Path string of the node of the module. Use wild card to select all. 
                  Alternatively also a list of path strings can be specified
        '''
        self.checkModuleNameValid(moduleName)
        if moduleName in ZiDAQServerMessager.METHOD_NOT_RELEVENT:
            raise Exception("Not relevant for %s module." % moduleName)
        self.socket.send("subscribeToModule"+self.separator+pickle.dumps(moduleName)+self.separator+pickle.dumps(path))

    
    def unsubscribeFromModule(self, moduleName, path):
        '''Unsubscribe from one or several nodes. During the process paths can not be subscribed or unsubscribed.
        @param moduleName: the name of the sub-Module object.
        @param path: Path string of the node of the module. Use wild card to select all. 
                    Alternatively also a list of path strings can be specified.
        '''
        self.checkModuleNameValid(moduleName)
        if moduleName in ZiDAQServerMessager.METHOD_NOT_RELEVENT:
            raise Exception("Not relevant for %s module." % moduleName)
        self.socket.send("unsubscribeFromModule"+self.separator+pickle.dumps(moduleName)+self.separator+pickle.dumps(path))
        
    def read(self, moduleName, flat=True):
        '''read data from specified module. If execution is still ongoing only a subset
        of the data is returned. If many triggers or huge data sets are acquired call 
        this method to keep memory usage reasonable. 
        This method expects users to subscribe, execute and unsubscribe to a path separately!
        @param moduleName: the name of the module object to read data from
        @param flat: Specify which type of data structure to return.
                Return data either as a flat dict (True) or as a nested dict tree (False). Default = True.
        '''
        self.checkModuleNameValid(moduleName)
        reply=self.socket.send("read"+self.separator+pickle.dumps(moduleName)+self.separator+pickle.dumps(flat))
        return pickle.loads(reply)
                        
    def readPath(self, moduleName, path, flat=True):
        '''read completed data from specified path of the specified module. This method blocks and wait 
        until all data are read. 
        @param moduleName: the name of the module object to read data from
        @param path: the Path string of the node to be read 
        @param flat: Specify which type of data structure to return.
                Return data either as a flat dict (True) or as a nested dict tree (False). Default = True.
       '''
        self.checkModuleNameValid(moduleName)
        reply=self.socket.send("readPath"+self.separator+pickle.dumps(moduleName)+self.separator+pickle.dumps(path)+self.separator+pickle.dumps(flat))
        return pickle.loads(reply)

## scope module    
    def readScope(self, path, flat=True):
        '''read all data from specified path of the scope module.This method blocks and wait 
        until all data are read. 
        @param path: the Path string of the node to be read 
        @param flat: Specify which type of data structure to return.
                Return data either as a flat dict (True) or as a nested dict tree (False). Default = True.
        '''
        reply=self.socket.send("readScope"+self.separator+pickle.dumps(path)+self.separator+pickle.dumps(flat))
        return pickle.loads(reply)

    def setScope(self, path, value):
        '''set a value to a specified path of the scope module.
        @param path: the Path string of the node to be set
        @param value: the valve to be set to.  
        '''
        self.socket.send("setScope"+self.separator+pickle.dumps(path)+self.separator+pickle.dumps(value))
    
    def getScope(self, path, flat=True):
        '''get value of the specified path of the scope module.
        @param path: the path string of the node to be read
        @param flat: Specify which type of data structure to return.
                Return data either as a flat dict (True) or as a nested dict tree (False). Default = True.
        '''
        reply=self.socket.send("setScope"+self.separator+pickle.dumps(path)+self.separator+pickle.dumps(flat))
        return pickle.loads(reply)
       
    def stopScope(self):
        '''stop execution of the scope module
        '''
        self.socket.send("stopScope")
    
    def isScopeFinished(self):
        ''' check if scope module execution is finished or not. 
        '''
        reply=self.socket.send("isScopeFinished")
        return pickle.loads(reply)

## sweep module        
    def readSweep(self, path, flat=True):
        '''read all data from specified path of the sweep module.This method blocks and wait 
        until all data are read. 
        @param path: the Path string of the node to be read 
        @param flat: Specify which type of data structure to return.
                Return data either as a flat dict (True) or as a nested dict tree (False). Default = True.
        '''
        reply=self.socket.send("readSweep"+self.separator+pickle.dumps(path)+self.separator+pickle.dumps(flat))
        return pickle.loads(reply)
     
    def setSweep(self, path, value):
        '''set a value to a specified path of the sweep module.
        @param path: the Path string of the node to be set
        @param value: the valve to be set to.  
       '''
        self.socket.send("setSweep"+self.separator+pickle.dumps(path)+self.separator+pickle.dumps(value))
    
    def getSweep(self, path, flat=True):
        '''get value of the specified path of the sweep module.
        @param path: the path string of the node to be read
        @param flat: Specify which type of data structure to return.
                Return data either as a flat dict (True) or as a nested dict tree (False). Default = True.
        '''
        reply=self.socket.send("getSweep"+self.separator+pickle.dumps(path)+self.separator+pickle.dumps(flat))
        return pickle.loads(reply)

    def stopSweep(self):
        '''stop execution of the sweep module
        '''
        self.socket.send("stopSweep")
        
    def isSweepFinished(self):
        ''' check if sweep module execution is finished or not. 
        '''
        reply=self.socket.send("isSweepFinished")
        return pickle.loads(reply)
        
