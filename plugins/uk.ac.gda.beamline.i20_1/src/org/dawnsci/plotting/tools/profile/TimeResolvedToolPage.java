/*-
 * Copyright © 2014 Diamond Light Source Ltd.
 *
 * This file is part of GDA.
 *
 * GDA is free software: you can redistribute it and/or modify it under the
 * terms of the GNU General Public License version 3 as published by the Free
 * Software Foundation.
 *
 * GDA is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
 * details.
 *
 * You should have received a copy of the GNU General Public License along
 * with GDA. If not, see <http://www.gnu.org/licenses/>.
 */

package org.dawnsci.plotting.tools.profile;

import gda.scan.ede.datawriters.TimeResolvedDataFileHelper;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.File;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.dawb.common.ui.widgets.ActionBarWrapper;
import org.dawnsci.plotting.tools.profile.model.SpectraRegionDataNode;
import org.dawnsci.plotting.tools.profile.model.SpectrumDataNode;
import org.dawnsci.plotting.tools.profile.model.TimeEnergyShiftingModel;
import org.dawnsci.plotting.tools.profile.model.TimeResolvedDataNode;
import org.dawnsci.plotting.tools.profile.model.ToolPageModel;
import org.eclipse.core.databinding.observable.list.IListChangeListener;
import org.eclipse.core.databinding.observable.list.ListChangeEvent;
import org.eclipse.core.databinding.observable.list.ListDiffVisitor;
import org.eclipse.dawnsci.analysis.dataset.roi.RectangularROI;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.dawnsci.plotting.api.PlotType;
import org.eclipse.dawnsci.plotting.api.PlottingFactory;
import org.eclipse.dawnsci.plotting.api.histogram.ImageServiceBean.HistoType;
import org.eclipse.dawnsci.plotting.api.region.IRegion;
import org.eclipse.dawnsci.plotting.api.region.IRegion.RegionType;
import org.eclipse.dawnsci.plotting.api.region.IRegionListener;
import org.eclipse.dawnsci.plotting.api.region.RegionEvent;
import org.eclipse.dawnsci.plotting.api.region.RegionUtils;
import org.eclipse.dawnsci.plotting.api.tool.AbstractToolPage;
import org.eclipse.dawnsci.plotting.api.tool.IToolPageSystem;
import org.eclipse.dawnsci.plotting.api.trace.IImageTrace;
import org.eclipse.dawnsci.plotting.api.trace.ILineTrace;
import org.eclipse.dawnsci.plotting.api.trace.ITrace;
import org.eclipse.dawnsci.plotting.api.trace.ITraceListener;
import org.eclipse.dawnsci.plotting.api.trace.TraceEvent;
import org.eclipse.dawnsci.plotting.api.trace.TraceWillPlotEvent;
import org.eclipse.january.dataset.DoubleDataset;
import org.eclipse.january.dataset.IDataset;
import org.eclipse.january.metadata.IMetadata;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.IEditorInput;
import org.eclipse.ui.part.EditorPart;
import org.eclipse.ui.part.FileEditorInput;

import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.calibration.data.CalibrationDetails;

import com.swtdesigner.ResourceManager;

public class TimeResolvedToolPage extends AbstractToolPage implements IRegionListener, ITraceListener {

	private final Image energyTimeViewIcon = ResourceManager.getImageDescriptor(TimeResolvedToolPage.class, "/icons/layout-header-2-equal.png").createImage();

	private SashForm rootComposite;
	private SashForm plotsParentComposite;
	private SpectraTableComposite spectraTableComposite;
	private SpectraRegionComposite spectraRegionTableComposite;

	private IPlottingSystem<Composite> plottingSystem;
	private IImageTrace imageTrace;
	private File dataFile;
	private String cycleIndex;
	private IDataset energy;

	// TODO Review the page lifecycle
	private boolean spectraDataLoaded = false;
	private final ToolPageModel toolPageModel = new ToolPageModel();
	private final TimeEnergyShiftingModel timeEnergyShifting = new TimeEnergyShiftingModel(toolPageModel);
	private Label statusLabel;
	private final List<IRegion> cachedPlottedRegions = new ArrayList<IRegion>();
	private TimeResolvedDataNode timeResolvedData;

	private IRegion engerySelectionLine;

	@Override
	public void activate() {
		getPlottingSystem().addRegionListener(this);
		getPlottingSystem().addTraceListener(this);
		super.activate();
	}

