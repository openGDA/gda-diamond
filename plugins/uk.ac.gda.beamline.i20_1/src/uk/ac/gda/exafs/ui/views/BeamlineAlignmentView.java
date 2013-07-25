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
import gda.device.Scannable;
import gda.device.detector.StripDetector;
import gda.device.detector.XCHIPDetector;
import gda.device.scannable.ScannableStatus;
import gda.jython.InterfaceProvider;
import gda.observable.IObserver;
import gda.util.exafs.AbsorptionEdge;
import gda.util.exafs.Element;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Map.Entry;

import org.apache.commons.lang.ArrayUtils;
import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.list.IListChangeListener;
import org.eclipse.core.databinding.observable.list.ListChangeEvent;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.databinding.validation.ValidationStatus;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.databinding.viewers.ViewersObservables;
import org.eclipse.jface.dialogs.IMessageProvider;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.layout.TableColumnLayout;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.ColumnWeightData;
import org.eclipse.jface.viewers.ComboViewer;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.TableItem;
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
import uk.ac.gda.exafs.data.DetectorConfig;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.UIHelper.UIMotorControl;
import uk.ac.gda.exafs.ui.sections.DetectorSetupDialog;
import uk.ac.gda.richbeans.components.FieldComposite.NOTIFY_TYPE;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;
import uk.ac.gda.richbeans.event.ValueEvent;
import uk.ac.gda.richbeans.event.ValueListener;
import uk.ac.gda.ui.viewer.RotationViewer;

/**
 * Has controls for operating the lookuptable matching optics positions to energy
 */
public class BeamlineAlignmentView extends ViewPart implements ITabbedPropertySheetPageContributor {

	private static final int POWER_LABEL_WIDTH = 50;
	private static final int LABEL_WIDTH = 120;
	private static final int SUGGESTION_LABEL_WIDTH = 90;
	private static final int COMMAND_WAIT_TIME_IN_MILLI_SEC = 250;

	private static final String SUGGESTION_UNAVAILABLE_TEXT = "-";

	public static String ID = "uk.ac.gda.exafs.ui.views.beamlinealignmentview";

	private static Logger logger = LoggerFactory.getLogger(BeamlineAlignmentView.class);

	public static final String OUTPUT_BEAN_NAME = "beamlinealignmentresults";
	public static final String INPUT_BEAN_NAME = "beamlinealignmentparameters";

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private ComboViewer cmbCrystalCut;
	private ComboViewer cmbCrystalType;
	private GridData comboGD;
	private Combo cmbElement;
	private Combo cmdElementEdge;
	private ScaleBox scaleBoxEnergyRange;
	private Combo cmbCrystalQ;
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
	private FormText labelTemperatureValue;


	private final Map<Button, Label> suggestionControls = new HashMap<Button, Label>();
	private final WritableList movingScannables = new WritableList(new ArrayList<Scannable>(), Scannable.class);
	private final MoveObserver moveObserver = new MoveObserver(movingScannables);
	private static class MoveObserver implements IObserver {
		private final WritableList movingScannables;
		public MoveObserver(WritableList movingScannables) {
			this.movingScannables = movingScannables;
		}

		@Override
		public void update(final Object source,final Object arg) {
			if (arg instanceof ScannableStatus) {
				movingScannables.getRealm().asyncExec(new Runnable() {
					@Override
					public void run() {
						ScannableStatus status = (ScannableStatus) arg;
						if (status.status == ScannableStatus.BUSY) {
							if (!movingScannables.contains(source)) {
								movingScannables.add(source);
							}
						}
						else {
							movingScannables.remove(source);
						}
					}
				});
			}
		}
	}

