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

package uk.ac.gda.beamline.i20_1.utils;

import uk.ac.gda.exafs.data.ClientConfig;


public class DataHelper {

	private DataHelper() {}

	public static String toString(double[] value) {
		return DataHelper.toString(value, ',');
	}

	public static String toString(double[] value, char delimiter) {
		StringBuilder stringBuilder = new StringBuilder();
		if (value.length > 0) {
			for (double selected : value) {
				stringBuilder.append(selected);
				stringBuilder.append(delimiter);
			}
			removeLastChar(stringBuilder);
		}
		return stringBuilder.toString();
	}

	public static <T> String toString(T[] value) {
		return DataHelper.toString(value, ',');
	}

	public static <T> String toString(T[] value, char delimiter) {
		StringBuilder stringBuilder = new StringBuilder();
		if (value.length > 0) {
			for (T selected : value) {
				stringBuilder.append(selected);
				stringBuilder.append(delimiter);
			}
			removeLastChar(stringBuilder);
		}
		return stringBuilder.toString();
	}

	public static String toString(int[] value) {
		StringBuilder stringBuilder = new StringBuilder();
		if (value.length > 0) {
			for (int selected : value) {
				stringBuilder.append(selected);
				stringBuilder.append(",");
			}
			removeLastChar(stringBuilder);
		}
		return stringBuilder.toString();
	}

	public static int[] toArray(String commaSepString) throws NumberFormatException {
		String[] strValues = commaSepString.split(",");
		int[] values = new int[strValues.length];
		for (int i = 0; i < strValues.length; i++) {
			values[i] = Integer.parseInt(strValues[i]);
		}
		return values;
	}

	public static StringBuilder removeLastChar(StringBuilder stringBuilder) {
		return stringBuilder.delete(stringBuilder.length() - 1, stringBuilder.length());
	}

	public static int getDecimalPlacePowValue(int decimalPlace) {
		return (int) Math.pow(10, decimalPlace);
	}

	public static String roundDoubletoString(double value) {
		return String.format("%." + ClientConfig.DEFAULT_DECIMAL_PLACE + "f", value);
	}

	public static String roundDoubletoStringWithOptionalDigits(double value) {
		return ClientConfig.DECIMAL_FORMAT.format(value);
	}

	public static String roundDoubletoString(double value, int decimalPlaces) {
		return String.format("%." + decimalPlaces + "f", value);
	}

	public static double roundDouble(double value) {
		int defaultDecimal = DataHelper.getDecimalPlacePowValue(ClientConfig.DEFAULT_DECIMAL_PLACE);
		return Math.round(value * defaultDecimal) / (double) defaultDecimal;
	}
}
