/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package gda.scan;

import gda.device.Detector;
import gda.device.Scannable;
import gda.gui.exafs.Converter;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A scan class which scan in energy with constant K increments.
 */
public class EnergyKScan extends ScanBase {
	
	private static final Logger logger = LoggerFactory.getLogger(EnergyKScan.class);

	protected Scan childScan;
	protected double start;
	protected double stop;
	protected double step;
	private double kStartTime = 0;
	private double kEndTime = 0;
	private double kWeighting = 0;
	private double edgeEnergy = 0;

	/**
	 * Creates a scan object
	 * 
	 * @param ve
	 *            the scannable
	 * @param start
	 *            double
	 * @param stop
	 *            double
	 * @param step
	 *            double
	 * @param kStartTime
	 *            Object
	 * @param kEndTime
	 *            Object
	 * @param kWeighting
	 *            Object
	 * @param edgeEnergy
	 *            Object
	 */
	public EnergyKScan(Scannable ve, Object start, Object stop, Object step, Object kStartTime, Object kEndTime,
			Object kWeighting, Object edgeEnergy) {
		allScannables.add(ve);
		this.start = Double.parseDouble(start.toString());
		this.stop = Double.parseDouble(stop.toString());
		this.step = Double.parseDouble(step.toString());
		this.childScan = null;
		this.kStartTime = Double.parseDouble(kStartTime.toString());
		this.kEndTime = Double.parseDouble(kEndTime.toString());
		this.kWeighting = Double.parseDouble(kWeighting.toString());
		this.edgeEnergy = Double.parseDouble(edgeEnergy.toString());
		setUp();
	}

	/**
	 * A static method to create a scan which has a nested scan inside it. To run the scan, call the runKScan() method.
	 * For example, in Jython: from gda.scan import EnergyKScan; myScan =
	 * EnergyKScan.create(tth,10,12,0.1,EnergyKScan.create(phi,20,30,1)); myScan.runEnergyKScan()
	 * 
	 * @param ve
	 *            the scannable
	 * @param start
	 *            The position of the first data point
	 * @param stop
	 *            The position of the final data point
	 * @param step
	 *            The increment between data points
	 * @param kStartTime
	 *            Object
	 * @param kEndTime
	 *            Object
	 * @param kWeighting
	 *            Object
	 * @param edgeEnergy
	 *            Object
	 * @param childScan
	 *            ScanBase
	 */
	public EnergyKScan(Scannable ve, Object start, Object stop, Object step, Object kStartTime, Object kEndTime,
			Object kWeighting, Object edgeEnergy, Scan childScan) {
		allScannables.add(ve);
		this.start = Double.parseDouble(start.toString());
		this.stop = Double.parseDouble(stop.toString());
		this.step = Double.parseDouble(step.toString());
		this.childScan = childScan;
		this.kStartTime = Double.parseDouble(kStartTime.toString());
		this.kEndTime = Double.parseDouble(kEndTime.toString());
		this.kWeighting = Double.parseDouble(kWeighting.toString());
		this.edgeEnergy = Double.parseDouble(edgeEnergy.toString());
		setUp();
	}

	/**
	 * Run the scan.
	 * <p>
	 * If the parameters given to this method are just numbers, then handle the scan logic here. If its more complicated
	 * then information should have been typed within []'s and would be passed to here from Jython as a PyList. In this
	 * case the logic should be handled in a Scannable object by a doScan method.
	 * </p>
	 * 
	 * @throws Exception
	 */
	@Override
	public void doCollection() throws Exception {
		try {

			// inform user that scan has started
			logger.debug("Started a scan in KSpace over " + allScannables.get(0).getName() + "\n");

			// check that step is negative when moving downwards to stop
			double difference = evToK(stop, edgeEnergy) - evToK(start, edgeEnergy);
			if (difference < 0 && step > 0) {
				step = -step;
			}
			int numberSteps = (int) (difference / step);

			// loop through all the points in the node vector
			double currentPosition;
			double mdegPosition = evToK(start, edgeEnergy);
			for (int j = 0; j <= numberSteps; j++) {

				// Increment the current position. This is done here so that we don't collect
				// a double point at the beginning of the region.
				mdegPosition += step;
				currentPosition = kToEv(mdegPosition, edgeEnergy);
				double secTime = timeForK(mdegPosition);

				checkThreadInterrupted();
				if (isFinishEarlyRequested()) {
					break;
				}
				
				logger.debug("Moving " + allScannables.get(0).getName() + " to " + currentPosition
						+ "\n");
				allScannables.get(0).moveTo(new Double(currentPosition));
				// run a nested scan if there is one
				if (childScan != null) {
					
					checkThreadInterrupted();
					if (isFinishEarlyRequested()) {
						break;
					}
					
					// The following line is required to ensure that for nested scans
					// the addData is called by the outer scan first in order to setup
					// the required columns and headers.
					ScanDataPoint point = new ScanDataPoint();
					point.setHasChild(hasChild());
					getDataWriter().addData(point);
					// TODO: should this not broadcast the point too?
					childScan.run();
				} else {
					// Set the collection time for all detectors
					for (Detector detector : allDetectors) {
						detector.setCollectionTime(secTime);
					}
					currentPointCount++;
					collectData();
				}
			}

			if (!getStatus().isAborting()) {
				logger.debug("Finished scanning over " + allScannables.get(0).getName() + "\n");
			}
		}
		// catch all errors, including InterruptedExceptions thrown by
		// checkForInterrupts() calls.
		catch (Exception ex1) {
			setStatus(ScanStatus.TIDYING_UP_AFTER_FAILURE);
			throw ex1;
		}
		// at end of scan remove all the observers of the detectors which were
		// registered through this scan
		endScan();
	}

