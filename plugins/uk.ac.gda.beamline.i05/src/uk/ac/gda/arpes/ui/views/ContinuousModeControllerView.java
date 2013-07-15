/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package uk.ac.gda.arpes.ui.views;

import gda.device.Device;
import gda.device.MotorStatus;
import gda.device.Scannable;
import gda.factory.Finder;
import gda.jython.JythonServerFacade;
import gda.observable.IObserver;
import gda.rcp.views.MotorPositionViewerComposite;

import java.util.Comparator;
import java.util.Map;
import java.util.TreeMap;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.part.ViewPart;

import uk.ac.gda.beamline.i05.I05BeamlineActivator;
import uk.ac.gda.devices.vgscienta.AnalyserCapabilties;

public class ContinuousModeControllerView extends ViewPart implements IObserver {
	private AnalyserCapabilties capabilities;
	private Combo lensMode;
	private Combo passEnergy;
	private Composite composite;
	private Button startButton;
	private Button stopButton;
	private Button zeroButton;
	private String[] lensModes;
	private String[] passArray;
	private Device analyser;
	private boolean running = false;

	public ContinuousModeControllerView() {
	}

	private int comboForMode(String mode) {
		for (int i = 0; i < lensModes.length; i++) {
			if (lensModes[i].equals(mode))
				return i;
		} 
		return -1;
	}
	private int comboForPE(String pe) {
		pe = pe + " eV";
		for (int i = 0; i < passArray.length; i++) {
			if (passArray[i].equals(pe))
				return i;
		} 
		return -1;
	}
	
	@Override
	public void createPartControl(Composite parent) {	
		capabilities = (AnalyserCapabilties) Finder.getInstance().listAllLocalObjects(AnalyserCapabilties.class.getCanonicalName()).get(0);
		MotorPositionViewerComposite mpvc;
		
		Composite comp = new Composite(parent, SWT.NONE);
		comp.setLayout(new GridLayout(4, false));
		
		Label label = new Label(comp, SWT.NONE);
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		label.setText("lensMode");
		lensMode = new Combo(comp, SWT.NONE);
		lensMode.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 2, 1));
		lensModes = capabilities.getLensModes();
		lensMode.setItems(lensModes);
		String activeLensMode = JythonServerFacade.getInstance().evaluateCommand("analyser.getLensMode()");
		lensMode.select(comboForMode(activeLensMode));
		SelectionListener lensModeListener = new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				JythonServerFacade.getInstance().runCommand(String.format("analyser.setLensMode(\"%s\")", lensMode.getItems()[lensMode.getSelectionIndex()] ));
			}
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		};
		lensMode.addSelectionListener(lensModeListener);
			
		{
			composite = new Composite(comp, SWT.NONE);
			composite.setLayout(new GridLayout(1, false));
			composite.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, false, 1, 4));
			startButton = new Button(composite, SWT.NONE);
			
			startButton.setText("Start");
			SelectionListener startListener = new SelectionListener() {
				@Override
				public void widgetSelected(SelectionEvent e) {
					JythonServerFacade.getInstance().runCommand("am.start()");				
				}
				@Override
				public void widgetDefaultSelected(SelectionEvent e) {
				}
			};
			startButton.addSelectionListener(startListener);
			
			stopButton = new Button(composite, SWT.NONE);
			stopButton.setText("Stop");
			SelectionListener stopListener = new SelectionListener() {
				@Override
				public void widgetSelected(SelectionEvent e) {
					JythonServerFacade.getInstance().runCommand("am.stop()");				
				}
				@Override
				public void widgetDefaultSelected(SelectionEvent e) {
				}
			};
			stopButton.addSelectionListener(stopListener);
			
			zeroButton = new Button(composite, SWT.NONE);
			zeroButton.setText("Zero Supplies");
			zeroButton.setEnabled(true);
			SelectionListener zeroListener = new SelectionListener() {
				@Override
				public void widgetSelected(SelectionEvent e) {
					JythonServerFacade.getInstance().runCommand("analyser.zeroSupplies()");				
				}
				@Override
				public void widgetDefaultSelected(SelectionEvent e) {
				}
			};
			zeroButton.addSelectionListener(zeroListener);
		}
		
		Comparator<String> passEComparator = new Comparator<String>() {
			@Override
			public int compare(String o1, String o2) {
				return Integer.valueOf(o1.substring(0, o1.lastIndexOf(" "))).compareTo(Integer.valueOf(o2.substring(0, o2.lastIndexOf(" "))));
			}
		};
		final Map<String, Short> passMap = 	new TreeMap<String, Short>(passEComparator);
		for (short s: capabilities.getPassEnergies()) {
			passMap.put(String.format("%d eV", s), s);
		}
		label = new Label(comp, SWT.NONE);
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		label.setText("passEnergy");
		passEnergy = new Combo(comp, SWT.NONE);
		passArray = passMap.keySet().toArray(new String[] {});
		passEnergy.setItems(passArray);
		String activePE = JythonServerFacade.getInstance().evaluateCommand("analyser.getPassEnergy()");
		passEnergy.select(comboForPE(activePE));
		SelectionListener passEnergyListener = new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				JythonServerFacade.getInstance().runCommand(String.format("analyser.setPassEnergy(%d)", passMap.get(passEnergy.getItem(passEnergy.getSelectionIndex()))));
			}
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		};
		passEnergy.addSelectionListener(passEnergyListener);
		passEnergy.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 2, 1));

		mpvc = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("centre_energy")), true, "centreEnergy", 4, null, true, false);
		mpvc.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 2, 1));
		
		mpvc = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("pgm_energy")), true, "photonEnergy", 4, null, true, false);
		mpvc.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
	
		mpvc = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("acquire_time")), true, "timePerStep", 2, null, true, false);
		mpvc.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 2, 1));

		mpvc = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find(I05BeamlineActivator.EXIT_SLIT_SIZE_SCANNABLE)), true, "exitSlit", 4, null, true, false);
		mpvc.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		
		mpvc = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("sax")), true, "sax", 4, null, true, false);
		GridData gd;
		gd = new GridData(SWT.RIGHT, SWT.CENTER, false, false, 2, 1);
		gd.verticalIndent = 8;
		mpvc.setLayoutData(gd);
		mpvc = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("say")), true, "say", 4, null, true, false);
		gd = new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1);
		gd.verticalIndent = 8;
		mpvc.setLayoutData(gd);		mpvc = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("saz")), true, "saz", 4, null, true, false);
		gd = new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1);
		gd.verticalIndent = 8;
		mpvc.setLayoutData(gd);		
		
		mpvc = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("satilt")), true, "satilt", 4, null, true, false);
		mpvc.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 2, 1));
		mpvc = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("sapolar")), true, "sapolar", 4, null, true, false);
		mpvc.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		mpvc = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("saazimuth")), true, "saazimuth", 4, null, true, false);
		mpvc.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		
		mpvc = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("sample_temp")), true, "sample_temp", 4, null, true, false);
		gd = new GridData(SWT.RIGHT, SWT.CENTER, false, false, 2, 1);
		gd.verticalIndent = 8;
		mpvc.setLayoutData(gd);
		
		analyser = (Device) Finder.getInstance().find("analyser");
		if (analyser != null) {
			analyser.addIObserver(this);
		}
	}

	@Override
	public void setFocus() {
	}

	@Override
	public void update(Object source, Object arg) {
		if (startButton.isDisposed()) {
			analyser.deleteIObserver(this);
			return;
		}
		
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
}