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

import org.eclipse.core.databinding.conversion.IConverter;
import org.eclipse.swt.events.SelectionListener;

import uk.ac.diamond.daq.mapping.ui.diffraction.model.MutatorType;
import uk.ac.diamond.daq.mapping.ui.diffraction.model.ShapeType;
import uk.ac.gda.ui.tool.ClientMessages;

/**
 * A GUI representation of the {@link MutatorType#RANDOM} mutator
 *
 * @author Maurizio Nagni
 */
class RandomMutator extends MutatorCompositeBase {

	private final IConverter converter = IConverter.create(ShapeType.class, Boolean.class,
			shape -> !((ShapeType) shape).equals(ShapeType.POINT));

	public RandomMutator(SelectionListener mutatorListener) {
		super(MutatorType.RANDOM, ClientMessages.RANDOM_MUTATOR, ClientMessages.RANDOM_MUTATOR_TP, mutatorListener);
	}

	@Override
	public IConverter filterShape() {
		return converter;
	}

}
