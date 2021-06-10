/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.summary.editor;

import java.util.function.Consumer;

import uk.ac.gda.ui.tool.ClientTextFormats;

/**
 * Basic implementation of the {@link SegmentGroup} interface for a {@code double[]} structure
 *
 * @author Maurizio Nagni
 */
public class SegmentDoubleGroup extends GenericSegmentGroup<double[]> {
	public SegmentDoubleGroup(Consumer<double[]> setter, boolean editable) {
		super(setter, ClientTextFormats.decimalFormat, editable);
	}

	@Override
	public double[] getValues() {
		return getSegments().stream()
				.mapToDouble(Segment::getNumericValue)
				.toArray();
	}
}
