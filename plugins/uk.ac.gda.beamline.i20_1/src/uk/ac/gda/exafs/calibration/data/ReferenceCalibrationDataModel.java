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

import gda.util.exafs.Element;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.io.DataHolder;
import uk.ac.diamond.scisoft.analysis.io.LoaderFactory;
import uk.ac.gda.beans.ObservableModel;

public class ReferenceCalibrationDataModel extends ObservableModel {
	// TODO Refactor to create ref data model
	public static final String FILE_NAME_PROP_NAME = "fileName";
	protected String fileName;

	public static final String MANUAL_CALIBRATION_PROP_NAME = "manualCalibration";
	private boolean manualCalibration;

	protected DataHolder dataHolder;
	protected AbstractDataset dataNode;
	protected AbstractDataset energyNode;

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

	public List<Double> getReferencePoints() {
		return refReferencePoints;
	}

	public void setReferencePoints(List<Double> refReferencePoints) {
		this.refReferencePoints = refReferencePoints;
	}

	public AbstractDataset getRefDataNode() {
		return dataNode;
	}

	public AbstractDataset getRefEnergyNode() {
		return energyNode;
	}

	public DataHolder getRefFile() {
		return dataHolder;
	}

	public void loadReferenceData(Element element, String edgeName) {
		File folder = new File(EdeCalibrationModel.REF_DATA_PATH);
		if (!folder.exists() || !folder.canRead()) {
			return;
		}

		String fileName = element.getSymbol() + "_" + edgeName + EdeCalibrationModel.REF_DATA_EXT;
		File file = new File(folder, fileName);
		if (file.exists() && file.canRead()) {
			try {
				setData(file.getAbsolutePath());
			} catch (Exception e) {
				// TODO Handle this
			}
		}
	}

	public void setData(String fileName) throws Exception {
		setData(fileName, EdeCalibrationModel.REF_ENERGY_COLUMN_NAME, EdeCalibrationModel.REF_DATA_COLUMN_NAME);
	}

	protected void setData(String fileName, String energyNodePath, String dataNodePath) throws Exception {
		try {
			DataHolder dataHolder = LoaderFactory.getData(fileName);
			if (dataHolder == null) {
				firePropertyChange(FILE_NAME_PROP_NAME, this.fileName, this.fileName = null);
				return;
			}
			this.dataHolder = dataHolder;
			energyNode = (AbstractDataset) this.dataHolder.getLazyDataset(energyNodePath).getSlice();
			dataNode = (AbstractDataset) this.dataHolder.getLazyDataset(dataNodePath).getSlice();
			loadReferencePoints();
			firePropertyChange(FILE_NAME_PROP_NAME, this.fileName, this.fileName = fileName);
		} catch (Exception e) {
			firePropertyChange(FILE_NAME_PROP_NAME, this.fileName, this.fileName = null);
			throw new Exception("Unable to load data for " + fileName, e);
		}
	}

	protected void loadReferencePoints() {
		refReferencePoints = new ArrayList<Double>(3);
		refReferencePoints.add(energyNode.min().doubleValue());
		refReferencePoints.add((Double) energyNode.mean());
		refReferencePoints.add(energyNode.max().doubleValue());
	}
}