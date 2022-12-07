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

import org.eclipse.jface.wizard.Wizard;

import uk.ac.gda.exafs.data.EdeDataStore;
import uk.ac.gda.exafs.experiment.ui.data.ExternalTriggerSetting;
import uk.ac.gda.exafs.experiment.ui.data.TimeResolvedExperimentModel;

public class ExternalTriggerDetailsWizard extends Wizard {

	private ExternalTriggerDetailsWizardPage externalTriggerDetailsWizardPage;
	private final ExternalTriggerSetting externalTriggerSetting;

	public ExternalTriggerDetailsWizard(ExternalTriggerSetting externalTriggerSetting) {
		this.externalTriggerSetting = externalTriggerSetting;
	}

	@Override
	public void addPages() {
		externalTriggerDetailsWizardPage = new ExternalTriggerDetailsWizardPage(externalTriggerSetting);
		addPage(externalTriggerDetailsWizardPage);
	}

	@Override
	public boolean performFinish() {
		EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(TimeResolvedExperimentModel.EXTERNAL_TRIGGER_DETAILS, externalTriggerSetting.getTfgTrigger());
		return true;
	}
}
