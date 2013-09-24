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

import gda.jython.Jython;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.beans.BeansObservables;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.forms.widgets.TableWrapData;

import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.DetectorUnavailableException;
import uk.ac.gda.exafs.data.SlitScannerModel;
import uk.ac.gda.exafs.ui.composites.NumberEditorControl;
import uk.ac.gda.exafs.ui.data.UIHelper;

public class SlitScanSection {
	public static final SlitScanSection INSTANCE = new SlitScanSection();
	private Section slitsParametersSection;
	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private SlitScanSection() {}

	@SuppressWarnings({ "static-access" })
	public void createSection(Form form, FormToolkit toolkit) {
		if (slitsParametersSection != null) {
			return;
		}
		slitsParametersSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		slitsParametersSection.setText("Slits scan");
		slitsParametersSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite slitsParametersSelectionComposite = toolkit.createComposite(slitsParametersSection, SWT.NONE);
		toolkit.paintBordersFor(slitsParametersSelectionComposite);
		slitsParametersSelectionComposite.setLayout(new GridLayout(2, false));
		slitsParametersSection.setClient(slitsParametersSelectionComposite);
		try{
			Label lbl = toolkit.createLabel(slitsParametersSelectionComposite, ClientConfig.ScannableSetup.SLIT_3_HORIZONAL_GAP.getLabel(), SWT.NONE);
			lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

			GridData gridDataForTxt = new GridData(SWT.FILL, GridData.CENTER, true, false);

			NumberEditorControl  txtGap = new NumberEditorControl(slitsParametersSelectionComposite, SWT.None, SlitScannerModel.getInstance(), SlitScannerModel.GAP_PROP_NAME, false);
			txtGap.setUnit(ClientConfig.ScannableSetup.SLIT_3_HORIZONAL_GAP.getUnit().getText());
			txtGap.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			txtGap.setLayoutData(gridDataForTxt);

			lbl = toolkit.createLabel(slitsParametersSelectionComposite, "From", SWT.NONE);
			lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

			NumberEditorControl spnFromOffset = new NumberEditorControl(slitsParametersSelectionComposite, SWT.None, SlitScannerModel.getInstance(), SlitScannerModel.FROM_OFFSET_PROP_NAME, true);
			spnFromOffset.setUnit(UnitSetup.MILLI_METER.getText());
			spnFromOffset.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			spnFromOffset.setLayoutData(gridDataForTxt);

			lbl = toolkit.createLabel(slitsParametersSelectionComposite, "To", SWT.NONE);
			lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

			NumberEditorControl spnToOffset = new NumberEditorControl(slitsParametersSelectionComposite, SWT.None, SlitScannerModel.getInstance(), SlitScannerModel.TO_OFFSET_PROP_NAME, true);
			spnToOffset.setUnit(UnitSetup.MILLI_METER.getText());
			spnToOffset.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			spnToOffset.setLayoutData(gridDataForTxt);

			lbl = toolkit.createLabel(slitsParametersSelectionComposite, "Step size", SWT.NONE);
			lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

			NumberEditorControl txtStep = new NumberEditorControl(slitsParametersSelectionComposite, SWT.None, SlitScannerModel.getInstance(), SlitScannerModel.STEP_PROP_NAME, true);
			txtStep.setUnit(UnitSetup.MILLI_METER.getText());
			txtStep.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			txtStep.setLayoutData(gridDataForTxt);

			lbl = toolkit.createLabel(slitsParametersSelectionComposite, "Integration time", SWT.NONE);
			lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

			NumberEditorControl integrationTime = new NumberEditorControl(slitsParametersSelectionComposite, SWT.None, SlitScannerModel.getInstance(), SlitScannerModel.INTEGRATION_TIME_PROP_NAME, true);
			integrationTime.setUnit(UnitSetup.MILLI_SEC.getText());
			integrationTime.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			integrationTime.setLayoutData(gridDataForTxt);

			Composite scanButtons = toolkit.createComposite(slitsParametersSelectionComposite);
			GridData gridData = new GridData(GridData.HORIZONTAL_ALIGN_FILL);
			gridData.horizontalSpan = 2;
			scanButtons.setLayoutData(gridData);
			scanButtons.setLayout(new GridLayout(2, true));

			Button startPauseButton = toolkit.createButton(scanButtons, "Start Scan", SWT.FLAT);
			startPauseButton.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));

			dataBindingCtx.bindValue(
					WidgetProperties.enabled().observe(startPauseButton),
					BeanProperties.value(SlitScannerModel.STATE_PROP_NAME).observe(SlitScannerModel.getInstance()),
					null,
					new UpdateValueStrategy() {
						@Override
						public Object convert(Object value) {
							return ((int) value == Jython.IDLE);
						}
					});

			startPauseButton.addListener(SWT.Selection, new Listener() {
				@Override
				public void handleEvent(Event event) {
					try {
						SlitScannerModel.getInstance().doScan();
					} catch (DetectorUnavailableException e) {
						UIHelper.showError("Unable to scan", e.getMessage());
					}
				}
			});

			Button stopButton = new Button(scanButtons, SWT.FLAT);
			stopButton.setText("Stop");
			stopButton.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
			dataBindingCtx.bindValue(
					WidgetProperties.enabled().observe(stopButton),
					BeanProperties.value(SlitScannerModel.STATE_PROP_NAME).observe(SlitScannerModel.getInstance()),
					null,
					new UpdateValueStrategy() {
						@Override
						public Object convert(Object value) {
							return ((int) value != Jython.IDLE);
						}
					});
			stopButton.addListener(SWT.Selection, new Listener() {
				@Override
				public void handleEvent(Event event) {
					SlitScannerModel.getInstance().doStop();
				}
			});

			Composite defaultSectionSeparator = toolkit.createCompositeSeparator(slitsParametersSection);
			toolkit.paintBordersFor(defaultSectionSeparator);
			slitsParametersSection.setSeparatorControl(defaultSectionSeparator);

			dataBindingCtx.bindValue(
					WidgetProperties.enabled().observe(slitsParametersSection),
					BeansObservables.observeValue(DetectorModel.INSTANCE, DetectorModel.DETECTOR_CONNECTED_PROP_NAME));
		} catch (Exception e) {
			UIHelper.showError("Unable to setup slit scan parameters", e.getMessage());
		}
	}
}
