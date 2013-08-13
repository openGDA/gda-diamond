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
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;

import uk.ac.gda.beans.exafs.i20.SampleStagePosition;
import uk.ac.gda.common.rcp.util.GridUtils;
import uk.ac.gda.exafs.ui.data.ScanObjectManager;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;
import uk.ac.gda.richbeans.components.selector.ListEditor;
import uk.ac.gda.richbeans.components.selector.ListEditorUI;
import uk.ac.gda.richbeans.components.wrappers.SpinnerWrapper;
import uk.ac.gda.richbeans.components.wrappers.TextWrapper;
import uk.ac.gda.richbeans.components.wrappers.TextWrapper.TEXT_TYPE;

public class SampleStageComposite extends I20SampleParamsComposite implements ListEditorUI {

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
	private Composite main;

	@SuppressWarnings("unused")
	public SampleStageComposite(Composite parent, int style) {
		super(parent, style);

		GridLayoutFactory.fillDefaults().applyTo(this);

		main = new Composite(this, SWT.NONE);
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(main);

		final Label lblSamname = new Label(main, SWT.NONE);
		lblSamname.setText("Filename");
		GridDataFactory.swtDefaults().applyTo(lblSamname);
		sample_name = new TextWrapper(main, SWT.NONE);
		sample_name.setTextType(TEXT_TYPE.FILENAME);
		GridDataFactory.fillDefaults().applyTo(sample_name);

		final Label lblSamdesc = new Label(main, SWT.NONE);
		lblSamdesc.setText("Sample description");
		GridDataFactory.fillDefaults().applyTo(lblSamdesc);
		sample_description = new TextWrapper(main, SWT.WRAP | SWT.V_SCROLL | SWT.MULTI | SWT.BORDER);
		final GridData gd_descriptions = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gd_descriptions.heightHint = 73;
		gd_descriptions.widthHint = 400;
		sample_description.setLayoutData(gd_descriptions);

		
		final Label lblNumOfRep = new Label(main, SWT.NONE);
		lblNumOfRep.setText("Number of repetitions");
		lblNumOfRep.setToolTipText("Number of repetitions over this sample");
		GridDataFactory.fillDefaults().grab(true, false).applyTo(lblNumOfRep);
		numberOfRepetitions = new SpinnerWrapper(main, SWT.NONE);
		numberOfRepetitions.setValue(1);
		numberOfRepetitions.setToolTipText("Number of repetitions over this sample");
		GridDataFactory.fillDefaults().applyTo(numberOfRepetitions);
		
		if (ScanObjectManager.isXESOnlyMode()) {
			sample_roll = new ScaleBox(main, SWT.NONE);
			sample_roll.setUnit("°");
			sample_roll.setDecimalPlaces(2);
			sample_roll.setVisible(false);
			GridDataFactory.fillDefaults().exclude(true).applyTo(sample_roll);
			sample_pitch = new ScaleBox(main, SWT.NONE);
			sample_pitch.setUnit("°");
			sample_pitch.setDecimalPlaces(2);
			sample_pitch.setVisible(false);
			GridDataFactory.fillDefaults().exclude(true).applyTo(sample_pitch);
		} else {
			sample_finerotation = new ScaleBox(main, SWT.NONE);
			sample_finerotation.setUnit("°");
			sample_finerotation.setDecimalPlaces(2);
			sample_finerotation.setVisible(false);
			GridDataFactory.fillDefaults().exclude(true).applyTo(sample_finerotation);
		}

		Group motorPositionsGroup = new Group(main, SWT.NONE);
		motorPositionsGroup.setText("Motor positions");
		GridDataFactory.fillDefaults().hint(450, 150).grab(true, false).span(2, 1).applyTo(motorPositionsGroup);
		GridLayoutFactory.fillDefaults().numColumns(4).applyTo(motorPositionsGroup);
		
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
				if (ScanObjectManager.isXESOnlyMode()) {
					sample_finerotation.setValue(getValueAsString("sample_fine_rot"));
				} else {
					sample_roll.setValue(getValueAsString("sample_roll"));
					sample_pitch.setValue(getValueAsString("sample_pitch"));
				}
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent arg0) {
				widgetSelected(arg0);
			}
		});

		new Label(motorPositionsGroup, SWT.NONE);
		new Label(motorPositionsGroup, SWT.NONE);
		new Label(motorPositionsGroup, SWT.NONE);

		final Label lblSamx = new Label(motorPositionsGroup, SWT.NONE);
		lblSamx.setText("Sample x");
		sample_x = new ScaleBox(motorPositionsGroup, SWT.NONE);
		sample_x.setUnit("mm");
		sample_x.setDecimalPlaces(2);
		sample_x.setMinimum(-15.3);
		sample_x.setMaximum(14.1);
		GridDataFactory.fillDefaults().hint(100, 0).applyTo(sample_x);

		final Label lblSamrot = new Label(motorPositionsGroup, SWT.NONE);
		lblSamrot.setText("Sample rotation");
		sample_rotation = new ScaleBox(motorPositionsGroup, SWT.NONE);
		sample_rotation.setUnit("°");
		sample_rotation.setDecimalPlaces(2);
		sample_rotation.setMinimum(-225);
		sample_rotation.setMaximum(53);
		GridDataFactory.fillDefaults().applyTo(sample_rotation);

		final Label lblSamy = new Label(motorPositionsGroup, SWT.NONE);
		lblSamy.setText("Sample y");
		sample_y = new ScaleBox(motorPositionsGroup, SWT.NONE);
		sample_y.setUnit("mm");
		sample_y.setDecimalPlaces(2);
		sample_y.setMinimum(-0.1);
		sample_y.setMaximum(90.1);
		GridDataFactory.fillDefaults().applyTo(sample_y);

		if (ScanObjectManager.isXESOnlyMode()) {
			final Label lblSamfinerot = new Label(motorPositionsGroup, SWT.NONE);
			lblSamfinerot.setText("Sample fine rotation");
			sample_finerotation = new ScaleBox(motorPositionsGroup, SWT.NONE);
			sample_finerotation.setUnit("°");
			sample_finerotation.setDecimalPlaces(2);
			sample_finerotation.setMinimum(-127.4);
			sample_finerotation.setMaximum(180);
			GridDataFactory.fillDefaults().hint(100, 0).applyTo(sample_finerotation);
		} else {
			final Label lblSamroll = new Label(motorPositionsGroup, SWT.NONE);
			lblSamroll.setText("Sample roll");
			sample_roll = new ScaleBox(motorPositionsGroup, SWT.NONE);
			sample_roll.setUnit("°");
			sample_roll.setDecimalPlaces(2);
			sample_roll.setMinimum(-12.2);
			sample_roll.setMaximum(12.2);
			GridDataFactory.fillDefaults().hint(100, 0).applyTo(sample_roll);
		}
		
		final Label lblSamz = new Label(motorPositionsGroup, SWT.NONE);
		lblSamz.setText("Sample z");
		sample_z = new ScaleBox(motorPositionsGroup, SWT.NONE);
		sample_z.setUnit("mm");
		sample_z.setDecimalPlaces(2);
		sample_z.setMinimum(-15.3);
		sample_z.setMaximum(14.1);
		GridDataFactory.fillDefaults().applyTo(sample_z);

		if (ScanObjectManager.isXESOnlyMode()) {
			new Label(main, SWT.NONE);
			new Label(main, SWT.NONE);
		} else {

			final Label lblSampitch = new Label(motorPositionsGroup, SWT.NONE);
			lblSampitch.setText("Sample pitch");
			sample_pitch = new ScaleBox(motorPositionsGroup, SWT.NONE);
			sample_pitch.setUnit("°");
			sample_pitch.setDecimalPlaces(2);
			sample_pitch.setMinimum(-10.64);
			sample_pitch.setMaximum(10.66);
			GridDataFactory.fillDefaults().applyTo(sample_pitch);
		}

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

	public void selectionChanged(SampleStagePosition selectedBean) {
		selectedBean.setNumberOfRepetitions((Integer) numberOfRepetitions.getValue());
		selectedBean.setSample_description(sample_description.getText());
		selectedBean.setSample_finerotation((Double) sample_finerotation.getValue());
		selectedBean.setSample_rotation((Double) sample_rotation.getValue());
		selectedBean.setSample_x((Double) sample_x.getValue());
		selectedBean.setSample_y((Double) sample_y.getValue());
		selectedBean.setSample_z((Double) sample_z.getValue());
		selectedBean.setSample_roll((Double) sample_roll.getValue());
		selectedBean.setSample_pitch((Double) sample_pitch.getValue());
		selectedBean.setSample_name(sample_name.getText());
	}

	@Override
	public void notifySelected(ListEditor listEditor) {
		GridUtils.layoutFull(main);
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

}
