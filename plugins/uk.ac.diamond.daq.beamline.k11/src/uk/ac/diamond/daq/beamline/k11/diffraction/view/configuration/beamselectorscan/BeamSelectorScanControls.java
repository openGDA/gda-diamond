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

import static uk.ac.gda.ui.tool.ClientSWTElements.STRETCH;
import static uk.ac.gda.ui.tool.ClientSWTElements.composite;
import static uk.ac.gda.ui.tool.ClientSWTElements.getImage;
import static uk.ac.gda.ui.tool.ClientSWTElements.innerComposite;
import static uk.ac.gda.ui.tool.ClientVerifyListener.verifyOnlyDoubleText;
import static uk.ac.gda.ui.tool.ClientVerifyListener.verifyOnlyPositiveIntegerText;

import java.beans.PropertyChangeListener;
import java.text.DecimalFormat;
import java.util.List;
import java.util.Optional;
import java.util.function.Consumer;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.scanning.api.points.models.TwoAxisPointSingleModel;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.factory.Finder;
import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.ProcessingRequestsControls;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.SummaryComposite;
import uk.ac.diamond.daq.client.gui.camera.CameraHelper;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent.UpdatedProperty;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.diamond.daq.mapping.region.PointMappingRegion;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController.RegionPathState;
import uk.ac.gda.api.acquisition.parameters.DetectorDocument;
import uk.ac.gda.api.acquisition.parameters.DevicePositionDocument;
import uk.ac.gda.api.camera.CameraControl;
import uk.ac.gda.client.widgets.DetectorExposureWidget;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.Reloadable;
import uk.ac.gda.ui.tool.document.ScanningAcquisitionTemporaryHelper;
import uk.ac.gda.ui.tool.images.ClientImages;


class BeamSelectorScanControls implements CompositeFactory, Reloadable {

	private static final Logger logger = LoggerFactory.getLogger(BeamSelectorScanControls.class);

	private RegionAndPathController mappingController;

	private final BeamSelectorScanUIConfiguration config;

	private static final DecimalFormat BEAM_POSITION_FORMAT = new DecimalFormat("#0.00");

	private Text name;

	private Text cycles;

	private Text xPosition;
	private Text yPosition;

	private DetectorExposureWidget imagingExposureWidget;
	private DetectorExposureWidget diffractionExposureWidget;

	private ProcessingRequestsControls processingControls;

	/** caching simply to remove listener when it is replaced */
	private PointMappingRegion point;

	/** triggered when the existing point moves */
	private PropertyChangeListener regionMoveListener = change -> handleRegionMove();

	/**
	 * Used for synchronisation
	 */
	private boolean handlingRegionMove = false;

	/** triggered when the existing point is replaced */
	private Consumer<RegionPathState> regionUpdateListener = this::handleRegionUpdate;

	public BeamSelectorScanControls() {
		config = Finder.findLocalSingleton(BeamSelectorScanUIConfiguration.class);
	}

	@Override
	public Composite createComposite(Composite parent, int style) {

		var composite = composite(parent, 1);
		var twoColumnComposite = innerComposite(composite, 2, true);

		createNameControl(twoColumnComposite);
		createCyclesControl(twoColumnComposite);
		separator(twoColumnComposite);
		createImagingBeamControl(twoColumnComposite);
		separator(twoColumnComposite);
		createDiffractionBeamControl(twoColumnComposite);

		createSummary(composite);
		createProcessingSection(composite);

		initialiseControls();

		composite.addDisposeListener(event -> dispose());

		return composite;
	}

	private void dispose() {
		mappingController.detachViewUpdater(regionUpdateListener);
		if (point != null) {
			point.removePropertyChangeListener(regionMoveListener);
		}
	}

	private void createNameControl(Composite composite) {
		new Label(composite, SWT.NONE).setText("Acquisition name");
		name = new Text(composite, SWT.BORDER);
		STRETCH.applyTo(name);

		name.addModifyListener(event -> getScanningAcquisitionTemporaryHelper().getScanningAcquisition().orElseThrow().setName(name.getText()));
	}

