/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.beamselectorscan;

import static uk.ac.gda.ui.tool.ClientSWTElements.getImage;
import static uk.ac.gda.ui.tool.ClientVerifyListener.verifyOnlyDoubleText;
import static uk.ac.gda.ui.tool.ClientVerifyListener.verifyOnlyPositiveIntegerText;

import java.beans.PropertyChangeListener;
import java.text.DecimalFormat;
import java.util.Optional;
import java.util.function.Consumer;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.beans.typed.BeanProperties;
import org.eclipse.core.databinding.observable.value.SelectObservableValue;
import org.eclipse.jface.databinding.swt.typed.WidgetProperties;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.factory.Finder;
import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.region.PointMappingRegion;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController.RegionPathState;
import uk.ac.gda.api.acquisition.AcquisitionEngineDocument;
import uk.ac.gda.api.acquisition.parameters.DevicePositionDocument;
import uk.ac.gda.api.acquisition.parameters.DevicePositionDocument.ValueType;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.Reloadable;
import uk.ac.gda.ui.tool.document.ScanningAcquisitionTemporaryHelper;
import uk.ac.gda.ui.tool.images.ClientImages;


class BeamSelectorScanControls implements CompositeFactory, Reloadable {

	private static final Logger logger = LoggerFactory.getLogger(BeamSelectorScanControls.class);

	private RegionAndPathController mappingController;

	private final BeamSelectorScanUIConfiguration config;

	private static final DecimalFormat BEAM_POSITION_FORMAT = new DecimalFormat("#0.00");

	private Text xPosition;
	private Text yPosition;

	private DataBindingContext bindingContext = new DataBindingContext();
	
	/** caching simply to remove listener when it is replaced */
	private PointMappingRegion point;
	
	/** triggered when the existing point moves */
	private PropertyChangeListener regionMoveListener = change -> handleRegionMove();
	
	/** triggered when the existing point is replaced */
	private Consumer<RegionPathState> regionUpdateListener = this::handleRegionUpdate;

	private GridDataFactory stretch = GridDataFactory.swtDefaults().align(SWT.FILL, SWT.CENTER).grab(true, false);

	public BeamSelectorScanControls() {
		config = Finder.findLocalSingleton(BeamSelectorScanUIConfiguration.class);
	}

	@Override
	public Composite createComposite(Composite parent, int style) {

		var composite = createBaseComposite(parent);

		createNameControl(composite);
		createCyclesControl(composite);
		separator(composite);
		createImagingBeamControl(composite);
		separator(composite);
		createDiffractionBeamControl(composite);

		composite.addDisposeListener(event -> dispose());

		return composite;
	}

	private void dispose() {
		mappingController.detachViewUpdater(regionUpdateListener);
		if (point != null) {
			point.removePropertyChangeListener(regionMoveListener);
		}
	}

	private Composite createBaseComposite(Composite parent) {
		var composite = new Composite(parent, SWT.NONE);
		GridLayoutFactory.swtDefaults().numColumns(2).equalWidth(true).applyTo(composite);
		stretch.applyTo(composite);
		return composite;
	}

	private void createNameControl(Composite composite) {
		new Label(composite, SWT.NONE).setText("Acquisition name");
		Text name = new Text(composite, SWT.BORDER);
		stretch.applyTo(name);

		var acquisition = getScanningAcquisitionTemporaryHelper().getScanningAcquisition().orElseThrow();
		bindingContext.bindValue(WidgetProperties.text(SWT.Modify).observe(name),
				BeanProperties.value("name").observe(acquisition));
	}

	private void createCyclesControl(Composite composite) {
		new Label(composite, SWT.NONE).setText("Number of cycles");
		Text cycles = new Text(composite, SWT.BORDER);
		stretch.applyTo(cycles);

		cycles.addVerifyListener(verifyOnlyPositiveIntegerText);
		cycles.setText(String.valueOf(getScanningAcquisitionTemporaryHelper().getScannableTrackDocuments().iterator().next().getPoints()));
		cycles.addModifyListener(event -> setNumberOfCycles(Integer.parseInt(cycles.getText())));
	}

	private void createImagingBeamControl(Composite composite) {
		new Label(composite, SWT.NONE).setText("Imaging beam");
		var mono = new Button(composite, SWT.RADIO);
		mono.setText("Monochromatic");

		space(composite);

		var pink = new Button(composite, SWT.RADIO);
		pink.setText("Polychromatic");

		SelectObservableValue<String> detectorName = new SelectObservableValue<>();
		detectorName.addOption(config.getMonoImagingScan(), WidgetProperties.buttonSelection().observe(mono));
		detectorName.addOption(config.getPinkImagingScan(), WidgetProperties.buttonSelection().observe(pink));

		AcquisitionEngineDocument engine = getScanningAcquisitionTemporaryHelper().getAcquisitionControllerElseThrow()
			.getAcquisition().getAcquisitionEngine();

		bindingContext.bindValue(detectorName, BeanProperties.value("id").observe(engine));
	}

