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

import java.io.IOException;

import org.apache.commons.lang.StringUtils;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;

import gda.device.DeviceException;

public class OverviewButtonsView extends HardwareDisplayComposite {

	public static final String ID = "uk.ac.gda.ui.views.synoptic.OverviewButtonsView";
	private Composite group;

	public OverviewButtonsView(Composite parent, int style) {
		super(parent, style, new GridLayout(1, true));
	}

	@Override
	protected void createControls(Composite parent) throws Exception {
		setViewName("Beamline overview");
		createLabels(parent);
	}

	private Button addButton(Composite parent, String pathToImage, String labelText) throws IOException {
		return addButton(parent, pathToImage, labelText, "");
	}

	private Button addButton(Composite parent, String pathToImage, String labelText, final String viewName) throws IOException {
		Composite group = new Composite(parent, SWT.NONE);
		group.setLayout(new GridLayout(1, false));
		group.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true, 1, 1));

		Label label = new Label(group, SWT.NONE);
		label.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, false, 1, 1));
		label.setText(labelText);

		Button button = new Button(group, SWT.PUSH);
		button.setImage(getImageFromDalPlugin(pathToImage));
		button.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true, 1, 1));

		// Add listener to open view when button is clicked
		if (!StringUtils.isEmpty(viewName)) {
			button.setToolTipText("Open controls for "+labelText);
			button.addSelectionListener(new SelectionAdapter() {
				@Override
				public void widgetSelected(SelectionEvent e) {
					SynopticView.openView(viewName);
				}
			});
		} else {
			button.setToolTipText("Does not open any controls");
		}
		return button;
	}

	private void createLabels(Composite parent) throws IOException, DeviceException {
		group = new Composite(parent, SWT.NONE);
		group.setLayout(new GridLayout(19, false));

		addButton(group, "oe thumb images/slits_thumb.png", "S1");
		addButton(group, "oe thumb images/diagnostic.png", "D1");
		addButton(group, "oe thumb images/m1_thumb.png", "M1");
		addButton(group, "oe thumb images/m2_thumb.png", "M2");
		addButton(group, "oe thumb images//diagnostic.png", "D3");
		addButton(group, "oe thumb images/qcm_thumb.png", "QCM");
		addButton(group, "oe thumb images/diagnostic.png", "D5");
		addButton(group, "oe thumb images/m3_thumb.png", "M3");
		addButton(group, "oe thumb images//diagnostic.png", "D6");
		addButton(group, "oe thumb images/m4_thumb.png", "M4");
		addButton(group, "oe thumb images/diagnostic.png", "D7");

		EnumPositionerGui experimentalShutter = new EnumPositionerGui(group, "shutter1");
		experimentalShutter.createControls();
		experimentalShutter.setLabel("Experimental shutter");

		addButton(group, "oe thumb images/hrm_thumb.png", "HRM");
		addButton(group, "oe thumb images/diagnostic.png", "D8");
		addButton(group, "oe thumb images/diagnostic.png", "ATN5", HutchFilterView.ID);

		EnumPositionerGui photonShutter = new EnumPositionerGui(group, "photonshutter");
		photonShutter.createControls();
		photonShutter.setLabel("Photon shutter");

		addButton(group, "oe thumb images/diagnostic.png", "D9");
		addButton(group, "oe thumb images/xes_spectometer.png", "XES", XesStageView.ID);
		addButton(group, "oe thumb images/ss_thumb.png", "Sample stage", SampleStageView.ID);
	}
}
