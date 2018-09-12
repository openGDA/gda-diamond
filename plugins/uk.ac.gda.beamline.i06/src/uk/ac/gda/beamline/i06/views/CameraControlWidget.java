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

package uk.ac.gda.beamline.i06.views;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.jface.layout.RowLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;

import gda.factory.FindableBase;
import uk.ac.gda.client.live.stream.view.ICustomWidget;
import uk.ac.gda.client.livecontrol.LiveControl;

public class CameraControlWidget extends FindableBase implements ICustomWidget {
	private List<LiveControl> liveControls=new ArrayList<>();

	@Override
	public void createWidget(Composite composite) {
		if (liveControls.isEmpty()) {
			return;
		}

		Group cameraControlGroup=new Group(composite, SWT.BORDER);
		cameraControlGroup.setLayout(RowLayoutFactory.fillDefaults().spacing(5).wrap(true).create());
		cameraControlGroup.setText("Camera Control");
		for (LiveControl control : liveControls) {
			control.createControl(cameraControlGroup);
		}
	}

	public void setLiveControls(List<LiveControl> liveControls) {
		this.liveControls = liveControls;
	}

}
