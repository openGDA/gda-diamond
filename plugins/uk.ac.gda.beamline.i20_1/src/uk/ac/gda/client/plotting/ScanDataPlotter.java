/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.client.plotting;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.HashMap;
import java.util.Map;

import org.dawnsci.plotting.api.IPlottingSystem;
import org.dawnsci.plotting.api.PlotType;
import org.dawnsci.plotting.api.PlottingFactory;
import org.dawnsci.plotting.api.trace.ILineTrace;
import org.eclipse.core.databinding.observable.IObservable;
import org.eclipse.core.databinding.observable.list.IListChangeListener;
import org.eclipse.core.databinding.observable.list.ListChangeEvent;
import org.eclipse.core.databinding.observable.list.ListDiffVisitor;
import org.eclipse.core.databinding.observable.masterdetail.IObservableFactory;
import org.eclipse.jface.databinding.viewers.ObservableListTreeContentProvider;
import org.eclipse.jface.viewers.AbstractTreeViewer;
import org.eclipse.jface.viewers.CheckStateChangedEvent;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jface.viewers.ICheckStateListener;
import org.eclipse.jface.viewers.ViewerCell;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.CoolBar;
import org.eclipse.swt.widgets.CoolItem;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.swt.widgets.ToolItem;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.client.plotting.model.DataNode;
import uk.ac.gda.client.plotting.model.LineTraceProvider;
import uk.ac.gda.client.plotting.model.LineTraceProvider.TraceStyleDetails;
import uk.ac.gda.exafs.ui.ResourceComposite;
import uk.ac.gda.exafs.ui.data.UIHelper;

public class ScanDataPlotter extends ResourceComposite {

	private static Logger logger = LoggerFactory.getLogger(ScanDataPlotter.class);

	private IPlottingSystem plottingSystem;

	private DataPlotterCheckedTreeViewer dataTreeViewer;
	private final DataNode rootDataNode;

	public ScanDataPlotter(Composite parent, int style, ViewPart parentView, DataNode rootDataNode) {
		super(parent, style);
		this.rootDataNode = rootDataNode;
		this.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		try {
			plottingSystem = PlottingFactory.createPlottingSystem();
		} catch (Exception e) {
			UIHelper.showError("Unable to create plotting system", e.getMessage());
			logger.error("Unable to create plotting system", e);
			return;
		}
		final SashForm composite = new SashForm(this, SWT.HORIZONTAL);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		Composite plot = new Composite(composite, SWT.None);
		plot.setLayout(new FillLayout());
		plottingSystem.createPlotPart(plot, parentView.getTitle(),
				parentView.getViewSite().getActionBars(), PlotType.XY, parentView);
		plottingSystem.getSelectedXAxis().setAxisAutoscaleTight(true);

		createDataTree(composite);
		composite.setWeights(new int[] {3, 1});
		setupDataSelection();
	}

