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

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StackLayout;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.forms.events.ExpansionAdapter;
import org.eclipse.ui.forms.events.ExpansionEvent;
import org.eclipse.ui.forms.widgets.ExpandableComposite;

import uk.ac.gda.beans.exafs.i20.CryostatParameters;
import uk.ac.gda.richbeans.components.FieldBeanComposite;
import uk.ac.gda.richbeans.components.scalebox.NumberBox;
import uk.ac.gda.richbeans.components.scalebox.RangeBox;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;
import uk.ac.gda.richbeans.components.wrappers.ComboWrapper;
import uk.ac.gda.richbeans.components.wrappers.RadioWrapper;
import uk.ac.gda.richbeans.components.wrappers.SpinnerWrapper;
import uk.ac.gda.richbeans.components.wrappers.TextWrapper;
import uk.ac.gda.richbeans.event.ValueAdapter;
import uk.ac.gda.richbeans.event.ValueEvent;

public class CryostatComposite extends FieldBeanComposite {

	private TextWrapper sampleNumber;
	private ComboWrapper sampleHolder;
	private ComboWrapper profileType;
	private ScaleBox time;
	private SpinnerWrapper heaterRange;
	private RangeBox temperature;
	private ScaleBox p, i, d, ramp;
	private StackLayout advStack;
	private ScaleBox tolerance;
	private ExpandableComposite advancedExpandableComposite;
	private Composite rampChoice, pidChoice, advChoice;
	private ExpansionAdapter expansionListener;
	private Label sampleNumberLabel;
	private RadioWrapper loopChoice;
	private Combo cmbSampleDetailsChoice;
	private Group positions;

	private ScaleBox finePosition1;
	private ScaleBox position1;
	private TextWrapper description1;
	private ScaleBox finePosition2;
	private ScaleBox position2;
	private TextWrapper description2;
	private ScaleBox finePosition3;
	private ScaleBox position3;
	private TextWrapper description3;
	private ScaleBox finePosition4;
	private ScaleBox position4;
	private TextWrapper description4;
	private Composite[] positionComposites;
	private StackLayout positionsStackLayout;
	private Composite positionsStack;

	public CryostatComposite(Composite parent, int style) {
		super(parent, style);
		setLayout(new FillLayout(SWT.VERTICAL));

		final Composite main = new Composite(this, SWT.NONE);
		GridLayoutFactory.swtDefaults().numColumns(1).applyTo(main);
		
		final Composite options = new Composite(main, SWT.NONE);
		options.setLayout(new FillLayout());
		
		loopChoice = new RadioWrapper(options,SWT.NONE, CryostatParameters.LOOP_OPTION);
		loopChoice.setValue(CryostatParameters.LOOP_OPTION[0]);

		createTemperatureComposite(main);

		createSampleComposite(main);

		this.layout();
		
	}