	// TODO Validate data and manage UI if not correct dataset
	private void validateAndLoadSpectra(IImageTrace image) {
		imageTrace = image;
		imageTrace.setHistoType(HistoType.OUTLIER_VALUES);
		try {
			String fullFilePath = getDataFilePath(image);
			dataFile = new File(fullFilePath);
			TimeResolvedDataFileHelper timeResolvedNexusFileHelper = new TimeResolvedDataFileHelper(fullFilePath);
			if (!timeResolvedNexusFileHelper.isTimeResolvedDataFile()) {
				return;
			}
			checkAndFillCyclicInfo(timeResolvedNexusFileHelper);
			timeResolvedData = new TimeResolvedDataNode();
			timeResolvedData.setData(timeResolvedNexusFileHelper.getItMetadata());
			energy = timeResolvedNexusFileHelper.getEnergy();
			toolPageModel.setEnergy(energy);
			toolPageModel.setTimeResolvedData(timeResolvedData);
			toolPageModel.setDataFile(dataFile);
			toolPageModel.setDataImagePlotting(getPlottingSystem());
			toolPageModel.setImageTrace(imageTrace);
			// repopulateCachedSpectraRegion();
			spectraDataLoaded = true;
			CalibrationDetails calibrationDetails = timeResolvedNexusFileHelper.getItMetadata().getCalibrationDetails();
			if (statusLabel !=null) {
				if (calibrationDetails != null) {
					statusLabel.setText("Energy calibrated with " + calibrationDetails.getReferenceDataFileName());
				} else {
					statusLabel.setText("");
				}
			}
		} catch (Exception e) {
			logger.error("Unable to find group data, not a valid dataset", e);
			UIHelper.showError("Unable to find group data, not a valid dataset", e.getMessage());
		}
	}

	private void repopulateCachedSpectraRegion() {
		spectraRegionTableComposite.populateSpectraRegion(cachedPlottedRegions);
		cachedPlottedRegions.clear();
	}



	private void checkAndFillCyclicInfo(TimeResolvedDataFileHelper timeResolvedNexusFileHelper) throws Exception {
		toolPageModel.setCyclesInfo(timeResolvedNexusFileHelper.getCyclesInfo());
		cycleIndex = "";
		if (toolPageModel.getCyclesInfo().length > 0) {
			Matcher matcher = Pattern.compile("Slice of.*=\\s*(\\d+)\\)").matcher(this.getPlottingSystem().getTitle());
			if (matcher.find()) {
				cycleIndex = matcher.group(1);
			}
		}
	}

	private String getDataFilePath(IImageTrace image) throws Exception {
		IMetadata metaData = image.getData().getFirstMetadata(IMetadata.class);
		if (metaData != null) {
			return metaData.getFilePath();
		}
		if (getPlottingSystem().getPart() instanceof EditorPart) {
			IEditorInput editorInput = ((EditorPart) getPlottingSystem().getPart()).getEditorInput();
			if (editorInput instanceof FileEditorInput) {
				return ((FileEditorInput) editorInput).getURI().getPath();
			}
		}
		throw new Exception("Unable to determine the data file");
	}

	private void clearData() {
		for (Object plottedRegion : spectraRegionTableComposite.getCheckedRegionSpectraList()) {
			cachedPlottedRegions.add(((SpectraRegionDataNode) plottedRegion).getRegion());
		}
		spectraDataLoaded = false;
		spectraTableComposite.clearSelectedSpectraList();
		spectraRegionTableComposite.clearRegionData();
		timeResolvedData.clearData();
	}

	@Override
	public void deactivate() {
		if (getPlottingSystem() != null) {
			getPlottingSystem().removeRegionListener(this);
			getPlottingSystem().removeTraceListener(this);
		}
		super.deactivate();
	}

	@Override
	public ToolPageRole getToolPageRole() {
		return ToolPageRole.ROLE_2D;
	}

	@Override
	public void createControl(Composite parent) {

		loadExistingData();

		rootComposite = new SashForm(parent, SWT.VERTICAL);
		rootComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		final SashForm tableComposite = new SashForm(rootComposite, SWT.HORIZONTAL);
		tableComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		createSpectraTable(tableComposite);
		createSpectraRegionTable(tableComposite);
		tableComposite.setWeights(new int[]{1,1});
		createPlotView(rootComposite);
		rootComposite.setWeights(new int[]{1,3});
		createActions();
		doBinding();

	}

