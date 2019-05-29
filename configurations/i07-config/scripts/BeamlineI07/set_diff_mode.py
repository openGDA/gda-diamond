# Diffractometer configuration switch script for use with Diffcalc 2.1 and later
#
# This replaces all the diff***.py scripts which have been moved into the
# deprecated folder and maps the motors for the various configurations to the
# internal diffcalc axes by calling the appropriate I07XX startup script from
# Diffcalc itself, The desired configuration is stored in the GDA property 
# gda.spring.profiles.active allowing it to be specified when the server starts
# and paving the ways for reloading of the Spring context to only include beans
# relevant to the configuration at a later stage.

from gda.configuration.properties import LocalProperties
from distutils.util import strtobool

# Carries out the switching to the specified mode with the facility for
# specifying options. Supported option values:
# >    silent       prevent the 'are you sure' message being displayed
def handle_options(mode, options=''):
    options = options.split(' ')
    if 'silent' not in options:
        choice = strtobool(raw_input(
            'This will re-map the diffcalc angles to those for {} and reset the namespace, do you wish to proceed (y/n) '
            .format(mode)))
    else:
        choice = True
    if choice:
        print 'Resetting diffractometer mode to {} - please wait whilst namespace is reset'.format(mode)
        LocalProperties.set('gda.active.diffractometer.mode', mode)
        reset_namespace()
    else:
        print 'Diffractometer reset cancelled'

def eh1v(options=''):
    handle_options('eh1v', options)

def eh1h(options=''):
    handle_options('eh1h', options)

def eh2(options=''):
    handle_options('eh2', options)

# Necessary to store the active mode in a local property so that it can 
# be updated without the need to restart the server. Defaults to eh1v
diffmode = LocalProperties.get('gda.active.diffractometer.mode')
if diffmode is None:
    diffmode = LocalProperties.get('gda.spring.profiles.active', 'eh1v')
LocalProperties.set('gda.active.diffractometer.mode', diffmode)

if diffmode in ['eh1v', 'eh1h', 'eh2']:
    pref = diffmode[:2].upper() + diffmode[2:]
    suff = '.py' if diffmode != 'eh2' else 'v.py'
    reset_script_name = '{}/diffcalc.git/startup/i07{}{}'.format(
        LocalProperties.get('gda.install.git.loc'), pref, suff)
    try_execfile(
        reset_script_name,
        'Switching diffractometer mappings to {} mode'.format(diffmode),
        False, True)
    alpha = {'eh1v' : mu, 'eh1h' : eta, 'eh2' : mu}.get(diffmode)
    gamma = gam
    omega = phi

silent = (lambda:'silent')()  # allows options without the need for brackets

alias('eh1h')
alias('eh1v')
alias('eh2')
alias('silent')
