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

import java.util.ArrayList;

import org.apache.commons.lang.ArrayUtils;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.ComboViewer;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.StructuredSelection;
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
import uk.ac.gda.exafs.ui.composites.FocusingFormComposite;
import uk.ac.gda.exafs.ui.composites.XHControlComposite;
import uk.ac.gda.exafs.ui.data.UIHelper;

/**
 * Shows detector controls for use when aligning the beamline.
 * <p>
 * Combobox to choose the detector type to show detector-specific composites.
 */
public class DetectorSetupView extends ViewPart {

	private static Logger logger = LoggerFactory.getLogger(DetectorSetupView.class);

	public static String ID = "uk.ac.gda.exafs.ui.views.detectorsetupview";

	public static IViewReference findMe() {
		IWorkbenchPage page = PlatformUI.getWorkbench().getWorkbenchWindows()[0].getActivePage();
		final IViewReference viewReference = page.findViewReference(ID);
		return viewReference;
	}

	private XHControlComposite xhComposite;
	private Text txtBiasVoltage;
	private Text txtExcludedStrips;
	private FormToolkit toolkit;
	private DetectorSetup activeDetectorSetup;
	private ComboViewer cmbDetectorType;

	@Override
	public void createPartControl(Composite parent) {
		activeDetectorSetup = DetectorSetup.getActiveDetectorSetup();
		if (activeDetectorSetup == null) {
			activeDetectorSetup = DetectorSetup.getAvailableDetectorSetups()[0];
		}
		this.setPartName(activeDetectorSetup.name() + " Detector");
		final CTabFolder tabFolder = new CTabFolder (parent, SWT.BOTTOM);
		tabFolder.setLayout(new GridLayout());
		CTabItem setupTabItem = new CTabItem(tabFolder, SWT.NULL);
		setupTabItem.setText("Detector");

		toolkit = new FormToolkit(parent.getDisplay());
		Form form = toolkit.createForm(tabFolder);
		form.getBody().setLayout(new GridLayout());
		toolkit.decorateFormHeading(form);
		form.setText("Setup");
		createFormDefaultSection(form);
		createTempratureSection(form);
		setupTabItem.setControl(form);

		// Capture Tab
		CTabItem scanTabItem = new CTabItem(tabFolder, SWT.NULL);
		scanTabItem.setText("Capture configuration");

		xhComposite = new XHControlComposite(tabFolder, this);
		scanTabItem.setControl(xhComposite);
		xhComposite.setLayoutData(new GridData(GridData.FILL_BOTH));
		tabFolder.setSelection(scanTabItem);

		// Focusing
		CTabItem focusingTabItem = new CTabItem(tabFolder, SWT.NULL);
		focusingTabItem.setText("Focusing");

		// TODO Refactor how the form is created
		FocusingFormComposite focusingForm = new FocusingFormComposite();
		ScrolledForm scrolledForm = focusingForm.getFocusingForm(toolkit, tabFolder);
		focusingTabItem.setControl(scrolledForm);
		tabFolder.setSelection(setupTabItem);
	}

	@SuppressWarnings({ "unused", "static-access" })
	private void createFormDefaultSection(Form form) {
		final Section defaultSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE);
		defaultSection.setText("Default");
		toolkit.paintBordersFor(defaultSection);
		defaultSection.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		Composite defaultSelectionComposite = toolkit.createComposite(defaultSection, SWT.NONE);
		toolkit.paintBordersFor(defaultSelectionComposite);
		defaultSelectionComposite.setLayout(new GridLayout(2, false));
		defaultSection.setClient(defaultSelectionComposite);

		Label lblDetector = toolkit.createLabel(defaultSelectionComposite, "Detector:", SWT.NONE);
		lblDetector.setLayoutData(new GridData(GridData.BEGINNING, GridData.BEGINNING, false, false));
		cmbDetectorType = new ComboViewer(defaultSelectionComposite, SWT.READ_ONLY);
		cmbDetectorType.setContentProvider(ArrayContentProvider.getInstance());
		cmbDetectorType.setLabelProvider(new LabelProvider() {
			@Override
			public String getText(Object element) {
				return ((DetectorSetup) element).name();
			}
		});
		cmbDetectorType.getCombo().setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

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

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(defaultSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		defaultSection.setSeparatorControl(defaultSectionSeparator);

		ToolBar defaultSectionTbar = new ToolBar(defaultSection, SWT.FLAT | SWT.HORIZONTAL);
		new ToolItem(defaultSectionTbar, SWT.SEPARATOR);
		ToolItem saveDefaultTBarItem = new ToolItem(defaultSectionTbar, SWT.NULL);
		saveDefaultTBarItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ETOOL_SAVE_EDIT));
		saveDefaultTBarItem.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				updateDetectorDefaultValues();
				populateDetectorDefaultValues();
			}
		});
		defaultSection.setTextClient(defaultSectionTbar);
		populateDetectorDefaultValues();

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
	}

	private final ArrayList<Integer> excludedStrips = new ArrayList<Integer>();

	private void showExcludedStripsDialog() {
		ListSelectionDialog dialog =
				new ListSelectionDialog(Display.getDefault().getActiveShell(), DetectorSetup.getActiveDetectorSetup().createArrayOfStrips(), new ArrayContentProvider(), new LabelProvider(), "Select excluded strips");
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

	private void updateDetectorDefaultValues() {
		try {
			// REVIEW Use data binding validation
			if (txtBiasVoltage.getText().isEmpty()) {
				throw new Exception("Enpty voltage value");
			}
			double voltage = Double.valueOf(txtBiasVoltage.getText());
			if (!activeDetectorSetup.isVoltageInRange(voltage)) {
				throw new Exception("Voltage out of range");
			}
			activeDetectorSetup.getDetectorScannable().setBias(voltage);
			activeDetectorSetup.getDetectorScannable().setExcludedStrips(ArrayUtils.toPrimitive(excludedStrips.toArray(new Integer[excludedStrips.size()])));
		} catch (Exception e) {
			String errorMessage = "Unable to save Detector parameter ";
			logger.error(errorMessage, e);
			UIHelper.showError(errorMessage, e.getMessage());
		}
	}

	private void populateDetectorDefaultValues() {
		// REVIEW Use data binding
		try {

			DetectorSetup detector = DetectorSetup.getActiveDetectorSetup();
			if (detector == null) {
				detector = DetectorSetup.getAvailableDetectorSetups()[0];
			}
			populateCmbDetectorType(detector);

			txtBiasVoltage.setText(activeDetectorSetup.getDetectorScannable().getBias().toString());
			int[] excludedStripsArray = activeDetectorSetup.getDetectorScannable().getExcludedStrips();
			if (excludedStripsArray == null) {
				throw new Exception("Unable to get excluded strips information from Detector");
			}
			excludedStrips.clear();
			if (excludedStripsArray.length > 0) {
				for (int selected : excludedStripsArray) {
					Integer stringNo = DetectorSetup.getActiveDetectorSetup().createArrayOfStrips()[selected];
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


	private void populateCmbDetectorType(DetectorSetup detector) {
		cmbDetectorType.setInput(new Object[]{detector});
		cmbDetectorType.setSelection(new StructuredSelection(detector));
		cmbDetectorType.getCombo().notifyListeners(SWT.Selection, new Event());
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
