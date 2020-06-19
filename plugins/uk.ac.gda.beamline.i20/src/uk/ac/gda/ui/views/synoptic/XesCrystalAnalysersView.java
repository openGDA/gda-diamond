/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

package uk.ac.gda.ui.views.synoptic;

import java.io.IOException;
import java.util.EnumMap;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.scannablegroup.IScannableGroupNamed;
import gda.factory.Finder;
/**
 * View of XES spectrometer crystal positions
 * @since 18/5/2017
 */
public class XesCrystalAnalysersView extends HardwareDisplayComposite {

	/** This 'SpectrometerScannable' enum (SS for brevity) is used to identify the different scannable motors associated
	 * with the crystal analysers.
	 * The enum contents should match the order (and purpose!) of scannables in the 'spectrometer' scannable group.
	 * This is used by {@link #scannableForType} map to go from enum value to the corresponding scannable.  */
	private enum SS {CRYST_MINUS1_X, CRYST_MINUS1_Y, CRYST_MINUS1_ROT, CRYST_MINUS1_PITCH,
		CRYST_CENTRE_Y, CRYST_CENTRE_ROT, CRYST_CENTRE_PITCH,
		CRYST_PLUS1_X, CRYST_PLUS1_Y, CRYST_PLUS1_ROT, CRYST_PLUS1_PITCH,
		DET_X, DET_Y, DET_ROT, XTAL_X, SPECT_ROT }

	/** Map from SS enum value to corresponding scannable object */
	private EnumMap<SS, Scannable> scannableForType;

	/** List of scannables that control position and orientation for each crystal */
	private static SS[] crystMinus1Scannables = new SS[]{SS.CRYST_MINUS1_X, SS.CRYST_MINUS1_Y, SS.CRYST_MINUS1_ROT, SS.CRYST_MINUS1_PITCH};
	private static SS[] crystCentreScannables = new SS[]{SS.CRYST_CENTRE_Y, SS.CRYST_CENTRE_ROT, SS.CRYST_CENTRE_PITCH};
	private static SS[] crystPlus1Scannables = new SS[]{SS.CRYST_PLUS1_X, SS.CRYST_PLUS1_Y, SS.CRYST_PLUS1_ROT, SS.CRYST_PLUS1_PITCH};

	private static SS[] rotationScannables = new SS[]{SS.CRYST_MINUS1_ROT, SS.CRYST_CENTRE_ROT, SS.CRYST_PLUS1_ROT};
	private static SS[] pitchScannables = new SS[]{SS.CRYST_MINUS1_PITCH, SS.CRYST_CENTRE_PITCH, SS.CRYST_PLUS1_PITCH};


	public XesCrystalAnalysersView(Composite parent, int style) {
		super(parent, style);
	}

	@Override
	protected void createControls(Composite parent) throws IOException, DeviceException {
		setViewName("XES Crystal Analyser View");
		setBackgroundImage(getImageFromPlugin("oe images/xes_analysers2.bmp"), new Point(50, 350));
		parent.setBackgroundMode(SWT.INHERIT_FORCE);

		setupScannables();

		createMotorControls(parent);
		createRadiusControls(parent);
		createCrystalCutControls(parent);
		createCrystalSelectControls(parent);
		createArrows(parent);
		createLabels(parent);

		addResizeListener(parent);
	}

	/**
	 * Map map from {@link SS} enum value to corresponding scannable.
	 * Scannables are obtained by using the finder for each name in the 'spectrometer' scannable group.
	 *
	 */
	private void setupScannables() {
		// Get list of names of all the scannables contained in the 'spectrometer' group
		IScannableGroupNamed spectrometerGroup = Finder.find("spectrometer");
		String[] nameList = spectrometerGroup.getGroupMembersNamesAsArray();

		// Get scannable for each item in group, store in map using corresponding enum value as key
		SS[] enumTypeForScannable = SS.values();
		scannableForType = new EnumMap<>(SS.class);
		for(int i=0; i<nameList.length; i++) {
			Scannable scannableFromGroup = Finder.find(nameList[i]);
			scannableForType.put(enumTypeForScannable[i], scannableFromGroup);
		}
	}

