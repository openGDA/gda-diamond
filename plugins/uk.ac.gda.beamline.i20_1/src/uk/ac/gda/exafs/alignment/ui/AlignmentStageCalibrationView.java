/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.alignment.ui;

import java.beans.PropertyChangeListener;
import java.util.ArrayList;

import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.forms.widgets.TableWrapData;
import org.eclipse.ui.forms.widgets.TableWrapLayout;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.AlignmentStage;
import gda.device.scannable.AlignmentStageScannable;
import gda.device.scannable.AlignmentStageScannable.AlignmentStageDevice;
import gda.rcp.views.NudgePositionerComposite;
import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.livecontrol.ScannablePositionerControl;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.EdeDataStore;
import uk.ac.gda.exafs.data.ScannableSetup;
import uk.ac.gda.exafs.ui.data.AlignmentStageModel;
import uk.ac.gda.exafs.ui.data.ScannableMotorMoveObserver;
import uk.ac.gda.ui.components.NumberEditorControl;

public class AlignmentStageCalibrationView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.alignmentstagecalibration";

	private static final Logger logger = LoggerFactory.getLogger(AlignmentStageCalibrationView.class);

	private FormToolkit toolkit;
	private Form form;

	private AlignmentStage alignmentStage;

	private final String ALIGNMENT_STAGE_DATA_STORE_KEY = "ALIGNMENT_STAGE_DATA_STORE_KEY";

	private final WritableList<Scannable> movingScannables = new WritableList<>(new ArrayList<>(), Scannable.class);
	private final ScannableMotorMoveObserver moveObserver = new ScannableMotorMoveObserver(movingScannables);

	public AlignmentStageCalibrationView() {}

	@Override
	public void createPartControl(Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		ScrolledForm scrolledform = toolkit.createScrolledForm(parent);
		form = scrolledform.getForm();
		form.getBody().setLayout(new TableWrapLayout());
		try {
			createControlsSection();
			loadAlignmentStageSettings();
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
			logger.error("Unable to create controls", e);
		}
	}

	// Make Listener object for given AlignmentStageDevice
	private Listener makeListenerForDevice( final AlignmentStageDevice alignmentStageDevice )
	{
		return event -> {
			try {
				alignmentStageDevice.moveLocation(ScannableSetup.ALIGNMENT_STAGE_X_POSITION.getScannable(),
						ScannableSetup.ALIGNMENT_STAGE_Y_POSITION.getScannable(),
						ScannableSetup.FAST_SHUTTER_X_POSITION.getScannable(),
						ScannableSetup.FAST_SHUTTER_Y_POSITION.getScannable());
			}
			catch (DeviceException e1) {
				logger.error("Problem moving alignment stage ", e1);
			} catch (Exception e2) {
				logger.error("Problem getting scannable for alignment stage ", e2);
			}
		};
	}

	protected String getDataStoreKey() {
		return ALIGNMENT_STAGE_DATA_STORE_KEY;
	}

	// Return model object with current device positions.
	private AlignmentStageModel getModelFromDevicePositions() {
		AlignmentStageModel model = new AlignmentStageModel(); // this model is apparently not used anywhere else - convenient structure for preference store.

		model.setxXeye( AlignmentStageScannable.AlignmentStageDevice.eye.getLocation().getxPosition() );
		model.setyXeye( AlignmentStageScannable.AlignmentStageDevice.eye.getLocation().getyPosition() );

		model.setxSlits( AlignmentStageScannable.AlignmentStageDevice.slits.getLocation().getxPosition() );
		model.setySlits( AlignmentStageScannable.AlignmentStageDevice.slits.getLocation().getyPosition() );

		model.setxFoils( AlignmentStageScannable.AlignmentStageDevice.foil.getLocation().getxPosition() );
		model.setyFoils( AlignmentStageScannable.AlignmentStageDevice.foil.getLocation().getyPosition() );

		model.setxHole( AlignmentStageScannable.AlignmentStageDevice.hole.getLocation().getxPosition() );
		model.setyHole( AlignmentStageScannable.AlignmentStageDevice.hole.getLocation().getyPosition() );

		model.setxShutter( AlignmentStageScannable.AlignmentStageDevice.shutter.getLocation().getxPosition() );
		model.setyShutter( AlignmentStageScannable.AlignmentStageDevice.shutter.getLocation().getyPosition() );

		model.setxHole2( AlignmentStageScannable.AlignmentStageDevice.hole2.getLocation().getxPosition() );
		model.setyHole2( AlignmentStageScannable.AlignmentStageDevice.hole2.getLocation().getyPosition() );

		model.setxLaser( AlignmentStageScannable.AlignmentStageDevice.laser.getLocation().getxPosition() );
		model.setyLaser( AlignmentStageScannable.AlignmentStageDevice.laser.getLocation().getyPosition() );

		return model;
	}

	// Set device positions from model (NB. no motors are actually moved).
	private void setDevicePositionsFromModel( AlignmentStageModel model ) {
		if ( model == null ) {
			return;
		}

		AlignmentStageScannable.AlignmentStageDevice.eye.getLocation().setxPosition( model.getxXeye() );
		AlignmentStageScannable.AlignmentStageDevice.eye.getLocation().setyPosition( model.getyXeye() );

		AlignmentStageScannable.AlignmentStageDevice.slits.getLocation().setxPosition( model.getxSlits() );
		AlignmentStageScannable.AlignmentStageDevice.slits.getLocation().setyPosition( model.getySlits() );

		AlignmentStageScannable.AlignmentStageDevice.foil.getLocation().setxPosition( model.getxFoils() );
		AlignmentStageScannable.AlignmentStageDevice.foil.getLocation().setyPosition( model.getyFoils() );

		AlignmentStageScannable.AlignmentStageDevice.hole.getLocation().setxPosition( model.getxHole() );
		AlignmentStageScannable.AlignmentStageDevice.hole.getLocation().setyPosition( model.getyHole() );

		AlignmentStageScannable.AlignmentStageDevice.shutter.getLocation().setxPosition( model.getxShutter() );
		AlignmentStageScannable.AlignmentStageDevice.shutter.getLocation().setyPosition( model.getyShutter() );

		AlignmentStageScannable.AlignmentStageDevice.hole2.getLocation().setxPosition( model.getxHole2() );
		AlignmentStageScannable.AlignmentStageDevice.hole2.getLocation().setyPosition( model.getyHole2() );

		AlignmentStageScannable.AlignmentStageDevice.laser.getLocation().setxPosition( model.getxLaser() );
		AlignmentStageScannable.AlignmentStageDevice.laser.getLocation().setyPosition( model.getyLaser() );
	}

	// Save alignment settings to persistence store.
	private void saveAlignmentStageSettings() {
		AlignmentStageModel model = getModelFromDevicePositions();
		EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(this.getDataStoreKey(), model);
	}

	// Load alignment settings from persistence store.
	private void loadAlignmentStageSettings() {
		AlignmentStageModel model = new AlignmentStageModel();
		model = EdeDataStore.INSTANCE.getPreferenceDataStore().loadConfiguration(this.getDataStoreKey(), AlignmentStageModel.class);
		setDevicePositionsFromModel( model );
	}

	@SuppressWarnings("static-access")
	private void createControlsSection() throws Exception {
		final Section section = toolkit.createSection(form.getBody(), Section.TITLE_BAR);
		toolkit.paintBordersFor(section);
		section.setText("Alignment stage");
		toolkit.paintBordersFor(section);
		section.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite sectionComposite = toolkit.createComposite(section, SWT.NONE);
		toolkit.paintBordersFor(sectionComposite);
		sectionComposite.setLayout(new GridLayout());
		section.setClient(sectionComposite);

		Composite composite = createAlignmentStageXY(sectionComposite, ScannableSetup.ALIGNMENT_STAGE_X_POSITION, ScannableSetup.ALIGNMENT_STAGE_Y_POSITION);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		ScannableMotorMoveObserver.setupStopToolbarButton(section, movingScannables);
		ScannableSetup.ALIGNMENT_STAGE_X_POSITION.getScannable().addIObserver(moveObserver);
		ScannableSetup.ALIGNMENT_STAGE_Y_POSITION.getScannable().addIObserver(moveObserver);

//		Button alignmentStageCalibrationButton = toolkit.createButton(sectionComposite, "Calibrate aligment stage", SWT.None);
//		alignmentStageCalibrationButton.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
//		alignmentStageCalibrationButton.addListener(SWT.Selection, new Listener() {
//			@Override
//			public void handleEvent(Event event) {
//				// FIXME Complete implementation
//			}
//		});

		Composite alignmentStageComposite = toolkit.createComposite(sectionComposite, SWT.None);
		alignmentStageComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		alignmentStageComposite.setLayout(new GridLayout(3, false));

		Scannable scannable = ScannableSetup.ALIGNMENT_STAGE.getScannable();
		if (scannable instanceof AlignmentStage) {
			alignmentStage = (AlignmentStage) scannable;

			Label label = toolkit.createLabel(alignmentStageComposite, "X-ray eye", SWT.None);
			label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

			createXYControlsAndMoveButton(alignmentStageComposite,
					AlignmentStageScannable.AlignmentStageDevice.eye,
					AlignmentStageScannable.Location.X_POS_PROP_NAME,
					AlignmentStageScannable.Location.Y_POS_PROP_NAME);

			label = toolkit.createLabel(alignmentStageComposite, "Slits", SWT.None);
			label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

			createXYControlsAndMoveButton(alignmentStageComposite,
					AlignmentStageScannable.AlignmentStageDevice.slits,
					AlignmentStageScannable.Location.X_POS_PROP_NAME,
					AlignmentStageScannable.Location.Y_POS_PROP_NAME);

			label = toolkit.createLabel(alignmentStageComposite, "Foils", SWT.None);
			label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

			createXYControlsAndMoveButton(alignmentStageComposite,
					AlignmentStageScannable.AlignmentStageDevice.foil,
					AlignmentStageScannable.Location.X_POS_PROP_NAME,
					AlignmentStageScannable.Location.Y_POS_PROP_NAME);

			label = toolkit.createLabel(alignmentStageComposite, "Hole", SWT.None);
			label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

			createXYControlsAndMoveButton(alignmentStageComposite,
					AlignmentStageScannable.AlignmentStageDevice.hole,
					AlignmentStageScannable.Location.X_POS_PROP_NAME,
					AlignmentStageScannable.Location.Y_POS_PROP_NAME);


			// Hole2
			label = toolkit.createLabel(alignmentStageComposite, "Hole2", SWT.None);
			label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

			createXYControlsAndMoveButton(alignmentStageComposite,
					AlignmentStageScannable.AlignmentStageDevice.hole2,
					AlignmentStageScannable.Location.X_POS_PROP_NAME,
					AlignmentStageScannable.Location.Y_POS_PROP_NAME);

			// Laser
			label = toolkit.createLabel(alignmentStageComposite, "Laser", SWT.None);
			label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

			createXYControlsAndMoveButton(alignmentStageComposite,
					AlignmentStageScannable.AlignmentStageDevice.laser,
					AlignmentStageScannable.Location.X_POS_PROP_NAME,
					AlignmentStageScannable.Location.Y_POS_PROP_NAME);

			//			Composite fastShutterComposite = toolkit.createComposite(sectionComposite, SWT.None);
			//			fastShutterComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
			//			fastShutterComposite.setLayout(new GridLayout(3, false));

			// label = toolkit.createLabel(alignmentStageComposite, "Fast shutter", SWT.None);
			// label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

			// Fast shutter not currently used - don't add button for it for now...
			/*
			createXYControlsAndMoveButton(alignmentStageComposite,
					AlignmentStageScannable.AlignmentStageDevice.shutter,
					AlignmentStageScannable.Location.X_POS_PROP_NAME,
					AlignmentStageScannable.Location.Y_POS_PROP_NAME);
			 */
		}

		Composite sectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(sectionSeparator);
		section.setSeparatorControl(sectionSeparator);
	}

	// Listener used to update persistence store when model changes.
	private final PropertyChangeListener textBoxListener = event -> saveAlignmentStageSettings();

	private Composite createAlignmentStageXY(Composite parent, ScannableSetup xScannable, ScannableSetup yScannable) throws Exception {
		Composite xyPositionComposite = toolkit.createComposite(parent, SWT.NONE);
		toolkit.paintBordersFor(xyPositionComposite);
		GridLayout layout = new GridLayout();
		layout.marginHeight = 0;
		layout.marginHeight = 0;
		xyPositionComposite.setLayout(layout);

		createMotorControl(xyPositionComposite, "Alignment stage x", xScannable);
		createMotorControl(xyPositionComposite, "Alignment stage y", yScannable);

		return xyPositionComposite;
	}

	/**
	 * Add a {@link NudgePositionerComposite} to parent composite to control the scannable in ScannableSetupObject
	 * @param parent
	 * @param label
	 * @param scnSetup
	 */
	private void createMotorControl(Composite parent, String label, ScannableSetup scnSetup) {
		ScannablePositionerControl control = new ScannablePositionerControl();
		control.setDisplayName(label);
		control.setHorizontalLayout(true);
		control.setScannableName(scnSetup.getScannableName());
		control.setUserUnits(scnSetup.getUnit().getText());
		control.setDisplayNameWidth(150);
		control.setIncrementTextWidth(30);
		control.createControl(parent);
	}

	// Like createXY function except also creates 'Move' button and adds listener to it.
	private void createXYControlsAndMoveButton(Composite parent, AlignmentStageDevice device, String xPropertyName, String yPropertyName) throws Exception {
		ObservableModel model = alignmentStage.getAlignmentStageDevice( device.name()).getLocation();
		Composite composite = createXY( parent, model, xPropertyName, yPropertyName );
		composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		model.addPropertyChangeListener( textBoxListener ); // add listener to update persistence store

		Button moveToButton = toolkit.createButton(parent, "Move", SWT.None);
		moveToButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));
		moveToButton.addListener(SWT.Selection, makeListenerForDevice( device ) );
	}

	private Composite createXY(Composite parent, ObservableModel model, String xPropertyName, String yPropertyName) throws Exception {
		Composite xyPositionComposite = toolkit.createComposite(parent, SWT.NONE);
		toolkit.paintBordersFor(xyPositionComposite);
		GridLayout layout = new GridLayout(2, true);
		layout.marginHeight = 0;
		layout.marginHeight = 0;
		xyPositionComposite.setLayout(layout);

		Composite xPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(xPositionComposite);
		xPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		xPositionComposite.setLayout(new GridLayout(2, false));

		Label xPosLabel = toolkit.createLabel(xPositionComposite, "x", SWT.None);
		xPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		NumberEditorControl xPosition = new NumberEditorControl(xPositionComposite, SWT.None, model, xPropertyName, false);
		xPosition.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		xPosition.setUnit(ClientConfig.UnitSetup.MILLI_METER.getText());
		xPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite yPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(yPositionComposite);
		yPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		yPositionComposite.setLayout(new GridLayout(2, false));

		Label yPosLabel = toolkit.createLabel(yPositionComposite, "y", SWT.None);
		yPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		NumberEditorControl yPosition = new NumberEditorControl(yPositionComposite, SWT.None, model, yPropertyName, false);
		yPosition.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		yPosition.setUnit(ClientConfig.UnitSetup.MILLI_METER.getText());
		yPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		return xyPositionComposite;
	}



	@Override
	public void setFocus() {
		form.setFocus();
	}

}