	protected void createSampleComposite(final Composite main) {
		final Group sampleComposite = new Group(main, SWT.BORDER);
		sampleComposite.setText("Sample holder options");
		GridDataFactory.fillDefaults().applyTo(sampleComposite);
		GridLayoutFactory.fillDefaults().numColumns(3).applyTo(sampleComposite);

		final Label sampleHolderLabel = new Label(sampleComposite, SWT.NONE);
		sampleHolderLabel.setText("Type");
		sampleHolder = new ComboWrapper(sampleComposite, SWT.READ_ONLY);
		sampleHolder.select(0);
		sampleHolder.setItems(new String[] { "4 Samples", "Liquid Cell" });
		GridDataFactory.fillDefaults().applyTo(sampleHolder);
		
		positions = new Group(sampleComposite, SWT.NONE);
		positions.setText("Details");
		GridDataFactory.fillDefaults().span(1,3).applyTo(positions);
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(positions);
		
//		final Label lblSampleDetailsChoice = new Label(positions, SWT.NONE);
//		lblSampleDetailsChoice.setText("Number");
		cmbSampleDetailsChoice = new Combo(positions, SWT.READ_ONLY);
		GridDataFactory.fillDefaults().applyTo(cmbSampleDetailsChoice);
		cmbSampleDetailsChoice.setItems(new String[] { "Sample 1","Sample 2","Sample 3" });
		cmbSampleDetailsChoice.select(0);
		cmbSampleDetailsChoice.addSelectionListener(new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				int index = cmbSampleDetailsChoice.getSelectionIndex();
				positionsStackLayout.topControl = positionComposites[index];
				positionComposites[index].layout();
				positionsStack.layout(); 
				positions.getParent().getParent().layout();
				sampleComposite.layout();
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				widgetSelected(e);
			}
		});
		
		positionsStack = new Composite(positions, SWT.NONE);
		GridDataFactory.fillDefaults().span(1,3).applyTo(positionsStack);
		positionsStackLayout = new  StackLayout();
		positionsStack.setLayout(positionsStackLayout);
		
		positionComposites = new Composite[3];
		
		positionComposites[0] = new Composite(positionsStack, SWT.NONE);
		GridDataFactory.swtDefaults().applyTo(positionComposites[0]);
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(positionComposites[0]);
		positionsStackLayout.topControl = positionComposites[0];
		final Label descLabel = new Label(positionComposites[0], SWT.NONE);
		descLabel.setText("Description");
		description1 = new TextWrapper(positionComposites[0], SWT.BORDER);
		description1.setTextType(TextWrapper.TEXT_TYPE.FREE_TXT);
		GridDataFactory.fillDefaults().applyTo(description1);
		final Label positionLabel = new Label(positionComposites[0], SWT.NONE);
		positionLabel.setText("Position");
		position1 = new ScaleBox(positionComposites[0], SWT.NONE);
		position1.setMinimum(-15);
		position1.setMaximum(15);
		position1.setUnit("mm");
		GridDataFactory.fillDefaults().applyTo(position1);
		final Label finePositionLabel = new Label(positionComposites[0], SWT.NONE);
		finePositionLabel.setText("Fine Position");
		finePosition1 = new ScaleBox(positionComposites[0], SWT.NONE);
		finePosition1.setDecimalPlaces(4);
		GridDataFactory.fillDefaults().applyTo(finePosition1);
		finePosition1.setUnit("mm");
		finePosition1.setMinimum(-1);
		finePosition1.setMaximum(1);
		positionComposites[0].layout();
		
		positionComposites[1] = new Composite(positionsStack, SWT.NONE);
		GridDataFactory.swtDefaults().applyTo(positionComposites[1]);
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(positionComposites[1]);
		final Label descLabel1 = new Label(positionComposites[1], SWT.NONE);
		descLabel1.setText("Description");
		description2 = new TextWrapper(positionComposites[1], SWT.BORDER);
		description2.setTextType(TextWrapper.TEXT_TYPE.FREE_TXT);
		GridDataFactory.fillDefaults().applyTo(description2);
		final Label positionLabel1 = new Label(positionComposites[1], SWT.NONE);
		positionLabel1.setText("Position");
		position2 = new ScaleBox(positionComposites[1], SWT.NONE);
		position2.setMinimum(-15);
		position2.setMaximum(15);
		position2.setUnit("mm");
		GridDataFactory.fillDefaults().applyTo(position2);
		final Label finePositionLabel1 = new Label(positionComposites[1], SWT.NONE);
		finePositionLabel1.setText("Fine Position");
		finePosition2 = new ScaleBox(positionComposites[1], SWT.NONE);
		finePosition2.setDecimalPlaces(4);
		GridDataFactory.fillDefaults().applyTo(finePosition2);
		finePosition2.setUnit("mm");
		finePosition2.setMinimum(-1);
		finePosition2.setMaximum(1);
		positionComposites[1].layout();
		
		positionComposites[2] = new Composite(positionsStack, SWT.NONE);
		GridDataFactory.swtDefaults().applyTo(positionComposites[2]);
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(positionComposites[2]);
		final Label descLabel2 = new Label(positionComposites[2], SWT.NONE);
		descLabel2.setText("Description");
		description3 = new TextWrapper(positionComposites[2], SWT.BORDER);
		description3.setTextType(TextWrapper.TEXT_TYPE.FREE_TXT);
		GridDataFactory.fillDefaults().applyTo(description3);
		final Label positionLabel2 = new Label(positionComposites[2], SWT.NONE);
		positionLabel2.setText("Position");
		position3 = new ScaleBox(positionComposites[2], SWT.NONE);
		position3.setMinimum(-15);
		position3.setMaximum(15);
		position3.setUnit("mm");
		GridDataFactory.fillDefaults().applyTo(position3);
		final Label finePositionLabel2 = new Label(positionComposites[2], SWT.NONE);
		finePositionLabel2.setText("Fine Position");
		finePosition3 = new ScaleBox(positionComposites[2], SWT.NONE);
		finePosition3.setDecimalPlaces(4);
		GridDataFactory.fillDefaults().applyTo(finePosition3);
		finePosition3.setUnit("mm");
		finePosition3.setMinimum(-1);
		finePosition3.setMaximum(1);
		positionComposites[2].layout();

