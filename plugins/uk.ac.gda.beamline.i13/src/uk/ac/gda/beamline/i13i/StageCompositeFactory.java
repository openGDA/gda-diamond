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

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Group;
import org.eclipse.ui.IWorkbenchPartSite;

import uk.ac.gda.ui.viewer.RotationViewer;

public class StageCompositeFactory implements CompositeFactory {
	
	StageCompositeDefinition[] stageCompositeDefinitions;
	
	public StageCompositeDefinition[] getStageCompositeDefinitions() {
		return stageCompositeDefinitions;
	}

	public void setStageCompositeDefinitions(StageCompositeDefinition[] stageCompositeDefinitions) {
		this.stageCompositeDefinitions = stageCompositeDefinitions;
	}

	String label;

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

		
		
		for(StageCompositeDefinition s :  stageCompositeDefinitions){
			if( s.controlType == 0 || s.controlType==1){
				RotationViewer rotViewer = new RotationViewer(s.scannable, s.stepSize);
				rotViewer.setNudgeSizeBoxDecimalPlaces(s.decimalPlaces);
				if( s.controlType ==0){
					rotViewer.configureFixedStepButtons(s.smallStep, s.bigStep);
				}
				int style = s.controlType == 0 ? SWT.NONE : SWT.SINGLE;
				rotViewer.createControls(translationGroup, style, true);
			}
			
		}
		
		return translationGroup;
	}

	@Override
	public Composite createComposite(Composite parent, int style, IWorkbenchPartSite iWorkbenchPartSite) {
		return (Composite) getTabControl(parent);
	}
	

}
