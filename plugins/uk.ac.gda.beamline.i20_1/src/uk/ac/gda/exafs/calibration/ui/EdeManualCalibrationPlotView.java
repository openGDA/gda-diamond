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

package uk.ac.gda.exafs.calibration.ui;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.List;

import org.dawnsci.ede.herebedragons.CalibrationEnergyData;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.dawnsci.plotting.api.PlotType;
import org.eclipse.dawnsci.plotting.api.PlottingFactory;
import org.eclipse.dawnsci.plotting.api.tool.IToolPageSystem;
import org.eclipse.january.dataset.IDataset;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.data.AlignmentParametersModel;

public class EdeManualCalibrationPlotView  extends ViewPart implements CalibrationPlotViewer {

	private static final Logger logger = LoggerFactory.getLogger(EdeManualCalibrationPlotView.class);

	private static final int ZOOM_START_LEVEL = 100;
	public static final String REFERENCE_ID = "uk.ac.gda.exafs.ui.views.calibrationreference";
	public static final String EDE_ID = "uk.ac.gda.exafs.ui.views.calibrationEdeData";

	private final IPlottingSystem plottingSystemRef;

	private CalibrationEnergyData referenceData;

	public EdeManualCalibrationPlotView() throws Exception {
		plottingSystemRef = PlottingFactory.createPlottingSystem();
	}

	@Override
	public void setCalibrationData(CalibrationEnergyData referenceData) {
		if (this.referenceData != null) {
			return;
		}
		this.referenceData = referenceData;
		this.referenceData.addPropertyChangeListener(CalibrationEnergyData.FILE_NAME_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				try {
					plotData();
				} catch (Exception e) {
					logger.error("Unable to plot data", e);
				}
			}
		});
		try {
			plotData();
		} catch (Exception e) {
			logger.error("Unable to plot data", e);
		}
	}

	@Override
	public void createPartControl(Composite parent) {
		plottingSystemRef.createPlotPart(parent,
				getTitle(),
				// unique id for plot.
				getViewSite().getActionBars(),
				PlotType.XY,
				this);
	}

	@Override
	public void plotData() throws Exception {
		if (referenceData.getRefFile() == null) {
			plottingSystemRef.clear();
			return;
		}
		List<IDataset> spectra = new ArrayList<IDataset>(1);
		spectra.add(referenceData.getEdeDataset());

		plottingSystemRef.clear();
		plottingSystemRef.createPlot1D(referenceData.getRefEnergyDataset(), spectra, new NullProgressMonitor());
		showReferencePoints();
		double startValue = getStartZoomForReferenceData();
		double lastValue = getEndZoomForReferenceData();
		plottingSystemRef.getSelectedXAxis().setRange(startValue, lastValue);
	}

	private double getStartZoomForReferenceData() {
		return AlignmentParametersModel.INSTANCE.getEnergy() - ZOOM_START_LEVEL;
	}

	private double getEndZoomForReferenceData() {
		double maxEnergy = referenceData.getRefEnergyDataset().getDouble(referenceData.getRefEnergyDataset().getSize() - 1);
		double endZoom = getStartZoomForReferenceData() + AlignmentParametersModel.INSTANCE.getAlignmentSuggestedParameters().getReadBackEnergyBandwidth();
		if (endZoom > maxEnergy) {
			endZoom = maxEnergy;
		}
		return endZoom;
	}

	private void showReferencePoints() {
		updateVisiability();
	}

	private void updateVisiability() {
		plottingSystemRef.repaint();
	}

	@Override
	public void setFocus() {
		//
	}

	@Override
	public Object getAdapter(@SuppressWarnings("rawtypes") Class clazz) {
		if (clazz == IToolPageSystem.class) {
			return plottingSystemRef;
		}
		return super.getAdapter(clazz);
	}
}
