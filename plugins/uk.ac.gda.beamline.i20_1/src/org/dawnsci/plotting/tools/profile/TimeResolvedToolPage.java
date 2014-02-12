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

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.Iterator;

import org.dawb.common.ui.widgets.ActionBarWrapper;
import org.dawnsci.plotting.api.IPlottingSystem;
import org.dawnsci.plotting.api.PlotType;
import org.dawnsci.plotting.api.PlottingFactory;
import org.dawnsci.plotting.api.filter.AbstractPlottingFilter;
import org.dawnsci.plotting.api.filter.IFilterDecorator;
import org.dawnsci.plotting.api.region.IRegion;
import org.dawnsci.plotting.api.region.IRegionListener;
import org.dawnsci.plotting.api.region.RegionEvent;
import org.dawnsci.plotting.api.region.RegionUtils;
import org.dawnsci.plotting.api.tool.AbstractToolPage;
import org.dawnsci.plotting.api.trace.IImageTrace;
import org.dawnsci.plotting.api.trace.ILineTrace;
import org.dawnsci.plotting.api.trace.ITrace;
import org.dawnsci.plotting.api.trace.ITraceListener;
import org.dawnsci.plotting.api.trace.TraceEvent;
import org.dawnsci.plotting.api.trace.TraceWillPlotEvent;
import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
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
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IMenuListener;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.action.Separator;
import org.eclipse.jface.databinding.viewers.ObservableListContentProvider;
import org.eclipse.jface.databinding.viewers.ObservableListTreeContentProvider;
import org.eclipse.jface.databinding.viewers.ObservableMapLabelProvider;
import org.eclipse.jface.databinding.viewers.ViewerProperties;
import org.eclipse.jface.viewers.CheckStateChangedEvent;
import org.eclipse.jface.viewers.CheckboxTableViewer;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jface.viewers.ICheckStateListener;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.jface.viewers.TreeViewerColumn;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.swt.widgets.ToolItem;
import org.eclipse.swt.widgets.Tree;
import org.eclipse.swt.widgets.TreeColumn;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.PlatformUI;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.dataset.IDataset;
import uk.ac.diamond.scisoft.analysis.dataset.ILazyDataset;
import uk.ac.diamond.scisoft.analysis.dataset.Maths;
import uk.ac.diamond.scisoft.analysis.dataset.Slice;
import uk.ac.diamond.scisoft.analysis.io.IMetaData;
import uk.ac.diamond.scisoft.analysis.io.LoaderFactory;
import uk.ac.diamond.scisoft.analysis.roi.RectangularROI;
import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.common.rcp.UIHelper;

public class TimeResolvedToolPage extends AbstractToolPage implements IRegionListener, ITraceListener {

	private static final double STACK_OFFSET = 0.1;
	private static final String GROUP_AXIS_PATH = "/entry1/instrument/xstrip/group";
	private static final String TIME_AXIS_PATH = "/entry1/instrument/xstrip/time";

	private static final int NUMBER_OF_STRIPS = 1024;

	private TimeResolvedData timeResolvedData;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private final IObservableList  spectraRegionList = new WritableList(new ArrayList<SpectraRegion>(), SpectraRegion.class);
	private final IObservableList selectedRegionSpectraList = new WritableList(new ArrayList<SpectraRegion>(), SpectraRegion.class);
	private final IObservableList selectedSpectraList = new WritableList(new ArrayList<Object>(), Object.class);

	private SashForm rootComposite;

	private TreeViewer spectraTreeTable;
	private CheckboxTableViewer spectraRegionTableViewer;

	private IPlottingSystem plottingSystem;
	private IImageTrace imageTrace;

	private IDataset energy;


	private Binding selectedSpectraBinding;


	public TimeResolvedToolPage() {
		System.out.println("test");
	}

	@Override
	public void activate() {
		getPlottingSystem().addRegionListener(this);
		getPlottingSystem().addTraceListener(this);
		super.activate();
	}

