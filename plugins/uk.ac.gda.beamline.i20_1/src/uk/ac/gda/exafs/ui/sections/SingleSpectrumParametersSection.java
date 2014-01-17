/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.ui.sections;

import gda.device.detector.XHDetector;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.beans.BeansObservables;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.databinding.viewers.ViewersObservables;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.ComboViewer;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.jface.viewers.StructuredViewer;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.CCombo;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.SingleSpectrumUIModel;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.experiment.ExperimentModelHolder;
import uk.ac.gda.exafs.ui.data.experiment.SampleStageMotors;
import uk.ac.gda.ui.components.NumberEditorControl;

public class SingleSpectrumParametersSection extends ResourceComposite {

	private final FormToolkit toolkit;

	private static final Logger logger = LoggerFactory.getLogger(SingleSpectrumParametersSection.class);

	private final DataBindingContext dataBindingCtx = new DataBindingContext();
	private Section section;

	private ComboViewer cmbFirstStripViewer;

	private StructuredViewer cmbLastStripViewer;

	protected Binding cmbFirstStripViewerBinding;

	protected Binding cmbLastStripViewerBinding;

	private final boolean forExperiment;

	private Section sectionIRefaccumulationSection;

	private NumberEditorControl iRefIntegrationTimeValueText;

	private NumberEditorControl iRefNoOfAccumulationValueText;

	private Button i0NoOfAccumulationCheck;

	private NumberEditorControl i0NoOfAccumulationValueText;

	public SingleSpectrumParametersSection(Composite parent, int style, boolean forExperiment) {
		super(parent, style);
		this.forExperiment = forExperiment;
		toolkit = new FormToolkit(parent.getDisplay());
		try {
			setupUI();
			bind();
		} catch (Exception e) {
			logger.error("Unable to create controls", e);
		}
	}