//		positionComposites[3] = new Composite(positionsStack, SWT.NONE);
//		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(positionComposites[3]);
//		final Label descLabel3 = new Label(positionComposites[3], SWT.NONE);
//		descLabel3.setText("Description");
//		description4 = new TextWrapper(positionComposites[3], SWT.BORDER);
//		description4.setTextType(TextWrapper.TEXT_TYPE.FREE_TXT);
//		GridDataFactory.fillDefaults().applyTo(description4);
//		final Label positionLabel3 = new Label(positionComposites[3], SWT.NONE);
//		positionLabel3.setText("Position");
//		position4 = new ScaleBox(positionComposites[3], SWT.NONE);
//		position4.setMinimum(-15);
//		position4.setMaximum(15);
//		position4.setUnit("mm");
//		GridDataFactory.fillDefaults().applyTo(position4);
//		final Label finePositionLabel3 = new Label(positionComposites[3], SWT.NONE);
//		finePositionLabel3.setText("Fine Position");
//		finePosition4 = new ScaleBox(positionComposites[3], SWT.NONE);
//		finePosition4.setDecimalPlaces(4);
//		GridDataFactory.fillDefaults().applyTo(finePosition4);
//		finePosition4.setUnit("mm");
//		finePosition4.setMinimum(-1);
//		finePosition4.setMaximum(1);
//		positionComposites[3].layout();
		
		this.sampleNumberLabel = new Label(sampleComposite, SWT.NONE);
		sampleNumberLabel.setText("Sample(s) to use:");
		sampleNumberLabel.setToolTipText("Comma separated list of the order of sample numbers to use");
		sampleNumber = new TextWrapper(sampleComposite, SWT.BORDER);
		sampleNumber.setTextType(TextWrapper.TEXT_TYPE.FREE_TXT);
		sampleNumber.setValue("1,2,3");
		sampleNumber.setToolTipText("Comma separated list of the order of sample numbers to use");
		final GridData gd_temperature = new GridData(SWT.FILL, SWT.CENTER, false, false);
		sampleNumber.setLayoutData(gd_temperature);
		sampleHolder.addValueListener(new ValueAdapter("sampleHolderListener") {
			@Override
			public void valueChangePerformed(ValueEvent e) {
				updateSampleRange();
				sampleComposite.layout();
			}
		});
		sampleNumberLabel.setVisible(true);
		sampleNumber.setVisible(true);
		
		sampleComposite.getParent().layout();
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
		GridDataFactory.fillDefaults().span(1,4).applyTo(advancedExpandableComposite);
		
		final Composite advanced = new Composite(advancedExpandableComposite, SWT.NONE);
		GridDataFactory.fillDefaults().applyTo(advanced);
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(advanced);
		
		createAdvancedComposite(advanced);

		final Label toleranceLabel = new Label(tempComposite, SWT.NONE);
		toleranceLabel.setText("Tolerance");
		tolerance = new ScaleBox(tempComposite, SWT.NONE);
		final GridData gd_tolerance = new GridData(SWT.FILL, SWT.CENTER, true, false);
		tolerance.setLayoutData(gd_tolerance);
		tolerance.setMaximum(5);

		final Label timeLabel = new Label(tempComposite, SWT.NONE);
		timeLabel.setText("Wait Time");
		time = new ScaleBox(tempComposite, SWT.NONE);
		final GridData gd_time = new GridData(SWT.FILL, SWT.CENTER, true, false);
		time.setLayoutData(gd_time);
		time.setUnit("s");
		time.setMaximum(400.0);

