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

package gda.scan.ede.datawriters;

import gda.data.nexus.extractor.NexusExtractor;
import gda.data.nexus.extractor.NexusGroupData;
import gda.device.detector.NXDetectorData;
import gda.device.detector.StripDetector;
import gda.jython.InterfaceProvider;
import gda.scan.EdeScan;
import gda.scan.ScanDataPoint;

import java.util.List;
import java.util.Vector;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;

public abstract class EdeAsciiFileWriter {

	public static DoubleDataset extractDetectorDataSets(String detectorName, EdeScan scan, int spectrumIndex) {
		List<ScanDataPoint> sdps = scan.getData();
		return extractDetectorDataFromSDP(detectorName, sdps.get(spectrumIndex));
	}

	public static DoubleDataset extractDetectorDataFromSDP(String detectorName, ScanDataPoint sdp) {
		Vector<Object> data = sdp.getDetectorData();
		int detIndex = getIndexOfMyDetector(detectorName, sdp);
		NXDetectorData detData = (NXDetectorData) data.get(detIndex);
		NexusGroupData groupData = detData.getData(detectorName, "data", NexusExtractor.SDSClassName);
		double[] originalData = (double[]) groupData.getBuffer();
		return new DoubleDataset(originalData, originalData.length);
	}

	public static int getIndexOfMyDetector(String detectorName, ScanDataPoint scanDataPoint) {
		Vector<String> names = scanDataPoint.getDetectorNames();
		return names.indexOf(detectorName);
	}

	public static Double calcLnI0It(Double i0_corrected, Double it_corrected) {
		Double lni0it = Math.log(i0_corrected / it_corrected);
		if (lni0it.isNaN() || lni0it.isInfinite() || lni0it < 0.0) {
			lni0it = .0;
		}
		return lni0it;
	}

	public static DoubleDataset normaliseDatasset(DoubleDataset itRaw, DoubleDataset i0Raw, DoubleDataset dark) {

		double[] itRawArray = itRaw.getData();
		double[] i0RawArray = i0Raw.getData();
		double[] darkArray = dark.getData();

		double[] itNormaliseArray = new double[itRawArray.length];

		for (int channel = 0; channel < itNormaliseArray.length; channel++) {
			itNormaliseArray[channel] = calcLnI0It(i0RawArray[channel]-darkArray[channel],itRawArray[channel]-darkArray[channel]);
		}

		return new DoubleDataset(itNormaliseArray,itNormaliseArray.length);
	}

	public static final String TIMINGGROUP_COLUMN_NAME = "Timing_Group";
	public static final String STRIP_COLUMN_NAME = "Strip";
	public static final String ENERGY_COLUMN_NAME = "Energy";
	public static final String I0_CORR_COLUMN_NAME = "I0_corr";
	public static final String IT_CORR_COLUMN_NAME = "It_corr";
	public static final String LN_I0_IT_COLUMN_NAME = "LnI0It";
	public static final String I0_RAW_COLUMN_NAME = "I0_raw";
	public static final String IT_RAW_COLUMN_NAME = "It_raw";
	public static final String I0_DARK_COLUMN_NAME = "I0_dark";
	public static final String IT_DARK_COLUMN_NAME = "It_dark";

	private static final Logger logger = LoggerFactory.getLogger(EdeAsciiFileWriter.class);

	protected String filenameTemplate = "";
	protected StripDetector theDetector;

	/**
	 * Write out the ascii file of derived data based on the data collected.
	 * 
	 * @return the full path of the ascii file
	 * @throws Exception
	 */
	public abstract String writeAsciiFile() throws Exception;

	public String getFilenameTemplate() {
		return filenameTemplate;
	}

	/**
	 * A String format for the name of the ascii file to be written.
	 * <p>
	 * It <b>must</b> contain a '%s' to substitute the nexus file name into the given template.
	 * <p>
	 * E.g. if the nexus file created was: '/dls/i01/data/1234.nxs' then the filenameTemplate given in this method
	 * should be something like: 'Fe-Kedge_%s' for the final ascii file to be: '/dls/i01/data/Fe-Kedge_1234.txt'
	 * 
	 * @param filenameTemplate
	 */
	public void setFilenameTemplate(String filenameTemplate) {
		this.filenameTemplate = filenameTemplate;
	}

	protected void log(String message) {
		InterfaceProvider.getTerminalPrinter().print(message);
		logger.info(message);
	}
}
