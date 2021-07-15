###
# Copyright 2016 Diamond Light Source Ltd.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

'''External python caller that does not depend on scisoftpy and its environment
'''

import os
_env = os.environ


'''
This is a way to create an external python process, execute a function,
with argument passing and output return, plus exception handling

. create python process with python path
.   setup import in process
.   call function
.   handle exceptions
. exception raising
'''

from os import path as _path


import sys
sys.path.append('/dls_sw/lab44/software/gda/workspace_git/scisoft-core.git/uk.ac.diamond.scisoft.python/src')

def pyenv(exe=None, path=None, ldpath=None):
    '''Get python environment
    exe -- python executable
    path -- list of paths
    ldpath -- list of dynamic library paths
    return tuple containing python executable string, python path as list 
    '''

    if exe is None:
        pyexe = sys.executable
    else:
        pyexe = exe

    if path is None:
        pypath = [ p for p in sys.path if not p.endswith('jar') ]
    else:
        pypath = list(path)

    if ldpath:
        pyldpath = ldpath
    else:
        pyldpath = None

    return pyexe, pypath, pyldpath


def find_module_path(path, module):
    modulefile = module +".py"
    for p in path:
        p = _path.abspath(p)
        if _path.exists(_path.join(p, module)):
            return p
        if _path.exists(_path.join(p, modulefile)):
            return p
    return None

from uk.ac.diamond.scisoft.python import PythonSubProcess

class ExternalFunction(object):
    '''Emulates a function object with an attached python process
    '''
    def __init__(self, exe, env, module, function, keep):
        self.exe = exe
        self.env = env
        self.mod = module
        self.func = function
        self.keep = keep
        self.thd = None
        self.proc = None
        if self.keep:
            self._mk_process()

    def _mk_process(self):
        self.proc = PythonSubProcess(self.exe, self.env)
#         self.proc.stdin.write('import sys\n')
#         self.proc.stdin.write('sys.path.append("%s")\n' % PYDEV_SRC)
        _out, err = self.proc.communicate('from %s import %s\n' % (self.mod, self.func))
        if err:
            raise RuntimeError, "Problem with import: %s" % err

    def stop(self):
        '''Stop process
        '''
        if self.proc:
            self.proc.stop()
            self.proc = None

    def __del__(self):
        self.stop()

    def __call__(self, *arg, **kwarg):
        try:
            if not self.keep or not self.proc:
                self._mk_process()
            #parse arguments 
            argsAsString=''
            for each in arg:
                if isinstance(each, str):
                    argsAsString+='"'+str(each)+'", '
                else:
                    argsAsString+=str(each)+', '
            for key,value in kwarg.items():
                if isinstance(value, str):
                    argsAsString+=str(key)+'="'+str(value)+'", '
                else:
                    argsAsString+=str(key)+'='+str(value)+', '
            argsAsString=argsAsString.strip(',')
            out, err = self.proc.communicate('print %s(%s)\n' % (self.func, argsAsString))
            if err:
                raise RuntimeError, "Problem with running external process: %s" % err
            return out
        finally:
            if not self.keep:
                self.stop()

def create_function(function, module=None, exe=None, path=None, extra_path=None, ldpath = None, keep=True):
    '''Create a function that will run in an external python

    function   -- function or its name, if the former then module is not needed
    module     -- name of module
    exe        -- path of Python executable
    path       -- list of Python paths
    extra_path -- list of extra Python (prepended) paths for local packages (the directory at which the module exists)
    ldpath     -- list of dynamic library paths
    keep       -- if True, keep process alive

    returns a function object

    For example, you have a module called blah with a function foo then
    >>> ext_foo = create_function("foo", "blah", extra_path=["path/to/your/module"])
    >>> ext_foo(1.2, 3.4, k=True)
    
    If blah is in your current python path then,
    >>> from blah import foo
    >>> ext_foo = create_function(foo)
    '''
    if not isinstance(function, str):
        fn = function
        function = fn.__name__
        if fn.__module__ == '__main__':
            raise RuntimeError, "Cannot create function as it needs to be in a module of its own"
        if module is None:
            module = fn.__module__

    exe, path, ldpath = pyenv(exe, path, ldpath)
    p = find_module_path(path, module)
    if p is None:
        p = find_module_path(sys.path, module)
    if p and p not in path:
        path.insert(0, p)
    if extra_path:
        if p is None:
            p = find_module_path(extra_path, module)
        path = extra_path + path
    if p is None:
        raise ValueError, "Cannot find module in path: try specifying it in extra_path"
    env = dict(_env)
    env['PYTHONPATH'] = os.pathsep.join(path)
    if ldpath:
        if sys.platform == 'win32':
            key = 'PATH'
        elif sys.platform == 'darwin':
            key = 'DYLD_LIBRARY_PATH'
        else:
            key = 'LD_LIBRARY_PATH'
        env[key] = os.pathsep.join(ldpath)
    return ExternalFunction(exe, env, module, function, keep)
