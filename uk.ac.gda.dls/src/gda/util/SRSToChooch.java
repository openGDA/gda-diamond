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

package gda.util;

import gda.gui.exafs.Converter;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.text.DecimalFormat;
import java.text.NumberFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.GregorianCalendar;
import java.util.StringTokenizer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Converts SRS format data files to files suitable for Chooch by the now traditional BFI method (no checking of
 * arguments, catching of file format errors or similar).
 */
public class SRSToChooch {
	private static final Logger logger = LoggerFactory.getLogger(SRSToChooch.class);

	private SimpleDateFormat sdf = new SimpleDateFormat("dd MMM yyyy HH:mm:ss");

	private DecimalFormat df = (DecimalFormat) NumberFormat.getInstance();

	private Calendar now;

	private String outDelimiter = " ";

	/**
	 * Constructor.
	 * 
	 * @param inputFileName
	 * @param outputFileName
	 * @param twoD
	 */
	public SRSToChooch(String inputFileName, String outputFileName, double twoD) {
		String line;
		double[] values;
		double iftot;
		double energy;
		double wavelength;
		df.setMaximumFractionDigits(6);
		df.setGroupingUsed(false);

		Converter.setTwoD(twoD);
		try {
			now = new GregorianCalendar();
			BufferedReader in = new BufferedReader(new FileReader(inputFileName));
			BufferedWriter out = new BufferedWriter(new FileWriter(outputFileName));

			// Write new header
			out.write("# Start of xafs scan - " + inputFileName + " converted " + sdf.format(now.getTime()) + "\n\n");
			out.write("# mDegrees I0 If If/I0  Angstroms eVolts \n");

			// Ignore old header
			do {
				line = in.readLine();
			} while (line.indexOf("&END") == -1);

			// Ignore blank line and column titles line
			line = in.readLine();
			line = in.readLine();

			while ((line = in.readLine()) != null) {
				values = stringToArray(line);
				iftot = values[5] + values[6] + values[7] + values[8];
				energy = Converter.convert(values[0], Converter.MDEG, Converter.EV);
				wavelength = Converter.convert(values[0], Converter.MDEG, Converter.ANGSTROM);
				out.write(" " + values[0] + outDelimiter + values[4] + outDelimiter + iftot + outDelimiter
						+ df.format(iftot / values[4]) + outDelimiter + df.format(wavelength) + outDelimiter
						+ df.format(energy) + "\n");
			}

			out.write("# End of xafs scan - " + inputFileName + " converted " + sdf.format(now.getTime()) + "\n");
			in.close();
			out.close();

		} catch (FileNotFoundException e) {
			logger.debug(e.getStackTrace().toString());
		} catch (IOException e) {
			logger.debug(e.getStackTrace().toString());
		}

	}

	private double[] stringToArray(String string) {
		StringTokenizer strtok = new StringTokenizer(string, "\t");
		double[] values = new double[strtok.countTokens()];
		int counter = 0;
		while (strtok.hasMoreTokens()) {
			values[counter] = Double.valueOf(strtok.nextToken()).doubleValue();
			counter++;
		}
		return values;
	}

	/**
	 * Main method.
	 * 
	 * @param args
	 */
	@SuppressWarnings("unused")
	public static void main(String[] args) {
		new SRSToChooch(args[0], args[1], 6.271);
	}
}
