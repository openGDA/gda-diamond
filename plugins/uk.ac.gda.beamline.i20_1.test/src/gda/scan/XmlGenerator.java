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

package gda.scan;

import java.util.Map;
import java.util.Map.Entry;

/**
 * Generate 'correct' TurboXasParameter XML files - for use in unit tests
 * to validate XML serialization.
 */
public class XmlGenerator {

	private static final String XML_HEADER = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";

	private boolean objectIncludesClass = false;

	public XmlGenerator(){
		// No initialisation needed
	}

	public static String getParameterString(TurboXasParameters params) {
		XmlGenerator gen = new XmlGenerator();
		return gen.getCorrectXmlString(params);
	}

	/**
	 * Return string with serialized version of TurboXasParameters object
	 * @return XML string
	 */
	public String getCorrectXmlString(TurboXasParameters parameters) {
		StringBuilder serializedXmlString = new StringBuilder();
		serializedXmlString.append(XML_HEADER);
		serializedXmlString.append("<TurboXasParameters>\n" +
				getXmlTagLine("sampleName", parameters.getSampleName(), 1) +
				getXmlTagLine("startEnergy", parameters.getStartEnergy()) +
				getXmlTagLine("endEnergy", parameters.getEndEnergy()) +
				getXmlTagLine("energyStep", parameters.getEnergyStep()) +
				getXmlTagLine("startPosition", parameters.getStartPosition()) +
				getXmlTagLine("endPosition", parameters.getEndPosition()) +
				getXmlTagLine("positionStepSize", parameters.getPositionStepSize()) +
				getXmlTagLine("usePositionsForScan", Boolean.toString(parameters.isUsePositionsForScan()), 1) +
				getXmlTagLine("energyCalibrationPolynomial", parameters.getEnergyCalibrationPolynomial(), 1) +
				getXmlTagLine("energyCalibrationMinPosition", parameters.getEnergyCalibrationMinPosition()) +
				getXmlTagLine("energyCalibrationMaxPosition", parameters.getEnergyCalibrationMaxPosition()) +
				getXmlTagLine("energyCalibrationReferenceFile", parameters.getEnergyCalibrationReferenceFile(), 1) +
				getXmlTagLine("energyCalibrationFile", parameters.getEnergyCalibrationFile(), 1) +
				getXmlTagLine("motorToMove", parameters.getMotorToMove(), 1));

		// Add the detector(s)
		serializedXmlString.append("  <detectors>\n");
		for(String detectorName : parameters.getDetectors()) {
			serializedXmlString.append(getXmlTagLine("string", detectorName, 2));
		}
		serializedXmlString.append("  </detectors>\n");

		serializedXmlString.append(getXmlTagLine("useTrajectoryScan", Boolean.toString(parameters.getUseTrajectoryScan()), 1));
		serializedXmlString.append(getXmlTagLine("twoWayScan", Boolean.toString(parameters.isTwoWayScan()), 1));

		// Add the timing groups
		if (parameters.getTimingGroups() != null) {
			parameters.getTimingGroups().forEach( timingGroup -> {
				serializedXmlString.append("  <TimingGroup>\n");
				serializedXmlString.append(getXmlTagLine("name", timingGroup.getName(), 2));
				serializedXmlString.append(getXmlTagLine("timePerSpectrum", timingGroup.getTimePerSpectrum(), 2));
				serializedXmlString.append(getXmlTagLine("timeBetweenSpectra", timingGroup.getTimeBetweenSpectra(), 2));
				serializedXmlString.append(getXmlTagLine("numSpectra", Integer.toString(timingGroup.getNumSpectra()), 2));
				serializedXmlString.append("  </TimingGroup>\n");
			});
		}

		if (parameters.getScannablesToMonitorDuringScan() != null) {
			serializedXmlString.append(getExpectedMapXmlString(parameters.getScannablesToMonitorDuringScan(), "  ")+"\n");
		}

		if (parameters.getExtraScannables() != null) {
			serializedXmlString.append("  <extraScannables>\n");
			parameters.getExtraScannables().forEach((name) -> serializedXmlString.append(getXmlTagLine("string", name, 2)));
			serializedXmlString.append("  </extraScannables>\n");
		}

		if (parameters.getNamesOfDatasetsToAverage() != null) {
			serializedXmlString.append("  <namesOfDatasetsToAverage>\n");
			parameters.getNamesOfDatasetsToAverage().forEach((name) -> serializedXmlString.append(getXmlTagLine("string", name, 2)) );
			serializedXmlString.append("  </namesOfDatasetsToAverage>\n");
		}

		serializedXmlString.append(getXmlTagLine("writeAsciiData", Boolean.toString(parameters.getWriteAsciiData()), 1));
		serializedXmlString.append(getXmlTagLine("fastShutterName", parameters.getFastShutterName(), 1));

		serializedXmlString.append(getXmlTagLine("runMappingScan", Boolean.toString(parameters.isRunMappingScan()), 1));
		if (parameters.getScannableToMove() != null && parameters.getScannablePositions() != null) {
			serializedXmlString.append(getXmlTagLine("scannableToMove", parameters.getScannableToMove(), 1));
			serializedXmlString.append("  <scannablePositions>\n");
			parameters.getScannablePositions().forEach(positions -> {
				serializedXmlString.append("    <list>\n");
				for(Double val : positions) {
					serializedXmlString.append(getXmlTagLine("double", val.toString(), 3));
				}
				serializedXmlString.append("    </list>\n");

			});
			serializedXmlString.append("  </scannablePositions>\n");
		}

		if (parameters.getSpectrumEvents() != null && !parameters.getSpectrumEvents().isEmpty()) {
			serializedXmlString.append("  <spectrumEvents>\n");
			for(SpectrumEvent event : parameters.getSpectrumEvents()) {
				serializedXmlString.append("    <SpectrumEvent>\n");
				serializedXmlString.append(getXmlTagLine("spectrumNumber", Integer.toString(event.getSpectrumNumber()), 3));
				serializedXmlString.append(getXmlTagLine("scannableName", event.getScannableName(), 3));

				Object pos = event.getPosition();
				String objectString = objectIncludesClass ?  " class=\""+pos.getClass().getSimpleName().toLowerCase()+"\"" : "";
				serializedXmlString.append("      <position"+objectString+">"+pos+"</position>\n");
				serializedXmlString.append("    </SpectrumEvent>\n");
			}
			serializedXmlString.append("  </spectrumEvents>\n");
		}
		serializedXmlString.append("</TurboXasParameters>\n");

		return serializedXmlString.toString();
	}

