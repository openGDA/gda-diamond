/*-
 * Copyright © 2024 Diamond Light Source Ltd.
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

import java.io.FileNotFoundException;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.Detector;
import gda.jython.InterfaceProvider;
import gda.util.JsonHelper;
import gda.util.XrayLibHelper;
import uk.ac.gda.beans.exafs.DetectorConfig;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.IonchamberOptimisationParams;
import uk.ac.gda.beans.exafs.QEXAFSParameters;
import uk.ac.gda.server.exafs.scan.DetectorPreparer;

public class AdjustmentPreparer implements DetectorPreparer {
	private static final Logger logger = LoggerFactory.getLogger(AdjustmentPreparer.class);

	private IScanParameters scanBean;
	private IDetectorParameters detectorBean;

	private String experimentFullPath;
	private String dummyDetectorName = "";

	private int repetitionNumber;
	private boolean runOnFirstRepetitionOnly;

	String jythonFunctionName = "adjust_sensitivities_2E";

	private double relativeLowEnergy= 50;

	@Override
	public void configure(IScanParameters scanBean, IDetectorParameters detectorBean, IOutputParameters outputBean,
			String experimentFullPath) throws Exception {
		this.experimentFullPath = experimentFullPath;
		this.scanBean = scanBean;
		this.detectorBean = detectorBean;
		repetitionNumber = 0;
	}

	@Override
	public void beforeEachRepetition() throws Exception {
		repetitionNumber++;

		if (runOnFirstRepetitionOnly && repetitionNumber > 1) {
			return;
		}

		if (detectorBean instanceof IDetectorParameters detParams) {

			DetectorConfig detConfig = detParams.getDetectorConfigurations()
					.stream().filter(conf -> conf.getDetectorName().equals(dummyDetectorName))
					.findFirst().orElse(null);

			if (detConfig != null && detConfig.isUseDetectorInScan()) {
				Path filePath = Paths.get(experimentFullPath, detConfig.getConfigFileName());

				if (!filePath.toFile().exists()) {
					throw new FileNotFoundException("Cannot run ionchmaber optimisation - file "+filePath.toString()+" cannot be read");
				}
				IonchamberOptimisationParams params = JsonHelper.readJson(filePath.toString(), IonchamberOptimisationParams.class);
				InterfaceProvider.getCommandRunner().runsource(createAdjustmentCommand(params));
			}
		}
	}

	private String createAdjustmentCommand(IonchamberOptimisationParams ionParams) {

		StringBuilder jythonCmd = new StringBuilder();
		jythonCmd.append(jythonFunctionName+"(");

		if (ionParams.isAutoControl()) {
			if (scanBean instanceof QEXAFSParameters qexafsParams) {
				double edgeEnergy = XrayLibHelper.getEdgeEnergy(qexafsParams.getElement(),  qexafsParams.getEdge());
				double lowEnergy = edgeEnergy - relativeLowEnergy;
				double highEnergy = qexafsParams.getFinalEnergy();

				jythonCmd.append(lowEnergy);
				jythonCmd.append(", ");
				jythonCmd.append(highEnergy);
			} else {
				throw new IllegalArgumentException("Cannot run ionchamber adjustment using element and edge unless using QExafs scan parameters");
			}
		} else {
			jythonCmd.append(ionParams.getEnergies()[0]);
			jythonCmd.append(", ");
			jythonCmd.append(ionParams.getEnergies()[1]);
		}

		jythonCmd.append(")");
		logger.info("Generate ionchamber adjustment command : {}", jythonCmd);
		return jythonCmd.toString();
	}

	@Override
	public void completeCollection() {
	}

	@Override
	public Detector[] getExtraDetectors() {
		return null;
	}

	public String getDummyDetectorName() {
		return dummyDetectorName;
	}

	public void setDummyDetectorName(String dummyDetectorName) {
		this.dummyDetectorName = dummyDetectorName;
	}

	public boolean isRunOnFirstRepetitionOnly() {
		return runOnFirstRepetitionOnly;
	}

	public void setRunOnFirstRepetitionOnly(boolean runOnFirstRepetitionOnly) {
		this.runOnFirstRepetitionOnly = runOnFirstRepetitionOnly;
	}

	public String getJythonFunctionName() {
		return jythonFunctionName;
	}

	public void setJythonFunctionName(String jythonFunctionName) {
		this.jythonFunctionName = jythonFunctionName;
	}

	public double getRelativeLowEnergy() {
		return relativeLowEnergy;
	}

	public void setRelativeLowEnergy(double relativeLowEnergy) {
		this.relativeLowEnergy = relativeLowEnergy;
	}


}
