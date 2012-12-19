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

import gda.device.detector.areadetector.v17.NDStats;
import gda.observable.Observable;
import gda.observable.Observer;

import org.dawb.common.ui.plot.AbstractPlottingSystem;
import org.dawb.common.ui.plot.PlotType;
import org.dawb.common.ui.plot.PlottingFactory;
import org.dawb.common.ui.plot.trace.ILineTrace;
import org.eclipse.draw2d.ColorConstants;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.IViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;

public class ADScaleAdjustmentComposite extends Composite {
	private static final Logger logger = LoggerFactory.getLogger(ADScaleAdjustmentComposite.class);
	private static final String INTENSITIES_lbl = "Intensities";

	private static final String HISTOGRAM_DATASET_lbl = "Histogram Dataset";

	private static final String HISTOGRAM_PLOT_TITLE_lbl = "Histogram Plot";

	private static final String HISTOGRAM_TRACE = "Histogram";
	private AbstractPlottingSystem plottingSystem;

	NDStats ndStats = null;

	public ADScaleAdjustmentComposite(IViewPart parentViewPart, Composite parent, int style, NDStats ndStats2) {
		super(parent, style);
		this.ndStats=ndStats2;
		this.setLayout(new FillLayout());
		try {
			// We always have a light weight one for this view as there is already
			// another using DatasetPlot.
			this.plottingSystem = PlottingFactory.getLightWeightPlottingSystem();
		} catch (Exception ne) {
			logger.error("Cannot create a plotting system!", ne);
			return;
		}
		plottingSystem.createPlotPart(this, parentViewPart.getTitle(), parentViewPart.getViewSite().getActionBars(),
				PlotType.PT1D, parentViewPart);
		plottingSystem.setXfirst(true);
	}

	private ILineTrace histogramTrace= null;
	private DoubleDataset xaxisRange = null;
	private Observable<Integer> counterObserver;
	private Observer<Integer> counterArrayObserver;

	public void stop(){
		if( counterObserver != null && counterArrayObserver != null){
			counterObserver.deleteIObserver(counterArrayObserver);
			counterArrayObserver = null;
			counterObserver = null;
		}
	}
	public void start() throws Exception {
		double histMax = ndStats.getHistMax_RBV();
		double histMin = ndStats.getHistMin_RBV();
		final int histSize = ndStats.getHistSize_RBV();
		double step = (histMax-histMin)/histSize;
		double[] range=new double[histSize];
		range[0] = histMin; 
		for( int i=1; i< histSize; i++){
			range[i] = range[i-1] + step;
		}
		xaxisRange = new DoubleDataset(range);
		xaxisRange.setName(INTENSITIES_lbl);
		if( counterObserver == null){
			counterObserver = ndStats.getPluginBase().createArrayCounterObservable();
		}
		if( counterArrayObserver == null){
			counterArrayObserver = new Observer<Integer>() {

				@Override
				public void update(Observable<Integer> source, Integer arg) {
					if( isDisposed())
						return;
					double[] histogram_RBV;
					try {
						histogram_RBV = ndStats.getHistogram_RBV(histSize);
					} catch (Exception e) {
						logger.error("Error getting histogram", e);
						return;
					}

					if( histogram_RBV.length != xaxisRange.getSize()){
						logger.error("Length of histogram does not match histSize");
						return;
					}
					DoubleDataset ds = new DoubleDataset(histogram_RBV);

					ds.setName(HISTOGRAM_DATASET_lbl);

					
					if (histogramTrace == null) {
						histogramTrace = plottingSystem.createLineTrace(HISTOGRAM_TRACE);
						histogramTrace.setTraceColor(ColorConstants.blue);
					}

					histogramTrace.setData(xaxisRange, ds);

					getDisplay().asyncExec(new Runnable(){

						@Override
						public void run() {

							if (plottingSystem.getTrace(HISTOGRAM_TRACE) == null) {
								plottingSystem.addTrace(histogramTrace);
							}
							plottingSystem.repaint();
							plottingSystem.setTitle(HISTOGRAM_PLOT_TITLE_lbl);
							plottingSystem.getSelectedYAxis().setFormatPattern("#####");
							plottingSystem.getSelectedXAxis().setFormatPattern("#####");
						}
					});
					
				}
			};
		}
		counterObserver.addIObserver(counterArrayObserver);
	}
	@Override
	public void dispose() {
		stop();
		super.dispose();
	}

}
