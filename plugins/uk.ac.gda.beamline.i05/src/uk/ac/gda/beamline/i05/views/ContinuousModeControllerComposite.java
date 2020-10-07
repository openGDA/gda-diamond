/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i05.views;

import java.util.Arrays;
import java.util.Set;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.layout.RowLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.swtdesigner.SWTResourceManager;

import gda.device.MotorStatus;
import gda.device.Scannable;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.JythonServerFacade;
import gda.rcp.views.NudgePositionerComposite;
import uk.ac.diamond.daq.concurrent.Async;
import uk.ac.gda.devices.vgscienta.IVGScientaAnalyserRMI;

public class ContinuousModeControllerComposite extends Composite {

	private static final Logger logger = LoggerFactory.getLogger(ContinuousModeControllerComposite.class);
	private Combo lensModeCombo;
	private Combo passEnergyCombo;
	private Button startButton;
	private Button stopButton;
	private boolean running = false;
	private Button closeShutterButton;
	private Button openShutterButton;
	private IVGScientaAnalyserRMI analyser;
	static final int NPC_INCREMENT_TEXT_WIDTH = 30;

	public ContinuousModeControllerComposite(Composite parent, final IVGScientaAnalyserRMI analyser) {
		super(parent, SWT.NONE);

		this.analyser = analyser;

		// Overall layout of groups
		//RowLayoutFactory.swtDefaults().type(SWT.VERTICAL).spacing(5).wrap(false).applyTo(this);
		GridLayoutFactory.fillDefaults().numColumns(5).equalWidth(false).applyTo(this);
		parent.setBackground(Display.getDefault().getSystemColor(SWT.COLOR_WHITE));

		// Analyser group
		Group analyserGroup = new Group(this, SWT.NONE);
		analyserGroup.setText("Analyser");
		analyserGroup.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		GridLayoutFactory.swtDefaults().numColumns(5).spacing(10, 0).applyTo(analyserGroup);
		GridDataFactory.fillDefaults().span(5, 1).applyTo(analyserGroup);

		// Lens mode
		Label lensModeLabel = new Label(analyserGroup, SWT.NONE);
		lensModeLabel.setText("Lens Mode");
		GridDataFactory.swtDefaults().align(SWT.END, SWT.CENTER).grab(false, true).applyTo(lensModeLabel);

		lensModeCombo = new Combo(analyserGroup, SWT.NONE);
		GridDataFactory.swtDefaults().align(SWT.FILL, SWT.CENTER).applyTo(lensModeCombo);
		// Setup lens modes and select currently selected one
		lensModeCombo.setItems(analyser.getEnergyRange().getAllLensModes().toArray(new String[0]));
		try {
			String activeLensMode = analyser.getLensMode();
			lensModeCombo.select(Arrays.asList(lensModeCombo.getItems()).indexOf(activeLensMode));
		} catch (Exception e) {
			logger.error("Failed to get current lens mode", e);
		}
		lensModeCombo.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				logger.info("Changing analyser lens mode to " + lensModeCombo.getText());
				try {
					analyser.setLensMode(lensModeCombo.getText());
				} catch (Exception ex) {
					logger.error("Failed to change lens mode", ex);
				}
				updatePassEnergyCombo();
			}
		});

		// Centre energy
		NudgePositionerComposite centreEnergyNPC = new NudgePositionerComposite(analyserGroup, SWT.NONE);
		centreEnergyNPC.setScannable((Scannable) Finder.getInstance().find("raw_centre_energy"));
		centreEnergyNPC.setDisplayName("centre_energy");
		centreEnergyNPC.setIncrementTextWidth(NPC_INCREMENT_TEXT_WIDTH);
		centreEnergyNPC.hideStopButton();
		GridDataFactory.swtDefaults().span(1, 2).applyTo(centreEnergyNPC);
		// Acquire time
		NudgePositionerComposite acquireTimeNPC = new NudgePositionerComposite(analyserGroup, SWT.NONE);
		acquireTimeNPC.setScannable((Scannable) Finder.getInstance().find("acquire_time"));
		acquireTimeNPC.hideStopButton();
		acquireTimeNPC.setIncrement(0.5);
		acquireTimeNPC.setIncrementTextWidth(NPC_INCREMENT_TEXT_WIDTH);
		GridDataFactory.swtDefaults().span(1, 2).applyTo(acquireTimeNPC);

		// Analyser Start Button
		startButton = new Button(analyserGroup, SWT.DEFAULT);
		startButton.setLayoutData(new GridData(100, SWT.DEFAULT));
		startButton.setText("Start");
		startButton.setToolTipText("Apply voltages and start acquiring");
		startButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				logger.debug("Starting continuous acquistion");
				try {
					// Need to reset lens mode and pass energy as they may have changed from the values
					// Shown in this GUI so resend the settings
					analyser.setLensMode(lensModeCombo.getText());
					analyser.setPassEnergy(Integer.parseInt(passEnergyCombo.getText()));
					analyser.startContinuious();
				} catch (Exception ex) {
					logger.error("Failed to start continuious acquisition", ex);
				}
			}
		});

		// Analyser pass energy
		Label passEnergyLabel = new Label(analyserGroup, SWT.NONE);
		passEnergyLabel.setText("Pass Energy");
		GridDataFactory.swtDefaults().align(SWT.END, SWT.CENTER).grab(false, true).applyTo(passEnergyLabel);

		passEnergyCombo = new Combo(analyserGroup, SWT.NONE);
		// Call update to setup passEnergyCombo
		updatePassEnergyCombo();

		// Add listener to update analyser pass energy when changed
		passEnergyCombo.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				logger.info("Changing analyser pass energy to " + passEnergyCombo.getText());
				try {
					analyser.setPassEnergy(Integer.parseInt(passEnergyCombo.getText()));
				} catch (Exception ex) {
					logger.error("Failed to set pass energy", ex);
				}
			}
		});
		// I05-207 Add a width hint here stops a mysterious resizing
		passEnergyCombo.setLayoutData(GridDataFactory.swtDefaults().align(SWT.FILL, SWT.CENTER).hint(200, SWT.DEFAULT).create());

		// Analyser Stop Button
		stopButton = new Button(analyserGroup, SWT.DEFAULT);
		stopButton.setLayoutData(new GridData(100, SWT.DEFAULT));
		stopButton.setText("Stop");
		stopButton.setToolTipText("Stop acquiring and zero supplies");
		stopButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				logger.info("Stopping continuous acquistion");
				Async.execute(() -> {
					try {
						analyser.zeroSupplies();
					} catch (Exception ex) {
						logger.error("Failed to stop analyser", ex);
					}
				});
			}
		});

		// Sample Translations
		Group translationNpcGroup = new Group(this, SWT.NONE);
		translationNpcGroup.setText("Sample Translations");
		translationNpcGroup.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		RowLayoutFactory.swtDefaults().type(SWT.HORIZONTAL).spacing(10).wrap(true).applyTo(translationNpcGroup);
		GridDataFactory.fillDefaults().span(3, 1).applyTo(translationNpcGroup);

		NudgePositionerComposite saxNPC = new NudgePositionerComposite(translationNpcGroup, SWT.NONE);
		saxNPC.setScannable((Scannable) Finder.find("sax"));
		saxNPC.setIncrementTextWidth(NPC_INCREMENT_TEXT_WIDTH);
		NudgePositionerComposite sayNPC = new NudgePositionerComposite(translationNpcGroup, SWT.NONE);
		sayNPC.setScannable((Scannable) Finder.find("say"));
		sayNPC.setIncrementTextWidth(NPC_INCREMENT_TEXT_WIDTH);
		NudgePositionerComposite sazNPC = new NudgePositionerComposite(translationNpcGroup, SWT.NONE);
		sazNPC.setScannable((Scannable) Finder.find("saz"));
		sazNPC.setIncrementTextWidth(NPC_INCREMENT_TEXT_WIDTH);

		// Beamline group
		Group beamlineGroup = new Group(this, SWT.NONE);
		beamlineGroup.setText("Beamline");
		beamlineGroup.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		GridLayoutFactory.swtDefaults().numColumns(2).spacing(10, 0).applyTo(beamlineGroup);
		GridDataFactory.fillDefaults().span(2, 2).applyTo(beamlineGroup);

		NudgePositionerComposite energyNPC = new NudgePositionerComposite(beamlineGroup, SWT.NONE);
		energyNPC.setScannable((Scannable) Finder.find("energy"));
		energyNPC.setIncrementTextWidth(NPC_INCREMENT_TEXT_WIDTH);
		NudgePositionerComposite exitSltNPC = new NudgePositionerComposite(beamlineGroup, SWT.NONE);
		exitSltNPC.setScannable((Scannable) Finder.find("exit_slit"));
		exitSltNPC.setIncrement(0.01); // Don't want to move the exit slit by an unreasonable amount
		exitSltNPC.setIncrementTextWidth(NPC_INCREMENT_TEXT_WIDTH);
		NudgePositionerComposite s2YsizeNPC = new NudgePositionerComposite(beamlineGroup, SWT.NONE);
		s2YsizeNPC.setScannable((Scannable) Finder.find("s2_ysize"));
		s2YsizeNPC.setIncrementTextWidth(NPC_INCREMENT_TEXT_WIDTH);
		NudgePositionerComposite s2XsizeNPC = new NudgePositionerComposite(beamlineGroup, SWT.NONE);
		s2XsizeNPC.setScannable((Scannable) Finder.find("s2_xsize"));
		s2XsizeNPC.setIncrementTextWidth(NPC_INCREMENT_TEXT_WIDTH);

