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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.shape;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.TemplateHelperBase;
import uk.ac.diamond.daq.mapping.ui.diffraction.base.DiffractionParameters;
import uk.ac.diamond.daq.mapping.ui.diffraction.model.ShapeType;

public class ShapeTemplateDataHelper extends TemplateHelperBase {

	public ShapeTemplateDataHelper(DiffractionParameters templateData) {
		super(templateData);
	}

	public void update(ShapeType shapeType) {
		updateTemplate(getBuilder().withModelDocument(shapeType.getAcquisitionTemplateType()));

		getTemplateData().setShapeType(shapeType);
		if (getLogger().isDebugEnabled()) {
			getLogger().debug(getTemplateData().toString());
		}
	}
}