	private void createCyclesControl(Composite composite) {
		new Label(composite, SWT.NONE).setText("Number of cycles");
		cycles = new Text(composite, SWT.BORDER);
		STRETCH.applyTo(cycles);

		cycles.addVerifyListener(verifyOnlyPositiveIntegerText);
		cycles.addModifyListener(event -> setNumberOfCycles(Integer.parseInt(cycles.getText())));
	}

	private void setNumberOfCycles(int points) {
		getAxis().setPoints(points);
		publishEvent(UpdatedProperty.PATH);
	}

	private ScannableTrackDocument getAxis() {
		return getScanningParameters().getScanpathDocument().getTrajectories().get(0).getAxes().get(0);
	}

	private void publishEvent(UpdatedProperty updatedProperty) {
		SpringApplicationContextFacade.publishEvent(new ScanningAcquisitionChangeEvent(this, updatedProperty));
	}

	private void createImagingBeamControl(Composite parent) {
		var group = createGroup(parent, "Imaging beam");
		new Label(group, SWT.NONE).setText("Detector exposure");
		imagingExposureWidget = new DetectorExposureWidget(group, this::setImagingDetectorExposure, this::readImagingDetectorExposure);
	}

	private void createProcessingSection(Composite parent) {
		processingControls = new ProcessingRequestsControls();
		processingControls.createComposite(parent, SWT.NONE);
	}

	private void createSummary(Composite parent) {
		var summary = new SummaryComposite();
		summary.createComposite(parent, SWT.IGNORE);
	}

	private double getImagingDetectorExposureFromScan() {
		return getDetectorExposureFromScan(config.getImagingDetectorId());
	}

	private double getDiffractionDetectorExposureFromScan() {
		return getDetectorExposureFromScan(config.getDiffractionDetectorId());
	}

	private double getDetectorExposureFromScan(String detectorId) {
		var params = getScanningParameters();
		var detector = params.getDetectors().stream()
				.filter(det -> det.getId().equals(detectorId))
				.findFirst().orElseThrow();
		return detector.getExposure();
	}

	private void setImagingDetectorExposure(double exposure) {
		updateDetectorDocument(config.getImagingDetectorId(), exposure);
	}

	private void setDiffractionDetectorExposure(double exposure) {
		updateDetectorDocument(config.getDiffractionDetectorId(), exposure);
	}

	private void updateDetectorDocument(String detectorId, double exposure) {
		ScanningParameters parameters = getScanningParameters();

		var detectorDocument = parameters.getDetectors().stream()
								.filter(doc -> doc.getId().equals(detectorId))
								.findFirst().orElseThrow();

		if (detectorDocument.getExposure() == exposure) return;

		var updatedDocument = new DetectorDocument.Builder()
								.withMalcolmDetectorName(detectorDocument.getMalcolmDetectorName())
								.withId(detectorDocument.getId())
								.withExposure(exposure)
								.build();
		parameters.setDetector(updatedDocument);
		publishEvent(UpdatedProperty.DETECTOR_EXPOSURE);
	}

	private double readImagingDetectorExposure() {
		return readDetectorExposure(config.getImagingDetectorId());

	}

	private double readDiffractionDetectorExposure() {
		return readDetectorExposure(config.getDiffractionDetectorId());
	}

	/**
	 * Read exposure from hardware
	 */
	private double readDetectorExposure(String detectorName) {
		try {
			return getCameraControl(detectorName).getAcquireTime();
		} catch (DeviceException e) {
			logger.error("Could not read {} exposure", detectorName, e);
			return 0.0;
		}
	}

	private CameraControl getCameraControl(String detector) {
		return CameraHelper.getCameraControlByCameraID(detector).orElseThrow();
	}

	private Composite createGroup(Composite parent, String groupName) {
		var group = new Group(parent, SWT.BORDER);
		group.setText(groupName);

		GridLayoutFactory.swtDefaults().extendedMargins(5, 5, 5, 5).numColumns(2).equalWidth(true).applyTo(group);
		STRETCH.copy().span(2,1).applyTo(group);

		return group;
	}

