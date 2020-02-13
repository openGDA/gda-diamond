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

package uk.ac.diamond.daq.beamline.k11.view;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.plugin.AbstractUIPlugin;

/**
 * Base class of SWT wrappers to reduce typing when laying elements out in standard ways
 */
public class LayoutUtilities {


	/**
	 * Adds a {@link Composite} with {@link GridLayout} and fill alignment that will grab it's container's frame
	 *
	 * @param parent 	The enclosing {@link Composite}
	 * @return			The created {@link Composite}
	 */
	Composite addGridComposite(final Composite parent) {
		return addGridComposite(parent, SWT.NONE);
	}

	/**
	 * Creates a {@link Composite} with {@link GridLayout} and fill alignment that will grab it's container's frame
	 * using the specified style
	 *
	 * @param parent	The {@link Composite} to add the new one to
	 * @return			The created {@link Composite}
	 */
	Composite addGridComposite(final Composite parent, int style) {
		final Composite composite = new Composite(parent, style);
		composite.setLayout(new GridLayout());
		fillGrab().applyTo(composite);
		return composite;
	}

	/**
	 * Adds a {@link Composite} with {@link GridLayout} and default alignment that will grab it's container's frame
	 *
	 * @param parent 	The enclosing {@link Composite}
	 * @return			The created {@link Composite}
	 */
	Composite addSWTGridComposite(final Composite parent) {
		final Composite composite = new Composite(parent, SWT.NONE);
		composite.setLayout(new GridLayout());
		gridGrab().applyTo(composite);
		return composite;
	}

	/**
	 * Shorthand for fill alignment that will grab it's container's frame
	 *
	 * @return	The specified {@link GridDataFactory}
	 */
	GridDataFactory fillGrab() {
		return GridDataFactory.fillDefaults().grab(true, true);
	}

	/**
	 * Shorthand for fill alignment that will grab it's container's frame in the horizontal direction
	 *
	 * @return	The specified {@link GridDataFactory}
	 */
	GridDataFactory horizGrab() {
		return GridDataFactory.fillDefaults().grab(true, false);
	}

	/**
	 * Shorthand for fill alignment that will not grab it's container's frame
	 *
	 * @return	The specified {@link GridDataFactory}
	 */
	GridDataFactory noGrab() {
		return GridDataFactory.fillDefaults();
	}

	/**
	 * Shorthand for SWT alignment that will grab it's container's frame in the horizontal direction
	 *
	 * @return	The specified {@link GridDataFactory}
	 */
	GridDataFactory gridGrab() {
		return GridDataFactory.swtDefaults().align(SWT.FILL, SWT.CENTER).grab(true, false);
	}

	/**
	 * Retrieves and {@link Image} using the specified path
	 *
	 * @param path	The path to the image file
	 * @return		The retrieved {@link Image}
	 */
	Image getImage(final String path) {
		return AbstractUIPlugin.imageDescriptorFromPlugin("uk.ac.diamond.daq.beamline.k11", path).createImage();
	}

	/**
	 * Adds a centred {@link Label} using the supplied text with  fill alignment that will grab it's container's frame
	 *
	 * @param parent	The enclosing {@link Composite}
	 * @param text		The required text
	 */
	void addGrabbingCenteredLabel(final Composite parent, final String text) {
		Label label = new Label(parent, SWT.CENTER);
		label.setText(text);
		fillGrab().applyTo(label);
	}

}
