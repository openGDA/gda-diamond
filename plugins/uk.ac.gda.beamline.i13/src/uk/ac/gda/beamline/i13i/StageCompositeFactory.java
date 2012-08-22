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

import gda.device.Scannable;
import gda.rcp.views.CompositeFactory;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Group;
import org.eclipse.ui.IWorkbenchPartSite;

import uk.ac.gda.ui.viewer.RotationViewer;

public class StageCompositeFactory implements CompositeFactory {
	
	
	Scannable[] scannables;
	String label;
	int decimalPlaces = 1;

	public void setScannables(Scannable[] scannables) {
		this.scannables = scannables;
	}

	public String getLabel() {
		return label;
	}

	public void setLabel(String label) {
		this.label = label;
	}

	public Control getTabControl(Composite parent) {

		
		Group translationGroup = new Group(parent, SWT.SHADOW_NONE);
		GridDataFactory.fillDefaults().applyTo(translationGroup);

		translationGroup.setText(label);
		translationGroup.setLayout(new GridLayout());

		
		
		for(Scannable s :  scannables){
			RotationViewer rotViewer = new RotationViewer(s, .1);
			rotViewer.setNudgeSizeBoxDecimalPlaces(decimalPlaces);
			rotViewer.createControls(translationGroup, SWT.SINGLE, true);
			
		}
		
		return translationGroup;
	}

	@Override
	public Composite createComposite(Composite parent, int style, IWorkbenchPartSite iWorkbenchPartSite) {
		return (Composite) getTabControl(parent);
	}
	

}
