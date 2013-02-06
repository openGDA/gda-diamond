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

package gda.exafs.ui.composites;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;

import uk.ac.gda.exafs.ui.data.ScanObjectManager;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;
import uk.ac.gda.richbeans.components.wrappers.BooleanWrapper;
import uk.ac.gda.richbeans.components.wrappers.TextWrapper;
import uk.ac.gda.richbeans.components.wrappers.TextWrapper.TEXT_TYPE;

public class RoomTemperatureTableComposite extends I20SampleParamsComposite {


	private String[] XES_COLUMNS = new String[] { "", "", "", "Sample", "", "            X            ",
			"            Y            ", "            Z            ", "       Rotation      ", "      Fine Rot      ",
			"       Sample Name       ", "                   Description                         " };
	private String[] XAS_COLUMNS = new String[] { "","", "Sample", "", "            X            ",
			"            Y            ", "            Z            ", "       Rotation      ",
			"           Roll          ", "          Pitch          ", "       Sample Name       ",
			"                   Description                         " };

	private static final int MAX_NUM_SAMPLES = 4;

	private BooleanWrapper[] sampleInUse = new BooleanWrapper[MAX_NUM_SAMPLES];
	private Button[] btnGetLiveValues = new Button[4];
	private ScaleBox[] x = new ScaleBox[MAX_NUM_SAMPLES];
	private ScaleBox[] y = new ScaleBox[MAX_NUM_SAMPLES];
	private ScaleBox[] z = new ScaleBox[MAX_NUM_SAMPLES];
	private ScaleBox[] rotation = new ScaleBox[MAX_NUM_SAMPLES];
	private ScaleBox[] finerotation = new ScaleBox[MAX_NUM_SAMPLES];
	private ScaleBox[] roll = new ScaleBox[MAX_NUM_SAMPLES];
	private ScaleBox[] pitch = new ScaleBox[MAX_NUM_SAMPLES];
	private TextWrapper[] sampleName = new TextWrapper[MAX_NUM_SAMPLES];
	private TextWrapper[] sampleDesc = new TextWrapper[MAX_NUM_SAMPLES];

	private Composite main;

	public RoomTemperatureTableComposite(Composite parent, int style) {
		super(parent, style);
		setLayout(new FillLayout(SWT.VERTICAL));
		main = new Composite(this, SWT.NONE);
		GridLayoutFactory.swtDefaults().numColumns(1).applyTo(main);

		buildTable();
		this.layout();
	}

	private void buildTable() {		
		Group table = new Group(main, SWT.BORDER);
		table.setText("Sample Details and Positions");
		GridDataFactory.fillDefaults().grab(true, false).applyTo(table);
		GridLayoutFactory.fillDefaults().spacing(0, 0).numColumns(XAS_COLUMNS.length).applyTo(table);

		for (int col = 0; col < XAS_COLUMNS.length; col++) {
			Label lbl = new Label(table, SWT.None);
			if (ScanObjectManager.isXESOnlyMode()) {
				lbl.setText(XES_COLUMNS[col]);
			} else {
				lbl.setText(XAS_COLUMNS[col]);
			}
			lbl.setAlignment(SWT.CENTER);
		}

		for (int row = 0; row < MAX_NUM_SAMPLES; row++) {
			if (ScanObjectManager.isXESOnlyMode()) {
				createXesRow(table, row);
			} else {
				createXasRow(table, row);
			}
		}
		table.layout();
		
		
	}

