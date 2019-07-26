'''
A socket communication message handler to support Zurich Instrument operations using ziPython API.
Instance of ..class:: ZurichInstrumentZiPythonyAPI is injected into .. class:: SocketServer which 
receives message for method call from a connected socket client.

It decodes received message and call related method to the instrument, and encode any response from 
the instrument and return it back to client. It only handle messages serialised using pickle.
 
Created on 5 Jun 2019

@author: fy65
'''
from python2_socket.MessageProcessor import Processor
import zhinst.ziPython  # @UnresolvedImport
from zhinst.ziPython import ScopeModule  # @UnresolvedImport
from collections import defaultdict
import pickle

class ZurichInstrumentZiPythonyAPI(Processor):
    '''
    A message processor which translates message received from socket client to method call to Zurich Instrument on the server.
    '''

    MODULES_SUPPORTED=[ 'awg','dataAcquisition','deviceSettings','impedance','multiDeviceSync','pidAdvisor','record','scope','sweep','zoomFFT']
    METHOD_NOT_RELEVENT=('awg', 'deviceSettings', 'impedance', 'multiDeviceSync')

    def __init__(self, deviceIPAddress='172.23.240.161', devicePort=8004, deviceLevel=6, separator=' '):
        '''
        Constructor
        '''
        self.host=deviceIPAddress
        self.port=devicePort
        self.level=deviceLevel
        self.flat_dictionary_key=False
        self.daq=zhinst.ziPython.ziDAQServer(self.host, self.port, self.level)
        self.modules={} #sub-module register
        for mname in ZurichInstrumentZiPythonyAPI.MODULES_SUPPORTED:
            self.modules[mname]=None
        self.separator=separator            
    
    def process(self, msg):
        '''parse message into method name and arguments list, and then call the method
        '''
        messages=msg.split(self.separator)
        name=messages[0]
        params=messages[1:]
        args=[]
        reply=None
        for param in params:
            #decode received message
            args.append(pickle.loads(param))
        if len(messages)==1:
            #no argument
            reply=getattr(self, name)()
        else:
            reply=getattr(self, name)(*args)            
        if reply:
            #encode response message
            return pickle.dumps(reply)

