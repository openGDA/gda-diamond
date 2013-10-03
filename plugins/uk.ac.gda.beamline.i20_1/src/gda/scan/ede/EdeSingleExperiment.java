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

import gda.device.detector.StripDetector;
import gda.scan.EdeScan;
import gda.scan.MultiScan;
import gda.scan.ScanBase;
import gda.scan.ede.datawriters.EdeSingleSpectrumAsciiFileWriter;
import gda.scan.ede.position.EdeScanPosition;

import java.util.List;
import java.util.Vector;

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
public class EdeSingleExperiment extends EdeExperiment {

	protected final EdeScanPosition i0Position;
	protected final EdeScanPosition itPosition;
	protected final EdeScanParameters i0ScanParameters;
	protected final EdeScanParameters itScanParameters;
	protected final Boolean runItDark;
	protected final StripDetector theDetector;

	private EdeScan i0DarkScan;
	private EdeScan itDarkScan;
	private EdeScan i0InitialScan;
	private EdeScan itScan;

	/**
	 * Use when the I0 and It timing parameters are different.
	 * 
	 * @param i0ScanParameters
	 * @param itScanParameters
	 * @param i0Position
	 * @param itPosition
	 * @param theDetector
	 */
	public EdeSingleExperiment(EdeScanParameters i0ScanParameters, EdeScanParameters itScanParameters,
			EdeScanPosition i0Position, EdeScanPosition itPosition, StripDetector theDetector) {
		super();
		this.i0ScanParameters = i0ScanParameters;
		this.i0Position = i0Position;
		this.itPosition = itPosition;
		this.itScanParameters = itScanParameters;
		this.theDetector = theDetector;
		runItDark = true;
		validateTimingParameters();
	}

	/**
	 * Use when the I0 and It timing parameters are the same.
	 * 
	 * @param itScanParameters
	 * @param i0Position
	 * @param itPosition
	 * @param theDetector
	 */
	public EdeSingleExperiment(EdeScanParameters itScanParameters, EdeScanPosition i0Position,
			EdeScanPosition itPosition, StripDetector theDetector) {
		super();
		this.i0Position = i0Position;
		this.itPosition = itPosition;
		i0ScanParameters = itScanParameters;
		this.itScanParameters = itScanParameters;
		this.theDetector = theDetector;
		runItDark = false;
		validateTimingParameters();
	}

	protected void validateTimingParameters() {
		if (i0ScanParameters.getGroups().size() != 1) {
			throw new IllegalArgumentException("Only one timing group must be used in this type of scan!");
		}
		if (i0ScanParameters.getGroups().get(0).getNumberOfFrames() != 1) {
			throw new IllegalArgumentException("Only one frame must be used in this type of scan!");
		}
		if (itScanParameters.getGroups().size() != 1) {
			throw new IllegalArgumentException("Only one timing group must be used in this type of scan!");
		}
		if (itScanParameters.getGroups().get(0).getNumberOfFrames() != 1) {
			throw new IllegalArgumentException("Only one frame must be used in this type of scan!");
		}
	}

	@Override
	public String runExperiment() throws Exception {
		runScans();
		EdeSingleSpectrumAsciiFileWriter writer = new EdeSingleSpectrumAsciiFileWriter(i0InitialScan, itScan,
				i0DarkScan, itDarkScan, theDetector);
		if (filenameTemplate != null && !filenameTemplate.isEmpty()) {
			writer.setFilenameTemplate(filenameTemplate);
		}
		writer.writeAsciiFile();
		log("EDE single spectrum experiment complete.");
		return writer.getAsciiFilename();
	}

	private void runScans() throws Exception {
		i0DarkScan = new EdeScan(i0ScanParameters, i0Position, EdeScanType.DARK, theDetector, 1);
		if (runItDark) {
			itDarkScan = new EdeScan(itScanParameters, itPosition, EdeScanType.DARK, theDetector, 1);
		} else {
			itDarkScan = i0DarkScan;
		}
		i0InitialScan = new EdeScan(i0ScanParameters, i0Position, EdeScanType.LIGHT, theDetector, 1);
		itScan = new EdeScan(itScanParameters, itPosition, EdeScanType.LIGHT, theDetector, 1);

		List<ScanBase> theScans = new Vector<ScanBase>();
		theScans.add(i0DarkScan);
		if (runItDark) {
			theScans.add(itDarkScan);
		}
		theScans.add(i0InitialScan);
		theScans.add(itScan);

		MultiScan theScan = new MultiScan(theScans);
		theScan.runScan();
	}
}