	private void createXesRow(Group table, final Integer row) {
		roll[row] = new ScaleBox(table, SWT.None);
		roll[row].setMinimum(-12.2);
		roll[row].setUnit("°");
		roll[row].setMaximum(12.2);
		roll[row].setVisible(false);

		pitch[row] = new ScaleBox(table, SWT.None);
		pitch[row].setMinimum(-10.6);
		pitch[row].setUnit("°");
		pitch[row].setMaximum(10.6);
		pitch[row].setVisible(false);

		sampleInUse[row] = new BooleanWrapper(table, SWT.None);
		sampleInUse[row]
				.setToolTipText("If selected the sample support stage will move to these positions.\nIf multiple samples selected then experiment will be repeated for each sample.");
		GridDataFactory.fillDefaults().applyTo(sampleInUse[row]);

		Label lbl = new Label(table, SWT.CENTER);
		lbl.setText("   " + row.toString()+ "   ");
		
		btnGetLiveValues[row] = new Button(table, SWT.None);
		btnGetLiveValues[row].setText("Fetch");
		btnGetLiveValues[row].setToolTipText("Fill text boxes with current motor positions");
		GridDataFactory.fillDefaults().applyTo(btnGetLiveValues[row]);
		btnGetLiveValues[row].addSelectionListener(new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent arg0) {
				x[row].setValue(getValueAsString("sample_x"));
				y[row].setValue(getValueAsString("sample_y"));
				z[row].setValue(getValueAsString("sample_z"));
				rotation[row].setValue(getValueAsString("sample_rot"));
				if (ScanObjectManager.isXESOnlyMode()) {
					finerotation[row].setValue(getValueAsString("sample_fine_rot"));
				} else {
					roll[row].setValue(getValueAsString("sample_roll"));
					pitch[row].setValue(getValueAsString("sample_pitch"));
				}
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent arg0) {
				widgetSelected(arg0);
			}
		});

		x[row] = new ScaleBox(table, SWT.None);
		x[row].setMinimum(-15.3);
		x[row].setMaximum(14.1);
		x[row].setUnit("mm");
		GridDataFactory.fillDefaults().applyTo(x[row]);

		y[row] = new ScaleBox(table, SWT.None);
		y[row].setMinimum(0.1);
		y[row].setMaximum(40.3);
		y[row].setUnit("mm");
		GridDataFactory.fillDefaults().applyTo(y[row]);

		z[row] = new ScaleBox(table, SWT.None);
		z[row].setMinimum(-15.3);
		z[row].setMaximum(14.1);
		z[row].setUnit("mm");
		GridDataFactory.fillDefaults().applyTo(z[row]);

		rotation[row] = new ScaleBox(table, SWT.None);
		rotation[row].setMinimum(-228);
		rotation[row].setMaximum(51);
		rotation[row].setUnit("°");
		GridDataFactory.fillDefaults().applyTo(rotation[row]);

		finerotation[row] = new ScaleBox(table, SWT.None);
		finerotation[row].setSize(0, 0);
		finerotation[row].setMaximum(360);
		finerotation[row].setUnit("°");
		GridDataFactory.fillDefaults().applyTo(finerotation[row]);

		sampleName[row] = new TextWrapper(table, SWT.BORDER | SWT.SINGLE);
		sampleName[row].setTextType(TEXT_TYPE.FILENAME);
		sampleName[row].setTextLimit(12);
		GridDataFactory.fillDefaults().applyTo(sampleName[row]);

		sampleDesc[row] = new TextWrapper(table, SWT.BORDER | SWT.SINGLE);
		sampleDesc[row].setTextType(TEXT_TYPE.FREE_TXT);
		sampleDesc[row].setTextLimit(60);
		GridDataFactory.fillDefaults().grab(true, false).applyTo(sampleDesc[row]);
	}

	private void createXasRow(Group table, final Integer row) {
		finerotation[row] = new ScaleBox(table, SWT.None);
		finerotation[row].setSize(0, 0);
		finerotation[row].setVisible(false);
		finerotation[row].setMaximum(360);
		finerotation[row].setUnit("°");

		sampleInUse[row] = new BooleanWrapper(table, SWT.CENTER);
		sampleInUse[row]
				.setToolTipText("If selected the sample support stage will move to these positions.\nIf multiple samples selected then experiment will be repeated for each sample.");
		GridDataFactory.fillDefaults().applyTo(sampleInUse[row]);

		Label lbl = new Label(table, SWT.CENTER);
		lbl.setText("   " + row.toString()+ "   ");
		
		btnGetLiveValues[row] = new Button(table, SWT.None);
		btnGetLiveValues[row].setText("Fetch");
		btnGetLiveValues[row].setToolTipText("Fill text boxes with current motor positions");
		GridDataFactory.fillDefaults().applyTo(btnGetLiveValues[row]);
		btnGetLiveValues[row].addSelectionListener(new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent arg0) {
				x[row].setValue(getValueAsString("sample_x"));
				y[row].setValue(getValueAsString("sample_y"));
				z[row].setValue(getValueAsString("sample_z"));
				rotation[row].setValue(getValueAsString("sample_rot"));
				if (ScanObjectManager.isXESOnlyMode()) {
					finerotation[row].setValue(getValueAsString("sample_fine_rot"));
				} else {
					roll[row].setValue(getValueAsString("sample_roll"));
					pitch[row].setValue(getValueAsString("sample_pitch"));
				}
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent arg0) {
				widgetSelected(arg0);
			}
		});

		x[row] = new ScaleBox(table, SWT.None);
		x[row].setMinimum(-15.3);
		x[row].setMaximum(14.1);
		x[row].setUnit("mm");
		GridDataFactory.fillDefaults().applyTo(x[row]);

		y[row] = new ScaleBox(table, SWT.None);
		y[row].setMinimum(0.1);
		y[row].setMaximum(40.3);
		y[row].setUnit("mm");
		GridDataFactory.fillDefaults().applyTo(y[row]);

		z[row] = new ScaleBox(table, SWT.None);
		z[row].setMinimum(-15.3);
		z[row].setMaximum(14.1);
		z[row].setUnit("mm");
		GridDataFactory.fillDefaults().applyTo(z[row]);

		rotation[row] = new ScaleBox(table, SWT.None);
		rotation[row].setMinimum(-228);
		rotation[row].setMaximum(51);
		rotation[row].setUnit("°");
		GridDataFactory.fillDefaults().applyTo(rotation[row]);

		roll[row] = new ScaleBox(table, SWT.None);
		roll[row].setMinimum(-12.2);
		roll[row].setUnit("°");
		roll[row].setMaximum(12.2);
		GridDataFactory.fillDefaults().applyTo(roll[row]);

		pitch[row] = new ScaleBox(table, SWT.None);
		pitch[row].setMinimum(-10.6);
		pitch[row].setUnit("°");
		pitch[row].setMaximum(10.6);
		GridDataFactory.fillDefaults().applyTo(pitch[row]);

		sampleName[row] = new TextWrapper(table, SWT.BORDER | SWT.SINGLE);
		sampleName[row].setTextType(TEXT_TYPE.FILENAME);
		sampleName[row].setTextLimit(12);
		GridDataFactory.fillDefaults().applyTo(sampleName[row]);

		sampleDesc[row] = new TextWrapper(table, SWT.BORDER | SWT.SINGLE);
		sampleDesc[row].setTextType(TEXT_TYPE.FREE_TXT);
		sampleDesc[row].setTextLimit(60);
		GridDataFactory.fillDefaults().grab(true, false).applyTo(sampleDesc[row]);
	}


	public BooleanWrapper getUseSample1() {
		return sampleInUse[0];
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

	public ScaleBox getSample1_finerotation() {
		return finerotation[0];
	}

	public ScaleBox getSample1_roll() {
		return roll[0];
	}

	public ScaleBox getSample1_pitch() {
		return pitch[0];
	}

	public TextWrapper getSample1_name() {
		return sampleName[0];
	}

	public TextWrapper getSample1_description() {
		return sampleDesc[0];
	}

	public BooleanWrapper getUseSample2() {
		return sampleInUse[1];
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

	public ScaleBox getSample2_finerotation() {
		return finerotation[1];
	}

	public ScaleBox getSample2_roll() {
		return roll[1];
	}

	public ScaleBox getSample2_pitch() {
		return pitch[1];
	}

	public TextWrapper getSample2_name() {
		return sampleName[1];
	}

	public TextWrapper getSample2_description() {
		return sampleDesc[1];
	}

	public BooleanWrapper getUseSample3() {
		return sampleInUse[2];
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

	public ScaleBox getSample3_finerotation() {
		return finerotation[2];
	}

	public ScaleBox getSample3_roll() {
		return roll[2];
	}

	public ScaleBox getSample3_pitch() {
		return pitch[2];
	}

	public TextWrapper getSample3_name() {
		return sampleName[2];
	}

	public TextWrapper getSample3_description() {
		return sampleDesc[2];
	}

	public BooleanWrapper getUseSample4() {
		return sampleInUse[3];
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

	public ScaleBox getSample4_finerotation() {
		return finerotation[3];
	}

	public ScaleBox getSample4_roll() {
		return roll[3];
	}

	public ScaleBox getSample4_pitch() {
		return pitch[3];
	}

	public TextWrapper getSample4_name() {
		return sampleName[3];
	}

	public TextWrapper getSample4_description() {
		return sampleDesc[3];
	}

}
