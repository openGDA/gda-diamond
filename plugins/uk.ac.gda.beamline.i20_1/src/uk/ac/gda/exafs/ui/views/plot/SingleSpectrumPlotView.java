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

package uk.ac.gda.exafs.ui.views.plot;

import java.util.List;
import java.util.Vector;

import org.dawnsci.plotting.api.IPlottingSystem;
import org.dawnsci.plotting.api.PlotType;
import org.dawnsci.plotting.api.PlottingFactory;
import org.dawnsci.plotting.api.trace.ILineTrace;
import org.eclipse.core.databinding.observable.IObservable;
import org.eclipse.core.databinding.observable.list.IListChangeListener;
import org.eclipse.core.databinding.observable.list.ListChangeEvent;
import org.eclipse.core.databinding.observable.list.ListDiffVisitor;
import org.eclipse.core.databinding.observable.masterdetail.IObservableFactory;
import org.eclipse.jface.databinding.viewers.ObservableSetTreeContentProvider;
import org.eclipse.jface.viewers.CheckStateChangedEvent;
import org.eclipse.jface.viewers.CheckboxTreeViewer;
import org.eclipse.jface.viewers.ICheckStateListener;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.perspectives.AlignmentPerspective;
import uk.ac.gda.exafs.ui.views.plot.model.DataNode;
import uk.ac.gda.exafs.ui.views.plot.model.DatasetNode;
import uk.ac.gda.exafs.ui.views.plot.model.PlotDataHolder;

public class SingleSpectrumPlotView extends ViewPart {

	public static String ID = AlignmentPerspective.SINGLE_SPECTRUM_PLOT_VIEW_ID;

	private static Logger logger = LoggerFactory.getLogger(SingleSpectrumPlotView.class);

	private IPlottingSystem plottingSystem;
	List<SelectionListener> selectionListeners = new Vector<SelectionListener>();

	private CheckboxTreeViewer dataTreeViewer;

	@Override
	public void createPartControl(Composite parent) {
		try {
			if (plottingSystem == null) {
				plottingSystem = PlottingFactory.createPlottingSystem();
			}
		} catch (Exception e) {
			UIHelper.showError("Unable to create plotting system", e.getMessage());
			logger.error("Unable to create plotting system", e);
			return;
		}

		PlotDataHolder.INSTANCE.initialise();
		final SashForm composite = new SashForm(parent, SWT.HORIZONTAL);

		Composite plot = new Composite(composite, SWT.None);
		plot.setLayout(new FillLayout());
		plottingSystem.createPlotPart(plot, getTitle(),
				// unique id for plot.
				getViewSite().getActionBars(), PlotType.XY, this);

		createDataTree(composite);
		composite.setWeights(new int[] {3, 1});
		setupDataSelection();
	}

	private void setupDataSelection() {
		PlotDataHolder.INSTANCE.getSelectedNodes().addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						removeFromPlot((DataNode) element);
					}
					@Override
					public void handleAdd(int index, Object element) {
						addToPlot((DataNode) element);
					}
				});
			}
		});
	}

	private void addToPlot(DataNode element) {
		ILineTrace lineTrace = plottingSystem.createLineTrace("Data");
		element.setLineTrace(lineTrace);
		plottingSystem.addTrace(lineTrace);
	}

	private void removeFromPlot(DataNode element) {
		if (element.getLineTrace() != null) {
			plottingSystem.removeTrace(element.getLineTrace());
			element.clearLineTrace();
		}
	}

	private final Object root = new Object();

	IObservableFactory dataObservableFactory = new IObservableFactory() {
		@Override
		public IObservable createObservable(Object target) {
			if (target == root) {
				return PlotDataHolder.INSTANCE.getDataset();
			} else if (target instanceof DatasetNode) {
				return (((DatasetNode) target).getDataset());
			}
			return null;
		}
	};

	private void createDataTree(final SashForm parent) {
		Composite dataTreeParent = new Composite(parent, SWT.None);
		dataTreeParent.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		dataTreeViewer = new CheckboxTreeViewer(dataTreeParent);
		dataTreeViewer.getTree().setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		dataTreeViewer.setLabelProvider(new LabelProvider() {

			@Override
			public String getText(Object element) {
				return super.getText(element);
			}

		});
		dataTreeViewer.setContentProvider(new ObservableSetTreeContentProvider(dataObservableFactory, null));
		dataTreeViewer.setInput(root);
		dataTreeViewer.addCheckStateListener(new ICheckStateListener() {
			@Override
			public void checkStateChanged(CheckStateChangedEvent event) {
				dataTreeViewer.setSubtreeChecked(event.getElement(), event.getChecked());
				Object element = event.getElement();
				if (element instanceof DatasetNode) {
					if (event.getChecked()) {
						PlotDataHolder.INSTANCE.getSelectedNodes().addAll(((DatasetNode) element).getDataset());
					} else {
						PlotDataHolder.INSTANCE.getSelectedNodes().removeAll(((DatasetNode) element).getDataset());
					}
				} else if (element instanceof DataNode) {
					if (event.getChecked()) {
						PlotDataHolder.INSTANCE.getSelectedNodes().add(element);
					} else {
						PlotDataHolder.INSTANCE.getSelectedNodes().remove(element);
					}
				}
			}
		});
	}

	@Override
	public void setFocus() {
		plottingSystem.setFocus();
	}

	@Override
	public void dispose() {
		plottingSystem.dispose();
		super.dispose();
	}

}
