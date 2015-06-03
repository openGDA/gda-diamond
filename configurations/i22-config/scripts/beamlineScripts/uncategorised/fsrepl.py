#Set up the detector with long enough wait pause to allow time for the sample stage to move in
#Need as many frames as you have pressure points
#Load script from the script perspective by pressing the run button
#To Run the script from the Jython Console type "fsrepl=FSRepl(121.41,121.41)" where numbers in brackets are inbeam and outofbeam positions in basex
#You also need to type "ncddetectors.addIObserver(fsrepl)" in the Jython Console to ensure the detectors are aware of this script and will cooperate
#To change the inbeam position you can type "fsrepl.inbeam=121.41" in the Jython Console, "fsrepl.outbeam=121.41" for out of beam position
#You may need to delete the object first, otherwise the old values remain. To do this type "del fsrepl" in the jython console
#At the end you need to type "ncddetectors.deleteIObserver(fsrepl)" in the Jython Console to allow you to use the GDA again normally


class FSRepl(gda.observable.IObserver):
    def __init__(self, inbeam, outbeam):
        self.inbeam = inbeam
        self.outbeam = outbeam
        self.oldstate = None
    
    def update(self, source, arg):
        try:
            state = arg.getCurrentStatus()
            if state == self.oldstate:
                return
            self.oldstate = state
            if state == "DEAD PAUSE":
                print "moving out"
                base_x.asynchronousMoveTo(self.outbeam)
            elif state == "DEAD FRAME":
                print "moving in"
                base_x.asynchronousMoveTo(self.inbeam)
            elif state == "LIVE FRAME":
                print "exposing I guess"
        except:
            print "unhappy update"
