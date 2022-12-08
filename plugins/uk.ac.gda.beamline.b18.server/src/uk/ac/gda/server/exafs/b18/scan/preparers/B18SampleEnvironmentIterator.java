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

package uk.ac.gda.server.exafs.b18.scan.preparers;

import java.util.Date;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.SampleWheel;
import gda.jython.InterfaceProvider;
import uk.ac.gda.beans.exafs.b18.B18SampleParameters;
import uk.ac.gda.beans.exafs.b18.FurnaceParameters;
import uk.ac.gda.beans.exafs.b18.LN2CryoStageParameters;
import uk.ac.gda.beans.exafs.b18.LakeshoreParameters;
import uk.ac.gda.beans.exafs.b18.PulseTubeCryostatParameters;
import uk.ac.gda.beans.exafs.b18.SXCryoStageParameters;
import uk.ac.gda.beans.exafs.b18.SampleWheelParameters;
import uk.ac.gda.beans.exafs.b18.UserStageParameters;
import uk.ac.gda.beans.exafs.b18.XYThetaStageParameters;
import uk.ac.gda.server.exafs.scan.SampleParameterMotorMover;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;

public class B18SampleEnvironmentIterator implements SampleEnvironmentIterator {

	private static final Logger logger = LoggerFactory.getLogger(B18SampleEnvironmentIterator.class);

	private B18SampleParameters parameters;

	private Scannable sxcryo_scannable;

	private Scannable xytheta_scannable;

	private Scannable ln2cryo_scannable;

	private Scannable lakeshore_scannable;

	private Scannable furnace_scannable;

	private Scannable pulsetube_scannable;

	private Scannable samplewheel_scannable;

	private Scannable user_scannable;

	// Repetition counters. added 26/5/2016
	int currentScanRepetitionNumber; // scan repetitions (i.e. 'number of repeats' in command queue)
	int currentSampleRepetitionNumber; // sample environment iterations

	public B18SampleEnvironmentIterator(B18SampleParameters parameters, Scannable sxcryo_scannable,
			Scannable xytheta_scannable, Scannable ln2cryo_scannable, Scannable lakeshore_scannable,
			Scannable furnace_scannable, Scannable pulsetube_scannable, Scannable samplewheel_scannable,
			Scannable user_scannable) {
				this.parameters = parameters;
				this.sxcryo_scannable = sxcryo_scannable;
				this.xytheta_scannable = xytheta_scannable;
				this.ln2cryo_scannable = ln2cryo_scannable;
				this.lakeshore_scannable = lakeshore_scannable;
				this.furnace_scannable = furnace_scannable;
				this.pulsetube_scannable = pulsetube_scannable;
				this.samplewheel_scannable = samplewheel_scannable;
				this.user_scannable = user_scannable;

				currentScanRepetitionNumber = 0;
				currentSampleRepetitionNumber = 0;
	}

	@Override
	public int getNumberOfRepeats() {
		return 1;
	}

	@Override
	public void next() throws DeviceException, InterruptedException {

		boolean enabled = parameters.getSampleWheelParameters().isWheelEnabled();
		if (enabled) {
			control_sample_wheel(parameters.getSampleWheelParameters());
		}

		//If it's set, use generic motor position in preference to old sample stages.
		if (parameters.getSampleParameterMotorPositions().size() > 0) {
			SampleParameterMotorMover.moveMotors(parameters.getSampleParameterMotorPositions());
		} else {
			List<String> selectedStages = parameters.getSelectedSampleStages();
			if ( selectedStages != null && selectedStages.size() > 0 ) {
				for( String stage : selectedStages ) {
					moveSampleStage( stage );
				}
			}
			else {
				moveSampleStage( parameters.getStage() );
			}
		}
		if (parameters.getTemperatureControl() != "None") {
			if (parameters.getTemperatureControl().equals("furnace")) {
				control_furnace(parameters.getFurnaceParameters());
			} else if (parameters.getTemperatureControl().equals("lakeshore")) {
				control_lakeshore(parameters.getLakeshoreParameters());
			} else if (parameters.getTemperatureControl().equals("pulsetubecryostat")) {
				control_pulsetube(parameters.getPulseTubeCryostatParameters());
			}
		}
		currentSampleRepetitionNumber++;
	}

	private void moveSampleStage(String stage) throws DeviceException {
		if (stage.equals("xythetastage")) {
			control_xytheta_stage(parameters.getXYThetaStageParameters());
		} else if (stage.equals("ln2cryostage")) {
			control_ln2cryo_stage(parameters.getLN2CryoStageParameters());
		} else if (stage.equals("sxcryostage")) {
			control_sxcryo_stage(parameters.getSXCryoStageParameters());
		} else if (stage.equals("userstage")) {
			control_user_stage(parameters.getUserStageParameters());
		}
	}

	@Override
	public void resetIterator() {
		// Reset and increment repetition counters - called just before loop over sample environment
		currentScanRepetitionNumber++;
		currentSampleRepetitionNumber = 0;
	}

