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
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.ComboViewer;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.viewers.StructuredSelection;
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
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.ui.views.properties.IPropertySheetPage;
import org.eclipse.ui.views.properties.tabbed.ITabbedPropertySheetPageContributor;
import org.eclipse.ui.views.properties.tabbed.TabbedPropertySheetPage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.data.AlignmentParametersBean;
import uk.ac.gda.exafs.data.ScannableSetup.CrystalCut;
import uk.ac.gda.exafs.data.ScannableSetup.DetectorSetup;
import uk.ac.gda.exafs.data.ScannableSetup.Units;
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
public class BeamlineAlignmentView extends ViewPart implements ITabbedPropertySheetPageContributor {

	private static Logger logger = LoggerFactory.getLogger(BeamlineAlignmentView.class);

	public static final String OUTPUT_BEAN_NAME = "beamlinealignmentresults";
	public static final String INPUT_BEAN_NAME = "beamlinealignmentparameters";
	public static String ID = "uk.ac.gda.exafs.ui.views.beamlinealignmentview";
	private ComboViewer cmbCrystalCut;
	private LabelWrapper txtWigglerTarget;
	private Button btnWigglerMove;
	private LabelWrapper txtSlitTarget;
	private Button btnSlitMove;
	private LabelWrapper cmbME1StripeTarget;
	private Button btnME1StripeMove;
	private LabelWrapper txtThetaTarget;
	private Button btnThetaMove;
	private RotationViewer lblThetaReadback;
	private LabelWrapper cmbME2StripeTarget;
	private Button btnME2StripeMove;
	private LabelWrapper txtME2PitchTarget;
	private Button btnME2PitchMove;
	private LabelWrapper txtDetDistTarget;
	private Button btnDetDistMove;
	private GridData comboGD;
	private GridData textGD;
	private GridData readbackGD;
	private Combo cmbElement;
	private Combo cmdElementEdge;
	private ScaleBox scaleBoxEnergyRange;
	private Combo cmbCrystalType;
	private Combo cmbCrystalQ;
	private LabelWrapper txtPolyThetaTarget;
	private Button btnPolyThetaMove;
	private RotationViewer lblPolyThetaReadback;
	private LabelWrapper txtPolyBendTarget;
	private Button btnPolyBendMove;
	private Button btnSynchroniseThetas;
	private LabelWrapper txtPolyBendTarget2;
	private Button btnPolyBendMove2;
	private Label lblPolyPower;
	private LabelWrapper cmbAtn1Target;
	private Button btnAtn1Move;
	private LabelWrapper cmbAtn2Target;
	private Button btnAtn2Move;
	private LabelWrapper cmbAtn3Target;
	private Button btnAtn3Move;
	private Composite mainControls;
	private LabelWrapper txtSampleHeight;
	private Button btnSampleHeightMove;
	private LabelWrapper txtDetHeightTarget;
	private Button btnDetHeightMove;
	private Scannable twoThetaScannable;
	private Button btnRefresh;

	private Shell parentShell;

	private static final String moveCmdTxt = "Move";
	private static final int COMMAND_WAIT_TIME = 500;

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
		final int width = 120;
		comboGD = new GridData(SWT.FILL, SWT.CENTER, false, false);
		comboGD.widthHint = width;

		textGD = new GridData(SWT.FILL, SWT.CENTER, false, false);
		textGD.widthHint = width;

