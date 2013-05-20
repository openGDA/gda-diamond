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

import gda.device.EnumPositioner;
import gda.device.Scannable;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.util.exafs.AbsorptionEdge;
import gda.util.exafs.Element;

import java.text.ParseException;
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
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.data.AlignmentParametersBean;
import uk.ac.gda.richbeans.components.FieldComposite.NOTIFY_TYPE;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;
import uk.ac.gda.richbeans.components.wrappers.LabelWrapper;
import uk.ac.gda.richbeans.components.wrappers.LabelWrapper.TEXT_TYPE;
import uk.ac.gda.richbeans.event.ValueAdapter;
import uk.ac.gda.richbeans.event.ValueEvent;
import uk.ac.gda.ui.viewer.EnumPositionViewer;
import uk.ac.gda.ui.viewer.MotorPositionViewer;
import uk.ac.gda.ui.viewer.RotationViewer;

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
	private LabelWrapper txtWigglerTarget;
	private Button btnWigglerMove;
	private MotorPositionViewer lblWigglerReadback;
	private LabelWrapper txtSlitTarget;
	private Button btnSlitMove;
	private MotorPositionViewer lblSlitReadback;
	private LabelWrapper cmbME1StripeTarget;
	private Button btnME1StripeMove;
	private EnumPositionViewer lblME1StripeReadback;
	private LabelWrapper txtThetaTarget;
	private Button btnThetaMove;
	private RotationViewer lblThetaReadback;
	private LabelWrapper cmbME2StripeTarget;
	private Button btnME2StripeMove;
	private EnumPositionViewer lblME2StripeReadback;
	private LabelWrapper txtME2PitchTarget;
	private Button btnME2PitchMove;
	private MotorPositionViewer lblME2PitchReadback;
	private LabelWrapper txtDetDistTarget;
	private Button btnDetDistMove;
	private MotorPositionViewer lblDetDistReadback;
	private GridData comboGD;
	private GridData textGD;
	private GridData readbackGD;
	private Combo element;
	private Combo edge;
	private ScaleBox edgeEnergy_Label;
	private Combo cmbCrystalType;
	private Combo cmbCrystalQ;
	private LabelWrapper txtPolyThetaTarget;
	private Button btnPolyThetaMove;
	private RotationViewer lblPolyThetaReadback;
	private LabelWrapper txtPolyBendTarget;
	private Button btnPolyBendMove;
	private RotationViewer lblPolyBendReadback;
	private Button btnSynchroniseThetas;
	private LabelWrapper txtPolyBendTarget2;
	private Button btnPolyBendMove2;
	private RotationViewer lblPolyBendReadback2;
	private Label lblPolyPower;
	private LabelWrapper cmbAtn1Target;
	private Button btnAtn1Move;
	private EnumPositionViewer lblAtn1Readback;
	private LabelWrapper cmbAtn2Target;
	private Button btnAtn2Move;
	private EnumPositionViewer lblAtn2Readback;
	private LabelWrapper cmbAtn3Target;
	private Button btnAtn3Move;
	private EnumPositionViewer lblAtn3Readback;
	private Composite mainControls;
	private LabelWrapper txtSampleHeight;
	private Button btnSampleHeightMove;
	private MotorPositionViewer lblSampleHeightReadback;
	private LabelWrapper txtDetHeightTarget;
	private Button btnDetHeightMove;
	private MotorPositionViewer lblDetHeightReadback;
	
	private Scannable twoThetaScannable;


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
		lbl.setText("Actual   ");
		lbl.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false));

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Detector Distance");
		lbl.setLayoutData(createLabelGridData());
		txtDetDistTarget = new LabelWrapper(motorGroup, SWT.NONE);
		txtDetDistTarget.setLayoutData(textGD);
		txtDetDistTarget.setUnit("mm");
		btnDetDistMove = new Button(motorGroup, SWT.NONE);
		btnDetDistMove.setText("Move");
		linkButtonToScannable(btnDetDistMove,"detector_z",txtDetDistTarget);
		lblDetDistReadback = createMotorPositionViewer(motorGroup,"detector_z");



		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Sample Height");
		lbl.setLayoutData(createLabelGridData());
		txtSampleHeight = new LabelWrapper(motorGroup, SWT.NONE);
		txtSampleHeight.setLayoutData(textGD);
		txtSampleHeight.setUnit("mm");
		btnSampleHeightMove = new Button(motorGroup, SWT.NONE);
		btnSampleHeightMove.setText("Move");
		// there is no sample y in EDM!
		lblSampleHeightReadback = createMotorPositionViewer(motorGroup,"sample_x");
		

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Detector Height");
		lbl.setLayoutData(createLabelGridData());
		txtDetHeightTarget = new LabelWrapper(motorGroup, SWT.NONE);
		txtDetHeightTarget.setLayoutData(textGD);
		txtDetHeightTarget.setUnit("mm");
		btnDetHeightMove = new Button(motorGroup, SWT.NONE);
		btnDetHeightMove.setText("Move");
		linkButtonToScannable(btnDetHeightMove,"detector_y",txtDetHeightTarget);
		lblDetHeightReadback = createMotorPositionViewer(motorGroup,"detector_y");
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
		txtWigglerTarget = new LabelWrapper(motorGroup, SWT.NONE);
		txtWigglerTarget.setLayoutData(textGD);
		txtWigglerTarget.setUnit("mm");
		btnWigglerMove = new Button(motorGroup, SWT.NONE);
		btnWigglerMove.setText("Move");
		linkButtonToScannable(btnWigglerMove, "wigglerGap", txtWigglerTarget);
		lblWigglerReadback = createMotorPositionViewer(motorGroup,"wigglerGap");
		

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Primary Slit HGap");
		lbl.setLayoutData(createLabelGridData());
		txtSlitTarget = new LabelWrapper(motorGroup, SWT.NONE);
		txtSlitTarget.setLayoutData(textGD);
		txtSlitTarget.setUnit("mrad");
		btnSlitMove = new Button(motorGroup, SWT.NONE);
		btnSlitMove.setText("Move");
		linkButtonToScannable(btnSlitMove, "s1_hgap", txtSlitTarget);
		lblSlitReadback = createMotorPositionViewer(motorGroup,"s1_hgap");
		
		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Attenuator 1");
		lbl.setLayoutData(createLabelGridData());
		cmbAtn1Target = new LabelWrapper(motorGroup, SWT.CENTER);
		cmbAtn1Target.setLayoutData(comboGD);
		cmbAtn1Target.setTextType(TEXT_TYPE.PLAIN_TEXT);
		btnAtn1Move = new Button(motorGroup, SWT.NONE);
		btnAtn1Move.setText("Move");
		linkButtonToScannable(btnAtn1Move, "atn1", cmbAtn1Target);
		lblAtn1Readback = createEnumPositionerViewer(motorGroup,"atn1");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Attenuator 2");
		lbl.setLayoutData(createLabelGridData());
		cmbAtn2Target = new LabelWrapper(motorGroup, SWT.CENTER);
		cmbAtn2Target.setLayoutData(comboGD);
		cmbAtn2Target.setTextType(TEXT_TYPE.PLAIN_TEXT);
		btnAtn2Move = new Button(motorGroup, SWT.NONE);
		btnAtn2Move.setText("Move");
		linkButtonToScannable(btnAtn2Move, "atn2", cmbAtn2Target);
		lblAtn2Readback = createEnumPositionerViewer(motorGroup,"atn2");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Attenuator 3");
		lbl.setLayoutData(createLabelGridData());
		cmbAtn3Target = new LabelWrapper(motorGroup, SWT.CENTER);
		cmbAtn3Target.setLayoutData(comboGD);
		cmbAtn3Target.setTextType(TEXT_TYPE.PLAIN_TEXT);
		btnAtn3Move = new Button(motorGroup, SWT.NONE);
		btnAtn3Move.setText("Move");
		linkButtonToScannable(btnAtn3Move, "atn3", cmbAtn3Target);
		lblAtn3Readback = createEnumPositionerViewer(motorGroup,"atn3");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("ME1 Stripe");
		lbl.setLayoutData(createLabelGridData());
		cmbME1StripeTarget = new LabelWrapper(motorGroup, SWT.CENTER);
		cmbME1StripeTarget.setLayoutData(comboGD);
		cmbME1StripeTarget.setTextType(TEXT_TYPE.PLAIN_TEXT);
		btnME1StripeMove = new Button(motorGroup, SWT.NONE);
		btnME1StripeMove.setText("Move");
		linkButtonToScannable(btnAtn1Move, "me1_stripe", cmbME1StripeTarget);
		lblME1StripeReadback = createEnumPositionerViewer(motorGroup,"me1_stripe");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("ME2 Stripe");
		lbl.setLayoutData(createLabelGridData());
		cmbME2StripeTarget = new LabelWrapper(motorGroup, SWT.CENTER);
		cmbME2StripeTarget.setLayoutData(comboGD);
		cmbME2StripeTarget.setTextType(TEXT_TYPE.PLAIN_TEXT);
		btnME2StripeMove = new Button(motorGroup, SWT.NONE);
		btnME2StripeMove.setText("Move");
		linkButtonToScannable(btnME2StripeMove, "me2_stripe", cmbME2StripeTarget);
		lblME2StripeReadback = createEnumPositionerViewer(motorGroup,"me2_stripe");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("ME2 Pitch");
		lbl.setLayoutData(createLabelGridData());
		txtME2PitchTarget = new LabelWrapper(motorGroup, SWT.NONE);
		txtME2PitchTarget.setLayoutData(textGD);
		txtME2PitchTarget.setUnit("mrad");
		btnME2PitchMove = new Button(motorGroup, SWT.NONE);
		btnME2PitchMove.setText("Move");
		linkButtonToScannable(btnME2PitchMove, "me2pitch", txtME2PitchTarget);
		lblME2PitchReadback = createMotorPositionViewer(motorGroup,"me2pitch");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Poly Bend1");
		lbl.setLayoutData(createLabelGridData());
		txtPolyBendTarget = new LabelWrapper(motorGroup, SWT.NONE);
		txtPolyBendTarget.setLayoutData(textGD);
		txtPolyBendTarget.setUnit("mm");
		btnPolyBendMove = new Button(motorGroup, SWT.NONE);
		btnPolyBendMove.setText("Move");
		linkButtonToScannable(btnPolyBendMove, "polybend1", txtPolyBendTarget);
		lblPolyBendReadback = createRotationViewer(motorGroup,"polybend1");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Poly Bend2");
		lbl.setLayoutData(createLabelGridData());
		txtPolyBendTarget2 = new LabelWrapper(motorGroup, SWT.NONE);
		txtPolyBendTarget2.setLayoutData(textGD);
		txtPolyBendTarget2.setUnit("mm");
		btnPolyBendMove2 = new Button(motorGroup, SWT.NONE);
		btnPolyBendMove2.setText("Move");
		linkButtonToScannable(btnPolyBendMove2, "polybend2", txtPolyBendTarget2);
		lblPolyBendReadback2 = createRotationViewer(motorGroup,"polybend2");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Poly Bragg");
		lbl.setLayoutData(createLabelGridData());
		txtPolyThetaTarget = new LabelWrapper(motorGroup, SWT.NONE);
		txtPolyThetaTarget.setLayoutData(textGD);
		txtPolyThetaTarget.setUnit("deg");
		btnPolyThetaMove = new Button(motorGroup, SWT.NONE);
		btnPolyThetaMove.setText("Move");
		linkButtonToScannable(btnPolyThetaMove, "polytheta", txtPolyThetaTarget);
		lblPolyThetaReadback = createRotationViewer(motorGroup,"polytheta");
		lblPolyThetaReadback.addValueListener(new ValueAdapter("polytheta") {
			
			@Override
			public void valueChangePerformed(ValueEvent e) {
				moveTwoThetaWithPolyBragg(e);
			}
		});
		

		btnSynchroniseThetas = new Button(motorGroup, SWT.CHECK);
		btnSynchroniseThetas.setText("Match TwoTheta arm to Poly Bragg value");
		GridDataFactory.swtDefaults().span(4, 1).applyTo(btnSynchroniseThetas);
		btnSynchroniseThetas.addSelectionListener(new SelectionAdapter() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				boolean selected = btnSynchroniseThetas.getSelection();
				txtThetaTarget.setEnabled(!selected);
				btnThetaMove.setEnabled(!selected);
				lblThetaReadback.setEnabled(!selected);
			}
		});
		
		btnPolyThetaMove.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				moveTwoThetaWithPolyBragg(null);
			}
		});

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Two Theta");
		lbl.setLayoutData(createLabelGridData());
		txtThetaTarget = new LabelWrapper(motorGroup, SWT.NONE);
		txtThetaTarget.setLayoutData(textGD);
		txtThetaTarget.setUnit("deg");
		btnThetaMove = new Button(motorGroup, SWT.NONE);
		btnThetaMove.setText("Move");
		linkButtonToScannable(btnThetaMove, "twotheta", txtThetaTarget);
		lblThetaReadback = createRotationViewer(motorGroup,"twotheta");

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
		edgeEnergy_Label.setValue(9442.3);
		edgeEnergy_Label.setToolTipText("Will be the centre of the spectrum");
		edgeEnergy_Label.setMinimum(6000);
		edgeEnergy_Label.setMaximum(26000);
		edgeEnergy_Label.on();

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
				cmbME1StripeTarget.setValue(requiredMe1Stripe);
				String requiredMe2Stripe = results.getMe2stripe().toString();
				cmbME2StripeTarget.setValue(requiredMe2Stripe);
				txtSlitTarget.setValue(results.getPrimarySlitGap());
				txtThetaTarget.setValue(results.getArm2Theta());
				txtPolyThetaTarget.setValue(results.getBraggAngle());
				txtDetDistTarget.setValue(results.getDetectorDistance()*1000); // convert to mm
				txtME2PitchTarget.setValue(results.getMe2Pitch());
				txtSampleHeight.setValue(results.getSampleHeight()); // convert to mm
				txtDetHeightTarget.setValue(results.getDetectorHeight()); // convert to mm

				String atn1String = results.getAtn1().toString();
				cmbAtn1Target.setValue(atn1String);
				String atn2String = results.getAtn2().toString();
				cmbAtn2Target.setValue(atn2String);
				String atn3String = results.getAtn3().toString();
				cmbAtn3Target.setValue(atn3String);

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

	private void linkButtonToScannable(Button theButton, final String scannableName, final LabelWrapper txtDetDistTarget2) {
		
		theButton.setToolTipText("Move to the calculated position");
		
		theButton.addSelectionListener(new SelectionListener() {

			Scannable theScannable = null;

			@Override
			public void widgetSelected(SelectionEvent e) {
				// get value from the scalebox
				Object target = txtDetDistTarget2.getValue();

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
	
	private RotationViewer createRotationViewer(Composite parent, String scannableName) {

		final Scannable theScannable = Finder.getInstance().find(scannableName);
		if (theScannable == null) {
			Label lbl = new Label(parent, SWT.NONE);
			lbl.setText("not connected");
			return null;
		}

		GridLayoutFactory rotationGroupLayoutFactory = GridLayoutFactory.swtDefaults().numColumns(3).margins(0, 0)
				.spacing(0, 0);
		GridLayoutFactory layoutFactory = GridLayoutFactory.swtDefaults().numColumns(3).margins(0, 0).spacing(0, 0);
		RotationViewer label = new RotationViewer(theScannable, "", false);
		label.configureStandardStep(1.0);
		label.setNudgeSizeBoxDecimalPlaces(2);
		label.createControls(parent, SWT.SINGLE, true, rotationGroupLayoutFactory.create(),
				layoutFactory.create(), null);

		return label;
	}
	
	private MotorPositionViewer createMotorPositionViewer(Composite parent, String scannableName) {

		final Scannable theScannable = Finder.getInstance().find(scannableName);
		if (theScannable == null) {
			Label lbl = new Label(parent, SWT.NONE);
			lbl.setText("not connected");
			return null;
		}
		MotorPositionViewer label = new MotorPositionViewer(parent,theScannable,null,true);
		return label;
	}

	private EnumPositionViewer createEnumPositionerViewer(Composite parent, String scannableName) {

		final EnumPositioner theScannable = Finder.getInstance().find(scannableName);
		if (theScannable == null) {
			Label lbl = new Label(parent, SWT.NONE);
			lbl.setText("not connected");
			return null;
		}
		EnumPositionViewer label = new EnumPositionViewer(parent,theScannable,"",true);
		return label;
	}
	
	@Override
	public void setFocus() {
	}
	
	private void moveTwoThetaWithPolyBragg(ValueEvent e) {
		if (btnSynchroniseThetas.getSelection()) {
			// get value from the scalebox
			Double target;
			if (e == null) {
				try {
					target = txtPolyThetaTarget.getNumericValue();
				} catch (ParseException e2) {
					logger.error("ParseException: twotheta could not be moved as the entered value "
							+ txtPolyThetaTarget.getValue() + " is not acceptable: " + e2.getMessage(), e2);
					return;
				}
				target *= 2;
			} else {
				target = e.getDoubleValue() * 2;
			}

			// get the scannable from finder
			if (twoThetaScannable == null)
				twoThetaScannable = Finder.getInstance().find("twotheta");

			// move the scannable to the value
			try {
				if (twoThetaScannable != null)
					twoThetaScannable.asynchronousMoveTo(target);
			} catch (Exception e1) {
				logger.error("Exception while moving twotheta to " + target + ": " + e1.getMessage(), e1);
			}
		}
	}

}