	public String getExpectedMapXmlString(Map<String, String> map) {
		return getExpectedMapXmlString(map, "");
	}

	public String getExpectedMapXmlString(Map<String, String> map, String prefix) {
		String xmlString = prefix+"<scannablesToMonitorDuringScan>\n";

		String keyName = "scannableName";
		String valueName = "pv";

		for(Entry item : map.entrySet()) {
			xmlString += String.format("%s  <%s>%s</%s>\n", prefix, keyName, item.getKey(), keyName);
			xmlString += String.format("%s  <%s>%s</%s>\n", prefix, valueName, item.getValue(), valueName);
		}
		xmlString += prefix+"</scannablesToMonitorDuringScan>";
		return xmlString;
	}

	private String getXmlTagLine(String tag, String value, int indent) {
		StringBuilder sb = new StringBuilder();
		sb.append("<" + tag + ">");
		sb.append(value);
		sb.append("</" + tag + ">\n");
		return getIndent(indent)+sb.toString();
	}

	private String getXmlTagLine(String tag, double value) {
		return getXmlTagLine(tag, doubleToString(value), 1);
	}

	private String getXmlTagLine(String tag, double value, int level) {
		return getXmlTagLine(tag, doubleToString(value), level);
	}
	private String getIndent(int indent) {
		StringBuilder sb = new StringBuilder();
		while (indent-- > 0) {
			sb.append("  ");
		}
		return sb.toString();
	}

	public boolean isObjectIncludesClass() {
		return objectIncludesClass;
	}

	public void setObjectIncludesClass(boolean objectIncludesClass) {
		this.objectIncludesClass = objectIncludesClass;
	}

	public static String doubleToString( double doubleVal ) {
		return Double.toString(doubleVal);
	}

}
