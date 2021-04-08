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

package uk.ac.gda.beamline.i08.views.statusview;

import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;

import uk.ac.gda.beamline.i08.shared.views.statusview.AbstractStatusView;

public class StatusView extends AbstractStatusView {

	@Override
	protected void createViewContent(Composite contentComposite) {

		final Group grpShutters = createGroup(contentComposite, "Shutters", 2);
		createShutterComposite(grpShutters, "shutter1", "shutter1");

		final Group grpZonePlate = createGroup(contentComposite, "Zone plate", 2);
		createNumericComposite(grpZonePlate, "ZonePlateZ", "ZonePlateZ", "mm", 2, 1000);

		createEnergyGroup(contentComposite);
		createPhaseGroup(contentComposite);
	}
}
