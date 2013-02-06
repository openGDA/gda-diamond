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
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.forms.events.ExpansionAdapter;
import org.eclipse.ui.forms.events.ExpansionEvent;
import org.eclipse.ui.forms.widgets.ExpandableComposite;

import uk.ac.gda.beans.exafs.i20.CryostatParameters;
import uk.ac.gda.richbeans.components.scalebox.NumberBox;
import uk.ac.gda.richbeans.components.scalebox.RangeBox;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;
import uk.ac.gda.richbeans.components.wrappers.BooleanWrapper;
import uk.ac.gda.richbeans.components.wrappers.ComboWrapper;
import uk.ac.gda.richbeans.components.wrappers.RadioWrapper;
import uk.ac.gda.richbeans.components.wrappers.TextWrapper;
import uk.ac.gda.richbeans.components.wrappers.TextWrapper.TEXT_TYPE;

public class CryostatTableComposite extends I20SampleParamsComposite {

	private static final int MAX_NUM_SAMPLES = 3;

	private RadioWrapper loopChoice;

	private ScaleBox tolerance;
	private ScaleBox waitTime;
	private RangeBox temperature;

	private ComboWrapper controlMode;
	private ComboWrapper heaterRange;
	private ScaleBox p, i, d;
	private ScaleBox manualOutput;
	private ExpandableComposite advancedExpandableComposite;
	private ExpansionAdapter expansionListener;

	private BooleanWrapper[] sampleInUse = new BooleanWrapper[MAX_NUM_SAMPLES];
	private Button[] btnGetLiveValues = new Button[4];
	private ScaleBox[] y = new ScaleBox[MAX_NUM_SAMPLES];
	private ScaleBox[] fineposition = new ScaleBox[MAX_NUM_SAMPLES];
	private TextWrapper[] sampleDesc = new TextWrapper[MAX_NUM_SAMPLES];

	public CryostatTableComposite(Composite parent, int style) {
		super(parent, style);
		setLayout(new FillLayout(SWT.VERTICAL));

		final Composite main = new Composite(this, SWT.NONE);
		GridLayoutFactory.swtDefaults().numColumns(1).applyTo(main);

		final Composite options = new Composite(main, SWT.NONE);
		options.setLayout(new FillLayout());

		loopChoice = new RadioWrapper(options, SWT.NONE, CryostatParameters.LOOP_OPTION);
		loopChoice.setValue(CryostatParameters.LOOP_OPTION[0]);

		createTemperatureComposite(main);

		createSampleComposite(main);

		this.layout();

	}

	protected void createSampleComposite(final Composite main) {
		String[] columns = new String[] { "", "Number", "", "       Position      ",
				"           Fine Position          ", "                   Description                         " };

		final Group sampleComposite = new Group(main, SWT.BORDER);
		sampleComposite.setText("Sample holder options");
		GridDataFactory.fillDefaults().applyTo(sampleComposite);
		GridLayoutFactory.fillDefaults().spacing(0, 0).numColumns(columns.length).applyTo(sampleComposite);

		for (int col = 0; col < columns.length; col++) {
			Label lbl = new Label(sampleComposite, SWT.None);
			lbl.setText(columns[col]);
			lbl.setAlignment(SWT.CENTER);
		}

		for (int row = 0; row < MAX_NUM_SAMPLES; row++) {
			createRow(sampleComposite, row);
		}
	}

