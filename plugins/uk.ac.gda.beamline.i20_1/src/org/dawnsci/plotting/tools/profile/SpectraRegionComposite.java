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
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;

import org.dawnsci.plotting.tools.profile.model.AvgRegionToolDataModel;
import org.dawnsci.plotting.tools.profile.model.SpectraRegionDataNode;
import org.dawnsci.plotting.tools.profile.model.ToolPageModel;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.list.IListChangeListener;
import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.ListChangeEvent;
import org.eclipse.core.databinding.observable.list.ListDiffVisitor;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.core.databinding.observable.map.IObservableMap;
import org.eclipse.core.databinding.observable.set.IObservableSet;
import org.eclipse.core.databinding.observable.set.WritableSet;
import org.eclipse.dawnsci.plotting.api.region.IRegion;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IMenuListener;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.MenuManager;
import org.eclipse.jface.databinding.viewers.ObservableListContentProvider;
import org.eclipse.jface.databinding.viewers.ObservableMapLabelProvider;
import org.eclipse.jface.databinding.viewers.ViewerProperties;
import org.eclipse.jface.databinding.viewers.ViewersObservables;
import org.eclipse.jface.viewers.CheckboxTableViewer;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.swt.widgets.ToolItem;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.PlatformUI;

import uk.ac.gda.client.UIHelper;

public class SpectraRegionComposite extends ObservableResourceComposite {

	public static final String SPECTRA_REGION_TRACE_SHOULD_ADD = "spectraRegionTraceShouldAdd";
	public static final String SPECTRA_REGION_TRACE_SHOULD_REMOVE = "spectraRegionTraceShouldRemove";

	private CheckboxTableViewer spectraRegionTableViewer;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private final IObservableList  spectraRegionList = new WritableList(new ArrayList<SpectraRegionDataNode>(), SpectraRegionDataNode.class);
	private final IObservableList selectedRegionSpectraList = new WritableList(new ArrayList<SpectraRegionDataNode>(), SpectraRegionDataNode.class);
	private final IObservableSet checkedRegionSpectraList = new WritableSet(new HashSet<SpectraRegionDataNode>(), SpectraRegionDataNode.class);

	private final ToolPageModel toolPageModel;

	public SpectraRegionComposite(Composite parent, int style, ToolPageModel toolPageModel) {
		super(parent, style);
		this.toolPageModel = toolPageModel;
		setup();
		doBinding();
	}

	public IObservableSet getCheckedRegionSpectraList() {
		return checkedRegionSpectraList;
	}


	public IObservableList getSelectedRegionSpectraList() {
		return selectedRegionSpectraList;
	}

	private void doBinding() {
		spectraRegionList.addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						SpectraRegionDataNode spectraRegion = (SpectraRegionDataNode) element;
						spectraRegion.getRegion().removeROIListener(spectraRegion);
						spectraRegion.removePropertyChangeListener(SpectraRegionDataNode.SPECTRA_CHANGED, spectraChangedListener);
						if (checkedRegionSpectraList.contains(spectraRegion)) {
							checkedRegionSpectraList.remove(spectraRegion);
							SpectraRegionComposite.this.firePropertyChange(SPECTRA_REGION_TRACE_SHOULD_REMOVE, null, spectraRegion);
						}
					}

