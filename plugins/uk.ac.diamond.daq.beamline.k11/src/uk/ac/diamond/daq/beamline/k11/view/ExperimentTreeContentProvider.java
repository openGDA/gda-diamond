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

import org.eclipse.jface.viewers.ITreeContentProvider;

public class ExperimentTreeContentProvider implements ITreeContentProvider {

	String[] exptNamesFromVisit = {"One", "Two", "THree", "Four",
			"AA34d3 Jun 2019", "AB76t2 Jun2019", "0-5 KN AA34d3", "280-370 KN AA34d3", "10-20 KN AB76t2", "100-120 KN AB76t2", "AA34d2 Jun 2019"};

	@Override
	public Object[] getElements(Object inputElement) {
		return exptNamesFromVisit;
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