		readbackGD = new GridData(SWT.FILL, SWT.CENTER, false, false);
		readbackGD.widthHint = width;
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
		txtDetDistTarget = new LabelWrapper(motorGroup, SWT.CENTER);
		txtDetDistTarget.setLayoutData(textGD);
		txtDetDistTarget.setUnit(Units.MILLI_METER.getText());
		btnDetDistMove = new Button(motorGroup, SWT.NONE);
		btnDetDistMove.setText(moveCmdTxt);
		linkButtonToScannable(btnDetDistMove,"detector_z",txtDetDistTarget);
		createMotorPositionViewer(motorGroup,"detector_z");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Sample Height");
		lbl.setLayoutData(createLabelGridData());
		txtSampleHeight = new LabelWrapper(motorGroup, SWT.CENTER);
		txtSampleHeight.setLayoutData(textGD);
		txtSampleHeight.setUnit(Units.MILLI_METER.getText());
		btnSampleHeightMove = new Button(motorGroup, SWT.NONE);
		btnSampleHeightMove.setText(moveCmdTxt);
		createMotorPositionViewer(motorGroup,"sample_x");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Detector Height");
		lbl.setLayoutData(createLabelGridData());
		txtDetHeightTarget = new LabelWrapper(motorGroup, SWT.CENTER);
		txtDetHeightTarget.setLayoutData(textGD);
		txtDetHeightTarget.setUnit(Units.MILLI_METER.getText());
		btnDetHeightMove = new Button(motorGroup, SWT.NONE);
		btnDetHeightMove.setText(moveCmdTxt);
		linkButtonToScannable(btnDetHeightMove,"detector_y",txtDetHeightTarget);
		createMotorPositionViewer(motorGroup,"detector_y");
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
		txtWigglerTarget = new LabelWrapper(motorGroup, SWT.CENTER);
		txtWigglerTarget.setLayoutData(textGD);
		txtWigglerTarget.setUnit(Units.MILLI_METER.getText());
		btnWigglerMove = new Button(motorGroup, SWT.NONE);

