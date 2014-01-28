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
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.forms.events.ExpansionAdapter;
import org.eclipse.ui.forms.events.ExpansionEvent;
import org.eclipse.ui.forms.widgets.ExpandableComposite;

import uk.ac.gda.beans.exafs.i20.CryostatParameters;
import uk.ac.gda.beans.exafs.i20.CryostatSampleDetails;
import uk.ac.gda.richbeans.components.scalebox.NumberBox;
import uk.ac.gda.richbeans.components.scalebox.RangeBox;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;
import uk.ac.gda.richbeans.components.selector.BeanSelectionEvent;
import uk.ac.gda.richbeans.components.selector.BeanSelectionListener;
import uk.ac.gda.richbeans.components.selector.VerticalListEditor;
import uk.ac.gda.richbeans.components.wrappers.ComboWrapper;
import uk.ac.gda.richbeans.components.wrappers.RadioWrapper;
import uk.ac.gda.richbeans.event.ValueEvent;
import uk.ac.gda.richbeans.event.ValueListener;

public class CryostatTableComposite extends I20SampleParamsComposite {
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
	private VerticalListEditor sampleDetails;

	public CryostatTableComposite(Composite parent, int style) {
		super(parent, style);
		setLayout(new FillLayout(SWT.VERTICAL));
		Composite main = new Composite(this, SWT.NONE);
		GridLayoutFactory.swtDefaults().numColumns(1).applyTo(main);
		Composite options = new Composite(main, SWT.NONE);
		options.setLayout(new FillLayout());
		loopChoice = new RadioWrapper(options, SWT.NONE, CryostatParameters.LOOP_OPTION);
		loopChoice.setValue(CryostatParameters.LOOP_OPTION[0]);
		createTemperatureComposite(main);
		createSampleComposite(main);
		this.layout();
	}

	protected void createSampleComposite(final Composite main) {
		Group sampleComposite = new Group(main, SWT.BORDER);
		sampleComposite.setText("Sample details");
		GridLayoutFactory.swtDefaults().numColumns(1).applyTo(sampleComposite);
		sampleDetails = new VerticalListEditor(sampleComposite, SWT.NONE);
		sampleDetails.setTemplateName("Sample");
		sampleDetails.setRequireSelectionPack(false);
		GridDataFactory.fillDefaults().hint(600, 400).grab(true, false).applyTo(sampleDetails);
		sampleDetails.setEditorClass(CryostatSampleDetails.class);
		sampleDetails.setFieldName("samples");
		sampleDetails.setNameField("sample_name");
		final CryostatSampleDetailsComposite sspComposite = new CryostatSampleDetailsComposite(sampleDetails, SWT.NONE);
		GridDataFactory.fillDefaults().grab(true, false).applyTo(sspComposite);
		sampleDetails.setEditorUI(sspComposite);
		sampleDetails.setListEditorUI(sspComposite);
		sampleDetails.addBeanSelectionListener(new BeanSelectionListener() {
			@Override
			public void selectionChanged(BeanSelectionEvent evt) {
				sspComposite.selectionChanged((CryostatSampleDetails) evt.getSelectedBean());
			}
		});
	}

	protected void createTemperatureComposite(final Composite main) {
		Group tempComposite = new Group(main, SWT.BORDER);
		tempComposite.setText("Cryostat settings");
		GridDataFactory.fillDefaults().applyTo(tempComposite);
		GridLayout gridLayout = new GridLayout();
		gridLayout.numColumns = 3;
		tempComposite.setLayout(gridLayout);
		Label temperatureLabel = new Label(tempComposite, SWT.NONE);
		temperatureLabel.setText("Temperature");
		temperature = new RangeBox(tempComposite, SWT.NONE, "Define setpoints...", "Set a single value, list all value or define a range.");
		temperature.setMaximum(300);
		temperature.setUnit("K");
		GridData gd_temperature = new GridData(SWT.FILL, SWT.CENTER, true, false);
		temperature.setLayoutData(gd_temperature);
		advancedExpandableComposite = new ExpandableComposite(tempComposite, SWT.NONE);
		advancedExpandableComposite.setText("Advanced");
		GridDataFactory.fillDefaults().span(1, 4).applyTo(advancedExpandableComposite);
		Composite advanced = new Composite(advancedExpandableComposite, SWT.NONE);
		GridDataFactory.fillDefaults().applyTo(advanced);
		GridLayoutFactory.fillDefaults().numColumns(4).applyTo(advanced);
		createAdvancedComposite(advanced);
		Label toleranceLabel = new Label(tempComposite, SWT.NONE);
		toleranceLabel.setText("Tolerance");
		tolerance = new ScaleBox(tempComposite, SWT.NONE);
		GridData gd_tolerance = new GridData(SWT.FILL, SWT.CENTER, true, false);
		tolerance.setLayoutData(gd_tolerance);
		tolerance.setMaximum(5);
		Label timeLabel = new Label(tempComposite, SWT.NONE);
		timeLabel.setText("Wait Time");
		waitTime = new ScaleBox(tempComposite, SWT.NONE);
		GridData gd_time = new GridData(SWT.FILL, SWT.CENTER, true, false);
		waitTime.setLayoutData(gd_time);
		waitTime.setDecimalPlaces(0);
		waitTime.setUnit("s");
		waitTime.setMaximum(400.0);
	}

	protected void createAdvancedComposite(final Composite advanced) {
		Label temperatureChangeProfileLabel = new Label(advanced, SWT.NONE);
		temperatureChangeProfileLabel.setText("Control Mode");
		controlMode = new ComboWrapper(advanced, SWT.READ_ONLY);
		controlMode.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		controlMode.setItems(CryostatParameters.CONTROL_MODE);
		controlMode.select(0);
		controlMode.addValueListener(new ValueListener() {
			
			@Override
			public void valueChangePerformed(ValueEvent e) {
				manualOutput.setEnabled(controlMode.getSelectionIndex() == 0);
			}
			
			@Override
			public String getValueListenerName() {
				return "grey out manual output listener";
			}
		});

		Label pLabel = new Label(advanced, SWT.RIGHT);
		pLabel.setText("P");
		p = new ScaleBox(advanced, SWT.NONE);
		p.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label heaterRangeLabel = new Label(advanced, SWT.NONE);
		heaterRangeLabel.setText("Heater Range");
		heaterRange = new ComboWrapper(advanced, SWT.READ_ONLY);
		heaterRange.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		heaterRange.setItems(CryostatParameters.HEATER_RANGE);
		heaterRange.select(0);

		Label iLabel = new Label(advanced, SWT.RIGHT);
		iLabel.setText("I");
		i = new ScaleBox(advanced, SWT.NONE);
		i.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label outputLabel = new Label(advanced, SWT.NONE);
		outputLabel.setText("Manual output");
		manualOutput = new ScaleBox(advanced, SWT.NONE);
		manualOutput.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label dLabel = new Label(advanced, SWT.RIGHT);
		dLabel.setText("D");
		d = new ScaleBox(advanced, SWT.NONE);
		d.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		advancedExpandableComposite.setClient(advanced);
		expansionListener = new ExpansionAdapter() {
			@Override
			public void expansionStateChanged(ExpansionEvent e) {
				getParent().getParent().getParent().getParent().layout();
				Composite temp = CryostatTableComposite.this.getParent().getParent().getParent().getParent()
						.getParent();
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
	
	public VerticalListEditor getSamples() {
		return sampleDetails;
	}
}
