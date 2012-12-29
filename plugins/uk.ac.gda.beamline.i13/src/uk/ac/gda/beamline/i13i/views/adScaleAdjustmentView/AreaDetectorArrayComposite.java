/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i13i.views.adScaleAdjustmentView;

import gda.observable.Observable;
import gda.observable.Observer;

import java.lang.reflect.Array;

import org.dawb.common.ui.plot.AbstractPlottingSystem;
import org.dawb.common.ui.plot.PlotType;
import org.dawb.common.ui.plot.PlottingFactory;
import org.dawb.common.ui.plot.trace.IImageTrace;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.RowLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.IViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.ByteDataset;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.dataset.FloatDataset;
import uk.ac.diamond.scisoft.analysis.dataset.LongDataset;
import uk.ac.diamond.scisoft.analysis.dataset.ShortDataset;

public class AreaDetectorArrayComposite extends Composite {

	private static final Logger logger = LoggerFactory.getLogger(AreaDetectorArrayComposite.class);

	private final ADController config;

	private AbstractPlottingSystem plottingSystem;

	private Observable<Integer> arrayArrayCounterObservable;
	private Observer<Integer> arrayArrayCounterObserver;

	private boolean arrayMonitoring = false;
	private Button arrayMonitoringBtn;
	private Label arrayMonitoringLbl;



	public AreaDetectorArrayComposite(IViewPart parentViewPart, Composite parent, int style, ADController config) {
		super(parent, style);
		this.config = config;

		this.setLayout(new GridLayout(2, false));
		Composite left = new Composite(this, SWT.NONE);
		GridDataFactory.fillDefaults().grab(false, true).applyTo(left);
		RowLayout layout = new RowLayout(SWT.VERTICAL);
		layout.center = true;
		layout.pack = false;
		RowLayoutFactory vertRowLayoutFactory = RowLayoutFactory.createFrom(layout);
		left.setLayout(vertRowLayoutFactory.create());
		Group stateGroup = new Group(left, SWT.NONE);
		stateGroup.setLayout(vertRowLayoutFactory.create());
		arrayMonitoringLbl = new Label(stateGroup, SWT.CENTER);
		arrayMonitoringBtn = new Button(stateGroup, SWT.PUSH | SWT.CENTER);
		arrayMonitoringBtn.addSelectionListener(new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				try {
					if (arrayMonitoring) {
						stop();
					} else {
						start();
					}
				} catch (Exception ex) {
					logger.error("Error responding to start_stop button", ex);
				}
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});
		setStarted(arrayMonitoring);


		Composite right = new Composite(this, SWT.NONE);
		GridDataFactory.fillDefaults().grab(true, true).align(SWT.FILL, SWT.FILL).applyTo(right);
		right.setLayout(new FillLayout());

		try {
			this.plottingSystem = PlottingFactory.getLightWeightPlottingSystem();
		} catch (Exception ne) {
			logger.error("Cannot create a plotting system!", ne);
			return;
		}
		plottingSystem.createPlotPart(right, "", parentViewPart.getViewSite().getActionBars(), PlotType.IMAGE,
				parentViewPart);

	}

	public void stop() throws Exception {
		config.getImageNDArray().getPluginBase().disableCallbacks();
		if (arrayArrayCounterObservable != null && arrayArrayCounterObserver != null) {
			arrayArrayCounterObservable.deleteIObserver(arrayArrayCounterObserver);
			arrayArrayCounterObserver = null;
			arrayArrayCounterObservable = null;
		}
		setStarted(false);

	}

	Job updateArrayJob;

	public void start() throws Exception {
		config.getImageNDArray().getPluginBase().enableCallbacks();
		if (arrayArrayCounterObservable == null) {
			arrayArrayCounterObservable = config.getImageNDArray().getPluginBase().createArrayCounterObservable();
		}
		if (arrayArrayCounterObserver == null) {
			arrayArrayCounterObserver = new Observer<Integer>() {

				private IImageTrace trace;

				
				@Override
				public void update(Observable<Integer> source, Integer arg) {
					if (isDisposed())
						return;
					if (updateArrayJob == null) {
						updateArrayJob = new Job("Update array") {

							AbstractDataset ads=null;
							private Runnable updateUIRunnable;
							volatile boolean runnableScheduled = false;

							@Override
							public boolean belongsTo(Object family) {
								return super.belongsTo(family);
							}

							@Override
							protected IStatus run(IProgressMonitor monitor) {
								try {
									ImageData imageData;
									imageData = config.getImageData();
									imageData.toString();
									if (imageData.data.getClass().isArray()) {
										Object object = Array.get(imageData.data, 0);
										if( object instanceof Short){
											ads = new ShortDataset((short[])(imageData.data), imageData.dimensions);
										}
										else if( object instanceof Double){
											ads = new DoubleDataset((double[])(imageData.data), imageData.dimensions);
										}
										else if( object instanceof Long){
											ads = new LongDataset((long[])(imageData.data), imageData.dimensions);
										}
										else if( object instanceof Byte){
											ads = new ByteDataset((byte[])(imageData.data), imageData.dimensions);
										}
										else if( object instanceof Float){
											ads = new FloatDataset((float[])(imageData.data), imageData.dimensions);
										} else
										{
											throw new IllegalArgumentException("Type of data not recognised: " + object.getClass().getName());
										}
										if (updateUIRunnable == null) {
											updateUIRunnable = new Runnable() {

												@Override
												public void run() {
													runnableScheduled = false;
													if( trace == null){
														trace = (IImageTrace) plottingSystem.updatePlot2D(getDataToPlot(), null, null);
														trace.setRescaleHistogram(false);
													} else {
														plottingSystem.updatePlot2D(getDataToPlot(), null, null);
													}
												}


											};
										}
										if (!runnableScheduled) {
											getDisplay().asyncExec(updateUIRunnable);
											runnableScheduled = true;
										}
									}									

								} catch (Exception e) {
									logger.error("Error reading image data", e);
								}
								return Status.OK_STATUS;
							}
							private AbstractDataset getDataToPlot() {
								return ads;
							}
						};
						updateArrayJob.setUser(false);
						updateArrayJob.setPriority(Job.SHORT);
					}
					updateArrayJob.schedule(1000); // limit to 1Hz

				}
			};
		}
		arrayArrayCounterObservable.addObserver(arrayArrayCounterObserver);
		setStarted(true);
	}

	private void setStarted(boolean b) {
		arrayMonitoring = b;
		arrayMonitoringBtn.setText(b ? "Stop" : "Start");
		arrayMonitoringLbl.setText(b ? "Running" : "Stopped");
	}

	@Override
	public void dispose() {
		try {
			stop();
		} catch (Exception e) {
			logger.error("Error stopping histogram computation", e);
		}
		if (plottingSystem != null) {
			plottingSystem.dispose();
			plottingSystem = null;
		}
		super.dispose();

	}

	/**
	 * Needed for the adapter of the parent view to return IToolPageSystem.class
	 */
	public AbstractPlottingSystem getPlottingSystem() {
		return plottingSystem;
	}

	public int getHistSize() {
		return config.getImageHistSize();
	}

	public int getImageMin() {
		return config.getImageMin();
	}

	public int getImageMax() {
		return config.getImageMax();
	}

}
