package uk.ac.gda.server.exafs.scan.preparers;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.jython.InterfaceProvider;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.b18.B18SampleParameters;
import uk.ac.gda.beans.exafs.b18.FurnaceParameters;
import uk.ac.gda.beans.exafs.b18.LN2CryoStageParameters;
import uk.ac.gda.beans.exafs.b18.LakeshoreParameters;
import uk.ac.gda.beans.exafs.b18.PulseTubeCryostatParameters;
import uk.ac.gda.beans.exafs.b18.SXCryoStageParameters;
import uk.ac.gda.beans.exafs.b18.SampleWheelParameters;
import uk.ac.gda.beans.exafs.b18.UserStageParameters;
import uk.ac.gda.beans.exafs.b18.XYThetaStageParameters;
import uk.ac.gda.server.exafs.scan.SampleEnvironmentPreparer;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;

public class B18SamplePreparer implements SampleEnvironmentPreparer {

	private static Logger logger = LoggerFactory.getLogger(B18SamplePreparer.class);
	
	private Scannable sxcryo_scannable;
	private Scannable xytheta_scannable;
	private Scannable ln2cryo_scannable;
	private Scannable lakeshore_scannable;
	private Scannable furnace_scannable;
	private Scannable pulsetube_scannable;
	private Scannable samplewheel_scannable;
	private Scannable user_scannable;
	private boolean logging_enabled;

	public B18SamplePreparer(Scannable sxcryo_scannable, Scannable xytheta_scannable, Scannable ln2cryo_scannable,
			Scannable lakeshore_scannable, Scannable furnace_scannable, Scannable pulsetube_scannable,
			Scannable samplewheel_scannable, Scannable user_scannable) {

		this.sxcryo_scannable = sxcryo_scannable;
		this.xytheta_scannable = xytheta_scannable;
		this.ln2cryo_scannable = ln2cryo_scannable;
		this.lakeshore_scannable = lakeshore_scannable;
		this.furnace_scannable = furnace_scannable;
		this.pulsetube_scannable = pulsetube_scannable;
		this.samplewheel_scannable = samplewheel_scannable;
		this.user_scannable = user_scannable;
		logging_enabled = true;
	}

	private void log(String msg) {
		if (logging_enabled) {
			logger.info(msg);
			InterfaceProvider.getTerminalPrinter().print(msg);
		} else {
			InterfaceProvider.getTerminalPrinter().print(msg);
		}
	}

	@Override
	public void prepare(ISampleParameters sampleParameters) throws Exception {

		B18SampleParameters parameters = (B18SampleParameters) sampleParameters;
		
		boolean enabled = parameters.getSampleWheelParameters().isWheelEnabled();
		if (enabled) {
			_control_sample_wheel(parameters.getSampleWheelParameters());
		}

		if (parameters.getStage().equals("xythetastage")) {
			_control_xytheta_stage(parameters.getXYThetaStageParameters());
		} else if (parameters.getStage().equals("ln2cryostage")) {
			_control_ln2cryo_stage(parameters.getLN2CryoStageParameters());
		} else if (parameters.getStage().equals("sxcryostage")) {
			_control_sxcryo_stage(parameters.getSXCryoStageParameters());
		} else if (parameters.getStage().equals("userstage")) {
			_control_user_stage(parameters.getUserStageParameters());
		}

		if (parameters.getTemperatureControl() != "None") {
			if (parameters.getTemperatureControl().equals("furnace")) {
				/* return */_control_furnace(parameters.getFurnaceParameters());
			} else if (parameters.getTemperatureControl().equals("lakeshore")) {
				/* return */_control_lakeshore(parameters.getLakeshoreParameters());
			} else if (parameters.getTemperatureControl().equals("pulsetubecryostat")) {
				/* return */_control_pulsetube(parameters.getPulseTubeCryostatParameters());
			}
		}
	}

