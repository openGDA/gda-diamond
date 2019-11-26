package uk.ac.gda.beamline.i21.views;

import java.util.Arrays;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;

import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.dawnsci.plotting.api.IPlottingService;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.dawnsci.plotting.api.PlotType;
import org.eclipse.dawnsci.plotting.api.trace.IImageTrace;
import org.eclipse.dawnsci.plotting.api.trace.ITraceListener;
import org.eclipse.dawnsci.plotting.api.trace.TraceEvent;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetUtils;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.jface.action.ToolBarManager;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.VerifyListener;
import org.eclipse.swt.graphics.Cursor;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.ui.IActionBars;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.processing.operations.rixs.RixsImageReductionBase;
import uk.ac.gda.client.live.stream.view.customui.AbstractLiveStreamViewCustomUi;

public class RixsSpectrumView extends AbstractLiveStreamViewCustomUi {
	private static final Logger logger = LoggerFactory.getLogger(RixsSpectrumView.class);
	private IPlottingSystem<Composite> spectrumPlot;
	private final AtomicReference<IImageTrace> activePaletteTrace = new AtomicReference<>(null);
	private Text energyDispersion;
	private Text slope;
	private Text offset;
	private static final int TEXT_WIDTH = 70;
	private int xSizeHint=100;
	private int ySizeHint=250;
	private final AtomicLong frameCounter = new AtomicLong();
	private FormToolkit toolkit;

	@Override
	public void createUi(Composite composite) {
		toolkit = new FormToolkit(composite.getDisplay());
		
		int boxWidthHint = calculateBoxWidth(composite, TEXT_WIDTH);

		VerifyListener v = buildDoubleVerifyListener();

		// input parameters
		createInputParametersGroup(composite, boxWidthHint, v);
		// spectrum plot
		createSpectrumPlot(composite);

		//listen to the image in main plot
		getPlottingSystem().addTraceListener(new TraceListener());

	}

	private void createSpectrumPlot(Composite comp) {
		Section section = toolkit.createSection(comp, Section.DESCRIPTION | Section.TITLE_BAR);
		section.setLayout(GridLayoutFactory.fillDefaults().create());
		section.setLayoutData(GridDataFactory.fillDefaults().grab(true, true).create());
		section.setExpanded(true);
		section.setEnabled(true);
		section.setVisible(true);
		section.setText("Spectrum Plot");
		section.setDescription("RIXS spectrum from live image stream above");

		Composite sectionClient = toolkit.createComposite(section);
		sectionClient.setLayout(GridLayoutFactory.fillDefaults().create());
		sectionClient.setLayoutData(GridDataFactory.fillDefaults().grab(true, true).create());

		final IPlottingService plottingService = PlatformUI.getWorkbench().getService(IPlottingService.class);
		try {
			spectrumPlot = plottingService.createPlottingSystem();
			//create plot with null action bar to stop this plot's action items being added to this plot's view's toolbar 
			spectrumPlot.createPlotPart(sectionClient, "LiveSpectrum", null, PlotType.XY, null);
			spectrumPlot.setShowLegend(false);
			spectrumPlot.getPlotComposite().setLayoutData(GridDataFactory.fillDefaults().grab(true, true).hint(xSizeHint,ySizeHint).create());
			frameCounter.set(0);
		} catch (Exception e) {
			logger.error("Failed to create a plotting system for spectrum plot", e);
		}

		createSectionToolbar(section);
		
		toolkit.adapt(spectrumPlot.getPlotComposite());
		section.setClient(sectionClient);
	}

	private void createSectionToolbar(Section control) {
		ToolBarManager toolBarManager1 = new ToolBarManager(SWT.FLAT);
		ToolBar toolbar = toolBarManager1.createControl(control);
		final Cursor handCursor = new Cursor(Display.getCurrent(), SWT.CURSOR_HAND);
		toolbar.setCursor(handCursor);
		// Cursor needs to be explicitly disposed
		toolbar.addDisposeListener(new DisposeListener() {
			@Override
			public void widgetDisposed(DisposeEvent e) {
				handCursor.dispose();
			}
		});
		
		// get action bar so we have access to the default tool bar items created during plot creation
		IActionBars actionBars = spectrumPlot.getActionBars();
		IToolBarManager toolBarManager = actionBars.getToolBarManager();
		
		// specify the tool bar items to be kept
		final List<String> toolBarItemIdsToKeep = Arrays.asList(
				"org.csstudio.swt.xygraph.autoscale",
				"org.dawb.common.ui.plot.tool",
				"org.dawnsci.plotting.system.preference.export",
				"org.eclipse.nebula.visualization.xygraph.figures.ZoomType");
		// Remove all ToolBar contributions with Ids which are either undefined or not required
		Arrays.stream(toolBarManager.getItems())
			.filter(ci -> ci.getId() == null || toolBarItemIdsToKeep.stream().noneMatch(ci.getId()::contains))
			.forEach(toolBarManager::remove);
		//add kept items to this scetion's toolar
		Arrays.stream(toolBarManager.getItems()).forEach(e->e.fill(toolbar, -1));
		control.setTextClient(toolbar);
	}
	
