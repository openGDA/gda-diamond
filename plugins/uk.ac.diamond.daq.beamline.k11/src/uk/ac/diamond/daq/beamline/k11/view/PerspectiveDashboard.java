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

import org.eclipse.jface.resource.FontDescriptor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;

import uk.ac.diamond.daq.beamline.k11.view.PerspectiveComposite.PerspectiveType;
import uk.ac.diamond.daq.beamline.k11.view.control.StageController;
import uk.ac.gda.tomography.stage.IStageController;
import uk.ac.gda.ui.tool.ClientResourceManager;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.spring.SpringApplicationContextProxy;

/**
 * The main Experiment configuration view visible in all k11 perspectives
 */
public class PerspectiveDashboard extends ViewPart {

	public static final String ID = "uk.ac.diamond.daq.beamline.k11.view.PerspectiveDashboard";

	@Override
	public void createPartControl(Composite parent) {
		parent.setBackground(parent.getDisplay().getSystemColor(SWT.COLOR_WIDGET_LIGHT_SHADOW));
		final Composite composite = ClientSWTElements.createComposite(parent, SWT.NONE, 1);
		ClientSWTElements.createLabel(composite, SWT.NONE, "DIAD",
				FontDescriptor.createFrom(ClientResourceManager.getDefaultFont(), 14, SWT.BOLD));

		PerspectiveComposite.buildModeComposite(composite, PerspectiveType.TOMOGRAPHY);
		new PerspectiveDashboardCompositeFactory(getStageController()).createComposite(composite, SWT.NONE);
	}

	@Override
	public void setFocus() {
		// experimentCompose.setFocus();
	}

	private IStageController getStageController() {
		return SpringApplicationContextProxy.getBean(StageController.class);
	}

}
