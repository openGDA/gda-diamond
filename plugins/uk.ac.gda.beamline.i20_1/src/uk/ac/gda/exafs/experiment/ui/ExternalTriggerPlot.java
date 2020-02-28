/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.experiment.ui;

import java.beans.PropertyChangeListener;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.apache.commons.lang3.tuple.Pair;
import org.dawb.common.ui.widgets.ActionBarWrapper;
import org.eclipse.core.databinding.observable.IChangeListener;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.dawnsci.plotting.api.PlotType;
import org.eclipse.dawnsci.plotting.api.PlottingFactory;
import org.eclipse.dawnsci.plotting.api.annotation.IAnnotation;
import org.eclipse.dawnsci.plotting.api.annotation.IAnnotation.LineStyle;
import org.eclipse.dawnsci.plotting.api.axis.AxisEvent;
import org.eclipse.dawnsci.plotting.api.axis.IAxis;
import org.eclipse.dawnsci.plotting.api.axis.IAxisListener;
import org.eclipse.dawnsci.plotting.api.trace.ILineTrace;
import org.eclipse.dawnsci.plotting.api.trace.ILineTrace.TraceType;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Slider;
import org.eclipse.swt.widgets.Widget;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.experiment.trigger.DetectorDataCollection;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject.TriggerOutputPort;
import uk.ac.gda.exafs.experiment.ui.data.ExternalTriggerSetting;

public class ExternalTriggerPlot {
	private static Logger logger = LoggerFactory.getLogger(ExternalTriggerPlot.class);

	private IPlottingSystem<Composite> plot;
	private Slider slider;
	private volatile boolean sliderBeingMoved = false;
	private double sliderScaleFactor = 5000;

	private Button showLabelsButton;
	private boolean showLabels;
	private double minY;
	private double maxY;

	private String timeUnits = "s";
	private DecimalFormat numberFormat = new DecimalFormat("0.#");

	private final ExternalTriggerSetting externalTriggerSetting;

	/** PropertyChange listener for each TriggerableObject in the sample environment */
	private Map<TriggerableObject, PropertyChangeListener> propertyChangeMap = new HashMap<>();

	public ExternalTriggerPlot(ExternalTriggerSetting externalTriggerSetting) {
		this.externalTriggerSetting = externalTriggerSetting;
	}

	public void createPlot(Composite parent) {

		try {
		    Composite content = new Composite(parent, SWT.NONE);
		    content.setLayout(new GridLayout(1, false));
		    GridDataFactory.fillDefaults().span(2, 1).applyTo(content);

			ActionBarWrapper actionbarWrapper = ActionBarWrapper.createActionBars(content, null);
			GridDataFactory.fillDefaults().align(SWT.FILL, SWT.BEGINNING).grab(true, false).applyTo(actionbarWrapper.getToolbarControl());

			plot = PlottingFactory.createPlottingSystem();
			plot.createPlotPart(content, "Tfg trigger pulses", actionbarWrapper, PlotType.XY, null);
			GridDataFactory.fillDefaults().hint(SWT.DEFAULT, 400).grab(true, true).applyTo(plot.getPlotComposite());

			showLabelsButton = new Button(content, SWT.CHECK);
			showLabelsButton.setText("Show pulse names");
			showLabelsButton.setSelection(showLabels);

			// Add a slider to control the horizontal view region of the plot
			slider = new Slider(content, SWT.HORIZONTAL);
			GridDataFactory.fillDefaults().applyTo(slider);

			//Add listener to dispose of the widgets and their listners
			parent.addDisposeListener( event  -> {
				removeTriggerableObjectListeners();
				removeListeners(slider, SWT.Selection);
				removeListeners(showLabelsButton, SWT.Selection);
				externalTriggerSetting.getTfgTrigger().getDetectorDataCollection().removePropertyChangeListener(tfgTriggerListener);
				externalTriggerSetting.getSampleEnvironment().removeChangeListener(sampleEnvironmentListener);
				plot.dispose();
			});

			addListeners();

		} catch (Exception e) {
			logger.error("Problem creating plotting system for Tfg trigger pulse plot", e);
		}
	}

	private void removeListeners(Widget widget, int type) {
		for(Listener l : widget.getListeners(type)) {
			widget.removeListener(type, l);
		}
	}

