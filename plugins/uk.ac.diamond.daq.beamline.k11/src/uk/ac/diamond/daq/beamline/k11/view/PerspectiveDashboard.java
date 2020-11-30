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

package uk.ac.diamond.daq.beamline.k11.view;

import static uk.ac.gda.ui.tool.ClientSWTElements.createClientCompositeWithGridLayout;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGridDataFactory;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientLabel;

import org.eclipse.jface.resource.FontDescriptor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.part.ViewPart;

import uk.ac.diamond.daq.beamline.k11.view.PerspectiveComposite.PerspectiveType;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientResourceManager;

/**
 * The main Experiment configuration view visible in all k11 perspectives
 */
public class PerspectiveDashboard extends ViewPart {

	public static final String ID = "uk.ac.diamond.daq.beamline.k11.view.PerspectiveDashboard";

	@Override
	public void createPartControl(Composite parent) {
		parent.setBackground(parent.getDisplay().getSystemColor(SWT.COLOR_WIDGET_LIGHT_SHADOW));
		final Composite composite = createClientCompositeWithGridLayout(parent, SWT.NONE, 1);

		Label labelName = createClientLabel(composite, SWT.NONE, ClientMessages.DIAD,
				FontDescriptor.createFrom(ClientResourceManager.getDefaultFont(), 14, SWT.BOLD));
		createClientGridDataFactory().align(SWT.BEGINNING, SWT.END).indent(5, 5).applyTo(labelName);

		PerspectiveComposite.buildModeComposite(composite, PerspectiveType.IMAGING);
		new PerspectiveDashboardCompositeFactory().createComposite(composite, SWT.NONE);
	}

	@Override
	public void setFocus() {
		// experimentCompose.setFocus();
	}
}