	private Scannable[] _control_furnace(FurnaceParameters furnace_bean) throws InterruptedException, DeviceException {
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
			if (temp_readback > min && temp_readback < max) {
				log("Temperature reached, checking if it has stablised");
				boolean finalised = true;
				int time = 0;
				while (finalised && time < wait_time) {
					log("Temperature stable");
					temp_readback = (Double) tempController.getPosition();
					if (temp_readback < min || temp_readback > max) {
						log("Temperature unstable");
						finalised = false;
					}
					time += 1;
					Thread.sleep(1);
				}
				if (finalised) {
					temp_final = true;
				}
			} else {
				log("Temperature = " + temp_readback);
				Thread.sleep(1000);
			}
		}
		// }
	}

	private Scannable[] _control_lakeshore(LakeshoreParameters lakeshore_bean) throws InterruptedException,
			DeviceException {
		log("Lakeshore is the temp controller");
		boolean selectTemp0 = lakeshore_bean.isTempSelect0();
		boolean selectTemp1 = lakeshore_bean.isTempSelect1();
		boolean selectTemp2 = lakeshore_bean.isTempSelect2();
		;
		boolean selectTemp3 = lakeshore_bean.isTempSelect3();
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

	private Scannable[] _control_pulsetube(PulseTubeCryostatParameters bean) throws DeviceException,
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

	private void _control_sxcryo_stage(SXCryoStageParameters bean) throws DeviceException {
		double[] targetPosition;
		if (bean.isManual()) {
			targetPosition = new double[] { bean.getHeight(), bean.getRot() };
		} else {
			int sample = bean.getSampleNumber();
			double offset = bean.getCalibHeight();
			double height = offset + ((sample - 1) * -15.5);
			targetPosition = new double[] { height, bean.getRot() };
		}
		log("moving sxcryostage (" + sxcryo_scannable.getName() + ") to " + targetPosition);
		sxcryo_scannable.moveTo(targetPosition);
		log("sxcryostage move complete.");
	}

	private void _control_xytheta_stage(XYThetaStageParameters bean) throws DeviceException {
		double[] targetPosition = new double[] { bean.getX(), bean.getY(), bean.getTheta() };
		log("moving xythetastage (" + xytheta_scannable.getName() + ") to " + targetPosition);
		xytheta_scannable.moveTo(targetPosition);
		log("xythetastage move complete.");
	}

	private void _control_user_stage(UserStageParameters bean) throws DeviceException {
		double[] targetPosition = new double[] { bean.getAxis2(), bean.getAxis4(), bean.getAxis5(), bean.getAxis6(),
				bean.getAxis7(), bean.getAxis8() };
		log("moving userstage (" + user_scannable.getName() + ") to " + targetPosition);
		user_scannable.moveTo(targetPosition);
		log("userstage move complete.");
	}

	private void _control_ln2cryo_stage(LN2CryoStageParameters bean) throws DeviceException {
		if (bean.isManual()) {
			double[] targetPosition = new double[] { bean.getHeight(), bean.getAngle() };
			log("moving ln2cryostage (" + ln2cryo_scannable.getName() + ") to " + targetPosition);
			ln2cryo_scannable.moveTo(targetPosition);
			log("ln2cryostage move complete.");
		} else {
			int sampleNumberA = bean.getSampleNumberA();
			int sampleNumberB = bean.getSampleNumberB();
			String cylinderType = bean.getCylinderType();
			double height = bean.getCalibHeight() + (sampleNumberA - 1) * 17.0;
			double angleOffset = bean.getCalibAngle();
			double angle = 0;
			if (cylinderType == "trans") {
				log("moving ln2 cryo transmission to " + sampleNumberA + ", " + sampleNumberB);
				angle = angleOffset + ((sampleNumberB - 1) * 16.36);
			} else if (cylinderType == "fluo") {
				log("moving ln2 cryo fluoresence to " + sampleNumberA + ", " + sampleNumberB);
				if (sampleNumberB < 5) {
					angle = angleOffset + ((sampleNumberB - 1) * 22.5);
				} else {
					angle = angleOffset + 180.0 + ((sampleNumberB - 5) * 22.5);
				}
				Double[] targetPosition = new Double[] { height, angle };
				log("Target positions = " + targetPosition);
				ln2cryo_scannable.moveTo(targetPosition);
			}
		}
	}

	private void _control_sample_wheel(SampleWheelParameters bean) throws DeviceException {
		if (bean.isManual()) {
			double demand = bean.getDemand();
			log("moving sample wheel to " + demand);
			samplewheel_scannable.moveTo(demand);
		} else {
			String filter = bean.getFilter();
			log("moving sample wheel to " + filter);
			samplewheel_scannable.moveTo(filter);
		}
		// print "sample wheel move complete";
	}

	@Override
	public SampleEnvironmentIterator createIterator(String experimentType) {
		return null;
	}
}