#@PydevCodeAnalysisIgnore
'''
Created on 9 Oct 2012

@author: fy65
'''
#!/usr/bin/python
"""
Epics Strip Chart application
"""
import os
import time
from scisoftpy import array, where

import wx
import wx.lib.colourselect as csel

from epics import PV
from epics.wx import EpicsFunction, DelayedEpicsCallback
from epics.wx.utils import SimpleText, Closure, FloatCtrl

from wxmplot.plotpanel import PlotPanel
from wxmplot.colors import hexcolor
from wxmplot.utils import LabelEntry

ICON_FILE = 'stripchart.ico'

FILECHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'

BGCOL = (250, 250, 240)

POLLTIME = 50

STY = wx.GROW|wx.ALL|wx.ALIGN_CENTER_VERTICAL
LSTY = wx.ALIGN_LEFT|wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_VERTICAL
CSTY = wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL


MENU_EXIT = wx.NewId()
MENU_SAVE_IMG = wx.NewId()
MENU_SAVE_DAT = wx.NewId()
MENU_CONFIG = wx.NewId()
MENU_UNZOOM = wx.NewId()
MENU_HELP = wx.NewId()
MENU_ABOUT = wx.NewId()
MENU_PRINT = wx.NewId()
MENU_PSETUP = wx.NewId()
MENU_PREVIEW = wx.NewId()
MENU_CLIPB = wx.NewId()
MENU_SELECT_COLOR = wx.NewId()
MENU_SELECT_SMOOTH = wx.NewId()


def get_bound(val):
    "return float value of input string or None"
    val = val.strip()
    if len(val) == 0 or val is None:
        return None
    try:
        val = float(val)
    except:
        val = None
    return val

class MyChoice(wx.Choice):
    """Simplified wx Choice"""
    def __init__(self, parent, choices=('No', 'Yes'),
                 defaultyes=True, size=(75, -1)):
        wx.Choice.__init__(self, parent, -1, size=size)
        self.choices = choices
        self.Clear()
        self.SetItems(self.choices)
        self.SetSelection({False:0, True:1}[defaultyes])

    def SetChoices(self, choices):
        self.Clear()
        self.SetItems(choices)
        self.choices = choices

    def Select(self, choice):
        if isinstance(choice, int):
            self.SetSelection(choice)
        elif choice in self.choices:
            self.SetSelection(self.choices.index(choice))