	public int getCurrentSampleRepetitionNumber() {
		return currentSampleRepetitionNumber;
	}

	public int getCurrentScanRepetitionNumber() {
		return currentScanRepetitionNumber;
	}

	@Override
	public String getNextSampleName() {
		return parameters.getName();
	}

	@Override
	public List<String> getNextSampleDescriptions() {
		return parameters.getDescriptions();
	}

	private Scannable[] control_furnace(FurnaceParameters furnace_bean) throws InterruptedException, DeviceException {
		log("furnace is the temperature controller");
		double temperature = furnace_bean.getTemperature();
		double tolerance = furnace_bean.getTolerance();
		double wait_time = furnace_bean.getTime();
		boolean only_read = furnace_bean.isControlFlag();
		// meta_add(self.furnace_scannable);
		if (!only_read) {
			log("controlling furnace");

			waitForValueToStabilise(temperature, tolerance, wait_time, furnace_scannable);
		}
		return new Scannable[] { furnace_scannable };
	}

	private void waitForValueToStabilise(double temperature, double tolerance, double wait_time,
			Scannable tempController) throws DeviceException, InterruptedException {
		// if (!only_read){
		tempController.moveTo(temperature);
		double min = temperature - tolerance;
		double max = temperature + tolerance;
		boolean temp_final = false;
		log("starting control loop");
		while (!temp_final) {
			double temp_readback = (Double) tempController.getPosition();
			if (temperatureInRequiredRange(min,max,temp_readback)) {
				log("Temperature reached, waiting for it to be stable...");
				boolean finalised = true;
				long startTime = new Date().getTime();
				while (finalised && stillWaiting(wait_time , startTime)) {
					log("Temperature stable");
					temp_readback = (Double) tempController.getPosition();
					if (!temperatureInRequiredRange(min,max,temp_readback)) {
						log("Temperature unstable");
						finalised = false;
					}
					Thread.sleep(1000);
				}
				if (finalised) {
					temp_final = true;
				}
			} else {
				log("Temperature = " + temp_readback);
				Thread.sleep(100);
			}
		}
		// }
	}

	private boolean temperatureInRequiredRange(double min, double max, double temp_readback) {
		return temp_readback > min && temp_readback < max;
	}

	private boolean stillWaiting(double wait_time_in_s, long start_of_wait) {
		long now = new Date().getTime();
		return (start_of_wait + (wait_time_in_s*1000)) > now;
	}

	private Scannable[] control_lakeshore(LakeshoreParameters lakeshore_bean) throws InterruptedException,
			DeviceException {
		log("Lakeshore is the temp controller");
//		boolean selectTemp0 = lakeshore_bean.isTempSelect0();
//		boolean selectTemp1 = lakeshore_bean.isTempSelect1();
//		boolean selectTemp2 = lakeshore_bean.isTempSelect2();
//		boolean selectTemp3 = lakeshore_bean.isTempSelect3();
		double temperature = lakeshore_bean.getSetPointSet();
		double tolerance = lakeshore_bean.getTolerance();
		double wait_time = lakeshore_bean.getTime();
		boolean only_read = lakeshore_bean.isControlFlag();
		// if (selectTemp0){
		// lakeshore_scannable.setTempSelect(0);
		// }
		// if (selectTemp1){
		// lakeshore_scannable.setTempSelect(1);
		// }
		// if (selectTemp2){
		// lakeshore_scannable.setTempSelect(2);
		// }
		// if (selectTemp3){
		// lakeshore_scannable.setTempSelect(3);
		// }
		// meta_add(lakeshore_scannable);

		if (!only_read) {
			log("controlling lakeshore");
			// if (selectTemp0){
			// lakeshore_scannable.rawAsynchronousMoveTo([[0], temp]);
			// }
			// if (selectTemp1){
			// lakeshore_scannable.rawAsynchronousMoveTo([[1], temp]);
			// }
			// if (selectTemp2){
			// lakeshore_scannable.rawAsynchronousMoveTo([[2], temp]);
			// }
			// if (selectTemp3){
			// lakeshore_scannable.rawAsynchronousMoveTo([[3], temp]);
			// }

			waitForValueToStabilise(temperature, tolerance, wait_time, lakeshore_scannable);
		}

		return new Scannable[] { lakeshore_scannable };
	}

