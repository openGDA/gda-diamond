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
import org.eclipse.swt.layout.RowData;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;

import uk.ac.gda.beans.exafs.i20.CryostatSampleDetails;
import uk.ac.gda.common.rcp.util.GridUtils;
import uk.ac.gda.richbeans.components.scalebox.ScaleBox;
import uk.ac.gda.richbeans.components.selector.ListEditor;
import uk.ac.gda.richbeans.components.selector.ListEditorUI;
import uk.ac.gda.richbeans.components.wrappers.SpinnerWrapper;
import uk.ac.gda.richbeans.components.wrappers.TextWrapper;
import uk.ac.gda.richbeans.components.wrappers.TextWrapper.TEXT_TYPE;

public class CryostatSampleDetailsComposite extends I20SampleParamsComposite implements ListEditorUI {
	private ScaleBox position;
	private ScaleBox fineposition;
	private TextWrapper sample_name;
	private TextWrapper sample_description;
	private SpinnerWrapper numberOfRepetitions;
	private Button btnGetLiveValues;
	private Composite main;

	public CryostatSampleDetailsComposite(Composite parent, int style) {
		super(parent, style);
		GridLayoutFactory.fillDefaults().applyTo(this);
		main = new Composite(this, SWT.NONE);
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(main);
		Label lblSamname = new Label(main, SWT.NONE);
		lblSamname.setText("Filename");
		GridDataFactory.fillDefaults().grab(false, false).applyTo(lblSamname);
		sample_name = new TextWrapper(main, SWT.NONE);
		sample_name.setTextType(TEXT_TYPE.FILENAME);
		GridDataFactory.fillDefaults().applyTo(sample_name);
		Label lblSamdesc = new Label(main, SWT.NONE);
		lblSamdesc.setText("Sample description");
		GridDataFactory.fillDefaults().grab(false, false).applyTo(lblSamdesc);
		sample_description = new TextWrapper(main, SWT.WRAP | SWT.V_SCROLL | SWT.MULTI | SWT.BORDER);
		GridData gd_descriptions = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gd_descriptions.heightHint = 73;
		gd_descriptions.widthHint = 400;
		sample_description.setLayoutData(gd_descriptions);
		Label lblNumOfRep = new Label(main, SWT.NONE);
		lblNumOfRep.setText("Repetitions");
		lblNumOfRep.setToolTipText("Number of repetitions over this sample");
		GridDataFactory.fillDefaults().grab(false, false).applyTo(lblNumOfRep);
		numberOfRepetitions = new SpinnerWrapper(main, SWT.NONE);
		numberOfRepetitions.setValue(1);
		numberOfRepetitions.setToolTipText("Number of repetitions over this sample");
		GridDataFactory.fillDefaults().applyTo(numberOfRepetitions);
		Group motorPositionsGroup = new Group(main, SWT.NONE);
		motorPositionsGroup.setText("Motor positions");
		GridDataFactory.fillDefaults().grab(true, false).span(2, 1).applyTo(motorPositionsGroup);
		RowLayout mpgLayout = new RowLayout();
		mpgLayout.justify = true;
		mpgLayout.pack = true;
		motorPositionsGroup.setLayout(mpgLayout);
		btnGetLiveValues = new Button(motorPositionsGroup, SWT.None);
		btnGetLiveValues.setText("Fetch");
		btnGetLiveValues.setToolTipText("Fill text boxes with current motor positions");
		btnGetLiveValues.addSelectionListener(new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent arg0) {
				position.setValue(getValueAsString("sample_rot"));
				fineposition.setValue(getValueAsString("sample_fine_rot"));
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent arg0) {
				widgetSelected(arg0);
			}
		});
		Label lblSamx = new Label(motorPositionsGroup, SWT.NONE);
		lblSamx.setText("Position");
		position = new ScaleBox(motorPositionsGroup, SWT.NONE);
		position.setUnit("°");
		position.setDecimalPlaces(2);
		position.setLayoutData(new RowData(100, 25));
		Label lblSamy = new Label(motorPositionsGroup, SWT.NONE);
		lblSamy.setText("Fine position");
		fineposition = new ScaleBox(motorPositionsGroup, SWT.NONE);
		fineposition.setUnit("°");
		fineposition.setDecimalPlaces(2);
		fineposition.setLayoutData(new RowData(100, 25));
		this.layout();
	}

	public ScaleBox getPosition() {
		return position;
	}

	public ScaleBox getFinePosition() {
		return fineposition;
	}

	public TextWrapper getSample_name() {
		return sample_name;
	}

	public TextWrapper getSampleDescription() {
		return sample_description;
	}

	public SpinnerWrapper getNumberOfRepetitions() {
		return numberOfRepetitions;
	}

	public void selectionChanged(CryostatSampleDetails selectedBean) {
		selectedBean.setNumberOfRepetitions((Integer) numberOfRepetitions.getValue());
		selectedBean.setSampleDescription(sample_description.getText());
		selectedBean.setPosition((Double) position.getValue());
		selectedBean.setFinePosition((Double) fineposition.getValue());
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