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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.mutator;

import org.apache.commons.lang3.tuple.ImmutablePair;
import org.eclipse.core.databinding.conversion.IConverter;
import org.eclipse.swt.widgets.Button;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.mapping.ui.diffraction.model.MutatorType;
import uk.ac.diamond.daq.mapping.ui.diffraction.model.ShapeType;

/**
 * Abstracts a {@link MutatorType} GUI element.
 *
 * @author Maurizio Nagni
 */
interface MutatorComposite extends CompositeFactory {

	/**
	 * Maps the {@link MutatorType} to the GUI elements
	 *
	 * @return an immutable pair
	 */
	public ImmutablePair<MutatorType, Button> getMutatorDefinition();

	/**
	 * An {@link IConverter} which map a {@link ShapeType} to a {@code boolean} which returns {@code true} if the mutator is
	 * permitted for the given {@link ShapeType}, {@code false} otherwise.
	 *
	 * @return the {@link MutatorComposite} converter
	 */
	public IConverter filterShape();

}
