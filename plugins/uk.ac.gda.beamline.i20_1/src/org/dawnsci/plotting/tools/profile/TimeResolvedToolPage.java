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

import gda.scan.ede.datawriters.EdeTimeResolvedExperimentDataWriter;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;

import org.dawb.common.ui.util.EclipseUtils;
import org.dawb.common.ui.widgets.ActionBarWrapper;
import org.dawb.common.ui.wizard.PlotDataConversionWizard;
import org.dawnsci.plotting.api.IPlottingSystem;
import org.dawnsci.plotting.api.PlotType;
import org.dawnsci.plotting.api.PlottingFactory;
import org.dawnsci.plotting.api.filter.AbstractPlottingFilter;
import org.dawnsci.plotting.api.filter.IFilterDecorator;
import org.dawnsci.plotting.api.histogram.ImageServiceBean.HistoType;
import org.dawnsci.plotting.api.region.IRegion;
import org.dawnsci.plotting.api.region.IRegion.RegionType;
import org.dawnsci.plotting.api.region.IRegionListener;
import org.dawnsci.plotting.api.region.RegionEvent;
import org.dawnsci.plotting.api.region.RegionUtils;
import org.dawnsci.plotting.api.tool.AbstractToolPage;
import org.dawnsci.plotting.api.tool.IToolPageSystem;
import org.dawnsci.plotting.api.trace.IImageTrace;
import org.dawnsci.plotting.api.trace.ILineTrace;
import org.dawnsci.plotting.api.trace.ITrace;
import org.dawnsci.plotting.api.trace.ITraceListener;
import org.dawnsci.plotting.api.trace.TraceEvent;
import org.dawnsci.plotting.api.trace.TraceWillPlotEvent;
import org.dawnsci.slicing.tools.hyper.HyperComponent;
import org.dawnsci.slicing.tools.hyper.IDatasetROIReducer;
import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateSetStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.IObservable;
import org.eclipse.core.databinding.observable.list.IListChangeListener;
import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.ListChangeEvent;
import org.eclipse.core.databinding.observable.list.ListDiffVisitor;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.core.databinding.observable.map.IObservableMap;
import org.eclipse.core.databinding.observable.masterdetail.IObservableFactory;
import org.eclipse.core.databinding.observable.set.IObservableSet;
import org.eclipse.core.databinding.observable.set.WritableSet;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IMenuListener;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.databinding.viewers.ObservableListContentProvider;
import org.eclipse.jface.databinding.viewers.ObservableListTreeContentProvider;
import org.eclipse.jface.databinding.viewers.ObservableMapLabelProvider;
import org.eclipse.jface.databinding.viewers.ViewerProperties;
import org.eclipse.jface.databinding.viewers.ViewersObservables;
import org.eclipse.jface.dialogs.IInputValidator;
import org.eclipse.jface.dialogs.InputDialog;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.viewers.CheckboxTableViewer;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.jface.viewers.TreeViewerColumn;
import org.eclipse.jface.window.Window;
import org.eclipse.jface.wizard.IWizard;
import org.eclipse.jface.wizard.WizardDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.DirectoryDialog;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.TabFolder;
import org.eclipse.swt.widgets.TabItem;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.swt.widgets.ToolItem;
import org.eclipse.swt.widgets.Tree;
import org.eclipse.swt.widgets.TreeColumn;
import org.eclipse.ui.IEditorInput;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.EditorPart;
import org.eclipse.ui.part.FileEditorInput;
import org.nexusformat.NexusFile;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.dataset.IDataset;
import uk.ac.diamond.scisoft.analysis.dataset.ILazyDataset;
import uk.ac.diamond.scisoft.analysis.dataset.Maths;
import uk.ac.diamond.scisoft.analysis.dataset.Slice;
import uk.ac.diamond.scisoft.analysis.io.DataHolder;
import uk.ac.diamond.scisoft.analysis.io.IMetaData;
import uk.ac.diamond.scisoft.analysis.io.LoaderFactory;
import uk.ac.diamond.scisoft.analysis.roi.IROI;
import uk.ac.diamond.scisoft.analysis.roi.LinearROI;
import uk.ac.diamond.scisoft.analysis.roi.RectangularROI;
import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.common.rcp.UIHelper;
import uk.ac.gda.exafs.calibration.data.EdeCalibrationModel;
import uk.ac.gda.exafs.calibration.ui.EnergyCalibrationWizard;

public class TimeResolvedToolPage extends AbstractToolPage implements IRegionListener, ITraceListener {

	private static final double STACK_OFFSET = 0.1;

	public static final String DATA_PATH = "/entry1/" + EdeTimeResolvedExperimentDataWriter.NXDATA_LN_I0_IT + "/data";
	public static final String CYCLE_AVERAGE_DATA_PATH = "/entry1/" + EdeTimeResolvedExperimentDataWriter.NXDATA_CYCLE_LN_I0_IT_WITH_AVERAGED + "/data";

	private static final String GROUP_PATH = "/entry1/" + EdeTimeResolvedExperimentDataWriter.NXDATA_LN_I0_IT + "/group";
	private static final String TIME_AXIS_PATH = "/entry1/" + EdeTimeResolvedExperimentDataWriter.NXDATA_LN_I0_IT + "/time";
	private static final String ENERGY_SOURCE_PATH = "/entry1/instrument/xstrip/Energy";
	private static final int ENERGY_AXIS_INDEX = 0;

