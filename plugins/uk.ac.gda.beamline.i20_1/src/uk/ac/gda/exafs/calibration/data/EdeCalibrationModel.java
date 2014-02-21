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

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

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
}

