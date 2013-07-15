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

package gda.scan;

import gda.data.nexus.extractor.NexusExtractor;
import gda.data.nexus.extractor.NexusGroupData;
import gda.data.scan.datawriter.DataWriter;
import gda.data.scan.datawriter.NexusDataWriter;
import gda.device.detector.NXDetectorData;
import gda.device.detector.StripDetector;

import java.io.File;
import java.io.FileWriter;
import java.util.List;
import java.util.Vector;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;

/**
 * The simplest EDE experiment type: collect Dark I0, Dark It, I0,It,I0, do corrections and calculate derived data.
 * Record data to Nexus while collection in progress, write to a custom Ascii format on completion.
 * <p>
 * The I0 timing is the same as the It timing parameters, not explicitly supplied instead. So only a single time frame
 * and timing group must be supplied.  Sample environments are not taken into account here.
 * <p>
 * TODO: need to include detector calibration control somewhere in this.
 */
public class EdeSingleExperiment {

	EdeScan i0DarkScan;
	EdeScan itDarkScan;
	EdeScan i0InitialScan;
	EdeScan itScan;
	EdeScan i0FinalScan;

	EdeScanPosition i0Position;
	EdeScanPosition itPosition;
	EdeScanParameters itScanParameters;

	DataWriter inProgressDataWriter;
	EdeDataWriter asciiDataWriter;
	private StripDetector theDetector;

	public EdeSingleExperiment(EdeScanParameters itScanParameters, EdeScanPosition i0Position,
			EdeScanPosition itPosition, StripDetector theDetector) {
		super();
		this.i0Position = i0Position;
		this.itPosition = itPosition;
		this.itScanParameters = itScanParameters;
		this.theDetector = theDetector;
		validateTimingParameters();
	}

	private void validateTimingParameters() {
		if (itScanParameters.getGroups().size() != 1){
			throw new IllegalArgumentException("Only one timing group must be used in this type of scan!");
		}
		if (itScanParameters.getGroups().get(0).getNumberOfFrames() != 1){ 
			throw new IllegalArgumentException("Only one frame must be used in this type of scan!");
		}
	}

	public void runExperiment() throws Exception {
		createDataWriters();
		generateSubScans();
		runScans();
		writeAsciiFile();
	}

	private void createDataWriters() {
		// has to be Nexus here to store the data properly
		inProgressDataWriter = new NexusDataWriter();
		asciiDataWriter = new EdeDataWriter();
	}

	private void generateSubScans() {
		i0DarkScan = new EdeScan(itScanParameters, i0Position, EdeScanType.DARK, inProgressDataWriter, theDetector);
		itDarkScan = new EdeScan(itScanParameters, itPosition, EdeScanType.DARK, inProgressDataWriter, theDetector);
		i0InitialScan = new EdeScan(itScanParameters, i0Position, EdeScanType.LIGHT, inProgressDataWriter, theDetector);
		itScan = new EdeScan(itScanParameters, itPosition, EdeScanType.LIGHT, inProgressDataWriter, theDetector);
		i0FinalScan = new EdeScan(itScanParameters, i0Position, EdeScanType.LIGHT, inProgressDataWriter, theDetector);
	}

	private void runScans() throws Exception {
		i0DarkScan.runScan();
		itDarkScan.runScan();
		i0InitialScan.runScan();
		itScan.runScan();
		i0FinalScan.runScan();
	}

	private void writeAsciiFile() throws Exception {
		DoubleDataset i0DarkDataSet = extractDetectorDataSets(i0DarkScan);
		DoubleDataset itDarkDataSet = extractDetectorDataSets(itDarkScan);
		DoubleDataset i0InitialDataSet = extractDetectorDataSets(i0InitialScan);
		DoubleDataset itDataSet = extractDetectorDataSets(itScan);
		DoubleDataset i0FinalDataSet = extractDetectorDataSets(i0FinalScan);
		
		String nexusFilename = inProgressDataWriter.getCurrentFileName();
		String nexusFileNumber = inProgressDataWriter.getCurrentScanIdentifier();
		
		String folderName = org.apache.commons.io.FilenameUtils.getFullPath(nexusFilename);
		String asciiFilename = folderName + nexusFileNumber + ".txt";
		
		File asciiFile = new File(asciiFilename);
		if (asciiFile.exists()){
			throw new Exception("File " + asciiFilename + " already exists!");
		}
		
		asciiFile.createNewFile();
		FileWriter writer = new FileWriter(asciiFile);
		writer.write("Strip #\tI0_corr\tIt_corr\tLn(I0/It)\tI0_dark\tIt_dark\tI0_raw\tIt_raw\n");
		for (int channel = 0; channel < theDetector.getNumberChannels(); channel++){
			Double i0DK = i0DarkDataSet.get(channel);
			Double itDK = itDarkDataSet.get(channel);
			Double i0Initial = i0InitialDataSet.get(channel);
			Double it = itDataSet.get(channel);
			Double i0Final = i0FinalDataSet.get(channel);
			
			Double i0_corrected = i0Initial - i0DK;
			Double it_corrected = it - itDK;
			Double lni0it = Math.log(i0_corrected/it_corrected);
			
		    StringBuffer stringToWrite = new StringBuffer(channel+"\t");
		    stringToWrite.append(String.format( "%.2f",i0_corrected) +"\t");
		    stringToWrite.append(String.format( "%.2f",it_corrected) +"\t");
		    stringToWrite.append(String.format( "%.5f",lni0it) +"\t");
		    stringToWrite.append(String.format( "%.2f",i0DK) +"\t");
		    stringToWrite.append(String.format( "%.2f",itDK) +"\t");
		    stringToWrite.append(String.format( "%.2f",i0Initial) +"\t");
		    stringToWrite.append(String.format( "%.2f",it) +"\t");
		    writer.write(stringToWrite.toString());
		}
		writer.close();
	}

	private DoubleDataset extractDetectorDataSets(EdeScan scan) {
		List<ScanDataPoint> sdps = scan.getData();
		Vector<Object> data = sdps.get(0).getDetectorData();
		int detIndex = getIndexOfMyDetector(sdps.get(0));
		NXDetectorData detData = (NXDetectorData) data.get(detIndex);
		NexusGroupData groupData = detData.getData(theDetector.getName(), null, NexusExtractor.SDSClassName);
		double[] originalData = (double[]) groupData.getBuffer();
		return new DoubleDataset(originalData,originalData.length);
	}

	private int getIndexOfMyDetector(ScanDataPoint scanDataPoint) {
		Vector<String> names = scanDataPoint.getDetectorNames();
		return names.indexOf(theDetector.getName());
	}
}
