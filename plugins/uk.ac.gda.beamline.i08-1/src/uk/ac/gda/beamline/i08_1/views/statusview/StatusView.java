/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i08_1.views.statusview;

import java.util.HashMap;
import java.util.Map;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.layout.RowLayoutFactory;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.swtdesigner.SWTResourceManager;

import gda.device.Scannable;
import gda.factory.Finder;
import uk.ac.gda.dls.client.views.ReadonlyScannableComposite;

public class StatusView extends ViewPart {
	private static final Logger logger = LoggerFactory.getLogger(StatusView.class);

	private static final String VIEW_NAME = "Status";

	private Map<String, Integer> colourMap;

	private String iconPlugin;
	private String iconFilePath;

	@Override
	public void createPartControl(Composite parent) {
		GridDataFactory.swtDefaults().applyTo(parent);
		RowLayoutFactory.swtDefaults().applyTo(parent);
		parent.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));

		setPartName(VIEW_NAME);
		setIcon();
		initialiseColourMap();

		final Group grpShutters = createGroup(parent, "Shutters", 2);
		createShutterComposite(grpShutters, "shutter2", "shutter2");
		createShutterComposite(grpShutters, "s3_shutter", "s3_shutter");

		final Group grpZonePlate = createGroup(parent, "Zone plate", 2);
		createNumericComposite(grpZonePlate, "ZonePlateZ", "ZonePlateZ", "mm", 2, 1000);
		createNumericComposite(grpZonePlate, "osa_z", "osa_z", "mm", 2, 1000);

		final Group grpEnergy = createGroup(parent, "Energy", 2);
		createNumericComposite(grpEnergy, "idgap", "idgap", "mm", 2, 1000);
		createNumericComposite(grpEnergy, "IDEnergy", "IDEnergy", "eV", 2, 1000);
		createNumericComposite(grpEnergy, "pgm_energy", "pgm_energy", "eV", 2, 1000);

		final Group grpPhase = createGroup(parent, "Phase", 2);
		createNumericComposite(grpPhase, "phase_upper", "phase_upper", "mm", 4, 1000);
		createNumericComposite(grpPhase, "phase_lower", "phase_lower", "mm", 4, 1000);
	}

	private void setIcon() {
		if (iconPlugin != null && iconFilePath != null) {
			try {
				final ImageDescriptor iconDescriptor = AbstractUIPlugin.imageDescriptorFromPlugin(iconPlugin, iconFilePath);
				setTitleImage(iconDescriptor.createImage());
			} catch (Exception e) {
			    logger.warn("Exception creating icon", e);
			}
		}
	}

	protected void initialiseColourMap() {
		colourMap = new HashMap<>(6);
		colourMap.put("Open", 6);
		colourMap.put("Opening", 6);
		colourMap.put("Closed", 3);
		colourMap.put("Closing", 3);
		colourMap.put("Reset", 8);
		colourMap.put("moving", 8);
	}

	protected static Group createGroup(Composite parent, String name, int columns) {
		final Group group = new Group(parent, SWT.NONE);
		group.setText(name);
		group.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		GridLayoutFactory.swtDefaults().numColumns(columns).applyTo(group);
		return group;
	}

	private void createShutterComposite(final Composite parent, final String scannableName, final String label) {
		final Scannable scannable = Finder.find(scannableName);
		final ReadonlyScannableComposite composite = new ReadonlyScannableComposite(parent, SWT.NONE, scannable, label, null, null);
		composite.setColourMap(colourMap);
	}

	private void createNumericComposite(final Composite parent, final String scannableName, final String label, final String units, final Integer decimalPlaces, final Integer minPeriodMS) {
		final Scannable scannable = Finder.find(scannableName);
		final ReadonlyScannableComposite composite = new ReadonlyScannableComposite(parent, SWT.NONE, scannable, label, units, decimalPlaces);
		composite.setMinPeriodMS(minPeriodMS);
	}

	@Override
	public void setFocus() {
		// nothing to do
	}

	public String getIconPlugin() {
		return iconPlugin;
	}

	public void setIconPlugin(String iconPlugin) {
		this.iconPlugin = iconPlugin;
	}

	public String getIconFilePath() {
		return iconFilePath;
	}

	public void setIconFilePath(String iconFilePath) {
		this.iconFilePath = iconFilePath;
	}
}