	private void createDiffractionBeamControl(Composite parent) {

		var group = createGroup(parent, "Diffraction beam");

		var left = new Composite(group, SWT.NONE);
		GridLayoutFactory.swtDefaults().numColumns(2).equalWidth(true).applyTo(left);
		STRETCH.copy().span(1, 2).applyTo(left);

		var selectFromMap = new Button(left, SWT.PUSH);
		var icon = getImage(ClientImages.POINT);
		selectFromMap.setImage(icon);
		selectFromMap.setToolTipText("Pick coordinates from map");
		selectFromMap.addDisposeListener(dispose -> icon.dispose());
		GridDataFactory.swtDefaults().span(1,  2).applyTo(selectFromMap);

		rightAlignedLabel(left, "X");
		rightAlignedLabel(left, "Y");

		xPosition = new Text(group, SWT.BORDER);
		xPosition.addVerifyListener(verifyOnlyDoubleText);
		STRETCH.applyTo(xPosition);

		yPosition = new Text(group, SWT.BORDER);
		xPosition.addVerifyListener(verifyOnlyDoubleText);
		STRETCH.applyTo(yPosition);

		initialiseMappingController();
		selectFromMap.addListener(SWT.Selection, event -> {
			mappingController.getRegionSelectorListener().handleRegionChange(new PointMappingRegion());
			mappingController.changePath(new TwoAxisPointSingleModel());
		});

		xPosition.addListener(SWT.Modify, event -> setStartPosition(config.getxAxisName(), "x", Double.parseDouble(xPosition.getText())));
		yPosition.addListener(SWT.Modify, event -> setStartPosition(config.getyAxisName(), "y", Double.parseDouble(yPosition.getText())));

		var label = new Label(group, SWT.NONE);
		label.setText("Detector exposure");

		diffractionExposureWidget = new DetectorExposureWidget(group, this::setDiffractionDetectorExposure, this::readDiffractionDetectorExposure);
	}

	private void initialiseMappingController() {
		mappingController = PlatformUI.getWorkbench().getService(RegionAndPathController.class);
		mappingController.initialise(Optional.of(regionUpdateListener), Optional.empty());
	}

	private void updateMappingController() {
		if (handlingRegionMove) {
			// controller already up to date
			return;
		}
		var x = Double.parseDouble(xPosition.getText());
		var y = Double.parseDouble(yPosition.getText());

		IMappingScanRegionShape shape = new PointMappingRegion();
		shape.centre(x, y);
		mappingController.getRegionSelectorListener().handleRegionChange(shape);

		var path = new TwoAxisPointSingleModel();
		path.setX(x);
		path.setY(y);
		mappingController.changePath(path);

		mappingController.updatePlotRegion();
	}

