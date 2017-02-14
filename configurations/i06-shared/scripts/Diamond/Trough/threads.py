# import the needed modules

import sys
import exceptions

## create the Factorial class, a general purpose factorial calculation engine
class Factorial:
    """A general purpose factorial calculation engine"""

## define the constructor
    def __init__ (self):
        self.__listeners = []
        self.__cancelled = 0

## allow other classes to register event listeners; 
##-    used to track calculation progress
## A "listener" is a function that takes an integer % argument
    def addListener (self, listener):
        if listener not in self.__listeners:
            self.__listeners.append(listener)

    def addListeners (self, listeners):
        for l in listeners:
            self.addListener(l)

    def removeListener (self, listener):
        self.__listeners.remove(listener)

    def removeListeners (self, listeners):
        for l in listeners:
            self.removeListener(l)

    def fireListeners (self, value):  # notify all listeners
        for func in self.__listeners:
            func(value)

## allow others to cancel a long running calculation
    def cancel (self):
        self.__cancelled = 1

## perform the factorial calculation; 
##     may take a long time (many minutes) for big numbers
    def calculate (self, value):
        if type(value) != type(0) or value < 0:
            raise ValueError,  \
               "only positive integers supported: " + str(value)

        self.__cancelled = 0
        result = 1L
        self.fireListeners(0)   # 0% done
        # calculate factorial ## may take quite a while
        if value > 1:           # need to do calculation
            last = 0
            # using iteration (vs. recursion) to increase performance
            # and eliminate any stack overflow possibility
            for x in xrange(1, value + 1):
                if self.__cancelled: break  # early abort requested
                result = result * x         # calc next value
                next = x * 100 / value
                if next != last:            # signal progress 
                    self.fireListeners(next)
                    last = next
        self.fireListeners(100)  # 100% done
        if self.__cancelled: result = -1
        return result

# test case
if __name__ == "__main__":
    print sys.argv[0], "running..."
    fac = Factorial()

    def doFac (value):
        try:
            print "For", value, "result =", fac.calculate(value)
        except ValueError, e: 
            print "Exception -", e

    doFac(-1)
    doFac(0)
    doFac(1)
    doFac(10)
    doFac(100)
    doFac(1000)


## import the needed modules
import sys
import string
from types import *

from java import lang
from java import awt
from java.awt import event as awtevent
from javax import swing

## PromptedValueLayout is a customized Java LayoutManager not discussed here 
##    but included with the resources
from com.ibm.articles import PromptedValueLayout as ValueLayout

## support asynchronous processing
class LongRunningTask(lang.Thread):
    def __init__ (self, runner, param=None):
        self.__runner = runner   # function to run
        self.__param = param     # function parameter (if any)
        self.complete = 0
        self.running = 0

## Java thread body
    def run (self):
        self.complete = 0; self.running = 1
        if self.__param is not None: 
            self.result = self.__runner(self.__param)
        else:
            self.result = self.__runner()
        self.complete = 1; self.running = 0

## start a long running activity
def doAsync (func, param):
    LongRunningTask(func, param).start()

## Swing GUI services must be called only on the AWT event thread,
class SwingNotifier(lang.Runnable):
    def __init__ (self, processor, param=None):
        self.__runner = processor  # function to do GUI updates
        self.__param = param       # function parameter (if any)

## Java thread body
    def run (self):
        if self.__param is not None: self.__runner(self.__param)
        else:                        self.__runner()

    def execute (self):
        swing.SwingUtilities.invokeLater(self)



     ## define and construct a GUI for factorial calculation
class FactorialGui(swing.JPanel):
    """Create and process the GUI."""

    def __init__ (self, engine):
        swing.JPanel.__init__(self)
        self.__engine = engine
        engine.addListener(self.update)
        self.createGui()

    def update (self, value):          # do on AWT thread
        SwingNotifier(self.updateProgress, value).execute()

    def updateProgress (self, value):  # display progress updates
        self.__progressBar.value = value

