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
import uk.ac.gda.api.acquisition.AcquisitionTemplateType;
import uk.ac.gda.ui.tool.images.ClientImages;

public enum ShapeDescriptor {
	POINT(AcquisitionTemplateType.TWO_DIMENSION_POINT, ClientImages.POINT, new PointMappingRegion(), PointScanpathEditor::new),
	LINE(AcquisitionTemplateType.TWO_DIMENSION_LINE, ClientImages.LINE, new LineMappingRegion(), LineScanpathEditor::new),
	RECTANGLE(AcquisitionTemplateType.TWO_DIMENSION_GRID, ClientImages.CENTERED_RECTAGLE, new CentredRectangleMappingRegion(), RectangleScanpathEditor::new);

	private AcquisitionTemplateType shape;
	private ClientImages icon;
	private IMappingScanRegionShape mappingRegion;
	private Supplier<ScanpathEditor> editor;

	ShapeDescriptor(AcquisitionTemplateType shape, ClientImages icon, IMappingScanRegionShape mappingRegion, Supplier<ScanpathEditor> editor) {
		this.shape = shape;
		this.icon = icon;
		this.mappingRegion = mappingRegion;
		this.editor = editor;
	}

	public AcquisitionTemplateType shape() {
		return shape;
	}

	public ClientImages icon() {
		return icon;
	}

	public IMappingScanRegionShape mappingRegion() {
		return mappingRegion;
	}

	public Supplier<ScanpathEditor> editor() {
		return editor;
	}

}