	private Scannable[] control_pulsetube(PulseTubeCryostatParameters bean) throws DeviceException,
			InterruptedException {
		log("pulse tube is the temp controller");

		if (!bean.isControlFlag()) {
			double temp = bean.getSetPoint();
			pulsetube_scannable.asynchronousMoveTo(temp);
			double tolerance = bean.getTolerance();
			double wait_time = bean.getTime();

			waitForValueToStabilise(temp, tolerance, wait_time, pulsetube_scannable);

			double min = temp - tolerance;
			double max = temp + tolerance;
			boolean temp_final = false;
			log("starting temperature control loop");
			while (!temp_final) {
				double temp_readback = ((double[]) pulsetube_scannable.getPosition())[0];
				if (temp_readback >= min && temp_readback <= max) {
					log("Temperature reached, checking if it has stabilised");
					boolean finalised = true;
					int time = 0;
					while (finalised && time < wait_time) {
						log("Temperature stable");
						temp_readback = ((double[]) pulsetube_scannable.getPosition())[0];
						if (temp_readback < min || temp_readback > max) {
							log("Temperature unstable");
							finalised = false;
						}
						time += 1;
						Thread.sleep(1000);
					}
					if (finalised) {
						temp_final = true;
					}
				} else {
					log("Temperature = " + ((double[]) pulsetube_scannable.getPosition())[0]);
					Thread.sleep(1000);
				}
			}
		}
		return new Scannable[] { pulsetube_scannable };
	}

	private void control_sxcryo_stage(SXCryoStageParameters bean) throws DeviceException {
		double[] targetPosition;
		if (bean.isManual()) {
			targetPosition = new double[] { bean.getHeight(), bean.getRot() };
		} else {
			int sample = bean.getSampleNumber();
			double offset = bean.getCalibHeight();
			double height = offset + ((sample - 1) * -15.5);
			targetPosition = new double[] { height, bean.getRot() };
		}
		log("moving sxcryostage (" + sxcryo_scannable.getName() + ") to " + doubleArrayToString(targetPosition));
		sxcryo_scannable.moveTo(targetPosition);
		log("sxcryostage move complete.");
	}

	private String doubleArrayToString(double[] array){
		StringBuffer buf = new StringBuffer();
		for(double element: array){
			buf.append(String.format("%.2f", element) + "\t");
		}
		return buf.toString();
	}

	private void control_xytheta_stage(XYThetaStageParameters bean) throws DeviceException {
		double[] targetPosition = new double[] { bean.getX(), bean.getY(), bean.getTheta() };
		log("moving xythetastage (" + xytheta_scannable.getName() + ") to " + doubleArrayToString(targetPosition));
		xytheta_scannable.moveTo(targetPosition);
		log("xythetastage move complete.");
	}

	private void control_user_stage(UserStageParameters bean) throws DeviceException {
		double[] targetPosition = new double[] { bean.getAxis2(), bean.getAxis4(), bean.getAxis5(), bean.getAxis6(),
				bean.getAxis7(), bean.getAxis8() };
		log("moving userstage (" + user_scannable.getName() + ") to " + doubleArrayToString(targetPosition));
		user_scannable.moveTo(targetPosition);
		log("userstage move complete.");
	}

	private void control_ln2cryo_stage(LN2CryoStageParameters bean) throws DeviceException {
		if (bean.isManual()) {
			double[] targetPosition = new double[] { bean.getHeight(), bean.getAngle() };
			log("moving ln2cryostage (" + ln2cryo_scannable.getName() + ") to " + doubleArrayToString(targetPosition));
			ln2cryo_scannable.moveTo(targetPosition);
			log("ln2cryostage move complete.");
		} else {
			int sampleNumberA = bean.getSampleNumberA();
			int sampleNumberB = bean.getSampleNumberB();
			String cylinderType = bean.getCylinderType();
			double height = bean.getCalibHeight() + (sampleNumberA - 1) * 17.0;
			double angleOffset = bean.getCalibAngle();
			double angle = 0;
			if (cylinderType.equals("trans")) {
				log("moving ln2 cryo transmission to " + sampleNumberA + ", " + sampleNumberB);
				angle = angleOffset + ((sampleNumberB - 1) * 16.36);
			} else if (cylinderType.equals("fluo")) {
				log("moving ln2 cryo fluorescence to " + sampleNumberA + ", " + sampleNumberB);
				if (sampleNumberB < 5) {
					angle = angleOffset + ((sampleNumberB - 1) * 22.5);
				} else {
					angle = angleOffset + 180.0 + ((sampleNumberB - 5) * 22.5);
				}
				double[] targetPosition = new double[] { height, angle };
				log("Target positions = " + doubleArrayToString(targetPosition));
				ln2cryo_scannable.moveTo(targetPosition);
			}
		}
	}

	private void control_sample_wheel(SampleWheelParameters bean) throws DeviceException, InterruptedException {
		if (bean.isManual()) {
			double demand = bean.getDemand();
			log("moving sample wheel to " + demand);
			samplewheel_scannable.moveTo(demand);
		} else {
			String filter = bean.getFilter();
			log("moving sample wheel to " + filter);
			// Move to named filter, block until finished
			((SampleWheel) samplewheel_scannable).moveToFilter(filter);
			((SampleWheel) samplewheel_scannable).waitWhileBusy();
		}
		log("sample wheel move complete");
	}

	private void log(String msg) {
		logger.info(msg);
		InterfaceProvider.getTerminalPrinter().print(msg);
	}

}
