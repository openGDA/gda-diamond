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

import static uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeHelper.POLICY_NEVER;
import static uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeHelper.POLICY_UPDATE;
import static uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeHelper.integerToString;
import static uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeHelper.stringToInteger;
import static uk.ac.gda.ui.tool.ClientMessages.POINTS_DENSITY;
import static uk.ac.gda.ui.tool.ClientMessages.POINTS_PER_SIDE;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientCompositeWithGridLayout;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGridDataFactory;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientLabel;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientText;
import static uk.ac.gda.ui.tool.ClientVerifyListener.verifyOnlyIntegerText;
import static uk.ac.gda.ui.tool.images.ClientImages.EXCLAMATION_RED;

import java.util.Arrays;
import java.util.Optional;
import java.util.function.Supplier;
import java.util.stream.IntStream;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.conversion.IConverter;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.databinding.observable.value.SelectObservableValue;
import org.eclipse.core.databinding.validation.ValidationStatus;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.fieldassist.ControlDecoration;
import org.eclipse.scanning.api.points.models.IScanPointGeneratorModel;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.events.KeyListener;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Scale;
import org.eclipse.swt.widgets.Text;

import com.google.common.primitives.Ints;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeInterface;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionEvent;
import uk.ac.diamond.daq.mapping.api.document.helper.ScannableTrackDocumentHelper;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanning.ShapeType;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.spring.SpringApplicationContextProxy;

/**
 * Component representing the GUI density elements
 *
 * @author Maurizio Nagni
 */
public class DensityCompositeFactory implements DiffractionCompositeInterface {

	private Scale densityScale;
	private Text points;

	private ControlDecoration readoutTextDecoration;

	private IObservableValue<Integer> scaleObservableValue;
	private IObservableValue<String> readoutObservableValue;

	private static final int HALF_RANGE = 25;
	private static final int MIN_POINT_DENSITY = 1;
	private static final int MAX_POINT_DENSITY = 50;
	private Color invalidEntryColor;

	private final ScannableTrackDocumentHelper scannableTrackDocumentHelper;
	private final Supplier<ScanningAcquisition> acquisitionSupplier;
	private final SelectObservableValue<ShapeType> selectedShapeType;

	private final DataBindingContext viewDBC;
	private final DataBindingContext regionDBC;

	public DensityCompositeFactory(DataBindingContext viewDBC, DataBindingContext regionDBC,
			Supplier<ScanningAcquisition> acquisitionSupplier, SelectObservableValue<ShapeType> selectedShapeType) {
		super();
		this.acquisitionSupplier = acquisitionSupplier;
		this.scannableTrackDocumentHelper = new ScannableTrackDocumentHelper(this::getScanningParameters);
		this.selectedShapeType = selectedShapeType;
		this.viewDBC = viewDBC;
		this.regionDBC = regionDBC;
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		Composite container = createClientCompositeWithGridLayout(parent, style, 2);
		createClientGridDataFactory().align(SWT.BEGINNING, SWT.BEGINNING).indent(5, SWT.DEFAULT).applyTo(container);

		Label label = createClientLabel(container, style, POINTS_DENSITY);
		createClientGridDataFactory().align(SWT.BEGINNING, SWT.END).span(2, 1).indent(5, SWT.DEFAULT).applyTo(label);

		densityScale = new Scale(container, SWT.VERTICAL);
		densityScale.setMinimum(1);
		densityScale.setMaximum(HALF_RANGE + HALF_RANGE);
		densityScale.setSelection(HALF_RANGE);
		densityScale.setIncrement(1);
		densityScale.setPageIncrement(HALF_RANGE);
		densityScale.setToolTipText("Set number of points per side of the region");

		points = createClientText(container, SWT.BORDER, POINTS_PER_SIDE, Optional.ofNullable(verifyOnlyIntegerText));
		createClientGridDataFactory().align(SWT.BEGINNING, SWT.CENTER).applyTo(points);
		points.setText(String.valueOf(densityScale.getSelection()));

		readoutTextDecoration = new ControlDecoration(points, SWT.LEFT | SWT.TOP);
		readoutTextDecoration.setImage(ClientSWTElements.getImage(EXCLAMATION_RED));
		readoutTextDecoration.setDescriptionText("Please enter an integer value between 1 and 50 inclusive");
		return parent;
	}

	@Override
	public void bindControls() {
		scaleObservableValue = WidgetProperties.selection().observe(densityScale);
		readoutObservableValue = WidgetProperties.text(SWT.Modify).observe(points);
		bindPointDensityWidgetBehaviour();
		updateScannableTrackDocumentsPoints();
		points.addModifyListener(event -> updateScannableTrackDocumentsPoints());
	}

	@Override
	public void updateScanPointBindings(final IScanPointGeneratorModel newPathValue, ShapeType shapeType) {
		updateScanPathPropertyBindings(newPathValue, shapeType);

	}

