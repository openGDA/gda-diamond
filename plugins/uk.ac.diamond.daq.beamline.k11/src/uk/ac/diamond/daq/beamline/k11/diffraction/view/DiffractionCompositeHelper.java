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

package uk.ac.diamond.daq.beamline.k11.diffraction.view;

import java.util.Arrays;
import java.util.Optional;

import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.conversion.IConverter;
import org.eclipse.scanning.api.points.models.IScanPathModel;
import org.eclipse.scanning.api.points.models.TwoAxisGridPointsRandomOffsetModel;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.shape.AcquisitionTemplateTypeCompositeFactory;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;

/**
 * Contains methods and function to support the DiffractionConfigurationCompositeFactory family
 * @author Maurizio Nagni
 */
public class DiffractionCompositeHelper {

	private DiffractionCompositeHelper() {
	}

	public static final UpdateValueStrategy POLICY_NEVER = new UpdateValueStrategy(false,
			UpdateValueStrategy.POLICY_NEVER);
	public static final UpdateValueStrategy POLICY_UPDATE = new UpdateValueStrategy(false,
			UpdateValueStrategy.POLICY_UPDATE);
	public static final IConverter<IMappingScanRegionShape, AcquisitionTemplateType> mappingRegionShapeToShape = IConverter.create(IMappingScanRegionShape.class,
			AcquisitionTemplateType.class,
			mappingRegion -> acquisitionTypeFromMappingRegion(mappingRegion).orElse(null));

	public static final Optional<AcquisitionTemplateType> acquisitionTypeFromMappingRegion(IMappingScanRegionShape mappingRegion) {
		if (mappingRegion == null)
			return Optional.empty();
		return Arrays.stream(AcquisitionTemplateType.values()).filter(sh ->
			AcquisitionTemplateTypeCompositeFactory.filterRegionScan(sh)
				.test(mappingRegion))
				.findFirst();
	}

	public static final IConverter<IScanPathModel, Boolean> scanPathToRandomised = IConverter.create(IScanPathModel.class, Boolean.class,
			scanPathModel -> scanPathModel.getClass().equals(TwoAxisGridPointsRandomOffsetModel.class));

	public static final IConverter<Integer, String> integerToString = IConverter.create(Integer.class, String.class, String::valueOf);
	public static final IConverter<String, Integer> stringToInteger = IConverter.create(String.class, Integer.class,
			Integer::valueOf);
}