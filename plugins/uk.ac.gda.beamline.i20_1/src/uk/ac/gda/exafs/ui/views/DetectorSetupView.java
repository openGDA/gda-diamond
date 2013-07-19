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

package uk.ac.gda.exafs.ui.views;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;

import org.apache.commons.lang.ArrayUtils;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.beans.BeansObservables;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.CTabFolder;
import org.eclipse.swt.custom.CTabItem;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Text;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.swt.widgets.ToolItem;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.IViewReference;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.dialogs.ListSelectionDialog;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.data.ClientConfig.DetectorSetup;
import uk.ac.gda.exafs.data.DetectorConfig;
import uk.ac.gda.exafs.ui.composites.FocusingFormComposite;
import uk.ac.gda.exafs.ui.composites.XHControlComposite;
import uk.ac.gda.exafs.ui.data.UIHelper;

public class DetectorSetupView extends ViewPart {

	private static Logger logger = LoggerFactory.getLogger(DetectorSetupView.class);
	public static String ID = "uk.ac.gda.exafs.ui.views.detectorsetupview";

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	public static IViewReference findMe() {
		IWorkbenchPage page = PlatformUI.getWorkbench().getWorkbenchWindows()[0].getActivePage();
		final IViewReference viewReference = page.findViewReference(ID);
		return viewReference;
	}

	private XHControlComposite xhComposite;

	private FormToolkit toolkit;

	private Text txtBiasVoltage;
	private Text txtExcludedStrips;

	@Override
	public void createPartControl(Composite parent) {
		this.setPartName("Alignment Configuration");
		final CTabFolder tabFolder = new CTabFolder (parent, SWT.BOTTOM);
		tabFolder.setLayout(new GridLayout());
		CTabItem setupTabItem = new CTabItem(tabFolder, SWT.NULL);
		setupTabItem.setText("Detector");

		toolkit = new FormToolkit(parent.getDisplay());
		Form form = toolkit.createForm(tabFolder);
		form.getBody().setLayout(new GridLayout());
		toolkit.decorateFormHeading(form);
		form.setText("Setup");
		createDetectorSetupFormSection(form);
		createTempratureSection(form);
		setupTabItem.setControl(form);

		CTabItem scanTabItem = new CTabItem(tabFolder, SWT.NULL);
		scanTabItem.setText("Capture configuration");

		xhComposite = new XHControlComposite(tabFolder, this);
		scanTabItem.setControl(xhComposite);
		xhComposite.setLayoutData(new GridData(GridData.FILL_BOTH));
		tabFolder.setSelection(scanTabItem);

		CTabItem focusingTabItem = new CTabItem(tabFolder, SWT.NULL);
		focusingTabItem.setText("Focusing");

		// TODO Refactor how the form is created
		FocusingFormComposite focusingForm = new FocusingFormComposite();
		ScrolledForm scrolledForm = focusingForm.getFocusingForm(toolkit, tabFolder);
		focusingTabItem.setControl(scrolledForm);
		tabFolder.setSelection(setupTabItem);
	}

	@SuppressWarnings({ "unused", "static-access" })
	private void createDetectorSetupFormSection(Form form) {
		final Section detectorSetupSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE);
		detectorSetupSection.setText("Detector configuration");
		toolkit.paintBordersFor(detectorSetupSection);
		detectorSetupSection.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		Composite defaultSelectionComposite = toolkit.createComposite(detectorSetupSection, SWT.NONE);
		toolkit.paintBordersFor(defaultSelectionComposite);
		defaultSelectionComposite.setLayout(new GridLayout(2, false));
		detectorSetupSection.setClient(defaultSelectionComposite);

		Label lblBiasVoltage = toolkit.createLabel(defaultSelectionComposite, "Voltage (V):", SWT.NONE);
		lblBiasVoltage.setLayoutData(new GridData(GridData.BEGINNING, GridData.BEGINNING, false, false));

