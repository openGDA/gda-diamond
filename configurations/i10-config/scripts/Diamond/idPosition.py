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
        myformat = "IdPosition(gap=%r, rowphase1=%r, rowphase2=%r, " + \
            "rowphase3=%r, rowphase4=%r, jawphase=%r)"
        return myformat % (self.gap, self.rowphase1, self.rowphase2,
            self.rowphase3, self.rowphase4, self.jawphase)

    def __str__(self):
        myformat = "gap=%r, rowphase1=%r, rowphase2=%r, " + \
            "rowphase3=%r, rowphase4=%r, jawphase=%r"
        return myformat % (self.gap, self.rowphase1, self.rowphase2,
            self.rowphase3, self.rowphase4, self.jawphase)

    def merge(self, mergable):
        assert((self.gap == None) != (mergable.gap == None))
        assert((self.rowphase1 == None) != (mergable.rowphase1 == None))
        assert((self.rowphase2 == None) != (mergable.rowphase2 == None))
        assert((self.rowphase3 == None) != (mergable.rowphase3 == None))
        assert((self.rowphase4 == None) != (mergable.rowphase4 == None))
        assert((self.jawphase == None) != (mergable.jawphase == None))
        return IdPosition(self.gap if mergable.gap == None else mergable.gap,
                          self.rowphase1 if mergable.rowphase1 == None else mergable.rowphase1,
                          self.rowphase2 if mergable.rowphase2 == None else mergable.rowphase2,
                          self.rowphase3 if mergable.rowphase3 == None else mergable.rowphase3,
                          self.rowphase4 if mergable.rowphase4 == None else mergable.rowphase4,
                          self.jawphase if mergable.jawphase == None else mergable.jawphase)