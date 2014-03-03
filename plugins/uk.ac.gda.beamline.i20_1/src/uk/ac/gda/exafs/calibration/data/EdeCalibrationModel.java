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

package uk.ac.gda.exafs.calibration.data;

import gda.configuration.properties.LocalProperties;
import gda.util.exafs.AbsorptionEdge;
import gda.util.exafs.Element;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.File;

import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.exafs.data.AlignmentParametersModel;

public class EdeCalibrationModel extends ObservableModel {
	public static final String REF_DATA_COLUMN_NAME = "lnI0It";
	public static final String REF_ENERGY_COLUMN_NAME = "Energy";
	public static final String REF_DATA_PATH = LocalProperties.getVarDir() + "edeRefData";
	public static final String REF_DATA_EXT = ".dat";

	public static final EdeCalibrationModel INSTANCE = new EdeCalibrationModel();
	public static final String MANUAL_PROP_NAME = "manual";
	private boolean manual;
	private final EdeCalibrationDataModel edeData = new EdeCalibrationDataModel();
	private final CalibrationDataModel refData = new CalibrationDataModel();

	private EdeCalibrationModel() {
		AlignmentParametersModel.INSTANCE.addPropertyChangeListener(AlignmentParametersModel.ELEMENT_EDGE_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if (evt.getNewValue() != null) {
					loadReferenceData(AlignmentParametersModel.INSTANCE.getElement(), ((AbsorptionEdge) evt.getNewValue()).getEdgeType());
				}
			}
		});
		if (AlignmentParametersModel.INSTANCE.getEdge() != null) {
			loadReferenceData(AlignmentParametersModel.INSTANCE.getElement(), AlignmentParametersModel.INSTANCE.getEdge().getEdgeType());
		}
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
				refData.setDataFile(file.getAbsolutePath());
			} catch (Exception e) {
				// TODO Handle this
			}
		}
	}

	public CalibrationDataModel getRefData() {
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
}

