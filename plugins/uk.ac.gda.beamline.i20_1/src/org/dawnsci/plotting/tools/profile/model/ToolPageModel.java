/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package org.dawnsci.plotting.tools.profile.model;

import java.io.File;

import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.dawnsci.plotting.api.trace.IImageTrace;
import org.eclipse.january.dataset.IDataset;

import uk.ac.gda.beans.ObservableModel;

public class ToolPageModel extends ObservableModel {
	private TimeResolvedDataNode timeResolvedData;
	private File dataFile;
	private IDataset energy;
	private IPlottingSystem dataImagePlotting;
	private IPlottingSystem spectraPlotting;
	private IImageTrace imageTrace;
	private int[] cyclesInfo;

	private static final double DEFAULT_STACK_OFFSET = 0.1;

	public static final String TRACE_STACK_PROP_NAME = "traceStack";
	private double traceStack = DEFAULT_STACK_OFFSET;

	public TimeResolvedDataNode getTimeResolvedData() {
		return timeResolvedData;
	}
	public void setTimeResolvedData(TimeResolvedDataNode timeResolvedData) {
		this.timeResolvedData = timeResolvedData;
	}
	public File getDataFile() {
		return dataFile;
	}
	public void setDataFile(File dataFile) {
		this.dataFile = dataFile;
	}
	public IDataset getEnergy() {
		return energy;
	}
	public void setEnergy(IDataset energy) {
		this.energy = energy;
	}
	public IPlottingSystem getDataImagePlotting() {
		return dataImagePlotting;
	}
	public void setDataImagePlotting(IPlottingSystem dataImagePlotting) {
		this.dataImagePlotting = dataImagePlotting;
	}
	public IPlottingSystem getSpectraPlotting() {
		return spectraPlotting;
	}
	public void setSpectraPlotting(IPlottingSystem spectraPlotting) {
		this.spectraPlotting = spectraPlotting;
	}

	public double getTraceStack() {
		return traceStack;
	}

	public void setTraceStack(double traceStack) {
		firePropertyChange(TRACE_STACK_PROP_NAME, this.traceStack, this.traceStack = traceStack);
	}
	public int[] getCyclesInfo() {
		return cyclesInfo;
	}
	public void setCyclesInfo(int[] cyclesInfo) {
		this.cyclesInfo = cyclesInfo;
	}

	public IImageTrace getImageTrace() {
		return imageTrace;
	}
	public void setImageTrace(IImageTrace imageTrace) {
		this.imageTrace = imageTrace;
	}
}