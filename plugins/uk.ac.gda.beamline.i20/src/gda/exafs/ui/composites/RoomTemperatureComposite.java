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

package gda.exafs.ui.composites;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableUtils;
import gda.factory.Finder;

import org.apache.commons.lang.ArrayUtils;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StackLayout;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Link;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.richbeans.components.FieldBeanComposite;
import uk.ac.gda.richbeans.components.scalebox.IntegerBox;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;
import uk.ac.gda.richbeans.event.ValueEvent;
import uk.ac.gda.richbeans.event.ValueListener;

public class RoomTemperatureComposite extends FieldBeanComposite {

	private static Logger logger = LoggerFactory.getLogger(RoomTemperatureComposite.class);

	private ScaleBox[] x = new ScaleBox[4];
	private ScaleBox[] y = new ScaleBox[4];
	private ScaleBox[] z = new ScaleBox[4];
	private ScaleBox[] rotation = new ScaleBox[4];
	private ScaleBox[] roll = new ScaleBox[4];
	private ScaleBox[] pitch = new ScaleBox[4];
	
	private IntegerBox numberOfSamples;

	private Composite sampleDetailsComposite;

	private StackLayout sampleDetailsStackLayout;

	private Composite[] sampleComposite = new Composite[4];

	private Button[] btnumSamples = new Button[4];

	private Combo cmbNumSamples;

	private SelectionListener radioButtonListener;

	public RoomTemperatureComposite(Composite parent, int style) {
		super(parent, style);
		GridLayoutFactory.fillDefaults().applyTo(this);
		GridDataFactory.fillDefaults().applyTo(this);
		
		numberOfSamples = new IntegerBox(this, SWT.NONE);
		numberOfSamples.setVisible(false);

		Group numSamples = new Group(this, SWT.BORDER);
		GridDataFactory.fillDefaults().applyTo(numSamples);
		GridLayoutFactory.fillDefaults().numColumns(4).applyTo(numSamples);
		numSamples.setText("Number of samples");
		btnumSamples[0] = new Button(numSamples, SWT.RADIO);
		btnumSamples[0].setText("1");
		btnumSamples[1] = new Button(numSamples, SWT.RADIO);
		btnumSamples[1].setText("2");
		btnumSamples[2] = new Button(numSamples, SWT.RADIO);
		btnumSamples[2].setText("3");
		btnumSamples[3] = new Button(numSamples, SWT.RADIO);
		btnumSamples[3].setText("4");
		
		Group sampleDetails = new Group(this, SWT.BORDER);
		GridDataFactory.fillDefaults().applyTo(sampleDetails);
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(sampleDetails);
		sampleDetails.setText("Motor positions");

		final Label lblSampleDetailsChoice = new Label(sampleDetails, SWT.NONE);
		lblSampleDetailsChoice.setText("Values for sample:");
		cmbNumSamples = new Combo(sampleDetails, SWT.NONE);
		GridDataFactory.fillDefaults().applyTo(cmbNumSamples);
		cmbNumSamples.setItems(new String[] { "1", "2", "3", "4" });
		cmbNumSamples.select(0);

		sampleDetailsComposite = new Composite(sampleDetails, SWT.NONE);
		GridDataFactory.fillDefaults().span(2, 1).applyTo(sampleDetailsComposite);
		sampleDetailsStackLayout = new StackLayout();
		sampleDetailsComposite.setLayout(sampleDetailsStackLayout);

		sampleComposite[0] = new Composite(sampleDetailsComposite, SWT.NONE);
		createScaleBoxes(sampleComposite[0], 0);
		sampleComposite[1] = new Composite(sampleDetailsComposite, SWT.NONE);
		createScaleBoxes(sampleComposite[1], 1);
		sampleComposite[2] = new Composite(sampleDetailsComposite, SWT.NONE);
		createScaleBoxes(sampleComposite[2], 2);
		sampleComposite[3] = new Composite(sampleDetailsComposite, SWT.NONE);
		createScaleBoxes(sampleComposite[3], 3);
		sampleDetailsStackLayout.topControl = sampleComposite[0];

		createSelectionListeners();

	}

