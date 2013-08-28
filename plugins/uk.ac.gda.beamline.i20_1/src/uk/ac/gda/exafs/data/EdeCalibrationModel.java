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

import gda.scan.ede.EdeAsciiFileWriter;
import gda.util.exafs.Element;

import java.util.ArrayList;
import java.util.List;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.io.DataHolder;
import uk.ac.diamond.scisoft.analysis.io.LoaderFactory;

public class EdeCalibrationModel extends ObservableModel {
	public static final String REF_DATA_COLUMN_NAME = "/entry1/qexafs_counterTimer01/lnI0It";
	public static final String REF_ENERGY_COLUMN_NAME = "/entry1/qexafs_counterTimer01/qexafs_energy";
	public static final String REF_DATA_PATH = "/Foils_reference";
	public static final String REF_DATA_EXT = ".xmu";

	public static final EdeCalibrationModel INSTANCE = new EdeCalibrationModel();
	public static final String MANUAL_PROP_NAME = "manual";
	private boolean manual;
	private final ElementEdeData edeData = new ElementEdeData();
	private final ElementReference refData = new ElementReference();

	private EdeCalibrationModel() {}
	public ElementReference getRefData() {
		return refData;
	}
	public ElementEdeData getEdeData() {
		return edeData;
	}
	public boolean isManual() {
		return manual;
	}
	public void setManual(boolean manual) {
		firePropertyChange(MANUAL_PROP_NAME, this.manual, this.manual = manual);
	}

	public static class ElementEdeData extends ElementReference {
		@Override
		public void setData(String fileName) throws Exception {
			setData(fileName, LoaderFactory.getData(fileName), EdeAsciiFileWriter.STRIP_COLUMN_NAME, EdeAsciiFileWriter.LN_I0_IT_COLUMN_NAME);
		}

		@Override
		public void setSelectedElement(Element selectedElement) {
			firePropertyChange(SELECTED_ELEMENT_PROP_NAME, this.selectedElement, this.selectedElement = selectedElement);
		}
	}

	public static class ElementReference extends ObservableModel {

		public static final String SELECTED_ELEMENT_PROP_NAME = "selectedElement";
		protected Element selectedElement;

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

		public Element getSelectedElement() {
			return selectedElement;
		}

		public void setSelectedElement(Element selectedElement) {
			firePropertyChange(SELECTED_ELEMENT_PROP_NAME, this.selectedElement, this.selectedElement = selectedElement);
			// TODO Implement this when data is available
			//			String fileName = REF_DATA_PATH + "/" + this.selectedElement.getSymbol() + REF_DATA_EXT;
			//			File file = new File(fileName);
			//			if (file.exists() && file.canRead()) {
			//				try {
			//					setData(fileName);
			//				} catch (Exception e) {
			//					// TODO Handle this
			//				}
			//			}
		}

		public void setData(String fileName) throws Exception {
			DataHolder dataHolder = LoaderFactory.getData(fileName);
			if (dataHolder != null) {
				setData(fileName, dataHolder, EdeCalibrationModel.REF_ENERGY_COLUMN_NAME, EdeCalibrationModel.REF_DATA_COLUMN_NAME);
			} else {
				throw new Exception("Unable to load reference data from " + fileName);
			}
		}

		protected void setData(String fileName, DataHolder dataHolder, String energyNodePath, String dataNodePath) {
			String previousRefFile = this.fileName;
			this.fileName = fileName;
			this.dataHolder = dataHolder;
			energyNode = (AbstractDataset) this.dataHolder.getLazyDataset(energyNodePath).getSlice();
			dataNode = (AbstractDataset) this.dataHolder.getLazyDataset(dataNodePath).getSlice();
			loadReferencePoints();
			firePropertyChange(FILE_NAME_PROP_NAME, previousRefFile, this.fileName);
		}

		protected void loadReferencePoints() {
			refReferencePoints = new ArrayList<Double>(3);
			refReferencePoints.add(energyNode.min().doubleValue());
			refReferencePoints.add((Double) energyNode.mean());
			refReferencePoints.add(energyNode.max().doubleValue());
		}
	}
}