	private void loadExistingData() {
		if (getPlottingSystem() != null && getPlottingSystem().getTraces().size() == 1) {
			ITrace trace = getPlottingSystem().getTraces().iterator().next();
			if (trace instanceof IImageTrace) {
				validateAndLoadSpectra((IImageTrace) trace);
				//setDataForEnergySelection();
			}
		}
	}

	private void doBinding() {
		spectraTableComposite.createSpectraSelectionBinding();

		spectraTableComposite.getSelectedSpectraList().addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						if (element instanceof SpectrumDataNode) {
							SpectrumDataNode spectrum = (SpectrumDataNode) element;
							if (!plottingSystem.isDisposed()) {
								removeFromPlottingSystem((ILineTrace) spectrum.getTrace());
							}
							spectrum.clearTrace();
						}
					}
					@Override
					public void handleAdd(int index, Object element) {
						if (element instanceof SpectrumDataNode) {
							SpectrumDataNode spectrum = (SpectrumDataNode) element;
							if (!plottingSystem.isDisposed()) {
								ITrace trace = TimeResolvedToolPage.this.plotSpectrum(spectrum);
								spectrum.setTrace(trace);
							}
						}
					}
				});
			}
		});

		spectraRegionTableComposite.getSelectedRegionSpectraList().addListChangeListener(new IListChangeListener() {
			private static final int ADDED_ALPHA_FOR_SELECTED_VALUE = 20;
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						IRegion region = ((SpectraRegionDataNode) element).getRegion();
						if (region.getAlpha() > 20) {
							region.setAlpha(region.getAlpha() - ADDED_ALPHA_FOR_SELECTED_VALUE);
						}
						TimeResolvedToolPage.this.getPlottingSystem().repaint();
					}

					@Override
					public void handleAdd(int index, Object element) {
						IRegion region = ((SpectraRegionDataNode) element).getRegion();
						if (region.getAlpha() < 255 - ADDED_ALPHA_FOR_SELECTED_VALUE) {
							region.setAlpha(region.getAlpha() + ADDED_ALPHA_FOR_SELECTED_VALUE);
						} else {
							region.setAlpha(255);
						}
						TimeResolvedToolPage.this.getPlottingSystem().repaint();
					}
				});
			}
		});

		spectraRegionTableComposite.addPropertyChangeListener(SpectraRegionComposite.SPECTRA_REGION_TRACE_SHOULD_ADD, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				SpectraRegionDataNode spectraRegion = (SpectraRegionDataNode) evt.getNewValue();
				addTracesForRegion(spectraRegion);
			}
		});

		spectraRegionTableComposite.addPropertyChangeListener(SpectraRegionComposite.SPECTRA_REGION_TRACE_SHOULD_REMOVE, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				SpectraRegionDataNode spectraRegion = (SpectraRegionDataNode) evt.getNewValue();
				removeTracesForRegion(spectraRegion);
			}
		});

	}

	private void createActions() {
		createToolPageActions();
	}

	private void createSpectraTable(Composite parent) {
		spectraTableComposite = new SpectraTableComposite(parent, SWT.None, toolPageModel, timeEnergyShifting);
		spectraTableComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		toolPageModel.addPropertyChangeListener(ToolPageModel.TRACE_STACK_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				updateStackOffset((double) evt.getOldValue(), (double) evt.getNewValue());
			}
		});
		spectraTableComposite.addPropertyChangeListener(SpectraTableComposite.NEW_REGION_PROP_NAME, new PropertyChangeListener() {

			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				addSpectraRegion((SpectraRegionDataNode) evt.getNewValue());
			}
		});
	}

	private void createSpectraRegionTable(Composite parent) {
		spectraRegionTableComposite = new SpectraRegionComposite(parent, SWT.None, toolPageModel);
		spectraRegionTableComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		repopulateCachedSpectraRegion();
	}


	private void createPlotView(Composite parent) {
		plotsParentComposite = new SashForm(parent, SWT.HORIZONTAL);
		plotsParentComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

		SpectraPlotComposite plotParent = new SpectraPlotComposite(plotsParentComposite, SWT.None);
		plotParent.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		plotParent.setLayout(new GridLayout(1, true));
		ActionBarWrapper actionbarWrapper = ActionBarWrapper.createActionBars(plotParent, null);
		try {
			if (plottingSystem == null) {
				plottingSystem = PlottingFactory.createPlottingSystem();
				plottingSystem.createPlotPart(plotParent,
						getTitle(),
						actionbarWrapper,
						PlotType.XY,
						this.getViewPart());
				plottingSystem.getPlotComposite().setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
				plottingSystem.getSelectedXAxis().setAxisAutoscaleTight(true);
				plottingSystem.getSelectedXAxis().setTitle("Energy");
				plottingSystem.setRescale(true);
				toolPageModel.setSpectraPlotting(plottingSystem);

				engerySelectionLine = plottingSystem.createRegion(RegionUtils.getUniqueName("Region", plottingSystem), IRegion.RegionType.XAXIS_LINE);
				engerySelectionLine.setPlotType(plottingSystem.getPlotType());
				engerySelectionLine.setROI(new RectangularROI(1, 1, 1, 1, 1));
				plottingSystem.addRegion(engerySelectionLine);
				timeEnergyShifting.setEnergyRegion(engerySelectionLine);
				engerySelectionLine.setVisible(false);
			}
		} catch (Exception e) {
			logger.error("Unable to create plotting system", e);
		}
		Composite statusComponent = new Composite(plotParent, SWT.None);
		statusComponent.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		statusComponent.setLayout(new GridLayout(1, false));
		statusLabel = new Label(statusComponent, SWT.None);

		Composite timeEnergyPlotParent = new EnergyTimePlotComposite(plotsParentComposite, SWT.None, toolPageModel, timeEnergyShifting);
		timeEnergyPlotParent.setLayout(new GridLayout(1, true));

		timeEnergyShifting.addPropertyChangeListener(TimeEnergyShiftingModel.LOAD_DATA_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				boolean isLoaded = (boolean) evt.getNewValue();
				if (isLoaded) {
					plotsParentComposite.setWeights(new int[]{1,1});
					engerySelectionLine.setVisible(true);
				} else {
					plotsParentComposite.setWeights(new int[]{1,0});
					engerySelectionLine.setVisible(false);
				}
			}
		});
		if (timeEnergyShifting.isLoadData()) {
			plotsParentComposite.setWeights(new int[]{1,1});
		} else {
			plotsParentComposite.setWeights(new int[]{1,0});
		}
	}


	private ILineTrace plotSpectrum(SpectrumDataNode spectrum) {
		int index  = spectrum.getIndex();
		DoubleDataset data = (DoubleDataset) imageTrace.getData().getSlice(new int[]{index,0}, new int[]{index + 1, TimeResolvedDataNode.NUMBER_OF_STRIPS}, new int[]{1, 1});
		data.squeeze();
		String name = Integer.toString(spectrum.getIndex());
		if (!cycleIndex.isEmpty()) {
			name = cycleIndex + "-" + name;
		}
		ILineTrace trace = plottingSystem.createLineTrace(name);
		trace.setData(energy, data);
		trace.setUserObject(spectrum);
		addToPlottingSystem(trace);
		return trace;
	}


	private void addTracesForRegion(SpectraRegionDataNode region) {
		DoubleDataset data = region.getDataset((DoubleDataset) imageTrace.getData());
		int noOfSpectra = data.getShape()[0];
		int noOfChannels = data.getShape()[1];
		String name = region.toString();
		if (!cycleIndex.isEmpty()) {
			name = cycleIndex + "-" + name;
		}
		for (int i = 0; i < noOfSpectra; i++) {
			DoubleDataset dataItem = (DoubleDataset) data.getSliceView(new int[]{i, 0}, new int[]{i + 1, noOfChannels}, null);
			dataItem.setName(name + " " + i);
			dataItem.squeeze();
			ILineTrace trace = plottingSystem.createLineTrace(name + " " + i);
			region.addTrace(trace);
			trace.setData(energy, dataItem);
			addToPlottingSystem(trace);
		}
	}

	private void removeTracesForRegion(SpectraRegionDataNode region) {
		for(ITrace object : region.getTraces()) {
			removeFromPlottingSystem((ILineTrace) object);
		}
		region.clearTrace();
	}

	private final List<ILineTrace> stackList = new LinkedList<ILineTrace>();
	private void addToPlottingSystem(ILineTrace trace) {
		((DoubleDataset) trace.getYData()).iadd(stackList.size() * toolPageModel.getTraceStack());
		if (timeEnergyShifting.isEnergyShifted()) {
			int[] selectedIndex = timeEnergyShifting.getSelectedIndex();
			if (selectedIndex.length > 1) {
				int[] dervIndex = timeEnergyShifting.getdervIndex();
				int index = ((SpectrumDataNode) trace.getUserObject()).getIndex();
				double diff = ((DoubleDataset) energy).get(dervIndex[selectedIndex[0]]) - ((DoubleDataset) energy).get(dervIndex[index]);
				((DoubleDataset) trace.getXData()).iadd(diff);
			}
		}
		plottingSystem.addTrace(trace);
		stackList.add(trace);
		if (plottingSystem.getTraces().size() == 1) {
			adjustROI(trace);
		}
		plottingSystem.repaint();
	}

	private void adjustROI(ILineTrace trace) {
		RectangularROI roi = (RectangularROI) engerySelectionLine.getROI();
		double x = roi.getPointX();
		if (x < trace.getXAxis().getLower() || x > trace.getXAxis().getUpper()) {
			engerySelectionLine.setROI(new RectangularROI((trace.getXAxis().getUpper() + trace.getXAxis().getLower()) / 2, 1, 1, 1, 1));
		}
	}

	private void removeFromPlottingSystem(ILineTrace trace) {
		int index = stackList.indexOf(trace);
		stackList.remove(index);
		plottingSystem.removeTrace(trace);
		for (int i = index; i < stackList.size(); i++) {
			((DoubleDataset) stackList.get(i).getYData()).isubtract(toolPageModel.getTraceStack());
		}
		plottingSystem.repaint();
	}

	private void updateStackOffset(double oldOffset, double newOffset) {
		for (int i = 0; i < stackList.size(); i++) {
			((DoubleDataset) stackList.get(i).getYData()).isubtract(i * oldOffset);
		}
		for (int i = 0; i < stackList.size(); i++) {
			((DoubleDataset) stackList.get(i).getYData()).iadd(i * newOffset);
		}
		plottingSystem.repaint();
	}

	@Override
	public Object getAdapter(@SuppressWarnings("rawtypes") Class clazz) {
		if (clazz == IToolPageSystem.class) {
			return plottingSystem;
		}
		return super.getAdapter(clazz);
	}

	@Override
	public Control getControl() {
		return rootComposite;
	}

	@Override
	public void setFocus() {
		if (!rootComposite.isDisposed()) {
			rootComposite.setFocus();
		}
	}

	@Override
	public void regionCreated(RegionEvent evt) {}

	@Override
	public void regionCancelled(RegionEvent evt) {}

	@Override
	public void regionNameChanged(RegionEvent evt, String oldName) {}

	@Override
	public void regionAdded(RegionEvent evt) {
		IRegion region = evt.getRegion();
		region.setShowPosition(true);
		if (spectraDataLoaded && region.getRegionType() == RegionType.YAXIS && region.getUserObject() == null) {
			SpectraRegionDataNode spectraRegion = new SpectraRegionDataNode(region, timeResolvedData);
			addSpectraRegion(spectraRegion);
		}
	}

	private void addSpectraRegion(SpectraRegionDataNode spectraRegion) {
		spectraRegionTableComposite.getSpectraRegionList().add(spectraRegion);
	}

	@Override
	public void regionRemoved(RegionEvent evt) {
		Object userObject = evt.getRegion().getUserObject();
		if (userObject instanceof SpectraRegionDataNode) {
			SpectraRegionDataNode spectraRegion = (SpectraRegionDataNode) userObject;
			spectraRegionTableComposite.getSpectraRegionList().remove(spectraRegion);
		}
	}

	@Override
	public void regionsRemoved(RegionEvent evt) {}

	@Override
	public void traceCreated(TraceEvent evt) {}

	@Override
	public void traceUpdated(TraceEvent evt) {
		if (evt.getSource() instanceof IImageTrace) {
			clearData();
			validateAndLoadSpectra((IImageTrace) evt.getSource());
		}
	}

	@Override
	public void traceAdded(TraceEvent evt) {
		if (evt.getSource() instanceof IImageTrace) {
			validateAndLoadSpectra((IImageTrace) evt.getSource());
		}
	}

	@Override
	public void traceRemoved(TraceEvent evt) {
		clearData();
	}

	@Override
	public void tracesUpdated(TraceEvent evt) {}

	@Override
	public void tracesRemoved(TraceEvent evet) {
		evet.getSource();
	}

	@Override
	public void tracesAdded(TraceEvent evt) {}

	@Override
	public void traceWillPlot(TraceWillPlotEvent evt) {}


	@Override
	public void dispose() {
		super.dispose();
		energyTimeViewIcon.dispose();
	}
}
