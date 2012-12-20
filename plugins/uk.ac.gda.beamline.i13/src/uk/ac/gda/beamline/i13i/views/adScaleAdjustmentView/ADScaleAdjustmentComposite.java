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
import org.dawb.common.ui.plot.IPlottingSystem;
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
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.IViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.roi.ROIBase;
import uk.ac.diamond.scisoft.analysis.roi.RectangularROI;

public class ADScaleAdjustmentComposite extends Composite {
	private static final Logger logger = LoggerFactory.getLogger(ADScaleAdjustmentComposite.class);
	private static final String INTENSITIES_lbl = "Intensities";

	private static final String HISTOGRAM_DATASET_lbl = "Histogram Dataset";

	private static final String HISTOGRAM_PLOT_TITLE_lbl = "Histogram Plot";

	private static final String HISTOGRAM_TRACE = "Histogram";
	private AbstractPlottingSystem plottingSystem;

	int histSize=1000; //number of points in the histogram
	int histMin=0;//
	int histMax=65535;
	private final ScaleAdjustmentViewConfig config;

	public ADScaleAdjustmentComposite(IViewPart parentViewPart, Composite parent, int style, ScaleAdjustmentViewConfig config) {
		super(parent, style);
		this.config = config;
		
		this.setLayout(new GridLayout(2,false));
		Composite left = new Composite(this,SWT.NONE);
		GridDataFactory.fillDefaults().grab(false,true).applyTo(left);
		left.setLayout(new GridLayout());
		Button button = new Button(left, SWT.PUSH);
		button.setText("Set Scaling");
		
		
		button.addSelectionListener(new SelectionListener() {
			
			private String regionName;

			@Override
			public void widgetSelected(SelectionEvent e) {
				try {
					if( regionName == null){
						regionName = RegionUtils.getUniqueName("Scaling Range", getPlottingSystem());
					}
					IRegion iRegion = getPlottingSystem().getRegion(regionName);
					if(iRegion == null){
						iRegion = getPlottingSystem().createRegion(regionName, IRegion.RegionType.XAXIS);
						double scale = ADScaleAdjustmentComposite.this.config.ndProc.getScale();
						double offset = ADScaleAdjustmentComposite.this.config.ndProc.getOffset();
						double min = -offset ;
						double max = (255.0/scale +min);
						RectangularROI roi = new RectangularROI(min, 0, max-min, 0, 0);
						iRegion.setROI(roi);
						getPlottingSystem().addRegion(iRegion);
						iRegion.addROIListener(new IROIListener(){

							@Override
							public void roiDragged(ROIEvent evt) {
								try {
									handleROIChangeEvent(evt);
								} catch (Exception e) {
									logger.error("Error handling change to scaling roi", e);
								}
							}

							private void handleROIChangeEvent(ROIEvent evt) throws Exception {
								final IRegion region = (IRegion)evt.getSource();
								RectangularROI roi = (RectangularROI) region.getROI();
								double min = roi.getPointX();
								double max = min + roi.getLengths()[0];
								double offset = - min;
								double scale = 255.0/(max - min);
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
							}});
					} else {
						iRegion.setVisible(true);
					}
				} catch (Exception e1) {
					logger.error("Error creating region", e1);
				}
			}
			
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});
		
		GridDataFactory.fillDefaults().grab(false,false).applyTo(button);

		stopStartedLbl = new Label(left, SWT.NONE);
		GridDataFactory.fillDefaults().grab(false,false).applyTo(stopStartedLbl);
		stopStartBtn = new Button(left, SWT.PUSH);
		GridDataFactory.fillDefaults().grab(false,false).applyTo(stopStartBtn);
		stopStartBtn.addSelectionListener(new SelectionListener() {
			
			@Override
			public void widgetSelected(SelectionEvent e) {
				try{
					if( started){
						stop();
					} else {
						start();
					}
				} catch(Exception ex){
					logger.error("Error responding to start_stop button",ex);
				}
			}
			
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});
		setStarted(started);
		
		
		Composite right = new Composite(this,SWT.NONE);
		GridDataFactory.fillDefaults().grab(true,true).align(SWT.FILL, SWT.FILL).applyTo(right);
		right.setLayout(new FillLayout());
		
		
		try {
			// We always have a light weight one for this view as there is already
			// another using DatasetPlot.
			this.plottingSystem = PlottingFactory.getLightWeightPlottingSystem();
		} catch (Exception ne) {
			logger.error("Cannot create a plotting system!", ne);
			return;
		}
		plottingSystem.createPlotPart(right, parentViewPart.getTitle(), parentViewPart.getViewSite().getActionBars(),
				PlotType.PT1D, parentViewPart);
		plottingSystem.setXfirst(true);
	}