### ziDAQServer interface API  
    def connect(self):
        '''connect with a Zurich Instruments data server.
        '''
        self.daq.connect()
        
    def disconnect(self):
        self.daq.disconnect()
        
    def set(self, args=[]):
        '''Set multiple nodes.
        @param args: A list of path/value pairs
        '''
        self.daq.set(args)
        
    def setDouble(self, path, value):
        self.daq.setDouble(path, value)
        
    def setInt(self, path, value):
        self.daq.setInt(path, value)
        
    def setString(self, path, value):
        self.daq.setString(path, value)
        
    def flush(self):
        '''Flush all data in the socket connection and API buffers.
          Call this function before a subscribe with subsequent poll
          to get rid of old streaming data that might still be in
          the buffers
         '''
        self.daq.flush()
         
    def get(self, path, flat_dictionary_key=True):
        '''Return a dict with all nodes from the specified sub-tree.
           High-speed streaming nodes (e.g. /devN/demods/0/sample) are not returned.
           @param path: Path string of the node. Use wild card to select all.
           @param flat_dictionary_key [optional]: Specify which type of data structure to return.
                    Return data either as a flat dict (True) or as a nested
                    dict tree (False). Default = False.
         '''
        return self.daq.get(path, flat_dictionary_key)
    
    def setDebugLevel(self, level):
        '''log levels are defined as following:
            trace:0, info:1, debug:2, warning:3, error:4, fatal:5, status:6
        '''
        self.daq.setDebugLevel(level)
        
    def subscribe(self, path):
        '''Subscribe to one or several nodes. Fetch data with the poll
          command. In order to avoid fetching old data that is still in the
          buffer this method executes a flush command before subscribing to data streams.
          @param path: Path string of the node. Use wild card to select all. 
                  Alternatively also a list of path strings can be specified
        '''
        self.daq.flush()
        self.daq.subscribe(path)
        
    def unsubscribe(self, path):
        '''Unsubscribe data streams. Use this command after recording to avoid
          buffer overflows that may increase the latency of other command.
          @param path: Path string of the node. Use wild card to select all. 
                  Alternatively also a list of path strings can be specified.
        '''
        self.daq.unsubscribe(path)
        
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
        return self.daq.poll(record_time_sec, poll_timeout_ms, poll_flag_int, flat_dictionary_key)
    

    def checkModuleNameValid(self, moduleName):
        if not moduleName in ZurichInstrumentZiPythonyAPI.MODULES_SUPPORTED:
            raise Exception("Module name is not recognised. Acceptable module are %s" % ZurichInstrumentZiPythonyAPI.MODULES_SUPPORTED)

    def loadModule(self, moduleName):
        '''start a thread to run the named Module, register it, and return the started module object
        @param moduleName: name of the sub-Module, one of 
        [ 'awg','dataAcquisition','deviceSettings','impedance','multiDeviceSync','pidAdvisor','record','scope','sweep','zoomFFT']
        @return: the module object
        '''
        self.checkModuleNameValid(moduleName)
           
        if moduleName=='scope':
            #start a thread for running an asynchronous ScopeModule
            scope=self.daq.scopeModule()
            self.modules[moduleName]=scope
            return scope
        elif moduleName=='sweep':
            #start a thread for asynchronous sweeping
            sweep=self.daq.sweep()
            self.modules[moduleName]=sweep
            return sweep
        elif moduleName=='awg':
            #start a thread for running an asynchronous AwgModule
            awg=self.daq.awgModule()
            self.modules[moduleName]=awg
            return awg
        elif moduleName=='dataAcquisition':
            #start a thread for running an asynchronous Data Acquisition Module.
            dataAcquisition=self.daq.dataAcquisitionModule()
            self.modules[moduleName]=dataAcquisition
            return dataAcquisition
        elif moduleName=='deviceSettings':
            #start a thread for running an asynchronous DeviceSettingsModule
            deviceSettings=self.daq.deviceSettings()
            self.modules[moduleName]=deviceSettings
            return deviceSettings
        elif moduleName=='impedance':
            #start a thread for running an asynchronous ImpedanceModule
            impedance=self.daq.impedanceModule()
            self.modules[moduleName]=impedance
            return impedance
        elif moduleName=='multiDeviceSync':
            #start a thread for running an asynchronous MultiDeviceSync module
            multiDeviceSync=self.daq.multiDeviceSyncModule()
            self.modules[moduleName]=multiDeviceSync
            return multiDeviceSync
        elif moduleName=='pidAdvisor':
            #start a thread for running an asynchronous PidAdvisorModule
            pidAdvisor=self.daq.pidAdvisor()
            self.modules[moduleName]=pidAdvisor
            return pidAdvisor
        elif moduleName=='record':
            #start a thread for an asynchronous recording
            record=self.daq.record()
            self.modules[moduleName]=record
            return record
        elif moduleName=='zoomFFT':
            #start a thread for running an asynchronous ZoomFFTModule
            zoomFFT=self.daq.zoomFFT()
            self.modules[moduleName]=zoomFFT
            return zoomFFT
        
    def revision(self):
        '''Get the revision number of the Python interface of Zurich Instruments
        '''
        return self.daq.revision()
    
    def version(self):
        '''Get version string of the Python interface of Zurich Instruments
        '''
        return self.daq.version()
        
    def sync(self):
        '''Synchronize all data path. Ensures that get and poll
          commands return data which was recorded after the
          setting changes before the sync command.
        '''
        self.daq.sync()


