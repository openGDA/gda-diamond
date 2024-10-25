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

package uk.ac.gda.server.exafs.scan;

import java.util.ArrayList;
import java.util.List;

import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.FluorescenceParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;
import uk.ac.gda.beans.exafs.Region;
import uk.ac.gda.beans.exafs.TransmissionParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;

public class I20PreparersTestUtils {

	protected static XanesScanParameters createXanesBean() {
		XanesScanParameters scanBean = new XanesScanParameters();
		scanBean.setElement("Cu");
		scanBean.setEdge("K");
		scanBean.setFinalEnergy(7010.0);

		List<Region> regions = new ArrayList<Region>();
		Region region1 = new Region();
		region1.setEnergy(7000.0);
		region1.setStep(2.0);
		region1.setTime(2.5);
		regions.add(region1);

		scanBean.setRegions(regions);
		return scanBean;
	}

	protected static IonChamberParameters makeIonChamberParameters(String name) {
		IonChamberParameters ionParams = new IonChamberParameters();
		ionParams.setChangeSensitivity(true);
		ionParams.setAutoFillGas(true);
		ionParams.setName(name);
		ionParams.setDeviceName("counterTimer01");
		ionParams.setGain("1 nA/V");
		ionParams.setOffset("1 pA");
		ionParams.setGasType("Ar");
		ionParams.setPercentAbsorption(15.0);
		ionParams.setTotalPressure(1.1);
		ionParams.setPressure(99.63);
		ionParams.setGas_fill1_period_box(200.0);
		ionParams.setGas_fill2_period_box(200.0);

		return ionParams;
	}

	protected static FluorescenceParameters createSiFluoParameters() {
		FluorescenceParameters fluoParams = new FluorescenceParameters();
		fluoParams.setCollectDiffractionImages(false);
		fluoParams.addIonChamberParameter(I20PreparersTestUtils.makeIonChamberParameters("I0"));
		fluoParams.addIonChamberParameter(I20PreparersTestUtils.makeIonChamberParameters("It"));
		fluoParams.addIonChamberParameter(I20PreparersTestUtils.makeIonChamberParameters("Iref"));
		fluoParams.setCollectDiffractionImages(false);
		fluoParams.setConfigFileName("Fluo_config.xml");
		fluoParams.setDetectorType(FluorescenceParameters.SILICON_DET_TYPE);
		return fluoParams;
	}


	protected static FluorescenceParameters createGeFluoParameters() {
		FluorescenceParameters fluoParams = createSiFluoParameters();
		fluoParams.setDetectorType(FluorescenceParameters.GERMANIUM_DET_TYPE);
		return fluoParams;
	}

	protected static TransmissionParameters createTransmissionParameters() {
		TransmissionParameters transParams = new TransmissionParameters();
		transParams.setCollectDiffractionImages(false);
		transParams.setDetectorType(DetectorParameters.TRANSMISSION_TYPE);
		transParams.addIonChamberParameter(I20PreparersTestUtils.makeIonChamberParameters("I0"));
		transParams.addIonChamberParameter(I20PreparersTestUtils.makeIonChamberParameters("It"));
		transParams.addIonChamberParameter(I20PreparersTestUtils.makeIonChamberParameters("Iref"));
		return transParams;
	}

	protected static DetectorParameters createDetectorParameters(FluorescenceParameters params) {
		DetectorParameters detBean = new DetectorParameters();
		detBean.setFluorescenceParameters(params);
		detBean.setExperimentType(DetectorParameters.FLUORESCENCE_TYPE);
		return detBean;
	}

	protected static DetectorParameters createDetectorParameters(TransmissionParameters params) {
		DetectorParameters detBean = new DetectorParameters();
		detBean.setTransmissionParameters(params);
		detBean.setExperimentType(DetectorParameters.TRANSMISSION_TYPE);
		return detBean;
	}

}
