/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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
import java.util.Optional;

import org.apache.commons.lang.StringUtils;
import org.apache.commons.math3.analysis.polynomials.PolynomialFunction;
import org.apache.commons.math3.exception.NoDataException;
import org.apache.commons.math3.exception.NullArgumentException;
import org.dawnsci.ede.CalibrationDetails;
import org.dawnsci.ede.EnergyCalibration;
import org.dawnsci.ede.PolynomialParser;
import org.dawnsci.ede.rcp.herebedragons.EnergyCalibrationWizard;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.jface.window.Window;
import org.eclipse.jface.wizard.WizardDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.jython.IJythonServerStatusObserver;
import gda.jython.InterfaceProvider;
import gda.scan.Scan.ScanStatus;
import gda.scan.ScanEvent;
import gda.util.exafs.Element;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.data.AlignmentParametersModel;
import uk.ac.gda.exafs.data.DataPaths;

/**
 * Class that adds GUI elements to a composite to allow user to view details of and run an energy calibration.
 *
 * <li>Various textboxes show the energy calibration polynomial, x-axis ranges used for calibration,
 * name of sample file used for the calibration, and a button to launch the calibration tool.
 * <li>Default reference data to use is determined from selected element and edge in {@link AlignmentParametersModel}.
 * and the default sample data opened is the Nexus file from the last scan run.
 * These are both changeable from the GUI once the Energy calibration tool has been opened.
 * <li>The calibration parameters and GUI are updated once they have been applied in the Energy calibration tool.
 * <li> An optional {@link Runnable} may also be set using {@link #setAfterCalibrationRunnable(Runnable)} - this is called
 * after calibration has been applied and parameters set.
 * <li> the methods {@link #getPolynomialString()}, {@link #getCalibrationMinPosition()}, {@link #getCalibrationMinPosition()},
 * {@link #getSampleFileName()}, {@link #getReferenceFileName()} (and corresponding setters)
 * can be used to access/set calibration parameters.
 *
 * @since 8/2/2019 (refactored from TurboXasExperimentView)
 */
public class EnergyCalibrationComposite {

	private static final Logger logger = LoggerFactory.getLogger(EnergyCalibrationComposite.class);

	public static final String REF_DATA_PATH = DataPaths.getCalibrationReferenceDataPath();
	public static final String REF_DATA_EXT = ".dat";

	private String lastScanFilename = "";
	private String referenceFileName = ""; /** Reference calibration data */
	private String sampleFileName= ""; /** Measured data being calibrated */
	private double calibrationMinPosition;
	private double calibrationMaxPosition;
	private String polynomialString = ""; /** Energy calibration polynomial */

	private final Composite parent;
	private final FormToolkit toolkit;

	private String unitStringForPosition = "cm";
	private Text polynomialTextbox;
	private Text minPositionTextbox;
	private Text maxPositionTextbox;
	private Text sampleFileTextbox;

	private boolean showPositions = true;
	private boolean autoUpdateLastScanName = true;

	private Optional<Runnable> afterCalibrationRunnable = Optional.empty();

	private CalibrationDetails calibrationDetails;

	public EnergyCalibrationComposite(Composite parent) {
		this.parent = parent;
		toolkit = new FormToolkit(parent.getDisplay());
	}

	/**
	 * Create new section in the parent composite and add calibration controls to it.
	 * @param sectionName title to used for the section
	 */
	public void createSection(String sectionName) {
		final Section section;
		section = toolkit.createSection(parent, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE);
		section.setText(sectionName);
		section.setExpanded(true);

		section.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		Composite mainComposite = toolkit.createComposite(section, SWT.NONE);
		mainComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(4, false));
		section.setClient(mainComposite);