		txtBiasVoltage = toolkit.createText(defaultSelectionComposite, "", SWT.NONE);
		txtBiasVoltage.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));

		Label lblexcludedStrips = toolkit.createLabel(defaultSelectionComposite, "Excluded strips:", SWT.NONE);
		lblexcludedStrips.setLayoutData(new GridData(GridData.BEGINNING, GridData.BEGINNING, false, false));

		txtExcludedStrips = toolkit.createText(defaultSelectionComposite, "", SWT.NONE);
		txtExcludedStrips.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));
		txtExcludedStrips.setEditable(false);

		Listener excludedStripsTxtListener = new Listener() {
			@Override
			public void handleEvent(Event event) {
				if (event.type == SWT.MouseUp | event.type == SWT.KeyUp) {
					showExcludedStripsDialog();
				}
			}
		};

		txtExcludedStrips.addListener(SWT.MouseUp, excludedStripsTxtListener);
		txtExcludedStrips.addListener(SWT.KeyUp, excludedStripsTxtListener);

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(detectorSetupSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		detectorSetupSection.setSeparatorControl(defaultSectionSeparator);

		ToolBar defaultSectionTbar = new ToolBar(detectorSetupSection, SWT.FLAT | SWT.HORIZONTAL);
		new ToolItem(defaultSectionTbar, SWT.SEPARATOR);
		ToolItem saveDefaultTBarItem = new ToolItem(defaultSectionTbar, SWT.NULL);
		saveDefaultTBarItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ETOOL_SAVE_EDIT));
		saveDefaultTBarItem.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				updateDetectorDefaultValues();
				populateDetectorDetectorValues();
			}
		});
		detectorSetupSection.setTextClient(defaultSectionTbar);
		DetectorConfig.INSTANCE.addPropertyChangeListener(DetectorConfig.CURRENT_DETECTOR_SETUP_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				populateDetectorDetectorValues();
			}
		});
		populateDetectorDetectorValues();

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(detectorSetupSection),
				BeansObservables.observeValue(DetectorConfig.INSTANCE, DetectorConfig.DETECTOR_CONNECTED_PROP_NAME),
				null,
				null);
	}

	private final ArrayList<Integer> excludedStrips = new ArrayList<Integer>();

	private void populateDetectorDetectorValues() {
		try {
			DetectorSetup currentDetectorSetup = DetectorConfig.INSTANCE.getCurrentDetectorSetup();
			if (DetectorConfig.INSTANCE.getCurrentDetectorSetup() == null) {
				txtBiasVoltage.setText("");
				txtExcludedStrips.setText("");
				return;
			}
			txtBiasVoltage.setText(currentDetectorSetup.getDetectorScannable().getBias().toString());
			int[] excludedStripsArray = currentDetectorSetup.getDetectorScannable().getExcludedStrips();
			if (excludedStripsArray == null) {
				throw new Exception("Unable to get excluded strips information from Detector");
			}
			excludedStrips.clear();
			if (excludedStripsArray.length > 0) {
				for (int selected : excludedStripsArray) {
					//FIXME This should be in the model code
					Integer stringNo = currentDetectorSetup.getStrips()[selected - DetectorSetup.MIN_ROIs];
					excludedStrips.add(stringNo);
				}
			}
			updateExcludedStripsText();
		} catch (Exception e) {
			String errorMessage = "Unable to get Detector parameter. ";
			logger.error(errorMessage, e);
			UIHelper.showError(errorMessage, e.getMessage());
		}
	}

	private void updateExcludedStripsText() {
		StringBuilder excludedListCsvString = new StringBuilder();
		if (!excludedStrips.isEmpty()) {
			for (Integer selected : excludedStrips) {
				excludedListCsvString.append(selected);
				excludedListCsvString.append(", ");
			}
			excludedListCsvString.delete(excludedListCsvString.length() - 2, excludedListCsvString.length());
		}
		txtExcludedStrips.setText(excludedListCsvString.toString());
	}

	private void showExcludedStripsDialog() {
		ListSelectionDialog dialog =
				new ListSelectionDialog(
						Display.getDefault().getActiveShell(),
						DetectorConfig.INSTANCE.getCurrentDetectorSetup().getStrips(),
						new ArrayContentProvider(),
						new LabelProvider(),
						"Select excluded strips");
		dialog.setInitialElementSelections(excludedStrips);
		if (dialog.open() == Window.OK) {
			Object[] selection = dialog.getResult();
			excludedStrips.clear();
			if (selection.length > 0) {
				for (Object selected : selection) {
					Integer stringNo = (Integer) selected;
					excludedStrips.add(stringNo);
				}
			}
			updateExcludedStripsText();
		}
	}

	private void updateDetectorDefaultValues() {
		try {
			if (txtBiasVoltage.getText().isEmpty()) {
				throw new Exception("Enpty voltage value");
			}
			double voltage = Double.valueOf(txtBiasVoltage.getText());
			if (!DetectorConfig.INSTANCE.getCurrentDetectorSetup().isVoltageInRange(voltage)) {
				throw new Exception("Voltage out of range");
			}
			DetectorConfig.INSTANCE.getCurrentDetectorSetup().getDetectorScannable().setBias(voltage);
			DetectorConfig.INSTANCE.getCurrentDetectorSetup().getDetectorScannable().setExcludedStrips(ArrayUtils.toPrimitive(excludedStrips.toArray(new Integer[excludedStrips.size()])));
		} catch (Exception e) {
			String errorMessage = "Unable to save Detector parameter ";
			logger.error(errorMessage, e);
			UIHelper.showError(errorMessage, e.getMessage());
		}
	}

	@SuppressWarnings({ "unused", "static-access" })
	private void createTempratureSection(Form form) {
		final Section temperatureSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR);
		temperatureSection.setText("Temperature");
		toolkit.paintBordersFor(temperatureSection);
		temperatureSection.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		Composite temperatureSelectionComposite = toolkit.createComposite(temperatureSection, SWT.NONE);
		toolkit.paintBordersFor(temperatureSelectionComposite);
		temperatureSelectionComposite.setLayout(new GridLayout(2, false));
		temperatureSection.setClient(temperatureSelectionComposite);
		ToolBar temperatureSectionTbar = new ToolBar(temperatureSection, SWT.FLAT | SWT.HORIZONTAL);
		new ToolItem(temperatureSectionTbar, SWT.SEPARATOR);
		ToolItem refreshTemperatureTBarItem = new ToolItem(temperatureSectionTbar, SWT.NULL);
		refreshTemperatureTBarItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ELCL_SYNCED));
		refreshTemperatureTBarItem.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				// FIXME update temperature
			}
		});
		temperatureSection.setTextClient(temperatureSectionTbar);

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(temperatureSection),
				BeansObservables.observeValue(DetectorConfig.INSTANCE, DetectorConfig.DETECTOR_CONNECTED_PROP_NAME),
				null,
				null);
	}

	@Override
	public void setFocus() {
	}

	public void startCollectingRates() {
		xhComposite.startCollectingRates();
	}

	public void stopCollectingRates() {
		xhComposite.stopCollectingRates();
	}
}
