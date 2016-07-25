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

import org.eclipse.dawnsci.analysis.api.io.IDataHolder;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetUtils;

import uk.ac.diamond.scisoft.analysis.io.LoaderFactory;
import uk.ac.gda.beans.ObservableModel;

public abstract class CalibrationDataModel extends ObservableModel {
	private static final int PADDING_FOR_REFERENCE = 100;
	// TODO Refactor to create ref data model
	public static final String FILE_NAME_PROP_NAME = "fileName";
	protected String fileName;

	public static final String MANUAL_CALIBRATION_PROP_NAME = "manualCalibration";
	private boolean manualCalibration;

	protected IDataHolder dataHolder;
	protected Dataset energyNode;

	private Dataset dataNode;
	private double startEnergy;
	private double endEnergy;

	private final double[] refReferencePoints = new double[3];

	public boolean isManualCalibration() {
		return manualCalibration;
	}

	public void setManualCalibration(boolean manualCalibration) {
		firePropertyChange(MANUAL_CALIBRATION_PROP_NAME, this.manualCalibration, this.manualCalibration = manualCalibration);
	}

	public String getFileName() {
		return fileName;
	}

	private void setInitialEnergyRange(double start, double end) {
		startEnergy = start;
		endEnergy = end;
	}

	public double[] getReferencePoints() {
		return refReferencePoints;
	}

	public void setReferencePoints(double start, double mid, double end) {
		refReferencePoints[0] = start;
		refReferencePoints[1] = mid;
		refReferencePoints[2] = end;
	}

	public Dataset getEdeDataset() {
		return dataNode;
	}

	public Dataset getRefEnergyDataset() {
		return energyNode;
	}

	public IDataHolder getRefFile() {
		return dataHolder;
	}

	protected abstract void setDataFile(String fileName) throws Exception;

	public Dataset getEnergyNode() {
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
			IDataHolder dataHolder = LoaderFactory.getData(fileName);
			if (dataHolder == null) {
				firePropertyChange(FILE_NAME_PROP_NAME, this.fileName, this.fileName = null);
				this.setManualCalibration(false);
				return;
			}
			this.dataHolder = dataHolder;
			energyNode = DatasetUtils.sliceAndConvertLazyDataset(dataHolder.getLazyDataset(energyNodePath));
			dataNode = DatasetUtils.sliceAndConvertLazyDataset(dataHolder.getLazyDataset(dataNodePath));

			setInitialEnergyRange(energyNode.min().doubleValue(), energyNode.max().doubleValue());
			double mid = (double) energyNode.mean();
			setReferencePoints(mid - PADDING_FOR_REFERENCE, mid, mid + PADDING_FOR_REFERENCE);
			firePropertyChange(FILE_NAME_PROP_NAME, this.fileName, this.fileName = fileName);
		} catch (Exception e) {
			firePropertyChange(FILE_NAME_PROP_NAME, this.fileName, this.fileName = null);
			this.setManualCalibration(false);
			throw new Exception("Unable to load data for " + fileName, e);
		}
	}

}