	private void updateScannableTrackDocumentsPoints() {
		Integer intPoints = Optional.ofNullable(points.getText()).filter(s -> !s.isEmpty()).map(Integer::parseInt)
				.orElse(0);
		int[] trackDocumentsPoints = null;
		switch (getScanpathDocument().getModelDocument()) {
		case ONE_DIMENSION_LINE:
			trackDocumentsPoints = new int[1];
			break;
		case TWO_DIMENSION_POINT:
		case TWO_DIMENSION_LINE:
		case TWO_DIMENSION_GRID:
			trackDocumentsPoints = new int[2];
			break;
		default:
			break;
		}
		Optional.ofNullable(trackDocumentsPoints).ifPresent(p -> {
			Arrays.fill(p, intPoints);
			scannableTrackDocumentHelper.updateScannableTrackDocumentsPoints(intPoints);
			SpringApplicationContextProxy.publishEvent(new ScanningAcquisitionEvent(acquisitionSupplier.get()));
		});
	}

	private ScanpathDocument getScanpathDocument() {
		return acquisitionSupplier.get().getAcquisitionConfiguration().getAcquisitionParameters().getScanpathDocument();
	}

	/**
	 * Creates the static bindings that control whether the point density controls are enabled based on the selected
	 * {@link ShapeType}. Listeners are also added to make mouse wheeel and pgUp/pgDn event move the scale to the min,
	 * max or centre point values.
	 *
	 * @param densityScale
	 *            The number of points scale control
	 * @param readoutText
	 *            The number of points text box
	 */
	private void bindPointDensityWidgetBehaviour() {
		viewDBC.bindValue(selectedShapeType, WidgetProperties.enabled().observe(densityScale),
				UpdateValueStrategy.create(hideControlForPoint), POLICY_NEVER);
		viewDBC.bindValue(selectedShapeType, WidgetProperties.enabled().observe(points),
				UpdateValueStrategy.create(hideControlForPoint), POLICY_NEVER);

		densityScale.addKeyListener(new KeyListener() {
			@Override
			public void keyReleased(KeyEvent e) {
				// no action
			}

			@Override
			public void keyPressed(KeyEvent e) {
				if (e.keyCode == SWT.PAGE_UP || e.keyCode == SWT.PAGE_DOWN) {
					adjustPageIncrement(e.keyCode == SWT.PAGE_UP);
				}
			}
		});
		densityScale.addMouseWheelListener(e -> adjustPageIncrement(e.count > 0));
	}

	private void adjustPageIncrement(final boolean up) {
		int adjustment = HALF_RANGE;
		if ((up && densityScale.getSelection() > HALF_RANGE) || (!up && densityScale.getSelection() < HALF_RANGE)) {
			adjustment = Math.abs(densityScale.getSelection() - HALF_RANGE);
		}
		densityScale.setPageIncrement(adjustment);
	}

	private void updateScanPathPropertyBindings(final IScanPointGeneratorModel newPathValue, ShapeType shapeType) {
		if (ShapeType.LINE.equals(shapeType)) {
			IObservableValue<Integer> pointsObservableValue = BeanProperties.value("points").observe(newPathValue);
			regionDBC.bindValue(getReadoutObservableValue(), pointsObservableValue, validatedReadoutToPointsStrategy(),
					validatedPointsToReadoutStrategy());
			regionDBC.bindValue(getScaleObservableValue(), pointsObservableValue, POLICY_UPDATE,
					validatedPointsToScaleStrategy());
		} else {
			IntStream.range(0, shapeType.getProperties().length).forEach(index -> {
				IObservableValue<Integer> pointsObservableValue = BeanProperties.value(shapeType.getProperties()[index])
						.observe(newPathValue);
				if (index == 0) {
					regionDBC.bindValue(getReadoutObservableValue(), pointsObservableValue,
							validatedReadoutToPointsStrategy(), validatedPointsToReadoutStrategy());
					regionDBC.bindValue(getScaleObservableValue(), pointsObservableValue, POLICY_UPDATE,
							validatedPointsToScaleStrategy());
				} else {
					regionDBC.bindValue(getReadoutObservableValue(), pointsObservableValue,
							validatedReadoutToPointsStrategy(), POLICY_NEVER);
					regionDBC.bindValue(getScaleObservableValue(), pointsObservableValue, POLICY_UPDATE, POLICY_NEVER);
				}
			});
		}
	}

	private UpdateValueStrategy validatedReadoutToPointsStrategy() {
		return UpdateValueStrategy.create(stringToInteger).setAfterGetValidator(this::densityReadoutValidator);
	}

	private UpdateValueStrategy validatedPointsToReadoutStrategy() {
		return UpdateValueStrategy.create(integerToString).setAfterConvertValidator(this::densityReadoutValidator);
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
		return densityRangeValidator(Ints.tryParse((String) stringContent));
	}

	private UpdateValueStrategy validatedPointsToScaleStrategy() {
		return new UpdateValueStrategy(UpdateValueStrategy.POLICY_UPDATE)
				.setAfterConvertValidator(this::densityRangeValidator);
	}

	private IStatus densityRangeValidator(Object integerContent) {
		IStatus result = ValidationStatus.error("");
		Integer value = (Integer) integerContent;
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

	private final IConverter hideControlForPoint = IConverter.create(ShapeType.class, Boolean.class,
			shape -> !((ShapeType) shape).equals(ShapeType.POINT));

	private IObservableValue<Integer> getScaleObservableValue() {
		return scaleObservableValue;
	}

	private IObservableValue<String> getReadoutObservableValue() {
		return readoutObservableValue;
	}

	private ScanningParameters getScanningParameters() {
		return this.acquisitionSupplier.get().getAcquisitionConfiguration().getAcquisitionParameters();
	}
}