	private void bind() {
		final SingleSpectrumUIModel singleSpectrumDataModel = ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel();

		dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(i0NoOfAccumulationCheck),
				BeanProperties.value(SingleSpectrumUIModel.USE_IT_TIME_FOR_I0_PROP_NAME).observe(singleSpectrumDataModel));
		dataBindingCtx.bindValue(
				BeanProperties.value(NumberEditorControl.EDITABLE_PROP_NAME).observe(i0NoOfAccumulationValueText),
				BeanProperties.value(SingleSpectrumUIModel.USE_IT_TIME_FOR_I0_PROP_NAME).observe(singleSpectrumDataModel),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {

					@Override
					public Object convert(Object value) {
						return !((boolean) value);
					}
				});
		dataBindingCtx.bindValue(
				WidgetProperties.visible().observe(sectionIRefaccumulationSection),
				BeanProperties.value(SampleStageMotors.USE_IREF_PROP_NAME).observe(SampleStageMotors.INSTANCE),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus result = super.doSet(observableValue, value);
						boolean useIRef = (boolean) value;
						((GridData) sectionIRefaccumulationSection.getLayoutData()).exclude = !useIRef;
						((GridData) sectionIRefaccumulationSection.getLayoutData()).exclude = !((boolean) value);
						((GridLayout) sectionIRefaccumulationSection.getParent().getLayout()).numColumns = useIRef ? 2 : 1;
						UIHelper.revalidateLayout(sectionIRefaccumulationSection.getParent());
						return result;
					}
				});
	}

	private void createI0IRefComposites() throws Exception {
		final SingleSpectrumUIModel singleSpectrumDataModel = ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel();

		// I0 and IRef accumulation times
		Composite composite = toolkit.createComposite(this);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		composite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, true));

		// I0
		Section sectionI0accumulationSection = toolkit.createSection(composite, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		sectionI0accumulationSection.setText("I0 acquisition settings");
		sectionI0accumulationSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		final Composite i0IaccumulationComposite = toolkit.createComposite(sectionI0accumulationSection, SWT.NONE);
		i0IaccumulationComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		sectionI0accumulationSection.setClient(i0IaccumulationComposite);

		i0NoOfAccumulationCheck = toolkit.createButton(i0IaccumulationComposite, "Use It and IRef for I0 no. of accumulations", SWT.CHECK);
		GridData gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gridData.horizontalSpan = 2;
		i0NoOfAccumulationCheck.setLayoutData(gridData);

		Label label = toolkit.createLabel(i0IaccumulationComposite, "Accumulation time", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		NumberEditorControl i0IntegrationTimeValueText = new NumberEditorControl(i0IaccumulationComposite, SWT.None, singleSpectrumDataModel, SingleSpectrumUIModel.I0_INTEGRATION_TIME_PROP_NAME, false);
		i0IntegrationTimeValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		i0IntegrationTimeValueText.setUnit(UnitSetup.MILLI_SEC.getText());

		label = toolkit.createLabel(i0IaccumulationComposite, "No. of accumulations", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		i0NoOfAccumulationValueText = new NumberEditorControl(i0IaccumulationComposite, SWT.None, singleSpectrumDataModel, SingleSpectrumUIModel.I0_NUMBER_OF_ACCUMULATIONS_PROP_NAME, false);
		i0NoOfAccumulationValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite sectionSeparator = toolkit.createCompositeSeparator(sectionI0accumulationSection);
		toolkit.paintBordersFor(sectionSeparator);
		sectionI0accumulationSection.setSeparatorControl(sectionSeparator);

		// IRef
		sectionIRefaccumulationSection = toolkit.createSection(composite, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		sectionIRefaccumulationSection.setText("IRef acquisition settings");
		sectionIRefaccumulationSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		final Composite iRefDetailsComposite = toolkit.createComposite(sectionIRefaccumulationSection, SWT.NONE);
		iRefDetailsComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		sectionIRefaccumulationSection.setClient(iRefDetailsComposite);

		label = toolkit.createLabel(iRefDetailsComposite, "Accumulation time", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		iRefIntegrationTimeValueText = new NumberEditorControl(iRefDetailsComposite, SWT.None, singleSpectrumDataModel, SingleSpectrumUIModel.IREF_INTEGRATION_TIME_PROP_NAME, false);
		iRefIntegrationTimeValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		iRefIntegrationTimeValueText.setUnit(UnitSetup.MILLI_SEC.getText());

		label = toolkit.createLabel(iRefDetailsComposite, "No. of accumulations", SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		iRefNoOfAccumulationValueText = new NumberEditorControl(iRefDetailsComposite, SWT.None, singleSpectrumDataModel, SingleSpectrumUIModel.IREF_NO_OF_ACCUMULATION_PROP_NAME, false);
		iRefNoOfAccumulationValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		sectionSeparator = toolkit.createCompositeSeparator(sectionIRefaccumulationSection);
		toolkit.paintBordersFor(sectionSeparator);
		sectionIRefaccumulationSection.setSeparatorControl(sectionSeparator);
	}


	private void setupUI() throws Exception {

		final SingleSpectrumUIModel singleSpectrumDataModel = ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel();
		this.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));

		createI0IRefComposites();

		section = toolkit.createSection(this, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		section.setText("I0 acquisition settings");
		section.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		Composite sectionComposite = toolkit.createComposite(section, SWT.NONE);
		sectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		toolkit.paintBordersFor(sectionComposite);
		section.setClient(sectionComposite);

		Composite stripsComposite = new Composite(sectionComposite, SWT.NONE);
		stripsComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, true));
		stripsComposite.setLayout(new GridLayout(4, false));

		final Label lblFirstStrip = toolkit.createLabel(stripsComposite, "First strip", SWT.NONE);
		lblFirstStrip.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		CCombo cmbFirstStrip = new CCombo(stripsComposite, SWT.BORDER | SWT.FLAT);
		cmbFirstStrip.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		cmbFirstStripViewer = new ComboViewer(cmbFirstStrip);
		cmbFirstStripViewer.setContentProvider(new ArrayContentProvider());
		cmbFirstStripViewer.setLabelProvider(new LabelProvider());
		cmbFirstStripViewer.setInput(XHDetector.getStrips());

		Label lblLastStrip = toolkit.createLabel(stripsComposite, "Last strip", SWT.NONE);
		lblLastStrip.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		CCombo cmbLastStrip = new CCombo(stripsComposite, SWT.BORDER | SWT.FLAT);
		cmbLastStrip.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		cmbLastStripViewer = new ComboViewer(cmbLastStrip);
		cmbLastStripViewer.setContentProvider(new ArrayContentProvider());
		cmbLastStripViewer.setLabelProvider(new LabelProvider());
		cmbLastStripViewer.setInput(XHDetector.getStrips());

		DetectorModel.INSTANCE.addPropertyChangeListener(DetectorModel.DETECTOR_CONNECTED_PROP_NAME, dectectorChangeListener);

		if (DetectorModel.INSTANCE.getCurrentDetector() != null) {
			bindUpperAndLowerChannelComboViewers();
		}


		if (DetectorModel.INSTANCE.getCurrentDetector() != null) {
			cmbFirstStripViewer.setSelection(new StructuredSelection(DetectorModel.INSTANCE.getCurrentDetector().getLowerChannel()));
			cmbLastStripViewer.setSelection(new StructuredSelection(DetectorModel.INSTANCE.getCurrentDetector().getUpperChannel()));
		}

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(cmbFirstStripViewer.getControl()),
				BeansObservables.observeValue(DetectorModel.INSTANCE, DetectorModel.DETECTOR_CONNECTED_PROP_NAME));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(cmbLastStripViewer.getControl()),
				BeansObservables.observeValue(DetectorModel.INSTANCE, DetectorModel.DETECTOR_CONNECTED_PROP_NAME));

		Composite acquisitionSettingsComposite = new Composite(sectionComposite, SWT.NONE);
		acquisitionSettingsComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, true));
		acquisitionSettingsComposite.setLayout(new GridLayout(2, false));
		toolkit.paintBordersFor(acquisitionSettingsComposite);

		Label itIntegrationTimeLabel = toolkit.createLabel(acquisitionSettingsComposite, "It Integration time");
		itIntegrationTimeLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		NumberEditorControl itIntegrationTimeText = new NumberEditorControl(acquisitionSettingsComposite, SWT.None, singleSpectrumDataModel, SingleSpectrumUIModel.IT_INTEGRATION_TIME_PROP_NAME, true);
		itIntegrationTimeText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		itIntegrationTimeText.setUnit(ClientConfig.UnitSetup.MILLI_SEC.getText());
		itIntegrationTimeText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label itNoOfAccumulationLabel = toolkit.createLabel(acquisitionSettingsComposite, "It Number of accumulations");
		itNoOfAccumulationLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		NumberEditorControl itNoOfAccumulationText = new NumberEditorControl(acquisitionSettingsComposite, SWT.None, singleSpectrumDataModel, SingleSpectrumUIModel.IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME, true);
		itNoOfAccumulationText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite acquisitionSettingsFileNameComposite = new Composite(sectionComposite, SWT.NONE);
		acquisitionSettingsFileNameComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, true));
		acquisitionSettingsFileNameComposite.setLayout(new GridLayout(2, false));
		toolkit.paintBordersFor(acquisitionSettingsFileNameComposite);

		if (forExperiment) {
			Label fileNameLabel = toolkit.createLabel(acquisitionSettingsFileNameComposite, "File name prefix");
			fileNameLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
			Text fileNamePrefixText = toolkit.createText(acquisitionSettingsFileNameComposite, "", SWT.None);
			fileNamePrefixText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
			// FIXME Add validation
			dataBindingCtx.bindValue(
					WidgetProperties.text(SWT.Modify).observe(fileNamePrefixText),
					BeanProperties.value(SingleSpectrumUIModel.FILE_TEMPLATE_PROP_NAME).observe(singleSpectrumDataModel),
					new UpdateValueStrategy(),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER));
		}

		// TODO Have to decide whether to present the filename text

		//		Label fileNameLabel = toolkit.createLabel(acquisitionSettingsFileNameComposite, "Filename");
		//		fileNameLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		//		Text fileNameText = toolkit.createText(acquisitionSettingsFileNameComposite, "", SWT.None);
		//		fileNameText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		//		dataBindingCtx.bindValue(WidgetProperties.text().observe(fileNameText), BeanProperties.value(SingleSpectrumUIModel.FILE_NAME_PROP_NAME).observe(SingleSpectrumUIModel.INSTANCE));
		//		fileNameText.setEditable(false);

		Composite acquisitionButtonsComposite = new Composite(sectionComposite, SWT.NONE);
		acquisitionButtonsComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, true));
		acquisitionButtonsComposite.setLayout(new GridLayout(2, true));
		toolkit.paintBordersFor(acquisitionButtonsComposite);

		Button startAcquicitionButton = toolkit.createButton(acquisitionButtonsComposite, "Start", SWT.PUSH);
		startAcquicitionButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		startAcquicitionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					singleSpectrumDataModel.doCollection(forExperiment);
				} catch (Exception e) {
					UIHelper.showError("Unable to scan", e.getMessage());
					logger.error("Unable to scan", e);
				}
			}
		});

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(startAcquicitionButton),
				BeanProperties.value(SingleSpectrumUIModel.SCANNING_PROP_NAME).observe(singleSpectrumDataModel),
				null,
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return (!(boolean) value);
					}
				});

		Button stopAcquicitionButton = toolkit.createButton(acquisitionButtonsComposite, "Stop", SWT.PUSH);
		stopAcquicitionButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(stopAcquicitionButton),
				BeanProperties.value(SingleSpectrumUIModel.SCANNING_PROP_NAME).observe(singleSpectrumDataModel));
		stopAcquicitionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				singleSpectrumDataModel.doStop();
			}
		});

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(section),
				BeansObservables.observeValue(DetectorModel.INSTANCE, DetectorModel.DETECTOR_CONNECTED_PROP_NAME));

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(defaultSectionSeparator);
		section.setSeparatorControl(defaultSectionSeparator);
	}

	private final PropertyChangeListener dectectorChangeListener = new PropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			boolean detectorConnected = (boolean) evt.getNewValue();
			if (detectorConnected) {
				bindUpperAndLowerChannelComboViewers();
			} else {
				if (cmbFirstStripViewerBinding != null) {
					dataBindingCtx.removeBinding(cmbFirstStripViewerBinding);
					cmbFirstStripViewerBinding.dispose();
					cmbFirstStripViewerBinding = null;
				}
				if (cmbLastStripViewerBinding != null) {
					dataBindingCtx.removeBinding(cmbLastStripViewerBinding);
					cmbLastStripViewerBinding.dispose();
					cmbLastStripViewerBinding = null;
				}
			}
		}
	};

	private void bindUpperAndLowerChannelComboViewers() {
		cmbFirstStripViewerBinding = dataBindingCtx.bindValue(
				ViewersObservables.observeSingleSelection(cmbFirstStripViewer),
				BeansObservables.observeValue(DetectorModel.INSTANCE, DetectorModel.LOWER_CHANNEL_PROP_NAME));
		cmbLastStripViewerBinding = dataBindingCtx.bindValue(
				ViewersObservables.observeSingleSelection(cmbLastStripViewer),
				BeansObservables.observeValue(DetectorModel.INSTANCE, DetectorModel.UPPER_CHANNEL_PROP_NAME));
	}

	@Override
	protected void disposeResource() {
		dataBindingCtx.dispose();
		DetectorModel.INSTANCE.removePropertyChangeListener(DetectorModel.DETECTOR_CONNECTED_PROP_NAME, dectectorChangeListener);
	}
}
