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
import gda.factory.Finder;
import gda.jython.scriptcontroller.ScriptControllerBase;
import gda.observable.IObserver;
import gda.scan.EdeScan;
import gda.scan.MultiScan;
import gda.scan.ScanBase;
import gda.scan.ede.datawriters.EdeAsciiFileWriter;
import gda.scan.ede.datawriters.EdeLinearExperimentAsciiFileWriter;
import gda.scan.ede.position.EdeScanPosition;

import java.util.List;
import java.util.Vector;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

/**
 * Similar to the {@link EdeLinearExperiment} class except that a series of TimingGroups are run which will produce
 * multiple spectra. In other words the itScanParameters given to this class is not assumed to be a single timing group
 * producing a single spectrum.
 * <p>
 * The experiment is not repeated, so all the spectra will occur at a different point in time wrt the progress of a
 * chemical reaction or other state of the sample.
 */
public class EdeLinearExperiment extends EdeExperiment implements IObserver {

	// private static final Logger logger = LoggerFactory.getLogger(EdeSingleExperiment.class);

	private final EdeScanParameters itScanParameters;
	private final EdeScanPosition i0Position;
	private final EdeScanPosition itPosition;
	private final StripDetector theDetector;

	private EdeScanParameters i0ScanParameters;
	private EdeScan i0DarkScan;
	private EdeScan i0InitialScan;
	private EdeScan itScan;
	private EdeScan i0FinalScan;
	private EdeLinearExperimentAsciiFileWriter writer;
	private final ScriptControllerBase controller;

	public EdeLinearExperiment(EdeScanParameters itScanParameters, EdeScanPosition i0Position,
			EdeScanPosition itPosition, StripDetector theDetector) {
		this.itScanParameters = itScanParameters;
		this.i0Position = i0Position;
		this.itPosition = itPosition;
		this.theDetector = theDetector;
		controller = (ScriptControllerBase) Finder.getInstance().findNoWarn(PROGRESS_UPDATER_NAME);
	}

	/**
	 * Run the scans and write the data files.
	 * <p>
	 * Should not return until data collection completed.
	 * 
	 * @throws Exception
	 */
	@Override
	public String runExperiment() throws Exception {
		deriveI0ScansFromIts();
		runScans();
		return writeAsciiFile();
	}

	@Override
	public void update(Object source, Object arg) {
		// only expect EdeScanProgressBean objects from the itScan here. Normalise the data and broadcast out to the
		if (controller != null && source.equals(itScan) && arg instanceof EdeScanProgressBean) {
			// assume that the I0 and dark scans have run correctly if we are getting messages back from It scan
			EdeScanProgressBean progress = (EdeScanProgressBean) arg;
			DoubleDataset darkData = EdeAsciiFileWriter.extractDetectorDataSets(theDetector.getName(), i0DarkScan, 0);
			DoubleDataset i0Data = EdeAsciiFileWriter.extractDetectorDataSets(theDetector.getName(), i0InitialScan, progress.getGroupNumOfThisSDP());
			DoubleDataset thisItData = EdeAsciiFileWriter.extractDetectorDataFromSDP(theDetector.getName(), progress.getThisPoint());
			DoubleDataset normalisedIt = EdeAsciiFileWriter.normaliseDatasset(thisItData, i0Data, darkData);
			controller.update(itScan, new EdeExperimentProgressBean(progress,normalisedIt));
		}
	}

	/**
	 * NPE if this is called before the scan has been run and the datawriter has been created
	 * 
	 * @return the name of the I0 output file
	 */
	public String getI0Filename() {
		return writer.getAsciiI0Filename();
	}

	/**
	 * NPE if this is called before the scan has been run and the datawriter has been created
	 * 
	 * @return the name of the It output file
	 */
	public String getItFilename() {
		return writer.getAsciiItFilename();
	}

	/**
	 * NPE if this is called before the scan has been run and the datawriter has been created
	 * 
	 * @return the name of the It output file
	 */
	public String getItFinalFilename() {
		return writer.getAsciiItFinalFilename();
	}

	/**
	 * NPE if this is called before the scan has been run and the datawriter has been created
	 * 
	 * @return the name of the It output file
	 */
	public String getItAveragedFilename() {
		return writer.getAsciiItAveragedFilename();
	}

	private void deriveI0ScansFromIts() {
		// need an I0 spectrum for each timing group in itScanParameters
		List<TimingGroup> itgroups = itScanParameters.getGroups();

		EdeScanParameters i0Parameters = new EdeScanParameters();
		for (TimingGroup itGroup : itgroups) {
			TimingGroup newI0Group = new TimingGroup();
			newI0Group.setLabel(itGroup.getLabel());
			newI0Group.setNumberOfFrames(1);
			newI0Group.setTimePerScan(itGroup.getTimePerScan());
			newI0Group.setTimePerFrame(itGroup.getTimePerFrame());
			newI0Group.setDelayBetweenFrames(0);
			newI0Group.setNumberOfScansPerFrame(itGroup.getNumberOfScansPerFrame());
			i0Parameters.addGroup(newI0Group);
		}

		i0ScanParameters = i0Parameters;
	}

	private void runScans() throws InterruptedException, Exception {
		i0DarkScan = new EdeScan(i0ScanParameters, i0Position, EdeScanType.DARK, theDetector, 1);
		i0InitialScan = new EdeScan(i0ScanParameters, i0Position, EdeScanType.LIGHT, theDetector, 1);
		itScan = new EdeScan(itScanParameters, itPosition, EdeScanType.LIGHT, theDetector, 1);
		itScan.setProgressUpdater(this);
		i0FinalScan = new EdeScan(i0ScanParameters, i0Position, EdeScanType.LIGHT, theDetector, 1);

		List<ScanBase> theScans = new Vector<ScanBase>();
		theScans.add(i0DarkScan);
		theScans.add(i0InitialScan);
		theScans.add(itScan);
		theScans.add(i0FinalScan);

		MultiScan theScan = new MultiScan(theScans);
		theScan.runScan();
	}

	private String writeAsciiFile() throws Exception {
		writer = new EdeLinearExperimentAsciiFileWriter(i0DarkScan, i0InitialScan, itScan, i0FinalScan, theDetector);
		if (filenameTemplate != null && !filenameTemplate.isEmpty()) {
			writer.setFilenameTemplate(filenameTemplate);
		}
		writer.writeAsciiFile();
		log("EDE single spectrum experiment complete.");
		return writer.getAsciiItFilename();
	}
}