	/**
	 * Creates and runs a scan. For example, in Jython: from gda.scan import StepScan; StepScan(tth,10,12,0.1)
	 * 
	 * @param ve
	 *            Scannable
	 * @param start
	 *            double
	 * @param stop
	 *            double
	 * @param step
	 *            double
	 * @param kStartTime
	 *            Object
	 * @param kEndTime
	 *            Object
	 * @param kWeighting
	 *            Object
	 * @param edgeEnergy
	 *            Object
	 * @param twoD
	 *            Object
	 * @throws InterruptedException
	 * @throws Exception
	 */
	public static void runKScan(Scannable ve, Object start, Object stop, Object step, Object kStartTime,
			Object kEndTime, Object kWeighting, Object edgeEnergy, Object twoD) throws InterruptedException, Exception {
		KScan thisScan = new KScan(ve, start, stop, step, kStartTime, kEndTime, kWeighting, edgeEnergy, twoD);
		thisScan.runScan();
	}

	/**
	 * Creates and runs a scan which has a nested scan inside it. For example, in Jython: from gda.scan import StepScan;
	 * StepScan(tth,10,12,0.1,StepScan(phi,20,30,1))
	 * 
	 * @param ve
	 *            Scannable
	 * @param start
	 *            double
	 * @param stop
	 *            double
	 * @param step
	 *            double
	 * @param kStartTime
	 *            Object
	 * @param kEndTime
	 *            Object
	 * @param kWeighting
	 *            Object
	 * @param edgeEnergy
	 *            Object
	 * @param childScan
	 *            Scan
	 * @throws InterruptedException
	 * @throws Exception
	 */
	public static void runKScan(Scannable ve, Object start, Object stop, Object step, Object kStartTime,
			Object kEndTime, Object kWeighting, Object edgeEnergy, Scan childScan) throws InterruptedException,
			Exception {
		EnergyKScan thisScan = new EnergyKScan(ve, start, stop, step, kStartTime, kEndTime, kWeighting, edgeEnergy,
				childScan);
		thisScan.runScan();
	}

	/**
	 * evForK converts energy in eV in k value (in inverse angstroms)
	 * 
	 * @param energy
	 *            energy to convert
	 * @param edgeEnergy
	 *            element edge energy in eV
	 * @return k in inverse Angstroms
	 */
	public double evToK(double energy, double edgeEnergy) {
		Converter.setEdgeEnergy(edgeEnergy/1000.0);
		return Converter.convert(energy, Converter.EV, Converter.PERANGSTROM);
	}

	/**
	 * kToEv converts energy in k to a value in ev 
	 * 
	 * @param value
	 *            value to convert
	 * @param edgeEnergy
	 *            element edge energy
	 * @return energy in eV
	 */
	public double kToEv(double value, double edgeEnergy) {
		Converter.setEdgeEnergy(edgeEnergy/1000.0);
		return Converter.convert(value, Converter.PERANGSTROM, Converter.EV);
	}

	/**
	 * timeForK calculates the appropriate counting time for a particular k value
	 * 
	 * @param k
	 *            double
	 * @return double
	 */
	public double timeForK(double k) {
		double a = Math.pow(k - start, kWeighting);
		double b = Math.pow(stop - start, kWeighting);
		double c = (kEndTime - kStartTime);
		double time = kStartTime + (a * c) / b;
		return time;
	}

	/**
	 * Returns whether a child scan has been requested.
	 * 
	 * @return a boolean indicating whether the gridscan has an associated childscan
	 */
	public boolean hasChild() {
		return childScan != null;
	}	
}
