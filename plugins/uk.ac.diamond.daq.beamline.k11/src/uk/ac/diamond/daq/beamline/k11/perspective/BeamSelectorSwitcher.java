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

package uk.ac.diamond.daq.beamline.k11.perspective;

import java.util.HashMap;
import java.util.Map;

import org.eclipse.scanning.event.util.SubmissionQueueUtils;
import org.eclipse.ui.IPerspectiveDescriptor;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PerspectiveAdapter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.factory.Finder;

/**
 * Perspective listener responsible for positioning the beam selector
 * to the position best suited to the active perspective
 */
public class BeamSelectorSwitcher extends PerspectiveAdapter {

	private static final Logger logger = LoggerFactory.getLogger(BeamSelectorSwitcher.class);

	private static final String MONO_IMAGING = "Mono imaging beam";

	private static final Map<String, String> POSITION_PER_PERSPECTIVE = new HashMap<>();

	private static final String BEAM_SELECTOR_SCANNABLE_PROPERTY = "beam.selector.scannable.name";
	private static final String BEAM_SELECTOR_SCANNABLE_DEFAULT_NAME = "beam_selector";

	private final Scannable beamSelector;

	public BeamSelectorSwitcher() {
		beamSelector = Finder.find(LocalProperties.get(BEAM_SELECTOR_SCANNABLE_PROPERTY, BEAM_SELECTOR_SCANNABLE_DEFAULT_NAME));
	}

	static {
		POSITION_PER_PERSPECTIVE.put(Tomography.ID, MONO_IMAGING);
		POSITION_PER_PERSPECTIVE.put(PointAndShoot.ID, MONO_IMAGING);
	}

	private void moveBeamSelector(String perspectiveId) {
		if (POSITION_PER_PERSPECTIVE.containsKey(perspectiveId)
				&& allowedToMove()) {
			try {
				beamSelector.moveTo(POSITION_PER_PERSPECTIVE.get(perspectiveId));
			} catch (DeviceException e) {
				logger.error("Could not move beam selector", e);
			}
		}
	}

	/** Tests can be added to this method as they arise */
	private boolean allowedToMove() {
		return !SubmissionQueueUtils.isJobRunningOrPending();
	}

	@Override
	public void perspectiveActivated(IWorkbenchPage page, IPerspectiveDescriptor perspective) {
		moveBeamSelector(perspective.getId());
	}

	@Override
	public void perspectiveOpened(IWorkbenchPage page, IPerspectiveDescriptor perspective) {
		// this method will ensure a consistent initial state
		// in the case where the active perspective when the listener is attached
		// is referenced in the map above
		moveBeamSelector(perspective.getId());
	}
}
