/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

import gda.rcp.views.CompositeFactory;

import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;

public class SimpleMode implements IImageMode {
	
	private Image image;
	String name;
	
	CompositeFactory compositeFactory;
	
	

	public void setName(String name) {
		this.name = name;
	}


	public CompositeFactory getCompositeFactory() {
		return compositeFactory;
	}


	public void setCompositeFactory(CompositeFactory compositeFactory) {
		this.compositeFactory = compositeFactory;
	}


	@Override
	public Control getTabControl(Composite parent) {

		return compositeFactory.createComposite(parent, SWT.NONE, null);
	}
	

	@Override
	public Image getTabImage() {
		if (image == null) {
			image = I13IBeamlineActivator.getImageDescriptor("icons/centring.gif").createImage();
		}
		return image;
	}

	@Override
	public ISelection getSelection() {
		return new StructuredSelection();
	}

	@Override
	public boolean supportsMoveOnClick() {
		return true;
	}

	@Override
	public String getName() {
		return name;
	}

}
