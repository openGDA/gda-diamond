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

package uk.ac.gda.beamline.i13i.ADViewer.composites;

import gda.observable.Observable;
import gda.observable.Observer;

import org.dawb.common.ui.plot.AbstractPlottingSystem;
import org.dawb.common.ui.plot.IAxis;
import org.dawb.common.ui.plot.PlotType;
import org.dawb.common.ui.plot.PlottingFactory;
import org.dawb.common.ui.plot.region.IROIListener;
import org.dawb.common.ui.plot.region.IRegion;
import org.dawb.common.ui.plot.region.ROIEvent;
import org.dawb.common.ui.plot.region.RegionUtils;
import org.dawb.common.ui.plot.trace.ILineTrace;
import org.eclipse.core.commands.Command;
import org.eclipse.core.commands.ExecutionEvent;
import org.eclipse.core.commands.IParameter;
import org.eclipse.core.commands.Parameterization;
import org.eclipse.core.commands.ParameterizedCommand;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.draw2d.ColorConstants;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.RowLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
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
import org.eclipse.ui.commands.ICommandService;
import org.eclipse.ui.handlers.IHandlerService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.roi.RectangularROI;
import uk.ac.gda.beamline.i13i.ADViewer.ADController;

import org.eclipse.swt.layout.GridData;

public class Histogram extends Composite {
	private static final String PROFILE = "PROFILE";

	private static final Logger logger = LoggerFactory.getLogger(Histogram.class);

	private final ADController config;

	private AbstractPlottingSystem plottingSystem;

	private ILineTrace histogramTrace = null;
	private DoubleDataset histogramXAxisRange = null;
	private Observable<Integer> statsArrayCounterObservable;
	private Observer<Integer> statsArrayCounterObserver;

	private boolean histogramMonitoring = false;
	private Button histogramMonitoringBtn;
	private Label histogramMonitoringLbl;

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

