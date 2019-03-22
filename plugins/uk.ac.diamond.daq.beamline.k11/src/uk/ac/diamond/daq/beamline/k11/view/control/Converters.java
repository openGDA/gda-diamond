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

package uk.ac.diamond.daq.beamline.k11.view.control;

import java.util.List;

import org.eclipse.core.databinding.conversion.IConverter;
import org.eclipse.scanning.api.points.models.IScanPathModel;
import org.eclipse.scanning.api.points.models.RandomOffsetGridModel;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.widgets.Display;

import uk.ac.diamond.daq.beamline.k11.view.control.PathSummary.Shape;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;

/**
 * A set of {@link IConverter}s used by the {@link DiffractionPathComposite}
 *
 * @since GDA 9.13
 */
class Converters {

	private final RegionAndPathController controller;
	private final Display currentDisplay = Display.getCurrent();
	private final Color armedColor;

	public Converters(final RegionAndPathController controller, final Color armedColor) {
		this.controller = controller;
		this.armedColor = armedColor;
	}

	IConverter hideControlForPoint = IConverter.create(Shape.class, Boolean.class,
			shape -> !((Shape)shape).equals(Shape.POINT));

	IConverter hideControlForPointOrLine = IConverter.create(Shape.class, Boolean.class,
			shape -> ((Shape)shape).equals(Shape.CENTRED_RECTANGLE));

	IConverter shapeToMappingRegionShape = IConverter.create(Shape.class, IMappingScanRegionShape.class,
			shape -> {return regionShapeForName(((Shape)shape).getMappingScanRegionName());
			});

	IConverter mappingRegionShapeToShape = IConverter.create(IMappingScanRegionShape.class, Shape.class,
			mappingRegionShape -> Shape.fromMappingScanRegion((IMappingScanRegionShape)mappingRegionShape));

	IConverter scanPathToRandomised = IConverter.create(IScanPathModel.class, Boolean.class,
			scanPathModel -> scanPathModel.getClass().equals(RandomOffsetGridModel.class));

	IConverter stringToInteger = IConverter.create(String.class, Integer.class,
			string -> Integer.valueOf((String)string));

	IConverter integerToString = IConverter.create(Integer.class, String.class, String::valueOf);

	IConverter armedStatusToTextTitleText = IConverter.create(Boolean.class, String.class,
			isArmed -> ((Boolean)isArmed) ? "ARMED: Use Ctrl-Click to start a Scan" : " ");

	IConverter armedStatusToTextColour = IConverter.create(Boolean.class, Color.class,
			isArmed -> ((Boolean)isArmed) ? getColour(SWT.COLOR_DARK_RED) : getColour(SWT.COLOR_BLACK));

	IConverter armedStatusToBackgroundColour = IConverter.create(Boolean.class, Color.class,
			isArmed -> ((Boolean)isArmed) ? getArmedColor() : getColour(SWT.COLOR_WHITE));

	/**
	 *  Converts the supplied name of a {@link IMappingScanRegionShape} to the corresponding object using the region
	 *  templates set up in the Spring config. It copes with names that have had underscores added (for filename use).
	 *  If an unknown name is supplied the default (first in the list) is returned
	 *
	 * @param regionShapeName	The name of the required region
	 * @return					The corresponding region or the default of the name is unrecognised.
	 */
	IMappingScanRegionShape regionShapeForName(final String regionShapeName) {
		final String standardisedShapeName = regionShapeName.replace('_', ' ');
		List<IMappingScanRegionShape> regions = getController().getTemplateRegions();
		return regions.stream().filter(region ->
					standardisedShapeName.equalsIgnoreCase(region.getName())).findFirst().orElse(regions.get(0));
	}

	private Color getColour(int colourId) {
		return currentDisplay.getSystemColor(colourId);
	}

	private Color getArmedColor() {
		return armedColor;
	}

	private RegionAndPathController getController() {
		return controller;
	}

}
