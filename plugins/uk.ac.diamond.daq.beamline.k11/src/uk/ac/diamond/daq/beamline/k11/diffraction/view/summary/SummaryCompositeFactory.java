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

import static uk.ac.gda.ui.tool.ClientMessages.SUMMARY;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientCompositeWithGridLayout;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGridDataFactory;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientLabel;

import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;

import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.springframework.context.ApplicationListener;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeInterface;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.ClientResourceManager;

/**
 * Components representing the GUI summary element per {@link ShapeType}. As not all the elements are available through
 * the update {@link IScanPointGeneratorModel}, some properties are binded/retrieved using
 * {@link RegionAndPathController}. In both cases to simplify the code specific {@link ShapeSummaryBase} property names
 * match the ones in {@link IScanPointGeneratorModel} or {@link RegionAndPathController}.
 *
 * @author Maurizio Nagni
 */
/**
 *
 */
public class SummaryCompositeFactory implements DiffractionCompositeInterface {

	private final Supplier<ScanningAcquisition> acquisitionSupplier;

	private static final int PADDING = 15;
	private StyledText summaryText;
	private Composite container;
	private final AcquisitionTemplateTypeSummaryBase summaryBase;


	public SummaryCompositeFactory(Supplier<ScanningAcquisition> acquisitionSupplier) {
		super();
		this.acquisitionSupplier = acquisitionSupplier;
		this.summaryBase = new AcquisitionTemplateTypeSummaryBase(acquisitionSupplier);
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		container = createClientCompositeWithGridLayout(parent, style, 1);
		createClientGridDataFactory().align(SWT.BEGINNING, SWT.BEGINNING).indent(5, SWT.DEFAULT).applyTo(container);

		Label label = createClientLabel(container, style, SUMMARY);
		createClientGridDataFactory().align(SWT.BEGINNING, SWT.END).span(2, 1).indent(5, SWT.DEFAULT).applyTo(label);

		createControl(container);
		return container;
	}

	/**
	 * Retrieves the {@link StyledText} control used to display the summary infomation
	 *
	 * @param parent
	 *            The containing {@link Composite for the control}
	 */
	private void createControl(Composite parent) {
		summaryText = new StyledText(parent, SWT.BORDER);
		summaryText.setMargins(PADDING, PADDING, PADDING, PADDING);
		summaryText.setWordWrap(true);
		summaryText.setFont(ClientResourceManager.getInstance().getTextDefaultItalicFont());
		summaryText.setCaret(null);
		summaryText.setEditable(false);
		createClientGridDataFactory().applyTo(summaryText);
		SpringApplicationContextFacade.addDisposableApplicationListener(this, listenToScanningAcquisitionChanges);
	}

	// At the moment is not possible to use anonymous lambda expression because it
	// generates a class cast exception
	private ApplicationListener<ScanningAcquisitionChangeEvent> listenToScanningAcquisitionChanges = new ApplicationListener<ScanningAcquisitionChangeEvent>() {
		@Override
		public void onApplicationEvent(ScanningAcquisitionChangeEvent event) {
			UUID eventUUID = Optional.ofNullable(event.getScanningAcquisition())
					.map(ScanningAcquisition.class::cast)
					.map(ScanningAcquisition::getUuid)
					.orElseGet(UUID::randomUUID);

			UUID scanningAcquisitionUUID = Optional.ofNullable(acquisitionSupplier.get())
					.map(ScanningAcquisition::getUuid)
					.orElseGet(UUID::randomUUID);

			if (eventUUID.equals(scanningAcquisitionUUID)) {
				summaryText.setText(summaryBase.toString());
				container.getParent().layout(true, true);
			}
		}
	};
}