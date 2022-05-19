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

import java.beans.PropertyChangeListener;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Optional;

import org.apache.commons.io.FileUtils;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.AlignmentStage;
import gda.rcp.views.NudgePositionerComposite;
import gda.scan.ede.position.AlignmentStageModel;
import gda.scan.ede.position.Location;
import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.livecontrol.ScannablePositionerControl;
import uk.ac.gda.ede.data.ClientConfig;
import uk.ac.gda.exafs.data.ScannableSetup;
import uk.ac.gda.exafs.experiment.ui.SaveLoadButtonsComposite;
import uk.ac.gda.exafs.ui.data.ScannableMotorMoveObserver;
import uk.ac.gda.ui.components.NumberEditorControl;

public class AlignmentStageCalibrationView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.alignmentstagecalibration";

	private static final Logger logger = LoggerFactory.getLogger(AlignmentStageCalibrationView.class);

	private FormToolkit toolkit;
	private Form form;

	private AlignmentStage alignmentStage;
	private Collection<Location> positions = Collections.emptyList();

	private final WritableList<Scannable> movingScannables = new WritableList<>(new ArrayList<>(), Scannable.class);
	private final ScannableMotorMoveObserver moveObserver = new ScannableMotorMoveObserver(movingScannables);

	public AlignmentStageCalibrationView() {}

	private Composite parent;

	@Override
	public void createPartControl(Composite parent) {
		this.parent = parent;
		try {
			loadSettings();
			createControls(parent);
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
			logger.error("Unable to create controls", e);
		}
	}

	private void createControls(Composite parent) throws Exception {
		toolkit = new FormToolkit(parent.getDisplay());
		ScrolledForm scrolledform = toolkit.createScrolledForm(parent);
		form = scrolledform.getForm();
		form.getBody().setLayout(new GridLayout(1, true));
		form.getBody().setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, false));

		createControlsSection(form.getBody());
		addLoadSaveButtons(form.getBody());
	}

	private void loadSettings() throws Exception {
		alignmentStage = getAlignmentStage().orElseThrow(() -> new Exception("Problem"));
		loadAlignmentStageSettings();
	}

	// Make Listener object to move alignment stage to specified position
	private Listener makeMoveListener( final String name, final Location location )
	{
		return event -> {
			try {
				logger.debug("Moving alignment stage to '{}' position - {}", name, location);
				alignmentStage.moveToLocation(location);
			}
			catch (DeviceException e1) {
				logger.error("Problem moving alignment stage to {}", location, e1);
			} catch (Exception e2) {
				logger.error("Problem getting scannable for alignment stage ", e2);
			}
		};
	}

	// Save alignment settings to persistence store.
	private void saveAlignmentStageSettings() {
		try {
			// Update AlignmentStageScannale with updated location list from GUI
			alignmentStage.clearLocations();
			for(Location loc : positions) {
				alignmentStage.setLocation(loc);
			}
			alignmentStage.saveConfiguration();

//			saveToFile();
		}catch(Exception e) {
			logger.warn("Problem saving alignment settings", e);
		}
	}

	// Load alignment settings from persistence store.
	private void loadAlignmentStageSettings() throws IOException {
		alignmentStage.loadConfiguration();
	}

	private Optional<AlignmentStage> getAlignmentStage() throws Exception {
		Scannable scannable = ScannableSetup.ALIGNMENT_STAGE.getScannable();
		if (scannable instanceof AlignmentStage) {
			return Optional.of( (AlignmentStage) scannable);
		}
		return Optional.empty();
	}

	private void createControlsSection(Composite parent) throws Exception {
		final Section section = toolkit.createSection(parent, Section.TITLE_BAR);
		toolkit.paintBordersFor(section);
		section.setText("Alignment stage");
		toolkit.paintBordersFor(section);
		section.setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, false));

		Composite sectionComposite = toolkit.createComposite(section, SWT.NONE);
		toolkit.paintBordersFor(sectionComposite);
		sectionComposite.setLayout(new GridLayout());
		section.setClient(sectionComposite);

		Composite composite = createAlignmentStageXY(sectionComposite, ScannableSetup.ALIGNMENT_STAGE_X_POSITION, ScannableSetup.ALIGNMENT_STAGE_Y_POSITION);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		ScannableMotorMoveObserver.setupStopToolbarButton(section, movingScannables);
		ScannableSetup.ALIGNMENT_STAGE_X_POSITION.getScannable().addIObserver(moveObserver);
		ScannableSetup.ALIGNMENT_STAGE_Y_POSITION.getScannable().addIObserver(moveObserver);

		Composite alignmentStageComposite = toolkit.createComposite(sectionComposite, SWT.None);
		alignmentStageComposite.setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, false));
		alignmentStageComposite.setLayout(new GridLayout(3, false));

		positions = alignmentStage.getLocations();

		for (Location location : positions) {
			createXYControlsAndMoveButton(alignmentStageComposite, location);
		}

		Composite sectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(sectionSeparator);
		section.setSeparatorControl(sectionSeparator);
	}
	private class SaveLoadButtons extends SaveLoadButtonsComposite {

		public SaveLoadButtons(Composite parent, FormToolkit toolkit) {
			super(parent, toolkit, AlignmentStageModel.class);
		}

		@Override
		protected void saveParametersToFile(String filename) throws Exception {
			Path filePath = Paths.get(filename);
			logger.info("Writing XML parameters to {}", filePath);
			AlignmentStageModel pos = new AlignmentStageModel(positions);
			FileUtils.writeStringToFile(filePath.toFile(), pos.toXml(), Charset.defaultCharset());
		}

		@Override
		protected void loadParametersFromFile(String filename) throws Exception {
			if (!beanIsCorrectType(filename)) {
				return;
			}
			Path filePath = Paths.get(filename);
			logger.info("Reading XML parameters from {}", filePath);
			AlignmentStageModel model = AlignmentStageModel.fromXml(getBeanFromFile(filename));
			positions = model.getDeviceLocations();
			saveAlignmentStageSettings();
			reOpenView(true);
			// update the GUI with new controls

		}

	}


	/**
	 * Open a live stream view with the secondary ID specified
	 *
	 * @param closeExistingView close the existing view first
	 */
	protected void reOpenView(boolean closeExistingView) {
		final IWorkbenchPage page = getSite().getPage();
		if (closeExistingView) {
			page.hideView(this);
		}
		try {
			page.showView(AlignmentStageCalibrationView.ID, null, IWorkbenchPage.VIEW_ACTIVATE);
		} catch (PartInitException e) {
			logger.error("Error activating AlignmentStageCalibrationView view",  e);
		}
	}

	private void addLoadSaveButtons(Composite parent) {
		final Section startStopScanSection = toolkit.createSection(parent, ExpandableComposite.TITLE_BAR);
		startStopScanSection.setText("Save and load settings");
		startStopScanSection.setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, false));