	private void handleRegionUpdate(RegionPathState state) {
		var shape = state.scanRegionShape();
		if (shape instanceof PointMappingRegion pointRegion) {
			newPoint(pointRegion);
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
		try {
			handlingRegionMove = true;
			xPosition.setText(String.valueOf(BEAM_POSITION_FORMAT.format(point.getxPosition())));
			yPosition.setText(String.valueOf(BEAM_POSITION_FORMAT.format(point.getyPosition())));
		} finally {
			handlingRegionMove = false;
		}
	}

	private void setStartPosition(String device, String axis, double position) {
		ScanningParameters parameters = getScanningAcquisitionTemporaryHelper().getAcquisitionControllerElseThrow()
											.getAcquisition().getAcquisitionConfiguration().getAcquisitionParameters();

		var start = parameters.getStartPosition();
		start.removeIf(positionDocument -> positionDocument.getDevice().equals(device));

		DevicePositionDocument document = new DevicePositionDocument.Builder()
												.withDevice(device)
												.withAxis(axis)
												.withPosition(position)
												.build();

		start.add(document);

		parameters.setStartPosition(start);

		updateMappingController();
	}

	private void rightAlignedLabel(Composite composite, String text) {
		var label = new Label(composite, SWT.NONE);
		label.setText(text);
		GridDataFactory.fillDefaults().align(SWT.RIGHT, SWT.CENTER).grab(true, false).applyTo(label);
	}

	private void separator(Composite composite) {
		var format = GridDataFactory.fillDefaults().span(numberOfColumns(composite), 1);
		format.applyTo(new Label(composite, SWT.NONE));
	}

	private int numberOfColumns(Composite composite) {
		return ((GridLayout) composite.getLayout()).numColumns;
	}

	/**
	 * Set their initial state according to the underlying acquisition
	 */
	private void initialiseControls() {
		initialiseName();
		initialiseCycles();
		initialiseImagingBeam();
		initialiseDiffractionBeam();
		processingControls.reload();
	}

	private void initialiseName() {
		name.setText(getScanningAcquisitionTemporaryHelper().getScanningAcquisition().orElseThrow().getName());
	}

	private void initialiseCycles() {
		cycles.setText(String.valueOf(getAxis().getPoints()));
	}

	private void initialiseImagingBeam() {
		imagingExposureWidget.updateFromModel(getImagingDetectorExposureFromScan());
	}

	public void resolveScanId() {
		Scannable imagingHintScannable = Finder.find(config.getImagingHintScannableName());
		try {
			var configuredImagingBranch = imagingHintScannable.getPosition().toString();
			var malcolmScanId = config.getImagingBeamToMalcolmScanId().get(configuredImagingBranch);
			getScanningAcquisitionTemporaryHelper().getAcquisitionControllerElseThrow()
				.getAcquisition().getAcquisitionEngine().setId(malcolmScanId);
		} catch (DeviceException e) {
			logger.error("Error resolving Malcolm scan ID for beam selector scan", e);
		}
	}

	private void initialiseDiffractionBeam() {

		String xAxis = config.getxAxisName();
		String yAxis = config.getyAxisName();

		List<DevicePositionDocument> beamPosition = beamPositionInAcquisition();
		if (beamPosition.size() == 2) {
			double x = (double) beamPosition.stream().filter(doc -> doc.getDevice().equals(xAxis)).findFirst().orElseThrow().getPosition();
			double y = (double) beamPosition.stream().filter(doc -> doc.getDevice().equals(yAxis)).findFirst().orElseThrow().getPosition();
			handlingRegionMove = true;
			xPosition.setText(String.valueOf(x));
			yPosition.setText(String.valueOf(y));
			handlingRegionMove = false;

		} else {

			try {
				Scannable xScannable = Finder.find(xAxis);
				Scannable yScannable = Finder.find(yAxis);
				handlingRegionMove = true;
				xPosition.setText(String.valueOf(BEAM_POSITION_FORMAT.format((double) xScannable.getPosition())));
				yPosition.setText(String.valueOf(BEAM_POSITION_FORMAT.format((double) yScannable.getPosition())));
				handlingRegionMove = false;
			} catch (DeviceException e) {
				logger.error("Couldn't read beam positions");
			}
		}

		diffractionExposureWidget.updateFromModel(getDiffractionDetectorExposureFromScan());
	}

	private List<DevicePositionDocument> beamPositionInAcquisition() {
		ScanningParameters parameters = getScanningParameters();

		return parameters.getStartPosition().stream()
				.filter(doc -> doc.getDevice().equals(config.getxAxisName()) || doc.getDevice().equals(config.getyAxisName()))
				.toList();
	}

	@Override
	public void reload() {
		initialiseControls();
	}

	private ScanningParameters getScanningParameters() {
		return getScanningAcquisitionTemporaryHelper().getAcquisitionControllerElseThrow()
				.getAcquisition().getAcquisitionConfiguration().getAcquisitionParameters();
	}

	private ScanningAcquisitionTemporaryHelper getScanningAcquisitionTemporaryHelper() {
		return SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class);
	}
}
