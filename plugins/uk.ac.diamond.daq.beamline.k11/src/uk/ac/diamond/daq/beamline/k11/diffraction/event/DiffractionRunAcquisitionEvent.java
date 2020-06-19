/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.event;

import uk.ac.diamond.daq.beamline.k11.diffraction.service.DiffractionService;
import uk.ac.diamond.daq.beamline.k11.diffraction.service.message.DiffractionRunMessage;

/**
 * Notifies to a listener, most commonly a {@link DiffractionService}, a request to run an acquisition as defined in the
 * {@cod runMessage}.
 *
 * @author Maurizio Nagni
 */
public class DiffractionRunAcquisitionEvent extends DiffractionEvent {
	private final DiffractionRunMessage runMessage;

	public DiffractionRunAcquisitionEvent(Object source, DiffractionRunMessage runMessage) {
		super(source);
		this.runMessage = runMessage;
	}

	public DiffractionRunMessage getRunDiffractionMessage() {
		return runMessage;
	}
}
