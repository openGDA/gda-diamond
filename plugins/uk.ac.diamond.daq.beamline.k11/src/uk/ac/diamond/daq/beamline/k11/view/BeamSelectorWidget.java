/*-
 * Copyright © 2022 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.view;

import static uk.ac.gda.ui.tool.ClientSWTElements.STRETCH;
import static uk.ac.gda.ui.tool.ClientSWTElements.composite;
import static uk.ac.gda.ui.tool.ClientSWTElements.label;

import java.util.List;

import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Text;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.EnumPositionerStatus;
import gda.factory.Finder;
import gda.observable.IObserver;

/**
 * Controls beam selector using a reduced, user-friendly positioner to set position,
 * and a full positioner to readback e.g. user selects Imaging and readback will
 * show 'Mono imaging beam'.
 */
public class BeamSelectorWidget {

	private static final Logger logger = LoggerFactory.getLogger(BeamSelectorWidget.class);

	private EnumPositioner beamSelector;
	private EnumPositioner beamSelectorReadback;

	private Text readBack;

	/**
	 * @param beamSelectorName user-friendly positioner with reduced positions
	 * @param beamSelectorReadbackName full positioner for full readback
	 */
	public BeamSelectorWidget(String beamSelectorName, String beamSelectorReadbackName) {
		beamSelector = Finder.find(beamSelectorName);
		beamSelectorReadback = Finder.find(beamSelectorReadbackName);
	}

	public Control createControls(Composite parent) {
		var composite = composite(parent, 1);

		label(composite, "Beam selector");

		var combo = new Combo(composite, SWT.DROP_DOWN | SWT.READ_ONLY);
		STRETCH.applyTo(combo);

		readBack = new Text(composite, SWT.READ_ONLY | SWT.BORDER);
		readBack.setEnabled(false); // visual hint that this is readback only
		STRETCH.applyTo(readBack);

		try {
			var positions = beamSelector.getPositions();
			combo.setItems(positions);
		} catch (DeviceException e) {
			logger.error("Error reading beam selector positions", e);
		}

		combo.addListener(SWT.Selection, event -> {
			try {
				beamSelector.asynchronousMoveTo(combo.getItem(combo.getSelectionIndex()));
			} catch (DeviceException e) {
				logger.error("Error moving beam selector", e);
			}
		});

		IObserver readBackListener = (source, argument) -> {
			if (argument == EnumPositionerStatus.IDLE) {
				// only updates when move complete
				updateReadbackLabel();
			}
		};

		beamSelectorReadback.addIObserver(readBackListener);
		readBack.addDisposeListener(dispose -> beamSelectorReadback.deleteIObserver(readBackListener));

		// initialise manually
		updateReadbackLabel();

		try {
			var position = beamSelector.getPosition().toString();
			combo.select(List.of(combo.getItems()).indexOf(position));
		} catch (DeviceException e) {
			logger.error("Error reading beam selector position", e);
		}

		return composite;
	}

	private void updateReadbackLabel() {
		try {
			final String position = beamSelectorReadback.getPosition().toString();
			Display.getDefault().syncExec(() -> readBack.setText(position));
		} catch (DeviceException e) {
			logger.error("Error reading beam selector position", e);
		}
	}


}
