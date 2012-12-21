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

import org.dawb.common.ui.plot.AbstractPlottingSystem;
import org.dawb.common.ui.plot.PlotType;
import org.dawb.common.ui.plot.PlottingFactory;
import org.dawb.common.ui.plot.region.IROIListener;
import org.dawb.common.ui.plot.region.IRegion;
import org.dawb.common.ui.plot.region.ROIEvent;
import org.dawb.common.ui.plot.region.RegionUtils;
import org.dawb.common.ui.plot.trace.ILineTrace;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.draw2d.ColorConstants;
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

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.roi.RectangularROI;

public class ADScaleAdjustmentComposite extends Composite {
	private static final Logger logger = LoggerFactory.getLogger(ADScaleAdjustmentComposite.class);

	private final ScaleAdjustmentViewConfig config;

	private AbstractPlottingSystem plottingSystem;

	private ILineTrace histogramTrace = null;
	private DoubleDataset histogramXAxisRange = null;
	private Observable<Integer> statsArrayCounterObservable;
	private Observer<Integer> statsArrayCounterObserver;

	private boolean histogramMonitoring = false;
	private Button histogramMonitoringBtn;
	private Label histogramMonitoringLbl;

	int histSize = 100; // number of points in the histogram
	int histMin = 0;//
	int histMax = 65535;

	private String mpegROIRegionName;
	private Observable<Double> mpegProcOffsetObservable;
	private Observable<Double> mpegProcScaleObservable;
	private Observer<Double> mpegProcObserver;

	/**
	 * To prevent cycles of Gui updates Epics, Epics update GUI, Gui updates EPICS... only update the GUI if the values
	 * from EPICS do not match those used to last update the GUI
	 */
	long current_mpegROIMin = Long.MIN_VALUE;
	long current_mpegROIMax = Long.MAX_VALUE;
	private RectangularROI current_mpegROI;

	private double getMPEGProcOffset() throws Exception {
		return config.ndProc.getOffset();
	}

	private double getMPEGProcScale() throws Exception {
		return config.ndProc.getScale();
	}

	protected void updateROIInGuiThread() {
		getDisplay().asyncExec(new Runnable() {
			@Override
			public void run() {
				try {
					createOrUpdateROI();
				} catch (Exception e) {
					logger.error("Error responding to external update of scale and offset", e);
				}
			}
		});
	}

	protected void createOrUpdateROI() throws Exception {
		double scale = ADScaleAdjustmentComposite.this.getMPEGProcScale();
		double offset = ADScaleAdjustmentComposite.this.getMPEGProcOffset();
		RectangularROI roi;
		long min = (long) -offset;
		long max = (long) (255.0 / scale + min);
		roi = current_mpegROI;
		if (min == current_mpegROIMin && max == current_mpegROIMax && roi != null)
			return;
		if (roi == null) {
			roi = new RectangularROI();
		}
		roi.setPoint(new double[] { min, 0 });
		roi.setLengths(new double[] { max - min, 0 });

		if (mpegROIRegionName == null) {
			mpegROIRegionName = RegionUtils.getUniqueName("Scaling Range", getPlottingSystem());
		}
		IRegion iRegion = getPlottingSystem().getRegion(mpegROIRegionName);
		if (iRegion == null) {
			iRegion = getPlottingSystem().createRegion(mpegROIRegionName, IRegion.RegionType.XAXIS);
			iRegion.addROIListener(new IROIListener() {

				@Override
				public void roiDragged(ROIEvent evt) {
					try {
						handleROIChangeEvent(evt);
					} catch (Exception e) {
						logger.error("Error handling change to scaling roi", e);
					}
				}

				private void handleROIChangeEvent(ROIEvent evt) throws Exception {
					final IRegion region = (IRegion) evt.getSource();
					RectangularROI roi = (RectangularROI) region.getROI();
					double min = roi.getPointX();
					double max = min + roi.getLengths()[0];
					double offset = -min;
					double scale = 255.0 / (max - min);
					ADScaleAdjustmentComposite.this.config.ndProc.setScale(scale);
					ADScaleAdjustmentComposite.this.config.ndProc.setOffset(offset);
					ADScaleAdjustmentComposite.this.config.ndProc.setEnableOffsetScale(1);
				}

				@Override
				public void roiChanged(ROIEvent evt) {
					try {
						handleROIChangeEvent(evt);
					} catch (Exception e) {
						logger.error("Error handling change to scaling roi", e);
					}
				}
			});
			mpegProcOffsetObservable = ADScaleAdjustmentComposite.this.config.ndProc.createOffsetObservable();
			mpegProcScaleObservable = ADScaleAdjustmentComposite.this.config.ndProc.createScaleObservable();
			mpegProcObserver = new Observer<Double>() {

				@Override
				public void update(Observable<Double> source, Double arg) {
					updateROIInGuiThread();
				}
			};
			mpegProcOffsetObservable.addObserver(mpegProcObserver);
			mpegProcScaleObservable.addObserver(mpegProcObserver);

			iRegion.setVisible(true);
			getPlottingSystem().addRegion(iRegion);
		}
		iRegion.setROI(roi);
		current_mpegROI = roi;
		current_mpegROIMax = max;
		current_mpegROIMin = min;
	}