	private void createSelectionListeners() {
		cmbNumSamples.addSelectionListener(new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				int selected = cmbNumSamples.getSelectionIndex();
				sampleDetailsStackLayout.topControl = sampleComposite[selected];
				sampleDetailsComposite.layout();
				layout();
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});

		radioButtonListener = new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				String text = ((Button) e.getSource()).getText();
				int numSamples = Integer.parseInt(text);
				numberOfSamples.setValue(text);
				
				String[] newSampleChoices = new String[numSamples];
				for (int i  = 0; i < numSamples; i++){
					newSampleChoices[i] = String.valueOf(i+1);
				}
				cmbNumSamples.setItems(newSampleChoices);
				cmbNumSamples.select(0);
				
				sampleDetailsStackLayout.topControl = sampleComposite[0];
				for (int i = 0; i < 4; i++) {
					sampleComposite[i].setVisible(i <= numSamples -1);
				}

				layout();
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		};

		for (Button button : btnumSamples) {
			button.addSelectionListener(radioButtonListener);
		}
		
		numberOfSamples.addValueListener(new ValueListener() {
			
			@Override
			public void valueChangePerformed(ValueEvent e) {
				// TODO Auto-generated method stub
				
			}
			
			@Override
			public String getValueListenerName() {
				// TODO Auto-generated method stub
				return null;
			}
		});
	}

	private void createScaleBoxes(Composite sampleComposite, final int i) {
		GridDataFactory.fillDefaults().applyTo(sampleComposite);
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(sampleComposite);

		Button btnGetCurrentValues = new Button(sampleComposite, SWT.NONE);
		btnGetCurrentValues.setText("Get current values");
		GridDataFactory.fillDefaults().span(2, 1).applyTo(btnGetCurrentValues);

		btnGetCurrentValues.addSelectionListener(new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent arg0) {
				x[i].setValue(getValueAsString("sample_x"));
				y[i].setValue(getValueAsString("sample_y"));
				z[i].setValue(getValueAsString("sample_z"));
				rotation[i].setValue(getValueAsString("sample_rot"));
				// if (ScanObjectManager.isXESOnlyMode()) {
				// fineRotation.setValue(getValueAsString("sample_fine_rot"));
				// } else {
				roll[i].setValue(getValueAsString("sample_roll"));
				pitch[i].setValue(getValueAsString("sample_pitch"));
				// }
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent arg0) {
				widgetSelected(arg0);
			}
		});

		final Label xLabel = new Label(sampleComposite, SWT.NONE);
		xLabel.setText("x");
		x[i] = new ScaleBox(sampleComposite, SWT.NONE);
		x[i].setMinimum(-15);
		x[i].setMaximum(15);
		x[i].setUnit("mm");
		final GridData gd_x = new GridData(SWT.FILL, SWT.CENTER, true, false);
		x[i].setLayoutData(gd_x);

		final Label yLabel = new Label(sampleComposite, SWT.NONE);
		yLabel.setText("y");

		y[i] = new ScaleBox(sampleComposite, SWT.NONE);
		y[i].setMinimum(-20.0);
		y[i].setMaximum(20.0);
		final GridData gd_y = new GridData(SWT.FILL, SWT.CENTER, true, false);
		y[i].setLayoutData(gd_y);
		y[i].setUnit("mm");

		final Label zLabel = new Label(sampleComposite, SWT.NONE);
		zLabel.setText("z");

		z[i] = new ScaleBox(sampleComposite, SWT.NONE);
		z[i].setMinimum(-15.0);
		z[i].setMaximum(15);
		final GridData gd_z = new GridData(SWT.FILL, SWT.CENTER, true, false);
		z[i].setLayoutData(gd_z);
		z[i].setUnit("mm");

		final Label rotationLabel = new Label(sampleComposite, SWT.NONE);
		rotationLabel.setText("Rotation");

		final GridData gd_rotation = new GridData(SWT.FILL, SWT.CENTER, true, false);
		rotation[i] = new ScaleBox(sampleComposite, SWT.NONE);
		rotation[i].setMaximum(360);
		rotation[i].setLayoutData(gd_rotation);
		rotation[i].setUnit("°");

		// if (ScanObjectManager.isXESOnlyMode()) {
		// // fine rotation when in XES position
		// final Label fineRotationLabel = new Label(sampleComposite, SWT.NONE);
		// fineRotationLabel.setText("Fine Rotation");
		//
		// fineRotation = new ScaleBox(sampleComposite, SWT.NONE);
		// fineRotation.setMaximum(360);
		// fineRotation.setLayoutData(gd_rotation);
		// fineRotation.setUnit("°");
		// } else {

		// roll and yaw when in XAS position
		final Label rollLabel = new Label(sampleComposite, SWT.NONE);
		rollLabel.setText("Roll");

		roll[i] = new ScaleBox(sampleComposite, SWT.NONE);
		roll[i].setMinimum(-5);
		final GridData gd_roll = new GridData(SWT.FILL, SWT.CENTER, true, false);
		roll[i].setLayoutData(gd_roll);
		roll[i].setUnit("°");
		roll[i].setMaximum(5);

		final Link yawLabel = new Link(sampleComposite, SWT.NONE);
		yawLabel.setText("Pitch");

		pitch[i] = new ScaleBox(sampleComposite, SWT.NONE);
		pitch[i].setMinimum(-5);
		final GridData gd_yaw = new GridData(SWT.FILL, SWT.CENTER, true, false);
		pitch[i].setLayoutData(gd_yaw);
		pitch[i].setUnit("°");
		pitch[i].setMaximum(5);
		// }
	}

	private String getValueAsString(String scannableName) {

		final Scannable scannable = (Scannable) Finder.getInstance().find(scannableName);
		if (scannable == null) {
			logger.error("Scannable " + scannableName + " cannot be found");
			return "";
		}
		String[] position;
		try {
			position = ScannableUtils.getFormattedCurrentPositionArray(scannable);
		} catch (DeviceException e) {
			logger.error("Scannable " + scannableName + " position cannot be resolved.");
			return "";
		}
		String strPosition = ArrayUtils.toString(position);
		strPosition = strPosition.substring(1, strPosition.length() - 1);
		return strPosition;
	}

	public IntegerBox getNumberOfSamples(){
		return numberOfSamples;
	}
	
	public ScaleBox getSample1_x() {
		return x[0];
	}

	public ScaleBox getSample1_y() {
		return y[0];
	}

	public ScaleBox getSample1_z() {
		return z[0];
	}

	public ScaleBox getSample1_rotation() {
		return rotation[0];
	}

	public ScaleBox getSample1_roll() {
		return roll[0];
	}

	public ScaleBox getSample1_pitch() {
		return pitch[0];
	}

	public ScaleBox getSample2_x() {
		return x[1];
	}

	public ScaleBox getSample2_y() {
		return y[1];
	}

	public ScaleBox getSample2_z() {
		return z[1];
	}

	public ScaleBox getSample2_rotation() {
		return rotation[1];
	}

	public ScaleBox getSample2_roll() {
		return roll[1];
	}

	public ScaleBox getSample2_pitch() {
		return pitch[1];
	}

	public ScaleBox getSample3_x() {
		return x[2];
	}

	public ScaleBox getSample3_y() {
		return y[2];
	}

	public ScaleBox getSample3_z() {
		return z[2];
	}

	public ScaleBox getSample3_rotation() {
		return rotation[2];
	}

	public ScaleBox getSample3_roll() {
		return roll[2];
	}

	public ScaleBox getSample3_pitch() {
		return pitch[2];
	}

	public ScaleBox getSample4_x() {
		return x[3];
	}

	public ScaleBox getSample4_y() {
		return y[3];
	}

	public ScaleBox getSample4_z() {
		return z[3];
	}

	public ScaleBox getSample4_rotation() {
		return rotation[3];
	}

	public ScaleBox getSample4_roll() {
		return roll[3];
	}

	public ScaleBox getSample4_pitch() {
		return pitch[3];
	}

}