//		Composite buttonsComposite = new Composite(beamlineGroup, SWT.NONE);
//		GridLayoutFactory.swtDefaults().numColumns(2).spacing(10, 0).applyTo(buttonsComposite);
//		GridDataFactory.fillDefaults().span(5, 1).applyTo(buttonsComposite);

		// Beamline shutter button
		closeShutterButton = new Button(beamlineGroup, SWT.NONE);
		GridDataFactory.fillDefaults().grab(true,  false).applyTo(closeShutterButton);
		closeShutterButton.setText("Close Shutter");
		closeShutterButton.setForeground(SWTResourceManager.getColor(SWT.COLOR_RED));
		closeShutterButton.setLayoutData(new GridData(100, SWT.DEFAULT));
		closeShutterButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				logger.info("Closing beamline shutter");
				InterfaceProvider.getCommandRunner().runCommand("hr_shutter('Close')");
			}
		});

		// Beamline shutter button
		openShutterButton = new Button(beamlineGroup, SWT.NONE);
		GridDataFactory.fillDefaults().grab(true, false).applyTo(openShutterButton);
		openShutterButton.setText("Open Shutter");
		openShutterButton.setForeground(SWTResourceManager.getColor(SWT.COLOR_DARK_BLUE));
		openShutterButton.setLayoutData(new GridData(100, SWT.DEFAULT));
		openShutterButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				logger.info("Closing beamline shutter");
				InterfaceProvider.getCommandRunner().runCommand("hr_shutter('Open')");
			}
		});

		// Sample Rotations
		Group rotationNpcGroup = new Group(this, SWT.NONE);
		rotationNpcGroup.setText("Sample Rotations");
		rotationNpcGroup.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		RowLayoutFactory.swtDefaults().type(SWT.HORIZONTAL).spacing(10).applyTo(rotationNpcGroup);
		GridDataFactory.fillDefaults().span(3, 1).applyTo(rotationNpcGroup);

		NudgePositionerComposite satiltNPC = new NudgePositionerComposite(rotationNpcGroup, SWT.NONE);
		satiltNPC.setScannable((Scannable) Finder.find("satilt"));
		satiltNPC.setIncrementTextWidth(NPC_INCREMENT_TEXT_WIDTH);
		NudgePositionerComposite sapolarNPC = new NudgePositionerComposite(rotationNpcGroup, SWT.NONE);
		sapolarNPC.setScannable((Scannable) Finder.find("sapolar"));
		sapolarNPC.setIncrementTextWidth(NPC_INCREMENT_TEXT_WIDTH);
		NudgePositionerComposite saazimuthNPC = new NudgePositionerComposite(rotationNpcGroup, SWT.NONE);
		saazimuthNPC.setScannable((Scannable) Finder.find("saazimuth"));
		saazimuthNPC.setIncrementTextWidth(NPC_INCREMENT_TEXT_WIDTH);

		// Add an observer to the psu_mode scannable to automatically detect changes in EPICS and update the GUI
		final Scannable psuModeScannable = Finder.find("psu_mode");
		// Connect observer to scannable.
		psuModeScannable.addIObserver((source, arg) -> {
			logger.info("Change of psu_mode detected, new mode = {}", arg);
			Display.getDefault().asyncExec(this::updatePassEnergyCombo);
		});

		// Observe the analyser, to get start and stop events
		analyser.addIObserver((source, arg) -> {
			if (arg instanceof MotorStatus) {
				running = MotorStatus.BUSY.equals(arg);
				Display.getDefault().asyncExec(() -> {
					// When running=true disable start and make selected (pressed)
					startButton.setEnabled(!running);
					startButton.setSelection(running);
					// When running=true enable start and make unselected
					stopButton.setEnabled(running);
					stopButton.setSelection(!running);
					// When running=true disable lens mode and pass energy changes
					lensModeCombo.setEnabled(!running);
					passEnergyCombo.setEnabled(!running);
				});
			}
		});

		ScrolledComposite scroller = new ScrolledComposite(parent, SWT.V_SCROLL);
		scroller.setContent(this);
		scroller.setExpandHorizontal(true);
		scroller.setExpandVertical(true);
		scroller.setMinSize(this.computeSize(SWT.DEFAULT, SWT.DEFAULT));
	}

	private void updatePassEnergyCombo() {
		try {
			// Get the current PSU mode
			final String psuMode = analyser.getPsuMode();

			// Get the available pass energies depending on the PSU mode and lens mode
			Set<Integer> passEnergies = analyser.getEnergyRange().getPassEnergies(psuMode, lensModeCombo.getText());

			// Convert the short array into a string ArrayList for combo box
			String[] passEnergyStrings = new String[passEnergies.size()];
			int i = 0;
			for (Integer pe : passEnergies) {
				passEnergyStrings[i++] = pe.toString();
			}

			// Set the new pass energies
			logger.debug("Setting items in pass energy combo box");
			passEnergyCombo.setItems(passEnergyStrings);

			// Automatically select the current pass energy if available in current PSU mode
			logger.debug("Selecting currently active pass energy in combo box");
			String activePassEnergy = JythonServerFacade.getInstance().evaluateCommand("analyser.getPassEnergy()");
			passEnergyCombo.select(Arrays.asList(passEnergyStrings).indexOf(activePassEnergy));
		} catch (Exception e) {
			logger.error("Failed to get PSU mode", e);
		}
	}

	@Override
	public boolean setFocus() {
		return stopButton.setFocus();
	}

}