	private void addListeners() {

		// Listener to slider to update the x axis plot range when slider is dragged
		slider.addListener(SWT.Selection, event -> {
			sliderBeingMoved = true;
			logger.trace("Slider position : {}/{}", slider.getSelection(), slider.getMaximum());
			double sliderTime = slider.getSelection()/sliderScaleFactor;
			logger.trace("Time from slider position : {} sec", sliderTime);

			IAxis xAxis = plot.getSelectedXAxis();
			double viewMin = xAxis.getLower();
			double viewMax = xAxis.getUpper();
			double viewRange = viewMax - viewMin;
			logger.trace("Current X Axis range : {}/{}", viewMin, viewMax);
			double newViewMin = sliderTime;
			double newViewMax = sliderTime + viewRange;
			logger.trace("New X Axis range : {}/{}", newViewMin, newViewMax);
			xAxis.setRange(newViewMin, newViewMax);
			sliderBeingMoved = false;
		});

		// Listener for the y axis to keep the vertical range fixed
		plot.getSelectedYAxis().addAxisListener(new IAxisListener() {
			private volatile boolean changeScaleInProgress = false;

			@Override
			public void rangeChanged(AxisEvent evt) {
				if (changeScaleInProgress) {
					return;
				}
				changeScaleInProgress = true;
				logger.trace("Setting y axis range to {}, {}: ", minY, maxY);
				plot.getSelectedYAxis().setRange(minY, maxY);
				changeScaleInProgress = false;
			}

			@Override
			public void revalidated(AxisEvent evt) {
			}
		});

		// Listener for the x axis to update the slider position when the view changes
		plot.getSelectedXAxis().addAxisListener(new IAxisListener() {

			@Override
			public void rangeChanged(AxisEvent evt) {
				if (sliderBeingMoved) {
					logger.trace("Slider is focused ? {}", sliderBeingMoved);
					return;
				}
				IAxis xAxis = plot.getSelectedXAxis();
				double min = xAxis.getLower();
				double max = xAxis.getUpper();
				double frac = (min - getMinPulseTime())/(getMaxPulseTime() - getMinPulseTime());
				logger.trace("X axis : rangeChanged : {} ... {}, {}", min, max, frac);
				if (frac >= 0 && frac < 1) {
					double val = slider.getMinimum() + frac*(slider.getMaximum() - slider.getMinimum());
					logger.trace("Setting slider to {}", val);
					slider.setSelection((int)val);
				}
			}

			@Override
			public void revalidated(AxisEvent evt) {
			}
		});

		showLabelsButton.addListener(SWT.Selection, v -> {
			showLabels = showLabelsButton.getSelection();
			plotPulses();
		});

		externalTriggerSetting.getTfgTrigger().getDetectorDataCollection().addPropertyChangeListener(tfgTriggerListener);

		// Update the listeners when items get added, removed from the list
		externalTriggerSetting.getSampleEnvironment().addChangeListener(sampleEnvironmentListener);

		updateSampleEnvironmentlListeners();
	}

	PropertyChangeListener tfgTriggerListener = event -> plotPulses();
	IChangeListener sampleEnvironmentListener = event -> { updateSampleEnvironmentlListeners(); plotPulses(); };

	/**
	 * Update listeners on sample environment TriggerableObjects - so that plotPulses gets called when anything changes.
	 */
	private void updateSampleEnvironmentlListeners() {
		logger.debug("Updating sample environment model listeners");
		// remove the old listeners
		removeTriggerableObjectListeners();
		propertyChangeMap.clear();

		// Replot when any of the TriggerableObject property change events get fired
		for(TriggerableObject trigger : externalTriggerSetting.getTfgTrigger().getSampleEnvironment()) {
			PropertyChangeListener listener = evt -> {
				logger.debug("Replot from {} , {}", trigger.getName(), trigger.getTriggerOutputPort());
				plotPulses();
			};
			trigger.addPropertyChangeListener(listener);
			propertyChangeMap.put(trigger, listener);
		}
	}

	private void removeTriggerableObjectListeners() {
		propertyChangeMap.forEach( (trigger, listener) -> {
			if (trigger != null) {
				logger.debug("Clearing triggers for {} {}", trigger.getName(), trigger.getTriggerOutputPort());
				trigger.removePropertyChangeListener(listener);
			}
		});
	}

