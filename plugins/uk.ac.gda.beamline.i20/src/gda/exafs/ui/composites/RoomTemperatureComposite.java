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

import org.dawnsci.common.richbeans.components.scalebox.ScaleBox;
import org.dawnsci.common.richbeans.components.selector.ListEditor;
import org.dawnsci.common.richbeans.components.selector.ListEditorUI;
import org.dawnsci.common.richbeans.components.wrappers.BooleanWrapper;
import org.dawnsci.common.richbeans.components.wrappers.SpinnerWrapper;
import org.dawnsci.common.richbeans.components.wrappers.TextWrapper;
import org.dawnsci.common.richbeans.components.wrappers.TextWrapper.TEXT_TYPE;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;

import uk.ac.gda.beans.exafs.i20.SampleStageParameters;
import uk.ac.gda.common.rcp.util.GridUtils;
import uk.ac.gda.exafs.ui.data.ScanObjectManager;

public class RoomTemperatureComposite extends I20SampleParametersComposite implements ListEditorUI {
	private ScaleBox sample_x;
	private ScaleBox sample_y;
	private ScaleBox sample_z;
	private ScaleBox sample_rotation;
	private ScaleBox sample_finerotation;
	private ScaleBox sample_roll;
	private ScaleBox sample_pitch;
	private TextWrapper sample_name;
	private TextWrapper sample_description;
	private SpinnerWrapper numberOfRepetitions;
	private Button btnGetLiveValues;
	//private Composite main;
	private Composite leftScannablesComposite;
	private Composite rightScannablesComposite;
	private BooleanWrapper btnSamX;
	private BooleanWrapper btnSamY;
	private BooleanWrapper btnSamZ;
	private BooleanWrapper btnRot;
	private BooleanWrapper btnRoll;
	private BooleanWrapper btnPitch;
	private BooleanWrapper btnFineRot;
	private Composite composite;

