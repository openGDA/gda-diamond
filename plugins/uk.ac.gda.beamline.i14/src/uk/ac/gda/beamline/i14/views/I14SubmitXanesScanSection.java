/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i14.views;

import org.eclipse.dawnsci.analysis.api.persistence.IMarshallerService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.jython.ICommandRunner;
import gda.jython.InterfaceProvider;
import uk.ac.diamond.daq.mapping.ui.experiment.SubmitScanSection;

public class I14SubmitXanesScanSection extends SubmitScanSection {

	private static final Logger logger = LoggerFactory.getLogger(I14SubmitXanesScanSection.class);

	@Override
	protected void submitScan() {
		final I14XanesEdgeParametersSection paramsSection = (I14XanesEdgeParametersSection) getMappingView().getSection(I14XanesEdgeParametersSection.class);
		final XanesScanParameters xanesScanParameters = new XanesScanParameters(paramsSection.getScanParameters());
		final IMarshallerService marshaller = getService(IMarshallerService.class);
		final ICommandRunner commandRunner = InterfaceProvider.getCommandRunner();

		try {
			final String parameterString = marshaller.marshal(xanesScanParameters).replaceAll("'", "\\\\'");
			final String command = String.format("run_xanes_scan('%s')", parameterString);
			logger.debug("Executing Jython command: {}", command);
			commandRunner.runCommand(command);
		} catch (Exception e) {
			logger.error("Error submitting XANES scan", e);
		}
	}

	/**
	 * Class to hold all parameters required by the XANES scan
	 * <p>
	 * This will be serialised to JSON and passed to the XANES script.
	 */
	private class XanesScanParameters {
		// XANES-specific parameters
		public final String linesToTrack;
		public final String trackingMethod;
		public final String energySteps;

		// Standard mscan command
		public final String mscanCommand;

		XanesScanParameters(I14XanesEdgeParameters xanesParams) {
			linesToTrack = xanesParams.getLinesToTrack();
			trackingMethod = xanesParams.getTrackingMethod();
			energySteps = xanesParams.getEnergySteps();
			mscanCommand = createScanCommand();
		}

		@Override
		public String toString() {
			return "XanesScanParameters [linesToTrack=" + linesToTrack + ", trackingMethod=" + trackingMethod
					+ ", energySteps=" + energySteps + ", mscanCommand=" + mscanCommand + "]";
		}

	}
}
