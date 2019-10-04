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

import java.util.ArrayDeque;
import java.util.ArrayList;

import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.observable.IObservable;
import org.eclipse.core.databinding.observable.list.IObservableList;
import org.eclipse.core.databinding.observable.list.ListDiffVisitor;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.core.databinding.observable.masterdetail.IObservableFactory;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.dawnsci.plotting.api.PlotType;
import org.eclipse.dawnsci.plotting.api.PlottingFactory;
import org.eclipse.jface.databinding.viewers.ObservableListTreeContentProvider;
import org.eclipse.jface.databinding.viewers.ViewersObservables;
import org.eclipse.jface.viewers.AbstractTreeViewer;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.CoolBar;
import org.eclipse.swt.widgets.CoolItem;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.swt.widgets.ToolItem;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.client.ResourceComposite;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.plotting.model.ITreeNode;
import uk.ac.gda.client.plotting.model.LineTraceProviderNode;
import uk.ac.gda.client.plotting.model.Node;
import uk.ac.gda.exafs.plotting.model.ExperimentRootNode;
import uk.ac.gda.exafs.plotting.model.ScanDataItemNode;
import uk.ac.gda.exafs.plotting.model.SpectraNode;

public class ScanDataPlotterComposite extends ResourceComposite {

	private static final Logger logger = LoggerFactory.getLogger(ScanDataPlotterComposite.class);

	private IPlottingSystem<Composite> plottingSystem;
	private PlotHandler plotHandler;

	private ScanDataPlotterTree dataTreeViewer;
	private final Node rootDataNode;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();
	private final IObservableList<Node> selectedNodeList = new WritableList<>(new ArrayList<>(), Node.class);

	private Binding selectionBinding;

	private boolean clearPlotOnStartOfScan = true;
	private ArrayDeque<Node> recentlyAddedSpectraList = new ArrayDeque<>();

	public ScanDataPlotterComposite(Composite parent, int style, ViewPart parentView, Node rootDataNode) {
		super(parent, style);
		this.rootDataNode = rootDataNode;
		this.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		try {
			plottingSystem = PlottingFactory.createPlottingSystem();
		} catch (Exception e) {
			UIHelper.showError("Unable to create plotting system", e);
			logger.error("Unable to create plotting system", e);
			return;
		}
		final SashForm composite = new SashForm(this, SWT.HORIZONTAL);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		Composite plot = new Composite(composite, SWT.None);
		plot.setLayout(new FillLayout());
		plottingSystem.createPlotPart(plot, parentView.getTitle(), parentView.getViewSite().getActionBars(), PlotType.XY, parentView);
		plottingSystem.getSelectedXAxis().setAxisAutoscaleTight(true);

		plotHandler = new PlotHandler(plottingSystem);

		setupDataTreeViewer(composite);
		composite.setWeights(new int[] {3, 1});
		setupRootDataNodeListeners();
	}

	private void setupRootDataNodeListeners() {
		rootDataNode.getChildren().addListChangeListener(event ->
			event.diff.accept(new ListDiffVisitor() {
				@Override
				public void handleRemove(int index, Object element) {
				}

				@Override
				public void handleAdd(int index, Object element) {
					recentlyAddedSpectraList.clear();
					if (clearPlotOnStartOfScan) {
						for (Object obj : dataTreeViewer.getCheckedElements()) {
							dataTreeViewer.updateCheckSelection(obj, false);
						}
					}
				}
			})
		);

		rootDataNode.addPropertyChangeListener(ExperimentRootNode.DATA_ADDED_PROP_NAME, event -> {
			Node node = (Node) event.getNewValue();
			// Only expand if there have been no lnI0It spectra added
			if (node instanceof SpectraNode && recentlyAddedSpectraList.isEmpty()) {
				dataTreeViewer.expandToLevel(node.getParent(), 1);

				boolean plotByDefault = false;
				if (!node.getChildren().isEmpty()) {
					plotByDefault = ((ScanDataItemNode)node.getChildren().get(0)).isPlotByDefault();
				}
				if (plotByDefault) {
					dataTreeViewer.expandToLevel(node, AbstractTreeViewer.ALL_LEVELS);
				}
			}
			if (node instanceof LineTraceProviderNode && dataTreeViewer.getChecked(node)) {
				plotHandler.addTrace((LineTraceProviderNode) node);
			}
		});

		rootDataNode.addPropertyChangeListener(ExperimentRootNode.SCAN_ADDED_PROP_NAME, event ->  {
			Node node = (Node) event.getNewValue();
			dataTreeViewer.setSelection(new StructuredSelection(node), true);
		});

		rootDataNode.addPropertyChangeListener(ExperimentRootNode.DATA_CHANGED_PROP_NAME, event -> {
			Node node = (Node) event.getNewValue();
			if (node instanceof LineTraceProviderNode && dataTreeViewer.getChecked(node)) {
				plotHandler.updateTrace((LineTraceProviderNode) node);
			}
		});
	}

