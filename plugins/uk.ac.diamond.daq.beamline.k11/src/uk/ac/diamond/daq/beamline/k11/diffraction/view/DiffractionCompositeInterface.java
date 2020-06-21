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

import org.eclipse.scanning.api.points.models.IScanPointGeneratorModel;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.mapping.api.document.diffraction.ShapeType;

/**
 * Defines the operations supported by a {@link DiffractionConfigurationCompositeFactory} component
 * @author Maurizio Nagni
 */
public interface DiffractionCompositeInterface extends CompositeFactory {

	/**
	 * At the creation of the component, binds the gui elements to the underlying models
	 */
	public void bindControls();

	/**
	 * Updates the binding after a GUI event
	 * @param scanPointmodel the mapping scan point generator model
	 * @param shapeType the mapping selected shape
	 */
	public void updateScanPointBindings(final IScanPointGeneratorModel scanPointmodel, ShapeType shapeType);
}