		createComposite(mainComposite);
	}

	/**
	 * Add calibration controls to the parent composite.
	 */
	public void createComposite() {
		createComposite(parent);
	}

	/**
	 * Add calibration controls to the parent composite.
	 * @param parent
	 */
	private void createComposite(Composite parent) {
		Composite comp = new Composite(parent, SWT.NONE);

		comp.setLayout(UIHelper.createGridLayoutWithNoMargin(4, false));
		comp.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

		polynomialTextbox = makeLabelAndTextBox(comp, "Energy calibration polynomial");
		// Non user editable - set from EnergyCalibrationWizard
		polynomialTextbox.setEditable(false);
		setRowSpan(polynomialTextbox, 3);

		if (showPositions) {
			minPositionTextbox = makeLabelAndTextBox(comp, "Min Position "+unitStringForPosition);
			maxPositionTextbox = makeLabelAndTextBox(comp, "Max Position "+unitStringForPosition);
			minPositionTextbox.setEditable(false);
			maxPositionTextbox.setEditable(false);
		}

		sampleFileTextbox = makeLabelAndTextBox(comp, "Energy calibration file", SWT.BORDER | SWT.RIGHT);
		setRowSpan(sampleFileTextbox, 2);
		// If using long path, then textbox is made very wide and it *doesn't shrink* to fit smaller window.
		// Set widthhint on gridlayout to something small to make it the box small initially, and have normal resize behaviour.
		setWidthHint(sampleFileTextbox, 100);

		Composite buttonComposite = toolkit.createComposite(comp, SWT.NONE);
		buttonComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		buttonComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));

		Button runCalibrationButton = toolkit.createButton(buttonComposite, "Run energy calibration", SWT.PUSH);
		runCalibrationButton.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		runCalibrationButton.addListener(SWT.Selection, e -> {
			int code = openEnergyCalibrationDialog(comp);
			if (code == Window.OK && afterCalibrationRunnable.isPresent()) {
				afterCalibrationRunnable.get().run();
			}
		});

		addDisposeListeners();
		setAutoUpdateLastScanName(autoUpdateLastScanName);
	}

	/**
	 * Set a runnable that will be called after calibration has been completed and user closes
	 * the dialog box by clicking the 'Ok' button.
	 * @param afterCalibrationRunnable
	 */
	public void setAfterCalibrationRunnable(Runnable afterCalibrationRunnable) {
		this.afterCalibrationRunnable = Optional.ofNullable(afterCalibrationRunnable);
	}

	private int openEnergyCalibrationDialog(final Composite parent) {

		// Get name of reference file from Alignment parameters.
		// Opening the 'Optics' view in Alignment perspective case would normally load settings from preference store
		// Load preferences here, to get element and edge values for reference file in case that view hasn't been opened...
		AlignmentParametersModel.INSTANCE.loadAlignmentParametersFromStore();
		String referenceDataFileName = getCurrentReferenceDataPath();
		String energyCalPolynomialString = polynomialTextbox.getText();

		EnergyCalibration calibrationModel = new EnergyCalibration();
		try {
			String message = "";
			message += tryToSetCalibrationData(calibrationModel, referenceDataFileName, true);
			message += tryToSetCalibrationData(calibrationModel, lastScanFilename, false);

			// Show warning message, but still display calibration tool if data cannot be set automatically
			if (message.length() > 0) {
				UIHelper.showWarning("Unable to set input for energy calibration tool automatically", message);
			}

			// Try to set the initial energy calibration polynomial
			if (!StringUtils.isEmpty(energyCalPolynomialString)) {
				try {
					PolynomialFunction poly = new PolynomialFunction(PolynomialParser.extractCoefficientsFromString(energyCalPolynomialString));
					calibrationModel.getCalibrationDetails().setCalibrationResult(poly);
				} catch(NullArgumentException | NoDataException ex) {
					logger.warn("Problem setting polynomial function from string {}", energyCalPolynomialString);
				}
			}

			WizardDialog wizardDialog = new WizardDialog(parent.getShell(),
					new EnergyCalibrationWizard(calibrationModel)) {
				@Override
				protected void createButtonsForButtonBar(Composite parent) {
					super.createButtonsForButtonBar(parent);
					this.getButton(IDialogConstants.FINISH_ID).setText("Apply Calibration");
					((GridData) this.getButton(IDialogConstants.FINISH_ID).getLayoutData()).widthHint = 200;
					this.getButton(IDialogConstants.FINISH_ID).getParent().layout();
				}
			};

			wizardDialog.setPageSize(1024, 768);
			int returnCode = wizardDialog.open();
			if (returnCode == Window.OK) {
				// Store the fit parameters
				PolynomialFunction polynomialFunction = calibrationModel.getCalibrationDetails().getCalibrationResult();
				if (polynomialFunction != null) {
					sampleFileName = calibrationModel.getSampleData().getFileName();
					referenceFileName = calibrationModel.getRefData().getFileName();
					polynomialString = polynomialFunction.toString();
					logger.debug("Storing calibration parameters : sample filename = {}, reference filename = {}, polynomial = {}",
							sampleFileName, referenceFileName, polynomialString);
					Dataset positions = calibrationModel.getSampleData().getEnergyNode();
					if (positions != null) {
						calibrationMinPosition = positions.min().doubleValue();
						calibrationMaxPosition = positions.max().doubleValue();
						logger.debug("Storing positions : min = {}, max = {}", calibrationMinPosition, calibrationMaxPosition);
					}
					// set the full path to sample file
					calibrationModel.getCalibrationDetails().setSampleDataFileName(sampleFileName);
					calibrationDetails = calibrationModel.getCalibrationDetails();
				}
				// Update the gui widgets
				updateGuiFromParameters();
				return Window.OK;
			}
		} catch (Exception e) {
			logger.error("Unable to perform energy calibration", e);
		}
		return Window.CANCEL;
	}

	private static String getReferenceDataPath(Element element, String edgeName) {
		return REF_DATA_PATH + File.separator + element.getSymbol() + "_" + edgeName + REF_DATA_EXT;
	}

	public static String getCurrentReferenceDataPath() {
		return getReferenceDataPath(AlignmentParametersModel.INSTANCE.getElement(), AlignmentParametersModel.INSTANCE.getEdge().getEdgeType());
	}

	/**
	 * Update the widgets in the GUI to show the currently stored values of polynomial string,
	 * calibration filename, min and max energy,
	 */
	public void updateGuiFromParameters() {
		logger.debug("Updating GUI to show stored calibration parameters. Polynomial = {}", polynomialString);
		sampleFileTextbox.setText(sampleFileName);

		if (!StringUtils.isEmpty(lastScanFilename)) {
			sampleFileTextbox.setToolTipText("Last scan : " + lastScanFilename);
		} else {
			// add tooltip so can see full name by by hovering with mouse
			sampleFileTextbox.setToolTipText(sampleFileName);
			// move cursor to end of text field, so filename can be seen in box (not just the leading directories in the fullpath...)
			sampleFileTextbox.setSelection(sampleFileTextbox.getText().length());
		}

		polynomialTextbox.setText(polynomialString);
		if (showPositions) {
			minPositionTextbox.setText(String.valueOf(calibrationMinPosition));
			maxPositionTextbox.setText(String.valueOf(calibrationMaxPosition));
		}
	}

	/**
	 * Try to load reference/sample data into EnergyCalibration model.
	 * @param model
	 * @param filename
	 * @param isReferenceData set to true to load file as reference data, otherwise file is loaded as sample data
	 * @return Error message if file was not found or could not be loaded; empty string if all was well.
	 * @throws Exception
	 */
	private String tryToSetCalibrationData(EnergyCalibration model, String filename, boolean isReferenceData) {
		String message = "";
		String dataType = isReferenceData ? "Reference data" : "Sample data";
		if (StringUtils.isEmpty(filename) || !new File(filename).isFile() ) {
			message += dataType + " " +filename + " was not found.\n";
		} else {
			try {
				if (isReferenceData) {
					model.setRefData(filename);
				} else {
					model.setSampleData(filename);
				}
			} catch(Exception e) {
				message += e.getMessage();
			}
		}
		return message;
	}

	/**
	 * Observer to update the 'last scan' filename and tooltip on sample file textbox after each scan.
	 */
	final IJythonServerStatusObserver serverObserver = (theObserved, changeCode) -> Display.getDefault().asyncExec(() -> {
		if (changeCode instanceof ScanEvent) {
			ScanEvent scanEvent = (ScanEvent) changeCode;
			ScanStatus status = scanEvent.getLatestStatus();
			logger.debug("ScanEvent = {}, ScanStatus = {}",changeCode.toString(), status.toString());
			if (scanEvent.getLatestStatus().isRunning()) {
				String nexusFilename = scanEvent.getLatestInformation().getFilename();
				if (!StringUtils.isEmpty(nexusFilename)) {
					setLastScanFileName(nexusFilename);
				}
			}
		}
	});

	/**
	 * Set flag for whether to auto update the name of the last scan and sample file tooltip after each scan.
	 * @param autoUpdateLastScanName
	 */
	public void setAutoUpdateLastScanName(boolean autoUpdateLastScanName) {
		this.autoUpdateLastScanName = autoUpdateLastScanName;
		if (autoUpdateLastScanName) {
			InterfaceProvider.getScanDataPointProvider().addScanEventObserver(serverObserver);
		} else {
			InterfaceProvider.getScanDataPointProvider().deleteScanEventObserver(serverObserver);
		}
	}

	public boolean isAutoUpdateLastScanName() {
		return autoUpdateLastScanName;
	}

	private void addDisposeListeners() {
		parent.addDisposeListener( disposeEvent -> {
			InterfaceProvider.getScanDataPointProvider().deleteScanEventObserver(serverObserver);
			toolkit.dispose();
		});
	}

	private Label makeLabel(Composite parent, String labelText) {
		Label label = toolkit.createLabel(parent, labelText, SWT.None);
		label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		return label;
	}

	private Text makeLabelAndTextBox(Composite parent, String labelText) {
		return makeLabelAndTextBox(parent, labelText, SWT.BORDER);
	}

	private Text makeLabelAndTextBox(Composite parent, String labelText, int style) {
		makeLabel(parent, labelText);
		Text textBox = toolkit.createText(parent, "", style);
		textBox.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		return textBox;
	}

	private void setWidthHint(Control controlWidget, int widthHint) {
		Object layoutData = controlWidget.getLayoutData();
		if (layoutData instanceof GridData) {
			GridData grid = (GridData) layoutData;
			grid.widthHint = widthHint;
		}
	}

	/**
	 * Set horizontal span of the GridLayout for supplied Control widget
	 * @param controlWidget
	 * @param span
	 */
	private void setRowSpan(Control controlWidget, int span) {
		Object layoutData = controlWidget.getLayoutData();
		if (layoutData instanceof GridData) {
			GridData grid = (GridData) layoutData;
			grid.horizontalSpan = span;
		}
	}

	public String getReferenceFileName() {
		return referenceFileName;
	}

	public void setReferenceFileName(String referenceFileName) {
		this.referenceFileName = referenceFileName;
	}

	public String getSampleFileName() {
		return sampleFileName;
	}

	public void setSampleFileName(String sampleFileName) {
		this.sampleFileName = sampleFileName;
	}

	public double getCalibrationMinPosition() {
		return calibrationMinPosition;
	}

	public void setCalibrationMinPosition(double calibrationMinPosition) {
		this.calibrationMinPosition = calibrationMinPosition;
	}

	public double getCalibrationMaxPosition() {
		return calibrationMaxPosition;
	}

	public void setCalibrationMaxPosition(double calibrationMaxPosition) {
		this.calibrationMaxPosition = calibrationMaxPosition;
	}

	public String getPolynomialString() {
		return polynomialString;
	}

	public void setPolynomialString(String polynomialString) {
		this.polynomialString = polynomialString;
	}

	public Text getSampleFileTextbox() {
		return sampleFileTextbox;
	}

	public Text getPolynomialTextbox() {
		return polynomialTextbox;
	}

	public void setLastScanFileName(String lastScanFilename) {
		this.lastScanFilename = lastScanFilename;
		if (sampleFileTextbox !=null && !sampleFileTextbox.isDisposed()) {
			sampleFileTextbox.setToolTipText("Last scan : " + lastScanFilename);
		}
	}

	public boolean isShowPositions() {
		return showPositions;
	}

	public void setShowPositions(boolean showPositions) {
		this.showPositions = showPositions;
	}

	public CalibrationDetails getCalibrationDetails() {
		return calibrationDetails;
	}

}