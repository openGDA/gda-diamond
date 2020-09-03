package uk.ac.diamond.daq.beamline.k11.diffraction;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import gda.configuration.properties.LocalProperties;
import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;

/**
 * Hides the configuration structural design.
 *
 * <p>
 * Defining an AcquisitionTemplateType is necessary to define which scannable is associated with each {@link ScannableTrackDocument}.
 * As such the client has to configure the possible acquisitions in the property file.
 * </p>
 * A typical configuration defining a camera would look like below
 *
 * <pre>
 * {@code
 *	acquisition.diffraction.two_dimension_point.scannable.0 = simx
 *	acquisition.diffraction.two_dimension_point.scannable.1 = simy
 *
 * 	acquisition.diffraction.two_dimension_line.scannable.0 = simx
 * 	acquisition.diffraction.two_dimension_line.scannable.1 = simy
 *
 * 	acquisition.diffraction.two_dimension_grid.scannable.0 = simx
 * 	acquisition.diffraction.two_dimension_grid.scannable.1 = simy
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
 * <li><i>scannable.INDEX</i>
 * <ul>
 * <li>an indexed list of scannables</li>
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

	private DiffractionAcquisitionTypeProperties() {}

	/**
	 * The prefix used in the property files to identify a camera configuration.
	 */
	private static final String ACQUISITION_TYPE_CONFIGURATION_PREFIX = "acquisition.diffraction";

	private static List<String> getAcquisitionTemplateTypeKeys(String acquisitionTemplateType) {
		return LocalProperties.getKeysByRegexp(String.format("%s\\.%s\\.scannable\\.\\d",
				ACQUISITION_TYPE_CONFIGURATION_PREFIX, acquisitionTemplateType));
	}

	private static void parseAcquisitionTypeScannableProperties() {
		Arrays.stream(AcquisitionTemplateType.values())
			.forEach(DiffractionAcquisitionTypeProperties::parseAcquisitionTemplateType);
	}

	private static void parseAcquisitionTemplateType(AcquisitionTemplateType acquisitonTemplateType) {
		List<ScannableTrackDocument> scannableTrackDocuments = getAcquisitionTemplateTypeKeys(acquisitonTemplateType.name().toLowerCase()).stream()
			.map(LocalProperties::get)
			.map(DiffractionAcquisitionTypeProperties::createScannableTrackDocuments)
			.collect(Collectors.toList());
		acquisitionTemplateTypeScanables.put(acquisitonTemplateType, scannableTrackDocuments);
	}

	private static ScannableTrackDocument createScannableTrackDocuments(String scannable) {
		ScannableTrackDocument.Builder builder = new ScannableTrackDocument.Builder();
		builder.withScannable(scannable);
		return builder.build();
	}

	/**
	 * Create a brand new list of scannableTrackDocument for the specified acquisition template type
	 * @param acquisitonTemplateType the acquisition type
	 * @return a list of predefined scannableTrackDocument
	 */
	public static ScanpathDocument.Builder createScanpathDocument(AcquisitionTemplateType acquisitonTemplateType) {
		List<ScannableTrackDocument> scannableTrackDocuments =
				acquisitionTemplateTypeScanables.get(acquisitonTemplateType).stream()
			.map(e -> {
				ScannableTrackDocument.Builder builder = new ScannableTrackDocument.Builder();
				builder.withPoints(5); // default points
				if (AcquisitionTemplateType.TWO_DIMENSION_POINT.equals(acquisitonTemplateType)) {
					builder.withPoints(1); // it's a point, what else?
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
}