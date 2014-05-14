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

package uk.ac.gda.dls.client.views;

import gda.rcp.views.CompositeFactory;

import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;

public class CompositeFactoryView extends ViewPart {

	public static String ID="uk.ac.gda.dls.client.views.CompositeFactoryView";
	
	static CompositeFactory _compositeFactory;
	
	
	
	public static CompositeFactory getCompositeFactory() {
		return _compositeFactory;
	}

	public static void setCompositeFactory(CompositeFactory compositeFactory) {
		_compositeFactory = compositeFactory;
	}

	public CompositeFactoryView() {
		// TODO Auto-generated constructor stub
	}

	@Override
	public void createPartControl(Composite parent) {
		_compositeFactory.createComposite(parent, SWT.NONE);

	}

	@Override
	public void setFocus() {
		// TODO Auto-generated method stub

	}

}
