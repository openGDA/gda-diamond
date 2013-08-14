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

import gda.jython.InterfaceProvider;
import gda.jython.JythonServerStatus;
import gda.observable.IObserver;
import uk.ac.gda.exafs.data.ClientConfig.ScannableSetup;

public class SlitScanner extends ObservableModel implements IObserver {

	private static SlitScanner INSTANCE;

	//TODO Find out values or refactor

	public static final double MAX_OFFSET = 1000.0;
	public static final double MIN_OFFSET = -1000.0;
	public static final double MAX_GAP = 1000.0;
	public static final double MIN_GAP = 0.00;

	public static final double MAX_INTEGRATION_TIME = 60 * 1000.0;
	public static final double MIN_INTEGRATION_TIME = 0.0001;

	public static final String STATE_PROP_NAME = "state";
	private int state;

	public static final String GAP_PROP_NAME = "gap";
	private double gap;

	public static final String FROM_OFFSET_PROP_NAME = "fromOffset";
	private double fromOffset;

	public static final String TO_OFFSET_PROP_NAME = "toOffset";
	private double toOffset;

	public static final String STEP_PROP_NAME = "step";
	private double step;

	public static final String INTEGRATION_TIME_PROP_NAME = "integrationTime";
	private double integrationTime = 1;

	private SlitScanner() {
		InterfaceProvider.getJSFObserver().addIObserver(this);
	}

	public static SlitScanner getInstance() {
		if (INSTANCE == null) {
			INSTANCE = new SlitScanner();
		}
		return INSTANCE;
	}

	public static boolean isGapInRange(double value) {
		return (MIN_GAP <= value & value <= MAX_GAP);
	}

	public int getState() {
		return state;
	}

	protected void setState(int value) {
		this.firePropertyChange(STATE_PROP_NAME, state, state = value);
	}
	public double getGap() {
		return gap;
	}

	public void setGap(double value) {
		this.firePropertyChange(GAP_PROP_NAME, gap, gap = value);
	}

	public double getFromOffset() {
		return fromOffset;
	}

	public void setFromOffset(double value) {
		this.firePropertyChange(FROM_OFFSET_PROP_NAME, fromOffset, fromOffset = value);
	}

	public double getToOffset() {
		return toOffset;
	}

	public void setToOffset(double value) {
		this.firePropertyChange(TO_OFFSET_PROP_NAME, toOffset, toOffset = value);
	}

	public double getIntegrationTime() {
		return integrationTime;
	}

	public void setIntegrationTime(double value) {
		this.firePropertyChange(INTEGRATION_TIME_PROP_NAME, integrationTime, integrationTime = value);
	}

	public double getStep() {
		return step;
	}

	public void setStep(double value) {
		this.firePropertyChange(STEP_PROP_NAME, step, step = value);
	}

	private String buildScanCommand() {
		double integrationTimeInS = (integrationTime) / ClientConfig.KILO_UNIT;
		return String.format("xh.loadParameters(EdeScanParameters.createSingleFrameScan(%f));scan %s %f %f %f %s %f %s", integrationTimeInS, ScannableSetup.SLIT_3_HORIZONAL_OFFSET.getScannableName(), fromOffset, toOffset, step, ScannableSetup.SLIT_3_HORIZONAL_GAP.getScannableName(), gap, DetectorConfig.INSTANCE.getCurrentDetector().getName());
	}

	public void doScan() throws DetectorUnavailableException {
		if (DetectorConfig.INSTANCE.getCurrentDetector() == null) {
			throw new DetectorUnavailableException();
		}
		InterfaceProvider.getCommandRunner().runCommand(buildScanCommand());
	}

	@Override
	public void update(Object source, Object arg) {
		if (arg instanceof JythonServerStatus) {
			JythonServerStatus status = (JythonServerStatus) arg;
			setState(status.scanStatus);
		}
	}

	public void save() throws DetectorUnavailableException {
		if (DetectorConfig.INSTANCE.getCurrentDetector() == null) {
			throw new DetectorUnavailableException();
		}
		InterfaceProvider.getCommandRunner().runCommand("alignment_stage.saveDeviceFromCurrentMotorPositions(\"slits\")");
	}
}
