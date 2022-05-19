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

import java.util.Map;

import org.dawnsci.ede.EdeScanType;

import gda.device.DeviceException;
import gda.device.scannable.TopupChecker;
import gda.scan.EdeScan;
import gda.scan.EdeScanWithTFGTrigger;
import gda.scan.ede.EdeExperimentProgressBean.ExperimentCollectionType;
import gda.scan.ede.datawriters.EdeExperimentDataWriter;
import gda.scan.ede.datawriters.EdeSingleSpectrumAsciiFileWriter;
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
	private double accumulationReadoutTime = 0;

	public SingleSpectrumScan(double i0AccumulationTime, int i0NoOfAccumulcation, double iTaccumulationTime, int iTnoOfAccumulcation,
			Map<String, Double> i0ScanableMotorPositions,
			Map<String, Double> iTScanableMotorPositions,
			String detectorName,
			String topupMonitorName,
			String beamShutterScannableName) throws DeviceException {
		super(EdeScanParameters.createSingleFrameScan(iTaccumulationTime, iTnoOfAccumulcation).getGroups(),
				i0ScanableMotorPositions,
				iTScanableMotorPositions,
				detectorName,
				topupMonitorName,
				beamShutterScannableName);
		if (i0AccumulationTime != iTaccumulationTime | i0NoOfAccumulcation != iTnoOfAccumulcation) {
			runItDark = true;
		}
		runItWithTriggerOptions = false;
		setCommonI0Parameters(i0AccumulationTime, i0NoOfAccumulcation);
	}

	public void setUseTopupChecker( boolean useTopupChecker ) {
		if ( itScanParameters.getGroups().size() > 0 ) {
			itScanParameters.getGroups().get(0).setUseTopupChecker( useTopupChecker );
		}
	}

	@Override
	protected ExperimentCollectionType getCollectionType() {
		return ExperimentCollectionType.SINGLE;
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
	public EdeExperimentDataWriter createFileWritter() {
		EdeSingleSpectrumAsciiFileWriter asciiWriter = new EdeSingleSpectrumAsciiFileWriter(i0DarkScan, i0LightScan, iRefScan, iRefDarkScan, itDarkScan,
				itScans, i0FinalScan, iRefFinalScan, theDetector, nexusFilename);
		asciiWriter.setAccumulationReadoutTime(accumulationReadoutTime);
		asciiWriter.setExtraScannables(itScans[0].getScannablesToMonitorDuringScan());
		return asciiWriter;
	}

	public void setAccumulationReadoutTime(double accumulationReadoutTime) {
		this.accumulationReadoutTime = accumulationReadoutTime;
	}

	@Override
	protected boolean shouldRunItDark() {
		return runItDark;
	}

	@Override
	protected void addFinalScans() throws Exception {
		int repetitions = getRepetitions();
		double timeToTopup = getNextTopupTime();

		if (shouldRunItDark()) {
			EdeScanParameters itDarkScanParameters = deriveItDarkParametersFromItParameters();
			itDarkScanParameters.setUseFrameTime(false);
			itDarkScan = makeEdeScan(itDarkScanParameters, itPosition, EdeScanType.DARK, firstRepetitionIndex, null);
			itDarkScan.setProgressUpdater(this);
			scansBeforeIt.add(itDarkScan);
		} else {
			itDarkScan = i0DarkScan;
		}

		// Add topup checker for I0 to make sure I0 and It collection occur in same topup cycle.
		double timeRequired = getTimeRequiredBeforeItCollection() + getTimeRequiredForItCollection();
		TopupChecker topupChecker = getItWaitForTopup() ? createTopupChecker(timeRequired, timeToTopup) : null;

		i0ScanParameters.setUseFrameTime(false);
		i0LightScan = makeEdeScan(i0ScanParameters, i0Position, EdeScanType.LIGHT, firstRepetitionIndex, topupChecker);
		i0LightScan.setProgressUpdater(this);
		scansBeforeIt.add(i0LightScan);

		if (runIRef) {
			i0ForiRefScanParameters.setUseFrameTime(false);
			i0ForiRefScan = makeEdeScan(i0ForiRefScanParameters, i0ForiRefPosition, EdeScanType.LIGHT, firstRepetitionIndex, null);
			scansBeforeIt.add(i0ForiRefScan);
			i0ForiRefScan.setProgressUpdater(this);

			iRefScanParameters.setUseFrameTime(false);
			iRefScan = makeEdeScan(iRefScanParameters, iRefPosition, EdeScanType.LIGHT, firstRepetitionIndex, null);
			scansBeforeIt.add(iRefScan);
			iRefScan.setProgressUpdater(this);
		}

		if (runItWithTriggerOptions) {
			itScans = new EdeScanWithTFGTrigger[repetitions];

			itScanParameters.setUseFrameTime(false);
			for(int repIndex = 0; repIndex < repetitions; repIndex++){
				itScans[repIndex] = new EdeScanWithTFGTrigger(itScanParameters, itTriggerOptions, itPosition, EdeScanType.LIGHT, theDetector, repIndex, beamLightShutter, false);
				itScans[repIndex].setProgressUpdater(this);
				scansForIt.add(itScans[repIndex]);
			}
		} else {
			itScans = new EdeScan[repetitions];
			itScanParameters.setUseFrameTime(false);
			for(int repIndex = 0; repIndex < repetitions; repIndex++){
				itScans[repIndex] = makeEdeScan(itScanParameters, itPosition, EdeScanType.LIGHT, repIndex, null);
				itScans[repIndex].setProgressUpdater(this);
				scansForIt.add(itScans[repIndex]);
			}
		}

	}

	@Override
	protected boolean shouldWaitForTopup(int repIndex, double timeToTopupInSec) {
		double timeRequired = getTimeRequiredForItCollection();

		if ( timeRequired < timeToTopupInSec || timeRequired < TOP_UP_TIME) {
			return false;
		} else {
			return true;
		}
	}

	//	@Override
	//	protected double getTimeRequiredBeforeItCollection() {
	//		// TODO Auto-generated method stub
	//		return 0;
	//	}
	//
	//	@Override
	//	protected double getTimeRequiredForItCollection() {
	//		// TODO Auto-generated method stub
	//		return 0;
	//	}
	//
	//	@Override
	//	protected double getTimeRequiredAfterItCollection() {
	//		// TODO Auto-generated method stub
	//		return 0;
}

