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

package uk.ac.gda.beamline.i05_1.views;

import java.util.Arrays;
import java.util.Set;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.layout.RowLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
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
import gda.observable.IObserver;
import gda.rcp.views.NudgePositionerComposite;
import uk.ac.diamond.daq.concurrent.Async;
import uk.ac.gda.devices.vgscienta.IVGScientaAnalyserRMI;

public class I05_1ContinuousModeControllerComposite extends Composite {

	private static final Logger logger = LoggerFactory.getLogger(I05_1ContinuousModeControllerComposite.class);
	private Combo lensModeCombo;
	private Combo passEnergyCombo;
	private Button startButton;
	private Button stopButton;
	private boolean running = false;
	private Button shutterButton;
	private IVGScientaAnalyserRMI analyser;

	public I05_1ContinuousModeControllerComposite(Composite parent, final IVGScientaAnalyserRMI analyser) {
		super(parent, SWT.NONE);

		this.analyser = analyser;

		// Overall layout of groups
		RowLayoutFactory.swtDefaults().type(SWT.VERTICAL).spacing(5).wrap(false).applyTo(this);

		// Analyser group
		Group analyserGroup = new Group(this, SWT.NONE);
		analyserGroup.setText("Analyser");
		analyserGroup.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		GridLayoutFactory.swtDefaults().numColumns(5).spacing(10, 0).applyTo(analyserGroup);

		// Lens mode
		Label lensModeLabel = new Label(analyserGroup, SWT.NONE);
		lensModeLabel.setText("Lens Mode");
		GridDataFactory.swtDefaults().align(SWT.END, SWT.CENTER).grab(false, true).applyTo(lensModeLabel);

		lensModeCombo = new Combo(analyserGroup, SWT.NONE);
		GridDataFactory.swtDefaults().grab(true, false).applyTo(lensModeCombo);
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
		NudgePositionerComposite centre_energyNPC = new NudgePositionerComposite(analyserGroup, SWT.NONE);
		centre_energyNPC.setScannable((Scannable) Finder.find("raw_centre_energy"));
		centre_energyNPC.setDisplayName("centre_energy");
		centre_energyNPC.hideStopButton();
		GridDataFactory.swtDefaults().span(1, 2).applyTo(centre_energyNPC);
		// Acquire time
		NudgePositionerComposite acquire_timeNPC = new NudgePositionerComposite(analyserGroup, SWT.NONE);
		acquire_timeNPC.setScannable((Scannable) Finder.find("acquire_time"));
		acquire_timeNPC.hideStopButton();
		acquire_timeNPC.setIncrement(0.5);
		GridDataFactory.swtDefaults().span(1, 2).applyTo(acquire_timeNPC);

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
					analyser.startContinuous();
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
		passEnergyCombo.setLayoutData(GridDataFactory.swtDefaults().align(SWT.FILL, SWT.CENTER).create());

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

		// Beamline group
		Group beamlineGroup = new Group(this, SWT.NONE);
		beamlineGroup.setText("Beamline");
		beamlineGroup.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		GridLayoutFactory.swtDefaults().numColumns(5).spacing(10, 0).applyTo(beamlineGroup);

		NudgePositionerComposite energyNPC = new NudgePositionerComposite(beamlineGroup, SWT.NONE);
		energyNPC.setScannable((Scannable) Finder.find("energy"));
		NudgePositionerComposite exitSltNPC = new NudgePositionerComposite(beamlineGroup, SWT.NONE);
		exitSltNPC.setScannable((Scannable) Finder.find("exit_slit"));
		exitSltNPC.setIncrement(0.01); // Don't want to move the exit slit by an unreasonable amount
		NudgePositionerComposite s2_ysizeNPC = new NudgePositionerComposite(beamlineGroup, SWT.NONE);
		s2_ysizeNPC.setScannable((Scannable) Finder.find("s2_ysize"));
		NudgePositionerComposite s2_xsizeNPC = new NudgePositionerComposite(beamlineGroup, SWT.NONE);
		s2_xsizeNPC.setScannable((Scannable) Finder.find("s2_xsize"));

		// Beamline shutter button
		shutterButton = new Button(beamlineGroup, SWT.NONE);
		shutterButton.setText("Close Shutter");
		shutterButton.setForeground(SWTResourceManager.getColor(SWT.COLOR_RED));
		shutterButton.setLayoutData(new GridData(100, SWT.DEFAULT));
		shutterButton.addSelectionListener(new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				InterfaceProvider.getCommandRunner().runCommand("nano_shutter(1)");
			}
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});

		// Add an observer to the psu_mode scannable to automatically detect changes in EPICS and update the GUI
		Scannable psuModeScannable = (Scannable) (Finder.find("psu_mode"));
		final IObserver psuModeObserver = new IObserver() {
			@Override
			public void update(Object source, Object arg) {
				logger.info("Change of psu_mode detected, new mode = " + arg);
				Display.getDefault().asyncExec(new Runnable() {
					@Override
					public void run() {
						updatePassEnergyCombo();
					}
				});
			}
		};

		// Connect observer to scannable.
		psuModeScannable.addIObserver(psuModeObserver);
	}

	public void update(Object arg){
		if (arg instanceof MotorStatus) {
			running = MotorStatus.BUSY.equals(arg);
			Display.getDefault().asyncExec(new Runnable() {
				@Override
				public void run() {
					// When running=true disable start and make selected (pressed)
					startButton.setEnabled(!running);
					startButton.setSelection(running);
					// When running=true enable start and make unselected
					stopButton.setEnabled(running);
					stopButton.setSelection(!running);
					// When running=true disable lens mode and pass energy changes
					lensModeCombo.setEnabled(!running);
					passEnergyCombo.setEnabled(!running);
				}
			});
		}
	}

	// This is used to check if the view is disposed (Might not be the best approach??)
	public Button getStartButton(){
		return startButton;
	}

	private void updatePassEnergyCombo() {
		// Get the current PSU mode
		String psuMode;
		try {
			psuMode = analyser.getPsuMode();

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
}
