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

import gda.jython.InterfaceProvider;
import gda.util.exafs.AbsorptionEdge;
import gda.util.exafs.Element;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.apache.commons.lang.ArrayUtils;
import org.eclipse.jface.dialogs.IMessageProvider;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.ComboViewer;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.forms.events.HyperlinkAdapter;
import org.eclipse.ui.forms.events.HyperlinkEvent;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Hyperlink;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.forms.widgets.TableWrapData;
import org.eclipse.ui.forms.widgets.TableWrapLayout;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.ui.views.properties.IPropertySheetPage;
import org.eclipse.ui.views.properties.tabbed.ITabbedPropertySheetPageContributor;
import org.eclipse.ui.views.properties.tabbed.TabbedPropertySheetPage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.data.AlignmentParametersBean;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.CrystalCut;
import uk.ac.gda.exafs.data.ClientConfig.CrystalType;
import uk.ac.gda.exafs.data.ClientConfig.DetectorSetup;
import uk.ac.gda.exafs.data.ClientConfig.ScannableSetup;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.UIHelper.UIMotorControl;
import uk.ac.gda.richbeans.components.FieldComposite.NOTIFY_TYPE;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;
import uk.ac.gda.richbeans.event.ValueEvent;
import uk.ac.gda.richbeans.event.ValueListener;
import uk.ac.gda.ui.viewer.MotorPositionViewer;

/**
 * Has controls for operating the lookuptable matching optics positions to energy
 */
public class BeamlineAlignmentView extends ViewPart implements ITabbedPropertySheetPageContributor {

	private static final int LABEL_WIDTH = 155;
	private static final int SUGGESTION_LABEL_WIDTH = 100;
	private static final int COMMAND_WAIT_TIME_IN_MILLI_SEC = 100;

	public static String ID = "uk.ac.gda.exafs.ui.views.beamlinealignmentview";

	private static Logger logger = LoggerFactory.getLogger(BeamlineAlignmentView.class);

	public static final String OUTPUT_BEAN_NAME = "beamlinealignmentresults";
	public static final String INPUT_BEAN_NAME = "beamlinealignmentparameters";

	private ComboViewer cmbCrystalCut;
	private ComboViewer cmbCrystalType;
	private GridData comboGD;
	private Combo cmbElement;
	private Combo cmdElementEdge;
	private ScaleBox scaleBoxEnergyRange;
	private Combo cmbCrystalQ;

	private FormToolkit toolkit;
	private ScrolledForm scrolledPolyForm;
	private Hyperlink lblWigglerSuggestion;
	private Hyperlink lblSlitGapSuggestion;
	private Hyperlink lblAtn1Suggestion;
	private Hyperlink lblAtn2Suggestion;
	private Hyperlink lblAtn3Suggestion;
	private Hyperlink lblMe1StripSuggestion;
	private Hyperlink lblMe2StripSuggestion;
	private Hyperlink lblMe2PitchAngleSuggestion;
	private Hyperlink lblPolyBender1Suggestion;
	private Hyperlink lblPolyBender2Suggestion;
	private Hyperlink lblPolyBraggSuggestion;
	private Hyperlink lblArm2ThetaAngleSuggestion;
	private Hyperlink lblDetectorHeightSuggestion;
	private Hyperlink lblDetectorDistanceSuggestion;

	@Override
	public void createPartControl(final Composite parent) {

		toolkit = new FormToolkit(parent.getDisplay());
		scrolledPolyForm = toolkit.createScrolledForm(parent);
		TableWrapLayout layout = new TableWrapLayout();
		scrolledPolyForm.getBody().setLayout(layout);
		toolkit.decorateFormHeading(scrolledPolyForm.getForm());
		scrolledPolyForm.setText("Configuration");

		createMainControls(scrolledPolyForm.getForm());
		createMotorControls(scrolledPolyForm.getForm());
		createSpectrumControls(scrolledPolyForm.getForm());

		updateElementEdgeSelection();
	}

