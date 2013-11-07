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

package uk.ac.gda.exafs.data;

import gda.configuration.properties.LocalProperties;
import gda.scan.ede.EdeExperiment;
import gda.util.exafs.AbsorptionEdge;
import gda.util.exafs.Element;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.File;
import java.util.ArrayList;
import java.util.List;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.io.DataHolder;
import uk.ac.diamond.scisoft.analysis.io.LoaderFactory;

public class EdeCalibrationModel extends ObservableModel {
	public static final String REF_DATA_COLUMN_NAME = "lnI0It";
	public static final String REF_ENERGY_COLUMN_NAME = "Energy";
	public static final String REF_DATA_PATH = LocalProperties.getVarDir() + "edeRefData";
	public static final String REF_DATA_EXT = ".dat";

	public static final EdeCalibrationModel INSTANCE = new EdeCalibrationModel();
	public static final String MANUAL_PROP_NAME = "manual";
	private boolean manual;
	private final EdeCalibrationDataModel edeData = new EdeCalibrationDataModel();
	private final ReferenceCalibrationDataModel refData = new ReferenceCalibrationDataModel();

	private EdeCalibrationModel() {
		AlignmentParametersModel.INSTANCE.addPropertyChangeListener(AlignmentParametersModel.ELEMENT_EDGE_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if (evt.getNewValue() != null) {
					refData.loadReferenceData(AlignmentParametersModel.INSTANCE.getElement(), ((AbsorptionEdge) evt.getNewValue()).getEdgeType());
				}
			}
		});
		if (AlignmentParametersModel.INSTANCE.getEdge() != null) {
			refData.loadReferenceData(AlignmentParametersModel.INSTANCE.getElement(), AlignmentParametersModel.INSTANCE.getEdge().getEdgeType());
		}
	}

	public ReferenceCalibrationDataModel getRefData() {
		return refData;
	}
	public EdeCalibrationDataModel getEdeData() {
		return edeData;
	}
	public boolean isManual() {
		return manual;
	}
	public void setManual(boolean manual) {
		firePropertyChange(MANUAL_PROP_NAME, this.manual, this.manual = manual);
	}

	public static class EdeCalibrationDataModel extends ReferenceCalibrationDataModel {
		@Override
		public void setData(String fileName) throws Exception {
			setData(fileName, EdeExperiment.STRIP_COLUMN_NAME, EdeExperiment.LN_I0_IT_COLUMN_NAME);
		}
	}

	public static class ReferenceCalibrationDataModel extends ObservableModel {
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
			File folder = new File(REF_DATA_PATH);
			if (!folder.exists() || !folder.canRead()) {
				return;
			}

			String fileName = element.getSymbol() + "_" + edgeName + REF_DATA_EXT;
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
}

