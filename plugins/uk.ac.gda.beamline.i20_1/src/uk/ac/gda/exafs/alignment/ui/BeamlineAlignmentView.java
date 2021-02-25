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

package uk.ac.gda.exafs.alignment.ui;

import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.dawnsci.ede.DataHelper;
import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.core.databinding.observable.value.IObservableValue;
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

import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.Scannable;
import gda.device.detector.EdeDetector;
import gda.factory.Findable;
import gda.factory.Finder;
import gda.observable.IObserver;
import gda.util.exafs.AbsorptionEdge;
import gda.util.exafs.Element;
import uk.ac.gda.beamline.i20_1.Activator;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.composites.MotorPositionEditorControl;
import uk.ac.gda.exafs.data.AlignmentParametersBean;
import uk.ac.gda.exafs.data.AlignmentParametersModel;
import uk.ac.gda.exafs.data.AlignmentParametersModel.CrystalCut;
import uk.ac.gda.exafs.data.AlignmentParametersModel.CrystalType;
import uk.ac.gda.exafs.data.AlignmentParametersModel.QValue;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.PowerCalulator;
import uk.ac.gda.exafs.data.ScannableSetup;
import uk.ac.gda.exafs.ui.data.ScannableMotorMoveObserver;
import uk.ac.gda.ui.viewer.EnumPositionViewer;

/**
 * Has controls for operating the lookuptable matching optics positions to energy
 */
public class BeamlineAlignmentView extends ViewPart implements ITabbedPropertySheetPageContributor {

	public static String ID = "uk.ac.gda.exafs.ui.views.beamlinealignmentview";
	public static final String ENABLE_CONTROLS_PROPERTY = "uk.ac.gda.exafs.alignment.ui.enablecontrols";

	private static final int LABEL_WIDTH = 125;
	private static final int SUGGESTION_LABEL_WIDTH = 100;

	private static final String SUGGESTION_UNAVAILABLE_TEXT = "-";

	private static Logger logger = LoggerFactory.getLogger(BeamlineAlignmentView.class);

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private ComboViewer comboCrystalCut;
	private ComboViewer comboCrystalType;
	private ComboViewer comboxElement;
	private ComboViewer comboElementEdge;
	private ComboViewer comboCrystalQ;
	private ComboViewer cmbDetectorType;
	private Button butDetectorConnect;

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

	private final WritableList<Scannable> movingScannables = new WritableList<>(new ArrayList<>(), Scannable.class);
	private final ScannableMotorMoveObserver moveObserver = new ScannableMotorMoveObserver(movingScannables);
	private Label energyLabel;
	private Button butDetectorSetup;

	private final Binding detectorValueBinding = null;
	private FormText labelDeltaEValue;

	/** Set to false to disable gui controls; widgets will still update to show current scannable values */
	private boolean controlsEnabled;

	@Override
	public void createPartControl(final Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		scrolledPolyForm = toolkit.createScrolledForm(parent);
		TableWrapLayout layout = new TableWrapLayout();
		scrolledPolyForm.getBody().setLayout(layout);
		toolkit.decorateFormHeading(scrolledPolyForm.getForm());
		scrolledPolyForm.setText("Configuration");

		controlsEnabled = Activator.getDefault().getPreferenceStore().getBoolean(ENABLE_CONTROLS_PROPERTY);

		try {
			createMainControls(scrolledPolyForm.getForm());
			createMotorControls(scrolledPolyForm.getForm());
			bindFiltersForPowerCalculation();
			bindModelWithUI();
			updatePower();
			AlignmentParametersModel.INSTANCE.loadAlignmentParametersFromStore();
			initialiseUI();
		} catch (Exception e) {
			UIHelper.showError("Unable to create motor controls", e.getMessage());
			logger.error("Unable to create motor controls", e);
		}
	}


