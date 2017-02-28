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

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import com.google.gson.annotations.Expose;

import gda.jython.InterfaceProvider;
import gda.jython.Jython;
import gda.jython.JythonServerStatus;
import gda.observable.IObserver;
import uk.ac.gda.beans.ObservableModel;

public class SlitsScanModel extends ObservableModel implements IObserver {

	private static SlitsScanModel INSTANCE;

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
	@Expose
	private double gap;

	public static final String FROM_OFFSET_PROP_NAME = "fromOffset";
	@Expose
	private double fromOffset;

	public static final String TO_OFFSET_PROP_NAME = "toOffset";
	@Expose
	private double toOffset;

	public static final String STEP_PROP_NAME = "step";
	@Expose
	private double step;

	public static final String INTEGRATION_TIME_PROP_NAME = "integrationTime";

	private static final String SLITS_SCAN_MODEL_DATA_STORE_KEY = "SLITS_SCAN_DATA";
	@Expose
	private double integrationTime = 1.0;

	private SlitsScanModel() {
		InterfaceProvider.getJSFObserver().addIObserver(this);
	}

	public static SlitsScanModel getInstance() {
		if (INSTANCE == null) {
			INSTANCE = new SlitsScanModel();
			SlitsScanModel slitScannerModel = EdeDataStore.INSTANCE.getPreferenceDataStore().loadConfiguration(SLITS_SCAN_MODEL_DATA_STORE_KEY, SlitsScanModel.class);
			if (slitScannerModel != null) {
				INSTANCE.setGap(slitScannerModel.getGap());
				INSTANCE.setFromOffset(slitScannerModel.getFromOffset());
				INSTANCE.setToOffset(slitScannerModel.getToOffset());
				INSTANCE.setStep(slitScannerModel.getStep());
				INSTANCE.setIntegrationTime(slitScannerModel.getIntegrationTime());
			}
			INSTANCE.addPropertyChangeListener(new PropertyChangeListener() {
				@Override
				public void propertyChange(PropertyChangeEvent evt) {
					EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(SLITS_SCAN_MODEL_DATA_STORE_KEY, SlitsScanModel.INSTANCE);
				}
			});
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
		double integrationTimeInS = integrationTime;
		return String.format("scan %s %f %f %f %s %f %s %f",
				ScannableSetup.SLIT_3_HORIZONAL_OFFSET.getScannableName(),
				fromOffset,
				toOffset,
				step,
				ScannableSetup.SLIT_3_HORIZONAL_GAP.getScannableName(),
				gap,
				DetectorModel.INSTANCE.getCurrentStepScanDetector().getName(),
				integrationTimeInS);
	}

	public void doScan() throws DetectorUnavailableException {
		if (DetectorModel.INSTANCE.getCurrentDetector() == null) {
			throw new DetectorUnavailableException();
		}
		String command = buildScanCommand();
		InterfaceProvider.getTerminalPrinter().print(String.format("\n%s\n",command));
		InterfaceProvider.getCommandRunner().runCommand(command);
	}

	@Override
	public void update(Object source, Object arg) {
		if (arg instanceof JythonServerStatus) {
			JythonServerStatus status = (JythonServerStatus) arg;
			setState(status.scanStatus);
		}
	}

	public void saveSlitsPosToAlignmentStage() throws DetectorUnavailableException {
		if (DetectorModel.INSTANCE.getCurrentDetector() == null) {
			throw new DetectorUnavailableException();
		}
		InterfaceProvider.getCommandRunner().runCommand("alignment_stage.saveDeviceFromCurrentMotorPositions(\"slits\")");
	}

	public void stopScan() {
		if (this.getState() != Jython.IDLE) {
			InterfaceProvider.getCurrentScanController().requestFinishEarly();
		}
	}
}
