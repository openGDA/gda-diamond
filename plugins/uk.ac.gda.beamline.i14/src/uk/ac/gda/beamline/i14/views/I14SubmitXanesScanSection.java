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

import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

import org.eclipse.dawnsci.analysis.api.persistence.IMarshallerService;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.scanning.api.device.models.AbstractDetectorModel;
import org.eclipse.scanning.api.device.models.ClusterProcessingModel;
import org.eclipse.scanning.api.device.models.IDetectorModel;
import org.eclipse.scanning.api.points.models.GridModel;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.jython.ICommandRunner;
import gda.jython.InterfaceProvider;
import uk.ac.diamond.daq.mapping.api.IMappingExperimentBean;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegion;
import uk.ac.diamond.daq.mapping.api.IScanModelWrapper;
import uk.ac.diamond.daq.mapping.region.RectangularMappingRegion;
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
		final XanesScanParameters scanParameters = new XanesScanParameters(getMappingBean(), paramsSection.getScanParameters());
		final IMarshallerService marshaller = getService(IMarshallerService.class);
		final ICommandRunner commandRunner = InterfaceProvider.getCommandRunner();

		try {
			final String parameterString = marshaller.marshal(scanParameters);
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

		public final double xStart;
		public final double xStop;
		@SuppressWarnings("unused")
		public final double xStep;
		public final double yStart;
		public final double yStop;
		@SuppressWarnings("unused")
		public final double yStep;

		@SuppressWarnings("unused")
		public final List<XanesDetectorModel> detectors;

		@SuppressWarnings("unused")
		public final List<String> processingFiles;

		XanesScanParameters(IMappingExperimentBean mappingBean, I14XanesEdgeParameters xanesParams) {
			preEdgeStart = xanesParams.getPreEdgeStart();
			preEdgeStop = xanesParams.getPreEdgeStop();
			preEdgeStep = xanesParams.getPreEdgeStep();
			linesToTrack = xanesParams.getLinesToTrack();
			trackingMethod = xanesParams.getTrackingMethod();

			final IMappingScanRegion region = mappingBean.getScanDefinition().getMappingScanRegion();
			if (!(region.getRegion() instanceof RectangularMappingRegion)) {
				throw new IllegalArgumentException("Scan region must be rectangular");
			}
			final RectangularMappingRegion mappingRegion = (RectangularMappingRegion) region.getRegion();

			if (!(region.getScanPath() instanceof GridModel)) {
				throw new IllegalArgumentException("Scan model must be a grid model");
			}
			final GridModel model = (GridModel) region.getScanPath();

			xStart = mappingRegion.getxStart();
			xStop = mappingRegion.getxStop();
			xStep = (xStop - xStart) / model.getFastAxisPoints();
			yStart = mappingRegion.getyStart();
			yStop = mappingRegion.getyStop();
			yStep = (yStop - yStart) / model.getSlowAxisPoints();

			final List<IScanModelWrapper<IDetectorModel>> detectorParameters = mappingBean.getDetectorParameters();
			if (detectorParameters == null) {
				detectors = Collections.emptyList();
			} else {
				final List<IDetectorModel> detectorModels = detectorParameters.stream()
						.filter(IScanModelWrapper<IDetectorModel>::isIncludeInScan)
						.map(IScanModelWrapper<IDetectorModel>::getModel)
						.collect(Collectors.toList());
				detectors = detectorModels.stream()
						.map(d -> new XanesDetectorModel(d.getName(), d.getExposureTime(), d.getTimeout()))
						.collect(Collectors.toList());
			}

			final List<IScanModelWrapper<ClusterProcessingModel>> clusterProcessingConfiguration = mappingBean.getClusterProcessingConfiguration();
			if (clusterProcessingConfiguration == null) {
				processingFiles = Collections.emptyList();
			} else {
				processingFiles = clusterProcessingConfiguration.stream()
						.filter(IScanModelWrapper<ClusterProcessingModel>::isIncludeInScan)
						.map(IScanModelWrapper<ClusterProcessingModel>::getName)
						.collect(Collectors.toList());
			}
		}

		private class XanesDetectorModel extends AbstractDetectorModel {
			XanesDetectorModel(String name, double exposureTime, long timeout) {
				setName(name);
				setExposureTime(exposureTime);
				setTimeout(timeout);
			}
		}
	}
}