	public synchronized void plotPulses() {

		if (plot == null || plot.isDisposed()) {
			return;
		}

		try {
			double yOffset = 1.0;
			double pulseHeight = 0.9;

			DetectorDataCollection detCollectionPulse = externalTriggerSetting.getTfgTrigger().getDetectorDataCollection();
			double collectionStart = detCollectionPulse.getTriggerDelay() + detCollectionPulse.getTriggerPulseLength();
			double collectionEnd = collectionStart + detCollectionPulse.getTotalDuration();

			List<Dataset> xDatasets = new ArrayList<>();
			List<Dataset> yDatasets = new ArrayList<>();

			Map<TriggerOutputPort, Double> heightForPlot = new EnumMap<>(TriggerOutputPort.class);

			List<TriggerOutputPort> ports = getUsedOutputPorts();
			double height = 0;
			for(TriggerOutputPort port : ports) {
				List<TriggerableObject> triggers = getTriggersForPort(port);
				List<List<Double>> pulses = getPulseProfile(triggers, pulseHeight);
				List<Double> xvals = pulses.get(0);
				List<Double> yvals = pulses.get(1);
				if (lastValue(xvals) < collectionEnd) {
					xvals.add(collectionEnd);
					yvals.add(lastValue(yvals));
				}
				Dataset xdataset = DatasetFactory.createFromList(xvals);
				Dataset ydataset = DatasetFactory.createFromList(yvals);

				ydataset.setName(port.getPortName());
				ydataset.imultiply(pulseHeight);
				ydataset.iadd(height); // vertical offset

				xDatasets.add(xdataset);
				yDatasets.add(ydataset);
				heightForPlot.put(port,  height);
				height += yOffset;
			}

			// add the traces
			plot.clearAnnotations();
			plot.reset();
			plot.getSelectedXAxis().setTitle("Time [sec]");
			plot.getSelectedYAxis().setTitle("Trigger Signal");
			minY = -0.1;
			maxY = 0.1+yOffset*ports.size();
			plot.getSelectedYAxis().setRange(minY, maxY);
			addSpectrumPulsesToPlot();
			for(int i=0; i<xDatasets.size(); i++) {
				String traceName = yDatasets.get(i).getName();
				ILineTrace trace = plot.createLineTrace(traceName);
				trace.setData(xDatasets.get(i), yDatasets.get(i));
				trace.setName(traceName);
				trace.setLineWidth(2);
				plot.addTrace(trace);
			}

			// add the pulse labels
			if (showLabels) {
				plotAnnotations(heightForPlot);
			}

			updateSliderRange();

		} catch (Exception e) {
			logger.error("Problem plotting Tfg trigger pulses", e);
		}
	}

	private void plotAnnotations(Map<TriggerOutputPort, Double> heightForPlot) throws Exception {
		List<TriggerOutputPort> ports = getUsedOutputPorts();

		// add the pulse labels
		for(TriggerOutputPort port : ports) {
			for(TriggerableObject t : getTriggersForPort(port)) {
				IAnnotation annotation = plot.createAnnotation("test");
				double time = t.getTriggerDelay();
				annotation.setLocation(time, heightForPlot.get(port));
				annotation.setName(String.format("%s : %s %s", t.getName(), numberFormat.format(time), timeUnits));
				annotation.setShowName(true);
				annotation.setShowPosition(false);
				annotation.setLineStyle(LineStyle.UP_DOWN);
				annotation.setVisible(true);
				plot.addAnnotation(annotation);
			}
		}
	}

	/**
	 * Set the slider range to match the range of the min and max pulse times.
	 */
	private void updateSliderRange() {
		int min = (int) (sliderScaleFactor*getMinPulseTime());
		int max = (int) (sliderScaleFactor*getMaxPulseTime());
		int range = (max - min)/100;
		slider.setMinimum(min);
		slider.setMaximum(max);
		slider.setThumb(range);
		slider.setIncrement(range);
		slider.setPageIncrement(2*range);
	}

	private double getMinPulseTime() {
		TriggerableObject detCollectionPulse = externalTriggerSetting.getTfgTrigger().getDetectorDataCollection();
		TriggerableObject sampleEnvPulse = Collections.min(externalTriggerSetting.getTfgTrigger().getSampleEnvironment());
		double minPulse = Math.min(detCollectionPulse.getTriggerDelay(),  sampleEnvPulse.getTriggerDelay());
		return Math.min(minPulse,  0.0);
	}

	private double getMaxPulseTime() {
		return externalTriggerSetting.getTfgTrigger().getTotalTime();
	}

