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

import org.eclipse.jface.viewers.ITreeContentProvider;

import uk.ac.diamond.daq.beamline.k11.view.control.DiffractionPathComposite;

/**
 * Provides content for the {@link DiffractionPathComposite} scan definition loader control
 *
 * @since GDA 9.13
 */
public class SavedScansContentProvider implements ITreeContentProvider {

	String[] sampleScanStrings = {"Rectangle 25 points per side Continuous Snake 10 by 5",
			"Line 6 points Stepped"};

	@Override
	public Object[] getElements(Object inputElement) {
		return sampleScanStrings;
	}

	@Override
	public Object[] getChildren(Object parentElement) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public Object getParent(Object element) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public boolean hasChildren(Object element) {
		// TODO Auto-generated method stub
		return false;
	}

}
