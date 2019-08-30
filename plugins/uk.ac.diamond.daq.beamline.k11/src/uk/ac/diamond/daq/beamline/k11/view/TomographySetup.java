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
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.daq.beamline.k11.view.PerspectiveComposite.PerspectiveType;
import uk.ac.gda.tomography.base.TomographyParameterAcquisition;
import uk.ac.gda.tomography.scan.editor.TomographyResourceManager;
import uk.ac.gda.tomography.scan.editor.view.TomographyAcquisitionComposite;
import uk.ac.gda.tomography.ui.controller.TomographyPerspectiveController;
import uk.ac.gda.tomography.ui.tool.TomographySWTElements;

/**
 * The main Experiment configuration view visible in all k11 perspectives
 */
public class TomographySetup extends ViewPart {
	private static final Logger logger = LoggerFactory.getLogger(TomographySetup.class);

	private TomographyAcquisitionComposite acquisitionCompose;

	private final TomographyPerspectiveController perspectiveController = new TomographyPerspectiveController();


	@Override
	public void createPartControl(Composite parent) {
		parent.setBackground(parent.getDisplay().getSystemColor(SWT.COLOR_WIDGET_LIGHT_SHADOW));
		final Composite composite = TomographySWTElements.createComposite(parent, SWT.NONE, 1);
		TomographySWTElements.createLabel(composite, SWT.NONE, "DIAD",
				FontDescriptor.createFrom(TomographyResourceManager.getDefaultFont(), 14, SWT.BOLD));

		PerspectiveComposite.buildModeComposite(composite, PerspectiveType.TOMOGRAPHY);

		acquisitionCompose = new TomographyAcquisitionComposite(composite, perspectiveController.getTomographyAcquisitionController());
	}

	private TomographyParameterAcquisition getAcquisition() {
		// For now is just a dummy method
		return new TomographyParameterAcquisition();
	}



	@Override
	public void setFocus() {
//		experimentCompose.setFocus();
	}

	/**
	 * Retrieves and {@link Image} using the specified path
	 *
	 * @param path
	 *            The path to the image file
	 * @return The retrieved {@link Image}
	 */
	Image getImage(final String path) {
		return AbstractUIPlugin.imageDescriptorFromPlugin("uk.ac.diamond.daq.beamline.k11", path).createImage();
	}


}