### sub-Module API
    def unloadModule(self,moduleName):
        '''end module running thread
        @param moduleName: the name of module 
        '''
        self.checkModuleNameValid(moduleName)
        module=self.modules[moduleName]
        if module:
            module.clear()
        
    def getValueFromModule(self, moduleName, path, flat=True): 
        '''Return a dict with all nodes from the specified path of specified module
        @param moduleName: the name of sub-Module object from which to get data
        @param path: Path string of the node of the Module,Use wild card to select all. 
        @param flat [optional]: Specify which type of data structure to return.
                    Return data either as a flat dict (True) or as a nested
                    dict tree (False). Default = True
        '''
        self.checkModuleNameValid(moduleName)
        module=self.modules[moduleName]
        if not module:
            module=self.loadModule(moduleName)
        return module.get(path, flat)
    
    def setValueToModule(self, moduleName, path, value):
        '''set value to the specified path node of the specified module
        @param moduleName: the name of the sub-Module to which to set value
        @param path: the Path string of node in specified module
        @param value: the value to set to   
        '''
        self.checkModuleNameValid(moduleName)
        module=self.modules[moduleName]
        if not module:
            module=self.loadModule(moduleName)
        module.set(path, value)
    
    def stopModuleCommandExecution(self, moduleName):
        '''stop command execution in the given module
        @param moduleName: the name of the execution module 
        '''
        self.checkModuleNameValid(moduleName)
        module=self.modules[moduleName]
        if not module:
            module=self.loadModule(moduleName)
        module.finish()
    
    def isModuleCommandExecutionFinished(self, moduleName):
        '''Check if the command execution in the specified module has finished. Returns True if finished.
        @param moduleName: the name of the execution module 
        '''
        self.checkModuleNameValid(moduleName)
        module=self.modules[moduleName]
        if not module:
            module=self.loadModule(moduleName)
        if isinstance(module, ScopeModule):
            #Scope module is always running, use progress instead
            return not module.progress()<1
        return module.finished()
    
    def execute(self, moduleName):
        '''starts execution of the given module if not yet running
        @param moduleName: the name of the sub-Module object 
        '''
        self.checkModuleNameValid(moduleName)
        module=self.modules[moduleName]
        if not module:
            module=self.loadModule(moduleName)
        module.execute()
        
    def progress(self, moduleName):
        '''Reports the progress of execution in given module with a number between 0 and 1
        @param moduleName: the name of the execution module to check progress 
        '''
        self.checkModuleNameValid(moduleName)
        module=self.modules[moduleName]
        if not module:
            module=self.loadModule(moduleName)
        return module.progress()
    
    def subscribeToModule(self, moduleName, path):
        '''Subscribe to one or several nodes of the specified module. After subscription the 
          process can be started with the 'execute' command. During the
          process paths can not be subscribed or unsubscribed.
          @param moduleName: the name of the sub-Module object  
          @param path: Path string of the node of the module. Use wild card to select all. 
                  Alternatively also a list of path strings can be specified
        '''
        self.checkModuleNameValid(moduleName)
        if moduleName in ZurichInstrumentZiPythonyAPI.METHOD_NOT_RELEVENT:
            raise Exception("Not relevant for %s module." % moduleName)
        module=self.modules[moduleName]
        if not module:
            module=self.loadModule(moduleName)
        module.subscribe(path)
    
    def unsubscribeFromModule(self, moduleName, path):
        '''Unsubscribe from one or several nodes. During the process paths can not be subscribed or unsubscribed.
        @param moduleName: the name of the sub-Module object.
        @param path: Path string of the node of the module. Use wild card to select all. 
                    Alternatively also a list of path strings can be specified.
        '''
        self.checkModuleNameValid(moduleName)
        if moduleName in ZurichInstrumentZiPythonyAPI.METHOD_NOT_RELEVENT:
            raise Exception("Not relevant for %s module." % moduleName)
        module=self.modules[moduleName]
        if not module:
            module=self.loadModule(moduleName)
        module.unsubscribe(path)
        
    def read(self, moduleName, flat=True):
        '''read data from specified module. If execution is still ongoing only a subset
        of the data is returned. If many triggers or huge data sets are acquired call 
        this method to keep memory usage reasonable.
        @param moduleName: the name of the module object to read data from
        @param flat: Specify which type of data structure to return.
                Return data either as a flat dict (True) or as a nested dict tree (False). Default = True.
        '''
        self.checkModuleNameValid(moduleName)
        module=self.modules[moduleName]
        if not module:
            module=self.loadModule(moduleName)
        return module.read(flat)
                        
    def readPath(self, moduleName, path, flat=True):
        '''read completed data from specified path of the specified module. This method blocks and wait 
        until all data are read. 
        @param moduleName: the name of the module object to read data from
        @param path: the Path string of the node to be read 
        @param flat: Specify which type of data structure to return.
                Return data either as a flat dict (True) or as a nested dict tree (False). Default = True.
       '''
        self.checkModuleNameValid(moduleName)
        module=self.modules[moduleName]
        if not module:
            module=self.loadModule(moduleName)
        module.subscribe(path)
        module.execute()
        data1=module.read(flat)
        data=defaultdict(list)
        while module.progress() < 1:
            data2=module.read(flat)
            for k, v in chain(data1.items(), data2.items()):
                data[k].append(v)
        module.unsubscribe(path)
        return data

