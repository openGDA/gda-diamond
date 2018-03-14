'''
Created on 14 Aug 2012

@author: fy65
'''
import logging
class ConnInfo:
    ''' An example class which shows how an arbitrary class can be used as the ‘extra’ context information repository passed to a LoggerAdapter. '''

    def __getitem__(self, name):

        ''' To allow this instance to look like a dict. ''' 
        from random import choice 
        if name == "ip":
            result = choice(["127.0.0.1", "192.168.0.1"])
        elif name == "user":
            result = choice(["jim", "fred2", "sheila"])
        else:
            result = self.__dict__.get(name, "?")
        return result
    
    def __iter__(self):
        """ To allow iteration over keys, which will be merged into the LogRecord dict before formatting and output. """
        keys = ["ip", "user"] 
        keys.extend(self.__dict__.keys()) 
        return keys.__iter__()

if __name__ == "__main__":
    from random import choice 
    levels = (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL) 
    a1 = logging.LoggerAdapter(logging.getLogger("a.b.c"),{ "ip" : "123.231.231.123", "user" : "sheila" })
    logging.basicConfig(level=logging.DEBUG,format="%(asctime)-15s %(name)-5s %(levelname)-8s IP: %(ip)-15s User: %(user)-8s %(message)s")
    a1.debug("A debug message") 
    a1.info("An info message with %s", "some parameters") 
    a2 = logging.LoggerAdapter(logging.getLogger("d.e.f"), ConnInfo()) 
    for x in range(10):
        lvl = choice(levels) 
        lvlname = logging.getLevelName(lvl) 
        a2.log(lvl, "A message at %s level with %d %s", lvlname, 2, "parameters")

