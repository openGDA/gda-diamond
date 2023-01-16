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
import uk.ac.diamond.daq.mapping.region.CentredRectangleMappingRegion;
import uk.ac.diamond.daq.mapping.region.LineMappingRegion;
import uk.ac.diamond.daq.mapping.region.PointMappingRegion;
import uk.ac.gda.api.acquisition.TrajectoryShape;
import uk.ac.gda.ui.tool.images.ClientImages;

public enum DiffractionShapeDescriptor implements ShapeDescriptor {
	POINT(TrajectoryShape.TWO_DIMENSION_POINT, ClientImages.POINT, new PointMappingRegion(), PointScanpathEditor::new),
	LINE(TrajectoryShape.TWO_DIMENSION_LINE, ClientImages.LINE, new LineMappingRegion(), LineScanpathEditor::new),
	RECTANGLE(TrajectoryShape.TWO_DIMENSION_GRID, ClientImages.CENTERED_RECTAGLE, new CentredRectangleMappingRegion(), RectangleScanpathEditor::new);

	private TrajectoryShape shape;
	private ClientImages icon;
	private IMappingScanRegionShape mappingRegion;
	private Supplier<ScanpathEditor> editor;

	DiffractionShapeDescriptor(TrajectoryShape shape, ClientImages icon, IMappingScanRegionShape mappingRegion, Supplier<ScanpathEditor> editor) {
		this.shape = shape;
		this.icon = icon;
		this.mappingRegion = mappingRegion;
		this.editor = editor;
	}

	@Override
	public TrajectoryShape shape() {
		return shape;
	}

	@Override
	public ClientImages icon() {
		return icon;
	}

	@Override
	public IMappingScanRegionShape mappingRegion() {
		return mappingRegion;
	}

	@Override
	public Supplier<ScanpathEditor> editor() {
		return editor;
	}

}
