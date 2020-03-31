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

package uk.ac.gda.beamline.i14.views;

import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;

/**
 * {@link StatusView} for beamline staff, giving control over all shutters
 */
public class StatusViewStaff extends StatusView {

	@Override
	public void createPartControl(Composite parent) {
		super.createPartControl(parent);

		// OH1 shutter
		final Group grpOH1 = createGroup(parent, "OH1 Shutter", 1);
		createShutterComposite(grpOH1, "oh1_shutter_status");
		createCommandCompositeOpenClose(grpOH1, "OH1", "toggle_oh1_shtr()");

		// OH2 shutter
		final Group grpOH2 = createGroup(parent, "OH2 Shutter", 1);
		createShutterComposite(grpOH2, "oh2_shutter_status");
		createCommandCompositeOpenClose(grpOH2, "OH2", "toggle_oh2_shtr()");

		// OH3 shutter
		final Group grpOH3 = createGroup(parent, "OH3 Shutter", 1);
		createShutterComposite(grpOH3, "oh3_shutter_status");
		createCommandCompositeOpenClose(grpOH3, "OH3", "toggle_oh3_shtr()");

		// EH2 Nano shutter
		final Group grpEH2Nano = createGroup(parent, "EH2 Nano Shutter", 1);
		createShutterComposite(grpEH2Nano, "eh2_nano_shutter_status");
		createCommandCompositeOpenClose(grpEH2Nano, "EH2 Nano", "toggle_eh2_nano_shtr()");

		// State of processing
		final Group grpProcessing = createGroup(parent, "Processing", 1);
		createNumericCompositeForProcessing(grpProcessing, "processing_monitor", "Processing");
	}

}