	private final PropertyChangeListener spectraChangedListener = new PropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getPropertyName().equals(SpectraRegion.SPECTRA_CHANGED)) {
				SpectraRegion spectraRegion = (SpectraRegion) evt.getSource();
				if (spectraRegionTableViewer != null && spectraRegionTableViewer.getChecked(spectraRegion)) {
					removeTracesForRegion(spectraRegion);
					addTracesForRegion(spectraRegion);
				}
			}
		}
	};

	// TODO Validate data
	private void populateSpectra(IImageTrace image) {
		clearRegionsOnPlot();
		clearSpectra();
		IMetaData metaData = image.getData().getMetadata();
		imageTrace = image;
		String path = metaData.getFilePath();
		try {
			ILazyDataset groups = LoaderFactory.getData(path).getLazyDataset(GROUP_AXIS_PATH);
			ILazyDataset time = LoaderFactory.getData(path).getLazyDataset(TIME_AXIS_PATH);
			if (groups != null) {
				timeResolvedData = new TimeResolvedData(
						(DoubleDataset) groups.getSlice(new Slice()),
						(DoubleDataset) time.getSlice(new Slice()));
				//updateTableData();
				populateSpectraRegion();

				energy = imageTrace.getAxes().get(0);
			} else {
				clearSpectra();
			}
		} catch (Exception e) {
			logger.error("Unable to find group data, not a valid dataset", e);
		}
	}

	private void populateSpectraRegion() {
		for (IRegion region : this.getPlottingSystem().getRegions()) {
			addSpectraRegion(region);
		}
	}

	private void clearSpectra() {
		timeResolvedData = null;
		if (selectedSpectraList != null) {
			selectedSpectraList.clear();
		}
		if (spectraRegionList != null) {
			spectraRegionList.clear();
		}
		selectedRegionSpectraList.clear();
	}

	@Override
	public void deactivate() {
		if (getPlottingSystem() != null) {
			getPlottingSystem().removeRegionListener(this);
			getPlottingSystem().removeTraceListener(this);
		}

		clearRegionsOnPlot();

		super.deactivate();
	}

	private void clearRegionsOnPlot() {
		for (Object region : spectraRegionList) {
			getPlottingSystem().removeRegion(((SpectraRegion) region).getRegion());
		}
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
				populateSpectra((IImageTrace) trace);
			}
		}
	}

	private void doBinding() {
		createSpectraSelectionBinding();

		selectedSpectraList.addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						if (element instanceof Spectrum) {
							Spectrum spectrum = (Spectrum) element;
							if (!plottingSystem.isDisposed()) {
								plottingSystem.removeTrace(spectrum.getTrace());
								plottingSystem.repaint(true);
							}
							spectrum.clearTrace();
						}
					}
					@Override
					public void handleAdd(int index, Object element) {
						if (element instanceof Spectrum) {
							Spectrum spectrum = (Spectrum) element;
							if (!plottingSystem.isDisposed()) {
								ITrace trace = TimeResolvedToolPage.this.plotSpectrum(spectrum, Integer.toString(spectrum.getIndex()));
								spectrum.setTrace(trace);
								plottingSystem.repaint(true);
								spectrum.setTrace(trace);
							}
						}
					}
				});
			}
		});

		spectraRegionList.addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						SpectraRegion spectraRegion = (SpectraRegion) element;
						spectraRegion.getRegion().removeROIListener(spectraRegion);
						spectraRegion.removePropertyChangeListener(spectraChangedListener);
						if (spectraRegionTableViewer != null && spectraRegionTableViewer.getChecked(spectraRegion)) {
							removeTracesForRegion(spectraRegion);
						}
					}
					@Override
					public void handleAdd(int index, Object element) {}
				});
			}
		});

		dataBindingCtx.bindList(
				ViewerProperties.multipleSelection().observe(spectraRegionTableViewer), selectedRegionSpectraList);

		selectedRegionSpectraList.addListChangeListener(new IListChangeListener() {
			Color lastColor;
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						if (lastColor != null) {
							((SpectraRegion) element).getRegion().setRegionColor(lastColor);
						}
					}

					@Override
					public void handleAdd(int index, Object element) {
						lastColor = ((SpectraRegion) element).getRegion().getRegionColor();
						((SpectraRegion) element).getRegion().setRegionColor(Display.getCurrent().getSystemColor(SWT.COLOR_RED));
					}
				});
			}
		});
	}

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
		Action createRegion = new Action("Create Region", PlatformUI.getWorkbench().getSharedImages().getImageDescriptor(ISharedImages.IMG_TOOL_NEW_WIZARD)) {
			@Override
			public void run() {
				try {
					createRegion();
				} catch (Exception e) {
					logger.error("Unable to create region", e);
				}
			}
		};
		getSite().getActionBars().getToolBarManager().add(new Separator());
		getSite().getActionBars().getToolBarManager().add(createRegion);
	}

	IObservableFactory dataObservableFactory = new IObservableFactory() {
		@Override
		public IObservable createObservable(Object target) {
			if (target instanceof TimeResolvedData) {
				return ((TimeResolvedData) target).getTimingGroups();
			} else if (target instanceof TimingGroup) {
				return ((TimingGroup) target).getSpectra();
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
		TreeColumn column1 = new TreeColumn(spectraTree, SWT.LEFT);
		column1.setAlignment(SWT.LEFT);
		column1.setText("Name");
		column1.setWidth(130);
		TreeViewerColumn nameColumn = new TreeViewerColumn(spectraTreeTable, column1);
		nameColumn.setLabelProvider(new ColumnLabelProvider());

		TreeColumn column2 = new TreeColumn(spectraTree, SWT.RIGHT);
		column2.setAlignment(SWT.LEFT);
		column2.setText("Start time");
		column2.setWidth(60);
		TreeViewerColumn timeColumn = new TreeViewerColumn(spectraTreeTable, column2);
		timeColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public String getText(Object element) {
				if (element instanceof TimingGroup) {
					return "";
				}
				return DataHelper.roundDoubletoString(((Spectrum) element).getStartTime()) + " s";
			}
		});

		spectraTreeTable.setContentProvider(new ObservableListTreeContentProvider(dataObservableFactory, null));

		final MenuManager menuManager = new MenuManager();
		Menu menu = menuManager.createContextMenu(spectraTreeTable.getTree());
		menuManager.addMenuListener(new IMenuListener() {
			@Override
			public void menuAboutToShow(IMenuManager manager) {
				if(spectraTreeTable.getSelection().isEmpty()) {
					return;
				}
				menuManager.add(createRegionAction);
			}
		});
		menuManager.setRemoveAllWhenShown(true);
		spectraTreeTable.getTree().setMenu(menu);

		spectraTreeTable.setInput(timeResolvedData);
	}

	private void createTootbarForSpectraTable(Composite treeParent) {
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
	}

	private final Action createRegionAction = new Action("Create region") {
		@Override
		public void run() {
			if(spectraTreeTable.getSelection() instanceof IStructuredSelection) {
				IStructuredSelection selection = (IStructuredSelection) spectraTreeTable.getSelection();
				Iterator<?> iterator = selection.iterator();
				int startIndex = -1;
				int endIndex = -1;
				while (iterator.hasNext()) {
					Object object = iterator.next();
					if (object instanceof Spectrum) {
						Spectrum spectrum = (Spectrum) object;
						if (startIndex == -1) {
							startIndex = spectrum.getIndex();
							endIndex = spectrum.getIndex();
							continue;
						}
						if (spectrum.getIndex() > endIndex + 1 ) { // break in selection
							createRegionROI(startIndex, endIndex);
							startIndex = spectrum.getIndex();
							endIndex = spectrum.getIndex();
						} else {
							endIndex = spectrum.getIndex();
						}
					}
				}
				if (startIndex != -1) {
					createRegionROI(startIndex, endIndex);
				}
			}
		}

		private void createRegionROI(int startIndex, int endIndex) {
			try {
				IRegion region = createRegion();
				region.setROI(new RectangularROI(0, startIndex, 100, endIndex - startIndex + 1, 0));
				TimeResolvedToolPage.this.getPlottingSystem().addRegion(region);
			} catch (Exception e) {
				logger.error("Unable to create region", e);
			}
		}
	};

	private void createSpectraRegionTable(Composite parent) {
		spectraRegionTableViewer = CheckboxTableViewer.newCheckList(
				parent, SWT.BORDER | SWT.H_SCROLL | SWT.V_SCROLL | SWT.MULTI);
		Table spectraRegionTable = spectraRegionTableViewer.getTable();
		spectraRegionTable.setHeaderVisible(true);
		spectraRegionTable.setLinesVisible(true);
		spectraRegionTable.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		TableViewerColumn colRegionName = new TableViewerColumn(spectraRegionTableViewer, SWT.NONE);
		colRegionName.getColumn().setText("Region name");
		colRegionName.getColumn().setWidth(100);
		colRegionName.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public String getText(Object element) {
				SpectraRegion p = (SpectraRegion) element;
				return p.getRegion().getName();
			}
		});
		TableViewerColumn colStartSpectrumIndex = new TableViewerColumn(spectraRegionTableViewer, SWT.NONE);
		colStartSpectrumIndex.getColumn().setText("Start");
		colStartSpectrumIndex.getColumn().setWidth(40);
		colStartSpectrumIndex.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public String getText(Object element) {
				SpectraRegion p = (SpectraRegion) element;
				return Integer.toString(p.getStart().getIndex());
			}
		});
		TableViewerColumn colEndSpectrumIndex = new TableViewerColumn(spectraRegionTableViewer, SWT.NONE);
		colEndSpectrumIndex.getColumn().setText("End");
		colEndSpectrumIndex.getColumn().setWidth(40);
		ObservableListContentProvider contentProvider = new ObservableListContentProvider();
		IObservableSet knownElements = contentProvider.getKnownElements();

		final IObservableMap startColumn = BeanProperties.value(SpectraRegion.class,
				SpectraRegion.START).observeDetail(knownElements);
		final IObservableMap endColumn = BeanProperties.value(SpectraRegion.class,
				SpectraRegion.END).observeDetail(knownElements);

		IObservableMap[] labelMaps = {startColumn, endColumn};

		spectraRegionTableViewer.setContentProvider(contentProvider);
		spectraRegionTableViewer.setLabelProvider(new ObservableMapLabelProvider(labelMaps) {
			@Override
			public String getColumnText(Object element, int columnIndex) {
				SpectraRegion p = (SpectraRegion) element;
				switch (columnIndex) {
				case 0: return p.getRegion().getLabel();
				case 1: return Integer.toString(p.getStart().getIndex());
				case 2: return Integer.toString(p.getEnd().getIndex());
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

		spectraRegionTableViewer.addCheckStateListener(new ICheckStateListener() {
			@Override
			public void checkStateChanged(CheckStateChangedEvent event) {
				updatePlotting((SpectraRegion) event.getElement(), event.getChecked());
			}
		});
		spectraRegionTableViewer.setInput(spectraRegionList);

	}

	private void createPlotView(Composite parent) {
		Composite plotParent = new Composite(parent, SWT.BORDER);
		GridData gridData = new GridData(SWT.FILL, SWT.FILL, true, true);
		gridData.horizontalSpan = 2;
		plotParent.setLayoutData(gridData);
		plotParent.setLayout(new GridLayout(1, false));
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

	private void updatePlotting(SpectraRegion region, boolean isAdded) {
		if (isAdded) {
			addTracesForRegion(region);
		} else {
			removeTracesForRegion(region);
		}
	}

	private void addTracesForRegion(SpectraRegion region) {
		plottingSystem.getTraces();
		for(Object object : region.getSpectra()) {
			Spectrum spectrum = (Spectrum) object;
			ILineTrace trace = plotSpectrum(spectrum, spectrum.getIndex() + " " + region.getRegion().getLabel());
			region.getRegionTraces().add(trace);
		}
		plottingSystem.repaint(true);
	}

	private void removeTracesForRegion(SpectraRegion region) {
		for(Object object : region.getRegionTraces()) {
			plottingSystem.removeTrace((ITrace) object);
		}
		region.getRegionTraces().clear();
		plottingSystem.repaint(true);
	}


	private ILineTrace plotSpectrum(Spectrum spectrum, String name) {
		int index  = spectrum.getIndex();
		DoubleDataset data = (DoubleDataset) imageTrace.getData().getSlice(new int[]{index,0}, new int[]{index + 1, NUMBER_OF_STRIPS}, new int[]{1,1});
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
					getPlottingSystem().removeRegion(((SpectraRegion) iterator.next()).getRegion());
				}
			}
		}
	};

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
		addSpectraRegion(evt.getRegion());
		System.out.println("regionAdded");
	}

	private void addSpectraRegion(IRegion region) {
		SpectraRegion spectraRegion = new SpectraRegion(region, timeResolvedData);
		spectraRegion.addPropertyChangeListener(spectraChangedListener);
		region.setUserObject(spectraRegion);
		spectraRegionList.add(spectraRegion);
	}

	@Override
	public void regionRemoved(RegionEvent evt) {
		spectraRegionList.remove(evt.getRegion().getUserObject());
	}

	@Override
	public void regionsRemoved(RegionEvent evt) {}

	@Override
	public void traceCreated(TraceEvent evt) {}

	@Override
	public void traceUpdated(TraceEvent evt) {
		if (evt.getSource() instanceof IImageTrace) {
			populateSpectra((IImageTrace) evt.getSource());
		}
	}

	@Override
	public void traceAdded(TraceEvent evt) {
		if (evt.getSource() instanceof IImageTrace) {
			populateSpectra((IImageTrace) evt.getSource());
		}
	}

	@Override
	public void traceRemoved(TraceEvent evt) {
		clearSpectra();
	}

	@Override
	public void tracesUpdated(TraceEvent evt) {}

	@Override
	public void tracesRemoved(TraceEvent evet) {}

	@Override
	public void tracesAdded(TraceEvent evt) {}

	@Override
	public void traceWillPlot(TraceWillPlotEvent evt) {}

	private IRegion createRegion() throws Exception {
		IPlottingSystem plotting = TimeResolvedToolPage.this.getPlottingSystem();
		IRegion region = plotting.createRegion(RegionUtils.getUniqueName("Region", plotting), IRegion.RegionType.YAXIS);
		region.setPlotType(plotting.getPlotType());
		region.setShowLabel(true);
		return region;
	}

}