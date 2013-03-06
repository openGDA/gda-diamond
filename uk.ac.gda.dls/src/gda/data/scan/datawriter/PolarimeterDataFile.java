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

package gda.data.scan.datawriter;

import gda.factory.Finder;
import gda.oe.MoveableException;
import gda.oe.OE;
import gda.scan.IScanDataPoint;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Vector;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * An extension of IncrementalFile class which produces ascii files specifically for the joint DL/DLS polarimeter. It
 * uses the reference of the scan which cre.ated this datahandler to determine which columns to have in the output. The
 * header information contains the time and date, the postion of all scannables plus a title and comment field.
 */
public class PolarimeterDataFile extends IncrementalFile {
	private static final Logger logger = LoggerFactory.getLogger(PolarimeterDataFile.class);

	// the columns of interest (scannables and detectors)
	// Vector columns = new Vector();

	/**
	 * Constructor
	 * 
	 * @throws InstantiationException
	 */
	public PolarimeterDataFile() throws InstantiationException {
		super();

		logger.debug("Finding: retarder");
		if ((retarder = (OE) Finder.getInstance().find("Retarder")) == null) {
			logger.error("Polarimeter Data File: Retarder not found");
		}
		logger.debug("Finding: analyser");
		if ((analyser = (OE) Finder.getInstance().find("Analyser")) == null) {
			logger.error("Polarimeter Data File: Analyser not found");
		}
		logger.debug("Finding: front pinhole");
		if ((frontPinhole = (OE) Finder.getInstance().find("FrontPinhole")) == null) {
			logger.error("Polarimeter Data File: FrontPinhole not found");
		}
		logger.debug("Finding: rear pinhole");
		if ((rearPinhole = (OE) Finder.getInstance().find("RearPinhole")) == null) {
			logger.error("Polarimeter Data File: RearPinhole not found");
		}
	}

	IScanDataPoint latestPoint;
	private OE retarder;
	private OE analyser;
	private OE frontPinhole;
	private OE rearPinhole;

	/**
	 * for incremental addition of data.
	 * <P>
	 * data should be in the form of a double array. This data will be tab separated, terminated with an "\n", and
	 * appended to the open file.
	 * 
	 * @param dataPoint
	 *            Object
	 * @throws Exception 
	 */
	@Override
	public void addData(IScanDataPoint dataPoint) throws Exception {
		latestPoint = dataPoint;
		if (firstData) {
			this.prepareForCollection();
			firstData = false;
		}

		try {
			// Build output string from positions and data in case
			// data has been modified i.e. don't use toString()
			String outputString = "";
			Vector<Object> positions = dataPoint.getPositions();
			for (int i = 0; i < positions.size(); i++) {
				outputString += positions.elementAt(i) + delimiter;
			}
			Vector<Object> data = dataPoint.getDetectorData();
			if (data.size() != 0) {
				double[] dataValues = (double[]) data.elementAt(0);
				for (int i = 0; i < dataValues.length; i++) {
					outputString += Double.toString(dataValues[i]) + delimiter;
				}
			}
			file.write(outputString + "\n");
			file.flush();
		} catch (Exception ex) {
			logger.debug(ex.getStackTrace().toString());
		}
	}

	@Override
	public void prepareForCollection() throws Exception {
		createNextFile();
		writeHeader();
	}

	@Override
	public void setHeader(String header) {
		this.header = new ArrayList<String>();
		for (int i = 0; i < 4; i++) {
			this.header.add("");
		}
		this.header.add(header);
	}

	@Override
	public void writeHeader() {
		try {
			// get relevent info and print to 'file'
			// get file name and datetime
			Calendar rightNow = Calendar.getInstance();
			int year = rightNow.get(Calendar.YEAR);
			int month = rightNow.get(Calendar.MONTH);
			int day = rightNow.get(Calendar.DAY_OF_MONTH);
			int hour = rightNow.get(Calendar.HOUR);
			int minute = rightNow.get(Calendar.MINUTE);
			int second = rightNow.get(Calendar.SECOND);
			// write datetime
			long fileNumber=0;
			try {
				fileNumber = getFileNumber();
			} catch (Exception e) {
				logger.error("Error getting fileNumber", e);
			}
			String line = " File number = " + fileNumber + "\n Date = " + String.valueOf(day) + "/"
					+ String.valueOf(month) + "/" + String.valueOf(year) + "\n" + " Time = " + String.valueOf(hour)
					+ ":" + String.valueOf(minute) + ":" + String.valueOf(second) + "\n";
			file.write(line);

			// add extra header information if a header has been added through the
			// setHeader() method.
			if (header == null) {
				file.write(" Title = \n");
				file.write(" Comment = \n");
			} else {
				file.write(" Title = " + header.get(0) + "\n");
				file.write(" Comment = " + header.get(1) + "\n");
			}
			// Write names and current positions of all scanables
			try {
				// README These hard coded DOF names need to stay for the moment until
				// a solution can be found that can get at relavent DOF names without
				// being requiring lists of Strings that need hand editing in XML.
				file.write(" Retarder rotation = " + retarder.getPosition("RetRotation").toString() + "\n");
				file.write(" Retarder tilt = " + retarder.getPosition("RetTilt").toString() + "\n");
				file.write(" Analyser rotation = " + analyser.getPosition("AnaRotation").toString() + "\n");
				file.write(" Analyser tilt = " + analyser.getPosition("AnaTilt").toString() + "\n");
				file.write(" Analyser detector = " + analyser.getPosition("AnaDetector").toString() + "\n");
				file.write(" Analyser translation = " + analyser.getPosition("AnaTranslation").toString() + "\n");
				file.write(" Front pinhole = " + frontPinhole.getPosition("FPSelection").toString() + "\n");
				file.write(" Rear pinhole = " + rearPinhole.getPosition("RPSelection").toString() + "\n");
			} catch (MoveableException ex) {
				logger.error("Unable to include polarimeter positions in output file " + ex.getMessage());
			}

			// now write the column headings
			line = latestPoint.getHeaderString();
			file.write(line + "\n");
		} catch (IOException ex) {
			logger.error("Error when writing PolarimeterDataFile header: " + ex.getMessage());
		}

	}

	@Override
	public void writeFooter() {
	}

	/**
	 * For addition of single line strings to the datafile
	 * 
	 * @param line
	 */
	public void writeLine(String line) {
		try {
			file.write(line + "\n");
			file.flush();
		} catch (IOException ex) {
			logger.error("Error when writing PolarimeterDataFile line: " + ex.getMessage());
		}

	}

	@Override
	public String getCurrentScanIdentifier() {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public void writeColumnHeadings() {
		// TODO Auto-generated method stub

	}

}
