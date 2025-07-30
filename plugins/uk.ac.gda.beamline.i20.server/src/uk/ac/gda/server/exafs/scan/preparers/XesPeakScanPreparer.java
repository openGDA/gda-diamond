/*-
 * Copyright © 2024 Diamond Light Source Ltd.
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

package uk.ac.gda.server.exafs.scan.preparers;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.apache.commons.math3.util.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.Detector;
import gda.device.Scannable;
import gda.jython.InterfaceProvider;
import gda.util.XrayLibHelper;
import uk.ac.diamond.scisoft.analysis.fitting.functions.Gaussian;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.ScanColourType;
import uk.ac.gda.beans.exafs.SpectrometerScanParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.server.exafs.scan.DetectorPreparer;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class XesPeakScanPreparer implements DetectorPreparer {
	private static final Logger logger = LoggerFactory.getLogger(XesPeakScanPreparer.class);

	private boolean runPeakFinding = false;
	private Map<String, CurveFitScanRunner> scanRunners = Collections.emptyMap();
	private Scannable monoScannable;
	private IScanParameters scanBean;
	private String experimentFullPath;
	private String oneColourXesScannableName = "XESEnergyLower";

	/** Energy relative to edge that mono should be moved to for peak scan */
	private double monoEnergyOffset = 0;

	@Override
	public void configure(IScanParameters scanBean, IDetectorParameters detectorBean, IOutputParameters outputBean,
			String experimentFullPath) throws Exception {
		this.experimentFullPath = experimentFullPath;
		this.scanBean = scanBean;
	}

	@Override
	public void beforeEachRepetition() throws Exception {
		if (!runPeakFinding) {
			return;
		}

		if (scanBean instanceof XesScanParameters xesParams &&
			(xesParams.getScanType() == XesScanParameters.FIXED_XES_SCAN_XANES
			|| xesParams.getScanType() == XesScanParameters.FIXED_XES_SCAN_XAS) ) {
				runPeakFinding(xesParams);
		}
	}

	private void logAndPrint(String message) {
		logger.info(message);
		InterfaceProvider.getTerminalPrinter().print(message);
	}

	private void runPeakFinding(XesScanParameters xesParams) throws Exception {

		// If 'one colour' mode, set to 'two colour' type so that peak can be found for both
		// rows and both rows can be set to their own peak energy position.
		if (xesParams.getScanColourType() == ScanColourType.ONE_COLOUR) {

			// set row2 energy to match row row1
			double fixedEnergy = xesParams.getPrimarySpectrometerScanParams().getFixedEnergy();

			logger.info("Changing colour type from'{}' to '{}' and using initial fixed energy of {} eV for both rows - to allow different peak positions during scan",
					ScanColourType.ONE_COLOUR.getDescription(), ScanColourType.TWO_COLOUR.getDescription(), fixedEnergy);

			xesParams.getSpectrometerScanParameters().get(1).setFixedEnergy(fixedEnergy);

			xesParams.setScanColourType(ScanColourType.TWO_COLOUR);
		}

		Map<String, SpectrometerScanParameters> spectrometerParams = xesParams.getActiveSpectrometerParameters();

		logger.info("Colour mode : {}, XES scannables : {}", xesParams.getScanColourType(), spectrometerParams.keySet());

		// Lookup element and edge, calculate the edge energy
		Pair<String, String> elementEdge = getElementAndEdge(xesParams);
		double edgeEnergy = XrayLibHelper.getEdgeEnergy(elementEdge.getFirst(), elementEdge.getSecond());
		logAndPrint(String.format("Element : %s, Edge : %s, Edge energy : %.4f eV", elementEdge.getFirst(), elementEdge.getSecond(), edgeEnergy));

		// move the mono into position
		double monoEnergy = getMonoEnergy(edgeEnergy);
		logAndPrint(String.format("Moving mono to %.4f eV", monoEnergy));

		monoScannable.moveTo(monoEnergy);

		for(var specParams : spectrometerParams.entrySet()) {
			double xesEnergy = specParams.getValue().getFixedEnergy();
			String xesScannableName = specParams.getKey();
			logAndPrint(String.format("Running peak scan for %s", xesScannableName));

			var scanRunner = getScanRunner(xesScannableName);
			if (scanRunner == null) {
				throw new IllegalArgumentException("Cannot run scan for "+xesScannableName+" - no CurveFitScanRunner has been set for that scannable");
			}
			scanRunner.runScan(xesEnergy);
			Gaussian fitResults = scanRunner.fitData();
			double peakEnergy = fitResults.getPosition();
			logAndPrint(String.format("Peak emission energy : %.4f eV", peakEnergy));

			specParams.getValue().setFixedEnergy(peakEnergy);
		}
	}

	/**
	 * Get the element and edge values from Xas/Xanes file referenced in XesScanParameters bean.
	 * @param xesParams
	 * @return
	 * @throws Exception
	 */
	private Pair<String, String> getElementAndEdge(XesScanParameters xesParams) throws Exception {
		// Load the Xas/Xanes scan parameters file
		var monoScanParams = XMLHelpers.getBeanObject(experimentFullPath, xesParams.getScanFileName());
		String edgeName;
		String elementName;
		// get element and edge values (these beans don't share a common interface...)
		if (monoScanParams instanceof XasScanParameters xasParams) {
			edgeName = xasParams.getEdge();
			elementName = xasParams.getElement();
		} else if (monoScanParams instanceof XanesScanParameters xanesParams) {
			edgeName = xanesParams.getEdge();
			elementName = xanesParams.getElement();
		} else {
			throw new IllegalArgumentException("Scan file "+xesParams.getScanFileName()+" is not of expected type (XasScanParameters or XanesScanParameters)");
		}
		return Pair.create(elementName, edgeName);
	}

	/**
	 * Return the energy the mono should move to for a given edge energy
	 * - currently just the edge energy + constant offset
	 * @param edgeEnergy
	 * @return
	 */
	private double getMonoEnergy(double edgeEnergy) {
		return edgeEnergy + monoEnergyOffset;
	}

	public double getMonoEnergyOffset() {
		return monoEnergyOffset;
	}

	public void setMonoEnergyOffset(double monoEnergyOffset) {
		this.monoEnergyOffset = monoEnergyOffset;
	}

	/**
	 * Return ScanRunner object that moves a scannable with given name.
	 * @param scnName
	 * @return CurveFitScanRunner object, or null if no match was found
	 */
	private CurveFitScanRunner getScanRunner(String scnName) {
		return scanRunners.get(scnName);
	}

	@Override
	public void completeCollection() {
	}

	@Override
	public Detector[] getExtraDetectors() {
		return null;
	}

	public boolean isRunPeakFinding() {
		return runPeakFinding;
	}

	public void setRunPeakFinding(boolean runPeakFinding) {
		this.runPeakFinding = runPeakFinding;
	}

	public Map<String, CurveFitScanRunner> getScanRunners() {
		return scanRunners;
	}

	public void setScanRunners(List<CurveFitScanRunner> scanRunners) {
		this.scanRunners = scanRunners.stream()
			.collect(Collectors.toMap(scanRunner -> scanRunner.getScannableToMove().getName(), scanRunner -> scanRunner));
	}

	public Scannable getMonoScannable() {
		return monoScannable;
	}

	public void setMonoScannable(Scannable monoScannable) {
		this.monoScannable = monoScannable;
	}

	public String getOneColourXesScannableName() {
		return oneColourXesScannableName;
	}

	public void setOneColourXesScannableName(String oneColourXesScannableName) {
		this.oneColourXesScannableName = oneColourXesScannableName;
	}

}
