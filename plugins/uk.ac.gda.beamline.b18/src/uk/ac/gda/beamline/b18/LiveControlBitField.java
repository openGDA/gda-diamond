/*-
 * Copyright © 2023 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.b18;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.swtdesigner.SWTResourceManager;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableUtils;
import gda.factory.Finder;
import uk.ac.gda.client.livecontrol.LiveControlBase;

public class LiveControlBitField extends LiveControlBase {

	private static final Logger logger = LoggerFactory.getLogger(LiveControlBitField.class);

	private String scannableName = "";
	private int numBits = 1;
	private List<String> bitFieldValues = Collections.emptyList();

	private Scannable scannable;
	private List<Control> bitFieldButtons = Collections.emptyList();

	private Color activeColour = Display.getDefault().getSystemColor(SWT.COLOR_GREEN);
	private Color inactiveColour = Display.getDefault().getSystemColor(SWT.COLOR_DARK_GREEN);
	private Map<Integer,Integer> bitColours = new HashMap<>();

	@Override
	public void createControl(Composite composite) {
		scannable = Finder.findOptionalOfType(scannableName, Scannable.class).orElse(null);
		if (scannable!=null) {
			addControls(composite);
			updateCheckBoxes(scannable, null);
			logger.warn("No bit field strings have been set and number of bits is set to zero - can't create live controls for {}", scannableName);

		} else {
			logger.warn("Could not get scannable '{}' for live control", scannableName);
		}
	}

	private void addControls(Composite parent) {

		parent.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		parent.setBackgroundMode(SWT.INHERIT_FORCE);

		int numBitsToDisplay = bitFieldValues.isEmpty() ? numBits : bitFieldValues.size();
		logger.info("Adding bit field live control for {}. NUmber of bits = {}", scannableName, numBitsToDisplay);
		bitFieldButtons = new ArrayList<>();
		for(int i=0; i<numBitsToDisplay; i++) {
			Composite c = new Composite(parent, SWT.NONE);
			c.setLayout(new GridLayout(2,false));
			Label colourLabel = new Label(c, SWT.NONE);
			colourLabel.setText("OO");
			bitFieldButtons.add(colourLabel);

			if (bitFieldValues.size() > i) {
				Label textLabel = new Label(c, SWT.NONE);
				textLabel.setText(bitFieldValues.get(i));
			}
		}
		scannable.addIObserver(this::updateCheckBoxes);
	}

	private int getNumericValue(Scannable scn) {
		try {
			return ScannableUtils.objectToDouble(scn.getPosition()).intValue();
		} catch (DeviceException e) {
			logger.error("Problem getting numeric value from {}. Using 0 instead.", scn, e);
		}
		return 0;
	}

	private void setBitState(int bit, boolean isSet) {
		Color col = isSet ? activeColour : inactiveColour;
		if (bitColours.containsKey(bit)) {
			int colorCode = bitColours.get(bit);
			if (!isSet) {
				colorCode++;
			}
			col = Display.getDefault().getSystemColor(colorCode);
		}
		bitFieldButtons.get(bit).setBackground(col);
		bitFieldButtons.get(bit).setForeground(col);

	}

	private void updateCheckBoxes(Object source, Object arg) {
		if (source != scannable) {
			return;
		}
		int value = getNumericValue(scannable);
		logger.debug("Update checkbox states : bit field value = {} ({})", value, Integer.toString(value,2));
		for(int bit=0; bit<bitFieldButtons.size(); bit++) {
			boolean bitIsSet =  (value & (int)Math.pow(2, bit)) > 0;
			logger.debug("{} = {}", bitFieldValues.get(bit), bitIsSet);
			Integer bitToSet = bit;
			Display.getDefault().asyncExec(() -> setBitState(bitToSet, bitIsSet));
		}
	}

	@Override
	public void dispose() {
		scannable.deleteIObserver(this::updateCheckBoxes);
	}

	public void setScannableName(String scannableName) {
		this.scannableName = scannableName;
	}

	public void setBitFieldValues(List<String> bitFieldValues) {
		this.bitFieldValues = bitFieldValues;
	}

	public void setNumBits(int numBits) {
		this.numBits = numBits;
	}

	public void setBitColours(Map<Integer, Integer> bitColours) {
		this.bitColours = bitColours;
	}

}