	private void plotSpectrum() {
		if (frameCounter.get()==0) {
			spectrumPlot.setRescale(true);
		} 
		Dataset transpose = DatasetUtils.transpose(activePaletteTrace.get().getData(), null);
		double energyDis = Double.parseDouble(energyDispersion.getText());
		double rslope = Double.parseDouble(slope.getText());
		double roffset = Double.parseDouble(offset.getText());
		Dataset[] spectrum = RixsImageReductionBase.makeSpectrum(transpose, 0, rslope, roffset, true);

		//apply energy calibration
		Dataset elastic = RixsImageReductionBase.makeEnergyScale(spectrum, 0, energyDis);
		if (energyDis==1.0) {
			elastic.setName("Pixels");
		} else {
			elastic.setName("Energy loss");
		}
		spectrum[1].setName("Intensity");
		spectrumPlot.updatePlot1D(elastic, Arrays.asList(spectrum[1]), "Live Spectrum - Frame "+frameCounter.incrementAndGet(),new NullProgressMonitor());
		if (spectrumPlot.isRescale()) {
			spectrumPlot.setRescale(false);
		}
		logger.trace(">>>>>>>>>>>> profile updated");
	}

	private void createInputParametersGroup(Composite comp, int boxWidthHint, VerifyListener v) {
		Section section = toolkit.createSection(comp, Section.EXPANDED | Section.TWISTIE | Section.TITLE_BAR | Section.DESCRIPTION);
		section.setText("Live RIXS Spectrum");
		section.setExpanded(true);
		section.setEnabled(true);
		section.setVisible(true);
		section.setLayout(GridLayoutFactory.fillDefaults().create());
		section.setLayoutData(GridDataFactory.fillDefaults().grab(true, false).create());
		section.setDescription("Calibration parameters: ");
		Composite client = toolkit.createComposite(section, SWT.WRAP);
		client.setLayout(GridLayoutFactory.fillDefaults().create());

		Composite inputParameters = toolkit.createComposite(client);
		GridLayoutFactory.swtDefaults().numColumns(6).applyTo(inputParameters);

		final Label createLabel = toolkit.createLabel(inputParameters, "Energy Dispersion");
		GridDataFactory.swtDefaults().applyTo(createLabel);
		energyDispersion = makeTextForDouble(inputParameters, "1.0", boxWidthHint, "Set energy dispersion value", v);
		
		final Label createLabel2 = toolkit.createLabel(inputParameters, "Slope");
		GridDataFactory.swtDefaults().applyTo(createLabel2);
		slope = makeTextForDouble(inputParameters, "0.0", boxWidthHint, "Set slope of reflection line", v);

		final Label createLabel3 = toolkit.createLabel(inputParameters, "Offset");
		GridDataFactory.swtDefaults().applyTo(createLabel3);
		offset = makeTextForDouble(inputParameters, "0.0", boxWidthHint, "Set pixel/energy offset", v);
		
		section.setClient(client);

	}
	
	private Text makeTextForDouble(Composite parent, String defaultValue, int widthHint, String toolTip, VerifyListener v) {
		Text t = toolkit.createText(parent, defaultValue, SWT.BORDER | SWT.RIGHT);
		GridDataFactory.swtDefaults().hint(widthHint, SWT.DEFAULT).applyTo(t);
		t.setToolTipText(toolTip);
		t.addVerifyListener(v);
		return t;
	}
	
	public void setXSizeHint(int xSizeHint) {
		this.xSizeHint = xSizeHint;
	}

	public void setYSizeHint(int ySizeHint) {
		this.ySizeHint = ySizeHint;
	}

	private class TraceListener extends ITraceListener.Stub {

		@Override
		public void traceUpdated(TraceEvent event) {
			if (!(event.getSource() instanceof IImageTrace)) {
				return;
			}

			IImageTrace trace = (IImageTrace) event.getSource();
			activePaletteTrace.set(trace);
			updateSpectrumPlot(trace);
		}

		@Override
		public void traceAdded(TraceEvent event) {
			IImageTrace trace = (IImageTrace) event.getSource();
			activePaletteTrace.set(trace);
			updateSpectrumPlot(trace);
		}

		private void updateSpectrumPlot(final IImageTrace trace) {
			if (trace != null && spectrumPlot != null && !spectrumPlot.isDisposed()) {
				spectrumPlot.clear();
				plotSpectrum();				
			}
		}
	}
	private VerifyListener buildDoubleVerifyListener() {
		return e -> {
			// Validation for keys like Backspace, left arrow key, right arrow key and del keys
			if (e.character == SWT.BS || e.keyCode == SWT.ARROW_LEFT || e.keyCode == SWT.ARROW_RIGHT
					|| e.keyCode == SWT.DEL || e.character == '.') {
				e.doit = true;
				return;
			}

			if (e.character == '\0') {
				e.doit = true;
				return;
			}

			if (e.character == '-') {
				e.doit = true;
				return;
			}
			// for scientific notation
			if (e.character == 'e' || e.character == 'E') {
				e.doit = true;
				return;
			}

			if (!('0' <= e.character && e.character <= '9')) {
				e.doit = false;
				return;
			}
		};
	}	
	private int calculateBoxWidth(Composite parent, int init) {
		GC g = null;

		try {
			g = new GC(parent);
			init = g.getFontMetrics().getAverageCharWidth() * 9;
		} finally {
			if (g != null) {
				g.dispose();
			}

		}
		return init;
	}
}
