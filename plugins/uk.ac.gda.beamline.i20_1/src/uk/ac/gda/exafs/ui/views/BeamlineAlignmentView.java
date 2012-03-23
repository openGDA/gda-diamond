/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.ui.views;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ControlAdapter;
import org.eclipse.swt.events.ControlEvent;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;

import uk.ac.gda.richbeans.components.FieldComposite.NOTIFY_TYPE;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;
import uk.ac.gda.richbeans.components.wrappers.ComboWrapper;

/**
 * Has controls for operating the lookuptable matching optics positions to energy
 * 
 */
public class BeamlineAlignmentView extends ViewPart {

	public static String ID = "uk.ac.gda.exafs.ui.views.beamlinealignmentview";
	private Combo cmbCrystalCut;
	private Combo cmbDetectorType;
	private ScaleBox txtWigglerTarget;
	private Button btnWigglerMove;
	private Label lblWigglerReadback;
	private ScaleBox txtSlitTarget;
	private Button btnSlitMove;
	private Label lblSlitReadback;
	private Combo txtME1StripeTarget;
	private Button btnME1StripeMove;
	private Label lblME1StripeReadback;
	private ScaleBox txtThetaTarget;
	private Button btnThetaMove;
	private Label lblThetaReadback;
	private Combo txtME2StripeTarget;
	private Button btnME2StripeMove;
	private Label lblME2StripeReadback;
	private ScaleBox txtME2PitchTarget;
	private Button btnME2PitchMove;
	private Label lblME2PitchReadback;
	private ScaleBox txtDetDistTarget;
	private Button btnDetDistMove;
	private Label lblDetDistReadback;
	private ScaleBox txtPolyTarget;
	private Button btnPolyMove;
	private Label lblPolyReadback;
	private ScaleBox txtPolyDistTarget;
	private Button btnPolyDistMove;
	private Label lblPolyDistReadback;
	private GridData comboGD;
	private GridData textGD;
	private GridData readbackGD;
	private ComboWrapper element;
	private ComboWrapper edge;
	private ScaleBox edgeEnergy_Label;
	private Combo cmbCrystalType;
	private Combo cmbCrystalQ;
	private ScaleBox txtPolyThetaTarget;
	private Button btnPolyThetaMove;
	private Label lblPolyThetaReadback;
	private ScaleBox txtPolyBendTarget;
	private Button btnPolyBendMove;
	private Label lblPolyBendReadback;
	private Button btnSynchroniseThetas;

	@Override
	public void createPartControl(final Composite parent) {
		
		switchLayoutMode(parent);
		
		parent.addControlListener(new ControlAdapter() {
			@Override
			public void controlResized(ControlEvent e) {
				switchLayoutMode(parent);
				parent.pack(true);
			}
		});


		createGridDataObjects();
		
		createMainControls(parent);

		createMotorControls(parent);

		createSpectrumControls(parent);	
	}

	private void switchLayoutMode(Composite parent) {
		
		Point size = parent.getSize();
		if (size.x <= size.y) {
			parent.setLayout(new GridLayout(1, false));
		} else {
			parent.setLayout(new GridLayout(3, false));
		}
	}

	private void createGridDataObjects() {
		comboGD = new GridData(SWT.FILL, SWT.CENTER, false, false);
		comboGD.widthHint = 120;

		textGD = new GridData(SWT.FILL, SWT.CENTER, false, false);
		textGD.widthHint = 120;
		
		readbackGD = new GridData(SWT.LEFT, SWT.CENTER, false, false);
	}
	
	private GridData createLabelGridData(){
		return new GridData(SWT.RIGHT, SWT.CENTER, false, false);
	}

