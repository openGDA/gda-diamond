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

package uk.ac.gda.exafs.alignment.ui;

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
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.jython.Jython;
import uk.ac.gda.client.ResourceComposite;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.observablemodels.ScannableWrapper;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.DetectorUnavailableException;
import uk.ac.gda.exafs.data.ScannableSetup;
import uk.ac.gda.exafs.data.SlitsScanModel;
import uk.ac.gda.ui.components.NumberEditorControl;

public class SlitsScanSection extends ResourceComposite {

	private final FormToolkit toolkit;

	private Section slitsParametersSection;

	private static Logger logger = LoggerFactory.getLogger(SlitsScanSection.class);

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	public SlitsScanSection(Composite parent, int style) {
		super(parent, style);
		toolkit = new FormToolkit(parent.getDisplay());
		setupUI();
	}

	private void setupUI() {
		this.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		slitsParametersSection = toolkit.createSection(this, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		slitsParametersSection.setText("Slits scan");
		slitsParametersSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		Composite slitsParametersSelectionComposite = toolkit.createComposite(slitsParametersSection, SWT.NONE);
		toolkit.paintBordersFor(slitsParametersSelectionComposite);
		slitsParametersSelectionComposite.setLayout(new GridLayout(2, false));
		slitsParametersSection.setClient(slitsParametersSelectionComposite);
		try{
			Label lbl = toolkit.createLabel(slitsParametersSelectionComposite, ScannableSetup.SLIT_3_HORIZONAL_GAP.getLabel(), SWT.NONE);
			lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

			GridData gridDataForTxt = new GridData(SWT.FILL, GridData.CENTER, true, false);

			NumberEditorControl txtGap = new NumberEditorControl(slitsParametersSelectionComposite, SWT.None, SlitsScanModel.getInstance(), SlitsScanModel.GAP_PROP_NAME, false);
			txtGap.setUnit(ScannableSetup.SLIT_3_HORIZONAL_GAP.getUnit().getText());
			txtGap.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			ScannableWrapper scannableWrapper = ScannableSetup.SLIT_3_HORIZONAL_GAP.getScannableWrapper();
			if (scannableWrapper.getLowerLimit() != null && scannableWrapper.getUpperLimit() != null) {
				txtGap.setRange(scannableWrapper.getLowerLimit(), scannableWrapper.getUpperLimit());
			}
			txtGap.setLayoutData(gridDataForTxt);

			lbl = toolkit.createLabel(slitsParametersSelectionComposite, "From", SWT.NONE);
			lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

			NumberEditorControl spnFromOffset = new NumberEditorControl(slitsParametersSelectionComposite, SWT.None, SlitsScanModel.getInstance(), SlitsScanModel.FROM_OFFSET_PROP_NAME, true);
			spnFromOffset.setUnit(UnitSetup.MILLI_METER.getText());
			spnFromOffset.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			spnFromOffset.setLayoutData(gridDataForTxt);

			lbl = toolkit.createLabel(slitsParametersSelectionComposite, "To", SWT.NONE);
			lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

			NumberEditorControl spnToOffset = new NumberEditorControl(slitsParametersSelectionComposite, SWT.None, SlitsScanModel.getInstance(), SlitsScanModel.TO_OFFSET_PROP_NAME, true);
			spnToOffset.setUnit(UnitSetup.MILLI_METER.getText());
			spnToOffset.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			spnToOffset.setLayoutData(gridDataForTxt);

			lbl = toolkit.createLabel(slitsParametersSelectionComposite, "Step size", SWT.NONE);
			lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

			NumberEditorControl txtStep = new NumberEditorControl(slitsParametersSelectionComposite, SWT.None, SlitsScanModel.getInstance(), SlitsScanModel.STEP_PROP_NAME, true);
			txtStep.setUnit(UnitSetup.MILLI_METER.getText());
			txtStep.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
			txtStep.setLayoutData(gridDataForTxt);

			lbl = toolkit.createLabel(slitsParametersSelectionComposite, "Integration time", SWT.NONE);
			lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

			NumberEditorControl integrationTime = new NumberEditorControl(slitsParametersSelectionComposite, SWT.None, SlitsScanModel.getInstance(), SlitsScanModel.INTEGRATION_TIME_PROP_NAME, true);
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
					BeanProperties.value(SlitsScanModel.STATE_PROP_NAME).observe(SlitsScanModel.getInstance()),
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
						SlitsScanModel.getInstance().doScan();
					} catch (DetectorUnavailableException e) {
						UIHelper.showError("Unable to scan", e.getMessage());
						logger.error("Unable to scan", e);
					}
				}
			});

			Button stopButton = new Button(scanButtons, SWT.FLAT);
			stopButton.setText("Stop");
			stopButton.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
			dataBindingCtx.bindValue(
					WidgetProperties.enabled().observe(stopButton),
					BeanProperties.value(SlitsScanModel.STATE_PROP_NAME).observe(SlitsScanModel.getInstance()),
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
					SlitsScanModel.getInstance().stopScan();
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
			logger.error("Unable to setup slit scan parameters", e);
		}
	}

	@Override
	protected void disposeResource() {
		dataBindingCtx.dispose();

	}
}
