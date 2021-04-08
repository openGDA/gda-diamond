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

package uk.ac.gda.beamline.i08.shared.views.statusview;

import java.util.Map;

import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.layout.RowLayoutFactory;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.slf4j.Logger;

import com.swtdesigner.SWTResourceManager;

import gda.device.Scannable;
import gda.factory.Finder;
import uk.ac.gda.dls.client.views.ReadonlyScannableComposite;

/**
 * Code common to the I08 & I08-1 StatusView
 */
public abstract class AbstractStatusView extends ViewPart {
	private static final Logger logger = org.slf4j.LoggerFactory.getLogger(AbstractStatusView.class);

	private static final String VIEW_NAME = "Status";

	private static final Map<String, Integer> COLOUR_MAP = Map.of("Open", 6, "Opening", 6, "Closed", 3, "Closing", 3, "Reset", 8);

	private String iconPlugin;
	private String iconFilePath;

	@Override
	public void createPartControl(Composite parent) {
		parent.setLayout(new FillLayout());
		parent.setBackground(Display.getDefault().getSystemColor(SWT.COLOR_WHITE));
		parent.setBackgroundMode(SWT.INHERIT_FORCE);

		final ScrolledComposite scrolledComposite = new ScrolledComposite(parent, SWT.H_SCROLL | SWT.V_SCROLL);
		scrolledComposite.setLayout(new FillLayout());
		scrolledComposite.setExpandHorizontal(true);
		scrolledComposite.setExpandVertical(true);

		final Composite content = new Composite(scrolledComposite, SWT.NONE);
		RowLayoutFactory.swtDefaults().applyTo(content);

		setPartName(VIEW_NAME);
		setIcon();

		createViewContent(content);

		scrolledComposite.setContent(content);
		scrolledComposite.setMinSize(content.computeSize(80, SWT.DEFAULT));
	}

	/**
	 * Create beamline specific content
	 *
	 * @param contentComposite
	 *            parent composite for the content
	 */
	protected abstract void createViewContent(Composite contentComposite);

	protected void createEnergyGroup(Composite parent) {
		final Group grpEnergy = createGroup(parent, "Energy", 2);
		createNumericComposite(grpEnergy, "idgap", "idgap", "mm", 2, 1000);
		createNumericComposite(grpEnergy, "IDEnergy", "IDEnergy", "eV", 2, 1000);
		createNumericComposite(grpEnergy, "pgm_energy", "pgm_energy", "eV", 2, 1000);
	}

	protected void createPhaseGroup(Composite parent) {
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

	protected static Group createGroup(Composite parent, String name, int columns) {
		final Group group = new Group(parent, SWT.NONE);
		group.setText(name);
		group.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		GridLayoutFactory.swtDefaults().numColumns(columns).applyTo(group);
		return group;
	}

	protected void createShutterComposite(final Composite parent, final String scannableName, final String label) {
		final Scannable scannable = Finder.find(scannableName);
		final ReadonlyScannableComposite composite = new ReadonlyScannableComposite(parent, SWT.NONE, scannable, label, null, null);
		composite.setColourMap(COLOUR_MAP);
	}

	protected void createNumericComposite(final Composite parent, final String scannableName, final String label, final String units, final Integer decimalPlaces, final Integer minPeriodMS) {
		final Scannable scannable = Finder.find(scannableName);
		final ReadonlyScannableComposite composite = new ReadonlyScannableComposite(parent, SWT.NONE, scannable, label, units, decimalPlaces);
		composite.setMinPeriodMS(minPeriodMS);
	}

	@Override
	public void setFocus() {
		// nothing to do
	}

	public void setIconPlugin(String iconPlugin) {
		this.iconPlugin = iconPlugin;
	}

	public void setIconFilePath(String iconFilePath) {
		this.iconFilePath = iconFilePath;
	}
}
