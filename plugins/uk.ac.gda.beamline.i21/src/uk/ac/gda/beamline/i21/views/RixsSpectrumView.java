package uk.ac.gda.beamline.i21.views;

import static org.eclipse.ui.forms.widgets.ExpandableComposite.EXPANDED;
import static org.eclipse.ui.forms.widgets.ExpandableComposite.TITLE_BAR;
import static org.eclipse.ui.forms.widgets.ExpandableComposite.TWISTIE;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;

import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.dawnsci.analysis.dataset.roi.ROISliceUtils;
import org.eclipse.dawnsci.analysis.dataset.roi.RectangularROI;
import org.eclipse.dawnsci.plotting.api.IPlottingService;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.dawnsci.plotting.api.PlotType;
import org.eclipse.dawnsci.plotting.api.region.IRegion;
import org.eclipse.dawnsci.plotting.api.region.IRegionListener;
import org.eclipse.dawnsci.plotting.api.region.RegionEvent;
import org.eclipse.dawnsci.plotting.api.trace.IImageTrace;
import org.eclipse.dawnsci.plotting.api.trace.ITraceListener;
import org.eclipse.dawnsci.plotting.api.trace.TraceEvent;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetUtils;
import org.eclipse.january.dataset.Slice;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.ActionContributionItem;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.action.IMenuCreator;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.jface.action.ToolBarManager;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.VerifyListener;
import org.eclipse.swt.graphics.Cursor;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.Text;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.ui.IActionBars;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.processing.operations.rixs.RixsImageReductionBase;
import uk.ac.gda.beamline.i21.I21BeamlineActivator;
import uk.ac.gda.client.live.stream.view.LivePlottingComposite;
import uk.ac.gda.client.live.stream.view.customui.AbstractLiveStreamViewCustomUi;

public class RixsSpectrumView extends AbstractLiveStreamViewCustomUi {

	private static final Logger logger = LoggerFactory.getLogger(RixsSpectrumView.class);
	private static final String ID = "uk.ac.gda.beamline.i21.views.spectrum.plot";
	private IPlottingSystem<Composite> spectrumPlot;
	private final AtomicReference<IImageTrace> activePaletteTrace = new AtomicReference<>(null);
	private Text energyResolution;
	private Text slope;
	private Text offset;
	private static final int TEXT_WIDTH = 70;
	private int xSizeHint = 100;
	private int ySizeHint = 250;
	private final AtomicLong frameCounter = new AtomicLong();
	private FormToolkit toolkit;
	private IToolBarManager toolBarManager;
	private IRegion selectedRegion;
	private DropdownMenuAction dropdownMenu;
	private TraceListener traceListener;
	private RegionListener regionListener;

	@Override
	public void createUi(Composite composite) {
		toolkit = new FormToolkit(composite.getDisplay());

		int boxWidthHint = calculateBoxWidth(composite, TEXT_WIDTH);

		VerifyListener v = buildDoubleVerifyListener();

		createLiveSpectrumPlot(composite, boxWidthHint, v);
		
		// initialize the trace reference to prevent NPE at client when region is added before camera is updating
		activePaletteTrace.set((IImageTrace)getPlottingSystem().getTrace(LivePlottingComposite.LIVE_CAMERA_STREAM));
		// add trace listener to capture image for data reduction spectrum plot
		traceListener = new TraceListener();
		getPlottingSystem().addTraceListener(traceListener);
		// add Region listener to update ROI selection drop down menu in spectrum plot
		regionListener = new RegionListener();
		getPlottingSystem().addRegionListener(regionListener);
	}
	
	@Override
	public void dispose() {
		super.dispose();
		if(regionListener != null) getPlottingSystem().removeRegionListener(regionListener);
		if (traceListener != null) getPlottingSystem().removeTraceListener(traceListener);
		dropdownMenu.dispose();
	}
	