//		return gd_temperature;
	}

	@SuppressWarnings("unused")
	protected void createAdvancedComposite(final Composite advanced) {
		final Label temperatureChangeProfileLabel = new Label(advanced, SWT.NONE);
		temperatureChangeProfileLabel.setText("Temperature Adjust");

		profileType = new ComboWrapper(advanced, SWT.READ_ONLY);
		profileType.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		profileType.setItems(new String[] { "PID", "Ramp" });
		profileType.select(0);

		new Label(advanced, SWT.NONE);

		this.advChoice = new Composite(advanced, SWT.NONE);
		advChoice.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		this.advStack = new StackLayout();
		advChoice.setLayout(advStack);

		this.pidChoice = new Composite(advChoice, SWT.NONE);
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(pidChoice);
		advStack.topControl = pidChoice;

		final Label pLabel = new Label(pidChoice, SWT.NONE);
		pLabel.setText("P");

		this.p = new ScaleBox(pidChoice, SWT.NONE);
		p.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		final Label iLabel = new Label(pidChoice, SWT.NONE);
		iLabel.setText("I");

		this.i = new ScaleBox(pidChoice, SWT.NONE);
		i.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		final Label dLabel = new Label(pidChoice, SWT.NONE);
		dLabel.setText("D");

		this.d = new ScaleBox(pidChoice, SWT.NONE);
		d.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		this.rampChoice = new Composite(advChoice, SWT.NONE);
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(rampChoice);

		final Label rampLabel = new Label(rampChoice, SWT.NONE);
		rampLabel.setText("Ramp");

		this.ramp = new ScaleBox(rampChoice, SWT.NONE);
		ramp.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		ramp.setUnit("K/minute");
		ramp.setMinimum(0.1d);
		ramp.setMaximum(100d);
		ramp.setValue(1d);

		final Label heaterLabel = new Label(advanced, SWT.NONE);
		heaterLabel.setText("Heater Range");

		heaterRange = new SpinnerWrapper(advanced, SWT.BORDER);
		heaterRange.setMinimum(1);
		heaterRange.setMaximum(5);
		heaterRange.setLayoutData(new GridData());

		advancedExpandableComposite.setClient(advanced);
		this.expansionListener = new ExpansionAdapter() {
			@Override
			public void expansionStateChanged(ExpansionEvent e) {
				updatePidLayout();
				getParent().getParent().getParent().getParent().layout();
			}
		};
		advancedExpandableComposite.addExpansionListener(expansionListener);

		profileType.setNotifyType(NOTIFY_TYPE.ALWAYS);
		profileType.addValueListener(new ValueAdapter("profileTypeListener") {
			@Override
			public void valueChangePerformed(ValueEvent e) {
				updatePidLayout();
				if (ramp.getNumericValue() < 0.1d) {
					ramp.setNumericValue(1d);
				}
			}
		});
	}

	protected void updateSampleRange() {
		final int index = sampleHolder.getSelectionIndex();
		if (index == 0) {
			sampleNumberLabel.setVisible(true);
			sampleNumber.setVisible(true);
			positions.setVisible(true);
		} else {
			sampleNumberLabel.setVisible(false);
			sampleNumber.setVisible(false);
			positions.setVisible(false);
		}
	}

	@Override
	public void setValue(Object value) {
		super.setValue(value);
		updateSampleRange();
	}

	@Override
	public void dispose() {
		advancedExpandableComposite.removeExpansionListener(expansionListener);
		super.dispose();
	}

	private void updatePidLayout() {
		advStack.topControl = profileType.getSelectionIndex() == 0 ? pidChoice : rampChoice;
		advChoice.layout();
	}

	public NumberBox getTemperature() {
		return temperature;
	}

	public ScaleBox getTolerance() {
		return tolerance;
	}

	public ScaleBox getTime() {
		return time;
	}

	public ComboWrapper getProfileType() {
		return profileType;
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

	public ScaleBox getRamp() {
		return ramp;
	}

	public SpinnerWrapper getHeaterRange() {
		return heaterRange;
	}

	public ComboWrapper getSampleHolder() {
		return sampleHolder;
	}

	public TextWrapper getSampleNumbers() {
		return sampleNumber;
	}

	public ScaleBox getFinePosition1() {
		return finePosition1;
	}

	public ScaleBox getPosition1() {
		return position1;
	}

	public TextWrapper getSampleDescription1() {
		return description1;
	}

	public ScaleBox getFinePosition2() {
		return finePosition2;
	}

	public ScaleBox getPosition2() {
		return position2;
	}

	public TextWrapper getSampleDescription2() {
		return description2;
	}

	public ScaleBox getFinePosition3() {
		return finePosition3;
	}

	public ScaleBox getPosition3() {
		return position3;
	}

	public TextWrapper getSampleDescription3() {
		return description3;
	}

	public ScaleBox getFinePosition4() {
		return finePosition4;
	}

	public ScaleBox getPosition4() {
		return position4;
	}

	public TextWrapper getSampleDescription4() {
		return description4;
	}
	
	public RadioWrapper getLoopChoice(){
		return loopChoice;
	}

	/**
	 * Used to show advanced in from test deck.
	 */
	public void _testSetAdvancedActive() {
		advancedExpandableComposite.setExpanded(true);
	}

	/**
	 * Used in testing.
	 * 
	 * @return true if pid top
	 */
	public boolean _testIsPidTop() {
		return advStack.topControl == pidChoice;
	}
}
