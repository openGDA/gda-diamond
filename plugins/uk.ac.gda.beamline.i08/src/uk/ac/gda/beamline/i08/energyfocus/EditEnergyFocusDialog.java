/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i08.energyfocus;

import static uk.ac.diamond.daq.mapping.ui.experiment.focus.FocusScanUtils.saveConfig;

import org.eclipse.jface.dialogs.TitleAreaDialog;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Shell;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.function.ILinearFunction;
import uk.ac.diamond.daq.mapping.ui.experiment.focus.EnergyFocusFunctionDisplay;

public class EditEnergyFocusDialog extends TitleAreaDialog {
	private static final Logger logger = LoggerFactory.getLogger(EditEnergyFocusDialog.class);

	private static final String TITLE = "Energy focus function editor";
	private static final String MESSAGE = "Edit the parameters for the energy focus mapping";

	private final ILinearFunction energyFocusFunction;
	private final String energyFocusConfigPath;
	private EnergyFocusFunctionDisplay energyFocusDisplay;

	public EditEnergyFocusDialog(Shell parentShell, ILinearFunction energyFocusFunction, String energyFocusConfigPath) {
		super(parentShell);
		this.energyFocusFunction = energyFocusFunction;
		this.energyFocusConfigPath = energyFocusConfigPath;
	}

	@Override
	public void create() {
		super.create();
		setTitle(TITLE);
		setMessage(MESSAGE);
	}

	@Override
	protected Control createDialogArea(Composite parent) {
		final Composite dialogArea = (Composite) super.createDialogArea(parent);
		final Composite container = new Composite(dialogArea, SWT.NONE);
		GridDataFactory.fillDefaults().grab(true, true).applyTo(container);
		GridLayoutFactory.swtDefaults().numColumns(2).applyTo(container);
		energyFocusDisplay = new EnergyFocusFunctionDisplay(container, energyFocusFunction);
		return container;
	}

	@Override
	protected void okPressed() {
		energyFocusDisplay.updateEnergyFocusFunction();
		saveConfig(energyFocusFunction, energyFocusConfigPath, logger);
		super.okPressed();
	}

}
