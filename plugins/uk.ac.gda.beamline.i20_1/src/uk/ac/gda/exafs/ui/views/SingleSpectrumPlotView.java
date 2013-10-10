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

package uk.ac.gda.exafs.ui.views;

import gda.scan.ede.datawriters.EdeAsciiFileWriter;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.File;
import java.util.List;
import java.util.Vector;

import org.dawnsci.plotting.api.IPlottingSystem;
import org.dawnsci.plotting.api.PlotType;
import org.dawnsci.plotting.api.PlottingFactory;
import org.dawnsci.plotting.api.trace.ITrace;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.IDataset;
import uk.ac.diamond.scisoft.analysis.io.DataHolder;
import uk.ac.diamond.scisoft.analysis.io.LoaderFactory;
import uk.ac.gda.exafs.data.SingleSpectrumModel;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.perspectives.AlignmentPerspective;

import com.swtdesigner.SWTResourceManager;

public class SingleSpectrumPlotView extends ViewPart {

	public static String ID = AlignmentPerspective.SINGLE_SPECTRUM_PLOT_VIEW_ID;

	private static String DARK_NAME = "Dark";
	private static String I0_NAME = "I0";
	private static String It_NAME = "It";
	private static String Lni0it_NAME = "Ln(I0/It)";

	private IPlottingSystem plottingSystem;
	List<SelectionListener> selectionListeners = new Vector<SelectionListener>();

	@Override
	public void createPartControl(Composite parent) {
		try {
			if (plottingSystem == null) {
				plottingSystem = PlottingFactory.createPlottingSystem();
			}
		} catch (Exception e) {
			UIHelper.showError("Unable to create plotting system", e.getMessage());
			return;
		}
		Composite composite = new Composite(parent, SWT.None);
		composite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		Composite plot = new Composite(composite, SWT.None);
		plot.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		plot.setLayout(new FillLayout());
		plottingSystem.createPlotPart(plot, getTitle(),
				// unique id for plot.
				getViewSite().getActionBars(), PlotType.XY, this);

		Composite controls = new Composite(composite, SWT.None);
		controls.setBackground(SWTResourceManager.getColor(SWT.COLOR_WHITE));
		controls.setLayout(UIHelper.createGridLayoutWithNoMargin(4, false));
		controls.setLayoutData(new GridData(SWT.FILL, SWT.END, true, false));
		addCheckBoxes(controls);

		addListener();
	}

	private void addListener() {
		SingleSpectrumModel.INSTANCE.addPropertyChangeListener(SingleSpectrumModel.FILE_NAME_PROP_NAME,
				new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				Object value = evt.getNewValue();
				if (value == null) {
					return;
				}
				String fileName = (String) value;
				File file = new File(fileName);
				if (file.exists() && file.canRead()) {
					try {
						DataHolder dataHolder = LoaderFactory.getData(fileName);
						AbstractDataset strips = (AbstractDataset) dataHolder.getLazyDataset(
								EdeAsciiFileWriter.STRIP_COLUMN_NAME).getSlice();
						AbstractDataset dk = (AbstractDataset) dataHolder.getLazyDataset(
								EdeAsciiFileWriter.I0_DARK_COLUMN_NAME).getSlice();
						dk.setName(DARK_NAME);
						AbstractDataset i0 = (AbstractDataset) dataHolder.getLazyDataset(
								EdeAsciiFileWriter.I0_RAW_COLUMN_NAME).getSlice();
						i0.setName(I0_NAME);
						AbstractDataset it = (AbstractDataset) dataHolder.getLazyDataset(
								EdeAsciiFileWriter.IT_RAW_COLUMN_NAME).getSlice();
						it.setName(It_NAME);
						AbstractDataset logI0It = (AbstractDataset) dataHolder.getLazyDataset(
								EdeAsciiFileWriter.LN_I0_IT_COLUMN_NAME).getSlice();
						logI0It.setName(Lni0it_NAME);
						List<IDataset> ds = new Vector<IDataset>();
						ds.add(dk);
						ds.add(i0);
						ds.add(it);
						ds.add(logI0It);
						plottingSystem.clear();
						plottingSystem.setTitle(fileName);
						plottingSystem.createPlot1D(strips, ds, null);
						updateVisibility();
						plottingSystem.autoscaleAxes();
						PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(ID);
					} catch (Exception e) {
						UIHelper.showError("Unable to plot the data", e.getMessage());
					}
				}
			}

			private void updateVisibility() {
				for (SelectionListener listener : selectionListeners) {
					listener.widgetSelected(null);
				}
			}
		});
	}

	private void addCheckBoxes(Composite controls) {
		createButton(controls, DARK_NAME);
		createButton(controls, I0_NAME);
		createButton(controls, It_NAME);
		createButton(controls, Lni0it_NAME);
	}

	private Button createButton(Composite parent, String label) {
		Button newBtn = new Button(parent, SWT.CHECK);
		newBtn.setText(label);
		newBtn.setSelection(true);
		newBtn.setBackground(SWTResourceManager.getColor(SWT.COLOR_WHITE));
		SelectionListener dkListener = new SpectrumSelectionListener(label, newBtn);
		selectionListeners.add(dkListener);
		newBtn.addSelectionListener(dkListener);
		return newBtn;
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

	private class SpectrumSelectionListener implements SelectionListener {

		private final String label;
		private final Button btn;

		SpectrumSelectionListener(String label, Button btn) {
			this.label = label;
			this.btn = btn;
		}

		@Override
		public void widgetSelected(SelectionEvent e) {
			ITrace dkTrace = plottingSystem.getTrace(label);
			dkTrace.setVisible(btn.getSelection());
		}

		@Override
		public void widgetDefaultSelected(SelectionEvent e) {
		}
	}
}