	private void createLiveSpectrumPlot(Composite composite, int boxWidthHint, VerifyListener v) {
		Section section = toolkit.createSection(composite, EXPANDED | TWISTIE | TITLE_BAR);
		section.setText("Live RIXS Spectrum");
		section.setExpanded(true);
		section.setEnabled(true);
		section.setVisible(true);
		section.setLayout(GridLayoutFactory.fillDefaults().create());
		section.setLayoutData(GridDataFactory.fillDefaults().grab(true, false).create());
		Composite client = toolkit.createComposite(section, SWT.WRAP);
		client.setLayout(GridLayoutFactory.fillDefaults().create());

		Composite inputParameters = toolkit.createComposite(client);
		GridLayoutFactory.swtDefaults().numColumns(6).applyTo(inputParameters);

		final Label createLabel = toolkit.createLabel(inputParameters, "Energy Dispersion");
		GridDataFactory.swtDefaults().applyTo(createLabel);
		energyResolution = makeTextForDouble(inputParameters, "1.0", boxWidthHint, "Set energy resolution (eV/pix)", v);

		final Label createLabel2 = toolkit.createLabel(inputParameters, "Slope");
		GridDataFactory.swtDefaults().applyTo(createLabel2);
		slope = makeTextForDouble(inputParameters, "0.0", boxWidthHint, "Set slope of reflection line", v);

		final Label createLabel3 = toolkit.createLabel(inputParameters, "Offset");
		GridDataFactory.swtDefaults().applyTo(createLabel3);
		offset = makeTextForDouble(inputParameters, "0.0", boxWidthHint, "Set pixel/energy offset", v);

		final IPlottingService plottingService = PlatformUI.getWorkbench().getService(IPlottingService.class);
		try {
			spectrumPlot = plottingService.createPlottingSystem();
			// create plot with null action bar to stop this plot's action items being added to this plot's view's toolbar
			spectrumPlot.createPlotPart(client, "LiveSpectrum", null, PlotType.XY, null);
			spectrumPlot.setShowLegend(false);
			spectrumPlot.autoscaleAxes();
			spectrumPlot.getPlotComposite().setLayoutData(GridDataFactory.fillDefaults().grab(true, true).hint(xSizeHint, ySizeHint).create());
			frameCounter.set(0);
		} catch (Exception e) {
			logger.error("Failed to create a plotting system for spectrum plot", e);
		}
		// add tool for spectrum plot local to the section
		createSectionToolbar(section);
		// enforce toolkit colour scheme
		toolkit.adapt(spectrumPlot.getPlotComposite());
		section.setClient(client);
	}

	private void createSectionToolbar(Section control) {
		ToolBarManager toolBarManager1 = new ToolBarManager(SWT.FLAT);
		ToolBar toolbar = toolBarManager1.createControl(control);
		final Cursor handCursor = new Cursor(Display.getCurrent(), SWT.CURSOR_HAND);
		toolbar.setCursor(handCursor);
		// Cursor needs to be explicitly disposed
		toolbar.addDisposeListener(e -> handCursor.dispose());

		// get action bar so we have access to the default tool bar items created during plot creation
		IActionBars actionBars = spectrumPlot.getActionBars();
		toolBarManager = actionBars.getToolBarManager();

		// specify the tool bar items to be kept
		final List<String> toolBarItemIdsToKeep = Arrays.asList("org.csstudio.swt.xygraph.autoscale", "org.dawb.common.ui.plot.tool",
				"org.dawnsci.plotting.system.preference.export", "org.eclipse.nebula.visualization.xygraph.figures.ZoomType");
		// Remove all ToolBar contributions with Ids which are either undefined or not required
		Arrays.stream(toolBarManager.getItems()).filter(ci -> ci.getId() == null || toolBarItemIdsToKeep.stream().noneMatch(ci.getId()::contains))
				.forEach(toolBarManager::remove);

		Action replotAndRescale = new Action("Re-plot the Spectrum", IAction.AS_PUSH_BUTTON) {
			@Override
			public void run() {
				spectrumPlot.clear();
				updateSpectrum(activePaletteTrace, true, selectedRegion);
			}
		};
		replotAndRescale.setImageDescriptor(I21BeamlineActivator.getImageDescriptor("icons/arrow-repeat-once.png"));
		toolBarManager.add(replotAndRescale);

		// menu to change ROI to be plotted in this spectrum
		createDropdownMenuForROIs();
		// add kept items to this section's tool bar
		Arrays.stream(toolBarManager.getItems()).forEach(e -> e.fill(toolbar, -1));
		control.setTextClient(toolbar);
	}

	private void createDropdownMenuForROIs() {
		Collection<IRegion> regions = getPlottingSystem().getRegions();
		List<IRegion> items = regions.stream().filter(e -> e.getROI() instanceof RectangularROI).collect(Collectors.toList());
		items.add(null); // represent whole image is used
		dropdownMenu = new DropdownMenuAction(items, ID, "ROIs");
		dropdownMenu.setToolTipText("Select a Region to plot");
		toolBarManager.add(dropdownMenu);
	}