	public RoomTemperatureComposite(Composite parent, int style) {
		super(parent, style);
		GridLayoutFactory.fillDefaults().applyTo(this);
		composite = new Composite(this, SWT.NONE);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false, 1, 1));
		composite.setLayout(new GridLayout(2, false));

		Label lblSamname = new Label(composite, SWT.NONE);
		lblSamname.setText("Filename");
		GridDataFactory.swtDefaults().applyTo(lblSamname);

		sample_name = new TextWrapper(composite, SWT.NONE);
		sample_name.setTextType(TEXT_TYPE.FILENAME);
		GridDataFactory.fillDefaults().applyTo(sample_name);

		Label lblSamdesc = new Label(composite, SWT.NONE);
		lblSamdesc.setText("Sample description");
		GridDataFactory.fillDefaults().applyTo(lblSamdesc);

		sample_description = new TextWrapper(composite, SWT.WRAP | SWT.V_SCROLL | SWT.MULTI | SWT.BORDER);
		sample_description.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		Label lblNumOfRep = new Label(composite, SWT.NONE);
		lblNumOfRep.setText("Number of repetitions");
		lblNumOfRep.setToolTipText("Number of repetitions over this sample");
		GridDataFactory.fillDefaults().grab(true, false).applyTo(lblNumOfRep);

		numberOfRepetitions = new SpinnerWrapper(composite, SWT.NONE);
		numberOfRepetitions.setValue(1);
		numberOfRepetitions.setToolTipText("Number of repetitions over this sample");
		GridDataFactory.fillDefaults().applyTo(numberOfRepetitions);

		Group motorPositionsGroup = new Group(this, SWT.NONE);
		motorPositionsGroup.setText("Motor positions");
		motorPositionsGroup.setLayout(new GridLayout(2, false));

		leftScannablesComposite = new Composite(motorPositionsGroup, SWT.NONE);
		leftScannablesComposite.setLayout(new GridLayout(3, false));

		Label lblSamx = new Label(leftScannablesComposite, SWT.NONE);
		lblSamx.setText("Sample x");

		sample_x = new ScaleBox(leftScannablesComposite, SWT.NONE);
		sample_x.setUnit("mm");
		sample_x.setDecimalPlaces(2);
		sample_x.setMinimum(-15.3);
		sample_x.setMaximum(14.1);
		GridDataFactory.fillDefaults().hint(100, 0).applyTo(sample_x);
		btnSamX = new BooleanWrapper(leftScannablesComposite, SWT.CHECK);

		Label lblSamy = new Label(leftScannablesComposite, SWT.NONE);
		lblSamy.setText("Sample y");
		sample_y = new ScaleBox(leftScannablesComposite, SWT.NONE);
		sample_y.setUnit("mm");
		sample_y.setDecimalPlaces(2);
		sample_y.setMinimum(-0.1);
		sample_y.setMaximum(90.1);
		GridDataFactory.fillDefaults().hint(100, 0).applyTo(sample_y);
		btnSamY = new BooleanWrapper(leftScannablesComposite, SWT.CHECK);

		Label lblSamz = new Label(leftScannablesComposite, SWT.NONE);
		lblSamz.setText("Sample z");
		sample_z = new ScaleBox(leftScannablesComposite, SWT.NONE);
		sample_z.setUnit("mm");
		sample_z.setDecimalPlaces(2);
		sample_z.setMinimum(-15.3);
		sample_z.setMaximum(14.1);
		GridDataFactory.fillDefaults().hint(100, 0).applyTo(sample_z);
		btnSamZ = new BooleanWrapper(leftScannablesComposite, SWT.CHECK);

		rightScannablesComposite = new Composite(motorPositionsGroup, SWT.NONE);
		rightScannablesComposite.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		rightScannablesComposite.setLayout(new GridLayout(3, false));

		Label lblSamrot = new Label(rightScannablesComposite, SWT.NONE);
		lblSamrot.setText("Sample rotation");
		sample_rotation = new ScaleBox(rightScannablesComposite, SWT.NONE);
		sample_rotation.setUnit("°");
		sample_rotation.setDecimalPlaces(2);
		sample_rotation.setMinimum(-225);
		sample_rotation.setMaximum(53);
		GridDataFactory.fillDefaults().hint(100, 0).applyTo(sample_rotation);
		btnRot = new BooleanWrapper(rightScannablesComposite, SWT.CHECK);

		if (ScanObjectManager.isXESOnlyMode()) {
			Label lblSamfinerot = new Label(rightScannablesComposite, SWT.NONE);
			lblSamfinerot.setText("Sample fine rotation");
			sample_finerotation = new ScaleBox(rightScannablesComposite, SWT.NONE);
			sample_finerotation.setUnit("°");
			sample_finerotation.setDecimalPlaces(2);
			sample_finerotation.setMinimum(-127.4);
			sample_finerotation.setMaximum(180);
			GridDataFactory.fillDefaults().hint(100, 0).applyTo(sample_finerotation);
			btnFineRot = new BooleanWrapper(rightScannablesComposite, SWT.CHECK);
		}
		else {
			Label lblSamroll = new Label(rightScannablesComposite, SWT.NONE);
			lblSamroll.setText("Sample roll");
			sample_roll = new ScaleBox(rightScannablesComposite, SWT.NONE);
			sample_roll.setUnit("°");
			sample_roll.setDecimalPlaces(2);
			sample_roll.setMinimum(-12.2);
			sample_roll.setMaximum(12.2);
			GridDataFactory.fillDefaults().hint(100, 0).applyTo(sample_roll);
			btnRoll = new BooleanWrapper(rightScannablesComposite, SWT.CHECK);

			Label lblSampitch = new Label(rightScannablesComposite, SWT.NONE);
			lblSampitch.setText("Sample pitch");
			sample_pitch = new ScaleBox(rightScannablesComposite, SWT.NONE);
			sample_pitch.setUnit("°");
			sample_pitch.setDecimalPlaces(2);
			sample_pitch.setMinimum(-10.64);
			sample_pitch.setMaximum(10.66);
			GridDataFactory.fillDefaults().hint(100, 0).applyTo(sample_pitch);
			btnPitch = new BooleanWrapper(rightScannablesComposite, SWT.CHECK);
		}

		btnGetLiveValues = new Button(motorPositionsGroup, SWT.None);
		btnGetLiveValues.setText("Fetch");
		btnGetLiveValues.setToolTipText("Fill text boxes with current motor positions");

		btnGetLiveValues.addSelectionListener(new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent arg0) {
				sample_x.setValue(getValueAsString("sample_x"));
				sample_y.setValue(getValueAsString("sample_y"));
				sample_z.setValue(getValueAsString("sample_z"));
				sample_rotation.setValue(getValueAsString("sample_rot"));
				if (ScanObjectManager.isXESOnlyMode())
					sample_finerotation.setValue(getValueAsString("sample_fine_rot"));
				else {
					sample_roll.setValue(getValueAsString("sample_roll"));
					sample_pitch.setValue(getValueAsString("sample_pitch"));
				}
			}
			@Override
			public void widgetDefaultSelected(SelectionEvent arg0) {
				widgetSelected(arg0);
			}
		});

		this.layout();
	}

	public ScaleBox getSample_x() {
		return sample_x;
	}

	public ScaleBox getSample_y() {
		return sample_y;
	}

	public ScaleBox getSample_z() {
		return sample_z;
	}

	public ScaleBox getSample_rotation() {
		return sample_rotation;
	}

	public ScaleBox getSample_finerotation() {
		return sample_finerotation;
	}

	public ScaleBox getSample_roll() {
		return sample_roll;
	}

	public ScaleBox getSample_pitch() {
		return sample_pitch;
	}

	public TextWrapper getSample_name() {
		return sample_name;
	}

	public TextWrapper getSample_description() {
		return sample_description;
	}

	public SpinnerWrapper getNumberOfRepetitions() {
		return numberOfRepetitions;
	}

	public void selectionChanged(SampleStageParameters selectedBean) {
		//if(numberOfRepetitions!=null){
			int numberOfRepetitionsValue = (Integer) numberOfRepetitions.getValue();
			selectedBean.setNumberOfRepetitions(numberOfRepetitionsValue);
		//}
		//if(sample_description!=null)
			selectedBean.setSample_description(sample_description.getText());
		if(sample_finerotation!=null)
			selectedBean.setSample_finerotation((Double) sample_finerotation.getValue());
		if(sample_rotation!=null)
			selectedBean.setSample_rotation((Double) sample_rotation.getValue());
		//if(sample_x!=null)
			selectedBean.setSample_x((Double) sample_x.getValue());
		//if(sample_y!=null)
			selectedBean.setSample_y((Double) sample_y.getValue());
		//if(sample_z!=null)
			selectedBean.setSample_z((Double) sample_z.getValue());
		//if(sample_roll!=null)
			selectedBean.setSample_roll((Double) sample_roll.getValue());
		//if(sample_pitch!=null)
			selectedBean.setSample_pitch((Double) sample_pitch.getValue());
		//if(sample_name!=null)
			selectedBean.setSample_name(sample_name.getText());
	}

	@Override
	public void notifySelected(ListEditor listEditor) {
		//GridUtils.layoutFull(main);
		GridUtils.layoutFull(this);
		GridUtils.layoutFull(getParent());
	}

	@Override
	public boolean isDeleteAllowed(ListEditor listEditor) {
		return true;
	}

	@Override
	public boolean isAddAllowed(ListEditor listEditor) {
		return true;
	}

	@Override
	public boolean isReorderAllowed(ListEditor listEditor) {
		return true;
	}

	public BooleanWrapper getSamXEnabled() {
		return btnSamX;
	}

	public BooleanWrapper getSamYEnabled() {
		return btnSamY;
	}

	public BooleanWrapper getSamZEnabled() {
		return btnSamZ;
	}

	public BooleanWrapper getRotEnabled() {
		return btnRot;
	}

	public BooleanWrapper getRollEnabled() {
		return btnRoll;
	}

	public BooleanWrapper getPitchEnabled() {
		return btnPitch;
	}

	public BooleanWrapper getFineRotEnabled() {
		return btnFineRot;
	}

}