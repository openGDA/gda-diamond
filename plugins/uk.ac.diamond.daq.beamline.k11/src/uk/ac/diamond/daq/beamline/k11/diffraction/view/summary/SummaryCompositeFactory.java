/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.summary;

import static uk.ac.gda.ui.tool.ClientSWTElements.createClientCompositeWithGridLayout;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGridDataFactory;

import java.util.Optional;

import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.springframework.context.ApplicationListener;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeInterface;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.summary.editor.AcquisitionSummary;
import uk.ac.diamond.daq.client.gui.camera.CameraHelper;
import uk.ac.diamond.daq.client.gui.camera.event.CameraControlSpringEvent;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent;
import uk.ac.diamond.daq.mapping.api.document.helper.reader.AcquisitionReader;
import uk.ac.gda.client.properties.camera.CameraConfigurationProperties;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.ClientResourceManager;
import uk.ac.gda.ui.tool.document.ScanningAcquisitionTemporaryHelper;

/**
 * Components representing the GUI acquisition configuration summary.
 *
 * @author Maurizio Nagni
 */
public class SummaryCompositeFactory implements DiffractionCompositeInterface {

	private StyledText summaryText;
	private Composite container;
	private AcquisitionSummary summaryBase;
	private AcquisitionReader reader;


	public SummaryCompositeFactory() {
		super();
		getScanningAcquisitionTemporaryHelper()
			.getAcquisitionController()
				.ifPresent(c -> reader = new AcquisitionReader(c::getAcquisition));
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		container = createClientCompositeWithGridLayout(parent, style, 1);
		createClientGridDataFactory().align(SWT.FILL, SWT.FILL).grab(true, true).applyTo(container);
		createControl(container);

		// Releases resources before dispose
		container.addDisposeListener(event -> dispose()	);
		return container;
	}

	private void dispose() {
		SpringApplicationContextFacade.removeApplicationListener(listenToScanningAcquisitionChanges);
		SpringApplicationContextFacade.removeApplicationListener(cameraControlSpringEventListener);
	}

	/**
	 * Retrieves the {@link StyledText} control used to display the summary infomation
	 *
	 * @param parent
	 *            The containing {@link Composite for the control}
	 */
	private void createControl(Composite parent) {
		summaryText = new StyledText(parent, SWT.NONE);
		summaryText.setWordWrap(true);
		summaryText.setFont(ClientResourceManager.getInstance().getTextDefaultItalicFont());
		summaryText.getCaret().setVisible(true);
		summaryText.getCaret().setSize(5, 20);
		summaryText.setEditable(false);
		this.summaryBase = new AcquisitionSummary(summaryText);
		createClientGridDataFactory().align(SWT.FILL, SWT.FILL).grab(true, true).applyTo(summaryText);
		SpringApplicationContextFacade.addDisposableApplicationListener(this, listenToScanningAcquisitionChanges);
		SpringApplicationContextFacade.addDisposableApplicationListener(this, cameraControlSpringEventListener);
	}

	/**
	 * This listener updates the summary when acquisition configuration changes.
	 * At the moment is not possible to use anonymous lambda expression because it generates a class cast exception
	 */
	private ApplicationListener<ScanningAcquisitionChangeEvent> listenToScanningAcquisitionChanges = new ApplicationListener<ScanningAcquisitionChangeEvent>() {
		@Override
		public void onApplicationEvent(ScanningAcquisitionChangeEvent event) {
			Display.getDefault().asyncExec(() -> updateSummary());
		}
	};


	/**
	 * This listener updates the summary when the camera control, publishing the event, and the detector control associated in this acquisition match.
	 * At the moment is not possible to use anonymous lambda expression because it generates a class cast exception
	 */
	private ApplicationListener<CameraControlSpringEvent> cameraControlSpringEventListener = new ApplicationListener<CameraControlSpringEvent>() {
		@Override
		public void onApplicationEvent(CameraControlSpringEvent event) {
			Display.getDefault().asyncExec(() -> prepareSummaryUpdate(event));
		}

		private void prepareSummaryUpdate(CameraControlSpringEvent event) {
			Optional.ofNullable(reader.getAcquisitionConfiguration().getAcquisitionParameters().getDetectors().iterator().next().getName())
			.map(CameraHelper::getCameraConfigurationPropertiesByCameraControlName)
			.filter(Optional::isPresent)
			.map(Optional::get)
			.map(CameraConfigurationProperties::getId)
			.filter(c -> c.equals(event.getCameraId()))
			.ifPresent(c -> updateSummary());
		}
	};

	private void updateSummary() {
		if (!summaryText.isDisposed()) {
			summaryBase.updateSummary();
			container.getShell().layout(true, true);
		}
	}

	private ScanningAcquisitionTemporaryHelper getScanningAcquisitionTemporaryHelper() {
		return SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class);
	}
}