/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.experiment.ui;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.validation.IValidator;
import org.eclipse.core.databinding.validation.ValidationStatus;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jface.databinding.viewers.ViewersObservables;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.ComboViewer;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.wizard.WizardPage;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.ede.data.ClientConfig;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentUnit;
import uk.ac.gda.ui.components.NumberEditorControl;

public class TimingGroupsSetupPage extends WizardPage {

	private static Logger logger = LoggerFactory.getLogger(TimingGroupsSetupPage.class);

	private final TimingGroupWizardModel model = new TimingGroupWizardModel();

	private DataBindingContext dataBindingCtx;

	protected TimingGroupsSetupPage() {
		super("Timing groups");
		setTitle("Timing groups");
		setDescription("Setup timing group times and number of initial groups");
	}

	@Override
	public void createControl(Composite parent) {
		dataBindingCtx = new DataBindingContext();
		Composite container = new Composite(parent, SWT.NONE);
		GridLayout layout = new GridLayout();
		container.setLayout(layout);
		layout.numColumns = 2;

		NumberEditorControl experimentTimeControl;
		try {

			Label label = new Label(container, SWT.NONE);
			label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
			label.setText("Time Unit");
			ComboViewer expUnitSelectionCombo = new ComboViewer(container);
			expUnitSelectionCombo.getControl().setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
			expUnitSelectionCombo.setContentProvider(new ArrayContentProvider());
			expUnitSelectionCombo.setLabelProvider(new LabelProvider() {
				@Override
				public String getText(Object element) {
					return ((ExperimentUnit) element).getUnitText();
				}
			});
			expUnitSelectionCombo.setInput(ExperimentUnit.values());

			label = new Label(container, SWT.NONE);
			label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
			label.setText("Total time");

			experimentTimeControl = new NumberEditorControl(container, SWT.None, model, TimingGroupWizardModel.IT_TIME, false);
			experimentTimeControl.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);

			// FIXME Should have option to be able to set Value > 0

			experimentTimeControl.setRange(0.00001, Double.MAX_VALUE);
			experimentTimeControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

			label = new Label(container, SWT.NONE);
			label.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
			label.setText("No. of groups");

			NumberEditorControl noOfGroupsControl;

			noOfGroupsControl = new NumberEditorControl(container, SWT.None, model, TimingGroupWizardModel.NO_OF_GROUPS, false);
			noOfGroupsControl.setValidators(null, new IValidator() {
				@Override
				public IStatus validate(Object value) {
					if (!ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.canConvertToFrame(model.getUnit().convertToDefaultUnit(model.getItTime()) / (int) value)) {
						return ValidationStatus.info("The End time of each group will be rounded to nearest " + ExperimentUnit.MAX_RESOLUTION_IN_NANO_SEC + " " + ExperimentUnit.NANO_SEC.getUnitText());
					}
					return ValidationStatus.ok();
				}
			});
			noOfGroupsControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
			noOfGroupsControl.setRange(1, Integer.MAX_VALUE);
			dataBindingCtx.bindValue(
					ViewersObservables.observeSingleSelection(expUnitSelectionCombo),
					BeanProperties.value(TimingGroupWizardModel.UNIT_PROP_NAME).observe(model));

			dataBindingCtx.bindValue(
					BeanProperties.value(NumberEditorControl.UNIT_PROP_NAME).observe(experimentTimeControl),
					BeanProperties.value(TimingGroupWizardModel.UNIT_PROP_NAME).observe(model),
					new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
					new UpdateValueStrategy() {
						@Override
						public Object convert(Object value) {
							return ((ExperimentUnit) value).getUnitText();
						}
					});
		} catch (Exception e) {
			UIHelper.showError("Unable to create widget", e.getMessage());
			logger.error("Unable to create widget", e);
		}

		// Required to avoid an error in the system
		setControl(container);
		setPageComplete(true);
	}

	public TimingGroupWizardModel getTimingGroupWizardModel() {
		return model;
	}

	public static class TimingGroupWizardModel extends ObservableModel {

		public static final String UNIT_PROP_NAME = "unit";
		private ExperimentUnit unit = ExperimentUnit.SEC;

		public static final String NO_OF_GROUPS = "noOfGroups";
		private int noOfGroups = 1;

		public static final String IT_TIME = "itTime";
		private double itTime = 1;

		public void setItTime(double value) {
			this.firePropertyChange(IT_TIME, itTime, itTime = value);
		}

		public double getItTime() {
			return itTime;
		}

		public void setNoOfGroups(int noOfGroups) {
			this.firePropertyChange(NO_OF_GROUPS, this.noOfGroups, this.noOfGroups = noOfGroups);
		}

		public int getNoOfGroups() {
			return noOfGroups;
		}

		public ExperimentUnit getUnit() {
			return unit;
		}

		public void setUnit(ExperimentUnit unit) {
			this.firePropertyChange(UNIT_PROP_NAME, this.unit, this.unit = unit);
		}
	}
}