/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package gda.exafs.scan;

import gda.data.scan.datawriter.NexusExtraMetadataDataWriter;
import gda.data.scan.datawriter.NexusFileMetadata;
import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.Scannable;
import gda.device.Temperature;
import gda.device.scannable.scannablegroup.ScannableGroup;
import gda.factory.Finder;
import gda.jython.scriptcontroller.event.ScriptProgressEvent;
import gda.observable.ObservableComponent;

import java.lang.reflect.Method;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beans.exafs.i20.CryostatParameters;
import uk.ac.gda.beans.exafs.i20.I20SampleParameters;
import uk.ac.gda.beans.exafs.i20.MicroreactorParameters;
import uk.ac.gda.beans.exafs.i20.SampleStageParameters;
import uk.ac.gda.devices.cirrus.CirrusDetector;

/**
 * Now replaced by Jython scripts - the logic in here is too variable
 * 
 */
@Deprecated()
public class I20SampleParametersManager extends ParametersManager {

	private static final Logger logger = LoggerFactory.getLogger(I20SampleParametersManager.class);

	private final I20SampleParameters sampleParameters;
	private final ObservableComponent controller;

	public I20SampleParametersManager(I20SampleParameters sampleParameters, ObservableComponent controller) {
		super();
		this.sampleParameters = sampleParameters;
		this.controller = controller;
	}

	/**
	 * Call to configure the sample.
	 * 
	 * @throws Exception
	 */
	@Override
	public void init() throws Exception {
		createSampleEnvironment();
	}

	private void log(String message) {
		if (this.controller != null) {
			controller.notifyIObservers(this, new ScriptProgressEvent(message));
		}
		logger.info(message);
	}

