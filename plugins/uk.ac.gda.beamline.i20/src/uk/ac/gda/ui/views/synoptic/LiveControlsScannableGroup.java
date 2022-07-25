/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Composite;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.swtdesigner.SWTResourceManager;

import gda.device.scannable.scannablegroup.IScannableGroup;
import gda.factory.FactoryException;
import gda.factory.Finder;
import uk.ac.gda.client.livecontrol.LiveControl;
import uk.ac.gda.client.livecontrol.LiveControlGroup;
import uk.ac.gda.client.livecontrol.ScannablePositionerControl;


public class LiveControlsScannableGroup extends LiveControlGroup {

	private static final Logger logger = LoggerFactory.getLogger(LiveControlsScannableGroup.class);

	private IScannableGroup scannableGroup;
	private int displayNameWidth = 0;
	private boolean horizontalLayout = false;
	private int incrementTextWidth = 30;
	private boolean showStop = true;
	private boolean readOnly = false;
	private boolean showIncrement = true;
	private int widgetWidth = SWT.DEFAULT;

	// For setting the description of each widget in the group
	private List<String> descriptions = Collections.emptyList();

	// For setting the read only property of each widget in the group
	private List<Boolean> readOnlyList = Collections.emptyList();

	public void setScannableGroupName(String name) throws FactoryException {
		IScannableGroup scnGroup = Finder.findOptionalOfType(name, IScannableGroup.class)
									.orElseThrow(() -> new FactoryException("Could not find scannable called "+name));
		setScannableGroup(scnGroup);
	}

	public void setScannableGroup(IScannableGroup crystalScannableGroup) {
		logger.info("Setting scannable group to : {}", crystalScannableGroup.getName());
		scannableGroup = crystalScannableGroup;
	}

	@Override
	public void createControl(Composite composite) {
		composite.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		composite.setBackgroundMode(SWT.INHERIT_FORCE);

		// Create LiveControl object for each scannable in the group
		List<LiveControl> liveControls = new ArrayList<>();
		for(String name : scannableGroup.getGroupMemberNames()) {
			int itemIndex = liveControls.size();
			Boolean isReadOnlyFromList = null;
			if (!readOnlyList.isEmpty()) {
				int size = readOnlyList.size();
				isReadOnlyFromList = readOnlyList.get(itemIndex%size);
			}

			// set the display name from the description
			String description = null;
			if (!descriptions.isEmpty()) {
				description = descriptions.get(itemIndex%descriptions.size());
			}

			var control = new ScannablePositionerControl();
			control.setScannableName(name);
			control.setDisplayName(name);
			control.setDisplayNameWidth(displayNameWidth);
			control.setIncrementTextWidth(incrementTextWidth);
			control.setHorizontalLayout(horizontalLayout);
			control.setShowStop(showStop);
			if (readOnly || Boolean.TRUE.equals(isReadOnlyFromList)) {
				control.setReadOnly(true);
			}
			control.setShowIncrement(showIncrement);
			if (description != null) {
				control.setDisplayName(description);
			}


			liveControls.add(control);
		}
		setControls(liveControls);

		// Make new composite for all the widgets to go into
		final Composite container = new Composite(composite, SWT.NONE);
		if (widgetWidth > 0 && !(composite.getLayout() instanceof RowLayout)) {
			GridDataFactory.fillDefaults().hint(widgetWidth, SWT.DEFAULT).applyTo(container);
		} else {
			container.setLayout(new FillLayout());
		}
		super.createControl(container);
	}

	public Boolean getShowIncrement() {
		return showIncrement;
	}

	public void setShowIncrement(Boolean showIncrement) {
		this.showIncrement = showIncrement;
	}

	public boolean isReadOnly() {
		return readOnly;
	}

	public void setReadOnly(boolean readOnly) {
		this.readOnly = readOnly;
	}

	public void setReadOnlyList(List<Boolean> readOnly) {
		this.readOnlyList = new ArrayList<>(readOnly);
	}

	public void setDisplayNameWidth(int displayNameWidth) {
		this.displayNameWidth = displayNameWidth;
	}

	public void setWidgetWidth(int widgetWidth) {
		this.widgetWidth = widgetWidth;
	}

	public void setHorizontalLayout(boolean horizontalLayout) {
		this.horizontalLayout = horizontalLayout;
	}

	public void setIncrementTextWidth(int incrementTextWidth) {
		this.incrementTextWidth = incrementTextWidth;
	}

	public void setShowStop(boolean showStop) {
		this.showStop = showStop;
	}

	/**
	 * Set the description for each widget in the group.
	 * <li> If empty, the scannable name will be used.
	 * <li> If there are fewer descriptions than scannables,
	 * the description indices will 'wrap around'.
	 * i.e. description index = widget index % num descriptions
	 * @param descriptions
	 */
	public void setDescriptions(List<String> descriptions) {
		this.descriptions = new ArrayList<>(descriptions);
	}
}