	/**
	 * Create SWT Group with several motor control widgets to control given list of scannable motors
	 * @param parent
	 * @param motors String array of scannable motor names
	 * @return Group containing motor controls
	 * @throws DeviceException
	 */
	private Group createMotorControlGroup(Composite parent, SS[] motors, int numColumns) throws DeviceException {
		// Controls for analyser crystal 1
		Group group = new Group(parent, SWT.NONE);
		GridLayout gridLayout = new GridLayout(numColumns, false);
		gridLayout.marginHeight = -5;
		gridLayout.verticalSpacing = -5;

		group.setLayout(gridLayout);
		for(SS motorName : motors) {
			MotorControlsGui motorControls = new MotorControlsGui(group, scannableForType.get(motorName), false);
			motorControls.getControls().setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, false, 1, 1));
		}
		return group;
	}

	private void createMotorControls(Composite parent) throws DeviceException {

		int topPositionPercentage = -85;
		int width = 180;
		// Controls for analyser crystal 1
		Group crystalGroupMinus1 = createMotorControlGroup(parent, crystMinus1Scannables, 1 );
		crystalGroupMinus1.setText("Analyser crystal -1");
		setWidgetPosition(crystalGroupMinus1, 0, topPositionPercentage, width);

		Group crystalGroupZero = createMotorControlGroup(parent, crystCentreScannables, 1);
		crystalGroupZero.setText("Analyser crystal 0");
		setWidgetPosition(crystalGroupZero, 45, topPositionPercentage, width);

		Group crystalGroupPlus1 = createMotorControlGroup(parent, crystPlus1Scannables, 1);
		crystalGroupPlus1.setText("Analyser crystal 1");
		setWidgetPosition(crystalGroupPlus1, 90, topPositionPercentage, width);

		MotorControlsGui motorControls = new MotorControlsGui(parent, scannableForType.get(SS.XTAL_X));
		motorControls.setLabel("Main translation (x)");
		setWidgetPosition(motorControls.getControls(), 0, 25, width);
	}

	private void createRadiusControls(Composite parent) {
		Composite group = new Group(parent, SWT.NONE);
		group.setLayout(new GridLayout(2, false));
		group.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, false, 1, 1));

		Label label = new Label(group, SWT.NONE);
		label.setText("Radius ");

		ScannablePositionGui radius = new ScannablePositionGui(group, "radius");
		radius.createTextbox();

		setWidgetPosition(group, 0,  95, 150);
	}

	private void createEnumControl(Composite parent, String labelText, String positionerName) {
		Label label = new Label(parent, SWT.NONE);
		label.setText(labelText);

		EnumPositionerGui enumPositioner = new EnumPositionerGui(parent, positionerName);
		enumPositioner.createCombo();
		label.setToolTipText(enumPositioner.getToolTipText());
	}

	private void createCrystalCutControls(Composite parent) {
		Group group = new Group(parent, SWT.NONE);
		group.setLayout(new GridLayout(2, false));
		group.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, false, 1, 1));
		group.setText("Crystal cuts");

		createEnumControl(group, "Material ", "material");
		createEnumControl(group, "   h", "cut1");
		createEnumControl(group, "   k", "cut2");
		createEnumControl(group, "   l", "cut3");

		setWidgetPosition(group, 0, 52, 150);
	}

	private void createCrystalSelectControls(Composite parent) {
		Group group = new Group(parent, SWT.NONE);
		group.setLayout(new GridLayout(2, false));
		group.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, false, 1, 1));
		group.setText("Analyser crystals to move");

		createEnumControl(group, "Crystal -1", "minusCrystalAllowedToMove");
		createEnumControl(group, "Crystal  0", "centreCrystalAllowedToMove");
		createEnumControl(group, "Crystal  1", "plusCrystalAllowedToMove");

		setWidgetPosition(group, 100, 32);
	}

	private void createArrows(Composite parent) throws IOException {
		// Crystal rotation
		HighlightImageLabel rotationArrow = new HighlightImageLabel(parent, scannableForType.get(SS.CRYST_MINUS1_ROT));
		rotationArrow.setImage(getImageFromPlugin("arrow images/yaw.png"));
		rotationArrow.setHighlightImage(getImageFromPlugin("arrow images/yaw_red.png"));
		setWidgetPosition(rotationArrow.getControl(), 64, 48);
		// attach all motors that do rotations to this label
		for(SS scn : rotationScannables) {
			scannableForType.get(scn).addIObserver(rotationArrow);
		}

		// Crystal pitch
		HighlightImageLabel pitchArrow = new HighlightImageLabel(parent, scannableForType.get(SS.CRYST_PLUS1_PITCH));
		pitchArrow.setImage(getImageFromPlugin("arrow images/pitch.png"));
		pitchArrow.setHighlightImage(getImageFromPlugin("arrow images/pitch_red.png"));
		setWidgetPosition(pitchArrow.getControl(), 82, 21);
		// attach all motors that do rotations to this label
		for(SS scn : pitchScannables) {
			scannableForType.get(scn).addIObserver(pitchArrow);
		}

		// X translation
		HighlightImageLabel xTranslationArrow = new HighlightImageLabel(parent, scannableForType.get(SS.XTAL_X));
		xTranslationArrow.setImage(getImageFromPlugin("arrow images/z.png"));
		xTranslationArrow.setHighlightImage(getImageFromPlugin("arrow images/z_red.png"));
		setWidgetPosition(xTranslationArrow.getControl(), 65, 80);
	}

	private void createLabels(Composite parent) {
		// Labels on crystals (-1, 0, 1)
		Label label = new Label(parent, SWT.NONE);
		label.setText("-1");
		setWidgetPosition(label, 46, 7);

		label = new Label(parent, SWT.NONE);
		label.setText("0");
		setWidgetPosition(label, 61, 12);

		label = new Label(parent, SWT.NONE);
		label.setText("1");
		setWidgetPosition(label, 71, 17);

		// Label for crystal rotation arrow
		label = new Label(parent, SWT.NONE);
		label.setText("Rotation");
		setWidgetPosition(label, 67, 66);

		// Label for crystal pitch arrow
		label = new Label(parent, SWT.NONE);
		label.setText("Pitch");
		setWidgetPosition(label, 93, 30);

		// Label for x translation arrow
		label = new Label(parent, SWT.NONE);
		label.setText("X translation");
		setWidgetPosition(label, 65, 90);
	}
}