	private TimeResolvedDataNode timeResolvedData; // = new TimeResolvedDataNode();

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private final IObservableList  spectraRegionList = new WritableList(new ArrayList<SpectraRegionDataNode>(), SpectraRegionDataNode.class);
	private final IObservableList selectedRegionSpectraList = new WritableList(new ArrayList<SpectraRegionDataNode>(), SpectraRegionDataNode.class);
	private final IObservableSet checkedRegionSpectraList = new WritableSet(new HashSet<SpectraRegionDataNode>(), SpectraRegionDataNode.class);
	private final IObservableList selectedSpectraList = new WritableList(new ArrayList<Object>(), Object.class);

	private final List<IRegion> plottedRegions = new ArrayList<IRegion>();

	private SashForm rootComposite;

	private TreeViewer spectraTreeTable;
	private CheckboxTableViewer spectraRegionTableViewer;

	private IPlottingSystem plottingSystem;
	private IImageTrace imageTrace;
	private File dataFile;

	private IDataset energy;

	private Binding selectedSpectraBinding;

	private boolean spectraDataLoaded = false;

	private HyperComponent hyperComponent;

	@Override
	public void activate() {
		getPlottingSystem().addRegionListener(this);
		getPlottingSystem().addTraceListener(this);
		super.activate();
	}

