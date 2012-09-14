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

package uk.ac.gda.ui.components.custom;

import org.eclipse.draw2d.ColorConstants;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.forms.widgets.FormToolkit;

import uk.ac.gda.client.tomo.composites.MotionControlComposite;

/**
 *
 */
public class MotionControlCompositeCustom extends MotionControlComposite {

	public MotionControlCompositeCustom(Composite parent, FormToolkit toolkit, int style) {
		super(parent, toolkit, style);
	}

	@Override
	protected Composite createBeamlineControlTomoAlignmentCameraMotionComposite(Composite parent, FormToolkit toolkit) {
		Composite firstThreeComposites = toolkit.createComposite(parent);

		GridLayout layout = new GridLayout(2, true);
		setDefaultLayoutSettings(layout);
		layout.marginWidth = 1;
		layout.marginHeight = 1;
		layout.horizontalSpacing = 1;
		firstThreeComposites.setLayout(layout);
		firstThreeComposites.setBackground(ColorConstants.black);
		// 1
		Composite beamlineControlsComposite = createBeamlineControlComposite(firstThreeComposites, toolkit);
		beamlineControlsComposite.setLayoutData(new GridData(GridData.FILL_BOTH));
		// 2
		Composite tomoAlignmentControlsComposite = createTomoAlignmentControlComposite(firstThreeComposites, toolkit);
		tomoAlignmentControlsComposite.setLayoutData(new GridData(GridData.FILL_BOTH));
		
		return firstThreeComposites;
	}

}