class StripChart(wx.Frame):
    default_colors = ((0, 0, 0), (0, 0, 255), (255, 0, 0),
                      (0, 0, 0), (255, 0, 255), (0, 125, 0))

    help_msg = """Quick help:

Left-Click: to display X,Y coordinates
Left-Drag: to zoom in on plot region
Right-Click: display popup menu with choices:
Zoom out 1 level
Zoom all the way out
--------------------
Configure
Save Image

Also, these key bindings can be used
(For Mac OSX, replace 'Ctrl' with 'Apple'):

Ctrl-S: save plot image to file
Ctrl-C: copy plot image to clipboard
Ctrl-K: Configure Plot
Ctrl-Q: quit

"""

    about_msg = """Epics PV Strip Chart version 0.1
Matt Newville <newville@cars.uchicago.edu>
"""

    def __init__(self, parent=None):
        self.pvdata = {}
        self.pvlist = [' -- ']
        self.pvwids = [None]
        self.pvchoices = [None]
        self.colorsels = []
        self.plots_drawn = [False]*10
        self.needs_refresh = False
        self.needs_refresh = False
        self.paused = False

        self.tmin = -60.0
        self.timelabel = 'seconds'

        self.create_frame(parent)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onUpdatePlot, self.timer)
        self.timer.Start(POLLTIME)

    def create_frame(self, parent, size=(750, 450), **kwds):
        self.parent = parent

        kwds['style'] = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL
        kwds['size'] = size
        wx.Frame.__init__(self, parent, -1, 'Epics PV Strip Chart', **kwds)

        self.build_statusbar()

        self.plotpanel = PlotPanel(self, trace_color_callback=self.onTraceColor)
        self.plotpanel.BuildPanel()
        self.plotpanel.messenger = self.write_message

        self.build_pvpanel()
        self.build_btnpanel()
        self.build_menus()
        self.SetBackgroundColour(wx.Colour(*BGCOL))

        mainsizer = wx.BoxSizer(wx.VERTICAL)

        p1 = wx.Panel(self)
        p1.SetBackgroundColour(wx.Colour(*BGCOL))
        s1 = wx.BoxSizer(wx.HORIZONTAL)
        n = LabelEntry(p1, '', labeltext=' Add PV: ',
                       size=300, action=self.onPVname)
        self.pvmsg = SimpleText(p1, ' ', minsize=(75, -1),
                                style=LSTY|wx.EXPAND)
        s1.Add(n.label, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER, 10)
        s1.Add(n, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER, 10)
        s1.Add(self.pvmsg, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER, 10)
        p1.SetAutoLayout(True)
        p1.SetSizer(s1)
        s1.Fit(p1)

        mainsizer.Add(p1, 0, wx.GROW|wx.EXPAND, 5)
        mainsizer.Add(wx.StaticLine(self, size=(250, -1),
                                    style=wx.LI_HORIZONTAL),
                      0, wx.EXPAND|wx.GROW, 8)
        mainsizer.Add(self.pvpanel, 0, wx.EXPAND, 5)
        mainsizer.Add(wx.StaticLine(self, size=(250, -1),
                                    style=wx.LI_HORIZONTAL),
                      0, wx.EXPAND|wx.GROW, 8)
        mainsizer.Add(self.btnpanel, 0, wx.EXPAND, 5)
        mainsizer.Add(self.plotpanel, 1, wx.EXPAND, 5)
        self.SetAutoLayout(True)
        self.SetSizer(mainsizer)
        self.Fit()

        try:
            self.SetIcon(wx.Icon(ICON_FILE, wx.BITMAP_TYPE_ICO))
        except:
            pass

        self.Refresh()


    def build_statusbar(self):
        sbar = self.CreateStatusBar(2, wx.CAPTION|wx.THICK_FRAME)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(10)
        sbar.SetFont(sfont)
        self.SetStatusWidths([-5, -2])
        self.SetStatusText('', 0)

    def build_pvpanel(self):
        panel = self.pvpanel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(*BGCOL))
        sizer = self.pvsizer = wx.GridBagSizer(4, 5)

        name = SimpleText(panel, ' PV: ', minsize=(75, -1), style=LSTY)
        colr = SimpleText(panel, ' Color ', minsize=(50, -1), style=LSTY)
        logs = SimpleText(panel, ' Log Scale?', minsize=(85, -1), style=LSTY)
        ymin = SimpleText(panel, ' Y Minimum ', minsize=(85, -1), style=LSTY)
        ymax = SimpleText(panel, ' Y Maximum ', minsize=(85, -1), style=LSTY)

        sizer.Add(name, (0, 0), (1, 1), LSTY|wx.EXPAND, 2)
        sizer.Add(colr, (0, 1), (1, 1), LSTY, 1)
        sizer.Add(logs, (0, 2), (1, 1), LSTY, 1)
        sizer.Add(ymin, (0, 3), (1, 1), LSTY, 1)
        sizer.Add(ymax, (0, 4), (1, 1), LSTY, 1)

        self.npv_rows = 0
        for i in range(4):
            self.AddPV_row()

        panel.SetAutoLayout(True)
        panel.SetSizer(sizer)
        sizer.Fit(panel)

    def build_btnpanel(self):
        panel = self.btnpanel = wx.Panel(self, )
        panel.SetBackgroundColour(wx.Colour(*BGCOL))

        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.pause_btn = wx.Button(panel, label='Pause', size=(100, 30))
        self.resume_btn = wx.Button(panel, label='Resume', size=(100, 30))
        self.resume_btn.Disable()

        self.pause_btn.Bind(wx.EVT_BUTTON, self.onPause)
        self.resume_btn.Bind(wx.EVT_BUTTON, self.onPause)

        time_label = SimpleText(panel, ' Time Range: ', minsize=(85, -1),
                                style=LSTY)
        self.time_choice = MyChoice(panel, size=(120, -1),
                                    choices=('seconds', 'minutes', 'hours'))
        self.time_choice.SetStringSelection(self.timelabel)
        self.time_choice.Bind(wx.EVT_CHOICE, self.onTimeChoice)

        self.time_ctrl = FloatCtrl(panel, value=-self.tmin, precision=2,
                                    size=(90, -1), action=self.onTimeVal)

        btnsizer.Add(self.pause_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER, 2)
        btnsizer.Add(self.resume_btn, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER, 2)
        btnsizer.Add(time_label, 1, wx.ALIGN_CENTER_HORIZONTAL, 2)
        btnsizer.Add(self.time_ctrl, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER, 2)
        btnsizer.Add(self.time_choice, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER, 2)

        panel.SetAutoLayout(True)
        panel.SetSizer(btnsizer)
        btnsizer.Fit(panel)

    def build_menus(self):
        mbar = wx.MenuBar()

        mfile = wx.Menu()
        mfile.Append(MENU_SAVE_DAT, "&Save Data\tCtrl+S",
                     "Save PNG Image of Plot")
        mfile.Append(MENU_SAVE_IMG, "Save Plot Image\t",
                     "Save PNG Image of Plot")
        mfile.Append(MENU_CLIPB, "&Copy Image to Clipboard\tCtrl+C",
                     "Copy Plot Image to Clipboard")
        mfile.AppendSeparator()
        mfile.Append(MENU_PSETUP, 'Page Setup...', 'Printer Setup')
        mfile.Append(MENU_PREVIEW, 'Print Preview...', 'Print Preview')
        mfile.Append(MENU_PRINT, "&Print\tCtrl+P", "Print Plot")
        mfile.AppendSeparator()
        mfile.Append(MENU_EXIT, "E&xit\tCtrl+Q", "Exit the 2D Plot Window")

        mopt = wx.Menu()
        mopt.Append(MENU_CONFIG, "Configure Plot\tCtrl+K",
                 "Configure Plot styles, colors, labels, etc")
        mopt.AppendSeparator()
        mopt.Append(MENU_UNZOOM, "Zoom Out\tCtrl+Z",
                 "Zoom out to full data range")

        mhelp = wx.Menu()
        mhelp.Append(MENU_HELP, "Quick Reference", "Quick Reference for MPlot")
        mhelp.Append(MENU_ABOUT, "About", "About MPlot")

        mbar.Append(mfile, "File")
        mbar.Append(mopt, "Options")
        mbar.Append(mhelp, "&Help")

        self.SetMenuBar(mbar)
        self.Bind(wx.EVT_MENU, self.onSaveData, id=MENU_SAVE_DAT)
        self.Bind(wx.EVT_MENU, self.onHelp, id=MENU_HELP)
        self.Bind(wx.EVT_MENU, self.onAbout, id=MENU_ABOUT)
        self.Bind(wx.EVT_MENU, self.onExit, id=MENU_EXIT)
        self.Bind(wx.EVT_CLOSE, self.onExit)

        pp = self.plotpanel
        self.Bind(wx.EVT_MENU, pp.configure, id=MENU_CONFIG)
        self.Bind(wx.EVT_MENU, pp.unzoom_all, id=MENU_UNZOOM)
        self.Bind(wx.EVT_MENU, pp.save_figure, id=MENU_SAVE_IMG)
        self.Bind(wx.EVT_MENU, pp.Print, id=MENU_PRINT)
        self.Bind(wx.EVT_MENU, pp.PrintSetup, id=MENU_PSETUP)
        self.Bind(wx.EVT_MENU, pp.PrintPreview, id=MENU_PREVIEW)
        self.Bind(wx.EVT_MENU, pp.canvas.Copy_to_Clipboard, id=MENU_CLIPB)

    def AddPV_row(self):
        i = self.npv_rows = self.npv_rows + 1

        panel = self.pvpanel
        sizer = self.pvsizer
        pvchoice = MyChoice(panel, choices=self.pvlist, size=(200, -1))
        pvchoice.SetSelection(0)
        logs = MyChoice(panel)
        logs.SetSelection(0)
        ymin = wx.TextCtrl(panel, -1, '', size=(75, -1))
        ymax = wx.TextCtrl(panel, -1, '', size=(75, -1))
        if i > 2:
            logs.Disable()
            ymin.Disable()
            ymax.Disable()

        colval = (0, 0, 0)
        if i < len(self.default_colors):
            colval = self.default_colors[i]
        colr = csel.ColourSelect(panel, -1, '', colval)
        self.colorsels.append(colr)

        sizer.Add(pvchoice, (i, 0), (1, 1), LSTY, 3)
        sizer.Add(colr, (i, 1), (1, 1), CSTY, 3)
        sizer.Add(logs, (i, 2), (1, 1), CSTY, 3)
        sizer.Add(ymin, (i, 3), (1, 1), CSTY, 3)
        sizer.Add(ymax, (i, 4), (1, 1), CSTY, 3)

        pvchoice.Bind(wx.EVT_CHOICE, Closure(self.onPVchoice, row=i))
        colr.Bind(csel.EVT_COLOURSELECT, Closure(self.onPVcolor, row=i))
        logs.Bind(wx.EVT_CHOICE, self.onPVwid)
        ymin.Bind(wx.EVT_TEXT_ENTER, self.onPVwid)
        ymax.Bind(wx.EVT_TEXT_ENTER, self.onPVwid)

        self.pvchoices.append(pvchoice)
        self.pvwids.append((logs, colr, ymin, ymax))

    def onTraceColor(self, trace, color, **kws):
        irow = self.get_current_traces()[trace][0] - 1
        self.colorsels[irow].SetColour(color)

    def onPVshow(self, event=None, row=0):
        if not event.IsChecked():
            trace = self.plotpanel.conf.get_mpl_line(row)
            trace.set_data([], [])
            self.plotpanel.canvas.draw()
        self.needs_refresh = True

    def onPVname(self, event=None):
        try:
            name = event.GetString()
        except AttributeError:
            return
        self.addPV(name)

    @EpicsFunction
    def addPV(self, name):
        if name is not None and name not in self.pvlist:
            pv = PV(str(name), callback=self.onPVChange)
            pv.get()
            conn = False
            if pv is not None:
                if not pv.connected:
                    pv.wait_for_connection()
                conn = pv.connected

            msg = 'PV not found: %s' % name
            if conn:
                msg = 'PV found: %s' % name
            self.pvmsg.SetLabel(msg)
            if not conn:
                return
            self.pvlist.append(name)
            self.pvdata[name] = [(time.time(), pv.get())]

            i_new = len(self.pvdata)
            new_shown = False
            for choice in self.pvchoices:
                if choice is None:
                    continue
                cur = choice.GetSelection()
                choice.Clear()
                choice.SetItems(self.pvlist)
                choice.SetSelection(cur)
                if cur == 0 and not new_shown:
                    choice.SetSelection(i_new)
                    new_shown = True
            self.needs_refresh = True

    @DelayedEpicsCallback
    def onPVChange(self, pvname=None, value=None, timestamp=None, **kw):
        if timestamp is None:
            timestamp = time.time()
        self.pvdata[pvname].append((timestamp, value))
        self.needs_refresh = True

    def onPVchoice(self, event=None, row=None, **kws):
        self.needs_refresh = True
        for i in range(len(self.pvlist)+1):
            try:
                trace = self.plotpanel.conf.get_mpl_line(row-1)
                trace.set_data([], [])
            except:
                pass
        if row == 1:
            self.plotpanel.set_y2label('')
        self.plotpanel.canvas.draw()

    def onPVcolor(self, event=None, row=None, **kws):
        self.plotpanel.conf.set_trace_color(hexcolor(event.GetValue()),
                                            trace=row-1)
        self.needs_refresh = True

    def onPVwid(self, event=None, row=None, **kws):
        self.needs_refresh = True

    def onTimeVal(self, event=None, value=None, **kws):
        new = -abs(value)
        if abs(new) < 0.1:
            new = -0.1
        if abs(new - self.tmin) > 1.e-3*max(new, self.tmin):
            self.tmin = new
            self.needs_refresh = True

    def onTimeChoice(self, event=None, **kws):
        newval = event.GetString()
        denom, num = 1.0, 1.0
        if self.timelabel != newval:
            if self.timelabel == 'hours':
                denom = 3600.
            elif self.timelabel == 'minutes':
                denom = 60.0
            if newval == 'hours':
                num = 3600.
            elif newval == 'minutes':
                num = 60.0

            self.timelabel = newval
            timeval = self.time_ctrl.GetValue()
            self.time_ctrl.SetValue(timeval * denom/num)
            self.plotpanel.set_xlabel('Elapsed Time (%s)' % self.timelabel)
        self.needs_refresh = True

    def onPause(self, event=None):
        if self.paused:
            self.pause_btn.Enable()
            self.resume_btn.Disable()
        else:
            self.pause_btn.Disable()
            self.resume_btn.Enable()
        self.paused = not self.paused

    def write_message(self, s, panel=0):
        """write a message to the Status Bar"""
        self.SetStatusText(s, panel)

    def onSaveData(self, event=None):
        dlg = wx.FileDialog(self, message='Save Data to File...',
                            defaultDir = os.getcwd(),
                            defaultFile='PVStripChart.dat',
                            style=wx.SAVE|wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.SaveDataFiles(path)
            self.write_message('Saved data to %s' % path)
        dlg.Destroy()

    def SaveDataFiles(self, path):
        basename, ext = os.path.splitext(path)
        if len(ext) < 2:
            ext = '.dat'
        if ext.startswith('.'):
            ext = ext[1:]

        for pvname, data in self.pvdata.items():
            tnow = time.time()
            tmin = data[0][0]
            fname = []
            for s in pvname:
                if s not in FILECHARS:
                    s = '_'
                fname.append(s)
            fname = os.path.join("%s_%s.%s" % (basename, ''.join(fname), ext))

            buff = ["# Epics PV Strip Chart Data for PV: %s " % pvname]
            buff.append("# Current Time = %s " % time.ctime(tnow))
            buff.append("# Earliest Time = %s " % time.ctime(tmin))
            buff.append("#------------------------------")
            buff.append("# Timestamp Value Time-Current_Time(s)")
            for tx, yval in data:
                buff.append(" %.3f %16g %.3f" % (tx, yval, tx-tnow))

            fout = open(fname, 'w')
            fout.write("\n".join(buff))
            fout.close()
            #dat = tnow, func(tnow)

    def onAbout(self, event=None):
        dlg = wx.MessageDialog(self, self.about_msg,
                               "About Epics PV Strip Chart",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def onHelp(self, event=None):
        dlg = wx.MessageDialog(self, self.help_msg, "Epics PV Strip Chart Help",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def onExit(self, event=None):
        try:
            self.plotpanel.win_config.Close(True)
            self.plotpanel.win_config.Destroy()
        except:
            pass

        self.Destroy()

    def get_current_traces(self):
        "return list of current traces"
        traces = [] # to be shown
        for irow, s in enumerate(self.pvchoices):
            if s is not None:
                ix = s.GetSelection()
                if ix > 0:
                    name = self.pvlist[ix]
                    logs = 1 == self.pvwids[irow][0].GetSelection()
                    color = self.pvwids[irow][1].GetColour()
                    ymin = get_bound(self.pvwids[irow][2].GetValue())
                    ymax = get_bound(self.pvwids[irow][3].GetValue())
                    traces.append((irow, name, logs, color, ymin, ymax))
        return traces

    def onUpdatePlot(self, event=None):
        if self.paused or not self.needs_refresh:
            return

        tnow = time.time()
        # set timescale sec/min/hour
        timescale = 1.0
        if self.time_choice.GetSelection() == 1:
            timescale = 1./60
        elif self.time_choice.GetSelection() == 2:
            timescale = 1./3600

        ylabelset, y2labelset = False, False
        xlabel = 'Elapsed Time (%s)' % self.timelabel
        itrace = -1
        update_failed = False
        hasplot = False
        span1 = (1, 0)
        did_update = False
        left_axes = self.plotpanel.axes
        right_axes = self.plotpanel.get_right_axes()

        for irow, pname, uselog, color, ymin, ymax in self.get_current_traces():
            if pname not in self.pvdata:
                continue
            itrace += 1
            if len(self.plots_drawn) < itrace:
                self.plots_drawn.extend([False]*3)
            side = 'left'
            if itrace == 1:
                side = 'right'
            data = self.pvdata[pname][:]
            if len(data) < 2:
                update_failed = True
                continue
            tdat = timescale * (array([i[0] for i in data]) - tnow)
            mask = where(tdat > self.tmin)
            if (len(mask[0]) < 2 or
                ((abs(min(tdat)) / abs(1 -self.tmin)) > 0.1)):
                data.append((time.time(), data[0][-1]))
                tdat = timescale*(array([i[0] for i in data]) - tnow)
                mask = where(tdat > self.tmin)

            i0 = mask[0][0]
            if i0 > 0:
                i0 = i0-1
            i1 = mask[0][-1] + 1
            tdat = timescale*(array([i[0] for i in data[i0:i1]]) - tnow)
            ydat = array([i[1] for i in data[i0:i1]])

            if len(ydat) < 2:
                update_failed = True
                continue
            if ymin is None:
                ymin = min(ydat)
            if ymax is None:
                ymax = max(ydat)

            # for more that 2 plots, scale to left hand axis
            if itrace == 0:
                span1 = (ymax-ymin, ymin)
                if span1[0]*ymax < 1.e-6:
                    update_failed = True
                    continue
            elif itrace > 1:
                yr = abs(ymax-ymin)
                if yr > 1.e-9:
                    ydat = span1[1] + 0.99*(ydat - ymin)*span1[0]/yr
                ymin, ymax = min(ydat), max(ydat)
            
            if self.needs_refresh:
                if itrace == 0:
                    self.plotpanel.set_ylabel(pname)
                elif itrace == 1:
                    self.plotpanel.set_y2label(pname)
                if not self.plots_drawn[itrace]:
                    plot = self.plotpanel.oplot
                    if itrace == 0:
                        plot = self.plotpanel.plot
                    try:
                        plot(tdat, ydat,
                             drawstyle='steps-post', side=side,
                             ylog_scale=uselog, color=color,
                             xmin=self.tmin, xmax=0,
                             xlabel=xlabel, label=pname, autoscale=False)
                        self.plots_drawn[itrace] = True
                    except:
                        update_failed = True
                else:
                    try:
                        self.plotpanel.update_line(itrace, tdat, ydat, draw=False)
                        self.plotpanel.set_xylims((self.tmin, 0, ymin, ymax),
                                                  side=side, autoscale=False)
                        did_update = True
                    except:
                        update_failed = True
                axes = left_axes
                if itrace == 1:
                    axes = right_axes
                if uselog and min(ydat) > 0:
                    axes.set_yscale('log', basey=10)
                else:
                    axes.set_yscale('linear')
                    
                    
        self.plotpanel.set_title(time.strftime("%Y-%b-%d %H:%M:%S", time.localtime()))
        if did_update:
            self.plotpanel.canvas.draw()
        self.needs_refresh = update_failed
        return

if __name__ == '__main__':
    app = wx.PySimpleApp()
    f = StripChart()
    f.Show(True)
    app.MainLoop()