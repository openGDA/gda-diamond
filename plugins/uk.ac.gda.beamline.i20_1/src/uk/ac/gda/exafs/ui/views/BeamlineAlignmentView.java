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
import gda.device.detector.StripDetector;
import gda.jython.InterfaceProvider;
import gda.util.exafs.AbsorptionEdge;
import gda.util.exafs.Element;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.list.IListChangeListener;
import org.eclipse.core.databinding.observable.list.ListChangeEvent;
import org.eclipse.core.databinding.observable.list.ListDiffVisitor;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.databinding.validation.ValidationStatus;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.databinding.viewers.ViewersObservables;
import org.eclipse.jface.dialogs.IMessageProvider;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.ComboViewer;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.CCombo;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.swt.widgets.ToolItem;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormText;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.forms.widgets.TableWrapData;
import org.eclipse.ui.forms.widgets.TableWrapLayout;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.ui.views.properties.tabbed.ITabbedPropertySheetPageContributor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.data.AlignmentParametersBean;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.CrystalCut;
import uk.ac.gda.exafs.data.ClientConfig.CrystalType;
import uk.ac.gda.exafs.data.ClientConfig.ScannableSetup;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.EdeCalibrationModel;
import uk.ac.gda.exafs.data.EdeCalibrationModel.ElementReference;
import uk.ac.gda.exafs.ui.composites.MotorPositionEditorControl;
import uk.ac.gda.exafs.ui.composites.ScannableWrapper;
import uk.ac.gda.exafs.ui.data.ScannableMotorMoveObserver;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.sections.DetectorSetupDialog;
import uk.ac.gda.ui.viewer.EnumPositionViewer;

/**
 * Has controls for operating the lookuptable matching optics positions to energy
 */
public class BeamlineAlignmentView extends ViewPart implements ITabbedPropertySheetPageContributor {

	private static final int LABEL_WIDTH = 125;
	private static final int SUGGESTION_LABEL_WIDTH = 100;
	private static final int COMMAND_WAIT_TIME_IN_MILLI_SEC = 100;

	private static final String SUGGESTION_UNAVAILABLE_TEXT = "-";

	public static String ID = "uk.ac.gda.exafs.ui.views.beamlinealignmentview";

	private static Logger logger = LoggerFactory.getLogger(BeamlineAlignmentView.class);

	public static final String OUTPUT_BEAN_NAME = "beamlinealignmentresults";
	public static final String INPUT_BEAN_NAME = "beamlinealignmentparameters";

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private ComboViewer cmbCrystalCut;
	private ComboViewer cmbCrystalType;
	private ComboViewer cmbElement;
	private ComboViewer cmdElementEdge;
	private ComboViewer cmbCrystalQ;
	private ComboViewer cmbDetectorType;

	private FormToolkit toolkit;
	private ScrolledForm scrolledPolyForm;
	private Label lblWigglerSuggestion;
	private Label lblSlitGapSuggestion;
	private Label lblAtn1Suggestion;
	private Label lblAtn2Suggestion;
	private Label lblAtn3Suggestion;
	private Label lblMe1StripSuggestion;
	private Label lblMe2StripSuggestion;
	private Label lblMe2PitchAngleSuggestion;
	private Label lblPolyBender1Suggestion;
	private Label lblPolyBender2Suggestion;
	private Label lblPolyBraggSuggestion;
	private Label lblArm2ThetaAngleSuggestion;
	private Label lblDetectorHeightSuggestion;
	private Label lblDetectorDistanceSuggestion;
	private FormText labelPowerEstimateValue;

	private boolean powerWarningDialogShown = false;
	private FormText labelDeltaEValueSuggestion;

	private final Map<Button, Label> suggestionControls = new HashMap<Button, Label>();
	private final WritableList movingScannables = new WritableList(new ArrayList<Scannable>(), Scannable.class);
	private final ScannableMotorMoveObserver moveObserver = new ScannableMotorMoveObserver(movingScannables);

	@Override
	public void createPartControl(final Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		scrolledPolyForm = toolkit.createScrolledForm(parent);
		TableWrapLayout layout = new TableWrapLayout();
		scrolledPolyForm.getBody().setLayout(layout);
		toolkit.decorateFormHeading(scrolledPolyForm.getForm());
		scrolledPolyForm.setText("Configuration");
		createMainControls(scrolledPolyForm.getForm());
		try {
			createMotorControls(scrolledPolyForm.getForm());
		} catch (Exception e) {
			UIHelper.showError("Unable to create motor controls", e.getMessage());
		}
	}

	@Override
	public void dispose() {
		toolkit.dispose();
		super.dispose();
	}

