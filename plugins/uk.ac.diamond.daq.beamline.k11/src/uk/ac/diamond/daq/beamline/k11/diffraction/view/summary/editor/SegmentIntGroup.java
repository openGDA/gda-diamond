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
 * Basic implementation of the {@link SegmentGroup} interface for a {@code int[]} structure
 *
 * @author Maurizio Nagni
 */
public class SegmentIntGroup extends GenericSegmentGroup<int[]> {
	public SegmentIntGroup(Consumer<int[]> setter, boolean editable) {
		super(setter, ClientTextFormats.integerFormat, editable);
	}

	@Override
	public int[] getValues() {
		return getSegments().stream()
				.mapToInt(s -> (int) s.getNumericValue())
				.toArray();
	}
}
