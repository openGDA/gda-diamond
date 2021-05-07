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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.density;

import static uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeHelper.stringToInteger;
import static uk.ac.gda.ui.tool.ClientMessages.POINTS_DENSITY;
import static uk.ac.gda.ui.tool.ClientMessages.POINTS_PER_SIDE;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientCompositeWithGridLayout;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGridDataFactory;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientLabel;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientText;
import static uk.ac.gda.ui.tool.ClientVerifyListener.verifyOnlyPositiveIntegerText;
import static uk.ac.gda.ui.tool.images.ClientImages.EXCLAMATION_RED;

import java.util.Arrays;
import java.util.EnumMap;
import java.util.Map;
import java.util.Optional;
import java.util.function.Supplier;
import java.util.stream.IntStream;

import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.databinding.validation.ValidationStatus;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jface.databinding.swt.typed.WidgetProperties;
import org.eclipse.jface.fieldassist.ControlDecoration;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.springframework.context.ApplicationListener;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeInterface;
import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent;
import uk.ac.diamond.daq.mapping.api.document.helper.ScannableTrackDocumentHelper;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.ClientSWTElements;

/**
 * Component representing the GUI density elements
 *
 * @author Maurizio Nagni
 */
public class DensityCompositeFactory implements DiffractionCompositeInterface {

	/**
	 * Maps, for each AcquisitionTemplateType, the relevant density properties for the associated IScanPointGeneratorModel class
	 */
	private static final Map<AcquisitionTemplateType, String[]> acquisitionTemplateTypeProperties = new EnumMap<>(AcquisitionTemplateType.class);

	static {
		acquisitionTemplateTypeProperties.put(AcquisitionTemplateType.TWO_DIMENSION_POINT, new String[] {});
		acquisitionTemplateTypeProperties.put(AcquisitionTemplateType.TWO_DIMENSION_LINE, new String[] { "points" });
		acquisitionTemplateTypeProperties.put(AcquisitionTemplateType.TWO_DIMENSION_GRID, new String[] { "xAxisPoints", "yAxisPoints" });
	}

	private Text points;

	private ControlDecoration readoutTextDecoration;

	private IObservableValue<String> readoutObservableValue;

	private static final int MIN_POINT_DENSITY = 1;
	private static final int MAX_POINT_DENSITY = 50;
	private Color invalidEntryColor;

	private final ScannableTrackDocumentHelper scannableTrackDocumentHelper;
	private final Supplier<ScanningAcquisition> acquisitionSupplier;

	private final DataBindingContext regionDBC = new DataBindingContext();
	private Binding densityBinding;

	private RegionAndPathController rapController;

	public DensityCompositeFactory(Supplier<ScanningAcquisition> acquisitionSupplier, RegionAndPathController rapController) {
		super();
		this.acquisitionSupplier = acquisitionSupplier;
		this.rapController = rapController;
		this.scannableTrackDocumentHelper = new ScannableTrackDocumentHelper(this::getScanningParameters);
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		Composite container = createClientCompositeWithGridLayout(parent, style, 1);
		createClientGridDataFactory().align(SWT.FILL, SWT.TOP).applyTo(container);

		Label label = createClientLabel(container, style, POINTS_DENSITY);
		createClientGridDataFactory().align(SWT.CENTER, SWT.TOP).applyTo(label);

		points = createClientText(container, SWT.BORDER, POINTS_PER_SIDE, verifyOnlyPositiveIntegerText);
		createClientGridDataFactory().align(SWT.FILL, SWT.TOP).hint(ClientSWTElements.DEFAULT_TEXT_SIZE).applyTo(points);

		readoutTextDecoration = new ControlDecoration(points, SWT.LEFT | SWT.TOP);
		readoutTextDecoration.setImage(ClientSWTElements.getImage(EXCLAMATION_RED));
		readoutTextDecoration.setDescriptionText("Please enter an integer value between 1 and 50 inclusive");

		points.addModifyListener(modifyPointListener);
		SpringApplicationContextFacade.addDisposableApplicationListener(this, listenToScanningAcquisitionChanges);

		// Releases resources before dispose
		container.addDisposeListener(event -> dispose()	);
		return container;
	}

	@Override
	public void initialiseElements() {
		points.setEnabled(true);

		// Required to avoid an infinite loop on update
		points.removeModifyListener(modifyPointListener);

		updatePoints(0);

		// Re-enable the text listener
		points.addModifyListener(modifyPointListener);

		if (AcquisitionTemplateType.TWO_DIMENSION_POINT.equals(getSelectedAcquisitionTemplateType()))
			points.setEnabled(false);
	}

	private void dispose() {
		if (points != null) {
			points.removeModifyListener(modifyPointListener);
		}
		SpringApplicationContextFacade.removeApplicationListener(listenToScanningAcquisitionChanges);
	}


