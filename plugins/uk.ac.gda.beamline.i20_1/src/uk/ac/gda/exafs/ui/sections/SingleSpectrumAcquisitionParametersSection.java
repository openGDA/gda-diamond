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
import gda.scan.ede.datawriters.EdeAsciiFileWriter;

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
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.forms.widgets.TableWrapData;

import uk.ac.diamond.scisoft.analysis.SDAPlotter;
import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.io.DataHolder;
import uk.ac.diamond.scisoft.analysis.io.LoaderFactory;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.SingleSpectrumModel;
import uk.ac.gda.exafs.ui.composites.NumberEditorControl;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.perspectives.AlignmentPerspective;

public class SingleSpectrumAcquisitionParametersSection {
	public static final SingleSpectrumAcquisitionParametersSection INSTANCE = new SingleSpectrumAcquisitionParametersSection();

	private final DataBindingContext dataBindingCtx = new DataBindingContext();
	private Section section;

	private ComboViewer cmbFirstStripViewer;

	private StructuredViewer cmbLastStripViewer;

	protected Binding cmbFirstStripViewerBinding;

	protected Binding cmbLastStripViewerBinding;

	private SingleSpectrumAcquisitionParametersSection() {}

	@SuppressWarnings({ "static-access" })
	public void createEdeCalibrationSection(Form form, FormToolkit toolkit) throws Exception {
		//		if (section != null) {
		//			return;
		//		}
		section = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
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
		});

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
					SingleSpectrumModel.INSTANCE.doCollection();
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

//		SingleSpectrumModel.INSTANCE.addPropertyChangeListener(SingleSpectrumModel.FILE_NAME_PROP_NAME, new PropertyChangeListener() {
//			@Override
//			public void propertyChange(PropertyChangeEvent evt) {
//				Object value = evt.getNewValue();
//				if (value == null) {
//					return;
//				}
//				String fileName = (String) value;
//				File file = new File(fileName);
//				if (file.exists() && file.canRead()) {
//					try {
//						DataHolder dataHolder = LoaderFactory.getData(fileName);
//						AbstractDataset strips = (AbstractDataset) dataHolder.getLazyDataset(EdeAsciiFileWriter.STRIP_COLUMN_NAME).getSlice();
//						AbstractDataset dk = (AbstractDataset) dataHolder.getLazyDataset(EdeAsciiFileWriter.I0_DARK_COLUMN_NAME).getSlice();
//						AbstractDataset i0 = (AbstractDataset) dataHolder.getLazyDataset(EdeAsciiFileWriter.I0_RAW_COLUMN_NAME).getSlice();
//						AbstractDataset it = (AbstractDataset) dataHolder.getLazyDataset(EdeAsciiFileWriter.IT_RAW_COLUMN_NAME).getSlice();
//						AbstractDataset logI0It = (AbstractDataset) dataHolder.getLazyDataset(EdeAsciiFileWriter.LN_I0_IT_COLUMN_NAME).getSlice();
//						SDAPlotter.plot(AlignmentPerspective.SINGLE_SPECTRUM_PLOT_VIEW_NAME, fileName, strips, new AbstractDataset[]{dk,i0,it,logI0It});
//					} catch (Exception e) {
//						UIHelper.showError("Unable to plot the data", e.getMessage());
//					}
//				}
//			}
//		});

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(defaultSectionSeparator);
		section.setSeparatorControl(defaultSectionSeparator);
	}

	private void bindUpperAndLowerChannelComboViewers() {
		cmbFirstStripViewerBinding = dataBindingCtx.bindValue(
				ViewersObservables.observeSingleSelection(cmbFirstStripViewer),
				BeansObservables.observeValue(DetectorModel.INSTANCE, DetectorModel.LOWER_CHANNEL_PROP_NAME));
		cmbLastStripViewerBinding = dataBindingCtx.bindValue(
				ViewersObservables.observeSingleSelection(cmbLastStripViewer),
				BeansObservables.observeValue(DetectorModel.INSTANCE, DetectorModel.UPPER_CHANNEL_PROP_NAME));
	}
}
