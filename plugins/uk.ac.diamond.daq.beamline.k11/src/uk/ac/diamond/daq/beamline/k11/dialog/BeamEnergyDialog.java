/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.dialog;

import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;

import uk.ac.diamond.daq.beamline.k11.EnergyWorkflowControllers;
import uk.ac.diamond.daq.client.gui.energy.BeamEnergyControl;
import uk.ac.diamond.daq.client.gui.energy.EnergyWorkflowController;

public class BeamEnergyDialog extends Dialog {

	public BeamEnergyDialog(Shell parentShell) {
		super(parentShell);
	}

	@Override
	protected Control createDialogArea(Composite parent) {

		Composite base = new Composite(parent, SWT.NONE);
		GridLayoutFactory.swtDefaults().numColumns(3).applyTo(base);
		GridDataFactory.swtDefaults().align(SWT.FILL, SWT.BEGINNING).grab(true, true).applyTo(base);

		createEnergyControl("Diffraction", EnergyWorkflowControllers.getDiffractionEnergyController(), base);
		createDivider(base);
		createEnergyControl("Imaging", EnergyWorkflowControllers.getImagingEnergyController(), base);

		return base;
	}

	private void createEnergyControl(String title, EnergyWorkflowController controller, Composite parent) {
		Composite composite = new Composite(parent, SWT.NONE);
		GridLayoutFactory.fillDefaults().applyTo(composite);
		GridDataFactory.swtDefaults().applyTo(composite);

		Label label = new Label(composite, SWT.NONE);
		label.setText(title);
		GridDataFactory.swtDefaults().align(SWT.CENTER, SWT.TOP).applyTo(label);

		new BeamEnergyControl(controller).draw(composite);
	}

	private void createDivider(Composite parent) {
		GridDataFactory.fillDefaults().span(1, 2).applyTo(new Label(parent, SWT.SEPARATOR | SWT.VERTICAL));
	}

	@Override
	protected Button createButton(Composite parent, int id, String label, boolean defaultButton) {
		if (id == IDialogConstants.CANCEL_ID) return null;
		return super.createButton(parent, id, label, defaultButton);
	}

	@Override
	protected void configureShell(Shell shell) {
		super.configureShell(shell);
		shell.setText("Beam energy control");
	}

}