	public ADScaleAdjustmentComposite(IViewPart parentViewPart, Composite parent, int style,
			ScaleAdjustmentViewConfig config) {
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
		histogramMonitoringLbl = new Label(stateGroup, SWT.CENTER);
		histogramMonitoringBtn = new Button(stateGroup, SWT.PUSH | SWT.CENTER);
		histogramMonitoringBtn.addSelectionListener(new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				try {
					if (histogramMonitoring) {
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
		setStarted(histogramMonitoring);

		Composite right = new Composite(this, SWT.NONE);
		GridDataFactory.fillDefaults().grab(true, true).align(SWT.FILL, SWT.FILL).applyTo(right);
		right.setLayout(new FillLayout());

		try {
			this.plottingSystem = PlottingFactory.getLightWeightPlottingSystem();
		} catch (Exception ne) {
			logger.error("Cannot create a plotting system!", ne);
			return;
		}
		plottingSystem.createPlotPart(right, "", parentViewPart.getViewSite().getActionBars(), PlotType.PT1D,
				parentViewPart);
		plottingSystem.setXfirst(true);

		try {
			createOrUpdateROI();
		} catch (Exception e1) {
			logger.error("Error creating region", e1);
		}
	}

	public void stop() throws Exception {
		config.ndStats.setComputeHistogram(0);
		if (statsArrayCounterObservable != null && statsArrayCounterObserver != null) {
			statsArrayCounterObservable.deleteIObserver(statsArrayCounterObserver);
			statsArrayCounterObserver = null;
			statsArrayCounterObservable = null;
		}
		setStarted(false);

	}

	public void start() throws Exception {
		config.ndStats.setHistSize(histSize);
		config.ndStats.setHistMin(histMin);
		config.ndStats.setHistMax(histMax);
		config.ndStats.getPluginBase().enableCallbacks();
		config.ndStats.setComputeHistogram(1);
		double step = (histMax - histMin) / histSize;
		double[] range = new double[histSize];
		range[0] = histMin;
		for (int i = 1; i < histSize; i++) {
			range[i] = range[i - 1] + step;
		}
		histogramXAxisRange = new DoubleDataset(range);
		histogramXAxisRange.setName("Counts");
		if (statsArrayCounterObservable == null) {
			statsArrayCounterObservable = config.ndStats.getPluginBase().createArrayCounterObservable();
		}
		if (statsArrayCounterObserver == null) {
			statsArrayCounterObserver = new Observer<Integer>() {

				private Job job;

				@Override
				public void update(Observable<Integer> source, Integer arg) {
					if (isDisposed())
						return;
					if (job == null) {
						job = new Job("Update histogram") {

							private Runnable updateUIRunnable;
							volatile boolean runnableScheduled = false;

							@Override
							public boolean belongsTo(Object family) {
								return super.belongsTo(family);
							}

							@Override
							protected IStatus run(IProgressMonitor monitor) {
								double[] histogram_RBV;
								try {
									histogram_RBV = config.ndStats.getHistogram_RBV(histSize);
								} catch (Exception e) {
									logger.error("Error getting histogram", e);
									return Status.OK_STATUS;
								}

								if (histogram_RBV.length != histogramXAxisRange.getSize()) {
									logger.error("Length of histogram does not match histSize");
									return Status.OK_STATUS;
								}
								DoubleDataset ds = new DoubleDataset(histogram_RBV);

								ds.setName("Number in bin");

								if (histogramTrace == null) {
									histogramTrace = plottingSystem.createLineTrace("PROFILE");
									histogramTrace.setTraceColor(ColorConstants.blue);
								}

								histogramTrace.setData(histogramXAxisRange, ds);

								if (updateUIRunnable == null) {
									updateUIRunnable = new Runnable() {

										@Override
										public void run() {
											runnableScheduled = false;
											boolean firstTime = plottingSystem.getTrace("PROFILE") == null;
											if (firstTime) {
												plottingSystem.addTrace(histogramTrace);
												plottingSystem.setTitle("");
											}
											plottingSystem.repaint();
											plottingSystem.setTitle("");
											plottingSystem.getSelectedYAxis().setFormatPattern("#####");
											plottingSystem.getSelectedXAxis().setFormatPattern("#####");
										}

									};
								}
								if (!runnableScheduled) {
									getDisplay().asyncExec(updateUIRunnable);
									runnableScheduled = true;
								}
								return Status.OK_STATUS;
							}
						};
						job.setUser(false);
						job.setPriority(Job.SHORT);
					}
					job.schedule(200); // limit to 5Hz

				}
			};
		}
		statsArrayCounterObservable.addObserver(statsArrayCounterObserver);
		setStarted(true);
	}

	private void setStarted(boolean b) {
		histogramMonitoring = b;
		histogramMonitoringBtn.setText(b ? "Stop" : "Start");
		histogramMonitoringLbl.setText(b ? "Running" : "Stopped");
	}

	@Override
	public void dispose() {
		try {
			stop();
		} catch (Exception e) {
			logger.error("Error stopping histogram computation", e);
		}
		if (mpegProcObserver != null) {
			if (mpegProcOffsetObservable != null && mpegProcObserver != null)
				mpegProcOffsetObservable.deleteIObserver(mpegProcObserver);
			if (mpegProcScaleObservable != null && mpegProcObserver != null)
				mpegProcScaleObservable.deleteIObserver(mpegProcObserver);
			mpegProcObserver = null;
		}
		mpegProcOffsetObservable = null;
		mpegProcScaleObservable = null;
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

}