	@Override
	public void createPartControl(final Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		scrolledPolyForm = toolkit.createScrolledForm(parent);
		TableWrapLayout layout = new TableWrapLayout();
		scrolledPolyForm.getBody().setLayout(layout);
		toolkit.decorateFormHeading(scrolledPolyForm.getForm());
		scrolledPolyForm.setText("Configuration");

		final Button butStopMotor = toolkit.createButton(scrolledPolyForm.getForm().getHead(), "", SWT.FLAT);
		butStopMotor.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ELCL_STOP));

		movingScannables.addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				if (event.getObservableList().isEmpty()) {
					butStopMotor.setEnabled(false);
					butStopMotor.setText("");
				} else {
					butStopMotor.setEnabled(true);
					if (event.getObservableList().size() == 1) {
						butStopMotor.setText("Stop " + ((Scannable) event.getObservableList().get(0)).getName() + " motor");
					} else {
						butStopMotor.setText("Stop " + event.getObservableList().size() + " motors");
					}
				}
			}
		});
		butStopMotor.setEnabled(!movingScannables.isEmpty());
		butStopMotor.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				for (Object scannable : movingScannables) {
					try {
						((Scannable) scannable).stop();
					} catch (DeviceException e) {
						UIHelper.showError("Unable to stop motor " + ((Scannable) scannable).getName(), e.getMessage());
					}
				}
			}
		});
		scrolledPolyForm.getForm().setHeadClient(butStopMotor);
		createMainControls(scrolledPolyForm.getForm());
		createMotorControls(scrolledPolyForm.getForm());
		createSpectrumControls(scrolledPolyForm.getForm());
		createTempratureSection(scrolledPolyForm.getForm());
		updateElementEdgeSelection();
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
		Button butDetectorSetup = toolkit.createButton(detectorConfigComposite, "Setup", SWT.FLAT);
		butDetectorSetup.setLayoutData(new GridData(GridData.HORIZONTAL_ALIGN_END));

		Label lblCrystalType = toolkit.createLabel(mainSelectionComposite, "Crytal Type:", SWT.NONE);
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

		setupDetector();

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(cmdElementEdge),
				BeanProperties.value(DetectorConfig.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorConfig.INSTANCE));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(scaleBoxEnergyRange),
				BeanProperties.value(DetectorConfig.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorConfig.INSTANCE));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(cmbElement),
				BeanProperties.value(DetectorConfig.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorConfig.INSTANCE));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(cmbCrystalCut.getControl()),
				BeanProperties.value(DetectorConfig.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorConfig.INSTANCE));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(butDetectorSetup),
				BeanProperties.value(DetectorConfig.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorConfig.INSTANCE));

		butDetectorSetup.addListener(SWT.Selection, new Listener() {

			@Override
			public void handleEvent(Event event) {
				DetectorSetupDialog setup = new DetectorSetupDialog(form.getBody().getShell());
				setup.setBlockOnOpen(true);
				setup.open();
			}
		});
	}

	private Binding detectorValueBinding = null;
	private void setupDetector() {
		try {
			DetectorConfig.INSTANCE.setupDetectors();
			cmbDetectorType.setInput(DetectorConfig.INSTANCE.getAvailableDetectors());
			UpdateValueStrategy detectorSelectionUpdateStrategy = new UpdateValueStrategy() {
				@Override
				protected IStatus doSet(IObservableValue observableValue, Object value) {
					StripDetector detector = DetectorConfig.INSTANCE.getCurrentDetector();
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
						}
						return status;
					}
					revertToModel();
					return ValidationStatus.ok();
				}
			};
			detectorValueBinding = dataBindingCtx.bindValue(
					ViewersObservables.observeSingleSelection(cmbDetectorType),
					BeanProperties.value(DetectorConfig.CURRENT_DETECTOR_SETUP_PROP_NAME).observe(DetectorConfig.INSTANCE),
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

	private void getScannableValuesSuggestion() {
		String selectedElementString = cmbElement.getItem(cmbElement.getSelectionIndex());
		Element selectedElement = Element.getElement(selectedElementString);
		String selectedEdgeString = cmdElementEdge.getItem(cmdElementEdge.getSelectionIndex());
		AbsorptionEdge absEdge = selectedElement.getEdge(selectedEdgeString);

		String qString = cmbCrystalQ.getItem(cmbCrystalQ.getSelectionIndex());
		Double q = Double.parseDouble(qString);

		String xtalCutString = ((CrystalCut) ((StructuredSelection) cmbCrystalCut.getSelection()).getFirstElement()).name();
		String xtalTypeString = ((CrystalType) ((StructuredSelection) cmbCrystalType.getSelection()).getFirstElement()).name();
		String detectorString = DetectorConfig.INSTANCE.getCurrentDetector().getName();
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


	private void createMotorControls(Form form) {

		final Section motorSection = toolkit.createSection(form.getBody(), ExpandableComposite.TITLE_BAR
				| ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		motorSection.setText("Motor Positions");
		motorSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite motorSelectionComposite = toolkit.createComposite(motorSection, SWT.NONE);
		toolkit.paintBordersFor(motorSelectionComposite);
		motorSelectionComposite.setLayout(new GridLayout(4, false));
		motorSection.setClient(motorSelectionComposite);

		toolkit.createLabel(motorSelectionComposite, ""); // Place holder
		toolkit.createLabel(motorSelectionComposite, "Calculated");
		toolkit.createLabel(motorSelectionComposite, ""); // Place holder
		toolkit.createLabel(motorSelectionComposite, "Motor Readback");
		lblWigglerSuggestion = createSuggestionLabel(motorSelectionComposite, ScannableSetup.WIGGLER_GAP);
		SuggestionApplyButtonListener listener = new SuggestionApplyButtonListener(ScannableSetup.WIGGLER_GAP, lblWigglerSuggestion);
		Button applyButton = createMotorControl(motorSelectionComposite, listener);
		suggestionControls.put(applyButton, lblWigglerSuggestion);

		UIHelper.createMotorViewer(toolkit, motorSelectionComposite, ScannableSetup.WIGGLER_GAP, UIMotorControl.POSITION, moveObserver);

		lblSlitGapSuggestion = createSuggestionLabel(motorSelectionComposite, ScannableSetup.SLIT_1_HORIZONAL_GAP);
		listener = new SuggestionApplyButtonListener(ScannableSetup.SLIT_1_HORIZONAL_GAP, lblSlitGapSuggestion);
		applyButton = createMotorControl(motorSelectionComposite, listener);
		suggestionControls.put(applyButton, lblSlitGapSuggestion);
		UIHelper.createMotorViewer(toolkit, motorSelectionComposite, ScannableSetup.SLIT_1_HORIZONAL_GAP, UIMotorControl.POSITION, moveObserver);

		lblAtn1Suggestion = createSuggestionLabel(motorSelectionComposite, ScannableSetup.ATN1);
		listener = new SuggestionApplyButtonListener(ScannableSetup.ATN1, lblAtn1Suggestion);
		applyButton = createMotorControl(motorSelectionComposite, listener);
		suggestionControls.put(applyButton, lblAtn1Suggestion);
		UIHelper.createMotorViewer(toolkit, motorSelectionComposite, ScannableSetup.ATN1, UIMotorControl.ENUM, moveObserver);

		lblAtn2Suggestion = createSuggestionLabel(motorSelectionComposite, ScannableSetup.ATN2);
		listener = new SuggestionApplyButtonListener(ScannableSetup.ATN2, lblAtn2Suggestion);
		applyButton = createMotorControl(motorSelectionComposite, listener);
		suggestionControls.put(applyButton, lblAtn2Suggestion);
		UIHelper.createMotorViewer(toolkit, motorSelectionComposite, ScannableSetup.ATN2, UIMotorControl.ENUM, moveObserver);

		lblAtn3Suggestion = createSuggestionLabel(motorSelectionComposite, ScannableSetup.ATN3);
		listener = new SuggestionApplyButtonListener(ScannableSetup.ATN3, lblAtn3Suggestion);
		applyButton = createMotorControl(motorSelectionComposite, listener);
		suggestionControls.put(applyButton, lblAtn3Suggestion);
		UIHelper.createMotorViewer(toolkit, motorSelectionComposite, ScannableSetup.ATN3, UIMotorControl.ENUM, moveObserver);

		lblMe1StripSuggestion = createSuggestionLabel(motorSelectionComposite, ScannableSetup.ME1_STRIPE);
		listener = new SuggestionApplyButtonListener(ScannableSetup.ME1_STRIPE, lblMe1StripSuggestion);
		applyButton = createMotorControl(motorSelectionComposite, listener);
		suggestionControls.put(applyButton, lblMe1StripSuggestion);
		UIHelper.createMotorViewer(toolkit, motorSelectionComposite, ScannableSetup.ME1_STRIPE, UIMotorControl.ENUM, moveObserver);


		lblMe2StripSuggestion = createSuggestionLabel(motorSelectionComposite, ScannableSetup.ME2_STRIPE);
		listener = new SuggestionApplyButtonListener(ScannableSetup.ME2_STRIPE, lblMe2StripSuggestion);
		applyButton = createMotorControl(motorSelectionComposite, listener);
		suggestionControls.put(applyButton, lblMe2StripSuggestion);
		UIHelper.createMotorViewer(toolkit, motorSelectionComposite, ScannableSetup.ME2_STRIPE, UIMotorControl.ENUM, moveObserver);

		lblMe2PitchAngleSuggestion = createSuggestionLabel(motorSelectionComposite, ScannableSetup.ME2_PITCH_ANGLE);
		listener = new SuggestionApplyButtonListener(ScannableSetup.ME2_PITCH_ANGLE, lblMe2PitchAngleSuggestion);
		applyButton = createMotorControl(motorSelectionComposite, listener);
		suggestionControls.put(applyButton, lblMe2PitchAngleSuggestion);
		UIHelper.createMotorViewer(toolkit, motorSelectionComposite, ScannableSetup.ME2_PITCH_ANGLE, UIMotorControl.POSITION, moveObserver);

		lblPolyBender1Suggestion = createSuggestionLabel(motorSelectionComposite, ScannableSetup.POLY_BENDER_1);
		listener = new SuggestionApplyButtonListener(ScannableSetup.POLY_BENDER_1, lblPolyBender1Suggestion);
		applyButton = createMotorControl(motorSelectionComposite, listener);
		suggestionControls.put(applyButton, lblPolyBender1Suggestion);
		UIHelper.createMotorViewer(toolkit, motorSelectionComposite, ScannableSetup.POLY_BENDER_1, UIMotorControl.POSITION, moveObserver);

		lblPolyBender2Suggestion = createSuggestionLabel(motorSelectionComposite, ScannableSetup.POLY_BENDER_2);
		listener = new SuggestionApplyButtonListener(ScannableSetup.POLY_BENDER_2, lblPolyBender2Suggestion);
		applyButton = createMotorControl(motorSelectionComposite, listener);
		suggestionControls.put(applyButton, lblPolyBender2Suggestion);
		UIHelper.createMotorViewer(toolkit, motorSelectionComposite, ScannableSetup.POLY_BENDER_2, UIMotorControl.POSITION, moveObserver);

		final Button btnSynchroniseThetas = toolkit.createButton(motorSelectionComposite, "Match TwoTheta arm to Poly Bragg value", SWT.CHECK | SWT.WRAP);
		GridData gridData = new GridData(GridData.HORIZONTAL_ALIGN_BEGINNING);
		gridData.horizontalSpan = 4;
		btnSynchroniseThetas.setLayoutData(gridData);
		btnSynchroniseThetas.setSelection(true);

		lblPolyBraggSuggestion = createSuggestionLabel(motorSelectionComposite, ScannableSetup.POLY_BRAGG);
		listener = new LinkedSuggestionApplyButtonListener(ScannableSetup.POLY_BRAGG, lblPolyBraggSuggestion, btnSynchroniseThetas);
		applyButton = createMotorControl(motorSelectionComposite, listener);
		suggestionControls.put(applyButton, lblPolyBraggSuggestion);
		UIHelper.createMotorViewer(toolkit, motorSelectionComposite, ScannableSetup.POLY_BRAGG, UIMotorControl.ROTATION, moveObserver);

		((RotationViewer) ScannableSetup.POLY_BRAGG.getUiViewer()).addValueListener(new ValueListener() {
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

		lblArm2ThetaAngleSuggestion = createSuggestionLabel(motorSelectionComposite, ScannableSetup.ARM_2_THETA_ANGLE);
		listener = new SuggestionApplyButtonListener(ScannableSetup.ARM_2_THETA_ANGLE, lblArm2ThetaAngleSuggestion);
		applyButton = createMotorControl(motorSelectionComposite, listener);
		suggestionControls.put(applyButton, lblArm2ThetaAngleSuggestion);
		UIHelper.createMotorViewer(toolkit, motorSelectionComposite, ScannableSetup.ARM_2_THETA_ANGLE, UIMotorControl.ROTATION, moveObserver);

		Label labelTemperature = toolkit.createLabel(motorSelectionComposite, "Estimated power is: ");
		labelTemperature.setLayoutData(new GridData(GridData.HORIZONTAL_ALIGN_BEGINNING));
		labelTemperatureValue = toolkit.createFormText(motorSelectionComposite, false);
		labelTemperatureValue.setText(getPowerFormatedString(""), true, false);
		gridData = new GridData(GridData.HORIZONTAL_ALIGN_BEGINNING);
		gridData.horizontalSpan = 3;
		gridData.widthHint = POWER_LABEL_WIDTH;
		labelTemperatureValue.setLayoutData(gridData);

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(motorSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		motorSection.setSeparatorControl(defaultSectionSeparator);
	}

	private String getPowerFormatedString(String value) {
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


	private Button createMotorControl(Composite parent, SuggestionApplyButtonListener applySuggestionListener) {
		Button suggestionApplyButton = toolkit.createButton(parent, "", SWT.FLAT);
		suggestionApplyButton.addSelectionListener(applySuggestionListener);
		suggestionApplyButton.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_TOOL_FORWARD));
		suggestionApplyButton.setLayoutData(new GridData(GridData.BEGINNING, GridData.BEGINNING, false, false));
		return suggestionApplyButton;
	}

	private static class  LinkedSuggestionApplyButtonListener extends SuggestionApplyButtonListener {
		private final Button btnSynchroniseThetas;
		public LinkedSuggestionApplyButtonListener(ScannableSetup scannableSetup, Label suggestionLabel, Button btnSynchroniseThetas) {
			super(scannableSetup, suggestionLabel);
			this.btnSynchroniseThetas = btnSynchroniseThetas;
		}

		@Override
		public void widgetSelected(SelectionEvent event) {
			try {
				scannableSetup.getScannable().asynchronousMoveTo(suggestionLabel.getText());
				if (btnSynchroniseThetas.getSelection()) {
					if (event != null) {
						double thetaAngle = Double.parseDouble(suggestionLabel.getText()) * 2;
						try {
							ScannableSetup.ARM_2_THETA_ANGLE.getScannable().asynchronousMoveTo(thetaAngle);
						} catch (Exception e) {
							String errorMessage = "Error while applying " + ScannableSetup.ARM_2_THETA_ANGLE.getLabel() + " to " + thetaAngle;
							logger.error(errorMessage, e);
							UIHelper.showError(errorMessage, e.getMessage());
						}
					}
				}
			} catch (Exception e) {
				String errorMessage = "Exception while applying " + scannableSetup.getLabel() + " to " + suggestionLabel.getText();
				logger.error(errorMessage, e);
				UIHelper.showError(errorMessage, e.getMessage());
			}
		}
	}

	private static class SuggestionApplyButtonListener implements SelectionListener {
		protected final ScannableSetup scannableSetup;
		protected final Label suggestionLabel;
		public SuggestionApplyButtonListener(ScannableSetup scannableSetup, Label suggestionLabel) {
			this.scannableSetup = scannableSetup;
			this.suggestionLabel = suggestionLabel;
		}

		@Override
		public void widgetSelected(SelectionEvent event) {
			try {
				scannableSetup.getScannable().asynchronousMoveTo(scannableSetup.getUnit().removeUnitSuffix(suggestionLabel.getText()));
			} catch (Exception e) {
				String errorMessage = "Exception while applying " + scannableSetup.getLabel() + " to " + suggestionLabel.getText();
				logger.error(errorMessage, e);
				UIHelper.showError(errorMessage, e.getMessage());
			}
		}

		@Override
		public void widgetDefaultSelected(SelectionEvent event) {
			this.widgetSelected(event);
		}
	}

	private boolean powerWarningDialogShown = false;

	private void reportPowerEst(Double powerValue) {
		if (powerValue > ScannableSetup.MAX_POWER_IN_WATT) {
			String value = UnitSetup.WATT.addUnitSuffix("WARNING: Estimated power is " + powerValue);
			if (!powerWarningDialogShown) {
				UIHelper.showWarning("Power is above the maximum expected for operation", "Estimated power is " + value);
			}
			scrolledPolyForm.getForm().setMessage(value, IMessageProvider.ERROR);
			labelTemperatureValue.setText(getPowerFormatedString("WARNING: Estimated power is " + value), true, false);
			powerWarningDialogShown = true;
		} else {
			scrolledPolyForm.getForm().setMessage("");
			labelTemperatureValue.setText(getPowerFormatedString(""), true, false);
			powerWarningDialogShown = false;
		}
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
		spectrumSelectionComposite.setLayout(new GridLayout(4, false));
		spectrumSection.setClient(spectrumSelectionComposite);

		toolkit.createLabel(spectrumSelectionComposite, ""); // Place holder
		toolkit.createLabel(spectrumSelectionComposite, "Calculated");
		toolkit.createLabel(spectrumSelectionComposite, ""); // Place holder
		toolkit.createLabel(spectrumSelectionComposite, "Motor Readback");

		lblDetectorHeightSuggestion = createSuggestionLabel(spectrumSelectionComposite, ScannableSetup.DETECTOR_HEIGHT);
		SuggestionApplyButtonListener listener = new SuggestionApplyButtonListener(ScannableSetup.DETECTOR_HEIGHT, lblDetectorHeightSuggestion);
		Button applyButton = createMotorControl(spectrumSelectionComposite, listener);
		suggestionControls.put(applyButton, lblDetectorHeightSuggestion);
		UIHelper.createMotorViewer(toolkit, spectrumSelectionComposite, ScannableSetup.DETECTOR_HEIGHT, UIMotorControl.POSITION, moveObserver);

		lblDetectorDistanceSuggestion = createSuggestionLabel(spectrumSelectionComposite, ScannableSetup.DETECTOR_DISTANCE);
		listener = new SuggestionApplyButtonListener(ScannableSetup.DETECTOR_DISTANCE, lblDetectorDistanceSuggestion);
		applyButton = createMotorControl(spectrumSelectionComposite, listener);
		suggestionControls.put(applyButton, lblDetectorDistanceSuggestion);
		UIHelper.createMotorViewer(toolkit, spectrumSelectionComposite, ScannableSetup.DETECTOR_DISTANCE, UIMotorControl.POSITION, moveObserver);

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(spectrumSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		spectrumSection.setSeparatorControl(defaultSectionSeparator);
	}

	// TODO Use data binding
	private void clearSuggestionValues() {
		for (Entry<Button, Label> suggestionButton : suggestionControls.entrySet()) {
			suggestionButton.getKey().setVisible(false);
			suggestionButton.getValue().setText(SUGGESTION_UNAVAILABLE_TEXT);
		}
	}

	private void showSuggestionValues(final AlignmentParametersBean results) {
		PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
			@Override
			public void run() {
				for (Entry<Button, Label> suggestionButton : suggestionControls.entrySet()) {
					suggestionButton.getKey().setVisible(true);
				}
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
				lblDetectorDistanceSuggestion.setText(ClientConfig.roundDoubletoString(results.getDetectorDistance() * 1000)); // Convert to mm
				lblDetectorHeightSuggestion.setText(ClientConfig.roundDoubletoString(results.getDetectorHeight())); // FIXME Why not convert for this one?

				lblAtn1Suggestion.setText(results.getAtn1().toString());
				lblAtn2Suggestion.setText(results.getAtn2().toString());
				lblAtn3Suggestion.setText(results.getAtn3().toString());

				reportPowerEst(results.getPower());
			}
		});
	}

	@SuppressWarnings({ "unused", "static-access" })
	private void createTempratureSection(Form form) {
		final Section temperatureSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		temperatureSection.setText("Temperature");
		temperatureSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		final Composite temperatureSelectionComposite = toolkit.createComposite(temperatureSection, SWT.NONE);
		toolkit.paintBordersFor(temperatureSelectionComposite);
		final TableColumnLayout layout = new TableColumnLayout();
		temperatureSelectionComposite.setLayout(layout);
		temperatureSection.setClient(temperatureSelectionComposite);


		ToolBar temperatureSectionTbar = new ToolBar(temperatureSection, SWT.FLAT | SWT.HORIZONTAL);
		new ToolItem(temperatureSectionTbar, SWT.SEPARATOR);
		ToolItem refreshTemperatureTBarItem = new ToolItem(temperatureSectionTbar, SWT.NULL);
		refreshTemperatureTBarItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ELCL_SYNCED));
		refreshTemperatureTBarItem.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				createTempTable(temperatureSelectionComposite, layout);
				temperatureSection.layout();
			}
		});
		temperatureSection.setTextClient(temperatureSectionTbar);
		createTempTable(temperatureSelectionComposite, layout);
		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(temperatureSection),
				BeanProperties.value(DetectorConfig.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorConfig.INSTANCE));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(refreshTemperatureTBarItem),
				BeanProperties.value(DetectorConfig.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorConfig.INSTANCE));

		DetectorConfig.INSTANCE.addPropertyChangeListener(DetectorConfig.DETECTOR_CONNECTED_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if ((boolean) evt.getNewValue()) {
					createTempTable(temperatureSelectionComposite, layout);
					temperatureSection.layout();
				}
			}
		});
	}

	private Table temperatureTable;

	private void createTempTable(Composite parent, TableColumnLayout layout) {
		if (temperatureTable != null && !temperatureTable.isDisposed()) {
			temperatureTable.dispose();
			temperatureTable = null;
		}
		temperatureTable = toolkit.createTable(parent, SWT.NONE);
		temperatureTable.setLinesVisible (true);
		temperatureTable.setHeaderVisible (true);
		temperatureTable.setLayoutData(new TableWrapData());
		// TODO Refactor to allow ccd
		Map<String, Double> temperatureValues;
		try {
			temperatureValues = ((XCHIPDetector) DetectorConfig.INSTANCE.getCurrentDetector()).getTemperatures();
			if (!temperatureValues.isEmpty()) {
				int weight = 100 / temperatureValues.size();
				String[] values = new String[temperatureValues.size()];
				int i = 0;
				for (Map.Entry<String,Double> entry : temperatureValues.entrySet()) {
					TableColumn column = new TableColumn (temperatureTable, SWT.NONE);
					layout.setColumnData(column, new ColumnWeightData(weight));
					column.setText(entry.getKey());
					values[i++] = Double.toString(entry.getValue());
				}
				TableItem item = new TableItem (temperatureTable, SWT.NONE);
				item.setText(values);
			}
		} catch (DeviceException e) {
			UIHelper.showError("Unable to show temperature readings", e.getMessage());
		}
	}

	@Override
	public void setFocus() {
	}

	@Override
	public String getContributorId() {
		return this.getSite().getId();
	}
}
