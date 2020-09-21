package uk.ac.diamond.daq.beamline.k11.diffraction;

import static uk.ac.gda.client.properties.ClientPropertiesHelper.getProperty;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import gda.configuration.properties.LocalProperties;
import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;

/**
 * Hides the configuration structural design.
 *
 * <p>
 * Defining an AcquisitionTemplateType is necessary to define which scannable is associated with each
 * {@link ScannableTrackDocument}. As such the client has to configure the possible acquisitions in the property file.
 * </p>
 * A typical configuration defining an acquisition would look like below
 *
 * <pre>
 * {@code
 *	acquisition.diffraction.two_dimension_point.0.scannable = simx
 *  acquisition.diffraction.two_dimension_point.0.axis = x
 *	acquisition.diffraction.two_dimension_point.1.scannable = simy
 *	acquisition.diffraction.two_dimension_point.1.axis = y
 *
 * 	acquisition.diffraction.two_dimension_line.0.scannable = simx
 *  acquisition.diffraction.two_dimension_line.0.axis = x
 * 	acquisition.diffraction.two_dimension_line.1.scannable = simy
 * 	acquisition.diffraction.two_dimension_line.1.axis = y
 *
 * 	acquisition.diffraction.two_dimension_grid.0.scannable = simx
 *  acquisition.diffraction.two_dimension_grid.0.axis = x
 * 	acquisition.diffraction.two_dimension_grid.1.scannable = simy
 *  acquisition.diffraction.two_dimension_grid.1.axis = y
 * }
 * </pre>
 *
 * where the fields meaning represent
 *
 * <ul>
 * <li><i>acquisition.diffraction</i>
 * <ul>
 * <li>the acquisition perspective prefix</li>
 * </ul>
 * </li>
 * <li><i>two_dimension_point | two_dimension_line | two_dimension_grid</i>
 * <ul>
 * <li>a specific AcquisitionTemplateType</li>
 * </ul>
 * </li>
 * <li><i>INDEX</i>
 * <ul>
 * <li>an indexed list of axis</li>
 * </ul>
 * <li><i>INDEX.axis</i>
 * <ul>
 * <li>the name of the axis </li>
 * </ul>
 * </li>
 * <li><i>INDEX.scannable</i>
 * <ul>
 * <li>the name of the scannable for this axis</li>
 * </ul>
 * </li>
 * </ul>
 *
 * @author Maurizio Nagni
 *
 */
public final class DiffractionAcquisitionTypeProperties {

	/**
	 * Map each acquisition type to a pre-build list of scannableTrack documents
	 */
	private static final Map<AcquisitionTemplateType, List<ScannableTrackDocument>> acquisitionTemplateTypeScanables = new HashMap<>();

	static {
		parseAcquisitionTypeScannableProperties();
	}

	private DiffractionAcquisitionTypeProperties() {
	}

	/**
	 * The prefix used in the property files to identify a camera configuration.
	 */
	private static final String ACQUISITION_TYPE_CONFIGURATION_PREFIX = "acquisition.diffraction";

	private static List<String> getAcquisitionTemplateTypeKeys(String acquisitionTemplateType) {
		return LocalProperties.getKeysByRegexp(
				String.format("%s\\.%s\\.\\d.*", ACQUISITION_TYPE_CONFIGURATION_PREFIX, acquisitionTemplateType));
	}

	private static void parseAcquisitionTypeScannableProperties() {
		Arrays.stream(AcquisitionTemplateType.values())
			.forEach(DiffractionAcquisitionTypeProperties::parseAcquisitionTemplateType);
	}

	private static void parseAcquisitionTemplateType(AcquisitionTemplateType acquisitonTemplateType) {
		String name = acquisitonTemplateType.name().toLowerCase();
		List<String> elements = getAcquisitionTemplateTypeKeys(name);

		List<ScannableTrackDocument> scannableTrackDocuments = IntStream.range(0, elements.size()/2)
				.mapToObj(index -> 	parseAcquisitionTemplateType(index, name))
				.collect(Collectors.toList());
		acquisitionTemplateTypeScanables.put(acquisitonTemplateType, scannableTrackDocuments);
	}

	private static ScannableTrackDocument parseAcquisitionTemplateType(int index, String key) {
		ScannableTrackDocument.Builder builder = new ScannableTrackDocument.Builder();
		String prefix = String.format("%s.%s", ACQUISITION_TYPE_CONFIGURATION_PREFIX, key);
		 builder.withAxis(getAcquisitionTemplateAxis(index, prefix));
		 builder.withScannable(getAcquisitionTemplateScannable(index, prefix));
		return builder.build();
	}

	private static String getAcquisitionTemplateAxis(int index, String prefix) {
		return getProperty(prefix, index, "axis", null);
	}

	private static String getAcquisitionTemplateScannable(int index, String prefix) {
		return getProperty(prefix, index, "scannable", null);
	}

	/**
	 * Create a brand new list of scannableTrackDocument for the specified acquisition template type
	 * according to the parsed {@code acquisition.diffraction} configurations
	 *
	 * @param acquisitonTemplateType
	 *            the acquisition type
	 * @return a list of predefined scannableTrackDocument
	 */
	public static ScanpathDocument.Builder createScanpathDocument(AcquisitionTemplateType acquisitonTemplateType) {

		List<ScannableTrackDocument> scannableTrackDocuments =
				createScannableTrackDocuments(acquisitonTemplateType).stream()
				.map(ScannableTrackDocument.Builder::new)
				.map(builder -> {
					if (AcquisitionTemplateType.TWO_DIMENSION_POINT.equals(acquisitonTemplateType)) {
						builder.withPoints(1); // it's a point, what else?
					} else {
						builder.withPoints(5); // default points
					}
					return builder;
				})
				.map(ScannableTrackDocument.Builder::build)
				.collect(Collectors.toList());

		ScanpathDocument.Builder builder = new ScanpathDocument.Builder();
		builder.withModelDocument(acquisitonTemplateType);
		builder.withScannableTrackDocuments(scannableTrackDocuments);
		return builder;
	}

	/**
	 * Builds a set of ScannableTrackDocument exactly how specified for the DiffractionAcquisitionTypeProperties
	 * associated with the AcquisitionTemplateType
	 *
	 * @param acquisitonTemplateType
	 * @return a list of scannable track builders
	 */
	private static List<ScannableTrackDocument> createScannableTrackDocuments(AcquisitionTemplateType acquisitonTemplateType) {
		return acquisitionTemplateTypeScanables
				.get(acquisitonTemplateType).stream().map(e -> {
					ScannableTrackDocument.Builder builder = new ScannableTrackDocument.Builder();
					builder.withAxis(e.getAxis());
					builder.withScannable(e.getScannable());
					return builder;
				})
				.map(ScannableTrackDocument.Builder::build)
				.collect(Collectors.toList());
	}
}