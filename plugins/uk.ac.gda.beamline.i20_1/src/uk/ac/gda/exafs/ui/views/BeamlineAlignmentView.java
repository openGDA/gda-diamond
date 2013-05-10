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

import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.Scannable;
import gda.device.scannable.ScannableUtils;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.observable.IObserver;
import gda.util.exafs.AbsorptionEdge;
import gda.util.exafs.Element;

import java.util.Iterator;

import org.apache.commons.lang.ArrayUtils;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ControlAdapter;
import org.eclipse.swt.events.ControlEvent;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.data.AlignmentParametersBean;
import uk.ac.gda.richbeans.components.FieldComposite.NOTIFY_TYPE;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;

/**
 * Has controls for operating the lookuptable matching optics positions to energy
 */
public class BeamlineAlignmentView extends ViewPart {

	private static Logger logger = LoggerFactory.getLogger(BeamlineAlignmentView.class);

	public static final String OUTPUT_BEAN_NAME = "beamlinealignmentresults";
	public static final String INPUT_BEAN_NAME = "beamlinealignmentparameters";
	public static String ID = "uk.ac.gda.exafs.ui.views.beamlinealignmentview";
	private Combo cmbCrystalCut;
	private Combo cmbDetectorType;
	private ScaleBox txtWigglerTarget;
	private Button btnWigglerMove;
	private Label lblWigglerReadback;
	private ScaleBox txtSlitTarget;
	private Button btnSlitMove;
	private Label lblSlitReadback;
	private Combo cmbME1StripeTarget;
	private Button btnME1StripeMove;
	private Label lblME1StripeReadback;
	private ScaleBox txtThetaTarget;
	private Button btnThetaMove;
	private Label lblThetaReadback;
	private Combo cmbME2StripeTarget;
	private Button btnME2StripeMove;
	private Label lblME2StripeReadback;
	private ScaleBox txtME2PitchTarget;
	private Button btnME2PitchMove;
	private Label lblME2PitchReadback;
	private ScaleBox txtDetDistTarget;
	private Button btnDetDistMove;
	private Label lblDetDistReadback;
	private GridData comboGD;
	private GridData textGD;
	private GridData readbackGD;
	private Combo element;
	private Combo edge;
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
	private ScaleBox txtPolyBendTarget2;
	private Button btnPolyBendMove2;
	private Label lblPolyBendReadback2;
	private Label lblPolyPower;
	private Combo cmbAtn1Target;
	private Button btnAtn1Move;
	private Label lblAtn1Readback;
	private Combo cmbAtn2Target;
	private Button btnAtn2Move;
	private Label lblAtn2Readback;
	private Combo cmbAtn3Target;
	private Button btnAtn3Move;
	private Label lblAtn3Readback;

	private Composite mainControls;

	private ScaleBox txtSampleHeight;

	private Button btnSampleHeightMove;

	private Label lblSampleHeightReadback;

	private ScaleBox txtDetHeightTarget;

	private Button btnDetHeightMove;

	private Label lblDetHeightReadback;

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

