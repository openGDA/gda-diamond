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

import java.io.File;

import org.dawnsci.ede.rcp.herebedragons.EnergyCalibration;
import org.dawnsci.ede.rcp.herebedragons.EnergyCalibrationWizard;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.dialogs.IDialogConstants;
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
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import gda.util.exafs.Element;
import uk.ac.gda.client.ResourceComposite;
import uk.ac.gda.client.UIHelper;
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
	private Text polynomialValueText;
	private Button runCalibrationButton;

	public EDECalibrationSection(Composite parent, int style) {
		super(parent, style);
		toolkit = new FormToolkit(parent.getDisplay());
		setupUI();
		doBinding();
	}

	private void doBinding() {
		dataBindingCtx.bindValue(
				WidgetProperties.text().observe(polynomialValueText),
				BeanProperties.value(EnergyCalibrationSetObserver.ENERGY_CALIBRATION_PROP_NAME).observe(DetectorModel.INSTANCE.getEnergyCalibrationSetObserver()));
	}

	public String getReferenceDataPath(Element element, String edgeName) {
		return REF_DATA_PATH + File.separator + element.getSymbol() + "_" + edgeName + REF_DATA_EXT;
	}

	public String loadReferenceData(String path) {
		File file = new File(path);
		if (!file.exists() || !file.canRead()) {
			return null;
		}
		return file.getAbsolutePath();
	}

	public String loadReferenceData(Element element, String edgeName) {
		return loadReferenceData( getReferenceDataPath( element, edgeName ) );
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
				String refDataPath = getReferenceDataPath(AlignmentParametersModel.INSTANCE.getElement(), AlignmentParametersModel.INSTANCE.getEdge().getEdgeType());
				String referenceDataFileName = loadReferenceData(refDataPath);
				// Display different messages for missing energy calibration data and missing scan data
				String message = "";
				if (referenceDataFileName == null) {
					message += "Reference data " + refDataPath + " is not found.\n";
				}
				if (lastEdeScanFileName == null) {
					message += "Ede spectrum data is unavailable - try doing a scan first.";
				}
				// Show warning message, but still display calibration tool if data cannot be set automatically
				if (message.length() > 0) {
					UIHelper.showWarning("Unable to set input for energy calibration tool automatically", message);
				}

				try {
					calibrationModel.setRefData(referenceDataFileName);
					calibrationModel.setSampleData(lastEdeScanFileName);
					WizardDialog wizardDialog = new WizardDialog(runCalibrationButton.getShell(), new EnergyCalibrationWizard(calibrationModel)) {
						@Override
						protected void createButtonsForButtonBar(Composite parent) {
							super.createButtonsForButtonBar(parent);
							this.getButton(IDialogConstants.FINISH_ID).setText("Apply Calibration");
							((GridData) this.getButton(IDialogConstants.FINISH_ID).getLayoutData()).widthHint = 200;
							this.getButton(IDialogConstants.FINISH_ID).getParent().layout();
						}
					};
					wizardDialog.setPageSize(1024, 768);
					if (wizardDialog.open() == Window.OK) {
						if (calibrationModel.getCalibrationDetails().getCalibrationResult() != null) {
							DetectorModel.INSTANCE.getCurrentDetector().setEnergyCalibration(calibrationModel.getCalibrationDetails());
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

//		polynomialValueLbl = toolkit.createLabel(polyLabelComposite, "", SWT.BORDER);
		polynomialValueText = toolkit.createText(polyLabelComposite, "", SWT.BORDER);
		polynomialValueText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		polynomialValueText.setEditable(false);

		Composite roisSectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(roisSectionSeparator);
		section.setSeparatorControl(roisSectionSeparator);
	}

	@Override
	protected void disposeResource() {
		dataBindingCtx.dispose();
	}

}
