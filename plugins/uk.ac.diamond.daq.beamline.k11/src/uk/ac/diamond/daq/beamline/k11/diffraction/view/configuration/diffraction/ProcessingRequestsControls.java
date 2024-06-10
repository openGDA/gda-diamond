/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;

import gda.rcp.views.CompositeFactory;
import uk.ac.gda.ui.tool.Reloadable;
import uk.ac.gda.ui.tool.processing.ProcessingRequestComposite;

public class ProcessingRequestsControls implements CompositeFactory, Reloadable {

	private Reloadable controls;

	@Override
	public Composite createComposite(Composite parent, int style) {
		var composite = new Composite(parent, SWT.NONE);
		GridDataFactory.fillDefaults().align(SWT.FILL, SWT.CENTER).grab(true, false).applyTo(composite);
		GridLayoutFactory.swtDefaults().applyTo(composite);

		new Label(composite, SWT.NONE).setText("Process requests");
		var processingControls = new ProcessingRequestComposite();
		processingControls.createComposite(composite, SWT.NONE);
		controls = processingControls;
		return composite;
	}

	@Override
	public void reload() {
		controls.reload();
	}
}