		readbackGD = new GridData(SWT.FILL, SWT.CENTER, false, false);
		readbackGD.widthHint = 120;
	}

	private GridData createLabelGridData() {
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

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Detector Distance");
		lbl.setLayoutData(createLabelGridData());
		txtDetDistTarget = new ScaleBox(motorGroup, SWT.NONE);
		txtDetDistTarget.setMinimum(0.1);
		txtDetDistTarget.setMaximum(5);
		txtDetDistTarget.setLayoutData(textGD);
		txtDetDistTarget.setUnit("mm");
		btnDetDistMove = new Button(motorGroup, SWT.NONE);
		btnDetDistMove.setText("Move");
		linkButtonToScannable(btnDetDistMove,"detector_z",txtDetDistTarget);
		lblDetDistReadback = new Label(motorGroup, SWT.NONE);
		lblDetDistReadback.setText("1.95 mm");
		lblDetDistReadback.setLayoutData(readbackGD);
		linkLabelToScannable(lblDetDistReadback,"detector_z");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Sample Height");
		lbl.setLayoutData(createLabelGridData());
		txtSampleHeight = new ScaleBox(motorGroup, SWT.NONE);
		txtSampleHeight.setMinimum(0.1);
		txtSampleHeight.setMaximum(5);
		txtSampleHeight.setLayoutData(textGD);
		txtSampleHeight.setUnit("mm");
		btnSampleHeightMove = new Button(motorGroup, SWT.NONE);
		btnSampleHeightMove.setText("Move");
		// there is no sample y in EDM!
//		linkButtonToScannable(btnSampleHeightMove,"sample_x",txtSampleHeight);
		lblSampleHeightReadback = new Label(motorGroup, SWT.NONE);
		lblSampleHeightReadback.setText("1.95 mm");
		lblSampleHeightReadback.setLayoutData(readbackGD);
//		linkLabelToScannable(lblDetDistReadback,"detector_z");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Detector Height");
		lbl.setLayoutData(createLabelGridData());
		txtDetHeightTarget = new ScaleBox(motorGroup, SWT.NONE);
		txtDetHeightTarget.setMinimum(0.1);
		txtDetHeightTarget.setMaximum(5);
		txtDetHeightTarget.setLayoutData(textGD);
		txtDetHeightTarget.setUnit("mm");
		btnDetHeightMove = new Button(motorGroup, SWT.NONE);
		btnDetHeightMove.setText("Move");
		linkButtonToScannable(btnDetHeightMove,"detector_y",txtDetHeightTarget);
		lblDetHeightReadback = new Label(motorGroup, SWT.NONE);
		lblDetHeightReadback.setText("1.95 mm");
		lblDetHeightReadback.setLayoutData(readbackGD);
		linkLabelToScannable(lblDetHeightReadback,"detector_y");
		
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

		grpBandWidthEst.pack(); // pack now to get the right size before the rest of the view is packed.

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
		linkButtonToScannable(btnWigglerMove, "wigglerGap", txtWigglerTarget);
		lblWigglerReadback = new Label(motorGroup, SWT.NONE);
		lblWigglerReadback.setText("1.95 mm");
		lblWigglerReadback.setLayoutData(readbackGD);
		linkLabelToScannable(lblWigglerReadback, "wigglerGap");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Primary Slit HGap");
		lbl.setLayoutData(createLabelGridData());
		txtSlitTarget = new ScaleBox(motorGroup, SWT.NONE);
		txtSlitTarget.setMinimum(0.1);
		txtSlitTarget.setMaximum(5);
		txtSlitTarget.setLayoutData(textGD);
		txtSlitTarget.setUnit("mrad");
		btnSlitMove = new Button(motorGroup, SWT.NONE);
		btnSlitMove.setText("Move");
		linkButtonToScannable(btnSlitMove, "s1_hgap", txtSlitTarget);
		lblSlitReadback = new Label(motorGroup, SWT.NONE);
		lblSlitReadback.setText("25.50 mrad");
		lblSlitReadback.setLayoutData(readbackGD);
		linkLabelToScannable(lblSlitReadback, "s1_hgap");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Attenuator 1");
		lbl.setLayoutData(createLabelGridData());
		cmbAtn1Target = new Combo(motorGroup, SWT.CENTER);
		// cmbAtn1Target.setItems(AlignmentParametersBean.ATN1Values);
		fillComboFromScannable(cmbAtn1Target, "atn1");
		cmbAtn1Target.select(0);
		cmbAtn1Target.setLayoutData(comboGD);
		btnAtn1Move = new Button(motorGroup, SWT.NONE);
		btnAtn1Move.setText("Move");
		linkComboButtonToScannable(btnAtn1Move, "atn1", cmbAtn1Target);
		lblAtn1Readback = new Label(motorGroup, SWT.NONE);
		lblAtn1Readback.setText(AlignmentParametersBean.ATN1Values[0]);
		lblAtn1Readback.setLayoutData(readbackGD);
		linkLabelToScannable(lblAtn1Readback, "atn1");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Attenuator 2");
		lbl.setLayoutData(createLabelGridData());
		cmbAtn2Target = new Combo(motorGroup, SWT.CENTER);
		// cmbAtn2Target.setItems(AlignmentParametersBean.ATN2Values);
		fillComboFromScannable(cmbAtn2Target, "atn2");
		cmbAtn2Target.select(0);
		cmbAtn2Target.setLayoutData(comboGD);
		btnAtn2Move = new Button(motorGroup, SWT.NONE);
		btnAtn2Move.setText("Move");
		linkComboButtonToScannable(btnAtn2Move, "atn2", cmbAtn2Target);
		lblAtn2Readback = new Label(motorGroup, SWT.NONE);
		lblAtn2Readback.setText(AlignmentParametersBean.ATN2Values[0]);
		lblAtn2Readback.setLayoutData(readbackGD);
		linkLabelToScannable(lblAtn2Readback, "atn2");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Attenuator 3");
		lbl.setLayoutData(createLabelGridData());
		cmbAtn3Target = new Combo(motorGroup, SWT.CENTER);
		// cmbAtn3Target.setItems(AlignmentParametersBean.ATN3Values);
		fillComboFromScannable(cmbAtn3Target, "atn3");
		cmbAtn3Target.select(0);
		cmbAtn3Target.setLayoutData(comboGD);
		btnAtn3Move = new Button(motorGroup, SWT.NONE);
		btnAtn3Move.setText("Move");
		linkComboButtonToScannable(btnAtn3Move, "atn3", cmbAtn3Target);
		lblAtn3Readback = new Label(motorGroup, SWT.NONE);
		lblAtn3Readback.setText(AlignmentParametersBean.ATN3Values[0]);
		lblAtn3Readback.setLayoutData(readbackGD);
		linkLabelToScannable(lblAtn3Readback, "atn3");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("ME1 Stripe");
		lbl.setLayoutData(createLabelGridData());
		cmbME1StripeTarget = new Combo(motorGroup, SWT.CENTER);
		// cmbME1StripeTarget.setItems(new String[] { AlignmentParametersBean.ME1Stripe[0],
		// AlignmentParametersBean.ME1Stripe[1] });
		fillComboFromScannable(cmbME1StripeTarget, "me1_stripe");
		cmbME1StripeTarget.select(0);
		cmbME1StripeTarget.setLayoutData(comboGD);
		btnME1StripeMove = new Button(motorGroup, SWT.NONE);
		btnME1StripeMove.setText("Move");
		linkComboButtonToScannable(btnME1StripeMove, "me1_stripe", cmbME1StripeTarget);
		lblME1StripeReadback = new Label(motorGroup, SWT.NONE);
		lblME1StripeReadback.setText(AlignmentParametersBean.ME1Stripe[0]);
		lblME1StripeReadback.setLayoutData(readbackGD);
		linkLabelToScannable(lblME1StripeReadback, "me1_stripe");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("ME2 Stripe");
		lbl.setLayoutData(createLabelGridData());
		cmbME2StripeTarget = new Combo(motorGroup, SWT.CENTER);
		// cmbME2StripeTarget.setItems(new String[] { AlignmentParametersBean.ME2Stripe[0],
		// AlignmentParametersBean.ME2Stripe[1], AlignmentParametersBean.ME2Stripe[2] });
		fillComboFromScannable(cmbME2StripeTarget, "me2_stripe");
		cmbME2StripeTarget.select(0);
		cmbME2StripeTarget.setLayoutData(comboGD);
		btnME2StripeMove = new Button(motorGroup, SWT.NONE);
		btnME2StripeMove.setText("Move");
		linkComboButtonToScannable(btnME2StripeMove, "me2_stripe", cmbME2StripeTarget);
		lblME2StripeReadback = new Label(motorGroup, SWT.NONE);
		lblME2StripeReadback.setText(AlignmentParametersBean.ME2Stripe[0]);
		lblME2StripeReadback.setLayoutData(readbackGD);
		linkLabelToScannable(lblME2StripeReadback, "me2_stripe");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("ME2 Pitch");
		lbl.setLayoutData(createLabelGridData());
		txtME2PitchTarget = new ScaleBox(motorGroup, SWT.NONE);
		txtME2PitchTarget.setMinimum(0.1);
		txtME2PitchTarget.setMaximum(5);
		txtME2PitchTarget.setLayoutData(textGD);
		txtME2PitchTarget.setUnit("mrad");
		btnME2PitchMove = new Button(motorGroup, SWT.NONE);
		btnME2PitchMove.setText("Move");
		linkButtonToScannable(btnME2PitchMove, "me2pitch", txtME2PitchTarget);
		lblME2PitchReadback = new Label(motorGroup, SWT.NONE);
		lblME2PitchReadback.setText("1.95 mrad");
		lblME2PitchReadback.setLayoutData(readbackGD);
		linkLabelToScannable(lblME2PitchReadback, "me2pitch");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Poly Bend1");
		lbl.setLayoutData(createLabelGridData());
		txtPolyBendTarget = new ScaleBox(motorGroup, SWT.NONE);
		txtPolyBendTarget.setMinimum(0.1);
		txtPolyBendTarget.setMaximum(5);
		txtPolyBendTarget.setLayoutData(textGD);
		txtPolyBendTarget.setUnit("mm");
		btnPolyBendMove = new Button(motorGroup, SWT.NONE);
		btnPolyBendMove.setText("Move");
		linkButtonToScannable(btnPolyBendMove, "polybend1", txtPolyBendTarget);
		lblPolyBendReadback = new Label(motorGroup, SWT.NONE);
		lblPolyBendReadback.setText("20.00 mm");
		lblPolyBendReadback.setLayoutData(readbackGD);
		linkLabelToScannable(lblPolyBendReadback, "polybend1");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Poly Bend2");
		lbl.setLayoutData(createLabelGridData());
		txtPolyBendTarget2 = new ScaleBox(motorGroup, SWT.NONE);
		txtPolyBendTarget2.setMinimum(0.1);
		txtPolyBendTarget2.setMaximum(5);
		txtPolyBendTarget2.setLayoutData(textGD);
		txtPolyBendTarget2.setUnit("mm");
		btnPolyBendMove2 = new Button(motorGroup, SWT.NONE);
		btnPolyBendMove2.setText("Move");
		linkButtonToScannable(btnPolyBendMove2, "polybend2", txtPolyBendTarget2);
		lblPolyBendReadback2 = new Label(motorGroup, SWT.NONE);
		lblPolyBendReadback2.setText("20.00 mm");
		lblPolyBendReadback2.setLayoutData(readbackGD);
		linkLabelToScannable(lblPolyBendReadback2, "polybend2");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Poly Bragg");
		lbl.setLayoutData(createLabelGridData());
		txtPolyThetaTarget = new ScaleBox(motorGroup, SWT.NONE);
		txtPolyThetaTarget.setMinimum(0.1);
		txtPolyThetaTarget.setMaximum(5);
		txtPolyThetaTarget.setLayoutData(textGD);
		txtPolyThetaTarget.setUnit("deg");
		btnPolyThetaMove = new Button(motorGroup, SWT.NONE);
		btnPolyThetaMove.setText("Move");
		linkButtonToScannable(btnPolyThetaMove, "polytheta", txtPolyThetaTarget);
		lblPolyThetaReadback = new Label(motorGroup, SWT.NONE);
		lblPolyThetaReadback.setText("60.00 deg");
		lblPolyThetaReadback.setLayoutData(readbackGD);
		linkLabelToScannable(lblPolyThetaReadback, "polytheta");

		btnSynchroniseThetas = new Button(motorGroup, SWT.CHECK);
		btnSynchroniseThetas.setText("Match TwoTheta arm to Poly Bragg value");
		GridDataFactory.swtDefaults().span(4, 1).applyTo(btnSynchroniseThetas);
		btnSynchroniseThetas.addSelectionListener(new SelectionAdapter() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				boolean selected = btnSynchroniseThetas.getSelection();
				txtThetaTarget.setEnabled(!selected);
				btnThetaMove.setEnabled(!selected);
			}
		});
		
		btnPolyThetaMove.addSelectionListener(new SelectionAdapter() {

			private Scannable theScannable;

			@Override
			public void widgetSelected(SelectionEvent e) {
				if (btnSynchroniseThetas.getSelection()) {
					// get value from the scalebox
					Double target = txtPolyThetaTarget.getNumericValue();
					target *= 2;

					// get the scannable from finder
					if (theScannable == null)
						theScannable = Finder.getInstance().find("twotheta");

					// move the scannable to the value
					try {
						if (theScannable != null)
							theScannable.asynchronousMoveTo(target);
					} catch (Exception e1) {
						logger.error("Exception while moving twotheta to " + target + ": " + e1.getMessage(), e1);
					}
				}
			}
		});

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
		linkButtonToScannable(btnThetaMove, "twotheta", txtThetaTarget);
		lblThetaReadback = new Label(motorGroup, SWT.NONE);
		lblThetaReadback.setText("60.00 deg");
		lblThetaReadback.setLayoutData(readbackGD);
		linkLabelToScannable(lblThetaReadback, "twotheta");

		Group grpPowerEst = new Group(motorGroup, SWT.NONE);
		GridDataFactory.swtDefaults().span(2, 2).applyTo(grpPowerEst);
		GridLayout subPanelLayout = new GridLayout();
		subPanelLayout.numColumns = 2;
		grpPowerEst.setLayout(subPanelLayout);

		lbl = new Label(grpPowerEst, SWT.NONE);
		lbl.setText("Estimated power\n on polychromator");
		lbl.setLayoutData(createLabelGridData());

		lblPolyPower = new Label(grpPowerEst, SWT.NONE);
		lblPolyPower.setText("180W");
		lblPolyPower.setForeground(PlatformUI.getWorkbench().getDisplay().getSystemColor(SWT.COLOR_RED));

		grpPowerEst.pack(); // pack first

	}

	private void createMainControls(Composite parent) {
		mainControls = new Composite(parent, SWT.NONE);
		GridDataFactory.fillDefaults().align(SWT.CENTER, SWT.FILL).applyTo(mainControls);
		GridLayoutFactory.swtDefaults().numColumns(2).applyTo(mainControls);

		Label lbl = new Label(mainControls, SWT.NONE);
		lbl.setText("Element");
		lbl.setLayoutData(createLabelGridData());
		element = new Combo(mainControls, SWT.READ_ONLY);
		element.setLayoutData(comboGD);
		element.setItems(Element.getSortedEdgeSymbols("P", "U"));
		element.select(0);

		element.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				updateEdgesCombo();
			}

		});

		lbl = new Label(mainControls, SWT.NONE);
		lbl.setText("Edge");
		lbl.setLayoutData(createLabelGridData());
		edge = new Combo(mainControls, SWT.READ_ONLY);
		edge.setLayoutData(comboGD);
		edge.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				try {
					String selectedElementString = element.getItem(element.getSelectionIndex());
					Element selectedElement = Element.getElement(selectedElementString);
					String selectedEdgeString = edge.getItem(edge.getSelectionIndex());
					final double edgeEn = selectedElement.getEdgeEnergy(selectedEdgeString);
					edgeEnergy_Label.setValue(edgeEn);
				} catch (Exception e1) {
					// logger.error("Cannot update element.", e1);
				}
			}
		});

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
		edgeEnergy_Label.setMinimum(6000);
		edgeEnergy_Label.setMaximum(26000);

		lbl = new Label(mainControls, SWT.NONE);
		lbl.setText("Crystal Type");
		lbl.setLayoutData(createLabelGridData());
		cmbCrystalType = new Combo(mainControls, SWT.NONE);
		cmbCrystalType.setItems(new String[] { AlignmentParametersBean.CrystalType[0],
				AlignmentParametersBean.CrystalType[1] });
		cmbCrystalType.select(0);
		cmbCrystalType.setEnabled(false);
		cmbCrystalType.addSelectionListener(new SelectionListener() {
			
			@Override
			public void widgetSelected(SelectionEvent e) {
				updateEdgesCombo();
			}
			
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});

		lbl = new Label(mainControls, SWT.NONE);
		lbl.setText("Crystal Cut");
		lbl.setLayoutData(createLabelGridData());
		cmbCrystalCut = new Combo(mainControls, SWT.NONE);
		cmbCrystalCut.setItems(new String[] { AlignmentParametersBean.CrystalCut[0],
				AlignmentParametersBean.CrystalCut[1] });
		cmbCrystalCut.select(0);
		cmbCrystalCut.addSelectionListener(new SelectionListener() {
			
			@Override
			public void widgetSelected(SelectionEvent e) {
				updateEdgesCombo();
			}
			
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});


		lbl = new Label(mainControls, SWT.NONE);
		lbl.setText("q");
		lbl.setLayoutData(createLabelGridData());
		cmbCrystalQ = new Combo(mainControls, SWT.NONE);
		cmbCrystalQ.setItems(new String[] { AlignmentParametersBean.Q[0].toString(),
				AlignmentParametersBean.Q[1].toString(), AlignmentParametersBean.Q[2].toString() });
		cmbCrystalQ.select(1);

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

				String selectedElementString = element.getItem(element.getSelectionIndex());
				Element selectedElement = Element.getElement(selectedElementString);
				String selectedEdgeString = edge.getItem(edge.getSelectionIndex());
				AbsorptionEdge absEdge = selectedElement.getEdge(selectedEdgeString);

				String qString = cmbCrystalQ.getItem(cmbCrystalQ.getSelectionIndex());
				Double q = Double.parseDouble(qString);

				String xtalCutString = cmbCrystalCut.getItem(cmbCrystalCut.getSelectionIndex());
				String xtalTypeString = cmbCrystalType.getItem(cmbCrystalType.getSelectionIndex());
				String detectorString = cmbDetectorType.getItem(cmbDetectorType.getSelectionIndex());

				try {
					AlignmentParametersBean bean = new AlignmentParametersBean(xtalTypeString, xtalCutString, q,
							detectorString, absEdge);

					InterfaceProvider.getJythonNamespace().placeInJythonNamespace(INPUT_BEAN_NAME, bean);

					InterfaceProvider.getCommandRunner().runCommand(
							OUTPUT_BEAN_NAME + "=None;from alignment import alignment_parameters; " + OUTPUT_BEAN_NAME
									+ " = alignment_parameters.calc_parameters(" + INPUT_BEAN_NAME + ")");
					// give the command a chance to run.
					Thread.sleep(500);
					AlignmentParametersBean results = (AlignmentParametersBean) InterfaceProvider.getJythonNamespace()
							.getFromJythonNamespace(OUTPUT_BEAN_NAME);

					updateUIFromBean(results);
				} catch (Exception e1) {
					logger.error("Exception when trying to run the script which performs the alignment calculations.",e1);
				}

			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				widgetSelected(e);
			}
		});
	}
	
	private void updateEdgesCombo() {
		String selectedElementString = element.getItem(element.getSelectionIndex());
		Element selectedElement = Element.getElement(selectedElementString);
		final Iterator<String> edges;
		if (cmbCrystalCut.getSelectionIndex() == 0) {
			edges = selectedElement.getEdgesInEnergyRange(6000.0, 14000.0);
		} else {
			edges = selectedElement.getEdgesInEnergyRange(7000.0, 26000.0);
		}
		if (edges == null) {
			edge.setItems(new String[] {});
			edgeEnergy_Label.setValue(0.0);
		} else {
			String[] edgesArray = new String[] {};
			for (; edges.hasNext();) {
				String edge = edges.next();
				edgesArray = (String[]) ArrayUtils.add(edgesArray, edge);
			}
			edge.setItems(edgesArray);
			edge.select(0);
			edgeEnergy_Label.setValue(selectedElement.getEdgeEnergy(edgesArray[0]));
		}
		mainControls.redraw();
		mainControls.pack(true);
	}

	protected void updateUIFromBean(final AlignmentParametersBean results) {

		if (results == null) {
			logger.info("Nothing returned from the script which runs the alignment calculations.");
			return;
		}

		PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {

			@Override
			public void run() {
				txtWigglerTarget.setValue(results.getWigglerGap());
				txtPolyBendTarget.setValue(results.getPolyBend1());
				txtPolyBendTarget2.setValue(results.getPolyBend2());
				String requiredMe1Stripe = results.getMe1stripe().toString();
				cmbME1StripeTarget.select(cmbME1StripeTarget.indexOf(requiredMe1Stripe));
				String requiredMe2Stripe = results.getMe2stripe().toString();
				cmbME2StripeTarget.select(cmbME2StripeTarget.indexOf(requiredMe2Stripe));
				txtSlitTarget.setValue(results.getPrimarySlitGap());
				txtThetaTarget.setValue(results.getArm2Theta());
				txtPolyThetaTarget.setValue(results.getBraggAngle());
				txtDetDistTarget.setValue(results.getDetectorDistance()*1000); // convert to mm
				txtME2PitchTarget.setValue(results.getMe2Pitch());
				txtSampleHeight.setValue(results.getSampleHeight()); // convert to mm
				txtDetHeightTarget.setValue(results.getDetectorHeight()); // convert to mm

				String atn1String = results.getAtn1().toString();
				int atn1Index = ArrayUtils.indexOf(AlignmentParametersBean.ATN1, atn1String);
				cmbAtn1Target.select(atn1Index);
				String atn2String = results.getAtn2().toString();
				int atn2Index = ArrayUtils.indexOf(AlignmentParametersBean.ATN2, atn2String);
				cmbAtn2Target.select(atn2Index);
				String atn3String = results.getAtn3().toString();
				int atn3Index = ArrayUtils.indexOf(AlignmentParametersBean.ATN3, atn3String);
				cmbAtn3Target.select(atn3Index);

				String powerString = String.format("%.1d W", results.getPower());
				lblPolyPower.setText(powerString);
				if (results.getPower() > 350) {
					lblPolyPower.setForeground(PlatformUI.getWorkbench().getDisplay().getSystemColor(SWT.COLOR_RED));
				} else {
					lblPolyPower.setForeground(PlatformUI.getWorkbench().getDisplay().getSystemColor(SWT.COLOR_BLACK));
				}
			}

		});
	}

	private void linkButtonToScannable(Button theButton, final String scannableName, final ScaleBox theScaleBox) {
		theButton.addSelectionListener(new SelectionListener() {

			Scannable theScannable = null;

			@Override
			public void widgetSelected(SelectionEvent e) {
				// get value from the scalebox
				Double target = theScaleBox.getNumericValue();

				// get the scannable from finder
				if (theScannable == null)
					theScannable = Finder.getInstance().find(scannableName);

				// move the scannable to the value
				try {
					if (theScannable != null)
						theScannable.asynchronousMoveTo(target);
				} catch (Exception e1) {
					logger.error("Exception while moving " + scannableName + " to " + target + ": " + e1.getMessage(),
							e1);
				}
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				widgetSelected(e);
			}
		});
	}
	
	private void linkComboButtonToScannable(Button theButton, final String scannableName, final Combo combo) {
		theButton.addSelectionListener(new SelectionListener() {

			Scannable theScannable = null;

			@Override
			public void widgetSelected(SelectionEvent e) {
				// get value from the scalebox
				int index = combo.getSelectionIndex();
				if (index == -1) return;
				
				String selected  =combo.getItem(index);

				// get the scannable from finder
				if (theScannable == null)
					theScannable = Finder.getInstance().find(scannableName);

				// move the scannable to the value
				try {
					if (theScannable != null)
						theScannable.asynchronousMoveTo(selected);
				} catch (Exception e1) {
					logger.error("Exception while moving " + scannableName + " to " + selected + ": " + e1.getMessage(),
							e1);
				}
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				widgetSelected(e);
			}
		});
	}


	private void fillComboFromScannable(final Combo combo, final String scannableName) {

		// get the scannable from the finder
		final EnumPositioner theScannable = Finder.getInstance().find(scannableName);
		if (theScannable == null){
			return;
		}

		String[] positions;
		try {
			positions = theScannable.getPositions();
			combo.setItems(positions);
		} catch (DeviceException e) {
			logger.error("Exception while getting positions from  " + scannableName +": "+e.getMessage(), e);
		}
		
	}

	private void linkLabelToScannable(final Label lblPolyDistReadback2, final String scannableName) {

		// get the scannable from the finder
		final Scannable theScannable = Finder.getInstance().find(scannableName);
		if (theScannable == null){
			lblPolyDistReadback2.setText("not connected");
			return;
		}

		theScannable.addIObserver(new IObserver() {

			@Override
			public void update(Object source, Object arg) {
				try {
					//String or double?
					final String newPosition;
					if (theScannable.getOutputFormat()[0].contains("s")){
						newPosition = ScannableUtils.getFormattedCurrentPositionArray(theScannable)[0];
					} else {
						double[] values = ScannableUtils.positionToArray(theScannable.getPosition(),theScannable);
						newPosition = String.format(theScannable.getOutputFormat()[0], values[0]);
					}
					Display.getDefault().asyncExec(new Runnable() {
						@Override
						public void run() {
							lblPolyDistReadback2.setText(newPosition);
						}
					});
				} catch (DeviceException e) {
					logger.error("Exception while getting position of  " + scannableName + ": "+e.getMessage(), e);
				}

			}
		});
	}

	@Override
	public void setFocus() {
	}

}
