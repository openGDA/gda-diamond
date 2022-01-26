from gda.device import ScannableMotion
from gda.device.scannable.scannablegroup import DeferredAndTrajectoryScannableGroup,\
    ScannableGroup, CoordinatedScannableGroup, CoordinatedScannableGroup, ScannableMotionWithScannableFieldsBase
ScannableMotionWithScannableFieldsBase.ScannableField
from gda.jython.commands.GeneralCommands import alias


NOT_SPECIFIED = object()
ROOT_NAMESPACE = {}
NOMINAL_LIMITS = {}

def _try_to_tuple(possibly_iterable):
    try:
        t = tuple(possibly_iterable)
        return  t[0] if len(t) == 1 else t
    except TypeError:
        return possibly_iterable
    
def _set_llm(scn, new_lower):
    if new_lower is NOT_SPECIFIED:
        new_lower = scn()
    new_lower = _try_to_tuple(new_lower)
    old_lower = _try_to_tuple(scn.getLowerGdaLimits())
    scn.setLowerGdaLimits(new_lower)
    current_lower = _try_to_tuple(scn.getLowerGdaLimits())
    return old_lower, current_lower

def _set_ulm(scn, new_upper):
    if new_upper is NOT_SPECIFIED:
        new_upper = scn()
    new_upper = _try_to_tuple(new_upper)
    old_upper = _try_to_tuple(scn.getUpperGdaLimits())
    scn.setUpperGdaLimits(new_upper)
    current_upper = _try_to_tuple(scn.getUpperGdaLimits())
    return old_upper, current_upper

def setulm(scn, new_upper=NOT_SPECIFIED):
    old_upper, current_upper = _set_ulm(scn, new_upper)
    print scn.name + " upper limit : %s --> %s" % (old_upper, current_upper)

def setllm(scn, new_lower=NOT_SPECIFIED):
    old_lower, current_lower = _set_llm(scn, new_lower)
    print scn.name + " lower limit : %s --> %s" % (old_lower, current_lower)

def setulm_no_offset(scn, new_upper_below_offset=NOT_SPECIFIED):
    scn_offset = scn.getOffset()[0] if scn.getOffset()!=None else 0.
    if scn_offset is None:
        scn_offset = 0
    old_upper, current_upper = _set_ulm(scn, new_upper_below_offset + scn_offset)
    print scn.name + " upper limit (below offset) : %s --> %s" % (None if old_upper is None else (old_upper - scn_offset), current_upper - scn_offset)

def setllm_no_offset(scn, new_lower_below_offset=NOT_SPECIFIED):
    scn_offset = scn.getOffset()[0] if scn.getOffset()!=None else 0.
    if scn_offset is None:
        scn_offset = 0
    old_lower, current_lower = _set_llm(scn, new_lower_below_offset + scn_offset)
    print scn.name + " upper limit (below offset) : %s --> %s" % (None if old_lower is None else (old_lower - scn_offset), current_lower - scn_offset)

def setlm(scn, new_lower, new_upper):
    setllm(scn, new_lower)
    setulm(scn, new_upper)

def setlm_no_offset(scn, new_lower, new_upper):
    setllm_no_offset(scn, new_lower)
    setulm_no_offset(scn, new_upper)
    
#
#kdelta.setUpperGdaLimits(delta_no_offset_high + kdelta_offset_value)
#kdelta.setLowerGdaLimits(delta_no_offset_low + kdelta_offset_value)


def _nearly_equal(a, b):
    return abs(float(b) - float(a)) < .0001

def _show_scn(scn):
    lower = scn.getLowerGdaLimits()
    upper = scn.getUpperGdaLimits()
    if upper is not None or lower is not None:
        if lower is not None:
            lower = tuple(lower) if len(lower) > 1 else lower[0]
        if upper is not None:
            upper = tuple(upper) if len(upper) > 1 else upper[0]
        
        offset = 0 if scn.getOffset() is None else scn.getOffset()[0]
        
        if offset is None:  #  scn.getOffset()[0] was None
            offset = 0
        
        if NOMINAL_LIMITS.has_key(scn.name):
            nom_lower, nom_upper =  NOMINAL_LIMITS[scn.name]
            # print "lower, upper, nom_lower, nom_upper, offset = ", lower, upper, nom_lower, nom_upper, offset
            nom_lower += offset
            nom_upper += offset
            nom_differ_lower = None if ((lower is None) or _nearly_equal(nom_lower, lower)) else nom_lower
            nom_differ_upper = None if ((upper is None) or _nearly_equal(nom_upper, upper)) else nom_upper
            nominal = nom_differ_lower is None and nom_differ_upper is None
            has_nominal = True
            #print nom_differ_lower, nom_differ_upper, nominal
        else:
            nom_differ_lower = None
            nom_differ_upper = None
            nominal = False
            has_nominal = False
            
        s = ('/' if has_nominal and not nominal else ' ')
        s += '           ' if lower is None else '%8s <= '%(lower,)
        s += '%-6s'%scn.name
        s += '' if upper is None else ' <= %s'%(upper,)
        if offset:
            s += ' (+ %s)' % offset
        if not has_nominal:
            s += ' (no nominal)'
        if has_nominal and not nominal:
            s += ' (*non nominal)\n'
            s += '\\' + ('            ' if nom_differ_lower is None else '%8s <= '%(nom_differ_lower,))
            s += '      '
            s += '' if nom_differ_upper is None else ' <= %s'%(nom_differ_upper,)
            

        
        return s
    return None

def showlm():
    """Print the gda limits for all scannables in namespace that possess them"""

            
    scannable_groups = sorted(list(set([o for o in ROOT_NAMESPACE.values() if isinstance(o, (ScannableGroup, ScannableMotionWithScannableFieldsBase))])))
    scannable_group_members = []
    
    def _get_members(grp):
        try:
            return grp.getGroupMembers()
        except AttributeError:
            return [grp.__getattr__(name) for name in grp.inputNames]
        
    for group in scannable_groups:
        scannable_group_members += _get_members(group)
    print
    # 1. Non group members
    for key in sorted(ROOT_NAMESPACE.keys()):
        o = ROOT_NAMESPACE[key]
        if isinstance(o, ScannableMotion) and o not in scannable_group_members and not isinstance(o, (ScannableMotionWithScannableFieldsBase.ScannableField, ScannableMotionWithScannableFieldsBase)):
            r = _show_scn(o)
            if r is not None:
                print r
            
    #2. Group members
    for group in scannable_groups:
        displayed_group = False
        for scn in _get_members(group):
            r = _show_scn(scn)
            if r is not None:
                if not displayed_group:
                    print '\n  ==%s==\n' % group.name
                    displayed_group = True
                print r
                    
        if isinstance(group, CoordinatedScannableGroup):
            validator_dict = dict(group.getAdditionalPositionValidators())
            for name in validator_dict:
                if not displayed_group:
                    print '\n        ==%s==\n' % group.name
                    displayed_group = True
                print "  %s : %s" % (name, validator_dict[name])


alias('setulm')
alias('setllm')
alias('setlm')
alias('setulm_no_offset')
alias('setllm_no_offset')
alias('setlm_no_offset')
alias('showlm')
