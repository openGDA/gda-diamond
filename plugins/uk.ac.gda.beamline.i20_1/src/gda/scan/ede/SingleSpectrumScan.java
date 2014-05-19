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

package gda.scan.ede;

import gda.device.DeviceException;
import gda.scan.ede.EdeExperimentProgressBean.ExperimentCollectionType;
import gda.scan.ede.datawriters.EdeExperimentDataWriter;
import gda.scan.ede.datawriters.EdeSingleSpectrumAsciiFileWriter;
import gda.scan.ede.timeestimators.SingleExperimentTimeEstimator;

import java.util.Map;

import uk.ac.gda.exafs.ui.data.EdeScanParameters;

/**
 * The simplest EDE experiment type: collect Dark I0, Dark It (optional), I0,It,I0, do corrections and calculate derived
 * data. Record data to Nexus while collection in progress, write to a custom Ascii format on completion.
 * <p>
 * The I0 timing can be the same as the It timing parameters, if not explicitly supplied instead. So only a single time
 * frame and timing group must be supplied. Sample environments are not taken into account here.
 * <p>
 * It will be assumed that the EdeScanParameters objects given to this class respresent a single TmingGroup producing a
 * single spectrum.
 */
public class SingleSpectrumScan extends EdeExperiment {

	private boolean runItDark;

	public SingleSpectrumScan(double i0accumulationTime, double iTAccumulationTime, int iTnoOfAccumulcation,
			Map<String, Double> i0ScanableMotorPositions,
			Map<String, Double> iTScanableMotorPositions,
			String detectorName,
			String topupMonitorName,
			String beamShutterScannableName) throws DeviceException {
		this(i0accumulationTime, iTnoOfAccumulcation, iTAccumulationTime, iTnoOfAccumulcation, i0ScanableMotorPositions, iTScanableMotorPositions, detectorName, topupMonitorName, beamShutterScannableName);
	}

	public SingleSpectrumScan(double i0AccumulationTime, int i0NoOfAccumulcation, double iTaccumulationTime, int iTnoOfAccumulcation,
			Map<String, Double> i0ScanableMotorPositions,
			Map<String, Double> iTScanableMotorPositions,
			String detectorName,
			String topupMonitorName,
			String beamShutterScannableName) throws DeviceException {
		super(EdeScanParameters.createSingleFrameScan(iTaccumulationTime, iTnoOfAccumulcation),
				i0ScanableMotorPositions,
				iTScanableMotorPositions,
				detectorName,
				topupMonitorName,
				beamShutterScannableName);
		if (i0AccumulationTime != iTaccumulationTime | i0NoOfAccumulcation != iTnoOfAccumulcation) {
			runItDark = true;
		}
		setCommonI0Parameters(i0AccumulationTime, i0NoOfAccumulcation);
	}

	@Override
	protected ExperimentCollectionType getCollectionType() {
		return ExperimentCollectionType.SINGLE;
	}

	@Override
	protected boolean shouldPublishItScanData(EdeScanProgressBean progress) {
		return true;
	}

	@Override
	protected int getRepetitions() {
		return 1;
	}

	@Override
	protected String getHeaderText() {
		StringBuilder header = new StringBuilder();
		header.append("i0Dark: " + i0DarkScan.getHeaderDescription() + "\n");
		if (runItDark) {
			header.append("itDark: " + itDarkScan.getHeaderDescription() + "\n");
		}
		header.append("i0InitialScan: " + i0LightScan.getHeaderDescription() + "\n");
		header.append("itScan: " + itScans[0].getHeaderDescription() + "\n");
		return header.toString();
	}

	@Override
	protected double getTimeRequiredBeforeTopup() {
		// for this type, the time required before to-up is the total predicted duration of the entire experiment.
		return new SingleExperimentTimeEstimator(itScanParameters, i0Position, itPosition).getTotalDuration();
	}

	@Override
	protected EdeExperimentDataWriter createFileWritter() {
		return new EdeSingleSpectrumAsciiFileWriter(i0LightScan, itScans[0],
				i0DarkScan, itDarkScan, theDetector);
	}

	@Override
	protected boolean shouldRunItDark() {
		return runItDark;
	}

	@Override
	protected void addFinalScans() {
		// Nothing to add
	}
}