	private void createSpectrumControls(Composite parent) {
		Group motorGroup = new Group(parent, SWT.NONE);
		motorGroup.setText("Spectrum Bandwidth");
		GridDataFactory.fillDefaults().align(SWT.LEFT, SWT.FILL).applyTo(motorGroup);
		GridLayoutFactory.swtDefaults().numColumns(4).applyTo(motorGroup);

		Label lbl = new Label(motorGroup, SWT.NONE);
		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Calculated");
		lbl.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false));
		lbl = new Label(motorGroup, SWT.NONE);
		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Readback   ");
		lbl.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false));

		lbl = new Label(motorGroup, SWT.RIGHT);
		lbl.setText("Polychromator\nto sample");
		lbl.setLayoutData(createLabelGridData());
		txtPolyDistTarget = new ScaleBox(motorGroup, SWT.NONE);
		txtPolyDistTarget.setMinimum(0.1);
		txtPolyDistTarget.setMaximum(5);
		txtPolyDistTarget.setLayoutData(textGD);
		txtPolyDistTarget.setUnit("mm");
		btnPolyDistMove = new Button(motorGroup, SWT.NONE);
		btnPolyDistMove.setText("Move");
		linkButtonToScannable(btnPolyDistMove,"scannableName",txtPolyDistTarget);
		lblPolyDistReadback = new Label(motorGroup, SWT.NONE);
		lblPolyDistReadback.setText("1.95 mm");
		lblPolyDistReadback.setLayoutData(readbackGD);
		linkLabelToScannable(lblPolyDistReadback,"scannableName");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Sample to detector");
		lbl.setLayoutData(createLabelGridData());
		txtDetDistTarget = new ScaleBox(motorGroup, SWT.NONE);
		txtDetDistTarget.setMinimum(0.1);
		txtDetDistTarget.setMaximum(5);
		txtDetDistTarget.setLayoutData(textGD);
		txtDetDistTarget.setUnit("mm");
		btnDetDistMove = new Button(motorGroup, SWT.NONE);
		btnDetDistMove.setText("Move");
		lblDetDistReadback = new Label(motorGroup, SWT.NONE);
		lblDetDistReadback.setText("1.95 mm");
		lblDetDistReadback.setLayoutData(readbackGD);

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Polychromator");
		lbl.setLayoutData(createLabelGridData());
		txtPolyTarget = new ScaleBox(motorGroup, SWT.NONE);
		txtPolyTarget.setMinimum(0.1);
		txtPolyTarget.setMaximum(5);
		txtPolyTarget.setLayoutData(textGD);
		txtPolyTarget.setUnit("");
		btnPolyMove = new Button(motorGroup, SWT.NONE);
		btnPolyMove.setText("Move");
		lblPolyReadback = new Label(motorGroup, SWT.NONE);
		lblPolyReadback.setText("0.2");
		lblPolyReadback.setLayoutData(readbackGD);

		Group grpBandWidthEst = new Group(motorGroup, SWT.NONE);
		GridDataFactory.swtDefaults().span(2, 2).applyTo(grpBandWidthEst);
		GridLayout subPanelLayout = new GridLayout();
		subPanelLayout.numColumns = 2;
		grpBandWidthEst.setLayout(subPanelLayout);

		lbl = new Label(grpBandWidthEst, SWT.NONE);
		lbl.setText("Predicted bandwidth\n on detector");
		lbl.setLayoutData(createLabelGridData());

		lbl = new Label(grpBandWidthEst, SWT.NONE);
		lbl.setText("750eV");
		lbl.setForeground(PlatformUI.getWorkbench().getDisplay().getSystemColor(SWT.COLOR_RED));
		
		grpBandWidthEst.pack();  //pack now to get the right size before the rest of the view is packed.

	}

	private void createMotorControls(Composite parent) {
		Group motorGroup = new Group(parent, SWT.NONE);
		motorGroup.setText("Motor Positions");
		GridDataFactory.fillDefaults().align(SWT.LEFT, SWT.FILL).applyTo(motorGroup);
		GridLayoutFactory.swtDefaults().numColumns(4).applyTo(motorGroup);

		Label lbl = new Label(motorGroup, SWT.NONE);
		lbl = new Label(motorGroup, SWT.CENTER);
		lbl.setText("Calculated");
		lbl.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false));
		lbl = new Label(motorGroup, SWT.NONE);
		lbl = new Label(motorGroup, SWT.CENTER);
		lbl.setText("Readback   ");
		lbl.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false));

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Wiggler Gap");
		lbl.setLayoutData(createLabelGridData());
		txtWigglerTarget = new ScaleBox(motorGroup, SWT.NONE);
		txtWigglerTarget.setMinimum(0.1);
		txtWigglerTarget.setMaximum(5);
		txtWigglerTarget.setLayoutData(textGD);
		txtWigglerTarget.setUnit("mm");
		btnWigglerMove = new Button(motorGroup, SWT.NONE);
		btnWigglerMove.setText("Move");
		lblWigglerReadback = new Label(motorGroup, SWT.NONE);
		lblWigglerReadback.setText("1.95 mm");
		lblWigglerReadback.setLayoutData(readbackGD);

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Primary Slit HGap");
		lbl.setLayoutData(createLabelGridData());
		txtSlitTarget = new ScaleBox(motorGroup, SWT.NONE);
		txtSlitTarget.setMinimum(0.1);
		txtSlitTarget.setMaximum(5);
		txtSlitTarget.setLayoutData(textGD);
		txtSlitTarget.setUnit("mm");
		btnSlitMove = new Button(motorGroup, SWT.NONE);
		btnSlitMove.setText("Move");
		lblSlitReadback = new Label(motorGroup, SWT.NONE);
		lblSlitReadback.setText("25.50 mm");
		lblSlitReadback.setLayoutData(readbackGD);
		
		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("ME1 Stripe");
		lbl.setLayoutData(createLabelGridData());
		txtME1StripeTarget = new Combo(motorGroup, SWT.CENTER);
		txtME1StripeTarget.setItems(new String[] { "Rh", "Pt" });
		txtME1StripeTarget.select(0);
		txtME1StripeTarget.setLayoutData(comboGD);
		btnME1StripeMove = new Button(motorGroup, SWT.NONE);
		btnME1StripeMove.setText("Move");
		lblME1StripeReadback = new Label(motorGroup, SWT.NONE);
		lblME1StripeReadback.setText("Pt");
		lblME1StripeReadback.setLayoutData(readbackGD);

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("ME2 Stripe");
		lbl.setLayoutData(createLabelGridData());
		txtME2StripeTarget = new Combo(motorGroup, SWT.CENTER);
		txtME2StripeTarget.setItems(new String[] { "Rh", "Pt" });
		txtME2StripeTarget.select(0);
		txtME2StripeTarget.setLayoutData(comboGD);
		btnME2StripeMove = new Button(motorGroup, SWT.NONE);
		btnME2StripeMove.setText("Move");
		lblME2StripeReadback = new Label(motorGroup, SWT.NONE);
		lblME2StripeReadback.setText("Pt");
		lblME2StripeReadback.setLayoutData(readbackGD);

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("ME2 Pitch");
		lbl.setLayoutData(createLabelGridData());
		txtME2PitchTarget = new ScaleBox(motorGroup, SWT.NONE);
		txtME2PitchTarget.setMinimum(0.1);
		txtME2PitchTarget.setMaximum(5);
		txtME2PitchTarget.setLayoutData(textGD);
		txtME2PitchTarget.setUnit("mm");
		btnME2PitchMove = new Button(motorGroup, SWT.NONE);
		btnME2PitchMove.setText("Move");
		lblME2PitchReadback = new Label(motorGroup, SWT.NONE);
		lblME2PitchReadback.setText("1.95 mm");
		lblME2PitchReadback.setLayoutData(readbackGD);

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Poly Bend");
		lbl.setLayoutData(createLabelGridData());
		txtPolyBendTarget = new ScaleBox(motorGroup, SWT.NONE);
		txtPolyBendTarget.setMinimum(0.1);
		txtPolyBendTarget.setMaximum(5);
		txtPolyBendTarget.setLayoutData(textGD);
		txtPolyBendTarget.setUnit("mm");
		btnPolyBendMove = new Button(motorGroup, SWT.NONE);
		btnPolyBendMove.setText("Move");
		lblPolyBendReadback = new Label(motorGroup, SWT.NONE);
		lblPolyBendReadback.setText("20.00 mm");
		lblPolyBendReadback.setLayoutData(readbackGD);
		
		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Poly Theta");
		lbl.setLayoutData(createLabelGridData());
		txtPolyThetaTarget = new ScaleBox(motorGroup, SWT.NONE);
		txtPolyThetaTarget.setMinimum(0.1);
		txtPolyThetaTarget.setMaximum(5);
		txtPolyThetaTarget.setLayoutData(textGD);
		txtPolyThetaTarget.setUnit("deg");
		btnPolyThetaMove = new Button(motorGroup, SWT.NONE);
		btnPolyThetaMove.setText("Move");
		lblPolyThetaReadback = new Label(motorGroup, SWT.NONE);
		lblPolyThetaReadback.setText("60.00 deg");
		lblPolyThetaReadback.setLayoutData(readbackGD);
		
		btnSynchroniseThetas = new Button(motorGroup, SWT.CHECK);
		btnSynchroniseThetas.setText("Match TwoTheta arm to poly Theta value");
		GridDataFactory.swtDefaults().span(4, 1).applyTo(btnSynchroniseThetas);

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Two Theta");
		lbl.setLayoutData(createLabelGridData());
		txtThetaTarget = new ScaleBox(motorGroup, SWT.NONE);
		txtThetaTarget.setMinimum(0.1);
		txtThetaTarget.setMaximum(5);
		txtThetaTarget.setLayoutData(textGD);
		txtThetaTarget.setUnit("deg");
		btnThetaMove = new Button(motorGroup, SWT.NONE);
		btnThetaMove.setText("Move");
		lblThetaReadback = new Label(motorGroup, SWT.NONE);
		lblThetaReadback.setText("60.00 deg");
		lblThetaReadback.setLayoutData(readbackGD);

		Group grpPowerEst = new Group(motorGroup, SWT.NONE);
		GridDataFactory.swtDefaults().span(2, 2).applyTo(grpPowerEst);
		GridLayout subPanelLayout = new GridLayout();
		subPanelLayout.numColumns = 2;
		grpPowerEst.setLayout(subPanelLayout);

		lbl = new Label(grpPowerEst, SWT.NONE);
		lbl.setText("Estimated power\n on polychromator");
		lbl.setLayoutData(createLabelGridData());

		lbl = new Label(grpPowerEst, SWT.NONE);
		lbl.setText("180W");
		lbl.setForeground(PlatformUI.getWorkbench().getDisplay().getSystemColor(SWT.COLOR_RED));
		
		grpPowerEst.pack();  // pack first

	}

	private void createMainControls(Composite parent) {
		Composite mainControls = new Composite(parent, SWT.NONE);
		GridDataFactory.fillDefaults().align(SWT.CENTER, SWT.FILL).applyTo(mainControls);
		GridLayoutFactory.swtDefaults().numColumns(2).applyTo(mainControls);
		
		Label lbl = new Label(mainControls, SWT.NONE);
		lbl.setText("Element");
		lbl.setLayoutData(createLabelGridData());
		element = new ComboWrapper(mainControls, SWT.READ_ONLY);
		element.setItems(new String[]{"Au", "Ag", "Cu"});
		element.select(0);
		
		lbl = new Label(mainControls, SWT.NONE);
		lbl.setText("Edge");
		lbl.setLayoutData(createLabelGridData());
		edge = new ComboWrapper(mainControls, SWT.READ_ONLY);
		edge.setItems(new String[]{"k", "L1", "l2"});
		edge.select(1);
		
		lbl = new Label(mainControls, SWT.NONE);
		lbl.setText("Edge energy");
		lbl.setLayoutData(createLabelGridData());
		edgeEnergy_Label = new ScaleBox(mainControls, SWT.NONE);
		edgeEnergy_Label.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		edgeEnergy_Label.setUnit("eV");
		edgeEnergy_Label.setNotifyType(NOTIFY_TYPE.VALUE_CHANGED);
		edgeEnergy_Label.on();
		edgeEnergy_Label.setValue(9442.3);
		edgeEnergy_Label.setToolTipText("Will be the centre of the spectrum");

		lbl = new Label(mainControls, SWT.NONE);
		lbl.setText("Crystal Type");
		lbl.setLayoutData(createLabelGridData());
		cmbCrystalType = new Combo(mainControls, SWT.NONE);
		cmbCrystalType.setItems(new String[] { "Bragg" });
		cmbCrystalType.select(0);
		cmbCrystalType.setEnabled(false);

		lbl = new Label(mainControls, SWT.NONE);
		lbl.setText("Crystal Cut");
		lbl.setLayoutData(createLabelGridData());
		cmbCrystalCut = new Combo(mainControls, SWT.NONE);
		cmbCrystalCut.setItems(new String[] { "Si (1 1 1)" });
		cmbCrystalCut.select(0);

		lbl = new Label(mainControls, SWT.NONE);
		lbl.setText("q");
		lbl.setLayoutData(createLabelGridData());
		cmbCrystalQ = new Combo(mainControls, SWT.NONE);
		cmbCrystalQ.setItems(new String[] { "0.8", "1.0", "1.2" });
		cmbCrystalQ.select(0);

		lbl = new Label(mainControls, SWT.NONE);
		lbl.setText("Detector Type");
		lbl.setLayoutData(createLabelGridData());
		cmbDetectorType = new Combo(mainControls, SWT.NONE);
		cmbDetectorType.setItems(new String[] { "XSTRIP", "XH", "CCD" });
		cmbDetectorType.select(0);
		
		Button btnRefresh = new Button(mainControls, SWT.NONE);
		GridDataFactory.fillDefaults().span(2, 1).applyTo(btnRefresh);
		btnRefresh.setText("Refresh Calculations");
		
		btnRefresh.addSelectionListener(new SelectionListener() {
			
			@Override
			public void widgetSelected(SelectionEvent e) {
				// TODO choose correct table
				
				// extract suggested values from the table's columns
				
				// change all the txt widgets to the suggested values
				
			}
			
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				widgetSelected(e);				
			}
		});		
	}
	
	private void linkButtonToScannable(Button btnPolyDistMove2, final String string, final ScaleBox txtPolyDistTarget2) {
		btnPolyDistMove2.addSelectionListener(new SelectionListener() {
			
			@Override
			public void widgetSelected(SelectionEvent e) {
				// TODO get value from the scalebox
				
				// get the scannable from finder
				
				// move the scannable to the value
				
			}
			
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				widgetSelected(e);				
			}
		});
		
	}
	
	private void linkLabelToScannable(final Label lblPolyDistReadback2, String string) {
		// TODO get the scannable from the finder
		
		// create anonymous IObserver of the scannable which updates the Label
		
	}



	@Override
	public void setFocus() {
	}

}