	private void createDiffractionBeamControl(Composite composite) {
		new Label(composite, SWT.NONE).setText("Diffraction beam");

		space(composite);

		var left = new Composite(composite, SWT.NONE);
		GridLayoutFactory.swtDefaults().numColumns(2).equalWidth(true).applyTo(left);
		stretch.copy().span(1, 2).applyTo(left);

		var selectFromMap = new Button(left, SWT.PUSH);
		selectFromMap.setImage(getImage(ClientImages.POINT));
		selectFromMap.setToolTipText("Pick coordinates from map");
		GridDataFactory.swtDefaults().span(1,  2).applyTo(selectFromMap);

		rightAlignedLabel(left, "X");
		rightAlignedLabel(left, "Y");

		xPosition = new Text(composite, SWT.BORDER);
		xPosition.addVerifyListener(verifyOnlyDoubleText);
		stretch.applyTo(xPosition);

		yPosition = new Text(composite, SWT.BORDER);
		xPosition.addVerifyListener(verifyOnlyDoubleText);
		stretch.applyTo(yPosition);

		String xAxis = config.getxAxisName();
		String yAxis = config.getyAxisName();

		try {
			Scannable xScannable = Finder.find(xAxis);
			Scannable yScannable = Finder.find(yAxis);
			xPosition.setText(String.valueOf(BEAM_POSITION_FORMAT.format((double) xScannable.getPosition())));
			yPosition.setText(String.valueOf(BEAM_POSITION_FORMAT.format((double) yScannable.getPosition())));
		} catch (DeviceException e) {
			logger.error("Couldn't read beam positions");
		}

		initialiseMappingController();
		selectFromMap.addListener(SWT.Selection, event -> mappingController.getRegionSelectorListener().handleRegionChange(new PointMappingRegion()));

		xPosition.addListener(SWT.Modify, event -> setStartPosition(xAxis, "x", Double.parseDouble(xPosition.getText())));
		yPosition.addListener(SWT.Modify, event -> setStartPosition(yAxis, "y", Double.parseDouble(yPosition.getText())));
	}

	private void initialiseMappingController() {
		mappingController = PlatformUI.getWorkbench().getService(RegionAndPathController.class);
		mappingController.initialise(Optional.of(regionUpdateListener), Optional.empty());
	}

	private void handleRegionUpdate(RegionPathState state) {
		var shape = state.scanRegionShape();
		if (shape instanceof PointMappingRegion) {
			newPoint((PointMappingRegion) shape);
		}
	}

	private void newPoint(PointMappingRegion point) {
		if (this.point != null) {
			this.point.removePropertyChangeListener(regionMoveListener);
		}
		point.addPropertyChangeListener(regionMoveListener);
		this.point = point;
	}

	private void handleRegionMove() {
		xPosition.setText(String.valueOf(BEAM_POSITION_FORMAT.format(point.getxPosition())));
		yPosition.setText(String.valueOf(BEAM_POSITION_FORMAT.format(point.getyPosition())));
	}

	private void setNumberOfCycles(int points) {
		getScanningAcquisitionTemporaryHelper().createScannableTrackDocumentHelper()
		.ifPresent(helper -> helper.updateScannableTrackDocumentsPoints(points));
	}

	private void setStartPosition(String device, String axis, double position) {
		ScanningParameters parameters = getScanningAcquisitionTemporaryHelper().getAcquisitionControllerElseThrow()
											.getAcquisition().getAcquisitionConfiguration().getAcquisitionParameters();

		var start = parameters.getStartPosition();
		start.removeIf(positionDocument -> positionDocument.getDevice().equals(device));

		DevicePositionDocument document = new DevicePositionDocument.Builder()
												.withDevice(device)
												.withAxis(axis)
												.withValueType(ValueType.NUMERIC)
												.withPosition(position)
												.build();

		start.add(document);

		parameters.setStartPosition(start);
	}

	private void rightAlignedLabel(Composite composite, String text) {
		var label = new Label(composite, SWT.NONE);
		label.setText(text);
		GridDataFactory.fillDefaults().align(SWT.RIGHT, SWT.CENTER).grab(true, false).applyTo(label);
	}

	private void separator(Composite composite) {
		GridDataFactory.fillDefaults().span(numberOfColumns(composite), 1).applyTo(
				new Label(composite, SWT.NONE));
	}

	private int numberOfColumns(Composite composite) {
		return ((GridLayout) composite.getLayout()).numColumns;
	}

	private void space(Composite composite) {
		GridDataFactory.swtDefaults().applyTo(new Label(composite, SWT.NONE));
	}

	@SuppressWarnings("unused")
	private void emptyCell(Composite composite) {
		new Label(composite, SWT.NONE);
	}

	@Override
	public void reload() {
		// Coming soon...
	}

	private ScanningAcquisitionTemporaryHelper getScanningAcquisitionTemporaryHelper() {
		return SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class);
	}
}
