/*-
 * Copyright © 2023 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.tomography.view;

import java.util.Optional;

import org.dawnsci.mapping.ui.api.IMapFileController;
import org.dawnsci.mapping.ui.datamodel.LiveStreamMapObject;
import org.dawnsci.mapping.ui.datamodel.PlottableMapObject;
import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;

import uk.ac.diamond.daq.beamline.k11.Activator;
import uk.ac.gda.ui.tool.ClientSWTElements;

/**
 * Assumes that <ol>
 * <li> a live stream object is plotted, and
 * <li> the centre of rotation is aligned with the centre (in X) of the live stream
 * </ol>
 *
 * If live stream object not found, user will be prompted to supply the centre of rotation position
 */
public class CentreOfRotationLocator {

	private IMapFileController fileController;
	private Shell shell;

	private Optional<Double> userProvidedCOR = Optional.empty();

	public CentreOfRotationLocator(Shell shell) {
		this.shell = shell;
	}

	public double getCentreOfRotation() {
		return getFileController().getPlottedObjects().stream()
				.filter(LiveStreamMapObject.class::isInstance)
				.filter(PlottableMapObject::isPlotted)
				.map(PlottableMapObject::getRange)
				.map(this::centreOfRotationFromMapRange)
				.findFirst().orElseGet(this::promptUser);
	}

	private IMapFileController getFileController() {
		if (fileController == null) {
			fileController = Activator.getService(IMapFileController.class);
		}
		return fileController;
	}

	private double centreOfRotationFromMapRange(double[] range) {
		return (range[1]-range[0])/2.0;
	}

	private class UserPrompt extends Dialog {

		private Text corText;
		private double cor;

		protected UserPrompt(Shell parentShell) {
			super(parentShell);
		}

		@Override
		protected void configureShell(Shell newShell) {
			super.configureShell(newShell);
			newShell.setText("Centre of rotation required");
		}

		@Override
		protected Control createDialogArea(Composite parent) {
			var composite = (Composite) super.createDialogArea(parent);
			ClientSWTElements.label(composite, "Enter centre of rotation coordinate");
			corText = ClientSWTElements.numericTextBox(composite);
			return composite;
		}

		@Override
		protected void createButtonsForButtonBar(Composite parent) {
			createButton(parent, IDialogConstants.OK_ID, IDialogConstants.OK_LABEL, true);
		}

		@Override
		protected void okPressed() {
			cor = Double.parseDouble(corText.getText());
			super.okPressed();
		}

		public double getCentreOfRotation() {
			return cor;
		}
	}

	private double promptUser() {
		if (userProvidedCOR.isPresent()) return userProvidedCOR.get();
		var prompt = new UserPrompt(shell);
		if (prompt.open() == Window.OK) {
			var cor = prompt.getCentreOfRotation();

			userProvidedCOR = Optional.of(cor);

			return cor;
		} else {
			throw new IllegalStateException("I do not know what the centre of rotation is");
		}
	}
}