	private void createMainControls(final Form form) {
		final Section mainSection = toolkit.createSection(form.getBody(), ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		mainSection.setText("Main Parameters");

		mainSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite mainSelectionComposite = toolkit.createComposite(mainSection, SWT.NONE);
		toolkit.paintBordersFor(mainSelectionComposite);
		mainSelectionComposite.setLayout(new GridLayout(2, false));
		mainSection.setClient(mainSelectionComposite);

		Label lblDetector = toolkit.createLabel(mainSelectionComposite, "Detector:", SWT.NONE);
		lblDetector.setLayoutData(createLabelGridData());

		Composite detectorConfigComposite = toolkit.createComposite(mainSelectionComposite, SWT.None);
		detectorConfigComposite.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		GridLayout gridLayout = new GridLayout(2, false);
		gridLayout.verticalSpacing = 0;
		detectorConfigComposite.setLayout(gridLayout);
		cmbDetectorType =  new ComboViewer(detectorConfigComposite, SWT.READ_ONLY);
		cmbDetectorType.setContentProvider(ArrayContentProvider.getInstance());
		cmbDetectorType.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object element) {
				return ((StripDetector) element).getName();
			}
		});
		cmbDetectorType.getCombo().setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		toolkit.paintBordersFor(detectorConfigComposite);

		Button butDetectorSetup = toolkit.createButton(detectorConfigComposite, "Setup", SWT.FLAT);
		butDetectorSetup.setLayoutData(new GridData(GridData.HORIZONTAL_ALIGN_END));

		Label lblCrystalType = toolkit.createLabel(mainSelectionComposite, "Crytal type:", SWT.NONE);
		lblCrystalType.setLayoutData(createLabelGridData());
		cmbCrystalType = new ComboViewer(new CCombo(mainSelectionComposite, SWT.READ_ONLY));
		cmbCrystalType.setContentProvider(ArrayContentProvider.getInstance());
		cmbCrystalType.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object element) {
				return ((CrystalType) element).name();
			}
		});
		cmbCrystalType.setInput(new CrystalType[]{CrystalType.Bragg});
		cmbCrystalType.setSelection(new StructuredSelection(CrystalType.Bragg));
		cmbCrystalType.getCCombo().setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		Label lblCrystalCut = toolkit.createLabel(mainSelectionComposite, CrystalCut.UI_LABEL, SWT.NONE);
		lblCrystalCut.setLayoutData(createLabelGridData());
		cmbCrystalCut = new ComboViewer(new CCombo(mainSelectionComposite, SWT.READ_ONLY));
		cmbCrystalCut.setContentProvider(ArrayContentProvider.getInstance());
		cmbCrystalCut.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object element) {
				return ((CrystalCut) element).name();
			}
		});
		cmbCrystalCut.setInput(CrystalCut.values());
		cmbCrystalCut.addSelectionChangedListener(new ISelectionChangedListener() {
			@Override
			public void selectionChanged(SelectionChangedEvent event) {
				CrystalCut cut = ((CrystalCut) ((IStructuredSelection) event.getSelection()).getFirstElement());
				Element selectedElement = null;
				if (cmbElement.getSelection() != null && ((IStructuredSelection) cmbElement.getSelection()).getFirstElement() != null) {
					Element element = (Element) ((IStructuredSelection) cmbElement.getSelection()).getFirstElement();
					if (cut.getElementsInEnergyRange().keySet().contains(element)) {
						selectedElement = element;
					}
				}
				cmbElement.setInput(cut.getElementsInEnergyRange().keySet());
				if (selectedElement == null) {
					cmbElement.setSelection(new StructuredSelection(cmbElement.getElementAt(0)));
				} else {
					cmbElement.setSelection(new StructuredSelection(selectedElement));
				}
			}
		});
		cmbCrystalCut.getCCombo().setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		Label lblCrystalQ = toolkit.createLabel(mainSelectionComposite, "Crystal q:", SWT.NONE);
		lblCrystalQ.setLayoutData(createLabelGridData());
		cmbCrystalQ = new ComboViewer(new CCombo(mainSelectionComposite, SWT.READ_ONLY));
		cmbCrystalQ.setContentProvider(new ArrayContentProvider());
		cmbCrystalQ.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object value) {
				return value.toString();
			}
		});
		cmbCrystalQ.setInput(new String[] { AlignmentParametersBean.Q[0].toString(),
				AlignmentParametersBean.Q[1].toString(), AlignmentParametersBean.Q[2].toString() });
		cmbCrystalQ.setSelection(new StructuredSelection(AlignmentParametersBean.Q[0].toString()));
		cmbCrystalQ.addSelectionChangedListener(new ISelectionChangedListener() {
			@Override
			public void selectionChanged(SelectionChangedEvent event) {
				getScannableValuesSuggestion();
			}
		});
		cmbCrystalQ.getCCombo().setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		Label lbl = toolkit.createLabel(mainSelectionComposite, "Element:", SWT.NONE);
		lbl.setLayoutData(createLabelGridData());
		cmbElement = new ComboViewer(new CCombo(mainSelectionComposite, SWT.READ_ONLY));
		cmbElement.getCCombo().setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		cmbElement.setContentProvider(new ArrayContentProvider());
		cmbElement.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object value) {
				Element element = (Element) value;
				return element.getName() + " (" + element.getSymbol() + ")";
			}
		});

		lbl = toolkit.createLabel(mainSelectionComposite, "Edge:", SWT.NONE);
		lbl.setLayoutData(createLabelGridData());
		cmdElementEdge = new ComboViewer(new CCombo(mainSelectionComposite, SWT.READ_ONLY));
		cmdElementEdge.getCCombo().setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		cmdElementEdge.setContentProvider(ArrayContentProvider.getInstance());

		lbl = toolkit.createLabel(mainSelectionComposite, "Energy:", SWT.NONE);
		lbl.setLayoutData(createLabelGridData());
		final Label energyLabel = toolkit.createLabel(mainSelectionComposite, "", SWT.BORDER);
		energyLabel.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		cmdElementEdge.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object element) {
				Element selectedElement = (Element) ((IStructuredSelection) cmbElement.getSelection()).getFirstElement();
				String edgeName = (String) element;
				energyLabel.setText(UnitSetup.EV.addUnitSuffix(Double.toString(selectedElement.getEdgeEnergy(edgeName))));
				return edgeName;
			}
		});

		cmbElement.addSelectionChangedListener(new ISelectionChangedListener() {
			@Override
			public void selectionChanged(SelectionChangedEvent event) {
				Element element = ((Element) ((IStructuredSelection) event.getSelection()).getFirstElement());
				CrystalCut cut = ((CrystalCut) ((IStructuredSelection) cmbCrystalCut.getSelection()).getFirstElement());
				if (element != null && cut != null) {
					cmdElementEdge.setInput(cut.getElementsInEnergyRange().get(element));
					cmdElementEdge.setSelection(new StructuredSelection(cmdElementEdge.getElementAt(0)));
				}
			}
		});

		cmdElementEdge.addSelectionChangedListener(new ISelectionChangedListener() {
			@Override
			public void selectionChanged(SelectionChangedEvent event) {
				getScannableValuesSuggestion();
			}
		});

		DetectorModel.INSTANCE.addPropertyChangeListener(DetectorModel.DETECTOR_CONNECTED_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if ((boolean) evt.getNewValue()) {
					final StructuredSelection initialSelection = new StructuredSelection(CrystalCut.Si111);
					cmbCrystalCut.setSelection(initialSelection);
				}
			}
		});

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(mainSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		mainSection.setSeparatorControl(defaultSectionSeparator);

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(cmdElementEdge.getControl()),
				BeanProperties.value(DetectorModel.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorModel.INSTANCE));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(cmbElement.getControl()),
				BeanProperties.value(DetectorModel.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorModel.INSTANCE));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(cmbCrystalCut.getControl()),
				BeanProperties.value(DetectorModel.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorModel.INSTANCE));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(butDetectorSetup),
				BeanProperties.value(DetectorModel.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorModel.INSTANCE));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(cmbCrystalQ.getControl()),
				BeanProperties.value(DetectorModel.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorModel.INSTANCE));

		dataBindingCtx.bindValue(
				ViewersObservables.observeSingleSelection(cmbElement),
				BeanProperties.value(ElementReference.SELECTED_ELEMENT_PROP_NAME).observe(EdeCalibrationModel.INSTANCE.getEdeData()));

		dataBindingCtx.bindValue(
				ViewersObservables.observeSingleSelection(cmbElement),
				BeanProperties.value(ElementReference.SELECTED_ELEMENT_PROP_NAME).observe(EdeCalibrationModel.INSTANCE.getRefData()));

		butDetectorSetup.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				DetectorSetupDialog setup = new DetectorSetupDialog(form.getBody().getShell());
				setup.setBlockOnOpen(true);
				setup.open();
			}
		});

		setupDetector();

	}

	private Binding detectorValueBinding = null;
	private FormText labelDeltaEValue;
	private void setupDetector() {
		try {
			DetectorModel.INSTANCE.setupDetectors();
			cmbDetectorType.setInput(DetectorModel.INSTANCE.getAvailableDetectors());
			UpdateValueStrategy detectorSelectionUpdateStrategy = new UpdateValueStrategy() {
				@Override
				protected IStatus doSet(IObservableValue observableValue, Object value) {
					StripDetector detector = DetectorModel.INSTANCE.getCurrentDetector();
					boolean changeConfirm = true;
					if (detector != null && detector.isConnected()) {
						changeConfirm = MessageDialog.openConfirm(Display.getDefault().getActiveShell(), "Changing Detectors", detector.getName() + " is currently connected. Disconnect " + detector.getName() + " and connect " + ((StripDetector)value).getName() + "?");
					}
					if (changeConfirm) {
						IStatus status = super.doSet(observableValue, value);
						if (!status.isOK()) {
							revertToModel();
							logger.error("Unable to set new detector", status.getMessage());
							UIHelper.showError("Unable to set new detector", status.getMessage());
						} else {
							getScannableValuesSuggestion();
						}
						return status;
					}
					revertToModel();
					return ValidationStatus.ok();
				}
			};
			detectorValueBinding = dataBindingCtx.bindValue(
					ViewersObservables.observeSingleSelection(cmbDetectorType),
					BeanProperties.value(DetectorModel.CURRENT_DETECTOR_SETUP_PROP_NAME).observe(DetectorModel.INSTANCE),
					detectorSelectionUpdateStrategy, null);

		} catch (Exception e) {
			logger.error("Error while retrieving available detectors", e);
			UIHelper.showError("Unable to setup detectors", "Error while retrieving available detectors");
		}
	}

	private void revertToModel() {
		if (detectorValueBinding != null) {
			detectorValueBinding.updateModelToTarget();
		}
	}

	// FIXME this is not a elegant way to providing suggestion values
	private void getScannableValuesSuggestion() {
		if (!DetectorModel.INSTANCE.isDetectorConnected()) {
			return;
		}
		Element selectedElement = (Element) ((IStructuredSelection) cmbElement.getSelection()).getFirstElement();
		String selectedEdgeString = (String) ((IStructuredSelection) cmdElementEdge.getSelection()).getFirstElement();
		AbsorptionEdge absEdge = selectedElement.getEdge(selectedEdgeString);
		String qString = (String) ((IStructuredSelection) cmbCrystalQ.getSelection()).getFirstElement();
		Double q = Double.parseDouble(qString);

		String xtalCutString = ((CrystalCut) ((StructuredSelection) cmbCrystalCut.getSelection()).getFirstElement()).name();
		String xtalTypeString = ((CrystalType) ((StructuredSelection) cmbCrystalType.getSelection()).getFirstElement()).name();
		String detectorString = DetectorModel.INSTANCE.getCurrentDetector().getName();
		try {
			AlignmentParametersBean bean = new AlignmentParametersBean(xtalTypeString, xtalCutString, q,
					detectorString, absEdge);

			InterfaceProvider.getJythonNamespace().placeInJythonNamespace(INPUT_BEAN_NAME, bean);

			InterfaceProvider.getCommandRunner().runCommand(
					OUTPUT_BEAN_NAME + "=None;from alignment import alignment_parameters; " + OUTPUT_BEAN_NAME
					+ " = alignment_parameters.calc_parameters(" + INPUT_BEAN_NAME + ")");
			// give the command a chance to run.
			boolean waitForResult = true;
			Object result = null;
			while (waitForResult) {
				Thread.sleep(COMMAND_WAIT_TIME_IN_MILLI_SEC);
				result = InterfaceProvider.getJythonNamespace()
						.getFromJythonNamespace(OUTPUT_BEAN_NAME);
				if (result != null && (result instanceof AlignmentParametersBean)) {
					waitForResult = false;
				}
			}
			showSuggestionValues((AlignmentParametersBean) result);
		} catch (Exception e1) {
			logger.error("Exception when trying to run the script which performs the alignment calculations.",e1);
		}
	}

	@SuppressWarnings("unused")
	private void createMotorControls(Form form) throws Exception {

		final Section motorSection = toolkit.createSection(form.getBody(), ExpandableComposite.TITLE_BAR
				| ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		motorSection.setText("Motor Positions");
		motorSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite motorSectionComposite = toolkit.createComposite(motorSection, SWT.NONE);
		toolkit.paintBordersFor(motorSectionComposite);
		motorSectionComposite.setLayout(new GridLayout(4, false));
		motorSection.setClient(motorSectionComposite);

		toolkit.createLabel(motorSectionComposite, ""); // Place holder
		toolkit.createLabel(motorSectionComposite, "Calculated");
		toolkit.createLabel(motorSectionComposite, ""); // Place holder
		toolkit.createLabel(motorSectionComposite, "Motor Readback");
		lblWigglerSuggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.WIGGLER_GAP);

		Button applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblWigglerSuggestion);

		Scannable scannable = ScannableSetup.WIGGLER_GAP.getScannable();
		scannable.addIObserver(moveObserver);
		MotorPositionEditorControl motorPositionEditorControl = new MotorPositionEditorControl(motorSectionComposite, SWT.None, new ScannableWrapper(scannable), true);

		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		applyButton.addListener(SWT.Selection, new SuggestionApplyButtonListener(ScannableSetup.WIGGLER_GAP, lblWigglerSuggestion, motorPositionEditorControl));

		lblSlitGapSuggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.SLIT_1_HORIZONAL_GAP);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblSlitGapSuggestion);

		scannable = ScannableSetup.SLIT_1_HORIZONAL_GAP.getScannable();
		scannable.addIObserver(moveObserver);
		motorPositionEditorControl = new MotorPositionEditorControl(motorSectionComposite, SWT.None, new ScannableWrapper(scannable), true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		applyButton.addListener(SWT.Selection, new SuggestionApplyButtonListener(ScannableSetup.SLIT_1_HORIZONAL_GAP, lblSlitGapSuggestion, motorPositionEditorControl));

		lblAtn1Suggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.ATN1);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblAtn1Suggestion);
		EnumPositionViewer enumPositionViewer = new EnumPositionViewer(motorSectionComposite, (EnumPositioner) ScannableSetup.ATN1.getScannable(), "", true);
		enumPositionViewer.getComboWrapper().setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		applyButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					ScannableSetup.ATN1.getScannable().asynchronousMoveTo(lblAtn1Suggestion.getText());
				} catch (Exception e) {
					UIHelper.showError("Exception setting motor to " + lblAtn1Suggestion.getText(), e.getMessage());
				}
			}
		});

		lblAtn2Suggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.ATN2);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblAtn2Suggestion);
		enumPositionViewer = new EnumPositionViewer(motorSectionComposite, (EnumPositioner) ScannableSetup.ATN2.getScannable(), "", true);
		enumPositionViewer.getComboWrapper().setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		applyButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					ScannableSetup.ATN2.getScannable().asynchronousMoveTo(lblAtn2Suggestion.getText());
				} catch (Exception e) {
					UIHelper.showError("Exception setting motor to " + lblAtn2Suggestion.getText(), e.getMessage());
				}
			}
		});

		lblAtn3Suggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.ATN3);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblAtn3Suggestion);
		enumPositionViewer = new EnumPositionViewer(motorSectionComposite, (EnumPositioner) ScannableSetup.ATN3.getScannable(), "", true);
		enumPositionViewer.getComboWrapper().setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		applyButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					ScannableSetup.ATN3.getScannable().asynchronousMoveTo(lblAtn3Suggestion.getText());
				} catch (Exception e) {
					UIHelper.showError("Exception setting motor to " + lblAtn3Suggestion.getText(), e.getMessage());
				}
			}
		});

		lblMe1StripSuggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.ME1_STRIPE);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblMe1StripSuggestion);
		enumPositionViewer = new EnumPositionViewer(motorSectionComposite, (EnumPositioner) ScannableSetup.ME1_STRIPE.getScannable(), "", true);
		enumPositionViewer.getComboWrapper().setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		applyButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					ScannableSetup.ME1_STRIPE.getScannable().asynchronousMoveTo(lblMe1StripSuggestion.getText());
				} catch (Exception e) {
					UIHelper.showError("Exception setting motor to " + lblMe1StripSuggestion.getText(), e.getMessage());
				}
			}
		});

		lblMe2StripSuggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.ME2_STRIPE);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblMe2StripSuggestion);
		enumPositionViewer = new EnumPositionViewer(motorSectionComposite, (EnumPositioner) ScannableSetup.ME2_STRIPE.getScannable(), "", true);
		enumPositionViewer.getComboWrapper().setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		applyButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					ScannableSetup.ME2_STRIPE.getScannable().asynchronousMoveTo(lblMe2StripSuggestion.getText());
				} catch (Exception e) {
					UIHelper.showError("Exception setting motor to " + lblMe2StripSuggestion.getText(), e.getMessage());
				}
			}
		});

		lblMe2PitchAngleSuggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.ME2_PITCH_ANGLE);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblMe2PitchAngleSuggestion);

		scannable = ScannableSetup.ME2_PITCH_ANGLE.getScannable();
		scannable.addIObserver(moveObserver);
		motorPositionEditorControl = new MotorPositionEditorControl(motorSectionComposite, SWT.None, new ScannableWrapper(scannable), true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		applyButton.addListener(SWT.Selection, new SuggestionApplyButtonListener(ScannableSetup.ME2_PITCH_ANGLE, lblMe2PitchAngleSuggestion, motorPositionEditorControl));

		lblPolyBender1Suggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.POLY_BENDER_1);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblPolyBender1Suggestion);

		scannable = ScannableSetup.POLY_BENDER_1.getScannable();
		scannable.addIObserver(moveObserver);
		motorPositionEditorControl = new MotorPositionEditorControl(motorSectionComposite, SWT.None, new ScannableWrapper(scannable), true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		applyButton.addListener(SWT.Selection, new SuggestionApplyButtonListener(ScannableSetup.POLY_BENDER_1, lblPolyBender1Suggestion, motorPositionEditorControl));

		lblPolyBender2Suggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.POLY_BENDER_2);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblPolyBender2Suggestion);

		scannable = ScannableSetup.POLY_BENDER_2.getScannable();
		scannable.addIObserver(moveObserver);
		motorPositionEditorControl = new MotorPositionEditorControl(motorSectionComposite, SWT.None, new ScannableWrapper(scannable), true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		applyButton.addListener(SWT.Selection, new SuggestionApplyButtonListener(ScannableSetup.POLY_BENDER_2, lblPolyBender2Suggestion, motorPositionEditorControl));

		final Button btnSynchroniseThetas = toolkit.createButton(motorSectionComposite, "Match TwoTheta arm to Poly Bragg value", SWT.CHECK | SWT.WRAP);
		GridData gridData = new GridData(GridData.HORIZONTAL_ALIGN_BEGINNING);
		gridData.horizontalSpan = 4;
		btnSynchroniseThetas.setLayoutData(gridData);
		btnSynchroniseThetas.setSelection(true);

		lblPolyBraggSuggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.POLY_BRAGG);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblPolyBraggSuggestion);

		scannable = ScannableSetup.POLY_BRAGG.getScannable();
		scannable.addIObserver(moveObserver);
		BraggAngleAndTwoThetaScannableWrapper braggAngleScannableWrapper = new BraggAngleAndTwoThetaScannableWrapper(scannable, btnSynchroniseThetas);
		motorPositionEditorControl = new MotorPositionEditorControl(motorSectionComposite, SWT.None, braggAngleScannableWrapper, true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		applyButton.addListener(SWT.Selection, new SuggestionApplyButtonListener(ScannableSetup.POLY_BRAGG, lblPolyBraggSuggestion, motorPositionEditorControl));

		lblArm2ThetaAngleSuggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.ARM_2_THETA_ANGLE);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblArm2ThetaAngleSuggestion);

		scannable = ScannableSetup.ARM_2_THETA_ANGLE.getScannable();
		scannable.addIObserver(moveObserver);
		BraggAngleAndTwoThetaScannableWrapper twoThetacannableWrapper = new BraggAngleAndTwoThetaScannableWrapper(scannable, btnSynchroniseThetas);
		motorPositionEditorControl = new MotorPositionEditorControl(motorSectionComposite, SWT.None, twoThetacannableWrapper, true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		applyButton.addListener(SWT.Selection, new SuggestionApplyButtonListener(ScannableSetup.ARM_2_THETA_ANGLE, lblArm2ThetaAngleSuggestion, motorPositionEditorControl));

		braggAngleScannableWrapper.setLinkedMotorPositionEditor(twoThetacannableWrapper, true);
		twoThetacannableWrapper.setLinkedMotorPositionEditor(braggAngleScannableWrapper, false);

		Label lblPowerEstimate = toolkit.createLabel(motorSectionComposite, "Estimated power is: ");
		lblPowerEstimate.setLayoutData(new GridData(GridData.HORIZONTAL_ALIGN_BEGINNING));
		labelPowerEstimateValue = toolkit.createFormText(motorSectionComposite, false);
		labelPowerEstimateValue.setText(getHighlightedFormatedString(""), true, false);
		gridData = new GridData(GridData.HORIZONTAL_ALIGN_FILL);
		gridData.horizontalSpan = 3;
		labelPowerEstimateValue.setLayoutData(gridData);

		lblDetectorHeightSuggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.DETECTOR_HEIGHT);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblDetectorHeightSuggestion);

		scannable = ScannableSetup.DETECTOR_HEIGHT.getScannable();
		scannable.addIObserver(moveObserver);
		motorPositionEditorControl = new MotorPositionEditorControl(motorSectionComposite, SWT.None, new ScannableWrapper(scannable), true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		applyButton.addListener(SWT.Selection, new SuggestionApplyButtonListener(ScannableSetup.DETECTOR_HEIGHT, lblDetectorHeightSuggestion, motorPositionEditorControl));

		try {
			final Scannable detectorHeight = ScannableSetup.DETECTOR_HEIGHT.getScannable();
			final Scannable detectorDistance = ScannableSetup.DETECTOR_DISTANCE.getScannable();
			movingScannables.addListChangeListener(new IListChangeListener() {
				@Override
				public void handleListChange(ListChangeEvent event) {
					event.diff.accept(new ListDiffVisitor() {
						@Override
						public void handleRemove(int index, Object element) {
							if (element == detectorHeight | element == detectorDistance) {
								getScannableValuesSuggestion();
							}
						}
						@Override
						public void handleAdd(int index, Object element) {}
					});
				}
			});

		} catch (Exception e) {
			UIHelper.showError("Unable to find detector details", e.getMessage());
		}
		lblDetectorDistanceSuggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.DETECTOR_DISTANCE);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblDetectorDistanceSuggestion);

		scannable = ScannableSetup.DETECTOR_DISTANCE.getScannable();
		scannable.addIObserver(moveObserver);
		motorPositionEditorControl = new MotorPositionEditorControl(motorSectionComposite, SWT.None, new ScannableWrapper(scannable), true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		applyButton.addListener(SWT.Selection, new SuggestionApplyButtonListener(ScannableSetup.DETECTOR_DISTANCE, lblDetectorDistanceSuggestion, motorPositionEditorControl));

		Label lblDeltaE = toolkit.createLabel(motorSectionComposite, "Energy bandwidth for\n calculated detector distance:", SWT.WRAP);
		gridData = new GridData(SWT.BEGINNING, SWT.BEGINNING, false, false);
		gridData.horizontalSpan = 3;
		lblDeltaE.setLayoutData(gridData);

		labelDeltaEValueSuggestion = toolkit.createFormText(motorSectionComposite, false);
		labelDeltaEValueSuggestion.setText(getHighlightedFormatedString(""), true, false);
		gridData = new GridData(GridData.HORIZONTAL_ALIGN_FILL);
		labelDeltaEValueSuggestion.setLayoutData(gridData);

		lblDeltaE = toolkit.createLabel(motorSectionComposite, "Energy bandwidth for\n current detector distance:", SWT.WRAP);
		gridData = new GridData(SWT.BEGINNING, SWT.BEGINNING, false, false);
		gridData.horizontalSpan = 3;
		lblDeltaE.setLayoutData(gridData);

		labelDeltaEValue = toolkit.createFormText(motorSectionComposite, false);
		labelDeltaEValue.setText(getHighlightedFormatedString(""), true, false);
		gridData = new GridData(GridData.HORIZONTAL_ALIGN_FILL);
		labelDeltaEValue.setLayoutData(gridData);

		final ToolBar motorSectionTbar = new ToolBar(motorSection, SWT.FLAT | SWT.HORIZONTAL);
		new ToolItem(motorSectionTbar, SWT.SEPARATOR);
		final ToolItem stopMotorsBarItem = ScannableMotorMoveObserver.setupStopToolItem(motorSectionTbar, movingScannables);
		motorSection.setTextClient(motorSectionTbar);
		movingScannables.addListChangeListener(ScannableMotorMoveObserver.getStopButtonListener(motorSection, stopMotorsBarItem));
		stopMotorsBarItem.setEnabled(!movingScannables.isEmpty());

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(motorSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		motorSection.setSeparatorControl(defaultSectionSeparator);
	}

	private static String getHighlightedFormatedString(String value) {
		return String.format("<form><p><b>%s</b></p></form>", value);
	}

	private Label createSuggestionLabel(Composite parent, ScannableSetup scannableSetup) {
		Label lbl = toolkit.createLabel(parent, scannableSetup.getLabel(), SWT.NONE);
		lbl.setLayoutData(createLabelGridData());
		Label lblSuggestion = toolkit.createLabel(parent, SUGGESTION_UNAVAILABLE_TEXT, SWT.NONE);
		lblSuggestion.setLayoutData(createSuggestionLabelLayout());
		return lblSuggestion;
	}

	private GridData createLabelGridData() {
		GridData gridData = new GridData(GridData.BEGINNING, GridData.CENTER, false, false);
		gridData.widthHint = LABEL_WIDTH;
		return gridData;
	}

	private GridData createSuggestionLabelLayout() {
		GridData gridData = new GridData(GridData.BEGINNING, GridData.CENTER, false, false);
		gridData.widthHint = SUGGESTION_LABEL_WIDTH;
		return gridData;
	}

	private Button createMotorControl(Composite parent) {
		Button suggestionApplyButton = toolkit.createButton(parent, "", SWT.FLAT);
		suggestionApplyButton.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_TOOL_FORWARD));
		suggestionApplyButton.setLayoutData(new GridData(GridData.BEGINNING, GridData.BEGINNING, false, false));
		return suggestionApplyButton;
	}

	private static class BraggAngleAndTwoThetaScannableWrapper extends ScannableWrapper {
		private ScannableWrapper otherScannableEditorControl;
		private final Button btnSynchroniseThetas;
		private boolean isTimesTwo;

		@Override
		public void setPosition(double value) throws DeviceException {
			super.setPosition(value);
			if (btnSynchroniseThetas.getSelection()) {
				if (otherScannableEditorControl.getTargetPosition() == null) {
					if (isTimesTwo) {
						if (value * 2 != otherScannableEditorControl.getPosition()) {
							otherScannableEditorControl.setPosition(value * 2);
						}
					} else {
						if (value / 2 != otherScannableEditorControl.getPosition()) {
							otherScannableEditorControl.setPosition(value / 2);
						}
					}
				}
			}
		}

		public void setLinkedMotorPositionEditor(ScannableWrapper otherScannableEditorControl, boolean isTimesTwo) {
			this.otherScannableEditorControl = otherScannableEditorControl;
			this.isTimesTwo = isTimesTwo;
		}

		public BraggAngleAndTwoThetaScannableWrapper(Scannable scannable, Button btnSynchroniseThetas) {
			super(scannable);
			this.btnSynchroniseThetas = btnSynchroniseThetas;
		}
	}

	private static class SuggestionApplyButtonListener implements Listener {
		MotorPositionEditorControl motorPositionEditorControl;
		protected final ScannableSetup scannableSetup;
		protected final Label suggestionLabel;
		public SuggestionApplyButtonListener(ScannableSetup scannableSetup, Label suggestionLabel,
				MotorPositionEditorControl motorPositionEditorControl) {
			this.motorPositionEditorControl = motorPositionEditorControl;
			this.scannableSetup = scannableSetup;
			this.suggestionLabel = suggestionLabel;
		}

		@Override
		public void handleEvent(Event event) {
			try {
				motorPositionEditorControl.setPosition(Double.parseDouble(scannableSetup.getUnit().removeUnitSuffix(suggestionLabel.getText())));
			} catch (Exception e) {
				String errorMessage = "Exception while applying " + scannableSetup.getLabel() + " to " + suggestionLabel.getText();
				logger.error(errorMessage, e);
				UIHelper.showError(errorMessage, e.getMessage());
			}
		}
	}

	private void reportPowerEst(Double powerValue) {
		if (powerValue > ScannableSetup.MAX_POWER_IN_WATT) {
			if (!powerWarningDialogShown) {
				UIHelper.showWarning("Power is above the maximum expected for operation", "Estimated power is " + powerValue);
			}
			String value = UnitSetup.WATT.addUnitSuffix("WARNING: Estimated power is " + powerValue);
			scrolledPolyForm.getForm().setMessage(value, IMessageProvider.ERROR);
			labelPowerEstimateValue.setText(getHighlightedFormatedString(value), true, false);
			powerWarningDialogShown = true;
		} else {
			scrolledPolyForm.getForm().setMessage("");
			labelPowerEstimateValue.setText(getHighlightedFormatedString(UnitSetup.WATT.addUnitSuffix(powerValue.toString())), true, false);
			powerWarningDialogShown = false;
		}
	}

	private void showSuggestionValues(final AlignmentParametersBean results) {
		PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
			@Override
			public void run() {
				lblWigglerSuggestion.setText(ScannableSetup.WIGGLER_GAP.getUnit().addUnitSuffix(ClientConfig.roundDoubletoString(results.getWigglerGap())));
				lblPolyBender1Suggestion.setText(ScannableSetup.POLY_BENDER_1.getUnit().addUnitSuffix(ClientConfig.roundDoubletoString(results.getPolyBend1())));
				lblPolyBender2Suggestion.setText(ScannableSetup.POLY_BENDER_2.getUnit().addUnitSuffix(ClientConfig.roundDoubletoString(results.getPolyBend2())));
				lblMe1StripSuggestion.setText(results.getMe1stripe());
				lblMe2StripSuggestion.setText(results.getMe2stripe());
				lblSlitGapSuggestion.setText(ScannableSetup.SLIT_1_HORIZONAL_GAP.getUnit().addUnitSuffix(ClientConfig.roundDoubletoString(results.getPrimarySlitGap())));
				lblArm2ThetaAngleSuggestion.setText(ScannableSetup.ARM_2_THETA_ANGLE.getUnit().addUnitSuffix(ClientConfig.roundDoubletoString(results.getArm2Theta())));
				lblPolyBraggSuggestion.setText(ScannableSetup.POLY_BRAGG.getUnit().addUnitSuffix(ClientConfig.roundDoubletoString(results.getBraggAngle())));
				lblMe2PitchAngleSuggestion.setText(ScannableSetup.ME2_PITCH_ANGLE.getUnit().addUnitSuffix(ClientConfig.roundDoubletoString(results.getMe2Pitch())));

				// TODO Check if this value is correct
				// FIXME Conversion shouldn't not be done in this UI section
				lblDetectorDistanceSuggestion.setText(ScannableSetup.DETECTOR_DISTANCE.getUnit().addUnitSuffix(ClientConfig.roundDoubletoString(results.getDetectorDistance() * 1000))); // Convert to mm
				lblDetectorHeightSuggestion.setText(ScannableSetup.DETECTOR_HEIGHT.getUnit().addUnitSuffix(ClientConfig.roundDoubletoString(results.getDetectorHeight())));

				lblAtn1Suggestion.setText(results.getAtn1().toString());
				lblAtn2Suggestion.setText(results.getAtn2().toString());
				lblAtn3Suggestion.setText(results.getAtn3().toString());

				reportPowerEst(results.getPower());
				if (results.getEnergyBandwidth() != null) {
					String value = getHighlightedFormatedString(UnitSetup.EV.addUnitSuffix(Integer.toString(results.getEnergyBandwidth().intValue())));
					labelDeltaEValueSuggestion.setText(value, true, false);
				}
				if (results.getReadBackEnergyBandwidth() != null) {
					String value = getHighlightedFormatedString(UnitSetup.EV.addUnitSuffix(Integer.toString(results.getReadBackEnergyBandwidth().intValue())));
					labelDeltaEValue.setText(value, true, false);
				}
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
}
