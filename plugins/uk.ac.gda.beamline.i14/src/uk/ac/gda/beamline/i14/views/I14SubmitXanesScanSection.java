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
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.jython.ICommandRunner;
import gda.jython.InterfaceProvider;
import uk.ac.diamond.daq.mapping.ui.experiment.AbstractMappingSection;

public class I14SubmitXanesScanSection extends AbstractMappingSection {

	private static final Logger logger = LoggerFactory.getLogger(I14SubmitXanesScanSection.class);

	@Override
	public void createControls(Composite parent) {
		final Composite composite = new Composite(parent, SWT.NONE);
		GridDataFactory.swtDefaults().align(SWT.FILL, SWT.BOTTOM).applyTo(composite);
		GridLayoutFactory.swtDefaults().applyTo(composite);

		// Button to submit a scan to the queue
		final Button submitScanButton = new Button(composite, SWT.PUSH);
		GridDataFactory.swtDefaults().applyTo(submitScanButton);
		submitScanButton.setText("Queue Scan");
		submitScanButton.addSelectionListener(SelectionListener.widgetSelectedAdapter(e -> submitScan()));
	}

	@Override
	public boolean createSeparator() {
		return false;
	}

	private void submitScan() {
		final I14XanesMappingView mappingView = (I14XanesMappingView) getMappingView();
		final I14XanesEdgeParametersSection paramsSection = (I14XanesEdgeParametersSection) mappingView.getSection(I14XanesEdgeParametersSection.class);
		final XanesScanParameters scanParameters = new XanesScanParameters(paramsSection.getScanParameters());
		final IMarshallerService marshaller = getService(IMarshallerService.class);
		final ICommandRunner commandRunner = InterfaceProvider.getCommandRunner();

		try {
			final String parameterString = marshaller.marshal(scanParameters).replaceAll("'", "\\\\'");
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
		@SuppressWarnings("unused")
		public final double preEdgeStart;
		@SuppressWarnings("unused")
		public final double preEdgeStop;
		@SuppressWarnings("unused")
		public final double preEdgeStep;
		@SuppressWarnings("unused")
		public final String linesToTrack;
		@SuppressWarnings("unused")
		public final String trackingMethod;

		// Standard mscan command
		@SuppressWarnings("unused")
		public final String mscanCommand;

		XanesScanParameters(I14XanesEdgeParameters xanesParams) {
			preEdgeStart = xanesParams.getPreEdgeStart();
			preEdgeStop = xanesParams.getPreEdgeStop();
			preEdgeStep = xanesParams.getPreEdgeStep();
			linesToTrack = xanesParams.getLinesToTrack();
			trackingMethod = xanesParams.getTrackingMethod();

			mscanCommand = createScanCommand();
		}
	}
}
