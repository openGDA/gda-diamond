"""
Insertion Device position class
For use with I10 insertion device scannables on GDA at Diamond Light Source
"""
    
class IdPosition(list):
    def __init__(self, gap, rowphase1, rowphase2, rowphase3, rowphase4, jawphase):
        self.gap = gap
        self.rowphase1 = rowphase1
        self.rowphase2 = rowphase2
        self.rowphase3 = rowphase3
        self.rowphase4 = rowphase4
        self.jawphase = jawphase
        
    def __repr__(self):
        format = "IdPosition(gap=%r, rowphase1=%r, rowphase2=%r, " + \
            "rowphase3=%r, rowphase4=%r, jawphase=%r)"
        return format % (self.gap, self.rowphase1, self.rowphase2,
            self.rowphase3, self.rowphase4, self.jawphase)
    
    def __str__(self):
        format = "gap=%r, rowphase1=%r, rowphase2=%r, " + \
            "rowphase3=%r, rowphase4=%r, jawphase=%r"
        return format % (self.gap, self.rowphase1, self.rowphase2,
            self.rowphase3, self.rowphase4, self.jawphase)
