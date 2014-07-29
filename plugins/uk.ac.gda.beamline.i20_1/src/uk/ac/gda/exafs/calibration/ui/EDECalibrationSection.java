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

package uk.ac.gda.exafs.calibration.ui;

import gda.configuration.properties.LocalProperties;
import gda.device.DeviceException;
import gda.util.exafs.Element;

import java.io.File;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.window.Window;
import org.eclipse.jface.wizard.WizardDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.client.ResourceComposite;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.calibration.data.EnergyCalibration;
import uk.ac.gda.exafs.data.AlignmentParametersModel;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.DetectorModel.EnergyCalibrationSetObserver;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentModelHolder;

public class EDECalibrationSection extends ResourceComposite {

	private static final Logger logger = LoggerFactory.getLogger(EDECalibrationSection.class);

	public static final String REF_DATA_PATH = LocalProperties.getConfigDir() + "edeRefData";
	public static final String REF_DATA_EXT = ".dat";

	private final FormToolkit toolkit;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();
	private Section section;
	private Label polynomialValueLbl;
	private Button runCalibrationButton;

	public EDECalibrationSection(Composite parent, int style) {
		super(parent, style);
		toolkit = new FormToolkit(parent.getDisplay());
		setupUI();
		doBinding();
	}

	private void doBinding() {
		dataBindingCtx.bindValue(
				WidgetProperties.text().observe(polynomialValueLbl),
				BeanProperties.value(EnergyCalibrationSetObserver.ENERGY_CALIBRATION_SET_PROP_NAME).observe(DetectorModel.INSTANCE.getEnergyCalibrationSetObserver()),
				null,
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						try {
							return ((boolean) value) ? DetectorModel.INSTANCE.getCurrentDetector().getEnergyCalibration().getCalibrationResult().toString() : "";
						} catch (Exception e) {
							return "";
						}
					}
				});
	}

	public String loadReferenceData(Element element, String edgeName) {
		// FIXME Refactor the file name pattern out
		File file = new File(REF_DATA_PATH, element.getSymbol() + "_" + edgeName + REF_DATA_EXT);
		if (!file.exists() || !file.canRead()) {
			return null;
		}
		return  file.getAbsolutePath();
	}

	private void setupUI() {
		this.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		section = toolkit.createSection(this, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		section.setText("EDE Calibration");
		toolkit.paintBordersFor(section);
		section.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		Composite sectionComposite = toolkit.createComposite(section, SWT.NONE);
		toolkit.paintBordersFor(sectionComposite);
		section.setClient(sectionComposite);
		sectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));


		runCalibrationButton = toolkit.createButton(sectionComposite, "Run EDE Calibration", SWT.None);
		GridData gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		runCalibrationButton.setLayoutData(gridData);
		runCalibrationButton.addSelectionListener(new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent selectionEvent) {
				EnergyCalibration calibrationModel = new EnergyCalibration();
				String lastEdeScanFileName = ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentModel().getFileName();
				String referenceDataFileName = loadReferenceData(AlignmentParametersModel.INSTANCE.getElement(), AlignmentParametersModel.INSTANCE.getEdge().getEdgeType());
				if (lastEdeScanFileName == null || referenceDataFileName == null) {
					UIHelper.showError("Unable to set energy calibration", "Reference or Ede spectrum data is unavailable");
					return;
				}
				try {
					calibrationModel.setRefData(referenceDataFileName);
					calibrationModel.setEdeData(lastEdeScanFileName);
					WizardDialog wizardDialog = new WizardDialog(runCalibrationButton.getShell(), new EnergyCalibrationWizard(calibrationModel));
					wizardDialog.setPageSize(1024, 768);
					if (wizardDialog.open() == Window.OK) {
						if (calibrationModel.getCalibrationDetails().getCalibrationResult() != null) {
							try {
								DetectorModel.INSTANCE.getCurrentDetector().setEnergyCalibration(calibrationModel.getCalibrationDetails());
							} catch (DeviceException e1) {
								UIHelper.showError("Unable to set energy calibration", e1.getMessage());
								logger.warn("Unable to set energy calibration", e1);
							}
						}
					}
				} catch (Exception e) {
					logger.error("Unable to perform energy calibration", e);
				}
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				this.widgetSelected(e);
			}
		});

		Composite polyLabelComposite = toolkit.createComposite(sectionComposite, SWT.None);
		polyLabelComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		polyLabelComposite.setLayout(new GridLayout(2, false));

		final Label polynomialLbl = toolkit.createLabel(polyLabelComposite, "Calibration polynomial", SWT.NONE);
		polynomialLbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		polynomialValueLbl = toolkit.createLabel(polyLabelComposite, "", SWT.BORDER);
		polynomialValueLbl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Composite roisSectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(roisSectionSeparator);
		section.setSeparatorControl(roisSectionSeparator);
	}

	@Override
	protected void disposeResource() {
		dataBindingCtx.dispose();
	}

}