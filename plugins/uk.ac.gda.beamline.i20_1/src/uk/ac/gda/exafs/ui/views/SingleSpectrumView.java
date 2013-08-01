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
		String holePosition = "";
		Text i0Position = toolkit.createText(samplePositionSectionComposite, holePosition, SWT.None);
		i0Position.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		Composite sampleCustomPositionComposite = toolkit.createComposite(samplePositionSectionComposite, SWT.NONE);
		toolkit.paintBordersFor(sampleCustomPositionComposite);
		sampleCustomPositionComposite.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		sampleCustomPositionComposite.setLayout(new GridLayout(2, false));
		Button customI0PositionButton = toolkit.createButton(sampleCustomPositionComposite, "Custom position", SWT.CHECK);
		customI0PositionButton.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		Button customI0ReadPositionButton = toolkit.createButton(sampleCustomPositionComposite, "Read current position", SWT.PUSH);
		customI0ReadPositionButton.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
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
		i0Position.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		Composite sampleCustomPositionComposite = toolkit.createComposite(samplePositionSectionComposite, SWT.NONE);
		toolkit.paintBordersFor(sampleCustomPositionComposite);
		sampleCustomPositionComposite.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		sampleCustomPositionComposite.setLayout(new GridLayout(2, false));
		Button customI0PositionButton = toolkit.createButton(sampleCustomPositionComposite, "Custom position", SWT.CHECK);
		customI0PositionButton.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		Button customI0ReadPositionButton = toolkit.createButton(sampleCustomPositionComposite, "Read current position", SWT.PUSH);
		customI0ReadPositionButton.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
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
		stripsComposite.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, true));
		stripsComposite.setLayout(new GridLayout(4, false));

		final Label lblFirstStrip = toolkit.createLabel(stripsComposite, "First strip:", SWT.NONE);
		lblFirstStrip.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		CCombo cmbFirstStrip = new CCombo(stripsComposite, SWT.BORDER | SWT.FLAT);
		cmbFirstStrip.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		cmbFirstStripViewer = new ComboViewer(cmbFirstStrip);
		cmbFirstStripViewer.setContentProvider(new ArrayContentProvider());
		cmbFirstStripViewer.setLabelProvider(new LabelProvider());
		cmbFirstStripViewer.setInput(XHDetector.getStrips());

		Label lblLastStrip = toolkit.createLabel(stripsComposite, "Last strip:", SWT.NONE);
		lblLastStrip.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		CCombo cmbLastStrip = new CCombo(stripsComposite, SWT.BORDER | SWT.FLAT);
		cmbLastStrip.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
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
		acquisitionSettingsComposite.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, true));
		acquisitionSettingsComposite.setLayout(new GridLayout(2, false));
		toolkit.paintBordersFor(acquisitionSettingsComposite);

		Label i0IntegrationTimeLabel = toolkit.createLabel(acquisitionSettingsComposite, "I0 Integration time:");
		i0IntegrationTimeLabel.setLayoutData(new GridData(GridData.BEGINNING, GridData.BEGINNING, false, false));
		Text i0IntegrationTimeText = toolkit.createText(acquisitionSettingsComposite, "", SWT.None);
		GridData gridData = new GridData(GridData.FILL, GridData.BEGINNING, true, false);
		i0IntegrationTimeText.setLayoutData(gridData);

		Label i0NoOfAccumulationLabel = toolkit.createLabel(acquisitionSettingsComposite, "I0 Nnumber of accumulations:");
		i0NoOfAccumulationLabel.setLayoutData(new GridData(GridData.BEGINNING, GridData.BEGINNING, false, false));
		Text i0NoOfAccumulationText = toolkit.createText(acquisitionSettingsComposite, "", SWT.None);
		gridData = new GridData(GridData.FILL, GridData.BEGINNING, true, false);
		i0NoOfAccumulationText.setLayoutData(gridData);

		Label itIntegrationTimeLabel = toolkit.createLabel(acquisitionSettingsComposite, "It Integration time:");
		itIntegrationTimeLabel.setLayoutData(new GridData(GridData.BEGINNING, GridData.BEGINNING, false, false));
		Text itIntegrationTimeText = toolkit.createText(acquisitionSettingsComposite, "", SWT.None);
		gridData = new GridData(GridData.FILL, GridData.BEGINNING, true, false);
		itIntegrationTimeText.setLayoutData(gridData);

		Label itNoOfAccumulationLabel = toolkit.createLabel(acquisitionSettingsComposite, "It Nnumber of accumulations:");
		itNoOfAccumulationLabel.setLayoutData(new GridData(GridData.BEGINNING, GridData.BEGINNING, false, false));
		Text itNoOfAccumulationText = toolkit.createText(acquisitionSettingsComposite, "", SWT.None);
		gridData = new GridData(GridData.FILL, GridData.BEGINNING, true, false);
		itNoOfAccumulationText.setLayoutData(gridData);

		Composite acquisitionSettingsFileNameComposite = new Composite(acquisitionSectionComposite, SWT.NONE);
		acquisitionSettingsFileNameComposite.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, true));
		acquisitionSettingsFileNameComposite.setLayout(new GridLayout(2, false));
		toolkit.paintBordersFor(acquisitionSettingsFileNameComposite);

		Label fileNameLabel = toolkit.createLabel(acquisitionSettingsFileNameComposite, "Filename:");
		fileNameLabel.setLayoutData(new GridData(GridData.BEGINNING, GridData.BEGINNING, false, false));
		Text fileNameText = toolkit.createText(acquisitionSettingsFileNameComposite, "", SWT.None);
		gridData = new GridData(GridData.FILL, GridData.BEGINNING, true, false);
		fileNameText.setLayoutData(gridData);

		Composite acquisitionButtonsComposite = new Composite(acquisitionSectionComposite, SWT.NONE);
		acquisitionButtonsComposite.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, true));
		acquisitionButtonsComposite.setLayout(new GridLayout(2, true));
		toolkit.paintBordersFor(acquisitionButtonsComposite);

		Button startAcquicitionButton = toolkit.createButton(acquisitionButtonsComposite, "Start", SWT.PUSH);
		startAcquicitionButton.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));
		Button stopAcquicitionButton = toolkit.createButton(acquisitionButtonsComposite, "Stop", SWT.PUSH);
		gridData = new GridData(GridData.FILL, GridData.BEGINNING, true, false);
		stopAcquicitionButton.setLayoutData(gridData);
		startAcquicitionButton.setEnabled(false);

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(acquisitionSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		acquisitionSection.setSeparatorControl(defaultSectionSeparator);
	}

	@Override
	public void setFocus() {
		scrolledform.setFocus();
	}

}
