/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

import org.eclipse.core.commands.common.EventManager;

/**
 * Maintains the image mode for Mx Image View
 */
public class ImageModeManager extends EventManager {
	private static ImageModeManager manager; 
	
	private IImageMode currentMode;
	
	private ImageModeManager(){
	}
	
	/**
	 * Returns the singleton instance for this class
	 * 
	 * @return imageModeManager
	 */
	public static ImageModeManager getInstance(){
		if (manager == null){
			manager = new ImageModeManager();
		}
		return manager;
	}
	/**
	 * Set the current image mode and notifies and listeners
	 * of the change
	 * 
	 * @param mode mode to set
	 */
	public void setMode(IImageMode mode){
		if (this.currentMode != mode){
			this.currentMode = mode;
			fireValueChanged(mode);
		}
	}
	
	/**
	 * Notifies listeners
	 * 
	 * @param mode
	 */
	private void fireValueChanged(IImageMode mode) {
		Object[] listeners = getListeners();
		for (int i = 0; i < listeners.length; i++) {
			IImageModeListener listener = (IImageModeListener) listeners[i];
			listener.imageModeChanged(mode);
		}
		
	}
	
	/**
	 * Returns the current image mode
	 * @return image mode
	 */
	public IImageMode getMode(){
		return currentMode;
	}
	
	/**
	 * Adds the given image mode listener that will be notified
	 * when the image state changes. 
	 * <p>
	 * Listeners should be removed when no longer necessary.
	 * <p>
	 * 
	 * @param listener the listener to be added; must not be null
	 * @see #removeListener(IImageModeListener)
	 */
	public void addListener(IImageModeListener listener){
		addListenerObject(listener);
	}
	
	/**
	 * Removes the given listener from this manager.
	 * 
	 * @param listener the listener to be removed; must not be null
	 */
	public void removeListener(IImageModeListener listener){
		removeListenerObject(listener);
	}
	
}
