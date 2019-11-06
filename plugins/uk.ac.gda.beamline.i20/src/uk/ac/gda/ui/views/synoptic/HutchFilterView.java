/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

package uk.ac.gda.ui.views.synoptic;

import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;

import gda.device.Scannable;
import gda.device.scannable.scannablegroup.IScannableGroupNamed;
import gda.factory.Finder;

public class HutchFilterView extends HardwareDisplayComposite {

	public HutchFilterView(Composite parent, int style) {
		super(parent, style, new GridLayout(1,false));
	}

	@Override
	protected void createControls(Composite parent) throws Exception {
		setViewName("Experimental Hutch Filters");

		IScannableGroupNamed atn5group = Finder.getInstance().find("atn5group");

		Group group = new Group(parent, SWT.NONE);
		group.setLayout(new GridLayout(2, false));
		group.setText("Experimental Hutch Filters");

		if (atn5group!=null) {
			String[] groupNames = atn5group.getGroupMembersNamesAsArray();

			for(int i=0; i<groupNames.length; i+=2) {
				Scannable nameScannable = Finder.getInstance().find(groupNames[i]);
				String filterName = (String) nameScannable.getPosition();
				Label filterNameLabel = new Label(group, SWT.NONE);
				filterNameLabel.setText(filterName);
				filterNameLabel.setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, false, 1, 1));

				EnumPositionerGui enumpositioner = new EnumPositionerGui(group, groupNames[i+1]);
				enumpositioner.createCombo();
			}
		}
	}
}