	private void initialiseUI() {
		// Set crystal cut, Q and element edge combos manually (not automatically updated by binding)
		comboCrystalCut.setSelection( new StructuredSelection( AlignmentParametersModel.INSTANCE.getCrystalCut() ) );
		comboCrystalQ.setSelection( new StructuredSelection( AlignmentParametersModel.INSTANCE.getQ()) );
		comboElementEdge.setSelection( new StructuredSelection( AlignmentParametersModel.INSTANCE.getEdge().getEdgeType()) );

		cmbDetectorType.setSelection(new StructuredSelection(DetectorModel.INSTANCE.getCurrentDetector()));
		cmbDetectorType.addSelectionChangedListener( event -> {
			if (event != null && !event.getSelection().isEmpty()) {
				String text = cmbDetectorType.getCombo().getText();
				Findable detector = Finder.find(text);
				logger.debug("Detector name changed to {}", text);
				if (detector != null && detector instanceof EdeDetector) {
					EdeDetector edeDetector = (EdeDetector) detector;
					logger.debug("Setting EdeDetector object, configured = {}", edeDetector.isConfigured());
					DetectorModel.INSTANCE.setCurrentDetector(edeDetector);
				}
			}
		});

		// Try to (re)configure selected detector
		butDetectorConnect.addListener( SWT.Selection, listener -> {
			EdeDetector detector = DetectorModel.INSTANCE.getCurrentDetector();
			// Check really want to conf. detector.
			String message = "Are you sure you want to try and configure " + detector.getName() + "?";
			if (detector.isConfigured()) {
				message += "\n(It is already configured)";
			}
			boolean runConfigure = MessageDialog.openQuestion(butDetectorConnect.getShell(), "Configure detector", message);

			if (runConfigure) {
				logger.debug("Attempting to reconfigure detector {}", detector.getName());
				ConnectDeviceDialog connectionDialog = new ConnectDeviceDialog(butDetectorConnect.getShell());
				connectionDialog.setDetector(detector);
				connectionDialog.setBlockOnOpen(true);
				// need to try with hardware to find realistic timeout value (xh is slow to configure...)
				// Might need to use different value for different detectors.
				connectionDialog.setMaxExpectedConfigureTimeSecs(20);
				connectionDialog.open();
				if (detector.isConfigured()) {
					DetectorModel.INSTANCE.setCurrentDetector(detector);
				}
			}
		});
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
		GridLayout gridLayout = UIHelper.createGridLayoutWithNoMargin(3, false);
		detectorConfigComposite.setLayout(gridLayout);
		cmbDetectorType =  new ComboViewer(detectorConfigComposite, SWT.READ_ONLY);
		cmbDetectorType.setContentProvider(ArrayContentProvider.getInstance());
		cmbDetectorType.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object element) {
				return ((EdeDetector) element).getName();
			}
		});
		cmbDetectorType.getCombo().setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		toolkit.paintBordersFor(detectorConfigComposite);

		butDetectorConnect = toolkit.createButton(detectorConfigComposite, "Connect", SWT.FLAT);
		butDetectorConnect.setLayoutData(new GridData(GridData.HORIZONTAL_ALIGN_END));

		butDetectorSetup = toolkit.createButton(detectorConfigComposite, "Setup", SWT.FLAT);
		butDetectorSetup.setLayoutData(new GridData(GridData.HORIZONTAL_ALIGN_END));

		Label lblCrystalType = toolkit.createLabel(mainSelectionComposite, "Crystal type:", SWT.NONE);
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
		Display.getDefault().asyncExec(() -> {
			try {
				double wigglerGap = (double) ScannableSetup.WIGGLER_GAP.getScannable().getPosition();
				double slitHGap = (double) ScannableSetup.SLIT_1_HORIZONAL_GAP.getScannable().getPosition();
				logger.debug("Update power : wiggler gap = {}, slit gap = {}", wigglerGap, slitHGap);
				final double powerValue = PowerCalulator.getPower(wigglerGap, slitHGap, 300);
				String powerWatt = UnitSetup.WATT.addUnitSuffix(String.format("%4f", powerValue));
				if (powerValue > ScannableSetup.MAX_POWER_IN_WATT) {
					String value ="Estimated power is " + powerWatt;
					scrolledPolyForm.getForm().setMessage(value, IMessageProvider.ERROR);
				} else {
					scrolledPolyForm.getForm().setMessage("");
				}
				labelPowerEstimateValue.setText(getHighlightedFormatedString(powerWatt), true, false);
			} catch (FileNotFoundException e1) {
				labelPowerEstimateValue.setText(
						getHighlightedFormatedString("Unable to calculate with current parameters"), true, false);
				logger.warn("Power calculation file not found", e1);
			} catch (Exception e2) {
				labelPowerEstimateValue.setText(
						getHighlightedFormatedString("Unable to calculate with current parameters"), true, false);
				logger.error("Unable to calculate with current parameters", e2);
			}
		});
	}

	private class BeamLightFilterPowerUpdate implements IObserver{
		private String lastPos = "";
		@Override
		public void update(Object source, Object arg) {
			if (source instanceof Scannable) {
				Scannable scn = (Scannable) source;
				try {
					String newPos = scn.getPosition().toString();
					if (!newPos.equals(lastPos)) {
						updatePower();
						lastPos = newPos;
					}
				} catch (DeviceException e) {
					logger.error("Problem getting position of {} - updating power calculation anyway", scn.getName());
					updatePower();
				}
			}

		}
	}

	private void bindFiltersForPowerCalculation() throws Exception {

		List<ScannableSetup> mirrorFilters = PowerCalulator.getMirrorFilters();
		List<ScannableSetup> motors = Arrays.asList(ScannableSetup.ME1_STRIPE, ScannableSetup.ME2_STRIPE,
				ScannableSetup.ME2_PITCH_ANGLE, ScannableSetup.WIGGLER_GAP, ScannableSetup.SLIT_1_HORIZONAL_GAP);

		// Add IObservers
		List<ScannableSetup> all = new ArrayList<>(mirrorFilters);
		all.addAll(motors);
		for(ScannableSetup s : all) {
			s.getScannable().addIObserver(new BeamLightFilterPowerUpdate());
		}
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

			dataBindingCtx.bindValue(
					ViewersObservables.observeSingleSelection(comboxElement),
					BeanProperties.value(AlignmentParametersModel.ELEMENT_PROP_NAME).observe(AlignmentParametersModel.INSTANCE), null,
					new UpdateValueStrategy() {

						@Override
						protected IStatus doSet(IObservableValue observableValue, Object value) {
							return super.doSet(observableValue, value);
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
							if (value != null) {
								return ((AbsorptionEdge) value).getEdgeType();
							}
							return null;
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

			butDetectorSetup.addListener(SWT.Selection, event -> {
				DetectorSetupDialog setup;
				try {
					setup = new DetectorSetupDialog(Display.getDefault().getActiveShell());
					setup.setBlockOnOpen(true);
					setup.open();
				} catch (Exception e) {
					logger.error("Tried to open incorrect detector setup page.", e);
				}
			});

			cmbDetectorType.setInput(DetectorModel.INSTANCE.getAvailableDetectors());

			AlignmentParametersModel.INSTANCE.addPropertyChangeListener(AlignmentParametersModel.SUGGESTED_PARAMETERS_PROP_KEY,
					evt -> updateAlignmentParametersSuggestion((AlignmentParametersBean) evt.getNewValue()));

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
		lblWigglerSuggestion = createScannableAndSuggestionLabel(motorSectionComposite, ScannableSetup.WIGGLER_GAP);

		Button applyButton = createApplyButtonControl(motorSectionComposite);
		createMotorPositionEditorControl(motorSectionComposite, ScannableSetup.WIGGLER_GAP, lblWigglerSuggestion, applyButton);

		lblSlitGapSuggestion = createScannableAndSuggestionLabel(motorSectionComposite, ScannableSetup.SLIT_1_HORIZONAL_GAP);
		applyButton = createApplyButtonControl(motorSectionComposite);
		createMotorPositionEditorControl(motorSectionComposite, ScannableSetup.SLIT_1_HORIZONAL_GAP, lblSlitGapSuggestion, applyButton);

		if (AlignmentParametersModel.INSTANCE.isUseAtn45()) {
			lblAtn1Suggestion = createScannableAndSuggestionLabel(motorSectionComposite, ScannableSetup.ATN4);
			applyButton = createApplyButtonControl(motorSectionComposite, ScannableSetup.ATN4, lblAtn1Suggestion);
			createEnumPositioner(motorSectionComposite, ScannableSetup.ATN4, lblAtn1Suggestion, applyButton);

			lblAtn2Suggestion = createScannableAndSuggestionLabel(motorSectionComposite, ScannableSetup.ATN5);
			applyButton = createApplyButtonControl(motorSectionComposite, ScannableSetup.ATN5, lblAtn2Suggestion);
			createEnumPositioner(motorSectionComposite, ScannableSetup.ATN5, lblAtn2Suggestion, applyButton);
		} else {
			lblAtn1Suggestion = createScannableAndSuggestionLabel(motorSectionComposite, ScannableSetup.ATN1);
			applyButton = createApplyButtonControl(motorSectionComposite, ScannableSetup.ATN1, lblAtn1Suggestion);
			createEnumPositioner(motorSectionComposite, ScannableSetup.ATN1, lblAtn1Suggestion, applyButton);

			lblAtn2Suggestion = createScannableAndSuggestionLabel(motorSectionComposite, ScannableSetup.ATN2);
			applyButton = createApplyButtonControl(motorSectionComposite, ScannableSetup.ATN2, lblAtn2Suggestion);
			createEnumPositioner(motorSectionComposite, ScannableSetup.ATN2, lblAtn2Suggestion, applyButton);

			lblAtn3Suggestion = createScannableAndSuggestionLabel(motorSectionComposite, ScannableSetup.ATN3);
			applyButton = createApplyButtonControl(motorSectionComposite, ScannableSetup.ATN3, lblAtn3Suggestion);
			createEnumPositioner(motorSectionComposite, ScannableSetup.ATN3, lblAtn3Suggestion, applyButton);
		}

		lblMe1StripSuggestion = createScannableAndSuggestionLabel(motorSectionComposite, ScannableSetup.ME1_STRIPE);
		applyButton = createApplyButtonControl(motorSectionComposite, ScannableSetup.ME1_STRIPE, lblMe1StripSuggestion);
		createEnumPositioner(motorSectionComposite, ScannableSetup.ME1_STRIPE, lblMe1StripSuggestion, applyButton);

		lblMe2StripSuggestion = createScannableAndSuggestionLabel(motorSectionComposite, ScannableSetup.ME2_STRIPE);
		applyButton = createApplyButtonControl(motorSectionComposite, ScannableSetup.ME2_STRIPE, lblMe2StripSuggestion);
		createEnumPositioner(motorSectionComposite, ScannableSetup.ME2_STRIPE, lblMe2StripSuggestion, applyButton);

		lblMe2PitchAngleSuggestion = createScannableAndSuggestionLabel(motorSectionComposite, ScannableSetup.ME2_PITCH_ANGLE);
		applyButton = createApplyButtonControl(motorSectionComposite);
		createMotorPositionEditorControl(motorSectionComposite, ScannableSetup.ME2_PITCH_ANGLE, lblMe2PitchAngleSuggestion, applyButton);

		lblPolyBender1Suggestion = createScannableAndSuggestionLabel(motorSectionComposite, ScannableSetup.POLY_BENDER_1);
		applyButton = createApplyButtonControl(motorSectionComposite);
		createMotorPositionEditorControl(motorSectionComposite, ScannableSetup.POLY_BENDER_1, lblPolyBender1Suggestion, applyButton);

		lblPolyBender2Suggestion = createScannableAndSuggestionLabel(motorSectionComposite, ScannableSetup.POLY_BENDER_2);
		applyButton = createApplyButtonControl(motorSectionComposite);
		createMotorPositionEditorControl(motorSectionComposite, ScannableSetup.POLY_BENDER_2, lblPolyBender2Suggestion, applyButton);

		lblPolyBraggSuggestion = createScannableAndSuggestionLabel(motorSectionComposite, ScannableSetup.POLY_BRAGG);
		applyButton = createApplyButtonControl(motorSectionComposite);
		createMotorPositionEditorControl(motorSectionComposite, ScannableSetup.POLY_BRAGG, lblPolyBraggSuggestion, applyButton);

		lblArm2ThetaAngleSuggestion = createScannableAndSuggestionLabel(motorSectionComposite, ScannableSetup.ARM_2_THETA_ANGLE);
		applyButton = createApplyButtonControl(motorSectionComposite);
		createMotorPositionEditorControl(motorSectionComposite, ScannableSetup.ARM_2_THETA_ANGLE, lblArm2ThetaAngleSuggestion, applyButton);

		Label lblPowerEstimate = toolkit.createLabel(motorSectionComposite, "Estimated power is: ");
		lblPowerEstimate.setLayoutData(new GridData(GridData.HORIZONTAL_ALIGN_BEGINNING));
		labelPowerEstimateValue = toolkit.createFormText(motorSectionComposite, false);
		labelPowerEstimateValue.setText(getHighlightedFormatedString(""), true, false);
		GridData gridData = new GridData(GridData.HORIZONTAL_ALIGN_FILL);
		gridData.horizontalSpan = 3;
		labelPowerEstimateValue.setLayoutData(gridData);
		labelPowerEstimateValue.setToolTipText("Estimated power for current configuration (suggested maximum = "+ScannableSetup.MAX_POWER_IN_WATT+" W)");
		lblDetectorHeightSuggestion = createScannableAndSuggestionLabel(motorSectionComposite, ScannableSetup.DETECTOR_HEIGHT);
		applyButton = createApplyButtonControl(motorSectionComposite);
		createMotorPositionEditorControl(motorSectionComposite, ScannableSetup.DETECTOR_HEIGHT, lblDetectorHeightSuggestion, applyButton);

		lblDetectorDistanceSuggestion = createScannableAndSuggestionLabel(motorSectionComposite, ScannableSetup.DETECTOR_Z_POSITION);
		applyButton = createApplyButtonControl(motorSectionComposite);
		createMotorPositionEditorControl(motorSectionComposite, ScannableSetup.DETECTOR_Z_POSITION, lblDetectorDistanceSuggestion, applyButton);

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

		ScannableMotorMoveObserver.setupStopToolbarButton(motorSection, movingScannables);

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(motorSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		motorSection.setSeparatorControl(defaultSectionSeparator);
	}

	private static String getHighlightedFormatedString(String value) {
		return String.format("<form><p><b>%s</b></p></form>", value);
	}

	private Label createScannableAndSuggestionLabel(Composite parent, ScannableSetup scannableSetup) {
		Label lbl = toolkit.createLabel(parent, scannableSetup.getLabel(), SWT.NONE);
		lbl.setLayoutData(createLabelGridData());
		lbl.setToolTipText(scannableSetup.getScannableName());
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

	private Button createApplyButtonControl(Composite parent) {
		Button suggestionApplyButton = toolkit.createButton(parent, "", SWT.FLAT);
		suggestionApplyButton.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_TOOL_FORWARD));
		suggestionApplyButton.setLayoutData(new GridData(GridData.BEGINNING, GridData.BEGINNING, false, false));
		suggestionApplyButton.setVisible(controlsEnabled); // hide the button if controls are disabled
		return suggestionApplyButton;
	}

	private Button createApplyButtonControl(Composite parent, ScannableSetup scannableSetup, Label posLabel) {
		Button button = createApplyButtonControl(parent);
		button.addListener(SWT.Selection, event -> {
			try {
				scannableSetup.getScannable().asynchronousMoveTo(posLabel.getText());
			} catch (Exception e) {
				String errorMessage = "Exception setting motor to " + posLabel.getText();
				UIHelper.showError(errorMessage, e.getMessage());
				logger.error(errorMessage, e);
			}
		});
		return button;
	}

	private EnumPositionViewer createEnumPositioner(Composite parent, ScannableSetup scnSetup, Label suggestionLabel, Button applyButton) throws Exception {

		EnumPositionViewer enumPositionViewer = new EnumPositionViewer(parent, (EnumPositioner) scnSetup.getScannable(), "", true);
		enumPositionViewer.getComboWrapper().setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		enumPositionViewer.setEnabled(controlsEnabled);

		applyButton.addListener(SWT.Selection, event -> {
			try {
				scnSetup.getScannable().asynchronousMoveTo(suggestionLabel.getText());
			} catch (Exception e) {
				String errorMessage = "Exception setting motor to " + suggestionLabel.getText();
				UIHelper.showError(errorMessage, e.getMessage());
				logger.error(errorMessage, e);
			}
		});
		return enumPositionViewer;
	}

	private MotorPositionEditorControl createMotorPositionEditorControl(Composite parent, ScannableSetup scnSetup, Label suggestionLabel, Button applyButton) throws Exception {
		MotorPositionEditorControl motorPositionEditorControl = new MotorPositionEditorControl(parent, SWT.None, scnSetup.getScannableWrapper(), controlsEnabled, controlsEnabled);
		motorPositionEditorControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		motorPositionEditorControl.setEditable(controlsEnabled);

		applyButton.addListener(SWT.Selection, new SuggestionApplyButtonListener(scnSetup, suggestionLabel, motorPositionEditorControl));

		scnSetup.getScannable().addIObserver(moveObserver);

		return motorPositionEditorControl;
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
		PlatformUI.getWorkbench().getDisplay().asyncExec(() -> {
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
			lblDetectorDistanceSuggestion.setText(ScannableSetup.DETECTOR_Z_POSITION.getUnit().addUnitSuffix(DataHelper.roundDoubletoString(results.getDetectorDistance() * 1000))); // Convert to mm
			lblDetectorHeightSuggestion.setText(ScannableSetup.DETECTOR_HEIGHT.getUnit().addUnitSuffix(DataHelper.roundDoubletoString(results.getDetectorHeight())));

			List<String> attenuatorPositions = results.getAttenuatorPositions();
			lblAtn1Suggestion.setText(attenuatorPositions.get(0));
			lblAtn2Suggestion.setText(attenuatorPositions.get(1));
			if (attenuatorPositions.size() == 3 && lblAtn3Suggestion != null) {
				lblAtn3Suggestion.setText(attenuatorPositions.get(2));
			}

			if (results.getEnergyBandwidth() != null) {
				String value1 = getHighlightedFormatedString(UnitSetup.EV.addUnitSuffix(Integer.toString(results.getEnergyBandwidth().intValue())));
				labelDeltaEValueSuggestion.setText(value1, true, false);
			}
			if (results.getReadBackEnergyBandwidth() != null) {
				String value2 = getHighlightedFormatedString(UnitSetup.EV.addUnitSuffix(Integer.toString(results.getReadBackEnergyBandwidth().intValue())));
				labelDeltaEValue.setText(value2, true, false);
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