	private void createRow(Group table, final Integer row) {
		sampleInUse[row] = new BooleanWrapper(table, SWT.CENTER);
		sampleInUse[row]
				.setToolTipText("If selected the sample support stage will move to these positions.\nIf multiple samples selected then experiment will be repeated for each sample.");
		GridDataFactory.fillDefaults().applyTo(sampleInUse[row]);

		Label lbl = new Label(table, SWT.CENTER);
		lbl.setText("   " + row.toString() + "   ");

		btnGetLiveValues[row] = new Button(table, SWT.None);
		btnGetLiveValues[row].setText("Fetch");
		btnGetLiveValues[row].setToolTipText("Fill text boxes with current motor positions");
		GridDataFactory.fillDefaults().applyTo(btnGetLiveValues[row]);
		btnGetLiveValues[row].addSelectionListener(new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent arg0) {
				y[row].setValue(getValueAsString("sample_y"));
				fineposition[row].setValue(getValueAsString("sample_fine_rot"));
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent arg0) {
				widgetSelected(arg0);
			}
		});

		y[row] = new ScaleBox(table, SWT.None);
		y[row].setUnit("mm");
		GridDataFactory.fillDefaults().applyTo(y[row]);

		fineposition[row] = new ScaleBox(table, SWT.None);
		fineposition[row].setUnit("mm");
		GridDataFactory.fillDefaults().applyTo(fineposition[row]);

		sampleDesc[row] = new TextWrapper(table, SWT.BORDER | SWT.SINGLE);
		sampleDesc[row].setTextType(TEXT_TYPE.FREE_TXT);
		sampleDesc[row].setTextLimit(30);
		GridDataFactory.fillDefaults().grab(true, false).applyTo(sampleDesc[row]);
	}

	protected void createTemperatureComposite(final Composite main) {
		final Group tempComposite = new Group(main, SWT.BORDER);
		tempComposite.setText("Cryostat settings");
		GridDataFactory.fillDefaults().applyTo(tempComposite);
		final GridLayout gridLayout = new GridLayout();
		gridLayout.numColumns = 3;
		tempComposite.setLayout(gridLayout);

		final Label temperatureLabel = new Label(tempComposite, SWT.NONE);
		temperatureLabel.setText("Temperature");
		temperature = new RangeBox(tempComposite, SWT.NONE);
		temperature.setMaximum(300);
		temperature.setUnit("K");
		final GridData gd_temperature = new GridData(SWT.FILL, SWT.CENTER, true, false);
		temperature.setLayoutData(gd_temperature);

		this.advancedExpandableComposite = new ExpandableComposite(tempComposite, SWT.NONE);
		advancedExpandableComposite.setText("Advanced");
		GridDataFactory.fillDefaults().span(1, 4).applyTo(advancedExpandableComposite);

		final Composite advanced = new Composite(advancedExpandableComposite, SWT.NONE);
		GridDataFactory.fillDefaults().applyTo(advanced);
		GridLayoutFactory.fillDefaults().numColumns(4).applyTo(advanced);

		createAdvancedComposite(advanced);

		final Label toleranceLabel = new Label(tempComposite, SWT.NONE);
		toleranceLabel.setText("Tolerance");
		tolerance = new ScaleBox(tempComposite, SWT.NONE);
		final GridData gd_tolerance = new GridData(SWT.FILL, SWT.CENTER, true, false);
		tolerance.setLayoutData(gd_tolerance);
		tolerance.setMaximum(5);

		final Label timeLabel = new Label(tempComposite, SWT.NONE);
		timeLabel.setText("Wait Time");
		waitTime = new ScaleBox(tempComposite, SWT.NONE);
		final GridData gd_time = new GridData(SWT.FILL, SWT.CENTER, true, false);
		waitTime.setLayoutData(gd_time);
		waitTime.setUnit("s");
		waitTime.setMaximum(400.0);
	}

	protected void createAdvancedComposite(final Composite advanced) {

		final Label temperatureChangeProfileLabel = new Label(advanced, SWT.NONE);
		temperatureChangeProfileLabel.setText("Control Mode");
		controlMode = new ComboWrapper(advanced, SWT.READ_ONLY);
		controlMode.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		controlMode.setItems(CryostatParameters.CONTROL_MODE);
		controlMode.select(0);

		final Label pLabel = new Label(advanced, SWT.RIGHT);
		pLabel.setText("P");
		this.p = new ScaleBox(advanced, SWT.NONE);
		p.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		final Label heaterRangeLabel = new Label(advanced, SWT.NONE);
		heaterRangeLabel.setText("Heater Range");
		heaterRange = new ComboWrapper(advanced, SWT.READ_ONLY);
		heaterRange.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		heaterRange.setItems(CryostatParameters.HEATER_RANGE);
		heaterRange.select(0);

		final Label iLabel = new Label(advanced, SWT.RIGHT);
		iLabel.setText("I");
		this.i = new ScaleBox(advanced, SWT.NONE);
		i.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		final Label outputLabel = new Label(advanced, SWT.NONE);
		outputLabel.setText("Manual output");
		this.manualOutput = new ScaleBox(advanced, SWT.NONE);
		manualOutput.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		final Label dLabel = new Label(advanced, SWT.RIGHT);
		dLabel.setText("D");
		this.d = new ScaleBox(advanced, SWT.NONE);
		d.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		advancedExpandableComposite.setClient(advanced);
		this.expansionListener = new ExpansionAdapter() {
			@Override
			public void expansionStateChanged(ExpansionEvent e) {
				getParent().getParent().getParent().getParent().layout();
				Composite temp = CryostatTableComposite.this.getParent().getParent().getParent().getParent().getParent();
				temp.layout();
			}
		};
		advancedExpandableComposite.addExpansionListener(expansionListener);
	}

	@Override
	public void dispose() {
		advancedExpandableComposite.removeExpansionListener(expansionListener);
		super.dispose();
	}

	public RadioWrapper getLoopChoice() {
		return loopChoice;
	}

	public ScaleBox getTolerance() {
		return tolerance;
	}

	public ScaleBox getWaitTime() {
		return waitTime;
	}

	public NumberBox getTemperature() {
		return temperature;
	}

	public ComboWrapper getControlMode() {
		return controlMode;
	}

	public ComboWrapper getHeaterRange() {
		return heaterRange;
	}

	public ScaleBox getManualOutput() {
		return manualOutput;
	}

	public ScaleBox getP() {
		return p;
	}

	public ScaleBox getI() {
		return i;
	}

	public ScaleBox getD() {
		return d;
	}

	public BooleanWrapper getUseSample1() {
		return sampleInUse[0];
	}

	public ScaleBox getFinePosition1() {
		return fineposition[0];
	}

	public ScaleBox getPosition1() {
		return y[0];
	}

	public TextWrapper getSampleDescription1() {
		return sampleDesc[0];
	}

	public BooleanWrapper getUseSample2() {
		return sampleInUse[1];
	}

	public ScaleBox getFinePosition2() {
		return fineposition[1];
	}

	public ScaleBox getPosition2() {
		return y[1];
	}

	public TextWrapper getSampleDescription2() {
		return sampleDesc[1];
	}

	public BooleanWrapper getUseSample3() {
		return sampleInUse[2];
	}

	public ScaleBox getFinePosition3() {
		return fineposition[2];
	}

	public ScaleBox getPosition3() {
		return y[2];
	}

	public TextWrapper getSampleDescription3() {
		return sampleDesc[2];
	}

}
