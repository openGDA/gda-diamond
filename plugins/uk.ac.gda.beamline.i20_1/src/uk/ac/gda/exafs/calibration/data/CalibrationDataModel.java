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

package uk.ac.gda.exafs.calibration.data;

import java.util.ArrayList;
import java.util.List;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.io.DataHolder;
import uk.ac.diamond.scisoft.analysis.io.LoaderFactory;
import uk.ac.gda.beans.ObservableModel;

public class CalibrationDataModel extends ObservableModel {
	private static final int PADDING_FOR_REFERENCE = 20;
	// TODO Refactor to create ref data model
	public static final String FILE_NAME_PROP_NAME = "fileName";
	protected String fileName;

	public static final String MANUAL_CALIBRATION_PROP_NAME = "manualCalibration";
	private boolean manualCalibration;

	private DataHolder dataHolder;
	private AbstractDataset dataNode;
	private AbstractDataset energyNode;
	private double startEnergy;
	private double endEnergy;

	protected List<Double> refReferencePoints = new ArrayList<Double>();

	public boolean isManualCalibration() {
		return manualCalibration;
	}

	public void setManualCalibration(boolean manualCalibration) {
		firePropertyChange(MANUAL_CALIBRATION_PROP_NAME, this.manualCalibration, this.manualCalibration = manualCalibration);
	}

	public String getFileName() {
		return fileName;
	}

	public void setInitialEnergyRange(double start, double end) {
		startEnergy = start;
		endEnergy = end;
	}

	public List<Double> getReferencePoints() {
		return refReferencePoints;
	}

	public void setReferencePoints(List<Double> refReferencePoints) {
		this.refReferencePoints = refReferencePoints;
	}

	public AbstractDataset getEdeDataset() {
		return dataNode;
	}

	public AbstractDataset getRefEnergyDataset() {
		return energyNode;
	}

	public DataHolder getRefFile() {
		return dataHolder;
	}

	public void setDataFile(String fileName) throws Exception {
		setData(fileName, EdeCalibrationModel.REF_ENERGY_COLUMN_NAME, EdeCalibrationModel.REF_DATA_COLUMN_NAME);
	}

	public AbstractDataset getEnergyNode() {
		return energyNode;
	}

	public double getStartEnergy() {
		return startEnergy;
	}

	public double getEndEnergy() {
		return endEnergy;
	}

	protected void setData(String fileName, String energyNodePath, String dataNodePath) throws Exception {
		try {
			DataHolder dataHolder = LoaderFactory.getData(fileName);
			if (dataHolder == null) {
				firePropertyChange(FILE_NAME_PROP_NAME, this.fileName, this.fileName = null);
				this.setManualCalibration(false);
				return;
			}
			this.dataHolder = dataHolder;
			energyNode = (AbstractDataset) this.dataHolder.getLazyDataset(energyNodePath).getSlice();
			dataNode = (AbstractDataset) this.dataHolder.getLazyDataset(dataNodePath).getSlice();
			setInitialEnergyRange(energyNode.min().doubleValue(), energyNode.max().doubleValue());
			loadReferencePoints();
			firePropertyChange(FILE_NAME_PROP_NAME, this.fileName, this.fileName = fileName);
		} catch (Exception e) {
			firePropertyChange(FILE_NAME_PROP_NAME, this.fileName, this.fileName = null);
			this.setManualCalibration(false);
			throw new Exception("Unable to load data for " + fileName, e);
		}
	}

	private void loadReferencePoints() {
		refReferencePoints = new ArrayList<Double>(3);
		refReferencePoints.add(startEnergy + PADDING_FOR_REFERENCE);
		refReferencePoints.add((Double) energyNode.mean());
		refReferencePoints.add(endEnergy - PADDING_FOR_REFERENCE);
	}
}