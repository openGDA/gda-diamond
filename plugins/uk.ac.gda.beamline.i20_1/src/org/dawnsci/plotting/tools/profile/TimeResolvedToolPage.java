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
import java.util.List;

import org.dawb.common.ui.widgets.ActionBarWrapper;
import org.dawnsci.plotting.api.IPlottingSystem;
import org.dawnsci.plotting.api.PlotType;
import org.dawnsci.plotting.api.PlottingFactory;
import org.dawnsci.plotting.api.region.IRegion;
import org.dawnsci.plotting.api.region.IRegionListener;
import org.dawnsci.plotting.api.region.RegionEvent;
import org.dawnsci.plotting.api.region.RegionUtils;
import org.dawnsci.plotting.api.tool.AbstractToolPage;
import org.dawnsci.plotting.api.trace.IImageTrace;
import org.dawnsci.plotting.api.trace.ITrace;
import org.dawnsci.plotting.api.trace.ITraceListener;
import org.dawnsci.plotting.api.trace.TraceEvent;
import org.dawnsci.plotting.api.trace.TraceWillPlotEvent;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateListStrategy;
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
import org.eclipse.jface.action.Separator;
import org.eclipse.jface.databinding.viewers.ObservableListContentProvider;
import org.eclipse.jface.databinding.viewers.ObservableListTreeContentProvider;
import org.eclipse.jface.databinding.viewers.ObservableMapLabelProvider;
import org.eclipse.jface.databinding.viewers.ViewerProperties;
import org.eclipse.jface.viewers.CheckboxTableViewer;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.Tree;
import org.eclipse.swt.widgets.TreeColumn;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.dataset.IDataset;
import uk.ac.diamond.scisoft.analysis.dataset.ILazyDataset;
import uk.ac.diamond.scisoft.analysis.dataset.Slice;
import uk.ac.diamond.scisoft.analysis.io.IMetaData;
import uk.ac.diamond.scisoft.analysis.io.LoaderFactory;

public class TimeResolvedToolPage extends AbstractToolPage implements IRegionListener, ITraceListener {

	private static final String GROUP_AXIS_PATH = "/entry1/instrument/xstrip/group";
	private static final String TIME_AXIS_PATH = "/entry1/instrument/xstrip/time";
	protected static final int NUMBER_OF_STRIPS = 1024;

	private boolean isActivated;
	private TimeResolvedData timeResolvedData;

	private IObservableList spectraRegionList;
	private DataBindingContext dataBindingCtx;
	private SashForm rootComposite;
	private TreeViewer spectraTreeTable;
	private IImageTrace imageTrace;

	private CheckboxTableViewer spectraRegionTableViewer;
	private IPlottingSystem plottingSystem;
	private final IObservableList selectedSpectraList = new WritableList(new ArrayList<Spectrum>(), Spectrum.class);
	private final IObservableList selectedRegionSpectraList = new WritableList(new ArrayList<SpectraRegion>(), SpectraRegion.class);