## Calculate button press handler
    def doCalc (self, event):          # request a factorial
        self.__outputArea.text = ""
        ivalue = self.__inputField.text # get value to calculate
        value = -1
        try: value = int(ivalue)        # convert it
        except: pass
        if value < 0:                   # verify it
            self.__statusLabel.text = \
               "Cannot make into a positive integer value: " + ivalue
        else:
            self.__calcButton.enabled = 0
            self.__cancelButton.enabled = 1
            msg = "Calculating factorial of %i..." % value
            if value > 25000: msg += "; May take a very long time to complete!"
            self.__statusLabel.text = msg  # tell user we're busy
            doAsync(self.calcFac, value)   # do the calculation

## main calculation worker
    def calcFac (self, value): 
        stime = lang.System.currentTimeMillis()
        fac = self.__engine.calculate(value)   # time calculation
        etime = lang.System.currentTimeMillis()
        svalue = ""; order = 0
        if fac >= 0:          # we have a result, not cancelled
            svalue = str(fac); order = len(svalue) - 1
            formatted = ""
            while len(svalue) > 100:  # wrap long numbers
                formatted += svalue[0:100] + '\n'
                svalue = svalue[100:]
            formatted += svalue
            svalue = formatted
        ftime = lang.System.currentTimeMillis()

        SwingNotifier(self.setResult, \
          (svalue, order, ftime - stime, etime - stime)).execute()

## display the result
    def setResult (self, values):
        svalue, order, ttime, ftime = values
        self.__cancelButton.enabled = 0
        if len(svalue) > 0:
            self.__statusLabel.text = \
               "Setting result - Order: 10**%i" % order
            self.__outputArea.text = svalue
            self.__statusLabel.text = \
                "Total time: %ims, Calc time: %ims, Order: 10**%i" % \
                      (ttime, ftime, order)
        else:
            self.__statusLabel.text = "Cancelled"

        self.__calcButton.enabled = 1

## Cancel button press handler
    def doCancel (self, event):       # request a cancel
        self.__cancelButton.enabled = 0
        self.__engine.cancel()

## create (layout) the GUI
    def createGui (self):             # build the GUI
        self.layout = awt.BorderLayout()

        progB = self.__progressBar = \
            swing.JProgressBar(0, 100, stringPainted=1);

        inf = self.__inputField = swing.JTextField(5)
        inl = swing.JLabel("Calculate value of:", swing.JLabel.RIGHT)
        inl.labelFor = inf

        outf = self.__outputArea = swing.JTextArea()
        outl = swing.JLabel("Result:", swing.JLabel.RIGHT)
        outl.labelFor = outf

        calcb = self.__calcButton = \
            swing.JButton("Calculate", actionPerformed=self.doCalc,
                          enabled=1, mnemonic=awtevent.KeyEvent.VK_C)
        cancelb = self.__cancelButton = \
             swing.JButton("Cancel", actionPerformed=self.doCancel,
                          enabled=0, mnemonic=awtevent.KeyEvent.VK_L)

        vl = ValueLayout(5, 5)
        inp = swing.JPanel(vl)
        vl.setLayoutAlignmentX(inp, 0.2)
        inp.add(inl); inp.add(inf, inl)
        self.add(inp, awt.BorderLayout.NORTH)

        vl = ValueLayout(5, 5)
        outp = swing.JPanel(vl)
        vl.setLayoutAlignmentX(outp, 0.2)
        outp.add(outl); outp.add(swing.JScrollPane(outf), outl)

        xoutp = swing.JPanel(awt.BorderLayout())
        xoutp.add(progB, awt.BorderLayout.NORTH)
        xoutp.add(outp, awt.BorderLayout.CENTER)

        self.add(xoutp, awt.BorderLayout.CENTER)

        sp = swing.JPanel(awt.BorderLayout())

        bp = swing.JPanel()
        bp.add(calcb)
        bp.add(cancelb)
        sp.add(bp, awt.BorderLayout.NORTH)

        sl = self.__statusLabel = swing.JLabel(" ")
        sp.add(sl, awt.BorderLayout.SOUTH)
        self.add(sp, awt.BorderLayout.SOUTH)

## main entry point; launches the GUI in a frame
if __name__ == "__main__":
    print sys.argv[0], "running..."
    frame = swing.JFrame("Factorial Calculator",
                defaultCloseOperation=swing.JFrame.EXIT_ON_CLOSE)
    cp = frame.contentPane
    cp.layout = awt.BorderLayout()
    cp.add( FactorialGui(Factorial()) )
    frame.size = 900, 500
    frame.visible = 1


