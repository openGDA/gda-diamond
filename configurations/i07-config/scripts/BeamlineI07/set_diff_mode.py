# Diffractometer configuration switch script for use with Diffcalc 2.1 and later
#
# This replaces all the diff***.py scripts which have been moved into the
# deprecated folder and maps the motors for the various configurations to the
# internal diffcalc axes by calling the appropriate I07XX startup script from
# Diffcalc itself.

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


def set_motor_aliases(diffmode):
    global alpha, chi, delta, gamma, omega, theta
    alpha = {'eh1v' : None, 'eh1h' : diff1alpha, 'eh2' : None}.get(diffmode)
    chi = {'eh1v' : None, 'eh1h' : diff1chi, 'eh2' : None}.get(diffmode)
    delta = {'eh1v' : None, 'eh1h' : diff1delta, 'eh2' : None}.get(diffmode)
    gamma = {'eh1v' : None, 'eh1h' : diff1gamma, 'eh2' : None}.get(diffmode)
    omega  = {'eh1v' : None, 'eh1h' : diff1omega, 'eh2' : None}.get(diffmode)
    theta = {'eh1v' : None, 'eh1h' : diff1theta, 'eh2' : None}.get(diffmode)

# Necessary to store the active mode in a local property so that it can 
# be updated without the need to restart the server. Defaults to eh1h
diffmode = LocalProperties.get('gda.active.diffractometer.mode')
if diffmode is None:
    diffmode = 'eh1h'
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
    #set_motor_aliases(diffmode)

if diffmode == 'eh1v':
    pos(mo8ax8, "CS2")
else:
    pos(mo8ax8, "None")

silent = (lambda:'silent')()  # allows options without the need for brackets

alias('eh1h')
alias('eh1v')
alias('eh2')
alias('silent')