	IObservableFactory<ITreeNode, IObservable> dataObservableFactory = new IObservableFactory<ITreeNode, IObservable>() {
		/** This receives the data and adds it to the plot view */
		@Override
		public IObservable createObservable(ITreeNode target) {
			if (target instanceof LineTraceProviderNode) {
				LineTraceProviderNode lineTraceNode = (LineTraceProviderNode) target;
				if (lineTraceNode.isPlotByDefault()) {
					setPlotSelectionStatus(lineTraceNode); // de-select some of the earlier plots if necessary
					dataTreeViewer.updateCheckSelection(lineTraceNode, true); // fires CheckStateChangedEvent
				}
			}
			if (target instanceof Node) {
				return (((Node) target).getChildren());
			}
			return null;
		}


		/**
		 * De-select items in tree node to reduce number of spectra that are plotted during data acquisition.
		 *
		 * @param node
		 * @since 28/9/2016
		 */
		private void setPlotSelectionStatus(Node node) {
			int maxNumSpectraToPlot = dataTreeViewer.getMaxNumberOfAcquiredSpectraToPlot();
			// Remove excess items from start of checked nodes list and de-select them in tree view
			if (recentlyAddedSpectraList.size() >= maxNumSpectraToPlot) {
				while (recentlyAddedSpectraList.size() > maxNumSpectraToPlot/2) {
					// remove node at *start* of list
					Node removedNode = recentlyAddedSpectraList.remove();
					// de-select item in tree view
					plotHandler.updateDataItemNode(removedNode, false);
					dataTreeViewer.updateCheckSelection(removedNode, false, false);
				}
			}
			recentlyAddedSpectraList.add(node); // add new node to *end* of list
		}

	};

	private void addToolBarItems(ToolBar toolbar) {
		ToolItem backToolItem = new ToolItem(toolbar, SWT.NONE);
		backToolItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_TOOL_BACK));
		backToolItem.setToolTipText("Collapse all");
		backToolItem.addListener(SWT.Selection, event -> dataTreeViewer.collapseAll());

		ToolItem forwardToolItem = new ToolItem(toolbar, SWT.NONE);
		forwardToolItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_TOOL_FORWARD));
		forwardToolItem.setToolTipText("Expand all");
		forwardToolItem.addListener(SWT.Selection, event -> dataTreeViewer.expandAll());

		ToolItem highlightOnSelectionToolItem = new ToolItem(toolbar, SWT.CHECK);
		highlightOnSelectionToolItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ELCL_SYNCED));
		highlightOnSelectionToolItem.setToolTipText("Highlight selected line trace");
		highlightOnSelectionToolItem.addListener(SWT.Selection, event -> {
			if (!((ToolItem) event.widget).getSelection()) {
				selectedNodeList.clear();
				if (selectionBinding != null) {
					dataBindingCtx.removeBinding(selectionBinding);
					selectionBinding.dispose();
					selectionBinding = null;
				}
			} else {
				selectionBinding = dataBindingCtx.bindList(ViewersObservables.observeMultiSelection(dataTreeViewer.getTreeViewer()), selectedNodeList);
			}
		});

		ToolItem clearPlotOnStartOfScanToolItem = new ToolItem(toolbar, SWT.CHECK);
		clearPlotOnStartOfScanToolItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ETOOL_CLEAR));
		clearPlotOnStartOfScanToolItem.setSelection(clearPlotOnStartOfScan);
		clearPlotOnStartOfScanToolItem.setToolTipText("Clear plot on start of scan");
		clearPlotOnStartOfScanToolItem.addListener(SWT.Selection, event -> clearPlotOnStartOfScan = ((ToolItem) event.widget).getSelection() );

		ToolItem loadDataFromFile = new ToolItem(toolbar, SWT.NONE);
		loadDataFromFile.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_OBJ_FOLDER));
		loadDataFromFile.setToolTipText("Load data from Nexus file");
		loadDataFromFile.addListener(SWT.Selection, event -> dataTreeViewer.loadNexusDataFromFile());
	}

	private void setupDataTreeViewer(final SashForm parent) {
		Composite dataTreeParent = new Composite(parent, SWT.None);
		dataTreeParent.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		CoolBar composite = new CoolBar(dataTreeParent, SWT.NONE);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		CoolItem toolbarCoolItem = new CoolItem(composite, SWT.NONE);
		ToolBar tb = new ToolBar(composite, SWT.FLAT);
		addToolBarItems(tb);

		Point p = tb.computeSize(SWT.DEFAULT, SWT.DEFAULT);
		tb.setSize(p);
		Point p2 = toolbarCoolItem.computeSize(p.x, p.y);
		toolbarCoolItem.setControl(tb);
		toolbarCoolItem.setSize(p2);

		dataTreeViewer = new ScanDataPlotterTree(dataTreeParent, rootDataNode, new ObservableListTreeContentProvider(dataObservableFactory, null));
		dataTreeViewer.setPlotHandler(plotHandler);

		selectedNodeList.addListChangeListener(event ->
			event.diff.accept(new ListDiffVisitor() {
				@Override
				public void handleRemove(int index, Object element) {
					updateSelection(element, false);
				}

				@Override
				public void handleAdd(int index, Object element) {
					updateSelection(element, true);
				}

				private void updateSelection(Object element, boolean highlighted) {
					if (element instanceof LineTraceProviderNode && dataTreeViewer.getChecked(element)) {
						LineTraceProviderNode lineTraceProvider = (LineTraceProviderNode) element;
						lineTraceProvider.setHighlighted(highlighted);
						plotHandler.removeTrace(lineTraceProvider.getIdentifier());
						plotHandler.addTrace(lineTraceProvider);
					}
				}
			})
		);
	}

	@Override
	protected void disposeResource() {
		plottingSystem.dispose();
		plotHandler.dispose();
	}

	public IPlottingSystem<Composite> getPlottingSystem() {
		return plottingSystem;
	}
}
