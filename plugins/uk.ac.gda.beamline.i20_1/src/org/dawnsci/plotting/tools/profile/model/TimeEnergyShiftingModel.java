/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package org.dawnsci.plotting.tools.profile.model;

import java.util.Arrays;

import org.eclipse.dawnsci.analysis.dataset.impl.DatasetUtils;
import org.eclipse.dawnsci.analysis.dataset.impl.DoubleDataset;
import org.eclipse.dawnsci.plotting.api.region.IROIListener;
import org.eclipse.dawnsci.plotting.api.region.IRegion;
import org.eclipse.dawnsci.plotting.api.region.ROIEvent;
import org.eclipse.dawnsci.plotting.api.trace.ITrace;

import uk.ac.gda.beans.ObservableModel;

public class TimeEnergyShiftingModel extends ObservableModel implements IROIListener {
	public static final String LOAD_DATA_PROP_NAME = "loadData";
	private boolean loadData;

	public static final String USE_SPECTRA_PROP_NAME = "useSpectra";
	private boolean useSpectra;

	public static final String ENERGY_SHIFTED_PROP_NAME = "energyShifted";
	private boolean energyShifted;

	public static final String DATA_UPDATED_PROP_NAME = "dataUpdated";
	private DoubleDataset dataUpdated;

	private IRegion engeryRegion;
	private final ToolPageModel toolPageModel;

	public TimeEnergyShiftingModel(ToolPageModel toolPageModel) {
		this.toolPageModel = toolPageModel;
	}

	public boolean isLoadData() {
		return loadData;
	}

	public void setLoadData(boolean loadData) {
		firePropertyChange(LOAD_DATA_PROP_NAME, this.loadData, this.loadData = loadData);
	}

	public void setEnergyRegion(IRegion engeryRegion) {
		if (this.engeryRegion != null) {
			this.engeryRegion.removeROIListener(this);
		}
		this.engeryRegion = engeryRegion;
		this.engeryRegion.addROIListener(this);
		updateTimeEnergyValue();
	}

	@Override
	public void roiDragged(ROIEvent evt) {}

	@Override
	public void roiChanged(ROIEvent evt) {
		updateTimeEnergyValue();
	}

	@Override
	public void roiSelected(ROIEvent evt) {}


	public boolean isEnergyShifted() {
		return energyShifted;
	}

	public void setEnergyShifted(boolean energyShifted) {
		this.energyShifted = energyShifted;
	}

	private void updateTimeEnergyValue() {
		double energy = engeryRegion.getROI().getPointX();
		DoubleDataset newdata = null;
		int[] shape = toolPageModel.getImageTrace().getData().getShape();
		int numberOfSpectrum = shape[0];
		int numberOfChannels = shape[1];
		int index = DatasetUtils.findIndexGreaterThanOrEqualTo((DoubleDataset) toolPageModel.getImageTrace().getAxes().get(0), energy);
		DoubleDataset imageData = (DoubleDataset) toolPageModel.getImageTrace().getData();
		if (useSpectra && !toolPageModel.getSpectraPlotting().getTraces().isEmpty()) {
			if (toolPageModel.getSpectraPlotting().getTraces().size() == 1) {
				return;
			}
			int[] selectedIndex = new int[toolPageModel.getSpectraPlotting().getTraces().size()];

			int i = 0;
			for (ITrace trace : toolPageModel.getSpectraPlotting().getTraces()) {
				selectedIndex[i++] = ((SpectrumDataNode) trace.getUserObject()).getIndex();
			}
			Arrays.sort(selectedIndex);
			DoubleDataset data = null;
			if (energyShifted) {
				for (i = 0; i < selectedIndex.length; i++) {
					DoubleDataset tempData = (DoubleDataset) imageData.getSlice(new int[]{selectedIndex[i], 0}, new int[]{selectedIndex[i] + 1, numberOfChannels}, new int[]{1, 1}).squeeze();
					// TODO
					//Generic1DFitter.findPeaks(xdata, tempData, 2);
				}
			} else {
				data = (DoubleDataset) imageData.getSlice(new int[]{selectedIndex[0], 0}, new int[]{selectedIndex[selectedIndex.length - 1] + 1, numberOfChannels}, new int[]{1, 1});
			}
			newdata = (DoubleDataset) data.getSlice(new int[]{0, index},new int[]{data.getShape()[0], index + 1}, new int[]{1,1}).squeeze();
		} else {

			newdata = (DoubleDataset) imageData.getSlice(new int[]{0, index},new int[]{numberOfSpectrum, index + 1}, new int[]{1,1}).squeeze();
		}
		this.firePropertyChange(DATA_UPDATED_PROP_NAME, dataUpdated, dataUpdated = newdata);
	}

	public DoubleDataset getDataUpdated() {
		return dataUpdated;
	}

	public boolean isUseSpectra() {
		return useSpectra;
	}

	public void setUseSpectra(boolean useSpectra) {
		this.firePropertyChange(USE_SPECTRA_PROP_NAME, this.useSpectra, this.useSpectra = useSpectra);
	}
}