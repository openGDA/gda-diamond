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

import gda.data.scan.datawriter.NexusExtraMetadataDataWriter;
import gda.data.scan.datawriter.NexusFileMetadata;
import gda.data.scan.datawriter.NexusFileMetadata.EntryTypes;
import gda.data.scan.datawriter.NexusFileMetadata.NXinstrumentSubTypes;
import gda.device.Monitor;
import gda.device.Scannable;
import gda.device.detector.StripDetector;
import gda.device.scannable.TopupChecker;
import gda.observable.IObserver;
import gda.scan.EdeScan;
import gda.scan.MultiScan;
import gda.scan.ScanBase;
import gda.scan.ScanPlotSettings;
import gda.scan.ede.EdeExperimentProgressBean.ExperimentCollectionType;
import gda.scan.ede.datawriters.EdeAsciiFileWriter;
import gda.scan.ede.datawriters.EdeSingleSpectrumAsciiFileWriter;
import gda.scan.ede.position.EdeScanPosition;
import gda.scan.ede.timeestimators.SingleExperimentTimeEstimator;

import java.util.List;
import java.util.Vector;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
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
public class EdeSingleExperiment extends EdeExperiment implements IObserver {

	private static final Logger logger = LoggerFactory.getLogger(EdeSingleExperiment.class);

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

	private final Scannable shutter2;

