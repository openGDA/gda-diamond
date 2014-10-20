package uk.ac.gda.server.exafs.scan.preparers;

import gda.configuration.properties.LocalProperties;
import gda.data.scan.datawriter.DataWriter;
import gda.data.scan.datawriter.DataWriterFactory;
import gda.data.scan.datawriter.DefaultDataWriterFactory;
import gda.data.scan.datawriter.XasAsciiNexusDataWriter;
import gda.device.Scannable;
import gda.device.detector.BufferedDetector;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.mythen.MythenDetectorImpl;
import gda.device.detector.xmap.Xmap;
import gda.device.detector.xspress.Xspress2Detector;
import gda.exafs.scan.ExafsScanPointCreator;
import gda.exafs.scan.XanesScanPointCreator;
import gda.jython.InterfaceProvider;
import gda.scan.StaticScan;

import java.util.List;

import org.apache.commons.lang.ArrayUtils;

import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IExperimentDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.TransmissionParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.devices.detector.xspress3.Xspress3Detector;
import uk.ac.gda.server.exafs.scan.QexafsDetectorPreparer;

public class B18DetectorPreparer implements QexafsDetectorPreparer {

	private Scannable energy_scannable;
	private MythenDetectorImpl mythen_scannable;
	private Scannable[] sensitivities;
	private Scannable[] sensitivity_units;
	private Scannable[] offsets;
	private Scannable[] offset_units;
	private List<Scannable> ionc_gas_injector_scannables;
	private Xspress2Detector xspressSystem;
	private Xmap vortexConfig;
	private Xspress3Detector xspress3Config;
	private IScanParameters scanBean;
	private TfgScalerWithFrames ionchambers;
	private IDetectorParameters detectorBean;

	// QEXAFS options
	private boolean gmsd_enabled;
	private boolean additional_channels_enabled;

	public B18DetectorPreparer(Scannable energy_scannable, MythenDetectorImpl mythen_scannable,
			Scannable[] sensitivities, Scannable[] sensitivity_units, Scannable[] offsets, Scannable[] offset_units,
			List<Scannable> ionc_gas_injector_scannables, TfgScalerWithFrames ionchambers,
			Xspress2Detector xspressSystem, Xmap vortexConfig, Xspress3Detector xspress3Config) {
		this.energy_scannable = energy_scannable;
		this.mythen_scannable = mythen_scannable;
		this.sensitivities = sensitivities;
		this.sensitivity_units = sensitivity_units;
		this.offsets = offsets;
		this.offset_units = offset_units;
		this.ionc_gas_injector_scannables = ionc_gas_injector_scannables;
		this.ionchambers = ionchambers;
		this.xspressSystem = xspressSystem;
		this.vortexConfig = vortexConfig;
		this.xspress3Config = xspress3Config;
	}

	@Override
	public void configure(IScanParameters scanBean, IDetectorParameters detectorBean, IOutputParameters outputBean,
			String experimentFullPath) throws Exception {

		this.scanBean = scanBean;
		this.detectorBean = detectorBean;

		if (detectorBean.getExperimentType().equalsIgnoreCase("Fluorescence")) {
			FluorescenceParameters fluoresenceParameters = detectorBean.getFluorescenceParameters();
			if (fluoresenceParameters.isCollectDiffractionImages()) {
				control_mythen(fluoresenceParameters, outputBean, experimentFullPath);
			}
			String detType = fluoresenceParameters.getDetectorType();
			String xmlFileName = experimentFullPath + fluoresenceParameters.getConfigFileName();
			if (detType == "Germanium") {
				xspressSystem.setConfigFileName(xmlFileName);
				xspressSystem.configure();
			} else if (detType == "Silicon") {
				vortexConfig.setConfigFileName(xmlFileName);
				vortexConfig.configure();
			} else if (detType == "Xspress3") {
				xspress3Config.setConfigFileName(xmlFileName);
				xspress3Config.configure();
			}
			control_all_ionc(fluoresenceParameters.getIonChamberParameters());
		} else if (detectorBean.getExperimentType().equalsIgnoreCase("Transmission")) {
			TransmissionParameters transmissionParameters = detectorBean.getTransmissionParameters();
			if (transmissionParameters.isCollectDiffractionImages()) {
				control_mythen(transmissionParameters, outputBean, experimentFullPath);
			}
			control_all_ionc(transmissionParameters.getIonChamberParameters());
		}
	}