	private void createMainControls(Form form) {
		@SuppressWarnings("static-access")
		final Section mainSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		mainSection.setText("Main Parameters");

		mainSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite mainSelectionComposite = toolkit.createComposite(mainSection, SWT.NONE);
		toolkit.paintBordersFor(mainSelectionComposite);
		mainSelectionComposite.setLayout(new GridLayout(2, false));
		mainSection.setClient(mainSelectionComposite);

		Label lblCrystalType = toolkit.createLabel(mainSelectionComposite, CrystalType.UI_LABEL, SWT.NONE);
		lblCrystalType.setLayoutData(createLabelGridData());
		cmbCrystalType = new ComboViewer(mainSelectionComposite, SWT.READ_ONLY);
		cmbCrystalType.setContentProvider(ArrayContentProvider.getInstance());
		cmbCrystalType.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object element) {
				return ((CrystalType) element).name();
			}
		});
		cmbCrystalType.setInput(new CrystalType[]{CrystalType.Bragg});
		cmbCrystalType.setSelection(new StructuredSelection(CrystalType.Bragg));
		cmbCrystalType.getCombo().setLayoutData(new GridData(GridData.FILL_HORIZONTAL));


		Label lblCrystalCut = toolkit.createLabel(mainSelectionComposite, CrystalCut.UI_LABEL, SWT.NONE);
		lblCrystalCut.setLayoutData(createLabelGridData());
		cmbCrystalCut = new ComboViewer(mainSelectionComposite, SWT.READ_ONLY);
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
		cmbCrystalCut.getCombo().setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		Label lblCrystalQ = toolkit.createLabel(mainSelectionComposite, "Crystal q:", SWT.NONE);
		lblCrystalQ.setLayoutData(createLabelGridData());
		cmbCrystalQ = new Combo(mainSelectionComposite, SWT.READ_ONLY);
		cmbCrystalQ.setItems(new String[] { AlignmentParametersBean.Q[0].toString(),
				AlignmentParametersBean.Q[1].toString(), AlignmentParametersBean.Q[2].toString() });
		cmbCrystalQ.select(1);
		cmbCrystalQ.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		Label lbl = toolkit.createLabel(mainSelectionComposite, "Element:", SWT.NONE);
		lbl.setLayoutData(createLabelGridData());
		cmbElement = new Combo(mainSelectionComposite, SWT.READ_ONLY);
		cmbElement.setLayoutData(comboGD);
		cmbElement.setItems(Element.getSortedEdgeSymbols("P", "U"));
		cmbElement.select(0);

		cmbElement.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				updateElementEdgeSelection();
			}
		});
		cmbElement.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		lbl = toolkit.createLabel(mainSelectionComposite, "Edge:", SWT.NONE);
		lbl.setLayoutData(createLabelGridData());
		cmdElementEdge = new Combo(mainSelectionComposite, SWT.READ_ONLY);
		cmdElementEdge.setLayoutData(comboGD);
		cmdElementEdge.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		cmdElementEdge.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent event) {
				updateEngeryValue();
			}
		});

		lbl = toolkit.createLabel(mainSelectionComposite, "Edge energy:", SWT.NONE);
		lbl.setLayoutData(createLabelGridData());
		scaleBoxEnergyRange = new ScaleBox(mainSelectionComposite, SWT.NONE);
		scaleBoxEnergyRange.setUnit(UnitSetup.EV.getText());
		scaleBoxEnergyRange.setEditable(false);
		scaleBoxEnergyRange.setNotifyType(NOTIFY_TYPE.VALUE_CHANGED);
		scaleBoxEnergyRange.on();
		scaleBoxEnergyRange.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(mainSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		mainSection.setSeparatorControl(defaultSectionSeparator);
	}

	private void getScannableValuesSuggestion() {
		String selectedElementString = cmbElement.getItem(cmbElement.getSelectionIndex());
		Element selectedElement = Element.getElement(selectedElementString);
		String selectedEdgeString = cmdElementEdge.getItem(cmdElementEdge.getSelectionIndex());
		AbsorptionEdge absEdge = selectedElement.getEdge(selectedEdgeString);

		String qString = cmbCrystalQ.getItem(cmbCrystalQ.getSelectionIndex());
		Double q = Double.parseDouble(qString);

		String xtalCutString = ((CrystalCut) ((StructuredSelection) cmbCrystalCut.getSelection()).getFirstElement()).name();
		String xtalTypeString = ((CrystalType) ((StructuredSelection) cmbCrystalType.getSelection()).getFirstElement()).name();
		String detectorString = DetectorSetup.getActiveDetectorSetup().getDetectorName();

		try {
			AlignmentParametersBean bean = new AlignmentParametersBean(xtalTypeString, xtalCutString, q,
					detectorString, absEdge);

			InterfaceProvider.getJythonNamespace().placeInJythonNamespace(INPUT_BEAN_NAME, bean);

			InterfaceProvider.getCommandRunner().runCommand(
					OUTPUT_BEAN_NAME + "=None;from alignment import alignment_parameters; " + OUTPUT_BEAN_NAME
					+ " = alignment_parameters.calc_parameters(" + INPUT_BEAN_NAME + ")");
			// give the command a chance to run.
			Thread.sleep(COMMAND_WAIT_TIME_IN_MILLI_SEC);
			Object result = InterfaceProvider.getJythonNamespace()
					.getFromJythonNamespace(OUTPUT_BEAN_NAME);
			if (result != null && (result instanceof AlignmentParametersBean)) {
				showSuggestionValues((AlignmentParametersBean) result);
			} else {
				UIHelper.showError("Error", "Unable to calculate suggested values");
			}
		} catch (Exception e1) {
			logger.error("Exception when trying to run the script which performs the alignment calculations.",e1);
		}
	}

	private GridData createLabelGridData() {
		GridData gridData = new GridData(GridData.BEGINNING, GridData.CENTER, false, false);
		gridData.widthHint = LABEL_WIDTH;
		return gridData;
	}

	private void createMotorControls(Form form) {
		@SuppressWarnings("static-access")
		final Section motorSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		motorSection.setText("Motor Positions");
		motorSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite motorSelectionComposite = toolkit.createComposite(motorSection, SWT.NONE);
		toolkit.paintBordersFor(motorSelectionComposite);
		motorSelectionComposite.setLayout(new GridLayout(3, false));
		motorSection.setClient(motorSelectionComposite);

		lblWigglerSuggestion = createMotorControl(motorSelectionComposite, ScannableSetup.WIGGLER_GAP, UIMotorControl.POSITION);
		lblWigglerSuggestion.addHyperlinkListener(new SuggestionLinkAdapter(ScannableSetup.WIGGLER_GAP));
		lblSlitGapSuggestion = createMotorControl(motorSelectionComposite, ScannableSetup.SLIT_1_HORIZONAL_GAP, UIMotorControl.POSITION);
		lblSlitGapSuggestion.addHyperlinkListener(new SuggestionLinkAdapter( ScannableSetup.SLIT_1_HORIZONAL_GAP));
		lblAtn1Suggestion = createMotorControl(motorSelectionComposite, ScannableSetup.ATN1, UIMotorControl.ENUM);
		lblAtn1Suggestion.addHyperlinkListener(new SuggestionLinkAdapter(ScannableSetup.ATN1));
		lblAtn2Suggestion = createMotorControl(motorSelectionComposite, ScannableSetup.ATN2, UIMotorControl.ENUM);
		lblAtn2Suggestion.addHyperlinkListener(new SuggestionLinkAdapter(ScannableSetup.ATN2));
		lblAtn3Suggestion = createMotorControl(motorSelectionComposite, ScannableSetup.ATN3, UIMotorControl.ENUM);
		lblAtn3Suggestion.addHyperlinkListener(new SuggestionLinkAdapter(ScannableSetup.ATN3));
		lblMe1StripSuggestion = createMotorControl(motorSelectionComposite, ScannableSetup.ME1_STRIPE, UIMotorControl.ENUM);
		lblMe1StripSuggestion.addHyperlinkListener(new SuggestionLinkAdapter(ScannableSetup.ME1_STRIPE));
		lblMe2StripSuggestion = createMotorControl(motorSelectionComposite, ScannableSetup.ME2_STRIPE, UIMotorControl.ENUM);
		lblMe2StripSuggestion.addHyperlinkListener(new SuggestionLinkAdapter(ScannableSetup.ME2_STRIPE));
		lblMe2PitchAngleSuggestion = createMotorControl(motorSelectionComposite, ScannableSetup.ME2_PITCH_ANGLE, UIMotorControl.POSITION);
		lblMe2PitchAngleSuggestion.addHyperlinkListener(new SuggestionLinkAdapter(ScannableSetup.ME2_PITCH_ANGLE));
		lblPolyBender1Suggestion = createMotorControl(motorSelectionComposite, ScannableSetup.POLY_BENDER_1, UIMotorControl.POSITION);
		lblPolyBender1Suggestion.addHyperlinkListener(new SuggestionLinkAdapter(ScannableSetup.POLY_BENDER_1));
		lblPolyBender2Suggestion = createMotorControl(motorSelectionComposite, ScannableSetup.POLY_BENDER_2, UIMotorControl.POSITION);
		lblPolyBender2Suggestion.addHyperlinkListener(new SuggestionLinkAdapter(ScannableSetup.POLY_BENDER_2));

		final Button btnSynchroniseThetas = toolkit.createButton(motorSelectionComposite, "Match TwoTheta arm to Poly Bragg value", SWT.CHECK | SWT.WRAP);
		GridData gridData = new GridData(GridData.FILL_HORIZONTAL);
		gridData.horizontalSpan = 3;
		btnSynchroniseThetas.setLayoutData(gridData);
		btnSynchroniseThetas.setSelection(true);
		lblPolyBraggSuggestion = createMotorControl(motorSelectionComposite, ScannableSetup.POLY_BRAGG, UIMotorControl.POSITION);
		lblPolyBraggSuggestion.addHyperlinkListener(new BraggSuggestionLinkAdapter(btnSynchroniseThetas));
		((MotorPositionViewer) ScannableSetup.POLY_BRAGG.getUiViewer()).addValueListener(new ValueListener() {
			@Override
			public void valueChangePerformed(ValueEvent event) {
				if (btnSynchroniseThetas.getSelection()) {
					if (event != null) {
						double thetaAngle = event.getDoubleValue() * 2;
						try {
							ScannableSetup.ARM_2_THETA_ANGLE.getScannable().asynchronousMoveTo(thetaAngle);
						} catch (Exception e) {
							String errorMessage = "Error while applying " + ScannableSetup.ARM_2_THETA_ANGLE.getLabel() + " to " + thetaAngle;
							logger.error(errorMessage, e);
							UIHelper.showError(errorMessage, e.getMessage());
						}
					}
				}
			}

			@Override
			public String getValueListenerName() {
				return null;
			}
		});

		lblArm2ThetaAngleSuggestion = createMotorControl(motorSelectionComposite, ScannableSetup.ARM_2_THETA_ANGLE, UIMotorControl.POSITION);
		lblArm2ThetaAngleSuggestion.addHyperlinkListener(new SuggestionLinkAdapter(ScannableSetup.ARM_2_THETA_ANGLE));
		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(motorSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		motorSection.setSeparatorControl(defaultSectionSeparator);
	}

	private boolean powerWarningDialogShown = false;

	private void reportPowerEst(Double powerValue) {
		if (powerValue > ScannableSetup.MAX_POWER_IN_WATT) {
			if (!powerWarningDialogShown) {
				UIHelper.showWarning("Power is above the maximum expected for operation", "Estimated power is " + powerValue);
			}
			scrolledPolyForm.getForm().setMessage(UnitSetup.WATT.addUnitSuffix("WARNING: Estimated power is " + powerValue), IMessageProvider.ERROR);
			powerWarningDialogShown = true;
		} else {
			scrolledPolyForm.getForm().setMessage("");
			powerWarningDialogShown = false;
		}
	}

	private final List<Hyperlink> suggestionControls = new ArrayList<Hyperlink>();

	private Hyperlink createMotorControl(Composite parent, ScannableSetup scannableSetup, UIMotorControl uiMotorControl) {
		Label lbl = toolkit.createLabel(parent, scannableSetup.getLabelForUI(), SWT.NONE);
		lbl.setLayoutData(createLabelGridData());
		Hyperlink lblSuggestion = toolkit.createHyperlink(parent, SUGGESTION_UNAVAILABLE_TEXT, SWT.NONE);
		setSuggestionLabelLayout(lblSuggestion);
		UIHelper.createMotorViewer(toolkit, parent, scannableSetup, uiMotorControl);
		suggestionControls.add(lblSuggestion);
		return lblSuggestion;
	}

	private static class BraggSuggestionLinkAdapter extends SuggestionLinkAdapter {
		private final Button bindBraggToArm2Theta;

		public BraggSuggestionLinkAdapter(Button bindBraggToArm2Theta) {
			super(ScannableSetup.POLY_BRAGG);
			this.bindBraggToArm2Theta = bindBraggToArm2Theta;
		}

		@Override
		public void linkActivated(HyperlinkEvent event) {
			boolean applyChanges = MessageDialog.openConfirm(Display.getDefault().getActiveShell(), "Apply changes?", getDialogMessage(event.getLabel()));
			if (applyChanges) {
				try {
					ScannableSetup.POLY_BRAGG.getScannable().asynchronousMoveTo(event.getLabel());
					if (bindBraggToArm2Theta.getSelection()) {
						ScannableSetup.ARM_2_THETA_ANGLE.getScannable().asynchronousMoveTo(Double.parseDouble(event.getLabel()) * 2.0);
					}
				} catch (Exception e) {
					String errorMessage = "Exception while applying changes";
					logger.error(errorMessage, e);
					UIHelper.showError(errorMessage, e.getMessage());
				}
			}
		}
	}

	private static class SuggestionLinkAdapter extends HyperlinkAdapter {
		private final ScannableSetup scannableSetup;

		public SuggestionLinkAdapter(ScannableSetup scannableSetup) {
			this.scannableSetup = scannableSetup;
		}

		@Override
		public void linkActivated(HyperlinkEvent event) {
			boolean applyChanges = MessageDialog.openConfirm(Display.getDefault().getActiveShell(), "Apply changes?", getDialogMessage(event.getLabel()));
			if (applyChanges) {
				try {
					scannableSetup.getScannable().asynchronousMoveTo(event.getLabel());
				} catch (Exception e) {
					String errorMessage = "Exception while applying " + scannableSetup.getLabel() + " to " + event.getLabel();
					logger.error(errorMessage, e);
					UIHelper.showError(errorMessage, e.getMessage());
				}
			}
		}

		protected String getDialogMessage(String value) {
			return "Do you want to move " + scannableSetup.getLabel() + " with suggested position: " + scannableSetup.getUnit().addUnitSuffix(value) + "?";
		}
	}

	private void setSuggestionLabelLayout(Hyperlink lblWigglerSuggestion) {
		GridData gridData = new GridData();
		gridData.widthHint = SUGGESTION_LABEL_WIDTH;
		lblWigglerSuggestion.setLayoutData(gridData);
	}

	private void updateEngeryValue() {
		// TODO Do proper JFace data validation
		final int invalid = -1;
		if (cmdElementEdge.getSelectionIndex() == invalid) {
			scaleBoxEnergyRange.setValue("");
			clearSuggestionValues();
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
			getScannableValuesSuggestion();
		}
		scaleBoxEnergyRange.setEditable(false);
	}

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
	}

	private void createSpectrumControls(Form form) {
		@SuppressWarnings("static-access")
		final Section spectrumSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		spectrumSection.setText("Spectrum Bandwidth");
		spectrumSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite spectrumSelectionComposite = toolkit.createComposite(spectrumSection, SWT.NONE);
		toolkit.paintBordersFor(spectrumSelectionComposite);
		spectrumSelectionComposite.setLayout(new GridLayout(3, false));
		spectrumSection.setClient(spectrumSelectionComposite);

		lblDetectorHeightSuggestion = createMotorControl(spectrumSelectionComposite, ScannableSetup.DETECTOR_HEIGHT, UIMotorControl.POSITION);
		lblDetectorDistanceSuggestion = createMotorControl(spectrumSelectionComposite, ScannableSetup.DETECTOR_DISTANCE, UIMotorControl.POSITION);

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(spectrumSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		spectrumSection.setSeparatorControl(defaultSectionSeparator);
	}

	private static final String SUGGESTION_UNAVAILABLE_TEXT = "-";

	// TODO Use data binding
	private void clearSuggestionValues() {
		for (Hyperlink link : suggestionControls) {
			link.setText(SUGGESTION_UNAVAILABLE_TEXT);
			link.setUnderlined(false);
			link.setEnabled(false);
		}
	}

	private void showSuggestionValues(final AlignmentParametersBean results) {
		PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
			@Override
			public void run() {
				for (Hyperlink link : suggestionControls) {
					link.setUnderlined(true);
					link.setEnabled(true);
				}
				lblWigglerSuggestion.setText(UnitSetup.MILLI_METER.addUnitSuffix(ClientConfig.roundDoubletoString(results.getWigglerGap())));
				lblPolyBender1Suggestion.setText(ClientConfig.roundDoubletoString(results.getPolyBend1()));
				lblPolyBender2Suggestion.setText(ClientConfig.roundDoubletoString(results.getPolyBend2()));
				lblMe1StripSuggestion.setText(results.getMe1stripe());
				lblMe2StripSuggestion.setText(results.getMe2stripe());
				lblSlitGapSuggestion.setText(ClientConfig.roundDoubletoString(results.getPrimarySlitGap()));
				lblArm2ThetaAngleSuggestion.setText(ClientConfig.roundDoubletoString(results.getArm2Theta()));
				lblPolyBraggSuggestion.setText(ClientConfig.roundDoubletoString(results.getBraggAngle()));
				lblMe2PitchAngleSuggestion.setText(ClientConfig.roundDoubletoString(results.getMe2Pitch()));

				// TODO Check if this value is correct
				// FIXME Conversion shouldn't not be done in this UI section
				lblDetectorDistanceSuggestion.setText(ClientConfig.roundDoubletoString(results.getDetectorDistance() * 1000)); // Convert to mm
				lblDetectorHeightSuggestion.setText(ClientConfig.roundDoubletoString(results.getDetectorHeight())); // FIXME Why not convert for this one?

				lblAtn1Suggestion.setText(results.getAtn1().toString());
				lblAtn2Suggestion.setText(results.getAtn2().toString());
				lblAtn3Suggestion.setText(results.getAtn3().toString());

				reportPowerEst(results.getPower());
			}
		});
	}

	@Override
	public void setFocus() {
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
