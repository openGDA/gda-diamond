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

import uk.ac.diamond.daq.mapping.ui.properties.stages.ManagedScannable;
import uk.ac.diamond.daq.mapping.ui.properties.stages.ScannablesPropertiesHelper;
import uk.ac.gda.client.exception.GDAClientException;

/**
 * Perspective listener responsible for positioning the beam selector
 * to the position best suited to the active perspective
 */
public class BeamSelectorSwitcher extends PerspectiveAdapter {

	private static final Logger logger = LoggerFactory.getLogger(BeamSelectorSwitcher.class);

	private static final Map<String, String> POSITION_PER_PERSPECTIVE = new HashMap<>();

	private static final String BEAM_SELECTOR_GROUP_ID = "beam_selector";
	private static final String BEAM_SELECTOR_SCANNABLE_ID = "selector";
	private static final String BEAM_SELECTOR_MONO_IMAGING_POSITON = "MONO";

	private ManagedScannable<String> managedBeamSelector;

	public BeamSelectorSwitcher() {
		managedBeamSelector = ScannablesPropertiesHelper.getManagedScannable(BEAM_SELECTOR_GROUP_ID, BEAM_SELECTOR_SCANNABLE_ID, String.class);
	}

	static {
		POSITION_PER_PERSPECTIVE.put(Tomography.ID, BEAM_SELECTOR_MONO_IMAGING_POSITON);
		POSITION_PER_PERSPECTIVE.put(PointAndShoot.ID, BEAM_SELECTOR_MONO_IMAGING_POSITON);
	}

	private void moveBeamSelector(String perspectiveId) {
		if (POSITION_PER_PERSPECTIVE.containsKey(perspectiveId)
				&& allowedToMove()) {
				try {
					managedBeamSelector.moveTo(POSITION_PER_PERSPECTIVE.get(perspectiveId));
				} catch (GDAClientException e) {
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
