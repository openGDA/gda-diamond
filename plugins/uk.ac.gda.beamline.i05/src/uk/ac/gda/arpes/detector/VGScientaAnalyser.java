/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package uk.ac.gda.arpes.detector;

import gda.device.detector.NXDetectorData;
import gda.epics.connection.EpicsController;
import gda.factory.FactoryException;
import gda.factory.Finder;
import gov.aps.jca.event.MonitorEvent;
import gov.aps.jca.event.MonitorListener;

import java.util.Arrays;

import org.nexusformat.NexusFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.SDAPlotter;
import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;

public class VGScientaAnalyser extends gda.device.detector.addetector.ADDetector {
	private static final Logger logger = LoggerFactory.getLogger(VGScientaAnalyser.class);

	private class ArrayDispatcher implements MonitorListener {

		private String plotName;
		private VGScientaAnalyser analyser;

		public ArrayDispatcher(String plotName, VGScientaAnalyser analyser) {
			this.plotName = plotName;
			this.analyser = analyser;
		}

		@Override
		public void monitorChanged(MonitorEvent arg0) {
			try {
				logger.debug("sending some thing from "+arg0.toString()+" to plot "+plotName+" with axes from "+analyser.getName());
				double[] value = (double[]) arg0.getDBR().getValue();
				
				int[] dims = new int[] {getNdArray().getPluginBase().getArraySize1_RBV(), getNdArray().getPluginBase().getArraySize0_RBV()};
				value = Arrays.copyOf(value, dims[0]*dims[1]);
				AbstractDataset ds = new DoubleDataset(value, dims);

				double[] xdata = getEnergyAxis();
				double[] ydata = getAngleAxis();
				DoubleDataset xAxis = new DoubleDataset(xdata, new int[] { xdata.length });
				DoubleDataset yAxis = new DoubleDataset(ydata, new int[] { ydata.length });
				xAxis.setName("energies");
				yAxis.setName("angles");
				
				SDAPlotter.imagePlot(plotName, xAxis, yAxis, ds);
			} catch (Exception e) {
				logger.error("TODO put description of error here", e);
			}
		}
	}
	
	private VGScientaController controller;
	private AnalyserCapabilties ac;
	private EpicsController epicsController;
	private MonitorListener monlis;
	
	@Override
	public void configure() throws FactoryException {
		super.configure();
		
		monlis = new ArrayDispatcher("Detector Plot", this);
		epicsController = EpicsController.getInstance();
		try {
			epicsController.setMonitor(epicsController.createChannel("BL05I-EA-DET-01:ARR1:ArrayData"), monlis);
		} catch (Exception e) {
			throw new FactoryException("Cannot set up monitoring of arrays", e);
		}
	}
	
	private AnalyserCapabilties getAC() {
		if (ac != null) {
			return ac;
		}
		ac = Finder.getInstance().find(AnalyserCapabilties.name);
		if (ac == null)
			ac = new AnalyserCapabilties();
		return ac;
	}

	public VGScientaController getController() {
		return controller;
	}

	public void setController(VGScientaController controller) {
		this.controller = controller;
	}
	
public double[] getEnergyAxis() throws Exception {
	double start, step;
	if (controller.getAcquisitionMode().equalsIgnoreCase("Fixed")) {
		int pass = controller.getPassEnergy().intValue();
		start = controller.getCentreEnergy() - (getAC().getEnergyWidthForPass(pass)/2);
		step = getAC().getEnergyStepForPass(pass);
	} else {
		start = controller.getStartEnergy();
		step = controller.getEnergyStep();
	}

	int[] dims = determineDataDimensions(getNdArray());

	double[] axis = new double[dims[1]];
	for (int j = 0; j < dims[1]; j++) {
		axis[j] = start + j * step;
	}
	return axis;
	}

public double[] getAngleAxis() throws Exception {
	return getAC().getAngleAxis(controller.getLensMode(), getAdBase().getMinY_RBV(), getAdBase().getArraySizeY_RBV());
}

	@Override
	protected void appendDataAxes(NXDetectorData data) throws Exception {
		if (firstReadoutInScan) {
			int i = 1;
			String aname = "energies";
			String aunit = "eV";
			double[] axis = getEnergyAxis();

			data.addAxis(getName(), aname, new int[] { axis.length }, NexusFile.NX_FLOAT64, axis, i + 1, 1, aunit,
					false);

			i = 0;
			aname = "angles";
			aunit = "degree";
			axis = getAngleAxis();

			data.addAxis(getName(), aname, new int[] { axis.length }, NexusFile.NX_FLOAT64, axis, i + 1, 1, aunit,
					false);
		}
	}
}