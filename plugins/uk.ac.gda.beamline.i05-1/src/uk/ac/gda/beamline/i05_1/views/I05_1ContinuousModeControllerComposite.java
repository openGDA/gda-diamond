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

import gda.device.MotorStatus;
import gda.device.Scannable;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.JythonServerFacade;
import gda.observable.IObserver;
import gda.rcp.views.NudgePositionerComposite;

import java.util.Arrays;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.layout.RowLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.wb.swt.SWTResourceManager;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.devices.vgscienta.AnalyserCapabilties;

public class I05_1ContinuousModeControllerComposite extends Composite {
	
	private static final Logger logger = LoggerFactory.getLogger(I05_1ContinuousModeControllerComposite.class);
	private Combo lensMode;
	private Combo passEnergyCombo;
	private Button startButton;
	private Button stopButton;
	private boolean running = false;
	private Button shutterButton;
	private AnalyserCapabilties capabilities;

	@SuppressWarnings("unused") //compiler thinks NudgePositionerComposite isn't used
	public I05_1ContinuousModeControllerComposite(Composite parent, AnalyserCapabilties capabilities) {
		super(parent, SWT.NONE);
		this.capabilities = capabilities;

		// Overall layout of groups
		RowLayoutFactory.swtDefaults().type(SWT.VERTICAL).spacing(5).wrap(false).applyTo(this);

		// Analyser group
		Group analyserGroup = new Group(this, SWT.DEFAULT);
		analyserGroup.setText("Analyser");
		GridLayoutFactory.swtDefaults().numColumns(5).spacing(10, 0).applyTo(analyserGroup);

		// Lens mode
		Label lensModeLabel = new Label(analyserGroup, SWT.NONE);
		lensModeLabel.setText("Lens Mode");
		GridDataFactory.swtDefaults().align(SWT.END, SWT.CENTER).grab(false, true).applyTo(lensModeLabel);

		lensMode = new Combo(analyserGroup, SWT.NONE);
		GridDataFactory.swtDefaults().grab(true, false).applyTo(lensMode);
		// Setup lens modes and select currently selected one
		lensMode.setItems(capabilities.getLensModes());
		String activeLensMode = JythonServerFacade.getInstance().evaluateCommand("analyser.getLensMode()");
		lensMode.select(Arrays.asList(lensMode.getItems()).indexOf(activeLensMode));

		SelectionListener lensModeListener = new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				logger.info("Changing analyser lens mode to " + lensMode.getText());
				JythonServerFacade.getInstance().runCommand("analyser.setLensMode(\"" + lensMode.getText() + "\")");
			}
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		};
		lensMode.addSelectionListener(lensModeListener);

		// Centre energy
		NudgePositionerComposite centre_energyNpc = new NudgePositionerComposite(analyserGroup, SWT.NONE, (Scannable) (Finder.getInstance().find("raw_centre_energy")), "centre_energy", false);
		GridDataFactory.swtDefaults().span(1, 2).applyTo(centre_energyNpc);
		// Acquire time
		NudgePositionerComposite acquire_timeNpc = new NudgePositionerComposite(analyserGroup, SWT.NONE, (Scannable) (Finder.getInstance().find("acquire_time")), null, false);
		GridDataFactory.swtDefaults().span(1, 2).applyTo(acquire_timeNpc);

		// Analyser Start Button
		startButton = new Button(analyserGroup, SWT.DEFAULT);
		startButton.setLayoutData(new GridData(100, SWT.DEFAULT));
		startButton.setText("Start");
		startButton.setToolTipText("Apply voltages and start acquiring");
		SelectionListener startListener = new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				JythonServerFacade.getInstance().runCommand("am.start()");
			}
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				// Do nothing
			}
		};
		startButton.addSelectionListener(startListener);

		// Analyser pass energy
		Label passEnergyLabel = new Label(analyserGroup, SWT.NONE);
		passEnergyLabel.setText("Pass Energy");
		GridDataFactory.swtDefaults().align(SWT.END, SWT.CENTER).grab(false, true).applyTo(passEnergyLabel);

		passEnergyCombo = new Combo(analyserGroup, SWT.NONE);
		// Call update to setup passEnergyCombo
		updatePassEnergyCombo();

		// Add listener to update analyser pass energy when changed
		SelectionListener passEnergyListener = new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				logger.info("Changing analyser pass energy to " + passEnergyCombo.getText());
				JythonServerFacade.getInstance().runCommand("analyser.setPassEnergy(" + passEnergyCombo.getText() + ")");
			}
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				// Do nothing
			}
		};
		passEnergyCombo.addSelectionListener(passEnergyListener);

		// Analyser Stop Button
		stopButton = new Button(analyserGroup, SWT.DEFAULT);
		stopButton.setLayoutData(new GridData(100, SWT.DEFAULT));
		stopButton.setText("Stop");
		stopButton.setToolTipText("Stop acquiring and zero supplies");
		SelectionListener stopListener = new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				//am stands for ArpesMonitor. So this stops the ARPES monitor.
				JythonServerFacade.getInstance().runCommand("am.stop()");
			}
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		};
		stopButton.addSelectionListener(stopListener);

		// Beamline group
		Group beamlineGroup = new Group(this, SWT.DEFAULT);
		beamlineGroup.setText("Beamline");
		GridLayoutFactory.swtDefaults().numColumns(5).spacing(10, 0).applyTo(beamlineGroup);

		new NudgePositionerComposite(beamlineGroup, SWT.NONE, (Scannable) (Finder.getInstance().find("energy")));
		new NudgePositionerComposite(beamlineGroup, SWT.NONE, (Scannable) (Finder.getInstance().find("exit_slit")));
		new NudgePositionerComposite(beamlineGroup, SWT.NONE, (Scannable) (Finder.getInstance().find("s2_ysize")));
		new NudgePositionerComposite(beamlineGroup, SWT.NONE, (Scannable) (Finder.getInstance().find("s2_xsize")));

		// Beamline shutter button
		shutterButton = new Button(beamlineGroup, SWT.NONE);
		shutterButton.setText("Close Shutter");
		shutterButton.setForeground(SWTResourceManager.getColor(SWT.COLOR_RED));
		shutterButton.setLayoutData(new GridData(100, SWT.DEFAULT));
		SelectionListener shutterButtonListener = new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				InterfaceProvider.getCommandRunner().runCommand("nano_shutter(1)");
			}
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		};
		shutterButton.addSelectionListener(shutterButtonListener);

		// Add an observer to the psu_mode scannable to automatically detect changes in EPICS and update the GUI
		Scannable psuModeScannable = (Scannable) (Finder.getInstance().find("psu_mode"));
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
					startButton.setEnabled(!running);
					startButton.setSelection(running);
					stopButton.setEnabled(running);
					stopButton.setSelection(!running);
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
		String psuMode = JythonServerFacade.getInstance().evaluateCommand("psu_mode.getPosition()").trim();
		// Get the available pass energies depending on the PSU mode
		Short[] passEnergiesShortArray;
		if (psuMode.equalsIgnoreCase("High Pass (XPS)")) {
			passEnergiesShortArray = capabilities.getPassEnergiesHigh();
		} else if (psuMode.equalsIgnoreCase("Low Pass (UPS)")) {
			passEnergiesShortArray = capabilities.getPassEnergiesLow();
		} else { // In this case mode wasn't matched give all pass energies EPICS knows about and error
			logger.error("Failed to match psu_mode! Not all pass energies avaliable are valid!");
			passEnergiesShortArray = capabilities.getPassEnergies();
		}

		// Convert the short array into a string ArrayList for combo box
		String[] passEnergiesStringArray = new String[passEnergiesShortArray.length];
		for (int i = 0; i < passEnergiesShortArray.length; i++) {
			passEnergiesStringArray[i] = passEnergiesShortArray[i].toString();
		}

		// Set the new pass energies
		passEnergyCombo.setItems(passEnergiesStringArray);

		// Automatically select the current pass energy if available in current PSU mode
		String activePassEnergy = JythonServerFacade.getInstance().evaluateCommand("analyser.getPassEnergy()");
		passEnergyCombo.select(Arrays.asList(passEnergiesStringArray).indexOf(activePassEnergy));
	}
}
