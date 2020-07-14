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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.summary;

import java.util.Optional;
import java.util.function.Supplier;

import org.springframework.context.ApplicationListener;

import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionEvent;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;

class ScanningAcquisitionListener implements ApplicationListener<ScanningAcquisitionEvent> {

	private final ShapeSummaryBase summary;
	private final Supplier<ScanningAcquisition> acquisitionSupplier;

	public ScanningAcquisitionListener(ShapeSummaryBase summary, Supplier<ScanningAcquisition> acquisitionSupplier) {
		super();
		this.summary = summary;
		this.acquisitionSupplier = acquisitionSupplier;
	}

	@Override
	public void onApplicationEvent(ScanningAcquisitionEvent event) {
		Optional.ofNullable(acquisitionSupplier.get()).ifPresent(acquisition ->
			Optional.ofNullable(acquisitionSupplier.get()).map(ScanningAcquisition::getUuid).ifPresent(uuid -> {
				if (uuid.equals(ScanningAcquisition.class.cast(event.getSource()).getUuid())) {
					summary.printOut(summary.toString());
				}
			})
		);
	}
}
