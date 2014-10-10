package uk.ac.gda.server.exafs.scan.preparers;

import gda.device.Scannable;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.xmap.Xmap;
import gda.device.detector.xspress.Xspress2Detector;
import gda.device.scannable.BeamMonitor;
import gda.device.scannable.DetectorFillingMonitorScannable;
import gda.device.scannable.TopupChecker;
import gda.exafs.scan.ExafsScanPointCreator;
import gda.exafs.scan.XanesScanPointCreator;
import gda.jython.InterfaceProvider;
import gda.jython.commands.ScannableCommands;

import java.util.List;

import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.QEXAFSParameters;
import uk.ac.gda.beans.exafs.Region;
import uk.ac.gda.beans.exafs.TransmissionParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.server.exafs.scan.DetectorPreparer;

public class I18DetectorPreparer implements DetectorPreparer {

	private final Scannable[] sensitivities;
	private final Scannable[] sensitivity_units;
	private final Scannable[] offsets;
	private final Scannable[] offset_units;
	private final TfgScalerWithFrames counterTimer01;
	private final Xspress2Detector xspress2system;
	private final Xmap xmpaMca;

	private IScanParameters scanBean;
	private IDetectorParameters detectorBean;
	private TopupChecker topupMonitor;
	private BeamMonitor beam;
	private DetectorFillingMonitorScannable detectorFillingMonitor;

	public I18DetectorPreparer(Scannable[] sensitivities, Scannable[] sensitivity_units,
			Scannable[] offsets, Scannable[] offset_units,
			TfgScalerWithFrames ionchambers, Xspress2Detector xspressSystem, Xmap vortexConfig) {
		this.sensitivities = sensitivities;
		this.sensitivity_units = sensitivity_units;
		this.offsets = offsets;
		this.offset_units = offset_units;
		this.counterTimer01 = ionchambers;
		this.xspress2system = xspressSystem;
		this.xmpaMca = vortexConfig;
	}

	@Override
	public void configure(IScanParameters scanBean, IDetectorParameters detectorBean, IOutputParameters outputBean,
			String experimentFullPath) throws Exception {

		this.scanBean = scanBean;
		this.detectorBean = detectorBean;

		if (detectorBean.getExperimentType().equalsIgnoreCase("Fluorescence")) {
			FluorescenceParameters fluoresenceParameters = detectorBean.getFluorescenceParameters();
			String detType = fluoresenceParameters.getDetectorType();
			String xmlFileName = experimentFullPath + fluoresenceParameters.getConfigFileName();
			if (detType == "Germanium") {
				xspress2system.setConfigFileName(xmlFileName);
				xspress2system.configure();
			} else if (detType == "Silicon") {
				xmpaMca.setConfigFileName(xmlFileName);
				xmpaMca.configure();
			}
			control_all_ionc(fluoresenceParameters.getIonChamberParameters());
		} else if (detectorBean.getExperimentType().equalsIgnoreCase("Transmission")) {
			TransmissionParameters transmissionParameters = detectorBean.getTransmissionParameters();
			control_all_ionc(transmissionParameters.getIonChamberParameters());
		}
	}

	@Override
	public void beforeEachRepetition() throws Exception {
		configureMonitors();
		Double[] times = new Double[] {};
		if (scanBean instanceof XasScanParameters) {
			times = ExafsScanPointCreator.getScanTimeArray((XasScanParameters) scanBean);
		} else if (scanBean instanceof XanesScanParameters) {
			times = XanesScanPointCreator.getScanTimeArray((XanesScanParameters) scanBean);
		}
		if (times.length > 0) {
			counterTimer01.setTimes(times);
		}
		return;
	}

	@Override
	public void completeCollection() {
		// nothing here
	}

	public void addMonitors(TopupChecker topupMonitor, BeamMonitor beam,
			DetectorFillingMonitorScannable detectorFillingMonitor) {
		this.topupMonitor = topupMonitor;
		this.beam = beam;
		this.detectorFillingMonitor = detectorFillingMonitor;
	}

	private void configureMonitors() {
		double collectionTime = 0.0;
		if (scanBean instanceof XanesScanParameters) {
			List<Region> regions = ((XanesScanParameters) scanBean).getRegions();
			for (Region region : regions) {
				if (collectionTime < region.getTime()) {
					collectionTime = region.getTime();
				}
			}
		} else if (scanBean instanceof QEXAFSParameters) {
			// pass
		} else {
			// # EXAFS
			collectionTime = ((XasScanParameters) scanBean).getExafsTime();
			if (((XasScanParameters) scanBean).getExafsToTime() > collectionTime) {
				collectionTime = ((XasScanParameters) scanBean).getExafsToTime();
			}
		}
		// print "setting collection time to " + str(collectionTime)

		if (topupMonitor != null) {
			topupMonitor.setPauseBeforePoint(true);
			topupMonitor.setPauseBeforeLine(false);
			topupMonitor.setCollectionTime(collectionTime);
		}

		if (beam != null) {
			beam.setPauseBeforePoint(true);
			beam.setPauseBeforeLine(true);
		}

		if (detectorFillingMonitor != null && detectorBean.getExperimentType().equals("Fluorescence")
				&& detectorBean.getFluorescenceParameters().getDetectorType().equals("Germanium")) {
			detectorFillingMonitor.setPauseBeforePoint(true);
			detectorFillingMonitor.setPauseBeforeLine(false);
			// print "Adding the detectorFillingMonitor to the list of defaults";
			ScannableCommands.add_default(new Object[] { detectorFillingMonitor });
		} else {
			ScannableCommands.remove_default(new Object[] { detectorFillingMonitor });
		}
	}

	protected void control_all_ionc(List<IonChamberParameters> ion_chambers_bean) throws Exception {
		for (int index = 0; index < ion_chambers_bean.size(); index++) {
			control_ionc(ion_chambers_bean, index);
		}
	}

	protected void control_ionc(List<IonChamberParameters> ion_chambers_bean, int ion_chamber_num) throws Exception {
		IonChamberParameters ion_chamber = ion_chambers_bean.get(ion_chamber_num);
		setup_amp_sensitivity(ion_chamber, ion_chamber_num);
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

}