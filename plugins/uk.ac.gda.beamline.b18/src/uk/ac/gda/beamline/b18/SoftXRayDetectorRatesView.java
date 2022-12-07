/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.b18;

import java.util.Vector;

import org.eclipse.dawnsci.plotting.api.jreality.impl.PlotException;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DoubleDataset;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.ui.IPartListener2;
import org.eclipse.ui.IWorkbenchPartReference;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.NXDetectorData;
import gda.factory.Finder;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.DataSetPlotter;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.PlottingMode;

public class SoftXRayDetectorRatesView extends ViewPart implements IPartListener2{
	private Table table;
	private static final String[] titles = { "I0Drain","SampleDrain","SampleDrain/I0Drain","Element0","Element1","Element2","Element3" };
	private static final String[] formats = { "%.3f","%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f" };
	volatile boolean keepOnTrucking = true;
	private boolean amVisible = true;
	private volatile boolean runMonitoring = false;
	private volatile double refreshRate = 1.0; // seconds
	private volatile Thread updateThread;
	Scannable gmsd;
	Scannable xmapMca;
	private DataSetPlotter myPlotter;

	@Override
	public void createPartControl(Composite parent) {
		Group grpCurrentCountRates = new Group(parent, SWT.BORDER);
		grpCurrentCountRates.setText("Current count rates");
		grpCurrentCountRates.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		grpCurrentCountRates.setLayout(new GridLayout());
		table = new Table(grpCurrentCountRates, SWT.MULTI | SWT.BORDER | SWT.NO_FOCUS);
		table.setLinesVisible(true);
		table.setHeaderVisible(true);
		table.setItemCount(1);
		GridData gd = new GridData(SWT.CENTER, SWT.FILL, true, false);
		gd.heightHint = -1;
		//gd.widthHint = 400;
		table.setLayoutData(gd);

		gmsd = (Scannable) Finder.find("gmsd");
		xmapMca = (Scannable) Finder.find("xmapMca");

		final TableColumn[] columns = new TableColumn[titles.length];
		for (int i = 0; i < titles.length; i++) {
			columns[i] = new TableColumn(table, SWT.NONE);
			columns[i].setText(titles[i]);
			columns[i].setAlignment(SWT.CENTER);
		}
		for (int i = 0; i < titles.length; i++) {
			table.getItem(0).setText(i, "            "); // this string helps set the default width of the column
		}
		for (int i = 0; i < titles.length; i++) {
			table.getColumn(i).pack();
		}

		myPlotter = new DataSetPlotter(PlottingMode.ONED, grpCurrentCountRates, true);
		myPlotter.getComposite().setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		myPlotter.setXAxisLabel("Soft x ray");

		myPlotter.updateAllAppearance();
		myPlotter.refresh(false);

		keepOnTrucking = true;
		updateThread = new Thread(this::runUpdates, getClass().getSimpleName() + "_update Thread");
		updateThread.setDaemon(true);
		updateThread.start();
	}

	@Override
	public void setFocus() {

	}

	public void setI0Drain(double val) {
		String txt = String.format(formats[0], val);
		table.getItem(0).setText(0, txt);
	}

	public void setSampleDrain(double val) {
		String txt = String.format(formats[1], val);
		table.getItem(0).setText(1, txt);
	}

	public void setSamOverIoDrain(double val) {
		String txt = String.format(formats[2], val);
		table.getItem(0).setText(2, txt);
	}

	public void setElement0(double val) {
		String txt = String.format(formats[3], val);
		table.getItem(0).setText(3, txt);
	}

	public void setElement1(double val) {
		String txt = String.format(formats[4], val);
		table.getItem(0).setText(4, txt);
	}

	public void setElement2(double val) {
		String txt = String.format(formats[5], val);
		table.getItem(0).setText(5, txt);
	}

	public void setElement3(double val) {
		String txt = String.format(formats[6], val);
		table.getItem(0).setText(6, txt);
	}

	private void runUpdates() {
		while (keepOnTrucking) {
			if (!runMonitoring || !amVisible) {
				try {
					if (!keepOnTrucking){
						return;
					}
					Thread.sleep(1000);
					if (!keepOnTrucking){
						return;
					}
				} catch (InterruptedException e) {
					// end the thread
					return;
				}
			} else {

				PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
					@Override
					public void run() {
						try {


							double[] gmsdPositions = (double[]) gmsd.getPosition();

							double i0Drain = gmsdPositions[0];
							double sampleDrain = gmsdPositions[1];
							double sampleDrainOveri0Drain = sampleDrain/i0Drain;

							NXDetectorData xmapMcaPositionsNexus =  (NXDetectorData) xmapMca.getPosition();
							Double[] xmapMcaPositions = xmapMcaPositionsNexus.getDoubleVals();
							double element0 = xmapMcaPositions[0];
							double element1 = xmapMcaPositions[2];
							double element2 = xmapMcaPositions[4];
							double element3 = xmapMcaPositions[6];

							double[] values = new double[7];
							values[0] = i0Drain;
							values[1] = sampleDrain;
							values[2] = sampleDrainOveri0Drain;
							values[3] = element0;
							values[4] = element1;
							values[5] = element2;
							values[6] = element3;

							setI0Drain(values[0]);
							setSampleDrain(values[1]);
							setSamOverIoDrain(values[2]);
							setElement0(values[3]);
							setElement1(values[4]);
							setElement2(values[5]);
							setElement3(values[6]);

							Vector<DoubleDataset> dataSets = new Vector<DoubleDataset>();
							dataSets.add(DatasetFactory.createFromObject(DoubleDataset.class, values));
							myPlotter.replaceAllPlots(dataSets);
							myPlotter.updateAllAppearance();
							myPlotter.refresh(true);
						} catch (NumberFormatException e) {
							e.printStackTrace();
						} catch (DeviceException e) {
							e.printStackTrace();
						} catch (PlotException e) {
							e.printStackTrace();
						}


					}
				});

				try {
					if (!keepOnTrucking){
						return;
					}
					Thread.sleep((long) (refreshRate * 1000));
					if (!keepOnTrucking){
						return;
					}
				} catch (InterruptedException e) {
					return;
				}
			}
		}
	}

	@Override
	public void partActivated(IWorkbenchPartReference partRef) {
	}

	@Override
	public void partBroughtToTop(IWorkbenchPartReference partRef) {
	}

	@Override
	public void partClosed(IWorkbenchPartReference partRef) {
	}

	@Override
	public void partDeactivated(IWorkbenchPartReference partRef) {
	}

	@Override
	public void partHidden(IWorkbenchPartReference partRef) {
	}

	@Override
	public void partInputChanged(IWorkbenchPartReference partRef) {
	}

	@Override
	public void partOpened(IWorkbenchPartReference partRef) {
	}

	@Override
	public void partVisible(IWorkbenchPartReference partRef) {
	}

	@Override
	public void dispose() {
		keepOnTrucking = false;
		amVisible = false;
		super.dispose();
	}

	public void setRunMonitoring(boolean runMonitoring) {
		this.runMonitoring = runMonitoring;
	}
}
