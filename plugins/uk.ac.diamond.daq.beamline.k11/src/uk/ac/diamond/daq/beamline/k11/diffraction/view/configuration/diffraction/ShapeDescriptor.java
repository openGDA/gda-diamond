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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction;

import java.util.function.Supplier;

import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.gda.api.acquisition.TrajectoryShape;
import uk.ac.gda.ui.tool.images.ClientImages;

public interface ShapeDescriptor {

	TrajectoryShape shape();

	ClientImages icon();

	IMappingScanRegionShape mappingRegion();

	Supplier<ScanpathEditor> editor();
}