					@Override
					public void handleAdd(int index, Object element) {
						SpectraRegionDataNode spectraRegion = (SpectraRegionDataNode) element;
						SpectraRegionComposite.this.firePropertyChange(SPECTRA_REGION_TRACE_SHOULD_ADD, null, spectraRegion);
						spectraRegion.addPropertyChangeListener(SpectraRegionDataNode.SPECTRA_CHANGED, spectraChangedListener);
						checkedRegionSpectraList.add(spectraRegion);
					}
				});
			}
		});

		dataBindingCtx.bindList(
				ViewerProperties.multipleSelection().observe(spectraRegionTableViewer), selectedRegionSpectraList);
		dataBindingCtx.bindSet(
				ViewersObservables.observeCheckedElements(spectraRegionTableViewer, SpectraRegionDataNode.class),
				checkedRegionSpectraList);
	}

	private final PropertyChangeListener spectraChangedListener = new PropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			if (evt.getPropertyName().equals(SpectraRegionDataNode.SPECTRA_CHANGED)) {
				SpectraRegionDataNode spectraRegion = (SpectraRegionDataNode) evt.getSource();
				if (spectraRegionTableViewer != null && spectraRegionTableViewer.getChecked(spectraRegion)) {
					SpectraRegionComposite.this.firePropertyChange(SPECTRA_REGION_TRACE_SHOULD_REMOVE, null, spectraRegion);
					SpectraRegionComposite.this.firePropertyChange(SPECTRA_REGION_TRACE_SHOULD_ADD, null, spectraRegion);
				}
			}
		}
	};

	private void setup() {
		setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));

		createTootbarForSpectraRegionTable(this);

		spectraRegionTableViewer = CheckboxTableViewer.newCheckList(
				this, SWT.BORDER | SWT.H_SCROLL | SWT.V_SCROLL | SWT.MULTI);
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
				case 3: return spectraRegionToolDataModel.toString();
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

		spectraRegionTableViewer.setInput(spectraRegionList);
	}

	public IObservableList getSpectraRegionList() {
		return spectraRegionList;
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
		unSelectAllToolItem.setToolTipText("Clear region selection");
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

		final ToolItem saveNexusToolItem = new ToolItem(toolBar, SWT.PUSH);
		saveNexusToolItem.setText("");
		saveNexusToolItem.setToolTipText("Export selected regions");
		saveNexusToolItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ETOOL_SAVEAS_EDIT));
		saveNexusToolItem.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				TimeResolvedToolPageHelper timeResolvedToolPageHelper = new TimeResolvedToolPageHelper();
				timeResolvedToolPageHelper.averageSpectrumAndExport(toolPageModel.getDataFile(), saveNexusToolItem.getDisplay(), (SpectraRegionDataNode[]) spectraRegionList.toArray(new SpectraRegionDataNode[]{}));
			}
		});
	}

	private void fireCheckSelectionEvent(Event event, TableItem item) {
		SelectionEvent checkEvent = new SelectionEvent(event);
		checkEvent.detail = SWT.CHECK;
		checkEvent.item = item;
		spectraRegionTableViewer.handleSelect(checkEvent);
	}

	private final Action removeRegionAction = new Action("Remove") {
		@Override
		public void run() {
			if(spectraRegionTableViewer.getSelection() instanceof IStructuredSelection) {
				IStructuredSelection selection = (IStructuredSelection) spectraRegionTableViewer.getSelection();
				Iterator<?> iterator = selection.iterator();
				while (iterator.hasNext()) {
					toolPageModel.getDataImagePlotting().removeRegion(((SpectraRegionDataNode) iterator.next()).getRegion());
				}
			}
		}
	};

	public void populateSpectraRegion(List<IRegion> plottedRegions) {
		for (IRegion region : toolPageModel.getDataImagePlotting().getRegions()) {
			if (plottedRegions.contains(region)) {
				if (region.getUserObject() != null) {
					SpectraRegionDataNode spectraRegion;
					if (region.getUserObject() instanceof AvgRegionToolDataModel) {
						spectraRegion = new AvgRegionToolDataModel(region, toolPageModel.getTimeResolvedData());
					}
					else {
						spectraRegion = new SpectraRegionDataNode(region, toolPageModel.getTimeResolvedData());
					}
					spectraRegionList.add(spectraRegion);
				}
			}
		}
	}

	public void clearRegionData() {

	}

	@Override
	protected void disposeResource() {
		// TODO Auto-generated method stub
	}
}
