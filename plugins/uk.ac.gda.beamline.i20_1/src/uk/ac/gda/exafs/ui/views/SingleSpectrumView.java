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

import gda.device.Scannable;
import gda.device.detector.XHDetector;
import gda.device.scannable.AlignmentStage;
import gda.device.scannable.AlignmentStageScannable;
import gda.device.scannable.AlignmentStageScannable.AlignmentStageDevice;
import gda.scan.ede.EdeAsciiFileWriter;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.File;

import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.beans.BeansObservables;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.databinding.viewers.ViewersObservables;
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
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.forms.widgets.TableWrapData;
import org.eclipse.ui.forms.widgets.TableWrapLayout;
import org.eclipse.ui.part.ViewPart;

import uk.ac.diamond.scisoft.analysis.SDAPlotter;
import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.io.DataHolder;
import uk.ac.diamond.scisoft.analysis.io.LoaderFactory;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.ScannableSetup;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.SingleSpectrumModel;
import uk.ac.gda.exafs.ui.composites.NumberEditorControl;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.perspectives.AlignmentPerspective;
import uk.ac.gda.exafs.ui.sections.EDECalibrationSection;

public class SingleSpectrumView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.singlespectrumview";

	private FormToolkit toolkit;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private ScrolledForm scrolledform;

	private ComboViewer cmbFirstStripViewer;

	private ComboViewer cmbLastStripViewer;

	// Using index 0 for x and 1 for y
	private final Binding[] i0Binding = new Binding[2];
	private final Binding[] iYBinding = new Binding[2];

	private Binding cmbFirstStripViewerBinding;

	private Binding cmbLastStripViewerBinding;

	@Override
	public void createPartControl(Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		scrolledform = toolkit.createScrolledForm(parent);
		Form form = scrolledform.getForm();
		form.getBody().setLayout(new TableWrapLayout());
		toolkit.decorateFormHeading(form);
		form.setText("Single spectrum / E calibration");
		Composite formParent = form.getBody();
		try {
			createSamplePosition("I0 sample position", formParent, i0Binding, AlignmentStageDevice.hole.name(), SingleSpectrumModel.I0_X_POSITION_PROP_NAME, SingleSpectrumModel.I0_Y_POSITION_PROP_NAME);
			createSamplePosition("It sample position", formParent, iYBinding, AlignmentStageDevice.foil.name(), SingleSpectrumModel.IT_X_POSITION_PROP_NAME, SingleSpectrumModel.IT_Y_POSITION_PROP_NAME);
			createAcquisitionPosition(formParent);
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
		}
		EDECalibrationSection.INSTANCE.createEdeCalibrationSection(form, toolkit);
	}

	private void createSamplePosition(String title, Composite body, final Binding[] binding, final String alignmentStageDeviceName, final String xPostionPropName, final String yPostionPropName) throws Exception {
		@SuppressWarnings("static-access")
		final Section section = toolkit.createSection(body, Section.DESCRIPTION | Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		section.setText(title);
		section.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite samplePositionSectionComposite = toolkit.createComposite(section, SWT.NONE);
		samplePositionSectionComposite.setLayout(new GridLayout());
		toolkit.paintBordersFor(samplePositionSectionComposite);
		section.setClient(samplePositionSectionComposite);

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

		final NumberEditorControl xPosition = new NumberEditorControl(xPositionComposite, SWT.None, SingleSpectrumModel.INSTANCE, xPostionPropName, false);
		xPosition.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		xPosition.setUnit(ClientConfig.UnitSetup.MILLI_METER.getText());
		xPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite yPositionComposite = toolkit.createComposite(xyPositionComposite, SWT.NONE);
		toolkit.paintBordersFor(yPositionComposite);
		yPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		yPositionComposite.setLayout(new GridLayout(2, false));

		Label yPosLabel = toolkit.createLabel(yPositionComposite, "Y position", SWT.None);
		yPosLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		final NumberEditorControl yPosition = new NumberEditorControl(yPositionComposite, SWT.None, SingleSpectrumModel.INSTANCE, yPostionPropName, false);
		yPosition.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		yPosition.setUnit(ClientConfig.UnitSetup.MILLI_METER.getText());
		yPosition.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite sampleCustomPositionComposite = toolkit.createComposite(samplePositionSectionComposite, SWT.NONE);
		toolkit.paintBordersFor(sampleCustomPositionComposite);
		sampleCustomPositionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		sampleCustomPositionComposite.setLayout(new GridLayout(2, false));

		final Button customPositionButton = toolkit.createButton(sampleCustomPositionComposite, "Custom position", SWT.CHECK);
		customPositionButton.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		Button customReadPositionButton = toolkit.createButton(sampleCustomPositionComposite, "Read current", SWT.PUSH);
		customReadPositionButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, true, false));

		dataBindingCtx.bindValue(WidgetProperties.enabled().observe(customReadPositionButton), WidgetProperties.selection().observe(customPositionButton));

		customPositionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				updateBinding(section, binding, customPositionButton, xPosition, yPosition, alignmentStageDeviceName, xPostionPropName, yPostionPropName);
			}
		});
		updateBinding(section, binding, customPositionButton, xPosition, yPosition, alignmentStageDeviceName, xPostionPropName, yPostionPropName);

		Composite sectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(sectionSeparator);
		section.setSeparatorControl(sectionSeparator);
	}

	private void updateBinding(Section section, Binding[] binding, Button customPositionButton, NumberEditorControl xPosition, NumberEditorControl yPosition, String alignmentStageDeviceName, String propXName, String propYName) {
		Scannable scannable;
		try {
			scannable = ScannableSetup.ALIGNMENT_STAGE.getScannable();
		} catch (Exception e) {
			UIHelper.showError("Unable to get scannable " + ScannableSetup.ALIGNMENT_STAGE.getLabel(), e.getMessage());
			return;
		}
		if (scannable instanceof AlignmentStage) {
			final AlignmentStage alignmentStage = (AlignmentStage) scannable;
			xPosition.setEditable(customPositionButton.getSelection());
			yPosition.setEditable(customPositionButton.getSelection());
			if (!customPositionButton.getSelection()) {
				AlignmentStageScannable.Location location = alignmentStage.getAlignmentStageDevice(alignmentStageDeviceName).getLocation();
				if (binding[0] == null) {
					binding[0] = dataBindingCtx.bindValue(
							BeanProperties.value(AlignmentStageScannable.Location.X_POS_PROP_NAME).observe(location),
							BeanProperties.value(propXName).observe(SingleSpectrumModel.INSTANCE),
							new UpdateValueStrategy(),
							new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER));
					binding[0].updateTargetToModel();
				}
				if (binding[1] == null) {
					binding[1] = dataBindingCtx.bindValue(
							BeanProperties.value(AlignmentStageScannable.Location.Y_POS_PROP_NAME).observe(location),
							BeanProperties.value(propYName).observe(SingleSpectrumModel.INSTANCE),
							new UpdateValueStrategy(),
							new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER));
					binding[1].updateTargetToModel();
				}
				section.setDescription("Using alignment stage " + alignmentStageDeviceName + " as sample x and y position");
			} else {
				if (binding[0] != null) {
					dataBindingCtx.removeBinding(binding[0]);
					binding[0].dispose();
					binding[0] = null;
				}
				if (binding[1] != null) {
					dataBindingCtx.removeBinding(binding[1]);
					binding[1].dispose();
					binding[1] = null;
				}
				section.setDescription("Using custom position");
			}
		}
	}

	private void createAcquisitionPosition(Composite body) throws Exception {
		@SuppressWarnings("static-access")
		final Section section = toolkit.createSection(body, Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		section.setText("Acquisition settings");
		section.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite sectionComposite = toolkit.createComposite(section, SWT.NONE);
		sectionComposite.setLayout(new GridLayout());
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

		DetectorModel.INSTANCE.addPropertyChangeListener(DetectorModel.DETECTOR_CONNECTED_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				boolean detectorConnected = (boolean) evt.getNewValue();
				if (detectorConnected) {
					bindUpperAndLowerComboViewers();
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
		});

		if (DetectorModel.INSTANCE.getCurrentDetector() != null) {
			bindUpperAndLowerComboViewers();
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
		Label i0IntegrationTimeLabel = toolkit.createLabel(acquisitionSettingsComposite, "I0 Integration time");
		i0IntegrationTimeLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		NumberEditorControl i0IntegrationTimeText = new NumberEditorControl(acquisitionSettingsComposite, SWT.None, SingleSpectrumModel.INSTANCE, SingleSpectrumModel.I0_INTEGRATION_TIME_PROP_NAME, true);
		i0IntegrationTimeText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		i0IntegrationTimeText.setUnit(ClientConfig.UnitSetup.MILLI_SEC.getText());
		i0IntegrationTimeText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label i0NoOfAccumulationLabel = toolkit.createLabel(acquisitionSettingsComposite, "I0 Number of accumulations");
		i0NoOfAccumulationLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		NumberEditorControl i0NoOfAccumulationText = new NumberEditorControl(acquisitionSettingsComposite, SWT.None, SingleSpectrumModel.INSTANCE, SingleSpectrumModel.I0_NUMBER_OF_ACCUMULATIONS_PROP_NAME, true);
		i0NoOfAccumulationText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label itIntegrationTimeLabel = toolkit.createLabel(acquisitionSettingsComposite, "It Integration time");
		itIntegrationTimeLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		NumberEditorControl itIntegrationTimeText = new NumberEditorControl(acquisitionSettingsComposite, SWT.None, SingleSpectrumModel.INSTANCE, SingleSpectrumModel.IT_INTEGRATION_TIME_PROP_NAME, true);
		itIntegrationTimeText.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		itIntegrationTimeText.setUnit(ClientConfig.UnitSetup.MILLI_SEC.getText());
		itIntegrationTimeText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label itNoOfAccumulationLabel = toolkit.createLabel(acquisitionSettingsComposite, "It Number of accumulations");
		itNoOfAccumulationLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		NumberEditorControl itNoOfAccumulationText = new NumberEditorControl(acquisitionSettingsComposite, SWT.None, SingleSpectrumModel.INSTANCE, SingleSpectrumModel.IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME, true);
		itNoOfAccumulationText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite acquisitionSettingsFileNameComposite = new Composite(sectionComposite, SWT.NONE);
		acquisitionSettingsFileNameComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, true));
		acquisitionSettingsFileNameComposite.setLayout(new GridLayout(2, false));
		toolkit.paintBordersFor(acquisitionSettingsFileNameComposite);

		Label fileNameLabel = toolkit.createLabel(acquisitionSettingsFileNameComposite, "Filename");
		fileNameLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		Text fileNameText = toolkit.createText(acquisitionSettingsFileNameComposite, "", SWT.None);
		fileNameText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		dataBindingCtx.bindValue(WidgetProperties.text().observe(fileNameText), BeanProperties.value(SingleSpectrumModel.FILE_NAME_PROP_NAME).observe(SingleSpectrumModel.INSTANCE));
		fileNameText.setEditable(false);

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
					SingleSpectrumModel.INSTANCE.doScan();
				} catch (Exception e) {
					UIHelper.showError("Unable to scan", e.getMessage());
				}
			}
		});

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(startAcquicitionButton),
				BeanProperties.value(SingleSpectrumModel.SCANNING_PROP_NAME).observe(SingleSpectrumModel.INSTANCE),
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
				BeanProperties.value(SingleSpectrumModel.SCANNING_PROP_NAME).observe(SingleSpectrumModel.INSTANCE));
		stopAcquicitionButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				SingleSpectrumModel.INSTANCE.doStop();
			}
		});

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(section),
				BeansObservables.observeValue(DetectorModel.INSTANCE, DetectorModel.DETECTOR_CONNECTED_PROP_NAME));

		SingleSpectrumModel.INSTANCE.addPropertyChangeListener(SingleSpectrumModel.FILE_NAME_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				Object value = evt.getNewValue();
				if (value == null) {
					return;
				}
				String fileName = (String) value;
				File file = new File(fileName);
				if (file.exists() && file.canRead()) {
					try {
						DataHolder dataHolder = LoaderFactory.getData(fileName);
						AbstractDataset strips = (AbstractDataset) dataHolder.getLazyDataset(EdeAsciiFileWriter.STRIP_COLUMN_NAME).getSlice();
						AbstractDataset logI0It = (AbstractDataset) dataHolder.getLazyDataset(EdeAsciiFileWriter.LN_I0_IT_COLUMN_NAME).getSlice();
						SDAPlotter.plot(AlignmentPerspective.SINGLE_SPECTRUM_PLOT_VIEW_NAME, fileName, strips, new AbstractDataset[]{logI0It});
						PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(AlignmentPerspective.SINGLE_SPECTRUM_PLOT_VIEW_ID);
					} catch (Exception e) {
						UIHelper.showError("Unable to plot the data", e.getMessage());
					}
				}
			}
		});

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(defaultSectionSeparator);
		section.setSeparatorControl(defaultSectionSeparator);
	}

	private void bindUpperAndLowerComboViewers() {
		cmbFirstStripViewerBinding = dataBindingCtx.bindValue(
				ViewersObservables.observeSingleSelection(cmbFirstStripViewer),
				BeansObservables.observeValue(DetectorModel.INSTANCE, DetectorModel.LOWER_CHANNEL_PROP_NAME));
		cmbLastStripViewerBinding = dataBindingCtx.bindValue(
				ViewersObservables.observeSingleSelection(cmbLastStripViewer),
				BeansObservables.observeValue(DetectorModel.INSTANCE, DetectorModel.UPPER_CHANNEL_PROP_NAME));
	}

	@Override
	public void setFocus() {
		scrolledform.setFocus();
	}

}
