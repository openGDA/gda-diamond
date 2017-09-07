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

import java.util.Arrays;
import java.util.List;

import org.eclipse.dawnsci.analysis.api.io.IDataHolder;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.january.dataset.DatasetUtils;
import org.eclipse.january.dataset.DoubleDataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.scan.ede.datawriters.EdeDataConstants;
import uk.ac.diamond.scisoft.analysis.io.LoaderFactory;
import uk.ac.gda.beans.ObservableModel;

public abstract class CalibrationEnergyData extends ObservableModel {
	private static final Logger logger = LoggerFactory.getLogger(CalibrationEnergyData.class);

	// TODO Refactor to create ref data model
	public static final String FILE_NAME_PROP_NAME = "fileName";
	public static final String MANUAL_CALIBRATION_PROP_NAME = "manualCalibration";

	private static final int PADDING_FOR_REFERENCE = 100;

	protected String fileName;
	private boolean manualCalibration;

	protected IDataHolder dataHolder;
	protected Dataset energyNode;

	private Dataset dataNode;
	private double startEnergy;
	private double endEnergy;

	private final double[] refReferencePoints = new double[3];

	private String xAxisName;

	private static final String[] xValueDatasetNames = { EdeDataConstants.PIXEL_COLUMN_NAME, EdeDataConstants.STRIP_COLUMN_NAME, "position" };
	private static final String yValueDatasetName = EdeDataConstants.LN_I0_IT_COLUMN_NAME;

	public String getXAxisName() {
		return xAxisName;
	}

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


	private void setDataFromNexusFile(IDataHolder dataHolder) throws Exception {

		List<String> dataNames = Arrays.asList(dataHolder.getNames());
		String dataNodePath = "";
		String energyNodePath = "";

		// Try to locate suitable datasets in Nexus file to use for x and y values
		// (use last match found)
		for (int i = 0; i < dataNames.size(); i++) {
			String dataName = dataNames.get(i);

			for (String xvalueDatasetName : xValueDatasetNames) {
				if (dataName.endsWith(xvalueDatasetName)) {
					energyNodePath = dataName;
				}
			}
			if (dataName.endsWith(yValueDatasetName) || dataName.endsWith(yValueDatasetName+"/data")) {
				dataNodePath = dataName;
			}
		}

		String errorMessage = new String();
		if (energyNodePath.isEmpty()) {
			errorMessage += " Can't find any datasets called "+Arrays.toString(xValueDatasetNames)+" to use for for strip/pixel/position axis. ";
		}
		if (dataNodePath.isEmpty()) {
			errorMessage += " Can't find dataset called "+yValueDatasetName+" dataset to use for for y axis values. ";
		}
		if (!errorMessage.isEmpty()) {
			throw new Exception(errorMessage);
		}

		xAxisName = energyNodePath;
		this.dataHolder = dataHolder;
		energyNode = (Dataset) this.dataHolder.getLazyDataset(energyNodePath).getSlice();
		Dataset allData = (Dataset) dataHolder.getLazyDataset(dataNodePath).getSlice().squeeze();

		int[] shape = allData.getShape();

		int numReadouts = shape[shape.length - 1];
		int numRows = shape.length==1 ? 1 : shape[0];
		dataNode = DatasetFactory.zeros(DoubleDataset.class, numReadouts);

		if (numRows==1) {
			dataNode.setSlice(allData, new int[] {0}, new int[] {numReadouts}, null);
		} else {
			// Average together lnI0It values if there are more than 1 rows of data available
			for(int i=0; i<numRows; i++) {
				Dataset row = allData.getSlice(new int[]{i, 0}, new int[]{i+1, numReadouts}, null).squeeze();
				dataNode.iadd(row);
			}
			dataNode.imultiply(1.0/numRows);
		}
	}

	protected void setData(String fileName, String energyNodePath, String dataNodePath) throws Exception {
		if (fileName==null) {
			return;
		}
		try {
			IDataHolder dataHolder = LoaderFactory.getData(fileName);
			if (dataHolder == null) {
				firePropertyChange(FILE_NAME_PROP_NAME, this.fileName, this.fileName = null);
				this.setManualCalibration(false);
				return;
			}
			if (fileName.endsWith(".nxs")) {
				// Load datasets from Nexus file
				setDataFromNexusFile(dataHolder);
			} else {
				// Check to make sure named data for energy values is available, use first column from datafile if not found.
				List<String> dataNames = Arrays.asList(dataHolder.getNames());
				if ( !dataNames.contains(energyNodePath) ) {
					energyNodePath = dataNames.get(0);
				}
				xAxisName = energyNodePath;

				this.dataHolder = dataHolder;
				energyNode = DatasetUtils.sliceAndConvertLazyDataset(this.dataHolder.getLazyDataset(energyNodePath));
				dataNode = DatasetUtils.sliceAndConvertLazyDataset(dataHolder.getLazyDataset(dataNodePath));
			}

			setInitialEnergyRange(energyNode.min().doubleValue(), energyNode.max().doubleValue());
			double mid = (double) energyNode.mean();
			setReferencePoints(mid - PADDING_FOR_REFERENCE, mid, mid + PADDING_FOR_REFERENCE);
			firePropertyChange(FILE_NAME_PROP_NAME, this.fileName, this.fileName = fileName);
		} catch (Exception e) {
			firePropertyChange(FILE_NAME_PROP_NAME, this.fileName, this.fileName = null);
			this.setManualCalibration(false);
			logger.error("Problem loading data for {}", fileName, e);
			throw new Exception("Problem loading data for " + fileName + " : " + e.getMessage());
		}
	}

}