	private DoubleDataset energyData;
	private DoubleDataset i0DarkData;
	private DoubleDataset itDarkData;
	private DoubleDataset i0Data;
	private DoubleDataset itData;

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
			EdeScanPosition i0Position, EdeScanPosition itPosition, StripDetector theDetector, Monitor topupMonitor,
			Scannable shutter2) {
		super();
		this.i0ScanParameters = i0ScanParameters;
		this.i0Position = i0Position;
		this.itPosition = itPosition;
		this.itScanParameters = itScanParameters;
		this.theDetector = theDetector;
		this.shutter2 = shutter2;
		topup = topupMonitor;
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
			EdeScanPosition itPosition, StripDetector theDetector, Monitor topupMonitor, Scannable shutter2) {
		super();
		this.i0Position = i0Position;
		this.itPosition = itPosition;
		i0ScanParameters = itScanParameters;
		this.itScanParameters = itScanParameters;
		this.theDetector = theDetector;
		this.shutter2 = shutter2;
		topup = topupMonitor;
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
		logger.debug("EDE single experiment writing its ascii derived data files...");
		writer.writeAsciiFile();
		log("EDE single spectrum experiment complete.");
		return writer.getAsciiFilename();
	}

	@Override
	public void update(Object source, Object arg) {
		if (controller != null && arg instanceof EdeScanProgressBean) {
			EdeScanProgressBean progress = (EdeScanProgressBean) arg;
			if (source.equals(i0DarkScan)) {
				energyData = new DoubleDataset(theDetector.getEnergyForChannels());
				i0DarkData = EdeAsciiFileWriter.extractDetectorDataSets(theDetector.getName(), i0DarkScan, 0);
				controller.update(i0DarkScan, new EdeExperimentProgressBean(ExperimentCollectionType.SINGLE, progress,
						EdeExperiment.I0_DARK_COLUMN_NAME, i0DarkData, energyData));
			}
			if (source.equals(itDarkScan)) {
				itDarkData = EdeAsciiFileWriter.extractDetectorDataSets(theDetector.getName(), itDarkScan, 0);
				controller.update(itDarkScan, new EdeExperimentProgressBean(ExperimentCollectionType.SINGLE, progress,
						EdeExperiment.IT_DARK_COLUMN_NAME, itDarkData, energyData));
			}
			if (source.equals(i0InitialScan)) {
				i0Data = EdeAsciiFileWriter.extractDetectorDataSets(theDetector.getName(), i0InitialScan, 0);
				i0Data = i0Data.isubtract(i0DarkData);
				controller.update(i0InitialScan, new EdeExperimentProgressBean(ExperimentCollectionType.SINGLE, progress,
						EdeExperiment.I0_CORR_COLUMN_NAME, i0Data, energyData));
			}
			if (source.equals(itScan)) {
				itData = EdeAsciiFileWriter.extractDetectorDataSets(theDetector.getName(), itScan, 0);
				if (runItDark) {
					itData = itData.isubtract(itDarkData);
				} else {
					itData = itData.isubtract(i0DarkData);
				}
				controller.update(itScan, new EdeExperimentProgressBean(ExperimentCollectionType.SINGLE, progress, EdeExperiment.IT_CORR_COLUMN_NAME,
						itData, energyData));
				DoubleDataset normalisedIt = EdeAsciiFileWriter.normaliseDatasset(itData, i0Data);
				controller.update(itScan, new EdeExperimentProgressBean(ExperimentCollectionType.SINGLE, progress, EdeExperiment.LN_I0_IT_COLUMN_NAME,
						normalisedIt, energyData));
			}
		}
	}

	private void runScans() throws Exception {

		i0DarkScan = new EdeScan(i0ScanParameters, i0Position, EdeScanType.DARK, theDetector, 1, shutter2);
		i0DarkScan.setProgressUpdater(this);

		if (runItDark) {
			itDarkScan = new EdeScan(itScanParameters, itPosition, EdeScanType.DARK, theDetector, 1, shutter2);
		} else {
			itDarkScan = i0DarkScan;
		}
		itDarkScan.setProgressUpdater(this);

		i0InitialScan = new EdeScan(i0ScanParameters, i0Position, EdeScanType.LIGHT, theDetector, 1, shutter2);
		i0InitialScan.setProgressUpdater(this);

		itScan = new EdeScan(itScanParameters, itPosition, EdeScanType.LIGHT, theDetector, 1, shutter2);
		itScan.setProgressUpdater(this);

		List<ScanBase> theScans = new Vector<ScanBase>();
		theScans.add(i0DarkScan);
		if (runItDark) {
			theScans.add(itDarkScan);
		}
		theScans.add(i0InitialScan);
		theScans.add(itScan);

		try {
			addDetectorSettingsToMetadata();

			ScanPlotSettings plotNothing = new ScanPlotSettings();
			plotNothing.setUnlistedColumnBehaviour(ScanPlotSettings.IGNORE);
			plotNothing.setYAxesShown(new String[]{});
			plotNothing.setYAxesNotShown(new String[]{});

			MultiScan theScan = new MultiScan(theScans);
			theScan.setScanPlotSettings(plotNothing);theScan.setScanPlotSettings(plotNothing);
			pauseForToup();
			logger.debug("EDE single experiment starting its multiscan...");
			theScan.runScan();
		} finally {
			NexusExtraMetadataDataWriter.removeAllMetadataEntries();
		}
	}

	private void addDetectorSettingsToMetadata() {
		String header = "i0Dark: " + i0DarkScan.getHeaderDescription() + "\n";
		if (runItDark) {
			header += "itDark: " + itDarkScan.getHeaderDescription() + "\n";
		}
		header += "i0InitialScan: " + i0InitialScan.getHeaderDescription() + "\n";
		header += "itScan: " + itScan.getHeaderDescription() + "\n";

		NexusFileMetadata metadata = new NexusFileMetadata(theDetector.getName() + "_settings", header, EntryTypes.NXinstrument,
				NXinstrumentSubTypes.NXdetector, theDetector.getName()+ "_settings");
		NexusExtraMetadataDataWriter.addMetadataEntry(metadata);
	}

	private void pauseForToup() throws Exception {
		Double predictedExperimentTime = new SingleExperimentTimeEstimator(itScanParameters, i0Position, itPosition)
		.getTotalDuration();
		TopupChecker topup = createTopupChecker(predictedExperimentTime);
		topup.atScanStart();
	}
}