	@Override
	public void beforeEachRepetition() throws Exception {
		Double[] times = new Double[] {};
		if (scanBean instanceof XasScanParameters) {
			times = ExafsScanPointCreator.getScanTimeArray((XasScanParameters) scanBean);
		} else if (scanBean instanceof XanesScanParameters) {
			times = XanesScanPointCreator.getScanTimeArray((XanesScanParameters) scanBean);
		}
		if (times.length > 0) {
			ionchambers.setTimes(times);
			// log("Setting detector frame times, using array of length " + times.length + "...");
		}
		return;
	}

	@Override
	public void completeCollection() {
		// nothing here
	}

	protected void control_all_ionc(List<IonChamberParameters> ion_chambers_bean) throws Exception {
		for (int index = 0; index < ion_chambers_bean.size(); index++) {
			control_ionc(ion_chambers_bean, index);
		}
	}

	protected void control_ionc(List<IonChamberParameters> ion_chambers_bean, int ion_chamber_num) throws Exception {
		IonChamberParameters ion_chamber = ion_chambers_bean.get(ion_chamber_num);
		setup_amp_sensitivity(ion_chamber, ion_chamber_num);
		boolean autoGas = ion_chamber.getAutoFillGas();
		if (autoGas) {
			double gas_fill1_pressure = ion_chamber.getPressure() * 1000.0;
			double gas_fill1_period = ion_chamber.getGas_fill1_period_box();
			double gas_fill2_pressure = ion_chamber.getTotalPressure() * 1000.0;
			double gas_fill2_period = ion_chamber.getGas_fill2_period_box();
			String flushString = ion_chamber.getFlush().toString();
			String purge_pressure = "25.0";
			String purge_period = "120.0";
			String gas_select_val = "0";
			ionc_gas_injector_scannables.get(ion_chamber_num).moveTo(
					new Object[] { purge_pressure, purge_period, gas_fill1_pressure, gas_fill1_period,
							gas_fill2_pressure, gas_fill2_period, gas_select_val, flushString });
		}
	}

	protected void setup_amp_sensitivity(IonChamberParameters ionChamberParams, int index) throws Exception {
		if (ionChamberParams.getChangeSensitivity()) {
			if (ionChamberParams.getGain() == null || ionChamberParams.getGain() == "") {
				return;
			}
			String[] gainStringParts = ionChamberParams.getGain().split(" ");
			String[] ampStringParts = ionChamberParams.getOffset().split(" ");
			try {
				InterfaceProvider.getTerminalPrinter().print(
						"Changing sensitivity of " + ionChamberParams.getName() + " to " + ionChamberParams.getGain());

				sensitivities[index].moveTo(gainStringParts[0]);
				sensitivity_units[index].moveTo(gainStringParts[1]);
				offsets[index].moveTo(ampStringParts[0]);
				offset_units[index].moveTo(ampStringParts[1]);
			} catch (Exception e) {
				InterfaceProvider.getTerminalPrinter().print(
						"Exception while trying to change the sensitivity of ion chamber" + ionChamberParams.getName());
				InterfaceProvider
						.getTerminalPrinter()
						.print("Set the ion chamber sensitivity manually, uncheck the box in the Detector Parameters editor and restart the scan");
				InterfaceProvider.getTerminalPrinter().print("Please report this problem to Data Acquisition");
				throw e;
			}
		}
	}