	private final ModifyListener modifyPointListener = event -> updateScannableTrackDocumentsPoints();

	/**
	 * Despite this is a two way binding, is useful only to report the new number of points to the rapController.
	 */
	@Override
	public void updateScanPointBindings() {
		Optional.ofNullable(densityBinding).ifPresent(regionDBC::removeBinding);
		String[] properties = acquisitionTemplateTypeProperties.get(getSelectedAcquisitionTemplateType());
		IntStream.range(0, properties.length)
			.forEach(index -> {
				IObservableValue<Integer> pointsObservableValue = BeanProperties.value(properties[index])
						.observe(rapController.getScanPathModel());
				// The scan path is driven by the gui, NOT the other way (because the ScanningAcquisition drives all)
				densityBinding = regionDBC.bindValue(getReadoutObservableValue(), pointsObservableValue,
					validatedReadoutToPointsStrategy(), new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER));
			});
	}

	private void updateScannableTrackDocumentsPoints() {
		int numPoints = Integer.parseInt(points.getText());
		initialiseElements();

		// Skip the update if number of points is the same
		if (getScannableTrackDocument(0) == null || numPoints == getScannableTrackDocument(0).getPoints())
			return;

		int size = getScanningParameters().getScanpathDocument().getScannableTrackDocuments().size();
		int[] trackDocumentsPoints = new int[size];
		Arrays.fill(trackDocumentsPoints, numPoints);
		scannableTrackDocumentHelper.updateScannableTrackDocumentsPoints(trackDocumentsPoints);
		SpringApplicationContextFacade.publishEvent(
				new ScanningAcquisitionChangeEvent(this, getScanningAcquisition()));
	}

	private UpdateValueStrategy<String, Integer> validatedReadoutToPointsStrategy() {
		return UpdateValueStrategy.create(stringToInteger).setAfterGetValidator(this::densityReadoutValidator);
	}

	/**
	 * Validator for use with the point density {@link Text} control; it will accept numeric textual values between the
	 * specified min and max values
	 *
	 * @param stringContent
	 *            The {@link String} to be checked
	 * @return Success if the value is numeric and between the required min and max otherwise error
	 */
	private IStatus densityReadoutValidator(Object stringContent) {
		int density = 0;
		try {
			density = Integer.parseInt((String) stringContent);
			return densityRangeValidator(density);
		} catch (NumberFormatException e) {
			return ValidationStatus.error("");
		}
	}

	private IStatus densityRangeValidator(Integer value) {
		IStatus result = ValidationStatus.error("");
		Control readoutText = readoutTextDecoration.getControl();

		if (value != null && value.intValue() >= MIN_POINT_DENSITY && value.intValue() <= MAX_POINT_DENSITY) {
			readoutText.setBackground(readoutText.getDisplay().getSystemColor(SWT.COLOR_WHITE));
			readoutTextDecoration.hide();
			result = ValidationStatus.ok();
		} else {
			readoutText.setBackground(invalidEntryColor);
			readoutTextDecoration.show();
			readoutTextDecoration.showHoverText(readoutTextDecoration.getDescriptionText());
		}
		return result;
	}

	private IObservableValue<String> getReadoutObservableValue() {
		if (readoutObservableValue == null) {
			readoutObservableValue = WidgetProperties.text(SWT.Modify).observe(points);
		}
		return readoutObservableValue;
	}

	// At the moment is not possible to use anonymous lambda expression because it
	// generates a class cast exception
	private ApplicationListener<ScanningAcquisitionChangeEvent> listenToScanningAcquisitionChanges = new ApplicationListener<ScanningAcquisitionChangeEvent>() {
		@Override
		public void onApplicationEvent(ScanningAcquisitionChangeEvent event) {
				updatePoints(0);
		}
	};

	private void updatePoints(int index) {
		Optional.ofNullable(getScannableTrackDocument(index))
			.map(ScannableTrackDocument::getPoints)
			.map(p -> Integer.toString(p))
			.ifPresent(points::setText);
		// sets the cursor at the end
		points.setSelection(points.getCharCount());
	}

	// ------------ UTILS ----
	private ScannableTrackDocument getScannableTrackDocument(int index) {
		return Optional.ofNullable(getScanningParameters())
			.map(ScanningParameters::getScanpathDocument)
			.map(ScanpathDocument::getScannableTrackDocuments)
			.filter(l -> !l.isEmpty())
			.map(l -> l.get(index))
			.orElseGet(() -> null);
	}

	private ScanningAcquisition getScanningAcquisition() {
		return this.acquisitionSupplier.get();
	}

	private ScanningParameters getScanningParameters() {
		return getScanningAcquisition().getAcquisitionConfiguration().getAcquisitionParameters();
	}

	private AcquisitionTemplateType getSelectedAcquisitionTemplateType() {
		return getScanningParameters().getScanpathDocument().getModelDocument();
	}
}