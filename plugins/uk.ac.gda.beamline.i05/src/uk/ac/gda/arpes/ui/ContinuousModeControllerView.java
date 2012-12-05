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
import gda.jython.JythonServerStatus;

import java.util.Comparator;
import java.util.Map;
import java.util.TreeMap;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.part.ViewPart;

import uk.ac.gda.arpes.detector.AnalyserCapabilties;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;
import uk.ac.gda.richbeans.components.wrappers.ComboWrapper;
import uk.ac.gda.richbeans.event.ValueEvent;
import uk.ac.gda.richbeans.event.ValueListener;
import org.eclipse.swt.widgets.Button;

public class ContinuousModeControllerView extends ViewPart {
	private AnalyserCapabilties capabilities;
	private Combo lensMode;
	private Combo passEnergy;
	private ScaleBox centreEnergy;
	private ScaleBox timePerStep;
	private ScaleBox photonEnergy;
	private Composite composite;
	private Button startButton;
	private Button stopButton;
	private Button zeroButton;

	public ContinuousModeControllerView() {
	}

	@Override
	public void createPartControl(Composite parent) {
		Composite comp = new Composite(parent, SWT.NONE);
		comp.setLayout(new GridLayout(3, false));

		capabilities = new AnalyserCapabilties();
		
		Label label = new Label(comp, SWT.NONE);
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		label.setText("lensMode");
		lensMode = new Combo(comp, SWT.NONE);
		lensMode.setItems(capabilities.lens2angles.keySet().toArray(new String[0]));
		lensMode.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));

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
		
		composite = new Composite(comp, SWT.NONE);
		composite.setLayout(new GridLayout(1, false));
		composite.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, false, false, 1, 5));
		SelectionListener lensModeListener = new SelectionListener() {
			
			@Override
			public void widgetSelected(SelectionEvent e) {
				JythonServerFacade.getInstance().runCommand(String.format("am.setLensMode(\"%s\")", lensMode.getItems()[lensMode.getSelectionIndex()] ));
			}
			
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				// TODO Auto-generated method stub
				
			}
		};
		lensMode.addSelectionListener(lensModeListener);
			
		
		startButton = new Button(composite, SWT.NONE);
		startButton.setText("Start");
		SelectionListener startListener = new SelectionListener() {
			
			@Override
			public void widgetSelected(SelectionEvent e) {
				JythonServerFacade.getInstance().runCommand("am.start()");				
			}
			
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				// TODO Auto-generated method stub
				
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
				// TODO Auto-generated method stub
				
			}
		};
		stopButton.addSelectionListener(stopListener);
		
		zeroButton = new Button(composite, SWT.NONE);
		zeroButton.setText("Zero Supplies");
		zeroButton.setEnabled(false);
		
		label = new Label(comp, SWT.NONE);
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		label.setText("passEnergy");
		passEnergy = new Combo(comp, SWT.NONE);
		passEnergy.setItems(passMap.keySet().toArray(new String[] {}));
		SelectionListener passEnergyListener = new SelectionListener() {
			
			@Override
			public void widgetSelected(SelectionEvent e) {
				JythonServerFacade.getInstance().runCommand(String.format("am.setPassEnergy(%d)", passMap.get(passEnergy.getItem(passEnergy.getSelectionIndex()))));
			}
			
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				// TODO Auto-generated method stub
				
			}
		};
		passEnergy.addSelectionListener(passEnergyListener);
		passEnergy.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));

		label = new Label(comp, SWT.NONE);
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		label.setText("centreEnergy");
		centreEnergy = new ScaleBox(comp, SWT.NONE);
		centreEnergy.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		centreEnergy.setUnit("eV");
		centreEnergy.setDecimalPlaces(3);
		centreEnergy.setFieldName("centreEnergy");
		new Label(centreEnergy, SWT.NONE);
		centreEnergy.on();
//		centreEnergy.addValueListener(this);
		
		label = new Label(comp, SWT.NONE);
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		label.setText("timePerStep");
		timePerStep = new ScaleBox(comp, SWT.NONE);
		timePerStep.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		timePerStep.setUnit("s");
		new Label(timePerStep, SWT.NONE);
//		timePerStep.addValueListener(this);

		label = new Label(comp, SWT.NONE);
		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		label.setText("photonEnergy");
		photonEnergy = new ScaleBox(comp, SWT.NONE);
		photonEnergy.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		photonEnergy.setUnit("eV");
		photonEnergy.setDecimalPlaces(3);
		new Label(photonEnergy, SWT.NONE);
//		photonEnergy.addValueListener(this);
	}

	@Override
	public void setFocus() {
	}
	
//	@Override
//	public void valueChangePerformed(ValueEvent e) {
//	
//			if (e.getFieldName().equals("lensMode")) { 
//				JythonServerFacade.getInstance().runCommand(String.format("am.setLensMode(\"%s\")", lensMode.getItems()[lensMode.getSelectionIndex()] ));
//			}
//			if (e.getFieldName().equals("passEnergy")) { 
//				JythonServerFacade.getInstance().runCommand(String.format("am.setPassEnergy(\"%5.5f\")", passEnergy.getItems()[passEnergy.getSelectionIndex()] ));
//			}		
//			if (e.getFieldName().equals("timePerStep")) { 
//				JythonServerFacade.getInstance().runCommand(String.format("am.setCollectionTime(\"%5.5f\")", ((Number) timePerStep.getValue()).doubleValue() ));
//			}	
//			if (e.getFieldName().equals("photonEnergy")) { 
//				JythonServerFacade.getInstance().runCommand(String.format("am.setPhotonEnergy(\"%5.5f\")", ((Number) photonEnergy.getValue()).doubleValue() ));
//			}
//	}

//	@Override
//	public String getValueListenerName() {
//		// TODO Auto-generated method stub
//		return null;
//	}
}