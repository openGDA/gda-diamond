/*-
 * Copyright © 2022 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i14.views.beamlinereadiness;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.function.Consumer;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class CsvReader {

	private static final Logger logger = LoggerFactory.getLogger(CsvReader.class);

	private CsvReader() {
	}

	public static void processCsvFile(String csvFilePath, String key, String value, Consumer<CSVRecord> consumer) {

		CSVFormat csvFormat = CSVFormat.DEFAULT
				.withHeader(key, value)
				.withSkipHeaderRecord()
				.withIgnoreSurroundingSpaces(true);

		try (FileReader fileReader = new FileReader(csvFilePath);
				BufferedReader bufferedReader = new BufferedReader(fileReader)) {
				CSVParser csvParser = CSVParser.parse(bufferedReader, csvFormat);

				for (CSVRecord row : csvParser) {
					consumer.accept(row);
				}

		} catch (NumberFormatException e) {
			logger.error("Found non-numeric numbers in target intensities lookup table", e);
		} catch (FileNotFoundException e) {
			logger.error("CSV file not found", e);
		} catch (IOException e) {
			logger.error("Error reading CSV file", e);
		}
	}
}