	private void setupDataSelection() {
		rootDataNode.getChildren().addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						// TODO
					}
					@Override
					public void handleAdd(int index, Object element) {
						for (Object obj : dataTreeViewer.getCheckedElements()) {
							dataTreeViewer.updateCheckSelection(obj, false);
						}
					}
				});
			}
		});
		rootDataNode.addPropertyChangeListener(DataNode.DATA_ADDED_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(final PropertyChangeEvent evt) {
				DataNode node = (DataNode) evt.getNewValue();
				dataTreeViewer.expandToLevel(node.getParent(), AbstractTreeViewer.ALL_LEVELS);
				if (node instanceof LineTraceProvider && dataTreeViewer.getChecked(node)) {
					addTrace((LineTraceProvider) node);
				}
			}
		});

		rootDataNode.addPropertyChangeListener(DataNode.DATA_CHANGED_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(final PropertyChangeEvent evt) {
				DataNode node = (DataNode) evt.getNewValue();
				if (node instanceof LineTraceProvider && dataTreeViewer.getChecked(node)) {
					updateTrace((LineTraceProvider) node);
				}
			}
		});
	}

	private void updateTrace(LineTraceProvider lineTraceProvider) {
		ILineTrace trace = (ILineTrace) plottingSystem.getTrace(((DataNode) lineTraceProvider).getIdentifier());
		if (trace != null) {
			trace.setData(lineTraceProvider.getXAxisDataset(), lineTraceProvider.getYAxisDataset());
			plottingSystem.repaint();
		}
	}

	private void addTrace(LineTraceProvider lineTraceProvider) {
		ILineTrace trace = (ILineTrace) plottingSystem.getTrace(((DataNode) lineTraceProvider).getIdentifier());
		if (trace == null) {
			trace = plottingSystem.createLineTrace(((DataNode) lineTraceProvider).getIdentifier());
			TraceStyleDetails traceDetails = lineTraceProvider.getTraceStyleDetails();
			if (traceDetails.getColorHexValue() != null) {
				trace.setTraceColor(getTraceColor(traceDetails.getColorHexValue()));
			}
			trace.setTraceType(traceDetails.getTraceType());
			trace.setPointSize(traceDetails.getPointSize());
			trace.setPointStyle(traceDetails.getPointStyle());
			plottingSystem.addTrace(trace);
		}
		trace.setData(lineTraceProvider.getXAxisDataset(), lineTraceProvider.getYAxisDataset());
		plottingSystem.repaint();
	}

	private final Map<String, Color> nodeColors = new HashMap<String, Color>();

	private Color getTraceColor(String colorValue) {
		Color color = null;
		if (!nodeColors.containsKey(colorValue)) {
			color = UIHelper.convertHexadecimalToColor(colorValue, Display.getDefault());
			nodeColors.put(colorValue, color);
		} else {
			color = nodeColors.get(colorValue);
		}
		return color;
	}

	IObservableFactory dataObservableFactory = new IObservableFactory() {
		@Override
		public IObservable createObservable(Object target) {
			if (target instanceof LineTraceProvider) {
				if (((LineTraceProvider) target).isPlotByDefault()) {
					dataTreeViewer.updateCheckSelection(target, true);
				}
			}
			if (target instanceof DataNode) {
				return (((DataNode) target).getChildren());
			}
			return null;
		}
	};

	private void createDataTree(final SashForm parent) {
		Composite dataTreeParent = new Composite(parent, SWT.None);
		dataTreeParent.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		CoolBar composite = new CoolBar(dataTreeParent, SWT.NONE);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		CoolItem toolbarCoolItem = new CoolItem(composite, SWT.NONE);
		// TODO Do search text box
		//CoolItem filterCoolItem = new CoolItem(composite, SWT.NONE);
		ToolBar tb = new ToolBar(composite, SWT.FLAT);
		ToolItem backToolItem = new ToolItem(tb, SWT.NONE);
		backToolItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_TOOL_BACK));
		ToolItem forwardToolItem = new ToolItem(tb, SWT.NONE);
		forwardToolItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_TOOL_FORWARD));
		//		Text filterText = new Text(composite, SWT.BORDER);
		//		filterText.setText("");
		Point p = tb.computeSize(SWT.DEFAULT, SWT.DEFAULT);
		tb.setSize(p);
		Point p2 = toolbarCoolItem.computeSize(p.x, p.y);
		toolbarCoolItem.setControl(tb);
		toolbarCoolItem.setSize(p2);
		//		p = filterText.computeSize(SWT.DEFAULT, SWT.DEFAULT);
		//		filterText.setSize(p);
		//		p2 = filterCoolItem.computeSize(p.x, p.y);
		//		filterCoolItem.setControl(tb);
		//		filterCoolItem.setSize(p2);
		//		filterCoolItem.setControl(filterText);

		backToolItem.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				dataTreeViewer.collapseAll();
			}
		});

		forwardToolItem.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				dataTreeViewer.expandAll();
			}
		});

		dataTreeViewer = new DataPlotterCheckedTreeViewer(dataTreeParent);
		dataTreeViewer.getTree().setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		dataTreeViewer.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public void update(ViewerCell cell) {
				Object element = cell.getElement();
				cell.setText(element.toString());
				if (element instanceof LineTraceProvider) {
					LineTraceProvider item = ((LineTraceProvider) element);
					String color = item.getTraceStyleDetails().getColorHexValue();
					if (color != null) {
						cell.setForeground(getTraceColor(color));
					}
					return;
				}
			}
		});
		dataTreeViewer.setContentProvider(new ObservableListTreeContentProvider(dataObservableFactory, null));
		dataTreeViewer.setInput(rootDataNode);
		dataTreeViewer.addCheckStateListener(new ICheckStateListener() {
			@Override
			public void checkStateChanged(CheckStateChangedEvent event) {
				DataNode dataNode = (DataNode) event.getElement();
				updateSelection(dataNode, event.getChecked());
			}

			private void updateSelection(DataNode dataNode, boolean checked) {
				if (dataNode.getChildren() == null) {
					updateDataItemNode(dataNode, checked);
				} else {
					for (Object childDataNode : dataNode.getChildren()) {
						updateSelection((DataNode) childDataNode, checked);
					}
				}
			}
		});
	}

	private void updateDataItemNode(DataNode dataItemNode, boolean isAdded) {
		if (dataItemNode instanceof LineTraceProvider) {
			if (isAdded) {
				addTrace((LineTraceProvider) dataItemNode);
			} else {
				removeTrace(dataItemNode.getIdentifier());
			}
		}
	}

	private void removeTrace(String identifier) {
		ILineTrace trace = (ILineTrace) plottingSystem.getTrace(identifier);
		if (trace != null) {
			plottingSystem.removeTrace(trace);
		}
	}

	@Override
	protected void disposeResource() {
		plottingSystem.dispose();
		for (Color color : nodeColors.values()) {
			color.dispose();
		}
	}


}