	private void updateSpectrum(AtomicReference<IImageTrace> activePaletteTrace, boolean rescale, IRegion region) {
		spectrumPlot.setRescale(rescale);
		Dataset transpose = DatasetUtils.transpose(activePaletteTrace.get().getData());
		double energyRes = Double.parseDouble(energyResolution.getText());
		double rslope = Double.parseDouble(slope.getText());
		double[] rOrigin = {0, Double.parseDouble(offset.getText())};
		if (region != null && region.getROI() instanceof RectangularROI rroi) {
			// spectrum within ROI
			Slice[] slicesFromRectangularROI = ROISliceUtils.getSlicesFromRectangularROI(rroi, 1);
			rOrigin[0] = rroi.getIntPoint()[0]; // override X
			transpose = transpose.getSliceView(slicesFromRectangularROI);
		}
		Dataset[] spectrum = RixsImageReductionBase.makeSpectrum(transpose, rOrigin, rslope, true, true);
		// apply energy calibration
		Dataset xValues = RixsImageReductionBase.makeEnergyScale(spectrum, 0, rOrigin[1], energyRes);
		if (energyRes == 1.0) {
			xValues.setName("Pixels");
		} else {
			xValues.setName("Energy loss");
		}
		spectrum[1].setName("Intensity");
		spectrumPlot.updatePlot1D(xValues, Arrays.asList(spectrum[1]), "", new NullProgressMonitor());
		if (spectrumPlot.isRescale()) {
			spectrumPlot.setRescale(false);
		}
		logger.trace(">>>>>>>>>>>> profile updated");
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
				boolean rescale = frameCounter.getAndIncrement() == 0;
				updateSpectrum(activePaletteTrace, rescale, selectedRegion);
			}
		}
	}

	private VerifyListener buildDoubleVerifyListener() {
		return e -> {
			// Validation for keys like Backspace, left arrow key, right arrow key and del keys
			if (e.character == SWT.BS || e.keyCode == SWT.ARROW_LEFT || e.keyCode == SWT.ARROW_RIGHT || e.keyCode == SWT.DEL || e.character == '.') {
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
			init = (int) (g.getFontMetrics().getAverageCharacterWidth() * 9);
		} finally {
			if (g != null) {
				g.dispose();
			}
		}
		return init;
	}

	/**
	 * updates spectrum plot and ROI drop down menu in response to {@link RegionEvent}
	 * @author fy65
	 *
	 */
	private class RegionListener extends IRegionListener.Stub {

		@Override
		public void regionCreated(RegionEvent evt) {
			// do nothing, otherwise selectedRegion will be set to null temporarily
			// until region is added to the live stream plot.
		}

		@Override
		public void regionAdded(RegionEvent evt) {
			super.regionAdded(evt);
			selectedRegion = evt.getRegion();
			//plot the added region spectrum
			spectrumPlot.clear();
			updateSpectrum(activePaletteTrace, true, selectedRegion);
		}

		@Override
		public void regionRemoved(RegionEvent evt) {
			super.regionRemoved(evt);
			if (selectedRegion == evt.getRegion()) {
				// the plotted region being removed, plot the whole image spectrum
				selectedRegion = null;
				spectrumPlot.clear();
				updateSpectrum(activePaletteTrace, true, selectedRegion);
			}
		}

		@Override
		public void regionsRemoved(RegionEvent evt) {
			super.regionsRemoved(evt);
			// all regions are remove, plot the whole image spectrum
			selectedRegion = null;
			spectrumPlot.clear();
			updateSpectrum(activePaletteTrace, true, selectedRegion);
		}

		@Override
		protected void update(RegionEvent evt) {
			// update ROI drop down menu items
			Collection<IRegion> regions = getPlottingSystem().getRegions();
			regions.add(null); // represent the whole image - no ROI
			dropdownMenu.createActions(regions);
		}
	}
	
	/**
	 * plot the region's spectrum on selecting drop down menu item. 
	 * @author fy65
	 *
	 */
	private class ROIAction extends Action {

		private final IRegion region;

		public ROIAction(IRegion region) {
			super(region == null ? "Whole Image" : region.getName(), IAction.AS_PUSH_BUTTON);
			this.region = region;
		}

		@Override
		public void run() {
			selectedRegion = this.region;
			// plot the selected region's spectrum
			spectrumPlot.clear();
			updateSpectrum(activePaletteTrace, true, selectedRegion);
		}
	}

	/**
	 * A drop down menu for select region of  interest. 
	 * The items in this drop down menu can be updated dynamically by calling {@link DropdownMenuAction#createActions(Collection)}
	 * 
	 * @author fy65
	 *
	 */
	private class DropdownMenuAction extends Action implements IMenuCreator {

		private Menu fMenu;
		private List<Action> actions;

		public DropdownMenuAction(List<IRegion> items, String id, String name) {
			super(name, IAction.AS_DROP_DOWN_MENU);
			setId(id);
			setImageDescriptor(I21BeamlineActivator.getImageDescriptor("icons/plot-tool-region-edit.png"));
			setMenuCreator(this);
			actions = new ArrayList<>();
			createActions(items);
		}

		@Override
		public void dispose() {
			if (fMenu != null && !fMenu.isDisposed()) {
				fMenu.dispose();
			}
		}

		@Override
		public Menu getMenu(Control parent) {
			if (fMenu != null && !fMenu.isDisposed()) {
				fMenu.dispose();
			}
			fMenu = new Menu(parent);
			actions.stream().map(ActionContributionItem::new).forEach(this::fillMenu);
			return fMenu;
		}

		private void fillMenu(ActionContributionItem e) {
			e.fill(fMenu, -1);
		}

		@Override
		public Menu getMenu(Menu parent) {
			return null;
		}

		public void createActions(Collection<IRegion> regions) {
			actions.clear();
			regions.stream().map(ROIAction::new).forEach(actions::add);
		}
	}
}
