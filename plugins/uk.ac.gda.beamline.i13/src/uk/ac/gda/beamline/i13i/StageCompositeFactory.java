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
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
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
		Composite cmp;
		if( label != null){
			Group translationGroup = new Group(parent, SWT.SHADOW_NONE);
			translationGroup.setText(label);
			cmp = translationGroup;
		} else {
			cmp = new Composite(parent, SWT.NONE);
		}
		GridDataFactory.fillDefaults().applyTo(cmp);
		GridLayoutFactory.fillDefaults().margins(1, 1).spacing(2, 2).applyTo(cmp);

		
		
		for(StageCompositeDefinition s :  stageCompositeDefinitions){
			RotationViewer rotViewer = new RotationViewer(s.scannable, s.getLabel() != null ?s.getLabel() : s.scannable.getName(), s.isResetToZero());
			rotViewer.configureStandardStep(s.stepSize);
			rotViewer.setNudgeSizeBoxDecimalPlaces(s.decimalPlaces);
			if( s.isUseSteps() ){
				rotViewer.configureFixedStepButtons(s.smallStep, s.bigStep);
			}
			rotViewer.createControls(cmp, s.isSingleLineNudge()? SWT.SINGLE : SWT.NONE, s.isSingleLine());
		}
		
		return cmp;
	}

	@Override
	public Composite createComposite(Composite parent, int style, IWorkbenchPartSite iWorkbenchPartSite) {
		return (Composite) getTabControl(parent);
	}
	

}