		btnWigglerMove.setText(moveCmdTxt);
		linkButtonToScannable(btnWigglerMove, "wigglerGap", txtWigglerTarget);
		createMotorPositionViewer(motorGroup,"wigglerGap");


		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Primary Slit HGap");
		lbl.setLayoutData(createLabelGridData());
		txtSlitTarget = new LabelWrapper(motorGroup, SWT.CENTER);
		txtSlitTarget.setLayoutData(textGD);
		txtSlitTarget.setUnit(Units.MILLI_RADIAN.getText());
		btnSlitMove = new Button(motorGroup, SWT.NONE);
		btnSlitMove.setText(moveCmdTxt);
		linkButtonToScannable(btnSlitMove, "s1_hgap", txtSlitTarget);
		createMotorPositionViewer(motorGroup,"s1_hgap");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Attenuator 1");
		lbl.setLayoutData(createLabelGridData());
		cmbAtn1Target = new LabelWrapper(motorGroup, SWT.CENTER);
		cmbAtn1Target.setLayoutData(comboGD);
		cmbAtn1Target.setTextType(TEXT_TYPE.PLAIN_TEXT);
		btnAtn1Move = new Button(motorGroup, SWT.NONE);
		btnAtn1Move.setText(moveCmdTxt);
		linkButtonToScannable(btnAtn1Move, "atn1", cmbAtn1Target);
		createEnumPositionerViewer(motorGroup,"atn1");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Attenuator 2");
		lbl.setLayoutData(createLabelGridData());
		cmbAtn2Target = new LabelWrapper(motorGroup, SWT.CENTER);
		cmbAtn2Target.setLayoutData(comboGD);
		cmbAtn2Target.setTextType(TEXT_TYPE.PLAIN_TEXT);
		btnAtn2Move = new Button(motorGroup, SWT.NONE);
		btnAtn2Move.setText(moveCmdTxt);
		linkButtonToScannable(btnAtn2Move, "atn2", cmbAtn2Target);
		createEnumPositionerViewer(motorGroup,"atn2");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Attenuator 3");
		lbl.setLayoutData(createLabelGridData());
		cmbAtn3Target = new LabelWrapper(motorGroup, SWT.CENTER);
		cmbAtn3Target.setLayoutData(comboGD);
		cmbAtn3Target.setTextType(TEXT_TYPE.PLAIN_TEXT);
		btnAtn3Move = new Button(motorGroup, SWT.NONE);
		btnAtn3Move.setText(moveCmdTxt);
		linkButtonToScannable(btnAtn3Move, "atn3", cmbAtn3Target);
		createEnumPositionerViewer(motorGroup,"atn3");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("ME1 Stripe");
		lbl.setLayoutData(createLabelGridData());
		cmbME1StripeTarget = new LabelWrapper(motorGroup, SWT.CENTER);
		cmbME1StripeTarget.setLayoutData(comboGD);
		cmbME1StripeTarget.setTextType(TEXT_TYPE.PLAIN_TEXT);
		btnME1StripeMove = new Button(motorGroup, SWT.NONE);
		btnME1StripeMove.setText(moveCmdTxt);
		linkButtonToScannable(btnAtn1Move, "me1_stripe", cmbME1StripeTarget);
		createEnumPositionerViewer(motorGroup,"me1_stripe");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("ME2 Stripe");
		lbl.setLayoutData(createLabelGridData());
		cmbME2StripeTarget = new LabelWrapper(motorGroup, SWT.CENTER);
		cmbME2StripeTarget.setLayoutData(comboGD);
		cmbME2StripeTarget.setTextType(TEXT_TYPE.PLAIN_TEXT);
		btnME2StripeMove = new Button(motorGroup, SWT.NONE);
		btnME2StripeMove.setText(moveCmdTxt);
		linkButtonToScannable(btnME2StripeMove, "me2_stripe", cmbME2StripeTarget);
		createEnumPositionerViewer(motorGroup,"me2_stripe");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("ME2 Pitch");
		lbl.setLayoutData(createLabelGridData());
		txtME2PitchTarget = new LabelWrapper(motorGroup, SWT.CENTER);
		txtME2PitchTarget.setLayoutData(textGD);
		txtME2PitchTarget.setUnit(Units.MILLI_RADIAN.getText());
		btnME2PitchMove = new Button(motorGroup, SWT.NONE);
		btnME2PitchMove.setText(moveCmdTxt);
		linkButtonToScannable(btnME2PitchMove, "me2pitch", txtME2PitchTarget);
		createMotorPositionViewer(motorGroup,"me2pitch");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Poly Bend1");
		lbl.setLayoutData(createLabelGridData());
		txtPolyBendTarget = new LabelWrapper(motorGroup, SWT.CENTER);
		txtPolyBendTarget.setLayoutData(textGD);
		txtPolyBendTarget.setUnit(Units.MILLI_METER.getText());
		btnPolyBendMove = new Button(motorGroup, SWT.NONE);
		btnPolyBendMove.setText(moveCmdTxt);
		linkButtonToScannable(btnPolyBendMove, "polybend1", txtPolyBendTarget);
		createRotationViewer(motorGroup,"polybend1");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Poly Bend2");
		lbl.setLayoutData(createLabelGridData());
		txtPolyBendTarget2 = new LabelWrapper(motorGroup, SWT.CENTER);
		txtPolyBendTarget2.setLayoutData(textGD);
		txtPolyBendTarget2.setUnit(Units.MILLI_METER.getText());
		btnPolyBendMove2 = new Button(motorGroup, SWT.NONE);
		btnPolyBendMove2.setText(moveCmdTxt);
		linkButtonToScannable(btnPolyBendMove2, "polybend2", txtPolyBendTarget2);
		createRotationViewer(motorGroup,"polybend2");

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Poly Bragg");
		lbl.setLayoutData(createLabelGridData());
		txtPolyThetaTarget = new LabelWrapper(motorGroup, SWT.CENTER);
		txtPolyThetaTarget.setLayoutData(textGD);
		txtPolyThetaTarget.setUnit(Units.DEGREE.getText());
		btnPolyThetaMove = new Button(motorGroup, SWT.NONE);
		btnPolyThetaMove.setText(moveCmdTxt);
		linkButtonToScannable(btnPolyThetaMove, "polytheta", txtPolyThetaTarget);
		btnPolyThetaMove.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				moveTwoThetaWithPolyBragg(null);
			}
		});
		lblPolyThetaReadback = createRotationViewer(motorGroup,"polytheta");
		lblPolyThetaReadback.addValueListener(new ValueAdapter("polytheta") {

			@Override
			public void valueChangePerformed(ValueEvent e) {
				moveTwoThetaWithPolyBragg(e);
			}
		});

		lbl = new Label(motorGroup, SWT.NONE);
		lbl.setText("Two Theta");
		lbl.setLayoutData(createLabelGridData());
		txtThetaTarget = new LabelWrapper(motorGroup, SWT.CENTER);
		txtThetaTarget.setLayoutData(textGD);
		txtThetaTarget.setUnit(Units.DEGREE.getText());
		btnThetaMove = new Button(motorGroup, SWT.NONE);
		btnThetaMove.setText(moveCmdTxt);
		linkButtonToScannable(btnThetaMove, "twotheta", txtThetaTarget);
		lblThetaReadback = createRotationViewer(motorGroup,"twotheta");

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

		Group grpPowerEst = new Group(motorGroup, SWT.NONE);
		GridDataFactory.swtDefaults().span(2, 2).applyTo(grpPowerEst);
		GridLayout subPanelLayout = new GridLayout();
		subPanelLayout.numColumns = 2;
		grpPowerEst.setLayout(subPanelLayout);

		lbl = new Label(grpPowerEst, SWT.NONE);
		lbl.setText("Estimated power\n on polychromator");
		lbl.setLayoutData(createLabelGridData());

		lblPolyPower = new Label(grpPowerEst, SWT.NONE);

		// TODO Why Hard coded 180 here, should this live in data model?
		lblPolyPower.setText(Units.WATT.addUnitSuffix("180"));
		lblPolyPower.setForeground(PlatformUI.getWorkbench().getDisplay().getSystemColor(SWT.COLOR_RED));

		grpPowerEst.pack(); // pack first

	}

	private void createMainControls(Composite parent) {
		parentShell = parent.getShell();
		mainControls = new Composite(parent, SWT.NONE);
		GridDataFactory.fillDefaults().align(SWT.CENTER, SWT.FILL).applyTo(mainControls);
		GridLayoutFactory.swtDefaults().numColumns(2).applyTo(mainControls);

		Label lbl = new Label(mainControls, SWT.NONE);
		lbl.setText("Element");
		lbl.setLayoutData(createLabelGridData());
		cmbElement = new Combo(mainControls, SWT.READ_ONLY);
		cmbElement.setLayoutData(comboGD);
		cmbElement.setItems(Element.getSortedEdgeSymbols("P", "U"));
		cmbElement.select(0);

		cmbElement.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				updateElementEdgeSelection();
			}
		});

		lbl = new Label(mainControls, SWT.NONE);
		lbl.setText("Edge");
		lbl.setLayoutData(createLabelGridData());
		cmdElementEdge = new Combo(mainControls, SWT.READ_ONLY);
		cmdElementEdge.setLayoutData(comboGD);
		cmdElementEdge.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent event) {
				updateEngeryValue();
			}
		});

		lbl = new Label(mainControls, SWT.NONE);
		lbl.setText("Edge energy");
		lbl.setLayoutData(createLabelGridData());
		scaleBoxEnergyRange = new ScaleBox(mainControls, SWT.NONE);
		scaleBoxEnergyRange.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		scaleBoxEnergyRange.setUnit(Units.EV.getText());
		scaleBoxEnergyRange.setNotifyType(NOTIFY_TYPE.VALUE_CHANGED);
		scaleBoxEnergyRange.on();

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
				updateElementEdgeSelection();
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				widgetSelected(e);
			}
		});

		lbl = new Label(mainControls, SWT.NONE);
		lbl.setText("Crystal Cut");
		lbl.setLayoutData(createLabelGridData());
		cmbCrystalCut = new ComboViewer(mainControls, SWT.READ_ONLY);
		cmbCrystalCut.setContentProvider(ArrayContentProvider.getInstance());
		cmbCrystalCut.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object element) {
				return ((CrystalCut) element).name();
			}
		});
		cmbCrystalCut.setInput(CrystalCut.values());
		cmbCrystalCut.setSelection(new StructuredSelection(CrystalCut.Si111));
		cmbCrystalCut.addSelectionChangedListener(new ISelectionChangedListener() {
			@Override
			public void selectionChanged(SelectionChangedEvent event) {
				updateElementEdgeSelection();
			}
		});

		lbl = new Label(mainControls, SWT.NONE);
		lbl.setText("q");
		lbl.setLayoutData(createLabelGridData());
		cmbCrystalQ = new Combo(mainControls, SWT.NONE);
		cmbCrystalQ.setItems(new String[] { AlignmentParametersBean.Q[0].toString(),
				AlignmentParametersBean.Q[1].toString(), AlignmentParametersBean.Q[2].toString() });
		cmbCrystalQ.select(1);

		btnRefresh = new Button(mainControls, SWT.NONE);
		GridDataFactory.fillDefaults().span(2, 1).applyTo(btnRefresh);
		btnRefresh.setText("Refresh Calculations");
		btnRefresh.addSelectionListener(refreshSelectionListener);

		updateElementEdgeSelection();
	}

	private void updateEngeryValue() {
		// TODO Do proper JFace data validation
		final int invalid = -1;
		if (cmdElementEdge.getSelectionIndex() == invalid) {
			scaleBoxEnergyRange.setEnabled(false);
			scaleBoxEnergyRange.setValue(invalid);
			btnRefresh.setEnabled(false);
		} else {
			scaleBoxEnergyRange.setEnabled(true);
			String selectedElementString = cmbElement.getItem(cmbElement.getSelectionIndex());
			Element selectedElement = Element.getElement(selectedElementString);
			String selectedEdgeString = cmdElementEdge.getItem(cmdElementEdge.getSelectionIndex());
			final double edgeEn = selectedElement.getEdgeEnergy(selectedEdgeString);
			StructuredSelection cryCutSelection = ((StructuredSelection) cmbCrystalCut.getSelection());
			CrystalCut selectedCrystalCut = (CrystalCut) cryCutSelection.getFirstElement();
			scaleBoxEnergyRange.setMaximum(selectedCrystalCut.getMax());
			scaleBoxEnergyRange.setMinimum(selectedCrystalCut.getMin());
			scaleBoxEnergyRange.setValue(edgeEn);
			btnRefresh.setEnabled(true);
		}
	}

	private final SelectionListener refreshSelectionListener = new SelectionListener() {
		@Override
		public void widgetSelected(SelectionEvent selectionEvent) {
			String selectedElementString = cmbElement.getItem(cmbElement.getSelectionIndex());
			Element selectedElement = Element.getElement(selectedElementString);
			String selectedEdgeString = cmdElementEdge.getItem(cmdElementEdge.getSelectionIndex());
			AbsorptionEdge absEdge = selectedElement.getEdge(selectedEdgeString);

			String qString = cmbCrystalQ.getItem(cmbCrystalQ.getSelectionIndex());
			Double q = Double.parseDouble(qString);

			String xtalCutString = ((CrystalCut) ((StructuredSelection) cmbCrystalCut.getSelection()).getFirstElement()).name();
			String xtalTypeString = cmbCrystalType.getItem(cmbCrystalType.getSelectionIndex());
			String detectorString = DetectorSetup.getActiveDetectorSetup().getDetectorName();

			try {
				AlignmentParametersBean bean = new AlignmentParametersBean(xtalTypeString, xtalCutString, q,
						detectorString, absEdge);

				InterfaceProvider.getJythonNamespace().placeInJythonNamespace(INPUT_BEAN_NAME, bean);

				InterfaceProvider.getCommandRunner().runCommand(
						OUTPUT_BEAN_NAME + "=None;from alignment import alignment_parameters; " + OUTPUT_BEAN_NAME
						+ " = alignment_parameters.calc_parameters(" + INPUT_BEAN_NAME + ")");
				// give the command a chance to run.
				Thread.sleep(COMMAND_WAIT_TIME);
				Object result = InterfaceProvider.getJythonNamespace()
						.getFromJythonNamespace(OUTPUT_BEAN_NAME);
				if (result != null && (result instanceof AlignmentParametersBean)) {
					updateUIFromBean((AlignmentParametersBean) result);
				} else {
					MessageDialog.openError(parentShell, "Error", "Unable to calculate suggested values");
				}
			} catch (Exception e1) {
				logger.error("Exception when trying to run the script which performs the alignment calculations.",e1);
			}
		}

		@Override
		public void widgetDefaultSelected(SelectionEvent e) {
			widgetSelected(e);
		}
	};

	private void updateElementEdgeSelection() {
		String selectedElementString = cmbElement.getItem(cmbElement.getSelectionIndex());
		Element selectedElement = Element.getElement(selectedElementString);
		StructuredSelection cryCutSelection = ((StructuredSelection) cmbCrystalCut.getSelection());
		CrystalCut selectedCrystalCut = (CrystalCut) cryCutSelection.getFirstElement();
		final Iterator<String> edges;
		edges = selectedElement.getEdgesInEnergyRange(selectedCrystalCut.getMin(), selectedCrystalCut.getMax());

		if (edges == null) {
			cmdElementEdge.setItems(new String[] {});
			cmdElementEdge.deselectAll();
		} else {
			String[] edgesArray = new String[] {};
			for (; edges.hasNext();) {
				String edge = edges.next();
				edgesArray = (String[]) ArrayUtils.add(edgesArray, edge);
			}
			cmdElementEdge.setItems(edgesArray);
			cmdElementEdge.select(0);
		}
		cmdElementEdge.notifyListeners(SWT.Selection, new Event());
		mainControls.redraw();
		mainControls.pack(true);
	}

	protected void updateUIFromBean(final AlignmentParametersBean results) {

		PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
			// TODO Should not define here
			private static final int MAX_POWER_IN_WATT = 350;

			@Override
			public void run() {
				// TODO Should use data binding this is not needed
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

				String powerString = String.format("%.1d %s", results.getPower(), Units.WATT.getText());
				lblPolyPower.setText(powerString);
				// TODO Use JFace data binding to show validation
				if (results.getPower() > MAX_POWER_IN_WATT) {
					lblPolyPower.setForeground(PlatformUI.getWorkbench().getDisplay().getSystemColor(SWT.COLOR_RED));
				} else {
					lblPolyPower.setForeground(PlatformUI.getWorkbench().getDisplay().getSystemColor(SWT.COLOR_BLACK));
				}
			}

		});
	}

	private void linkButtonToScannable(Button theButton, final String scannableName, final LabelWrapper txtScannableValue) {

		theButton.setToolTipText("Move to the calculated position");

		theButton.addSelectionListener(new SelectionListener() {

			Scannable theScannable = null;

			@Override
			public void widgetSelected(SelectionEvent event) {
				// get value from the scalebox
				Object target = txtScannableValue.getValue();

				// get the scannable from finder
				if (theScannable == null) {
					theScannable = Finder.getInstance().find(scannableName);
				}

				// move the scannable to the value
				try {
					if (theScannable != null) {
						theScannable.asynchronousMoveTo(target);
					}
				} catch (Exception e) {
					String errorMessage = "Exception while moving " + scannableName + " to " + target + ": " + e.getMessage();
					logger.error(errorMessage, e);
					MessageDialog.openError(parentShell, "Error", errorMessage);
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
			if (twoThetaScannable == null) {
				twoThetaScannable = Finder.getInstance().find("twotheta");
			}

			// move the scannable to the value
			try {
				if (twoThetaScannable != null) {
					twoThetaScannable.asynchronousMoveTo(target);
				}
			} catch (Exception e1) {
				logger.error("Exception while moving twotheta to " + target + ": " + e1.getMessage(), e1);
			}
		}
	}

	@Override
	public String getContributorId() {
		return this.getSite().getId();
	}

	@Override
	public Object getAdapter(@SuppressWarnings("rawtypes") Class adapter) {
		if (adapter == IPropertySheetPage.class) {
			System.out.println("PRoperty sheet");
			return new TabbedPropertySheetPage(this);
		}
		return super.getAdapter(adapter);
	}
}