	public Histogram(final IViewPart parentViewPart, Composite parent, int style, ADController config) {
		super(parent, style);
		this.config = config;

		this.setLayout(new GridLayout(2, false));
		Composite left = new Composite(this, SWT.NONE);
		GridDataFactory.fillDefaults().grab(false, true).applyTo(left);
		RowLayout layout = new RowLayout(SWT.VERTICAL);
		layout.center = true;
		layout.pack = false;
		RowLayoutFactory vertRowLayoutFactory = RowLayoutFactory.createFrom(layout);
		left.setLayout(new GridLayout(1, false));
		
		statusComposite = new IOCStatus(left, SWT.NONE);
		GridData gd_statusComposite = new GridData(SWT.LEFT, SWT.CENTER, false, false, 1, 1);
		gd_statusComposite.widthHint = 164;
		statusComposite.setLayoutData(gd_statusComposite);
		Group stateGroup = new Group(left, SWT.NONE);
		stateGroup.setText("Profile View");
		GridData gd_stateGroup = new GridData(SWT.FILL, SWT.CENTER, false, false, 1, 1);
		gd_stateGroup.widthHint = 158;
		stateGroup.setLayoutData(gd_stateGroup);
		stateGroup.setLayout(new GridLayout(2, false));
		histogramMonitoringLbl = new Label(stateGroup, SWT.CENTER);
		GridData gd_histogramMonitoringLbl = new GridData(SWT.LEFT, SWT.CENTER, false, false, 1, 1);
		gd_histogramMonitoringLbl.widthHint = 77;
		histogramMonitoringLbl.setLayoutData(gd_histogramMonitoringLbl);
		histogramMonitoringBtn = new Button(stateGroup, SWT.PUSH | SWT.CENTER);
		GridData gd_histogramMonitoringBtn = new GridData(SWT.CENTER, SWT.CENTER, true, false, 1, 1);
		gd_histogramMonitoringBtn.widthHint = 58;
		histogramMonitoringBtn.setLayoutData(gd_histogramMonitoringBtn);
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

		autoScaleBtn = new Button(left, SWT.PUSH);
		autoScaleBtn.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false, 1, 1));
		autoScaleBtn.setText("Auto-Scale");
		autoScaleBtn.addSelectionListener(new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				try {
					ICommandService cs = (ICommandService) parentViewPart.getSite().getService(ICommandService.class);
					Command command = cs.getCommand("uk.ac.gda.beamline.i13i.commands.setLiveViewScale");
					IParameter parameter = command.getParameter("uk.ac.gda.beamline.i13i.commandParameters.adcontrollerServiceName");
					Parameterization[] parameterizations = new Parameterization[] { new Parameterization(parameter, "i13")};
					ParameterizedCommand cmd = new ParameterizedCommand(command, parameterizations);
					ExecutionEvent executionEvent = ((IHandlerService)parentViewPart.getSite().getService(IHandlerService.class)).createExecutionEvent(cmd, null);
					command.executeWithChecks(executionEvent);
				} catch (Exception e1) {
					logger.error("Error setting live view scaling", e1);
				}
			}


			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});

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
		try {
			statusComposite.setObservable(config.getImageNDStats().getPluginBase().createConnectionStateObservable());
		} catch (Exception e1) {
			logger.error("Error in monitoring connection state", e1);
		}
		addDisposeListener(new DisposeListener() {
			
			@Override
			public void widgetDisposed(DisposeEvent e) {
					try {
						stop();
					} catch (Exception ex) {
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

			}
		});
	}

	private double getMPEGProcOffset() throws Exception {
		return config.getLiveViewNDProc().getOffset();
	}

	private double getMPEGProcScale() throws Exception {
		return config.getLiveViewNDProc().getScale();
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
		double scale = Histogram.this.getMPEGProcScale();
		double offset = Histogram.this.getMPEGProcOffset();
		RectangularROI roi;
		long min = (long) -offset;
		long max = (long) (255.0 / scale + min);

		if (min < getImageMin())
			min = getImageMin(); // The lowest intensity is 0
		if (max > getImageMax())
			max = getImageMax();

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
					Histogram.this.config.getLiveViewNDProc().setScale(scale);
					Histogram.this.config.getLiveViewNDProc().setOffset(offset);
					Histogram.this.config.getLiveViewNDProc().setEnableOffsetScale(1);
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
			mpegProcOffsetObservable = Histogram.this.config.getLiveViewNDProc()
					.createOffsetObservable();
			mpegProcScaleObservable = Histogram.this.config.getLiveViewNDProc()
					.createScaleObservable();
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

	public void stop() throws Exception {
		config.getImageNDStats().setComputeHistogram(0);
		if (statsArrayCounterObservable != null && statsArrayCounterObserver != null) {
			statsArrayCounterObservable.deleteIObserver(statsArrayCounterObserver);
			statsArrayCounterObserver = null;
			statsArrayCounterObservable = null;
		}
		setStarted(false);

	}

	Job updateHistogramJob;

	private Button autoScaleBtn;
	private IOCStatus statusComposite;

	public void start() throws Exception {
		final int histSize = getHistSize();
		int histMin = getImageMin();
		int histMax = getImageMax();
		config.getImageNDStats().setHistSize(histSize);
		config.getImageNDStats().setHistMin(histMin);
		config.getImageNDStats().setHistMax(histMax);
		config.getImageNDStats().getPluginBase().enableCallbacks();
		config.getImageNDStats().setComputeHistogram(1);
		double step = (histMax - histMin) / histSize;
		double[] range = new double[histSize];
		range[0] = histMin;
		for (int i = 1; i < histSize; i++) {
			range[i] = range[i - 1] + step;
		}
		histogramXAxisRange = new DoubleDataset(range);
		histogramXAxisRange.setName("Counts");
		if (statsArrayCounterObservable == null) {
			statsArrayCounterObservable = config.getImageNDStats().getPluginBase().createArrayCounterObservable();
		}
		if (statsArrayCounterObserver == null) {
			statsArrayCounterObserver = new Observer<Integer>() {

				boolean first = true;

				@Override
				public void update(Observable<Integer> source, Integer arg) {
					if (isDisposed())
						return;
					if (first) {
						first = false;
						return; // ignore first update
					}
					if (updateHistogramJob == null) {
						updateHistogramJob = new Job("Update histogram") {

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
									histogram_RBV = config.getImageNDStats().getHistogram_RBV(histSize);
								} catch (Exception e) {
									logger.error("Error getting histogram", e);
									return Status.OK_STATUS;
								}

								if (histogram_RBV.length != histogramXAxisRange.getSize()) {
									logger.error("Length of histogram does not match histSize");
									return Status.OK_STATUS;
								}
								DoubleDataset ds = new DoubleDataset(histogram_RBV);

								ds.setName("");

								if (histogramTrace == null) {
									histogramTrace = plottingSystem.createLineTrace(PROFILE);
									histogramTrace.setTraceColor(ColorConstants.blue);
								}

								histogramTrace.setData(histogramXAxisRange, ds);

								if (updateUIRunnable == null) {
									updateUIRunnable = new Runnable() {

										@Override
										public void run() {
											runnableScheduled = false;
											boolean firstTime = plottingSystem.getTrace(PROFILE) == null;
											if (firstTime) {
												plottingSystem.addTrace(histogramTrace);
												plottingSystem.setTitle("");
												IAxis yaxis = plottingSystem.getSelectedYAxis();
												yaxis.setFormatPattern("#####");
												yaxis.setTitle("Number of Pixels");
												IAxis xaxis = plottingSystem.getSelectedXAxis();
												xaxis.setFormatPattern("#####");
												xaxis.setTitle("Counts");
											}
											plottingSystem.repaint();
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
						updateHistogramJob.setUser(false);
						updateHistogramJob.setPriority(Job.SHORT);
					}
					updateHistogramJob.schedule(200); // limit to 5Hz

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
