/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i13i;


import org.eclipse.jface.viewers.ISelection;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;


/**
 * Interface to describe a mode in the sample/image view. 
 * Each mode provides a tab control and optionally an image,
 * selection and ability to provide a custom side plot.
 */

public interface IImageMode {

	/**
	 * Return a user-friendly name for this mode
	 * @return String name
	 */
	public abstract String getName();
	
	/**
	 * Returns the Control page for this tab to be 
	 * rendered in the CTabFolder
	 * @param parent CTabFolder
	 * @return Control must not be null
	 */
	public abstract Control getTabControl(Composite parent);

	/**
	 * Returns the image to be used when displaying the tab
	 * for this mode.
	 * <p>
	 * It is up to the mode to dispose of any image
	 * resources created.
	 * </p>
	 * @return a tab image, or null to use default image
	 */
	public abstract Image getTabImage();
	
	/**
	 * Returns the selection to be set when this mode is selected
	 * @return ISelection object, or null if there is no active selection
	 */
	public abstract ISelection getSelection(); 
	
	/**
	 * Supports move on click functionality in the sample view
	 * <p>
	 * Modes should return false if they wish to override mouse
	 * click behaviour with custom functionality
	 * </p>
	 * @return true if this mode supports move on click, else false
	 */
	public abstract boolean supportsMoveOnClick();
	

}