//
		Composite startStopSectionComposite = toolkit.createComposite(startStopScanSection, SWT.NONE);
		startStopSectionComposite.setLayout(new GridLayout(1, true));
		startStopScanSection.setClient(startStopSectionComposite);

		new SaveLoadButtons(startStopSectionComposite, toolkit);
	}

	// Listener used to update persistence store when model changes.
	private final PropertyChangeListener textBoxListener = event -> saveAlignmentStageSettings();

	private Composite createAlignmentStageXY(Composite parent, ScannableSetup xScannable, ScannableSetup yScannable) throws Exception {
		Composite xyPositionComposite = toolkit.createComposite(parent, SWT.NONE);
		toolkit.paintBordersFor(xyPositionComposite);
		GridLayout layout = new GridLayout();
		layout.marginHeight = 0;
		layout.marginHeight = 0;
		xyPositionComposite.setLayout(layout);

		createMotorControl(xyPositionComposite, "Alignment stage x", xScannable);
		createMotorControl(xyPositionComposite, "Alignment stage y", yScannable);

		return xyPositionComposite;
	}

	/**
	 * Add a {@link NudgePositionerComposite} to parent composite to control the scannable in ScannableSetupObject
	 * @param parent
	 * @param label
	 * @param scnSetup
	 */
	private void createMotorControl(Composite parent, String label, ScannableSetup scnSetup) {
		ScannablePositionerControl control = new ScannablePositionerControl();
		control.setDisplayName(label);
		control.setHorizontalLayout(true);
		control.setScannableName(scnSetup.getScannableName());
		control.setUserUnits(scnSetup.getUnit().getText());
		control.setDisplayNameWidth(150);
		control.setIncrementTextWidth(30);
		control.createControl(parent);
	}

	// Like createXY function except also creates 'Move' button and adds listener to it.
	private void createXYControlsAndMoveButton(Composite parent, Location location) throws Exception {
		GridDataFactory factory = GridDataFactory.fillDefaults();

		String xPropertyName = Location.X_POS_PROP_NAME;
		String yPropertyName = Location.Y_POS_PROP_NAME;

		Label label = toolkit.createLabel(parent, location.getDisplayLabel(), SWT.None);
		factory.align(SWT.BEGINNING, SWT.CENTER).applyTo(label);
		label.setToolTipText(location.getName());

		Composite composite = createXY( parent, location, xPropertyName, yPropertyName );
		factory.applyTo(composite);
		location.addPropertyChangeListener( textBoxListener ); // add listener to update persistence store
		composite.addDisposeListener(l -> {
			logger.debug("Removing textbox property listener for {}", location.getName());
			location.removePropertyChangeListener(textBoxListener);
		});
		Button moveToButton = toolkit.createButton(parent, "Move", SWT.None);
		factory.applyTo(moveToButton);
		moveToButton.addListener(SWT.Selection, makeMoveListener(location.getName(), location));
	}

	private Composite createXY(Composite parent, ObservableModel model, String xPropertyName, String yPropertyName) throws Exception {
		GridDataFactory factory = GridDataFactory.fillDefaults().hint(150, SWT.DEFAULT);

		Composite xyPositionComposite = toolkit.createComposite(parent, SWT.NONE);
		toolkit.paintBordersFor(xyPositionComposite);
		xyPositionComposite.setLayout(new GridLayout(4, false));

		toolkit.createLabel(xyPositionComposite, "x", SWT.None);

		NumberEditorControl xPosition = new NumberEditorControl(xyPositionComposite, SWT.None, model, xPropertyName, false);
//		xPosition.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		xPosition.setUnit(ClientConfig.UnitSetup.MILLI_METER.getText());
		factory.applyTo(xPosition);

		toolkit.createLabel(xyPositionComposite, "y", SWT.None);

		NumberEditorControl yPosition = new NumberEditorControl(xyPositionComposite, SWT.None, model, yPropertyName, false);
//		yPosition.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		yPosition.setUnit(ClientConfig.UnitSetup.MILLI_METER.getText());
		factory.applyTo(yPosition);

		return xyPositionComposite;
	}

	@Override
	public void setFocus() {
		form.setFocus();
	}

	@Override
	public void dispose() {
		logger.debug("Dispose called");
		try {
			ScannableSetup.ALIGNMENT_STAGE_X_POSITION.getScannable().deleteIObserver(moveObserver);
			ScannableSetup.ALIGNMENT_STAGE_Y_POSITION.getScannable().deleteIObserver(moveObserver);
		} catch (Exception e) {
			logger.error("Problem removing 'move observers'", e);
		}
	}
}