	private final PropertyChangeListener spectraChangedListener = new PropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getPropertyName().equals(SpectraRegionDataNode.SPECTRA_CHANGED)) {
				SpectraRegionDataNode spectraRegion = (SpectraRegionDataNode) evt.getSource();
				if (spectraRegionTableViewer != null && spectraRegionTableViewer.getChecked(spectraRegion)) {
					removeTracesForRegion(spectraRegion);
					addTracesForRegion(spectraRegion);
				}
			}
		}
	};

	private int cycles = 0;

	// TODO Validate data and manage UI if not correct dataset
	private void validateAndLoadSpectra(IImageTrace image) {
		//clearRegionsOnPlot();
		//		clearSpectra();
		imageTrace = image;
		imageTrace.setHistoType(HistoType.OUTLIER_VALUES);
		try {
			String path = getDataFilePath(image);
			dataFile = new File(path);
			Collection<String> dataPaths = LoaderFactory.getMetaData(path, null).getDataNames();
			if (dataPaths.contains(GROUP_PATH) && dataPaths.contains(TIME_AXIS_PATH)) {
				DataHolder dataHolder = LoaderFactory.getData(path);
				ILazyDataset groups = dataHolder.getLazyDataset(GROUP_PATH);
				ILazyDataset time = dataHolder.getLazyDataset(TIME_AXIS_PATH);
				int[] dataShape = LoaderFactory.getMetaData(path, null).getDataShapes().get(DATA_PATH);
				if (dataShape != null && dataShape.length == 3) {
					cycles  = dataShape[0];
				}

				timeResolvedData = new TimeResolvedDataNode();

				//				if (dataHolder.contains(CYCLE_AXIS_PATH)) {
				//					ILazyDataset cycle = dataHolder.getLazyDataset(CYCLE_AXIS_PATH);
				//					timeResolvedData.setData(
				//							(DoubleDataset) groups.getSlice(),
				//							(DoubleDataset) time.getSlice(),
				//							(IntegerDataset) cycle.getSlice());
				//				} else {

				timeResolvedData.setData(
						(DoubleDataset) groups.getSlice(),
						(DoubleDataset) time.getSlice(),
						null);
				//				}
				energy = imageTrace.getAxes().get(ENERGY_AXIS_INDEX);
				if (spectraTreeTable != null) {
					spectraTreeTable.setInput(timeResolvedData);
				}
				populateSpectraRegion();
				spectraDataLoaded = true;
			}

		} catch (Exception e) {
			logger.error("Unable to find group data, not a valid dataset", e);
			UIHelper.showError("Unable to find group data, not a valid dataset", e.getMessage());
		}
	}

	private String getDataFilePath(IImageTrace image) throws Exception {
		IMetaData metaData = image.getData().getMetadata();
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

	private void populateSpectraRegion() {
		for (IRegion region : this.getPlottingSystem().getRegions()) {
			if (plottedRegions.contains(region)) {
				SpectraRegionDataNode spectraRegion = new SpectraRegionDataNode(region, timeResolvedData);
				addSpectraRegion(spectraRegion);
				checkedRegionSpectraList.add(spectraRegion);
			}
		}
		plottedRegions.clear();
	}

	private void clearData() {
		for (Object plottedRegion : checkedRegionSpectraList) {
			plottedRegions.add(((SpectraRegionDataNode) plottedRegion).getRegion());
		}
		spectraDataLoaded = false;

		if (selectedSpectraList != null) {
			selectedSpectraList.clear();
		}
		if (selectedRegionSpectraList != null) {
			selectedRegionSpectraList.clear();
		}
		if (spectraRegionList != null) {
			spectraRegionList.clear();
		}
		timeResolvedData.clearData();
	}

	@Override
	public void deactivate() {
		//		this.clearData();
		if (getPlottingSystem() != null) {
			getPlottingSystem().removeRegionListener(this);
			getPlottingSystem().removeTraceListener(this);
		}
		super.deactivate();
	}

	private void clearRegionsOnPlot() {
		//		IRegion[] regionsToRemove = new IRegion[spectraRegionList.size()];
		//		for (int i = 0; i < spectraRegionList.size(); i++) {
		//			regionsToRemove[i] = ((SpectraRegionDataNode) spectraRegionList.get(i)).getRegion();
		//		}
		//		for (int i = 0; i < spectraRegionList.size(); i++) {
		//			getPlottingSystem().removeRegion(regionsToRemove[i]);
		//		}
		spectraRegionList.clear();
	}

	@Override
	public ToolPageRole getToolPageRole() {
		return ToolPageRole.ROLE_2D;
	}

	@Override
	public void createControl(Composite parent) {

		initExistData();

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

	private void initExistData() {
		if (getPlottingSystem() != null && getPlottingSystem().getTraces().size() == 1) {
			ITrace trace = getPlottingSystem().getTraces().iterator().next();
			if (trace instanceof IImageTrace) {
				validateAndLoadSpectra((IImageTrace) trace);
				//setDataForEnergySelection();
			}
		}
	}

	// TODO Replace with hyper component 2D
	//	private void setDataForEnergySelection() {
	//		List<AbstractDataset> axes = new ArrayList<AbstractDataset>(imageTrace.getAxes().size());
	//		for(IDataset dataset : imageTrace.getAxes()) {
	//			axes.add((AbstractDataset) dataset);
	//		}
	//		hyperComponent.setData(imageTrace.getData(), axes, new Slice[2], new int[]{0,1}, main, side);
	//	}

	private final IDatasetROIReducer main = new IDatasetROIReducer() {
		private final RegionType regionType = RegionType.XAXIS_LINE;
		private final List<IDataset> traceAxes  = new ArrayList<IDataset>();
		@Override
		public boolean isOutput1D() {
			return true;
		}
		@Override
		public IDataset reduce(ILazyDataset data, List<AbstractDataset> axes, IROI roi, Slice[] slices, int[] order) {
			traceAxes.clear();
			traceAxes.add(axes.get(0).getSlice());
			return null;
		}
		@Override
		public List<RegionType> getSupportedRegionType() {
			List<IRegion.RegionType> regionList = new ArrayList<IRegion.RegionType>();
			regionList.add(regionType);
			return regionList;
		}
		@Override
		public IROI getInitialROI(List<AbstractDataset> axes, int[] order) {
			return new LinearROI(new double[]{500, 0}, new double[]{500, 10});
		}
		@Override
		public boolean supportsMultipleRegions() {
			return false;
		}
		@Override
		public List<IDataset> getAxes() {
			return traceAxes;
		}
	};

	private final IDatasetROIReducer side = new IDatasetROIReducer() {
		private final RegionType regionType = RegionType.XAXIS_LINE;
		private final List<IDataset> traceAxes = new ArrayList<IDataset>();
		@Override
		public boolean isOutput1D() {
			return true;
		}
		@Override
		public IDataset reduce(ILazyDataset data, List<AbstractDataset> axes, IROI roi, Slice[] slices, int[] order) {
			traceAxes.clear();
			traceAxes.add(axes.get(1).getSlice());

			return null;
		}
		@Override
		public List<RegionType> getSupportedRegionType() {
			List<IRegion.RegionType> regionList = new ArrayList<IRegion.RegionType>();
			regionList.add(regionType);
			return regionList;
		}
		@Override
		public IROI getInitialROI(List<AbstractDataset> axes, int[] order) {
			return new LinearROI(new double[]{0, 0}, new double[]{0, 10});
		}
		@Override
		public boolean supportsMultipleRegions() {
			return false;
		}
		@Override
		public List<IDataset> getAxes() {
			return traceAxes;
		}
	};

	private void doBinding() {
		createSpectraSelectionBinding();

		selectedSpectraList.addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						if (element instanceof SpectrumDataNode) {
							SpectrumDataNode spectrum = (SpectrumDataNode) element;
							if (!plottingSystem.isDisposed()) {
								plottingSystem.removeTrace(spectrum.getTrace());
								plottingSystem.repaint(true);
							}
							spectrum.clearTrace();
						}
					}
					@Override
					public void handleAdd(int index, Object element) {
						if (element instanceof SpectrumDataNode) {
							SpectrumDataNode spectrum = (SpectrumDataNode) element;
							if (!plottingSystem.isDisposed()) {
								ITrace trace = TimeResolvedToolPage.this.plotSpectrum(spectrum, Integer.toString(spectrum.getIndex()));
								spectrum.setTrace(trace);
								plottingSystem.repaint();
							}
						}
					}
				});
			}
		});

		spectraRegionList.addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(final ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						SpectraRegionDataNode spectraRegion = (SpectraRegionDataNode) element;
						spectraRegion.getRegion().removeROIListener(spectraRegion);
						spectraRegion.removePropertyChangeListener(spectraChangedListener);
						if (checkedRegionSpectraList.contains(spectraRegion)) {
							checkedRegionSpectraList.remove(spectraRegion);
						}
					}
					@Override
					public void handleAdd(int index, Object element) {}
				});
			}
		});

		dataBindingCtx.bindList(
				ViewerProperties.multipleSelection().observe(spectraRegionTableViewer), selectedRegionSpectraList);
		dataBindingCtx.bindSet(
				ViewersObservables.observeCheckedElements(spectraRegionTableViewer, SpectraRegionDataNode.class),
				checkedRegionSpectraList,
				plotCheckedRegionUpdateStrategy,
				plotCheckedRegionUpdateStrategy);

		//		spectraRegionTableViewer.addCheckStateListener(new ICheckStateListener() {
		//			@Override
		//			public void checkStateChanged(CheckStateChangedEvent event) {
		//				SpectraRegionDataNode spectraRegion = (SpectraRegionDataNode) event.getElement();
		//				if (event.getChecked()) {
		//					updatePlotting(spectraRegion, true);
		//				} else {
		//					updatePlotting(spectraRegion, false);
		//				}
		//			}
		//		});

		selectedRegionSpectraList.addListChangeListener(new IListChangeListener() {
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
	}

	private final UpdateSetStrategy plotCheckedRegionUpdateStrategy = new UpdateSetStrategy() {
		@Override
		protected IStatus doAdd(IObservableSet observableSet, Object element) {
			updatePlotting((SpectraRegionDataNode) element, true);
			return super.doAdd(observableSet, element);
		}
		@Override
		protected IStatus doRemove(IObservableSet observableSet, Object element) {
			updatePlotting((SpectraRegionDataNode) element, false);
			return super.doRemove(observableSet, element);
		}
	};


	private void createSpectraSelectionBinding() {
		if (selectedSpectraBinding == null) {
			selectedSpectraBinding = dataBindingCtx.bindList(ViewerProperties.multipleSelection().observe(spectraTreeTable), selectedSpectraList);
		}
	}

	private void removeSpectraSelectionBinding() {
		if (selectedSpectraBinding != null) {
			dataBindingCtx.removeBinding(selectedSpectraBinding);
			selectedSpectraBinding.dispose();
			selectedSpectraBinding = null;
		}
	}

	private void createActions() {
		createToolPageActions();
	}

	IObservableFactory dataObservableFactory = new IObservableFactory() {
		@Override
		public IObservable createObservable(Object target) {
			if (target instanceof TimeResolvedDataNode) {
				TimeResolvedDataNode root = (TimeResolvedDataNode) target;
				if (root.getCycles().size() == 1) {
					return ((CycleDataNode) root.getCycles().get(0)).getTimingGroups();
				}
				return root.getCycles();
			} else if (target instanceof CycleDataNode) {
				return ((CycleDataNode) target).getTimingGroups();
			} else if (target instanceof TimingGroupDataNode) {
				return ((TimingGroupDataNode) target).getSpectra();
			}
			return null;
		}
	};

	private void createSpectraTable(Composite parent) {
		Composite treeParent = new Composite(parent, SWT.None);
		treeParent.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		treeParent.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));

		createTootbarForSpectraTable(treeParent);

		Tree spectraTree = new Tree(treeParent, SWT.MULTI | SWT.BORDER | SWT.H_SCROLL | SWT.V_SCROLL);
		spectraTree.setHeaderVisible(true);
		spectraTree.setLinesVisible(true);
		spectraTree.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		spectraTreeTable = new TreeViewer(spectraTree);
		TreeColumn nameColumn = new TreeColumn(spectraTree, SWT.LEFT);
		nameColumn.setAlignment(SWT.LEFT);
		nameColumn.setText("Name");
		nameColumn.setWidth(155);
		TreeViewerColumn nameViewerColumn = new TreeViewerColumn(spectraTreeTable, nameColumn);
		nameViewerColumn.setLabelProvider(new ColumnLabelProvider());

		TreeColumn timeColumn = new TreeColumn(spectraTree, SWT.CENTER);
		timeColumn.setAlignment(SWT.LEFT);
		timeColumn.setText("Start time");
		timeColumn.setWidth(60);
		TreeViewerColumn timeViewerColumn = new TreeViewerColumn(spectraTreeTable, timeColumn);
		timeViewerColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public String getText(Object element) {
				if (element instanceof TimingGroupDataNode || element instanceof CycleDataNode) {
					return "";
				}
				return DataHelper.roundDoubletoString(((SpectrumDataNode) element).getStartTime()) + " s";
			}
		});

		spectraTreeTable.setContentProvider(new ObservableListTreeContentProvider(dataObservableFactory, null));

		final MenuManager menuManager = new MenuManager();
		Menu menu = menuManager.createContextMenu(spectraTreeTable.getTree());
		menuManager.addMenuListener(new IMenuListener() {
			@Override
			public void menuAboutToShow(IMenuManager manager) {
				menuManager.add(createPlotEveryIntervalAction);

				IStructuredSelection selection = (IStructuredSelection) spectraTreeTable.getSelection();
				if(selection.isEmpty()) {
					return;
				}

				if (isGroupsSelected(selection)) {
					// menuManager.add(zoomToGroupAction);
				}

				if (isSingleSpectrumSelected(selection)) {
					// menuManager.add(plotForEachGroupAction);
				}

				menuManager.add(createRegionAction);
				menuManager.add(createRegionAvgAction);
				menuManager.add(createRegionAvgEveryAction);
			}

			private boolean isSingleSpectrumSelected(IStructuredSelection selection) {
				return (selection.size() == 1 && selection.getFirstElement() instanceof SpectrumDataNode);
			}

			private boolean isGroupsSelected(IStructuredSelection selection) {
				Iterator<?> iterator = selection.iterator();
				while (iterator.hasNext()) {
					if (!(iterator.next() instanceof TimingGroupDataNode)) {
						return false;
					}
				}
				return true;
			}

			//			private boolean isCycleSelected(IStructuredSelection selection) {
			//				Iterator<?> iterator = selection.iterator();
			//				while (iterator.hasNext()) {
			//					if (!(iterator.next() instanceof CycleDataNode)) {
			//						return false;
			//					}
			//				}
			//				return true;
			//			}
		});
		menuManager.setRemoveAllWhenShown(true);
		spectraTreeTable.getTree().setMenu(menu);

		spectraTreeTable.setInput(timeResolvedData);
	}

	private final EdeCalibrationModel calibrationModel = new EdeCalibrationModel();

	private void createTootbarForSpectraTable(final Composite treeParent) {
		ToolBar toolBar = new ToolBar(treeParent, SWT.HORIZONTAL);
		toolBar.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		ToolItem collapseTree = new ToolItem(toolBar, SWT.PUSH);
		collapseTree.setText("");
		collapseTree.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_TOOL_BACK));
		collapseTree.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				spectraTreeTable.collapseAll();
			}
		});

		ToolItem expendTree = new ToolItem(toolBar, SWT.PUSH);
		expendTree.setText("");
		expendTree.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_TOOL_FORWARD));
		expendTree.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				spectraTreeTable.expandAll();
			}
		});

		final ToolItem plotOnSelection = new ToolItem(toolBar, SWT.CHECK);
		plotOnSelection.setText("");
		plotOnSelection.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ELCL_SYNCED));
		plotOnSelection.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				if (plotOnSelection.getSelection()) {
					selectedSpectraList.clear();
					removeSpectraSelectionBinding();
				} else {
					createSpectraSelectionBinding();
				}
			}
		});

		ToolItem calibrateEnergy = new ToolItem(toolBar, SWT.PUSH);
		calibrateEnergy.setText("");
		calibrateEnergy.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_OBJ_ELEMENT));
		calibrateEnergy.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				WizardDialog wizardDialog = new WizardDialog(treeParent.getShell(), new EnergyCalibrationWizard(calibrationModel));
				wizardDialog.setPageSize(1024, 768);
				if (wizardDialog.open() == Window.OK) {
					if (calibrationModel.getCalibrationResult() != null) {
						double[] value = applyNewEnergy(calibrationModel);
						try {
							applyEnergyToNexusFiles(value);
						} catch (Exception e) {
							UIHelper.showError("Error apply energy calibration", e.getMessage());
							logger.error("Error apply energy calibration", e);
						}
					}
				}
			}
		});

		ToolItem exportCycle = new ToolItem(toolBar, SWT.PUSH);
		exportCycle.setText("");
		exportCycle.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ETOOL_SAVEAS_EDIT));
		exportCycle.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				if (cycles > 0) {
					TimeResolvedDataExportUtils test = new TimeResolvedDataExportUtils();
					test.exportAndAverageCycles(dataFile, TimeResolvedToolPage.this.getControl().getDisplay(), cycles);
				} else {
					MessageDialog.openWarning(TimeResolvedToolPage.this.getControl().getShell(), "Unable to process", "Cycle data unavailable");
				}
			}
		});
	}

	private void applyEnergyToNexusFiles(double[] value) throws Exception {
		File[] selectedFiles = DataFileHelper.showMultipleFileSelectionDialog(this.getSite().getShell(), dataFile.getParent());
		if (selectedFiles == null || selectedFiles.length < 1) {
			return;
		}
		DirectoryDialog dlg = new DirectoryDialog(this.getSite().getShell());
		dlg.setFilterPath(selectedFiles[0].getParent());
		dlg.setText("Select a directory to store new data files");
		String dir = dlg.open();
		if (dir == null) {
			return;
		}

		for(File file : selectedFiles) {
			String path = DataFileHelper.copyToTempFolder(file, "calibrated");
			NexusFile nexusFile = new NexusFile(path, NexusFile.NXACC_RDWR);
			nexusFile.openpath(ENERGY_SOURCE_PATH);
			nexusFile.putdata(value);
			nexusFile.closedata();
			nexusFile.close();
			Files.copy(Paths.get(path), Paths.get(dir), StandardCopyOption.REPLACE_EXISTING);
		}
	}

	//	private final Action zoomToSelectedCycleAction = new Action("Zoom") {
	//		@Override
	//		public void run() {
	//			IStructuredSelection selection = (IStructuredSelection) spectraTreeTable.getSelection();
	//			CycleDataNode cycle = (CycleDataNode) selection.getFirstElement();
	//			double start = ((SpectrumDataNode) ((TimingGroupDataNode) cycle.getTimingGroups().get(0)).getSpectra().get(0)).getStartTime();
	//			TimingGroupDataNode lastTimingGroup = (TimingGroupDataNode) cycle.getTimingGroups().get(cycle.getTimingGroups().size() - 1);
	//			// FIXME
	//			double end = ((SpectrumDataNode) lastTimingGroup.getSpectra().get(lastTimingGroup.getSpectra().size() - 1)).getStartTime() + lastTimingGroup.getTimePerFrame();
	//			getPlottingSystem().getSelectedYAxis().setRange(end, start);
	//
	//		}
	//	};

	private final Action createPlotEveryIntervalAction = new Action("Select spectrum for every") {
		@Override
		public void run() {
			if (dlg.open() == Window.OK) {
				int intervalToPlot = Integer.parseInt(dlg.getValue());
				int counter = 0;
				for (Object objCycle : timeResolvedData.getCycles()) {
					for (Object objTimingGroup : ((CycleDataNode) objCycle).getTimingGroups()) {
						for (Object objSpectrum : ((TimingGroupDataNode) objTimingGroup).getSpectra()) {
							SpectrumDataNode spectrumToPlot = (SpectrumDataNode) objSpectrum;
							if (counter == 0) {
								spectraTreeTable.expandAll();
								selectedSpectraList.clear();
								selectedSpectraList.add(spectrumToPlot);
							}
							else if (counter % intervalToPlot == 0) {
								selectedSpectraList.add(spectrumToPlot);
							}
							counter++;
						}
					}
				}
			}
		}
	};

	private final Action createRegionAvgAction = new Action("Create region and average") {
		@Override
		public void run() {
			try {
				List<IRegion> regions = findSpectraAndCreateRegion();
				for (IRegion region : regions) {
					AvgRegionToolDataModel spectraRegion = new AvgRegionToolDataModel(region, timeResolvedData);
					addRegionAction(spectraRegion);
				}
			} catch (Exception e) {
				UIHelper.showError("Unable to create regions for spectra", e.getMessage());
			}
		}
	};

	private final Action createRegionAvgEveryAction = new Action("Create region and average every...") {
		@Override
		public void run() {
			if (dlg.open() == Window.OK) {
				try {
					List<IRegion> regions = findSpectraAndCreateRegion();
					for (IRegion region : regions) {
						AvgRegionToolDataModel spectraRegion = new AvgRegionToolDataModel(region, timeResolvedData);
						addRegionAction(spectraRegion);
						spectraRegion.setNoOfSpectraToAvg(Integer.parseInt(dlg.getValue()));
					}
				} catch (Exception e) {
					UIHelper.showError("Unable to create regions for spectra", e.getMessage());
				}
			}
		}
	};

	private final InputDialog dlg = new InputDialog(Display.getCurrent().getActiveShell(),
			"", "Enter number", "", new IInputValidator() {
		@Override
		public String isValid(String newText) {
			try {
				int avgValue = Integer.parseInt(newText);
				if (avgValue < 1) {
					return "Invalid number";
				}
			} catch(NumberFormatException e) {
				return "Not a number";
			}
			return null;
		}
	});

	private final Action createRegionAction = new Action("Create region") {
		@Override
		public void run() {
			try {
				List<IRegion> regions = findSpectraAndCreateRegion();
				for (IRegion region : regions) {
					SpectraRegionDataNode spectraRegion = new SpectraRegionDataNode(region, timeResolvedData);
					addRegionAction(spectraRegion);
				}
			} catch (Exception e) {
				UIHelper.showError("Unable to create regions for spectra", e.getMessage());
			}
		}
	};


	private void addRegionAction(SpectraRegionDataNode spectraRegion) {
		selectedSpectraList.clear();
		addSpectraRegion(spectraRegion);
		TimeResolvedToolPage.this.getPlottingSystem().addRegion(spectraRegion.getRegion());
	}

	private List<IRegion> findSpectraAndCreateRegion() throws Exception {
		List<IRegion> regions = new ArrayList<IRegion>();
		if(spectraTreeTable.getSelection() instanceof IStructuredSelection) {
			IStructuredSelection selection = (IStructuredSelection) spectraTreeTable.getSelection();
			Iterator<?> iterator = selection.iterator();
			int startIndex = -1;
			int endIndex = -1;
			while (iterator.hasNext()) {
				Object object = iterator.next();
				if (object instanceof SpectrumDataNode) {
					SpectrumDataNode spectrum = (SpectrumDataNode) object;
					if (startIndex == -1) {
						startIndex = spectrum.getIndex();
						endIndex = spectrum.getIndex();
						continue;
					}
					if (spectrum.getIndex() > endIndex + 1 ) { // break in selection
						regions.add(createRegionROI(startIndex, endIndex));
						startIndex = spectrum.getIndex();
						endIndex = spectrum.getIndex();
					} else {
						endIndex = spectrum.getIndex();
					}
				}
			}
			if (startIndex != -1) {
				regions.add(createRegionROI(startIndex, endIndex));
			}
		}
		return regions;
	}

	private IRegion createRegionROI(int startIndex, int endIndex) throws Exception {
		IRegion region = createRegion();
		region.setROI(new RectangularROI(0, startIndex, 100, endIndex - startIndex + 1, 0));
		return region;
	}

	private IRegion createRegion() throws Exception {
		IPlottingSystem plotting = getPlottingSystem();
		IRegion region = plotting.createRegion(RegionUtils.getUniqueName("Region", plotting), IRegion.RegionType.YAXIS);
		region.setPlotType(plotting.getPlotType());
		region.setShowLabel(true);
		return region;
	}

	private void createSpectraRegionTable(Composite parent) {

		Composite regionTableParent = new Composite(parent, SWT.None);
		regionTableParent.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		regionTableParent.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));

		createTootbarForSpectraRegionTable(regionTableParent);

		spectraRegionTableViewer = CheckboxTableViewer.newCheckList(
				regionTableParent, SWT.BORDER | SWT.H_SCROLL | SWT.V_SCROLL | SWT.MULTI);
		Table spectraRegionTable = spectraRegionTableViewer.getTable();
		spectraRegionTable.setHeaderVisible(true);
		spectraRegionTable.setLinesVisible(true);
		spectraRegionTable.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		TableViewerColumn colRegionName = new TableViewerColumn(spectraRegionTableViewer, SWT.NONE);
		colRegionName.getColumn().setText("Region name");
		colRegionName.getColumn().setWidth(100);

		TableViewerColumn colStartSpectrumIndex = new TableViewerColumn(spectraRegionTableViewer, SWT.NONE);
		colStartSpectrumIndex.getColumn().setText("Start");
		colStartSpectrumIndex.getColumn().setWidth(40);

		TableViewerColumn colEndSpectrumIndex = new TableViewerColumn(spectraRegionTableViewer, SWT.NONE);
		colEndSpectrumIndex.getColumn().setText("End");
		colEndSpectrumIndex.getColumn().setWidth(40);

		TableViewerColumn colRegionDesc = new TableViewerColumn(spectraRegionTableViewer, SWT.NONE);
		colRegionDesc.getColumn().setText("Description");
		colRegionDesc.getColumn().setWidth(60);

		ObservableListContentProvider contentProvider = new ObservableListContentProvider();
		IObservableSet knownElements = contentProvider.getKnownElements();

		final IObservableMap startColumn = BeanProperties.value(SpectraRegionDataNode.class,
				SpectraRegionDataNode.START).observeDetail(knownElements);
		final IObservableMap endColumn = BeanProperties.value(SpectraRegionDataNode.class,
				SpectraRegionDataNode.END).observeDetail(knownElements);

		IObservableMap[] labelMaps = {startColumn, endColumn};

		spectraRegionTableViewer.setContentProvider(contentProvider);
		spectraRegionTableViewer.setLabelProvider(new ObservableMapLabelProvider(labelMaps) {
			@Override
			public String getColumnText(Object element, int columnIndex) {
				SpectraRegionDataNode spectraRegionToolDataModel = (SpectraRegionDataNode) element;
				switch (columnIndex) {
				case 0: return spectraRegionToolDataModel.getRegion().getLabel();
				case 1: return Integer.toString(spectraRegionToolDataModel.getStart().getIndex());
				case 2: return Integer.toString(spectraRegionToolDataModel.getEnd().getIndex());
				case 3: return spectraRegionToolDataModel.getDescription();
				default : return "Unkown column";
				}
			}
		});

		final MenuManager menuManager = new MenuManager();
		Menu menu = menuManager.createContextMenu(spectraRegionTableViewer.getTable());
		menuManager.addMenuListener(new IMenuListener() {
			@Override
			public void menuAboutToShow(IMenuManager manager) {
				if(spectraRegionTableViewer.getSelection().isEmpty()) {
					return;
				}
				menuManager.add(removeRegionAction);
			}
		});
		menuManager.setRemoveAllWhenShown(true);
		// Set the MenuManager
		spectraRegionTableViewer.getTable().setMenu(menu);

		//		spectraRegionTableViewer.addCheckStateListener(new ICheckStateListener() {
		//			@Override
		//			public void checkStateChanged(CheckStateChangedEvent event) {
		//				updatePlotting((SpectraRegionDataNode) event.getElement(), event.getChecked());
		//			}
		//		});
		spectraRegionTableViewer.setInput(spectraRegionList);

	}

	private void createTootbarForSpectraRegionTable(Composite regionTableParent) {
		ToolBar toolBar = new ToolBar(regionTableParent, SWT.HORIZONTAL);
		toolBar.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		ToolItem selectAllToolItem = new ToolItem(toolBar, SWT.PUSH);
		selectAllToolItem.setText("");
		selectAllToolItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_OBJ_ADD));
		selectAllToolItem.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				for (TableItem item : spectraRegionTableViewer.getTable().getItems()) {
					if (!item.getChecked()) {
						spectraRegionTableViewer.setChecked(item.getData(), true);
						fireCheckSelectionEvent(event, item);
					}
				}

			}
		});

		ToolItem unSelectAllToolItem = new ToolItem(toolBar, SWT.PUSH);
		unSelectAllToolItem.setText("");
		unSelectAllToolItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ETOOL_CLEAR));
		unSelectAllToolItem.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				for (TableItem item : spectraRegionTableViewer.getTable().getItems()) {
					if (item.getChecked()) {
						spectraRegionTableViewer.setChecked(item.getData(), false);
						fireCheckSelectionEvent(event, item);
					}
				}
			}
		});

		ToolItem saveAsciiToolItem = new ToolItem(toolBar, SWT.PUSH);
		saveAsciiToolItem.setText("");
		saveAsciiToolItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ETOOL_SAVE_EDIT));
		saveAsciiToolItem.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				IWizard wiz;
				try {
					wiz = EclipseUtils.openWizard(PlotDataConversionWizard.ID, false);
					WizardDialog wd = new  WizardDialog(Display.getCurrent().getActiveShell(), wiz);
					wd.setTitle(wiz.getWindowTitle());
					if (wiz instanceof PlotDataConversionWizard) {
						((PlotDataConversionWizard)wiz).setPlottingSystem(plottingSystem);
					}
					wd.open();
				} catch (Exception e) {
					// TODO Auto-generated catch block
					logger.error("TODO put description of error here", e);
				}
			}
		});

		ToolItem saveNexusToolItem = new ToolItem(toolBar, SWT.PUSH);
		saveNexusToolItem.setText("");
		saveNexusToolItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ETOOL_SAVEAS_EDIT));
		saveNexusToolItem.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				//				String newFilePath = showNexusFileSaveDialog();
				//				if (newFilePath != null) {
				//					if (!Files.exists(Paths.get(newFilePath))) {
				//						try {
				//							Files.copy(Paths.get(imageFile.getAbsolutePath()), Paths.get(newFilePath));
				//							NexusFile nexusFile = new NexusFile(newFilePath, NexusFile.NXACC_RDWR);
				//							// TODO Implement this
				//							nexusFile.closedata();
				//						} catch (IOException | NexusException e) {
				//
				//						}
				//					}
				//				}
			}
		});
	}

	private void fireCheckSelectionEvent(Event event, TableItem item) {
		SelectionEvent checkEvent = new SelectionEvent(event);
		checkEvent.detail = SWT.CHECK;
		checkEvent.item = item;
		spectraRegionTableViewer.handleSelect(checkEvent);
	}

	private void createPlotView(Composite parent) {
		TabFolder folder = new TabFolder(parent, SWT.NONE);
		GridData gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
		gridData.horizontalSpan = 2;
		folder.setLayoutData(gridData);
		TabItem plottingTab = new TabItem(folder, SWT.NONE);
		plottingTab.setText("Plotting");
		createPlottingComposite(folder, plottingTab);
		TabItem energySelectionTab = new TabItem(folder, SWT.NONE);
		energySelectionTab.setText("Energy selection");
		createEnergySelectionComposite(folder, energySelectionTab);
	}

	private void createEnergySelectionComposite(TabFolder folder, TabItem tab) {
		hyperComponent = new HyperComponent(this.getPart());
		hyperComponent.createControl(folder);
		hyperComponent.getControl().setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		tab.setControl(hyperComponent.getControl());
		//setDataForEnergySelection();
	}

	private void createPlottingComposite(TabFolder folder, TabItem tab) {
		Composite plotParent = new Composite(folder, SWT.None);
		plotParent.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		plotParent.setLayout(new GridLayout(1, false));
		tab.setControl(plotParent);
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
				plottingSystem.getSelectedYAxis().setAxisAutoscaleTight(true);
				IFilterDecorator filter = PlottingFactory.createFilterDecorator(plottingSystem);
				plottingSystem.setRescale(true);
				filter.addFilter(stackFilter);
			}
		} catch (Exception e) {
			logger.error("Unable to create plotting system", e);
			return;
		}
	}

	private void updatePlotting(SpectraRegionDataNode region, boolean isAdded) {
		if (isAdded) {
			addTracesForRegion(region);
		} else {
			removeTracesForRegion(region);
		}
	}

	private void addTracesForRegion(SpectraRegionDataNode region) {
		ITrace[] traces = region.createTraces(plottingSystem, imageTrace, energy);
		plottingSystem.getTraces();
		for(ITrace trace : traces) {
			plottingSystem.addTrace(trace);
		}
		plottingSystem.repaint(true);
	}

	private void removeTracesForRegion(SpectraRegionDataNode region) {
		for(ITrace object : region.getTraces()) {
			plottingSystem.removeTrace(object);
		}
		region.clearTrace();
		plottingSystem.repaint(true);
	}

	private ILineTrace plotSpectrum(SpectrumDataNode spectrum, String name) {
		int index  = spectrum.getIndex();
		DoubleDataset data = (DoubleDataset) imageTrace.getData().getSlice(new int[]{index,0}, new int[]{index + 1, TimeResolvedDataNode.NUMBER_OF_STRIPS}, new int[]{1, 1});
		data.setName(name);
		data.squeeze();
		ILineTrace trace = plottingSystem.createLineTrace(name);
		trace.setData(energy, data);
		trace.setUserObject(spectrum);
		plottingSystem.addTrace(trace);
		return trace;
	}

	private final AbstractPlottingFilter stackFilter = new AbstractPlottingFilter() {
		@Override
		protected IDataset[] filter(IDataset x, IDataset y) {
			int traces = plottingSystem.getTraces().size();
			IDataset newY = Maths.add((AbstractDataset) y, new Double(traces * STACK_OFFSET));
			newY.setName(y.getName());
			return new IDataset[]{x, newY};
		}
		@Override
		public int getRank() {
			return 1;
		}
	};

	private final Action removeRegionAction = new Action("Remove") {
		@Override
		public void run() {
			if(spectraRegionTableViewer.getSelection() instanceof IStructuredSelection) {
				IStructuredSelection selection = (IStructuredSelection) spectraRegionTableViewer.getSelection();
				Iterator<?> iterator = selection.iterator();
				while (iterator.hasNext()) {
					getPlottingSystem().removeRegion(((SpectraRegionDataNode) iterator.next()).getRegion());
				}
			}
		}
	};

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
	public void regionAdded(RegionEvent evt) {
		//		IRegion region = evt.getRegion();
		//		region.setShowPosition(true);
		//		if (spectraDataLoaded && region.getRegionType() == RegionType.YAXIS && region.getUserObject() == null) {
		//			SpectraRegionDataNode spectraRegion = new SpectraRegionDataNode(region, timeResolvedData);
		//			addSpectraRegion(spectraRegion);
		//		}
	}

	private void addSpectraRegion(SpectraRegionDataNode spectraRegion) {
		spectraRegion.addPropertyChangeListener(spectraChangedListener);
		spectraRegionList.add(spectraRegion);
	}

	@Override
	public void regionRemoved(RegionEvent evt) {
		Object userObject = evt.getRegion().getUserObject();
		if (userObject instanceof SpectraRegionDataNode) {
			SpectraRegionDataNode spectraRegion = (SpectraRegionDataNode) userObject;
			spectraRegionList.remove(spectraRegion);
			if (spectraRegionTableViewer.getChecked(spectraRegion)) {
				removeTracesForRegion(spectraRegion);
			}
		}

		// evt.getRegion().getUserObject());
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
	public void tracesRemoved(TraceEvent evet) {}

	@Override
	public void tracesAdded(TraceEvent evt) {}

	@Override
	public void traceWillPlot(TraceWillPlotEvent evt) {}

	private double[] applyNewEnergy(EdeCalibrationModel calibrationModel) {
		int stripSize = energy.getSize();
		double[] value = new double[stripSize];
		for (int i = 0; i < stripSize; i++) {
			value[i] = calibrationModel.getCalibrationResult().value(i) / stripSize;
		}
		return value;
	}
}
