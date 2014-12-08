import logging
import logging.handlers
LOG_FILENAME='/dls_sw/i09/var/scripts.log'
FORMAT='%(asctime)-15s %(levelname)-8s %(name)-12s %funcName)s %(lineno)d %(message)s'
#logging.basicConfig(format=FORMAT,filename=LOG_FILENAME,filemode='w')

# logging to console, i.e. sys.stderr
console = logging.StreamHandler() 
console.setLevel(logging.INFO)
formatter=logging.Formatter('%(name)-12s: %(levelname)-8s %funcName)s %(lineno)d %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
#i09 script loggings to a file
logger = logging.getLogger("i09.scripts") 
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=20000000, backupCount=5)
#timeRotateHandler=logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="d", backupCount=7)
logger.addHandler(handler)




