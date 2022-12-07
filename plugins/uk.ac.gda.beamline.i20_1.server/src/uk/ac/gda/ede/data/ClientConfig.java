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

package uk.ac.gda.ede.data;

import java.text.DecimalFormat;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class ClientConfig {

	public static final int KILO_UNIT = 1000;
	public static final int DEFAULT_DECIMAL_PLACE = 5;
	public static final DecimalFormat DECIMAL_FORMAT = new DecimalFormat("#.#########");
	public static final String DEFAULT_DATA_PATH = "/dls/i20-1/data";
	public static final String EDE_GUI_DATA = "ede_gui.properties";
	
	public static final String ALIGNMENT_PARAMETERS_RESULT_BEAN_NAME = "beamlinealignmentresults";

	private ClientConfig() {}

	public enum UnitSetup {
		MILLI_METER("mm"),
		MILLI_RADIAN("mrad"),
		DEGREE("deg"),
		WATT("W"),
		EV("eV"),
		VOLTAGE("V"),
		MILLI_SEC("ms"),
		MICRO_SEC("μs"),
		NANO_SEC("ns"),
		SEC("s"),
		HOUR("h"),
		MINUTE("min"),
		TESLA("T"),
		PIXEL("pixel"),

		SELECTION("");

		private final String text;

		private UnitSetup(String text) {
			this.text = text;
		}

		public String getText() {
			return text;
		}

		public String addUnitSuffix(String value) {
			if (!value.isEmpty()) {
				return String.format("%s %s", value, text);
			}
			return value;
		}

		public String addUnitSuffixForLabel(String value) {
			if (!value.isEmpty()) {
				return String.format("%s (%s): ", value, text);
			}
			return String.format("(%s): ", text);
		}

		public String removeUnitSuffix(String value) throws Exception {
			if (text.isEmpty() | value.isEmpty()) {
				return value.trim();
			}
			Matcher matcher = Pattern.compile("(.*)\\s" + text + "$").matcher(value);
			if (matcher.find()) {
				return matcher.group(1).trim();
			}
			throw new Exception("Unable to find Unit suffix to remove");
		}
	}
}