	@Override
	public void activate() {
		super.activate();
		if (isActivated) {
			return;
		}
		dataBindingCtx = new DataBindingContext();
		spectraRegionList = new WritableList(new ArrayList<SpectraRegion>(), SpectraRegion.class);
		if (getPlottingSystem() != null && getPlottingSystem().getTraces().size() == 1) {
			getPlottingSystem().addRegionListener(this);
			ITrace trace = getPlottingSystem().getTraces().iterator().next();
			if (trace instanceof IImageTrace) {
				populateSpectra((IImageTrace) trace);
			}
		}

		getPlottingSystem().addTraceListener(this);
		spectraRegionList.addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						SpectraRegion spectraRegion = (SpectraRegion) element;
						spectraRegion.getRegion().removeROIListener(spectraRegion);
						spectraRegion.removePropertyChangeListener(spectraChangedListener);
					}
					@Override
					public void handleAdd(int index, Object element) {
						SpectraRegion spectraRegion = (SpectraRegion) element;
						spectraRegion.addPropertyChangeListener(spectraChangedListener);
						updateRegionSelection(spectraRegion);
					}
				});
			}
		});
		isActivated = true;
	}

	private final PropertyChangeListener spectraChangedListener = new PropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getPropertyName().equals(SpectraRegion.START)) {
				updateRegionSelection((SpectraRegion) evt.getSource());
			}
		}
	};

	private void updateRegionSelection(SpectraRegion spectraRegion) {
		selectedRegionSpectraList.clear();
		selectedRegionSpectraList.add(spectraRegion);
	}

	// TODO Validate data
	private void populateSpectra(IImageTrace image) {
		clearSpecta();
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
				updateTableData();
				populateSpectraRegion();
			} else {
				clearSpecta();
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

	private void clearSpecta() {
		timeResolvedData = null;
		if (spectraRegionList != null) {
			spectraRegionList.clear();
		}
		updateTableData();
	}

	private void updateTableData() {
		selectedSpectraList.clear();
		selectedRegionSpectraList.clear();
		if (spectraTreeTable != null && !spectraTreeTable.getTree().isDisposed()) {
			spectraTreeTable.setInput(timeResolvedData);
		}
		if (spectraRegionTableViewer != null && !spectraRegionTableViewer.getTable().isDisposed()) {
			spectraRegionTableViewer.setInput(spectraRegionList);
		}
	}

	@Override
	public void deactivate() {
		super.deactivate();
		if (getPlottingSystem() != null) {
			getPlottingSystem().removeRegionListener(this);
			getPlottingSystem().removeTraceListener(this);
		}
		clearSpecta();
		isActivated = false;
	}

	@Override
	public ToolPageRole getToolPageRole() {
		return ToolPageRole.ROLE_2D;
	}

	@Override
	public void createControl(Composite parent) {
		createActions();
		rootComposite = new SashForm(parent, SWT.VERTICAL);
		rootComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		final SashForm tableComposite = new SashForm(rootComposite, SWT.HORIZONTAL);
		tableComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		createSpectraTable(tableComposite);
		createSpectraRegionTable(tableComposite);

		tableComposite.setWeights(new int[]{1,1});
		createPlotView(rootComposite);
		rootComposite.setWeights(new int[]{1,3});
	}

	private void createActions() {
		createToolPageActions();
		Action createRegion = new Action("Create Region") {
			@Override
			public void run() {
				IPlottingSystem plotting = TimeResolvedToolPage.this.getPlottingSystem();
				try {
					IRegion region = plotting.createRegion(RegionUtils.getUniqueName("Region", plotting), IRegion.RegionType.YAXIS);
					region.setPlotType(plotting.getPlotType());
				} catch (Exception e) {
					logger.error("Unable to create region", e);
				}
			}
		};
		getSite().getActionBars().getToolBarManager().add(createRegion);
		getSite().getActionBars().getToolBarManager().add(new Separator());
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
		Tree spectraTree = new Tree(parent, SWT.MULTI | SWT.BORDER | SWT.H_SCROLL | SWT.V_SCROLL);
		spectraTree.setHeaderVisible(true);
		spectraTree.setLinesVisible(true);
		spectraTree.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		spectraTreeTable = new TreeViewer(spectraTree);
		TreeColumn column1 = new TreeColumn(spectraTree, SWT.LEFT);
		column1.setAlignment(SWT.LEFT);
		column1.setText("Name");
		column1.setWidth(120);
		TreeColumn column2 = new TreeColumn(spectraTree, SWT.RIGHT);
		column2.setAlignment(SWT.LEFT);
		column2.setText("Time");
		column2.setWidth(60);

		spectraTreeTable.setLabelProvider(new ColumnLabelProvider() {

		});
		spectraTreeTable.setContentProvider(new ObservableListTreeContentProvider(dataObservableFactory, null));

		dataBindingCtx.bindList(
				ViewerProperties.multipleSelection().observe(spectraTreeTable), selectedSpectraList,
				new UpdateListStrategy(UpdateListStrategy.POLICY_NEVER),
				new UpdateListStrategy());

		selectedSpectraList.addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				plottingSystem.clear();

				IDataset energy = imageTrace.getAxes().get(0);
				List<DoubleDataset> dataList = new ArrayList<DoubleDataset>();
				for(Object object : selectedSpectraList) {
					int index  = ((Spectrum) object).getIndex();
					DoubleDataset data = (DoubleDataset) imageTrace.getData().getSlice(new int[]{index,0}, new int[]{index + 1, NUMBER_OF_STRIPS}, new int[]{1,1});
					dataList.add(data);
				}
				plottingSystem.createPlot1D(energy, dataList, null);
			}
		});
		spectraTreeTable.setInput(timeResolvedData);
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
			}
		} catch (Exception e) {
			logger.error("Unable to create plotting system", e);
			return;
		}
	}

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

		dataBindingCtx.bindList(
				ViewerProperties.multipleSelection().observe(spectraRegionTableViewer), selectedRegionSpectraList);

		spectraRegionTableViewer.setInput(spectraRegionList);

		selectedRegionSpectraList.addListChangeListener(new IListChangeListener() {

			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						selectedSpectraList.removeAll(((SpectraRegion) element).getSpectra());
					}

					@Override
					public void handleAdd(int index, Object element) {
						selectedSpectraList.clear();
						selectedSpectraList.addAll(((SpectraRegion) element).getSpectra());
					}
				});
			}
		});
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
		addSpectraRegion(evt.getRegion());
		System.out.println("regionAdded");
	}

	private void addSpectraRegion(IRegion region) {
		SpectraRegion spectraRegion = new SpectraRegion(region, timeResolvedData);
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
		clearSpecta();
	}

	@Override
	public void tracesUpdated(TraceEvent evt) {}

	@Override
	public void tracesRemoved(TraceEvent evet) {}

	@Override
	public void tracesAdded(TraceEvent evt) {}

	@Override
	public void traceWillPlot(TraceWillPlotEvent evt) {}

}