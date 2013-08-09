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

package uk.ac.gda.exafs.ui.views;

import gda.device.detector.StripDetector;
import gda.device.detector.XHDetector;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.beans.BeansObservables;
import org.eclipse.jface.databinding.swt.WidgetProperties;
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
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.forms.widgets.TableWrapData;
import org.eclipse.ui.forms.widgets.TableWrapLayout;
import org.eclipse.ui.part.ViewPart;

import uk.ac.gda.exafs.data.DetectorConfig;
import uk.ac.gda.exafs.data.EDECalibrationModel;
import uk.ac.gda.exafs.ui.composites.NumberEditorControl;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.sections.EDECalibrationSection;

public class SingleSpectrumView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.singlespectrumview";

	private FormToolkit toolkit;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private ScrolledForm scrolledform;

	private ComboViewer cmbFirstStripViewer;

	private ComboViewer cmbLastStripViewer;

	@Override
	public void createPartControl(Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		scrolledform = toolkit.createScrolledForm(parent);
		Form form = scrolledform.getForm();
		form.getBody().setLayout(new TableWrapLayout());
		toolkit.decorateFormHeading(form);
		form.setText("Single spectrum / E calibration");
		Composite formParent = form.getBody();
		createSampleI0Position(formParent);
		createSampleItPosition(formParent);
		createAcquisitionPosition(formParent);
		EDECalibrationSection.INSTANCE.createEdeCalibrationSection(form, toolkit);
	}

	private void createSampleI0Position(Composite body) {
		@SuppressWarnings("static-access")
		final Section samplePositionSection = toolkit.createSection(body, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		samplePositionSection.setText("I0 sample position");
		samplePositionSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite samplePositionSectionComposite = toolkit.createComposite(samplePositionSection, SWT.NONE);
		samplePositionSectionComposite.setLayout(new GridLayout());
		toolkit.paintBordersFor(samplePositionSectionComposite);
		samplePositionSection.setClient(samplePositionSectionComposite);

		Composite xyPositionComposite = toolkit.createComposite(samplePositionSectionComposite, SWT.NONE);
		toolkit.paintBordersFor(xyPositionComposite);
		xyPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		xyPositionComposite.setLayout(new GridLayout(2, true));

		Composite xPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(xPositionComposite);
		xPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		xPositionComposite.setLayout(new GridLayout(2, false));

		Label xPosLabel = toolkit.createLabel(xPositionComposite, "X position", SWT.None);
		xPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		String holePosition = "";
		Text i0XPosition = toolkit.createText(xPositionComposite, holePosition, SWT.None);
		i0XPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite yPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(yPositionComposite);
		yPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		yPositionComposite.setLayout(new GridLayout(2, false));

		Label yPosLabel = toolkit.createLabel(yPositionComposite, "Y position", SWT.None);
		yPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		String foil = "";
		Text i0YPosition = toolkit.createText(yPositionComposite, foil, SWT.None);
		i0YPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite sampleCustomPositionComposite = toolkit.createComposite(samplePositionSectionComposite, SWT.NONE);
		toolkit.paintBordersFor(sampleCustomPositionComposite);
		sampleCustomPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		sampleCustomPositionComposite.setLayout(new GridLayout(2, false));
		Button customI0PositionButton = toolkit.createButton(sampleCustomPositionComposite, "Custom position", SWT.CHECK);
		customI0PositionButton.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		Button customI0ReadPositionButton = toolkit.createButton(sampleCustomPositionComposite, "Read current position", SWT.PUSH);
		customI0ReadPositionButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		dataBindingCtx.bindValue(WidgetProperties.enabled().observe(customI0ReadPositionButton), WidgetProperties.selection().observe(customI0PositionButton));

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(samplePositionSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		samplePositionSection.setSeparatorControl(defaultSectionSeparator);
	}

	private void createSampleItPosition(Composite body) {
		@SuppressWarnings("static-access")
		final Section samplePositionSection = toolkit.createSection(body, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		samplePositionSection.setText("It sample position");
		samplePositionSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite samplePositionSectionComposite = toolkit.createComposite(samplePositionSection, SWT.NONE);
		samplePositionSectionComposite.setLayout(new GridLayout());
		toolkit.paintBordersFor(samplePositionSectionComposite);
		samplePositionSection.setClient(samplePositionSectionComposite);
		String referenceFoil = "";

		Text i0Position = toolkit.createText(samplePositionSectionComposite, referenceFoil, SWT.None);
		i0Position.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		Composite sampleCustomPositionComposite = toolkit.createComposite(samplePositionSectionComposite, SWT.NONE);
		toolkit.paintBordersFor(sampleCustomPositionComposite);
		sampleCustomPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		sampleCustomPositionComposite.setLayout(new GridLayout(2, false));
		Button customI0PositionButton = toolkit.createButton(sampleCustomPositionComposite, "Custom position", SWT.CHECK);
		customI0PositionButton.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		Button customI0ReadPositionButton = toolkit.createButton(sampleCustomPositionComposite, "Read current position", SWT.PUSH);
		customI0ReadPositionButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		dataBindingCtx.bindValue(WidgetProperties.enabled().observe(customI0ReadPositionButton), WidgetProperties.selection().observe(customI0PositionButton));

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(samplePositionSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		samplePositionSection.setSeparatorControl(defaultSectionSeparator);
	}

	private void createAcquisitionPosition(Composite body) {
		@SuppressWarnings("static-access")
		final Section acquisitionSection = toolkit.createSection(body, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		acquisitionSection.setText("Acquisition settings");
		acquisitionSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite acquisitionSectionComposite = toolkit.createComposite(acquisitionSection, SWT.NONE);
		acquisitionSectionComposite.setLayout(new GridLayout());
		toolkit.paintBordersFor(acquisitionSectionComposite);
		acquisitionSection.setClient(acquisitionSectionComposite);

		Composite stripsComposite = new Composite(acquisitionSectionComposite, SWT.NONE);
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

		DetectorConfig.INSTANCE.addPropertyChangeListener(DetectorConfig.CURRENT_DETECTOR_SETUP_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				Object value = evt.getNewValue();
				if (value != null) {
					StripDetector detector = (StripDetector) value;
					cmbFirstStripViewer.setSelection(new StructuredSelection(detector.getLowerChannel()));
					cmbLastStripViewer.setSelection(new StructuredSelection(detector.getUpperChannel()));
				}
			}
		});

		if (DetectorConfig.INSTANCE.getCurrentDetector() != null) {
			cmbFirstStripViewer.setSelection(new StructuredSelection(DetectorConfig.INSTANCE.getCurrentDetector().getLowerChannel()));
			cmbLastStripViewer.setSelection(new StructuredSelection(DetectorConfig.INSTANCE.getCurrentDetector().getUpperChannel()));
		}

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(cmbFirstStripViewer.getControl()),
				BeansObservables.observeValue(DetectorConfig.INSTANCE, DetectorConfig.DETECTOR_CONNECTED_PROP_NAME));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(cmbLastStripViewer.getControl()),
				BeansObservables.observeValue(DetectorConfig.INSTANCE, DetectorConfig.DETECTOR_CONNECTED_PROP_NAME));

		Composite acquisitionSettingsComposite = new Composite(acquisitionSectionComposite, SWT.NONE);
		acquisitionSettingsComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, true));
		acquisitionSettingsComposite.setLayout(new GridLayout(2, false));
		toolkit.paintBordersFor(acquisitionSettingsComposite);
		try {
			Label i0IntegrationTimeLabel = toolkit.createLabel(acquisitionSettingsComposite, "I0 Integration time");
			i0IntegrationTimeLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

			NumberEditorControl i0IntegrationTimeText = new NumberEditorControl(acquisitionSettingsComposite, SWT.None, EDECalibrationModel.INSTANCE, EDECalibrationModel.I0_INTEGRATION_TIME_PROP_NAME, true);
			i0IntegrationTimeText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

			Label i0NoOfAccumulationLabel = toolkit.createLabel(acquisitionSettingsComposite, "I0 Number of accumulations");
			i0NoOfAccumulationLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

			NumberEditorControl i0NoOfAccumulationText = new NumberEditorControl(acquisitionSettingsComposite, SWT.None, EDECalibrationModel.INSTANCE, EDECalibrationModel.I0_NUMBER_OF_ACCUMULATIONS_PROP_NAME, true);
			i0NoOfAccumulationText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

			Label itIntegrationTimeLabel = toolkit.createLabel(acquisitionSettingsComposite, "It Integration time");
			itIntegrationTimeLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

			NumberEditorControl itIntegrationTimeText = new NumberEditorControl(acquisitionSettingsComposite, SWT.None, EDECalibrationModel.INSTANCE, EDECalibrationModel.IT_INTEGRATION_TIME_PROP_NAME, true);
			itIntegrationTimeText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

			Label itNoOfAccumulationLabel = toolkit.createLabel(acquisitionSettingsComposite, "It Number of accumulations");
			itNoOfAccumulationLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

			NumberEditorControl itNoOfAccumulationText = new NumberEditorControl(acquisitionSettingsComposite, SWT.None, EDECalibrationModel.INSTANCE, EDECalibrationModel.IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME, true);
			itNoOfAccumulationText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

			Composite acquisitionSettingsFileNameComposite = new Composite(acquisitionSectionComposite, SWT.NONE);
			acquisitionSettingsFileNameComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, true));
			acquisitionSettingsFileNameComposite.setLayout(new GridLayout(2, false));
			toolkit.paintBordersFor(acquisitionSettingsFileNameComposite);

			Label fileNameLabel = toolkit.createLabel(acquisitionSettingsFileNameComposite, "Filename");
			fileNameLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
			Text fileNameText = toolkit.createText(acquisitionSettingsFileNameComposite, "", SWT.None);
			fileNameText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

			Composite acquisitionButtonsComposite = new Composite(acquisitionSectionComposite, SWT.NONE);
			acquisitionButtonsComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, true));
			acquisitionButtonsComposite.setLayout(new GridLayout(2, true));
			toolkit.paintBordersFor(acquisitionButtonsComposite);

			Button startAcquicitionButton = toolkit.createButton(acquisitionButtonsComposite, "Start", SWT.PUSH);
			startAcquicitionButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

			Button stopAcquicitionButton = toolkit.createButton(acquisitionButtonsComposite, "Stop", SWT.PUSH);
			stopAcquicitionButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
			startAcquicitionButton.setEnabled(false);
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
		}
		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(acquisitionSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		acquisitionSection.setSeparatorControl(defaultSectionSeparator);
	}

	@Override
	public void setFocus() {
		scrolledform.setFocus();
	}

}