## scope module    
    def readScope(self, path, flat=True):
        '''read all data from specified path of the scope module.This method blocks and wait 
        until all data are read. 
        @param path: the Path string of the node to be read 
        @param flat: Specify which type of data structure to return.
                Return data either as a flat dict (True) or as a nested dict tree (False). Default = True.
        '''
        scope=self.daq.scopeModule()
        scope.subscribe(path)
        scope.execute()
        data1=scope.read(flat)
        data=defaultdict(list)
        while scope.progress() == 1:
            data2=scope.read(flat)
            for k, v in chain(data1.items(), data2.items()):
                data[k].append(v)
        scope.unsubscribe(path)
        return data

    def setScope(self, path, value):
        '''set a value to a specified path of the scope module.
        @param path: the Path string of the node to be set
        @param value: the valve to be set to.  
       '''
        scope=self.daq.scopeModule()
        scope.set(path, value)
    
    def getScope(self, path, flat=True):
        '''get value of the specified path of the scope module.
        @param path: the path string of the node to be read
        @param flat: Specify which type of data structure to return.
                Return data either as a flat dict (True) or as a nested dict tree (False). Default = True.
        '''
        scope=self.daq.scopeModule()
        return scope.get(path, flat)
        
    def stopScope(self):
        '''stop execution of the scope module
        '''
        scope=self.daq.scopeModule()
        scope.finish()
    
    def isScopeFinished(self):
        ''' check if scope module execution is finished or not. 
        '''
        scope=self.daq.scopeModule()
        return scope.finished()        

## sweep module        
    def readSweep(self, path, flat=True):
        '''read all data from specified path of the sweep module.This method blocks and wait 
        until all data are read. 
        @param path: the Path string of the node to be read 
        @param flat: Specify which type of data structure to return.
                Return data either as a flat dict (True) or as a nested dict tree (False). Default = True.
        '''
        sweep=self.daq.sweep()
        sweep.subscribe(path)
        sweep.execute()
        data1=sweep.read(flat)
        data=defaultdict(list)
        while sweep.progress() == 1:
            data2=sweep.read(flat)
            for k, v in chain(data1.items(), data2.items()):
                data[k].append(v)
        sweep.unsubscribe(path)
        return data
     
    def setSweep(self, path, value):
        '''set a value to a specified path of the sweep module.
        @param path: the Path string of the node to be set
        @param value: the valve to be set to.  
       '''
        sweep=self.daq.sweep()
        sweep.set(path, value)
    
    def getSweep(self, path, flat=True):
        '''get value of the specified path of the sweep module.
        @param path: the path string of the node to be read
        @param flat: Specify which type of data structure to return.
                Return data either as a flat dict (True) or as a nested dict tree (False). Default = True.
        '''
        sweep=self.daq.sweep()
        return sweep.get(path, flat)

    def stopSweep(self):
        '''stop execution of the sweep module
        '''
        sweep=self.daq.sweep()
        sweep.finish()
        
    def isSweepFinished(self):
        ''' check if sweep module execution is finished or not. 
        '''
        sweep=self.daq.sweep()
        return sweep.finished()
        
