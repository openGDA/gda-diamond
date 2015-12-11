/*-
 * Copyright © 2015 Diamond Light Source Ltd.
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
package uk.ac.gda.server.exafs.scan.preparers;

import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.countertimer.TfgScalerWithFrames;
import gda.device.detector.xmap.Xmap;
import gda.device.detector.xspress.Xspress2Detector;
import gda.device.scannable.TopupChecker;
import gda.util.Element;

import java.util.ArrayList;
import java.util.List;

import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.Region;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.server.exafs.scan.DetectorPreparer;

public class I20DetectorPreparer implements DetectorPreparer {

	private Xspress2Detector xspress2system;
	private Scannable[] sensitivities;
	private Scannable[] sensitivity_units;
	private Scannable[] offsets;
	private Scannable[] offset_units;
	private TfgScalerWithFrames ionchambers;
	private TfgScalerWithFrames i1;
	private Xmap vortex;
	private TopupChecker topupChecker;
	private IScanParameters scanBean;

	public I20DetectorPreparer(Xspress2Detector xspress2system, Scannable[] sensitivities, Scannable[] sensitivity_units,
			Scannable[] offsets, Scannable[] offset_units, TfgScalerWithFrames ionchambers, TfgScalerWithFrames I1,
			Xmap vortex, TopupChecker topupChecker) {
		this.xspress2system = xspress2system;
		this.sensitivities = sensitivities;
		this.sensitivity_units = sensitivity_units;
		this.offsets = offsets;
		this.offset_units = offset_units;
		this.ionchambers = ionchambers;
		this.i1 = I1;
		this.vortex = vortex;
		this.topupChecker = topupChecker;
		sensitivities = sensitivity_units;
	}

	public List<Detector> getDetectors() {
		ArrayList<Detector> detectors = new ArrayList<Detector>();
		detectors.add(xspress2system);
		detectors.add(ionchambers);
		detectors.add(i1);
		detectors.add(vortex);
		return detectors;
	}

	@Override
	public void configure(IScanParameters scanBean, IDetectorParameters detectorBean, IOutputParameters outputBean,
			String experimentFullPath) throws Exception {

		this.scanBean = scanBean;

		_setUpIonChambers();

		if (detectorBean.getExperimentType().equals(DetectorParameters.FLUORESCENCE_TYPE)) {
			FluorescenceParameters fluoresenceParameters = detectorBean.getFluorescenceParameters();
			String xmlFileName = experimentFullPath + fluoresenceParameters.getConfigFileName();
			String detType = fluoresenceParameters.getDetectorType();
			if (detType.equals(FluorescenceParameters.GERMANIUM_DET_TYPE)) {
				xspress2system.setConfigFileName(xmlFileName);
				xspress2system.configure();
				setXspressCorrectionParameters();
			} else if (detType.equals(FluorescenceParameters.SILICON_DET_TYPE)) {
				vortex.setConfigFileName(xmlFileName);
				vortex.configure();
			}
		} else if (detectorBean.getExperimentType() == DetectorParameters.XES_TYPE) {
			FluorescenceParameters fluoresenceParameters = detectorBean.getXesParameters();
			String detType = fluoresenceParameters.getDetectorType();
			if (detType.equals(FluorescenceParameters.SILICON_DET_TYPE)) {
				String xmlFileName = experimentFullPath + fluoresenceParameters.getConfigFileName();
				vortex.setConfigFileName(xmlFileName);
				vortex.configure();
			}
		}

		List<IonChamberParameters> ionChamberParamsArray = null;
		if (detectorBean.getExperimentType() == (DetectorParameters.FLUORESCENCE_TYPE)) {
			ionChamberParamsArray = detectorBean.getFluorescenceParameters().getIonChamberParameters();
		} else if (detectorBean.getExperimentType() == (DetectorParameters.TRANSMISSION_TYPE)) {
			ionChamberParamsArray = detectorBean.getTransmissionParameters().getIonChamberParameters();
		} else if (detectorBean.getExperimentType() == DetectorParameters.XES_TYPE) {
			ionChamberParamsArray = detectorBean.getXesParameters().getIonChamberParameters();
		}
		if (ionChamberParamsArray != null) {
			for (IonChamberParameters ionChamberParams : ionChamberParamsArray) {
				_setup_amp_sensitivity(ionChamberParams);
			}
		}
	}

	@Override
	public void beforeEachRepetition() throws Exception {
		// nothing needed here (yet)
	}

	@Override
	public Detector[] getExtraDetectors() {
		return null;
	}

	@Override
	public void completeCollection() {
		topupChecker.setCollectionTime(0.0);
		ionchambers.setOutputLogValues(false);
	}

	private void _setup_amp_sensitivity(IonChamberParameters ionChamberParams) throws Exception {
		if (ionChamberParams.getChangeSensitivity()) {
			String ionChamberName = ionChamberParams.getName();
			if (ionChamberParams.getGain() == null || ionChamberParams.getGain().isEmpty()) {
				return;
			}
			String[] gainStringParts = ionChamberParams.getGain().split(" ");
			String[] ampStringParts = ionChamberParams.getOffset().split(" ");
			int index = 0;
			if (ionChamberName.equalsIgnoreCase("It")) {
				index = 1;
			} else if (ionChamberName.equalsIgnoreCase("Iref")) {
				index = 2;
			} else if (ionChamberName.equalsIgnoreCase("I1")) {
				index = 3;
			}
			try {
				// print "Changing sensitivity of",ionChamberName,"to",ionChamberParams.getGain()
				sensitivities[index].moveTo(gainStringParts[0]);
				sensitivity_units[index].moveTo(gainStringParts[1]);
				offsets[index].moveTo(ampStringParts[0]);
				offset_units[index].moveTo(ampStringParts[1]);
			} catch (Exception e) {
				// InterfaceProvider.getTerminalPrinter().print(
				// "Exception while trying to change the sensitivity of ion chamber" + ionChamberParams.getName());
				// InterfaceProvider
				// .getTerminalPrinter()
				// .print("Set the ion chamber sensitivity manually, uncheck the box in the Detector Parameters editor and restart the scan");
				// InterfaceProvider.getTerminalPrinter().print("Please report this problem to Data Acquisition");
				throw e;
			}
		}
	}

	private void _setUpIonChambers() {
		// # determine max collection time
		double maxTime = 0;
		if (scanBean instanceof XanesScanParameters) {
			XanesScanParameters xanesParams = (XanesScanParameters) scanBean;
			for (Region region : xanesParams.getRegions()) {
				if (region.getTime() > maxTime) {
					maxTime = region.getTime();
				}
			}
		}

		else if (scanBean instanceof XasScanParameters) {
			XasScanParameters xasParams = (XasScanParameters) scanBean;
			if (xasParams.getPreEdgeTime() > maxTime) {
				maxTime = xasParams.getPreEdgeTime();
			}
			if (xasParams.getEdgeTime() > maxTime) {
				maxTime = xasParams.getEdgeTime();
			}
			if (xasParams.getExafsTimeType().equals("Constant Time")) {
				if (xasParams.getExafsTime() > maxTime) {
					maxTime = xasParams.getExafsTime();
				}
			} else {
				if (xasParams.getExafsToTime() > maxTime) {
					maxTime = xasParams.getExafsToTime();
				}
				if (xasParams.getExafsFromTime() > maxTime) {
					maxTime = xasParams.getExafsFromTime();
				}
			}
		}

		// # set dark current time and handle any errors here
		if (maxTime > 0) {
			// InterfaceProvider.getTerminalPrinter().print(
			// "Setting ionchambers dark current collectiom time to" + maxTime + "s.");
			ionchambers.setDarkCurrentCollectionTime(maxTime);
			i1.setDarkCurrentCollectionTime(maxTime);

			// double topupPauseTime = maxTime + topupChecker.getTolerance();
			// InterfaceProvider.getTerminalPrinter().print(
			// "Setting the topup checker to pause scans for" + topupPauseTime + "s before topup");
			topupChecker.setCollectionTime(maxTime);
		}

	}

	private void setXspressCorrectionParameters() throws DeviceException {
		double dtEnergy = 0.0;
		// # Use the fluo (emission) energy of the nearest transition based on the element and excitation edge
		// # to calculate the energy dependent deadtime parameters.
		if ((scanBean instanceof XasScanParameters) || (scanBean instanceof XanesScanParameters)) {
			String element;
			String edge;
			if (scanBean instanceof XasScanParameters) {
				element = ((XasScanParameters) scanBean).getElement();
				edge = ((XasScanParameters) scanBean).getEdge();
			} else {
				element = ((XanesScanParameters) scanBean).getElement();
				edge = ((XanesScanParameters) scanBean).getEdge();
			}
			Element elementObj = Element.getElement(element);
			dtEnergy = _getEmissionEnergy(elementObj, edge);
			dtEnergy /= 1000; // # convert from eV to keV;
			xspress2system.setDeadtimeCalculationEnergy(dtEnergy);
		}

	}

	private double _getEmissionEnergy(Element elementObj, String edge) {
		if (edge.equals("K")) {
			return elementObj.getEmissionEnergy("Ka1");
		} else if (edge.equals("L1")) {
			return elementObj.getEmissionEnergy("La1");
		} else if (edge.equals("L2")) {
			return elementObj.getEmissionEnergy("La1");
		} else if (edge.equals("L3")) {
			return elementObj.getEmissionEnergy("La1");
		} else if (edge.equals("M1")) {
			return elementObj.getEmissionEnergy("Ma1");
		} else if (edge.equals("M2")) {
			return elementObj.getEmissionEnergy("Ma1");
		} else if (edge.equals("M3")) {
			return elementObj.getEmissionEnergy("Ma1");
		} else if (edge.equals("M4")) {
			return elementObj.getEmissionEnergy("Ma1");
		} else if (edge.equals("M5")) {
			return elementObj.getEmissionEnergy("Ma1");
		} else {
			return elementObj.getEmissionEnergy("Ka1");
		}
	}
}
