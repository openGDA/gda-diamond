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

package uk.ac.gda.arpes.ui;

import gda.jython.JythonServerFacade;

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
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.part.ViewPart;

import uk.ac.gda.arpes.detector.AnalyserCapabilties;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;

public class ContinuousModeControllerView extends ViewPart {
	private AnalyserCapabilties capabilities;
	private Combo lensMode;
	private Combo passEnergy;
	private ScaleBox centreEnergy;
	private ScaleBox timePerStep;
	private ScaleBox photonEnergy;
	private ScaleBox exitSlit;
	private Composite composite;
	private Button startButton;
	private Button stopButton;
	private Button zeroButton;
	private String[] lensModes;
	private String[] passArray;

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
		capabilities = new AnalyserCapabilties();
		
		Composite comp = new Composite(parent, SWT.NONE);
		comp.setLayout(new GridLayout(5, false));
		
		Label label = new Label(comp, SWT.NONE);
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		label.setText("lensMode");
		lensMode = new Combo(comp, SWT.NONE);
		lensMode.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 3, 1));
		lensModes = capabilities.lens2angles.keySet().toArray(new String[0]);
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
		final Map<String, Short> passMap = 	new TreeMap<String, Short>(passEComparator) {{
			put("1 eV", (short) 1);
			put("2 eV", (short) 2);
			put("5 eV", (short) 5);
			put("10 eV", (short) 10);
			put("20 eV", (short) 20);
			put("50 eV", (short) 50);
			put("100 eV", (short) 100);
			put("200 eV", (short) 200);
			put("500 eV", (short) 500);
		}};
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
		passEnergy.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 3, 1));

		label = new Label(comp, SWT.NONE);
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		label.setText("centreEnergy");
		centreEnergy = new ScaleBox(comp, SWT.NONE);
		centreEnergy.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		centreEnergy.setUnit("eV");
		centreEnergy.setDecimalPlaces(3);
		centreEnergy.setFieldName("centreEnergy");
		centreEnergy.on();
		
		label = new Label(comp, SWT.NONE);
		GridData gd_label = new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1);
		gd_label.horizontalIndent = 15;
		label.setLayoutData(gd_label);
		label.setText("photonEnergy");
		photonEnergy = new ScaleBox(comp, SWT.NONE);
		photonEnergy.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		photonEnergy.setUnit("eV");
		photonEnergy.setDecimalPlaces(3);
		
		label = new Label(comp, SWT.NONE);
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		label.setText("timePerStep");
		timePerStep = new ScaleBox(comp, SWT.NONE);
		timePerStep.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		timePerStep.setUnit("s");

		label = new Label(comp, SWT.NONE);
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		label.setText("exitSlit");
		exitSlit = new ScaleBox(comp, SWT.NONE);
		exitSlit.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		exitSlit.setUnit("mm");
		exitSlit.setDecimalPlaces(3);
	}

	@Override
	public void setFocus() {
	}
}