	private ILineTrace histogramTrace= null;
	private DoubleDataset xaxisRange = null;
	private Observable<Integer> counterObserver;
	private Observer<Integer> counterArrayObserver;
	private boolean started = false;
	private Button stopStartBtn;
	private Label stopStartedLbl;

	public void stop() throws Exception{
		config.ndStats.setComputeHistogram(0);
		if( counterObserver != null && counterArrayObserver != null){
			counterObserver.deleteIObserver(counterArrayObserver);
			counterArrayObserver = null;
			counterObserver = null;
		}
		setStarted(false);
		
	}
	public void start() throws Exception {
		config.ndStats.setHistSize(histSize);
		config.ndStats.setHistMin(histMin);
		config.ndStats.setHistMax(histMax);
		config.ndStats.getPluginBase().enableCallbacks();
		config.ndStats.setComputeHistogram(1);
		double step = (histMax-histMin)/histSize;
		double[] range=new double[histSize];
		range[0] = histMin; 
		for( int i=1; i< histSize; i++){
			range[i] = range[i-1] + step;
		}
		xaxisRange = new DoubleDataset(range);
		xaxisRange.setName(INTENSITIES_lbl);
		if( counterObserver == null){
			counterObserver = config.ndStats.getPluginBase().createArrayCounterObservable();
		}
		if( counterArrayObserver == null){
			counterArrayObserver = new Observer<Integer>() {

				private Job job;

				@Override
				public void update(Observable<Integer> source, Integer arg) {
					if( isDisposed())
						return;
					if( job == null){
						job = new Job("Update histogram"){

							private Runnable updateUIRunnable;
							volatile boolean runnableScheduled=false;

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

								if( histogram_RBV.length != xaxisRange.getSize()){
									logger.error("Length of histogram does not match histSize");
									return Status.OK_STATUS;
								}
								DoubleDataset ds = new DoubleDataset(histogram_RBV);

								ds.setName(HISTOGRAM_DATASET_lbl);

								
								if (histogramTrace == null) {
									histogramTrace = plottingSystem.createLineTrace(HISTOGRAM_TRACE);
									histogramTrace.setTraceColor(ColorConstants.blue);
								}

								histogramTrace.setData(xaxisRange, ds);

								if( updateUIRunnable == null){
									updateUIRunnable = new Runnable(){

										@Override
										public void run() {
											runnableScheduled = false;
											if (plottingSystem.getTrace(HISTOGRAM_TRACE) == null) {
												plottingSystem.addTrace(histogramTrace);
											}
											plottingSystem.repaint();
											plottingSystem.setTitle(HISTOGRAM_PLOT_TITLE_lbl);
											plottingSystem.getSelectedYAxis().setFormatPattern("#####");
											plottingSystem.getSelectedXAxis().setFormatPattern("#####");
										}
									
									};
								}
								if( !runnableScheduled){
									getDisplay().asyncExec(updateUIRunnable);
									runnableScheduled=true;
								}
								return Status.OK_STATUS;
							}
						};
						job.setUser(false);
						job.setPriority(Job.SHORT);
					}
					job.schedule(200); //limit to 5Hz
					
					
				}
			};
		}
		counterObserver.addObserver(counterArrayObserver);
		setStarted(true);
	}
	private void setStarted(boolean b) {
		started = b;
		stopStartBtn.setText(b ? "Stop" : "Start");
		stopStartedLbl.setText(b ? "Running" : "Stopped");
	}
	@Override
	public void dispose() {
		try {
			stop();
		} catch (Exception e) {
			logger.error("Error stopping histogram computation", e);
		}
		super.dispose();
	}
	/**
	 * Needed for the adapter of the parent view to return IToolPageSystem.class
	 * 
	 */
	public IPlottingSystem getPlottingSystem() {
		return plottingSystem;
	}

}
