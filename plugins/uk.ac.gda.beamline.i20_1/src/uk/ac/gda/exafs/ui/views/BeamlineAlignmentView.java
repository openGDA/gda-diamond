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
import gda.observable.IObserver;
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
import org.eclipse.jface.viewers.LabelProvider;
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

import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.exafs.data.AlignmentParametersBean;
import uk.ac.gda.exafs.data.AlignmentParametersModel;
import uk.ac.gda.exafs.data.AlignmentParametersModel.CrystalCut;
import uk.ac.gda.exafs.data.AlignmentParametersModel.CrystalType;
import uk.ac.gda.exafs.data.AlignmentParametersModel.QValue;
import uk.ac.gda.exafs.data.ClientConfig.ScannableSetup;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.PowerCalulator;
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

	private static final String SUGGESTION_UNAVAILABLE_TEXT = "-";

	public static String ID = "uk.ac.gda.exafs.ui.views.beamlinealignmentview";

	private static Logger logger = LoggerFactory.getLogger(BeamlineAlignmentView.class);

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private ComboViewer comboCrystalCut;
	private ComboViewer comboCrystalType;
	private ComboViewer comboxElement;
	private ComboViewer comboElementEdge;
	private ComboViewer comboCrystalQ;
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
	private FormText labelDeltaEValueSuggestion;

	private final Map<Button, Label> suggestionControls = new HashMap<Button, Label>();
	private final WritableList movingScannables = new WritableList(new ArrayList<Scannable>(), Scannable.class);
	private final ScannableMotorMoveObserver moveObserver = new ScannableMotorMoveObserver(movingScannables);
	private Label energyLabel;
	private Button butDetectorSetup;

	private Binding detectorValueBinding = null;
	private FormText labelDeltaEValue;
	private Binding test;

	@Override
	public void createPartControl(final Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		scrolledPolyForm = toolkit.createScrolledForm(parent);
		TableWrapLayout layout = new TableWrapLayout();
		scrolledPolyForm.getBody().setLayout(layout);
		toolkit.decorateFormHeading(scrolledPolyForm.getForm());
		scrolledPolyForm.setText("Configuration");
		try {
			createMainControls(scrolledPolyForm.getForm());
			createMotorControls(scrolledPolyForm.getForm());
			bindFiltersForPowerCalculation();
			bindModelWithUI();
			updatePower();
		} catch (Exception e) {
			UIHelper.showError("Unable to create motor controls", e.getMessage());
			logger.error("Unable to create motor controls", e);
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
		GridLayout gridLayout = UIHelper.createGridLayoutWithNoMargin(2, false);
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

		butDetectorSetup = toolkit.createButton(detectorConfigComposite, "Setup", SWT.FLAT);
		butDetectorSetup.setLayoutData(new GridData(GridData.HORIZONTAL_ALIGN_END));

		Label lblCrystalType = toolkit.createLabel(mainSelectionComposite, "Crytal type:", SWT.NONE);
		lblCrystalType.setLayoutData(createLabelGridData());
		comboCrystalType = new ComboViewer(new CCombo(mainSelectionComposite, SWT.READ_ONLY));
		comboCrystalType.setContentProvider(ArrayContentProvider.getInstance());
		comboCrystalType.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object element) {
				return ((CrystalType) element).name();
			}
		});
		comboCrystalType.setInput(new CrystalType[]{ CrystalType.Bragg });
		comboCrystalType.getCCombo().setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		Label lblCrystalCut = toolkit.createLabel(mainSelectionComposite, CrystalCut.UI_LABEL, SWT.NONE);
		lblCrystalCut.setLayoutData(createLabelGridData());
		comboCrystalCut = new ComboViewer(new CCombo(mainSelectionComposite, SWT.READ_ONLY));
		comboCrystalCut.setContentProvider(ArrayContentProvider.getInstance());
		comboCrystalCut.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object element) {
				return ((CrystalCut) element).name();
			}
		});
		comboCrystalCut.setInput(CrystalCut.values());
		comboCrystalCut.getCCombo().setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		Label lblCrystalQ = toolkit.createLabel(mainSelectionComposite, "Crystal q:", SWT.NONE);
		lblCrystalQ.setLayoutData(createLabelGridData());
		comboCrystalQ = new ComboViewer(new CCombo(mainSelectionComposite, SWT.READ_ONLY));
		comboCrystalQ.setContentProvider(new ArrayContentProvider());
		comboCrystalQ.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object value) {
				return Double.toString(((QValue) value).getQValue());
			}
		});
		comboCrystalQ.setInput(QValue.values());
		comboCrystalQ.getCCombo().setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		Label lbl = toolkit.createLabel(mainSelectionComposite, "Element:", SWT.NONE);
		lbl.setLayoutData(createLabelGridData());
		comboxElement = new ComboViewer(new CCombo(mainSelectionComposite, SWT.READ_ONLY));
		comboxElement.getCCombo().setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		comboxElement.setContentProvider(new ArrayContentProvider());
		comboxElement.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object value) {
				if (value == null) {
					return "";
				}
				Element element = (Element) value;
				return element.getName() + " (" + element.getSymbol() + ")";
			}
		});

		lbl = toolkit.createLabel(mainSelectionComposite, "Edge:", SWT.NONE);
		lbl.setLayoutData(createLabelGridData());
		comboElementEdge = new ComboViewer(new CCombo(mainSelectionComposite, SWT.READ_ONLY));
		comboElementEdge.getCCombo().setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		comboElementEdge.setContentProvider(ArrayContentProvider.getInstance());

		lbl = toolkit.createLabel(mainSelectionComposite, "Energy:", SWT.NONE);
		lbl.setLayoutData(createLabelGridData());
		energyLabel = toolkit.createLabel(mainSelectionComposite, "", SWT.BORDER);
		energyLabel.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		comboElementEdge.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object element) {
				return (String) element;
			}
		});

		if (DetectorModel.INSTANCE.isDetectorConnected()) {
			final StructuredSelection initialSelection = new StructuredSelection(CrystalCut.Si111);
			comboCrystalCut.setSelection(initialSelection);
		}

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(mainSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		mainSection.setSeparatorControl(defaultSectionSeparator);
	}

	private void updatePower() {
		Display.getDefault().asyncExec(new Runnable() {
			@Override
			public void run() {
				try {
					double wigglerGap = (double) ScannableSetup.WIGGLER_GAP.getScannable().getPosition();
					double slitHGap = (double) ScannableSetup.SLIT_1_HORIZONAL_GAP.getScannable().getPosition();
					final int powerValue = (int) PowerCalulator.getPower(PowerCalulator.REF_DATA_PATH, wigglerGap, slitHGap, 300);
					String powerWatt = UnitSetup.WATT.addUnitSuffix(Integer.toString(powerValue));
					if (powerValue > ScannableSetup.MAX_POWER_IN_WATT) {
						String value ="Estimated power is " + powerWatt;
						scrolledPolyForm.getForm().setMessage(value, IMessageProvider.ERROR);
					} else {
						scrolledPolyForm.getForm().setMessage("");
					}
					labelPowerEstimateValue.setText(getHighlightedFormatedString(powerWatt), true, false);
				} catch (Exception e) {
					labelPowerEstimateValue.setText(
							getHighlightedFormatedString("Unable to calculate with current parameters"), true, false);
				}
			}
		});
	}

	private class BeamLightFilterPowerUpdate implements IObserver{
		private String value = "";
		@Override
		public void update(Object source, Object arg) {
			if (arg instanceof String && !value.equals(arg)) {
				updatePower();
				value = (String) arg;
			}
		}
	}

	private void bindFiltersForPowerCalculation() throws Exception {
		ScannableSetup.ATN1.getScannable().addIObserver(new BeamLightFilterPowerUpdate());
		ScannableSetup.ATN2.getScannable().addIObserver(new BeamLightFilterPowerUpdate());
		ScannableSetup.ATN3.getScannable().addIObserver(new BeamLightFilterPowerUpdate());
		ScannableSetup.ME1_STRIPE.getScannable().addIObserver(new BeamLightFilterPowerUpdate());
		ScannableSetup.ME2_STRIPE.getScannable().addIObserver(new BeamLightFilterPowerUpdate());
	}

	private void bindModelWithUI() {
		try {
			dataBindingCtx.bindValue(
					WidgetProperties.enabled().observe(butDetectorSetup),
					BeanProperties.value(DetectorModel.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorModel.INSTANCE));

			dataBindingCtx.bindValue(
					WidgetProperties.enabled().observe(comboxElement.getControl()),
					BeanProperties.value(DetectorModel.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorModel.INSTANCE));

			dataBindingCtx.bindValue(
					ViewersObservables.observeInput(comboxElement),
					BeanProperties.value(AlignmentParametersModel.ELEMENTS_IN_ENERGY_RANGE_PROP_NAME).observe(AlignmentParametersModel.INSTANCE), null,
					new UpdateValueStrategy() {

						@Override
						protected IStatus doSet(IObservableValue observableValue, Object value) {

							return super.doSet(observableValue, value);
						}
					});

			test = dataBindingCtx.bindValue(
					ViewersObservables.observeSingleSelection(comboxElement),
					BeanProperties.value(AlignmentParametersModel.ELEMENT_PROP_NAME).observe(AlignmentParametersModel.INSTANCE), null,
					new UpdateValueStrategy() {

						@Override
						protected IStatus doSet(IObservableValue observableValue, Object value) {
							return super.doSet(observableValue, value);
						}
					});

			AlignmentParametersModel.INSTANCE.addPropertyChangeListener(AlignmentParametersModel.ELEMENT_PROP_NAME, new PropertyChangeListener() {

				@Override
				public void propertyChange(PropertyChangeEvent evt) {
					//			test.updateModelToTarget();
				}
			});

			dataBindingCtx.bindValue(
					WidgetProperties.enabled().observe(comboElementEdge.getControl()),
					BeanProperties.value(DetectorModel.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorModel.INSTANCE));

			dataBindingCtx.bindValue(
					ViewersObservables.observeInput(comboElementEdge),
					BeanProperties.value(AlignmentParametersModel.ELEMENT_EDGES_NAMES_PROP_NAME).observe(AlignmentParametersModel.INSTANCE));

			dataBindingCtx.bindValue(
					ViewersObservables.observeSingleSelection(comboElementEdge),
					BeanProperties.value(AlignmentParametersModel.ELEMENT_EDGE_PROP_NAME).observe(AlignmentParametersModel.INSTANCE),
					new UpdateValueStrategy() {
						@Override
						public Object convert(Object value) {
							if (AlignmentParametersModel.INSTANCE.getElement() != null) {
								// TODO refactor this
								return AlignmentParametersModel.INSTANCE.getElement().getEdge((String) value);
							}
							return null;
						}
					},
					new UpdateValueStrategy() {
						@Override
						public Object convert(Object value) {
							return ((AbsorptionEdge) value).getEdgeType();
						}
					});

			dataBindingCtx.bindValue(
					ViewersObservables.observeSingleSelection(comboCrystalQ),
					BeanProperties.value(AlignmentParametersModel.Q_PROP_NAME).observe(AlignmentParametersModel.INSTANCE));

			dataBindingCtx.bindValue(
					WidgetProperties.enabled().observe(comboCrystalCut.getControl()),
					BeanProperties.value(DetectorModel.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorModel.INSTANCE));

			dataBindingCtx.bindValue(
					ViewersObservables.observeSingleSelection(comboCrystalCut),
					BeanProperties.value(AlignmentParametersModel.CRYSTAL_CUT_PROP_NAME).observe(AlignmentParametersModel.INSTANCE));

			dataBindingCtx.bindValue(
					ViewersObservables.observeSingleSelection(comboCrystalType),
					BeanProperties.value(AlignmentParametersModel.CRYSTAL_TYPE_PROP_NAME).observe(AlignmentParametersModel.INSTANCE));

			dataBindingCtx.bindValue(
					WidgetProperties.enabled().observe(comboCrystalQ.getControl()),
					BeanProperties.value(DetectorModel.DETECTOR_CONNECTED_PROP_NAME).observe(DetectorModel.INSTANCE));

			dataBindingCtx.bindValue(
					ViewersObservables.observeSingleSelection(comboCrystalQ),
					BeanProperties.value(AlignmentParametersModel.Q_PROP_NAME).observe(AlignmentParametersModel.INSTANCE));

			dataBindingCtx.bindValue(
					WidgetProperties.text().observe(energyLabel),
					BeanProperties.value(AlignmentParametersModel.ELEMENT_ENERGY_PROP_NAME).observe(AlignmentParametersModel.INSTANCE),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
					new UpdateValueStrategy() {
						@Override
						public Object convert(Object value) {
							return UnitSetup.EV.addUnitSuffix(Double.toString((double) value));
						}
					});

			butDetectorSetup.addListener(SWT.Selection, new Listener() {
				@Override
				public void handleEvent(Event event) {
					DetectorSetupDialog setup = new DetectorSetupDialog(Display.getDefault().getActiveShell());
					setup.setBlockOnOpen(true);
					setup.open();
				}
			});

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

			AlignmentParametersModel.INSTANCE.addPropertyChangeListener(AlignmentParametersModel.AUGGESTED_PARAMETERS_PROP_KEY, new PropertyChangeListener() {
				@Override
				public void propertyChange(PropertyChangeEvent evt) {
					updateAlignmentParametersSuggestion((AlignmentParametersBean) evt.getNewValue());
				}
			});

			updateAlignmentParametersSuggestion(AlignmentParametersModel.INSTANCE.getAlignmentSuggestedParameters());
		} catch (Exception e) {
			UIHelper.showError("Unable to setup detectors", "Error while retrieving available detectors");
			logger.error("Error while retrieving available detectors", e);
		}
	}

	private void updateAlignmentParametersSuggestion(AlignmentParametersBean result) {
		if (result != null) {
			showSuggestionValues(result);
		}
	}

	private void revertToModel() {
		if (detectorValueBinding != null) {
			detectorValueBinding.updateModelToTarget();
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
		ScannableWrapper scannableWrapper = ScannableSetup.WIGGLER_GAP.getScannableWrapper();
		scannableWrapper.addPropertyChangeListener(ScannableWrapper.POSITION_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				updatePower();
			}
		});
		MotorPositionEditorControl motorPositionEditorControl = new MotorPositionEditorControl(motorSectionComposite, SWT.None, scannableWrapper, true);

		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		applyButton.addListener(SWT.Selection, new SuggestionApplyButtonListener(ScannableSetup.WIGGLER_GAP, lblWigglerSuggestion, motorPositionEditorControl));

		lblSlitGapSuggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.SLIT_1_HORIZONAL_GAP);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblSlitGapSuggestion);

		scannable = ScannableSetup.SLIT_1_HORIZONAL_GAP.getScannable();
		scannable.addIObserver(moveObserver);
		scannableWrapper = ScannableSetup.SLIT_1_HORIZONAL_GAP.getScannableWrapper();
		scannableWrapper.addPropertyChangeListener(ScannableWrapper.POSITION_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				updatePower();
			}
		});
		motorPositionEditorControl = new MotorPositionEditorControl(motorSectionComposite, SWT.None, scannableWrapper, true);
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
					String errorMessage = "Exception setting motor to " + lblAtn1Suggestion.getText();
					UIHelper.showError(errorMessage, e.getMessage());
					logger.error(errorMessage, e);
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
					String errorMessage = "Exception setting motor to " + lblAtn2Suggestion.getText();
					UIHelper.showError(errorMessage, e.getMessage());
					logger.error(errorMessage, e);
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
					String errorMessage = "Exception setting motor to " + lblAtn3Suggestion.getText();
					UIHelper.showError(errorMessage, e.getMessage());
					logger.error(errorMessage);
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
					String errorMessage = "Exception setting motor to " + lblMe1StripSuggestion.getText();
					UIHelper.showError(errorMessage, e.getMessage());
					logger.error(errorMessage, e);
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
					String errorMessage = "Exception setting motor to " + lblMe2StripSuggestion.getText();
					UIHelper.showError(errorMessage, e.getMessage());
					logger.error(errorMessage, e);
				}
			}
		});

		lblMe2PitchAngleSuggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.ME2_PITCH_ANGLE);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblMe2PitchAngleSuggestion);

		scannable = ScannableSetup.ME2_PITCH_ANGLE.getScannable();
		// TODO Add remove observers on dispose
		scannable.addIObserver(moveObserver);
		scannableWrapper = ScannableSetup.ME2_PITCH_ANGLE.getScannableWrapper();
		scannableWrapper.addPropertyChangeListener(ScannableWrapper.POSITION_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				updatePower();
			}
		});

		motorPositionEditorControl = new MotorPositionEditorControl(motorSectionComposite, SWT.None, scannableWrapper, true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		applyButton.addListener(SWT.Selection, new SuggestionApplyButtonListener(ScannableSetup.ME2_PITCH_ANGLE, lblMe2PitchAngleSuggestion, motorPositionEditorControl));

		lblPolyBender1Suggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.POLY_BENDER_1);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblPolyBender1Suggestion);

		scannable = ScannableSetup.POLY_BENDER_1.getScannable();
		scannable.addIObserver(moveObserver);
		motorPositionEditorControl = new MotorPositionEditorControl(motorSectionComposite, SWT.None, ScannableSetup.POLY_BENDER_1.getScannableWrapper(), true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		applyButton.addListener(SWT.Selection, new SuggestionApplyButtonListener(ScannableSetup.POLY_BENDER_1, lblPolyBender1Suggestion, motorPositionEditorControl));

		lblPolyBender2Suggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.POLY_BENDER_2);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblPolyBender2Suggestion);

		scannable = ScannableSetup.POLY_BENDER_2.getScannable();
		scannable.addIObserver(moveObserver);
		motorPositionEditorControl = new MotorPositionEditorControl(motorSectionComposite, SWT.None, ScannableSetup.POLY_BENDER_2.getScannableWrapper(), true);
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
		//TODO Refactor to create singleton
		BraggAngleAndTwoThetaScannableWrapper braggAngleScannableWrapper = new BraggAngleAndTwoThetaScannableWrapper(scannable, btnSynchroniseThetas);
		motorPositionEditorControl = new MotorPositionEditorControl(motorSectionComposite, SWT.None, braggAngleScannableWrapper, true);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		applyButton.addListener(SWT.Selection, new SuggestionApplyButtonListener(ScannableSetup.POLY_BRAGG, lblPolyBraggSuggestion, motorPositionEditorControl));

		lblArm2ThetaAngleSuggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.ARM_2_THETA_ANGLE);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblArm2ThetaAngleSuggestion);

		scannable = ScannableSetup.ARM_2_THETA_ANGLE.getScannable();
		scannable.addIObserver(moveObserver);
		//TODO Refactor to create singleton
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
		motorPositionEditorControl = new MotorPositionEditorControl(motorSectionComposite, SWT.None, ScannableSetup.DETECTOR_HEIGHT.getScannableWrapper(), true);
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
								//								getScannableValuesSuggestion();
							}
						}
						@Override
						public void handleAdd(int index, Object element) {}
					});
				}
			});
		} catch (Exception e) {
			UIHelper.showError("Unable to find detector details", e.getMessage());
			logger.error("Unable to find detector details", e);
		}

		lblDetectorDistanceSuggestion = createSuggestionLabel(motorSectionComposite, ScannableSetup.DETECTOR_DISTANCE);
		applyButton = createMotorControl(motorSectionComposite);
		suggestionControls.put(applyButton, lblDetectorDistanceSuggestion);

		scannable = ScannableSetup.DETECTOR_DISTANCE.getScannable();
		scannable.addIObserver(moveObserver);
		motorPositionEditorControl = new MotorPositionEditorControl(motorSectionComposite, SWT.None, ScannableSetup.DETECTOR_DISTANCE.getScannableWrapper(), true);
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
						double valueTimes2 = value * 2;
						if (valueTimes2 != otherScannableEditorControl.getPosition()) {
							otherScannableEditorControl.setPosition(valueTimes2);
						}
					} else {
						double valueTimesHalf = value / 2;
						if (valueTimesHalf != otherScannableEditorControl.getPosition()) {
							otherScannableEditorControl.setPosition(valueTimesHalf);
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

	private void showSuggestionValues(final AlignmentParametersBean results) {
		PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
			@Override
			public void run() {
				lblWigglerSuggestion.setText(ScannableSetup.WIGGLER_GAP.getUnit().addUnitSuffix(DataHelper.roundDoubletoString(results.getWigglerGap())));
				lblPolyBender1Suggestion.setText(ScannableSetup.POLY_BENDER_1.getUnit().addUnitSuffix(DataHelper.roundDoubletoString(results.getPolyBend1())));
				lblPolyBender2Suggestion.setText(ScannableSetup.POLY_BENDER_2.getUnit().addUnitSuffix(DataHelper.roundDoubletoString(results.getPolyBend2())));
				lblMe1StripSuggestion.setText(results.getMe1stripe());
				lblMe2StripSuggestion.setText(results.getMe2stripe());
				lblSlitGapSuggestion.setText(ScannableSetup.SLIT_1_HORIZONAL_GAP.getUnit().addUnitSuffix(DataHelper.roundDoubletoString(results.getPrimarySlitGap())));
				lblArm2ThetaAngleSuggestion.setText(ScannableSetup.ARM_2_THETA_ANGLE.getUnit().addUnitSuffix(DataHelper.roundDoubletoString(results.getArm2Theta())));
				lblPolyBraggSuggestion.setText(ScannableSetup.POLY_BRAGG.getUnit().addUnitSuffix(DataHelper.roundDoubletoString(results.getBraggAngle())));
				lblMe2PitchAngleSuggestion.setText(ScannableSetup.ME2_PITCH_ANGLE.getUnit().addUnitSuffix(DataHelper.roundDoubletoString(results.getMe2Pitch())));

				// TODO Check if this value is correct
				// FIXME Conversion shouldn't not be done in this UI section
				lblDetectorDistanceSuggestion.setText(ScannableSetup.DETECTOR_DISTANCE.getUnit().addUnitSuffix(DataHelper.roundDoubletoString(results.getDetectorDistance() * 1000))); // Convert to mm
				lblDetectorHeightSuggestion.setText(ScannableSetup.DETECTOR_HEIGHT.getUnit().addUnitSuffix(DataHelper.roundDoubletoString(results.getDetectorHeight())));

				lblAtn1Suggestion.setText(results.getAtn1().toString());
				lblAtn2Suggestion.setText(results.getAtn2().toString());
				lblAtn3Suggestion.setText(results.getAtn3().toString());

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
