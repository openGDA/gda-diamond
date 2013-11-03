/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package gda;

import gda.rcp.views.CompositeFactory;

import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Composite;

import uk.ac.gda.epics.adviewer.ADController;
import uk.ac.gda.epics.adviewer.composites.MJPeg;
import uk.ac.gda.epics.adviewer.views.ADViewerCompositeFactory;
import uk.ac.gda.epics.adviewer.views.MJPegView;

public class SimpleADViewerCompositeFactory implements ADViewerCompositeFactory {

	private CompositeFactory compositeFactory;
	
	public CompositeFactory getCompositeFactory() {
		return compositeFactory;
	}

	public void setCompositeFactory(CompositeFactory stagesCompositeFactory) {
		this.compositeFactory = stagesCompositeFactory;
	}	
	
	
	@Override
	public Composite createComposite(ADController adController, Composite parent, MJPegView mjPegView, MJPeg mJPeg) {
		Composite top = new Composite(parent, SWT.NONE);
		top.setLayout(new RowLayout(SWT.VERTICAL));
		Composite c = new Composite(top, SWT.NONE);
		c.setLayout(new GridLayout(1, false));
		getCompositeFactory().createComposite(c, SWT.NONE, null);
		return c;
	}
}