	/**
	 *
	 * @return List of TriggerOutputPorts used in sample environment
	 */
	private List<TriggerOutputPort> getUsedOutputPorts() {
		List<TriggerableObject> triggers = externalTriggerSetting.getTfgTrigger().getSampleEnvironment();
		List<TriggerOutputPort> portList = new ArrayList<>();
		portList.add(TriggerOutputPort.USR_OUT_1); // always have USR_OUT_1
		triggers.stream()
			.map(TriggerableObject::getTriggerOutputPort)
			.filter(port -> !portList.contains(port))
			.forEach(portList::add);
		return portList;
	}

	/**
	 *
	 * @param outputPort
	 * @return List of TriggerableObjects for specified output port
	 */
	private List<TriggerableObject> getTriggersForPort(TriggerOutputPort outputPort) {
		if (outputPort == TriggerOutputPort.USR_OUT_1) {
			return Arrays.asList(externalTriggerSetting.getTfgTrigger().getDetectorDataCollection());
		} else {
			List<TriggerableObject> triggers = externalTriggerSetting.getTfgTrigger().getSampleEnvironment();
			return triggers
					.stream()
					.filter( t -> t.getTriggerOutputPort() == outputPort)
					.collect(Collectors.toList());
		}
	}

	/**
	 * Generate square pulse time series from TriggerableObject list.
	 * @param outputPort
	 * @return List of coordinates (first list = x values, second list = y values)
	 */
	private List<List<Double>> getPulseProfile(List<TriggerableObject> pulsesForPort, double height) {
		List<Pair<Double,Double>> values = new ArrayList<>();
		values.add(Pair.of(0.0, 0.0)); // always include time = 0
		for(TriggerableObject t : pulsesForPort) {
			double startTime = t.getTriggerDelay();
			double endTime = startTime + t.getTriggerPulseLength();
			values.add(Pair.of(startTime, 0.0));
			values.add(Pair.of(startTime, height));
			values.add(Pair.of(endTime, height));
			values.add(Pair.of(endTime, 0.0));
		}
		// sort the points into ascending time order
		values.sort( (val1, val2) -> val1.getKey() < val2.getKey() ? -1 : 1);
		List<Double> xvals = values.stream().map(Pair::getKey).collect(Collectors.toList());
		List<Double> yvals = values.stream().map(Pair::getValue).collect(Collectors.toList());
		return Arrays.asList(xvals, yvals);
	}

	/**
	 *
	 * @param list
	 * @return last value from the list
	 */
	private <T> T lastValue(List<T> list) {
		return list.get(list.size()-1);
	}

	/**
	 * Add profile corresponding to each spectrum to the plot.
	 */
	private void addSpectrumPulsesToPlot() {
		List<TriggerableObject> triggers = getSpectrumTriggers();
		List<List<Double>> pulses = getPulseProfile(triggers, 0.8);
		Dataset xvals = DatasetFactory.createFromList(pulses.get(0));
		Dataset yvals = DatasetFactory.createFromList(pulses.get(1));

		ILineTrace trace = plot.createLineTrace("Spectrum pulses");
		trace.setData(xvals, yvals);
		trace.setName("Spectrum pulses");
		trace.setLineWidth(0);
		trace.setTraceType(TraceType.AREA);
		plot.addTrace(trace);
	}

	/**
	 *
	 * @return TriggerableObject list, each element corresponding to one spectrum
	 * First spectrum begins on falling edge of DetectorDataCollection pulse
	 * (i.e. the pulse on USR_OUT_0 that starts the detector)
	 */
	private List<TriggerableObject> getSpectrumTriggers() {
		DetectorDataCollection detCollectionPulse = externalTriggerSetting.getTfgTrigger().getDetectorDataCollection();

		double collectionStart = detCollectionPulse.getTriggerDelay();
		int numPulses = detCollectionPulse.getNumberOfFrames();
		double spectrumStep = detCollectionPulse.getTotalDuration()/numPulses;
		double pulseWidth = spectrumStep*0.9;

		List<TriggerableObject> triggers = new ArrayList<>();
		for(int i=0; i<numPulses; i++) {
			double startTime = collectionStart + i*spectrumStep;
			triggers.add(new TriggerableObject(startTime, pulseWidth, TriggerOutputPort.USR_OUT_0));
		}
		return triggers;
	}

	public boolean isShowLabels() {
		return showLabels;
	}

	public void setShowLabels(boolean showLabels) {
		this.showLabels = showLabels;
	}

	public IPlottingSystem<Composite> getPlot() {
		return plot;
	}
}
