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

package uk.ac.gda.exafs.ui.data.experiment;

import uk.ac.gda.client.UIObservableModel;

import com.google.gson.annotations.Expose;

public class ExperimentDataModel extends UIObservableModel {
	public static final String I0_INTEGRATION_TIME_PROP_NAME = "i0IntegrationTime";
	@Expose
	private double i0IntegrationTime;

	public static final String I0_NUMBER_OF_ACCUMULATIONS_PROP_NAME = "i0NumberOfAccumulations";
	@Expose
	private int i0NumberOfAccumulations;

	public static final String IREF_INTEGRATION_TIME_PROP_NAME = "irefIntegrationTime";
	@Expose
	private double irefIntegrationTime = 1.0;

	public static final String IREF_NO_OF_ACCUMULATION_PROP_NAME = "irefNoOfAccumulations";
	@Expose
	private int irefNoOfAccumulations = 1;

	public static final String USE_NO_OF_ACCUMULATIONS_FOR_I0_PROP_NAME = "useNoOfAccumulationsForI0";
	@Expose
	private boolean useNoOfAccumulationsForI0 = false;

	public double getI0IntegrationTime() {
		return i0IntegrationTime;
	}

	public void setI0IntegrationTime(double value) {
		firePropertyChange(I0_INTEGRATION_TIME_PROP_NAME, i0IntegrationTime, i0IntegrationTime = value);
	}

	public int getI0NumberOfAccumulations() {
		return i0NumberOfAccumulations;
	}

	public void setI0NumberOfAccumulations(int value) {
		firePropertyChange(I0_NUMBER_OF_ACCUMULATIONS_PROP_NAME, i0NumberOfAccumulations, i0NumberOfAccumulations = value);
	}


	public double getIrefIntegrationTime() {
		return irefIntegrationTime;
	}

	public void setIrefIntegrationTime(double irefIntegrationTime) {
		this.firePropertyChange(IREF_INTEGRATION_TIME_PROP_NAME, this.irefIntegrationTime, this.irefIntegrationTime = irefIntegrationTime);
	}


	public int getIrefNoOfAccumulations() {
		return irefNoOfAccumulations;
	}

	public void setIrefNoOfAccumulations(int irefNoOfAccumulations) {
		this.firePropertyChange(IREF_NO_OF_ACCUMULATION_PROP_NAME, this.irefNoOfAccumulations, this.irefNoOfAccumulations = irefNoOfAccumulations);
	}


	public boolean isUseNoOfAccumulationsForI0() {
		return useNoOfAccumulationsForI0;
	}

	public void setUseNoOfAccumulationsForI0(boolean useNoOfAccumulationsForI0) {
		this.firePropertyChange(USE_NO_OF_ACCUMULATIONS_FOR_I0_PROP_NAME, this.useNoOfAccumulationsForI0, this.useNoOfAccumulationsForI0 = useNoOfAccumulationsForI0);
	}
}
