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
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.ISelectionProvider;
import org.eclipse.jface.viewers.SelectionChangedEvent;

/**
 * Handles selection changes in the image viewer mode panel
 */
public class ModePaneSelectionProvider extends EventManager implements ISelectionProvider {

	private ISelection selection;

	@Override
	public void addSelectionChangedListener(ISelectionChangedListener listener) {
		addListenerObject(listener);
	}

	@Override
	public ISelection getSelection() {
		return selection;
	}

	@Override
	public void removeSelectionChangedListener(ISelectionChangedListener listener) {
		removeListenerObject(listener);
	}

	@Override
	public void setSelection(ISelection selection) {
		this.selection = selection;
		fireSelectionChanged();
	}

	/**
	 * Notify listeners that the selection has been changed
	 */
	private void fireSelectionChanged() {
		SelectionChangedEvent evt = new SelectionChangedEvent(this, getSelection());
		Object[] listeners = getListeners();
		for (int i = 0; i < listeners.length; i++) {
			ISelectionChangedListener listener = (ISelectionChangedListener) listeners[i];
			listener.selectionChanged(evt);
		}
	}
}
