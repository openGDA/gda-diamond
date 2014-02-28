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

package uk.ac.gda.exafs.calibration.ui;

import org.eclipse.jface.wizard.Wizard;

import uk.ac.gda.exafs.calibration.data.EdeCalibrationModel;

public class EnergyCalibrationWizard extends Wizard {

	private final EnergyCalibrationWizardPage page;

	public EnergyCalibrationWizard(EdeCalibrationModel calibrationDataModel) {
		super();
		page = new EnergyCalibrationWizardPage(calibrationDataModel);
		setNeedsProgressMonitor(true);
	}

	@Override
	public void addPages() {
		addPage(page);
	}

	@Override
	public boolean performFinish() {
		return true;
	}
}
