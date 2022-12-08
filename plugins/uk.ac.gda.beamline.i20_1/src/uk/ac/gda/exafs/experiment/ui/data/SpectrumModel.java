/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.experiment.ui.data;


public class SpectrumModel extends TimeIntervalDataModel {

	private final TimingGroupUIModel parent;
	private final int fromSpectrum;
	private final int toSpectrum;

	public SpectrumModel(TimingGroupUIModel parent, int fromSpectrum, int toSpectrum) {
		this.parent = parent;
		this.fromSpectrum = fromSpectrum;
		this.toSpectrum = toSpectrum;
	}

	public TimingGroupUIModel getParent() {
		return parent;
	}

	@Override
	public void dispose() {
		//
	}

	public int getFromSpectrum() {
		return fromSpectrum;
	}

	public int getToSpectrum() {
		return toSpectrum;
	}

}
