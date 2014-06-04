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

package uk.ac.gda.plotting.model;

import org.dawnsci.plotting.api.trace.ILineTrace.PointStyle;
import org.dawnsci.plotting.api.trace.ILineTrace.TraceType;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;

public interface LineTraceProvider {

	public DoubleDataset getYAxisDataset();
	public DoubleDataset getXAxisDataset();

	public TraceStyleDetails getTraceStyleDetails();

	public boolean isPlotByDefault();

	public static class TraceStyleDetails {
		private String colorHexValue = null;
		private TraceType traceType;
		private PointStyle pointStyle;
		private int pointSize;

		public void setColorHexValue(String colorHexValue) {
			this.colorHexValue = colorHexValue;
		}

		public void setTraceType(TraceType traceType) {
			this.traceType = traceType;
		}

		public void setPointStyle(PointStyle pointStyle) {
			this.pointStyle = pointStyle;
		}

		public void setPointSize(int pointSize) {
			this.pointSize = pointSize;
		}

		public String getColorHexValue() {
			return colorHexValue;
		}

		public TraceType getTraceType() {
			return traceType;
		}

		public PointStyle getPointStyle() {
			return pointStyle;
		}

		public int getPointSize() {
			return pointSize;
		}
	}
}