	protected void control_mythen(IExperimentDetectorParameters fluoresenceParameters, IOutputParameters outputBean,
			String experimentFullPath) throws Exception {

		String experimentFolderName = experimentFullPath.substring(experimentFullPath.indexOf("xml") + 4,
				experimentFullPath.length());
		String nexusSubFolder = experimentFolderName + "/" + outputBean.getNexusDirectory();
		String asciiSubFolder = experimentFolderName + "/" + outputBean.getAsciiDirectory();

		InterfaceProvider.getTerminalPrinter().print("Moving DCM for Mythen image...");
		energy_scannable.moveTo(fluoresenceParameters.getMythenEnergy());

		mythen_scannable.setCollectionTime(fluoresenceParameters.getMythenTime());
		mythen_scannable.setSubDirectory(experimentFolderName);

		StaticScan staticscan = new StaticScan(new Scannable[] { mythen_scannable });

		// use the Factory to enable unit testing - which would use a DummyDataWriter
		DataWriterFactory datawriterFactory = new DefaultDataWriterFactory();
		DataWriter datawriter = datawriterFactory.createDataWriter();
		if (datawriter instanceof XasAsciiNexusDataWriter) {
			((XasAsciiNexusDataWriter) datawriter).setRunFromExperimentDefinition(false);
			((XasAsciiNexusDataWriter) datawriter).setNexusFileNameTemplate(nexusSubFolder + "/%d-mythen.nxs");
			((XasAsciiNexusDataWriter) datawriter).setAsciiFileNameTemplate(asciiSubFolder + "/%d-mythen.dat");
			staticscan.setDataWriter(datawriter);
		}

		LocalProperties.setScanSetsScanNumber(true);
		staticscan.setScanNumber(1); // need to do this here to prevent the scan trying to use a numtracker to derive
										// the scan number
		InterfaceProvider.getTerminalPrinter().print("Collecting a diffraction image...");
		staticscan.run();
		InterfaceProvider.getTerminalPrinter().print("Diffraction scan complete.");
	}

	@Override
	public BufferedDetector[] getQEXAFSDetectors() throws Exception {
		String expt_type = detectorBean.getExperimentType();
		if (expt_type.equals("Transmission")) {

			if (gmsd_enabled) {
				return createBufferedDetArray(new String[] { "qexafs_counterTimer01_gmsd" });
			} else if (additional_channels_enabled) {
				return createBufferedDetArray(new String[] { "qexafs_counterTimer01", "qexafs_counterTimer01_gmsd" });
			} else {
				return createBufferedDetArray(new String[] { "qexafs_counterTimer01" });
			}
		}

		if (detectorBean.getFluorescenceParameters().getDetectorType().equals("Silicon")) {
			return createBufferedDetArray(new String[] { "qexafs_counterTimer01", "qexafs_xmap", "VortexQexafsFFI0" });
		} else if (detectorBean.getFluorescenceParameters().getDetectorType().equals("Xspress3")) {
			return createBufferedDetArray(new String[] { "qexafs_counterTimer01", "qexafs_xspress3",
					"qexafs_FFI0_xspress3" });
		} else {
			return createBufferedDetArray(new String[] { "qexafs_counterTimer01", "qexafs_xspress", "QexafsFFI0" });
		}

	}

	protected BufferedDetector[] createBufferedDetArray(String[] names) throws Exception {
		BufferedDetector[] dets = new BufferedDetector[] {};
		for (String name : names) {
			Object detector = InterfaceProvider.getJythonNamespace().getFromJythonNamespace(name);
			if (detector == null) {
				throw new Exception("detector named " + name + " not found!");
			}
			dets = (BufferedDetector[]) ArrayUtils.add(dets, detector);
		}
		return dets;
	}

	public boolean isGmsd_enabled() {
		return gmsd_enabled;
	}

	public void setGmsd_enabled(boolean gmsd_enabled) {
		this.gmsd_enabled = gmsd_enabled;
	}

	public boolean isAdditional_channels_enabled() {
		return additional_channels_enabled;
	}

	public void setAdditional_channels_enabled(boolean additional_channels_enabled) {
		this.additional_channels_enabled = additional_channels_enabled;
	}

}