	private void createSampleEnvironment() throws Exception {

		NexusExtraMetadataDataWriter.removeAllMetadataEntries();

		final String sampleEnv = sampleParameters.getSampleEnvironment();

		if (I20SampleParameters.SAMPLE_ENV[1].equals(sampleEnv)) { // Room
			log("Moving Sample Table");
			final SampleStageParameters roomTemp = sampleParameters.getRoomTemperatureParameters();
			setScannable("sample_x", roomTemp.getX());
			setScannable("sample_y", roomTemp.getY());
			setScannable("sample_z", roomTemp.getZ());
			setScannable("sample_rot", roomTemp.getRotation());
			setScannable("sample_pitch", roomTemp.getRoll());
			setScannable("sample_roll", roomTemp.getYaw());

			NexusExtraMetadataDataWriter.addMetadataEntry(new NexusFileMetadata("x", roomTemp.getX().toString(),
					NexusFileMetadata.EntryTypes.NXinstrument, NexusFileMetadata.NXinstrumentSubTypes.NXpositioner,
					"sampletable"));
			NexusExtraMetadataDataWriter.addMetadataEntry(new NexusFileMetadata("y", roomTemp.getY().toString(),
					NexusFileMetadata.EntryTypes.NXinstrument, NexusFileMetadata.NXinstrumentSubTypes.NXpositioner,
					"sampletable"));
			NexusExtraMetadataDataWriter.addMetadataEntry(new NexusFileMetadata("z", roomTemp.getZ().toString(),
					NexusFileMetadata.EntryTypes.NXinstrument, NexusFileMetadata.NXinstrumentSubTypes.NXpositioner,
					"sampletable"));
			NexusExtraMetadataDataWriter.addMetadataEntry(new NexusFileMetadata("rot", roomTemp.getRotation().toString(),
					NexusFileMetadata.EntryTypes.NXinstrument, NexusFileMetadata.NXinstrumentSubTypes.NXpositioner,
					"sampletable"));
			NexusExtraMetadataDataWriter.addMetadataEntry(new NexusFileMetadata("yaw", roomTemp.getYaw().toString(),
					NexusFileMetadata.EntryTypes.NXinstrument, NexusFileMetadata.NXinstrumentSubTypes.NXpositioner,
					"sampletable"));
			NexusExtraMetadataDataWriter.addMetadataEntry(new NexusFileMetadata("roll", roomTemp.getRoll().toString(),
					NexusFileMetadata.EntryTypes.NXinstrument, NexusFileMetadata.NXinstrumentSubTypes.NXpositioner,
					"sampletable"));
		} else if (I20SampleParameters.SAMPLE_ENV[2].equals(sampleEnv)) {
			log("Preparing cryostat for experiment");

			final CryostatParameters cryo = sampleParameters.getCryostatParameters();
			final Temperature temp = (Temperature) Finder.getInstance().find("Clake");
			if (temp != null) {
				temp.setTargetTemperature(cryo.getTemperature());
				scannables.add(temp);
			} else {
				log("Clake could not be found in Jython namespace- cryostat not configured");
			}
		} else if (I20SampleParameters.SAMPLE_ENV[4].equals(sampleEnv)) {

			log("Preparing MicroReactor for experiment");
			final ScannableGroup microreactor = (ScannableGroup) Finder.getInstance().find("microreactor");
			final CirrusDetector cirrus = (CirrusDetector) Finder.getInstance().find("cirrus");

			if (microreactor == null) {
				log("Microreactor could not be found in Jython namespace - microreactor will not be setup");
				return;
			}
			if (cirrus == null) {
				log("Mass Spectrometer could not be found in Jython namespace - cirrus will not be setup");
				return;
			}

			this.scannables.add(microreactor);
			this.scannables.add(cirrus);

			MicroreactorParameters params = sampleParameters.getMicroreactorParameters();

			for (int flowRate = 0; flowRate < 7; flowRate++) {

				@SuppressWarnings("all")
				Method getter = MicroreactorParameters.class.getMethod("getGas" + flowRate + "Rate", null);
				Integer result = (Integer) getter.invoke(params, new Object[] {});

				if (result > 0) {
					Scannable thisFlowController = microreactor.getGroupMember("flow" + flowRate);
					thisFlowController.asynchronousMoveTo(result);
				}
			}
			int temperature = params.getTemperature();
			Scannable thisFlowController = microreactor.getGroupMember("temperature");
			thisFlowController.asynchronousMoveTo(temperature);
			
			Integer[] masses = params.getIntegerMasses();
			cirrus.setMasses(masses);
		}

		String sampleWheelPosition = sampleParameters.getSampleWheelPosition();
		if (sampleWheelPosition != null && !sampleWheelPosition.isEmpty()) {
			try {
				final EnumPositioner sampleWheel = (EnumPositioner) Finder.getInstance().find(
						I20SampleParameters.SAMPLE_WHEEL_NAME);
				if (sampleWheel == null){
					logger.error(I20SampleParameters.SAMPLE_WHEEL_NAME + " not found. It's position could not be set to " + sampleWheelPosition);
				} else {
				sampleWheel.moveTo(sampleWheelPosition);
				this.scannables.add(sampleWheel);
				}
			} catch (Exception e) {
				logger.error("Exception trying to move " + I20SampleParameters.SAMPLE_WHEEL_NAME + " to " + sampleWheelPosition, e);
			}
		}
		
		// loop until finished or exception thrown
		waitWhileBusy();
	}

	/**
	 * @return - The temperature of the sample in K
	 * @throws DeviceException
	 */
	public double getTemperature() throws DeviceException {

		final String sampleEnv = sampleParameters.getSampleEnvironment();
		if (I20SampleParameters.SAMPLE_ENV[2].equals(sampleEnv)) { // Cryo
			final Temperature temp = Finder.getInstance().find("Clake");
			return temp.getCurrentTemperature();

		} else if (I20SampleParameters.SAMPLE_ENV[3].equals(sampleEnv)) { // Furnace
			// TODO
			return 300d;

		}

		return -1d;
	}
}
