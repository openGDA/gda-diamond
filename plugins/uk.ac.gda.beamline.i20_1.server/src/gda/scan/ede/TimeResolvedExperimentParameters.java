package gda.scan.ede;

import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.apache.commons.io.FileUtils;
import org.apache.commons.lang.StringUtils;
import org.apache.commons.math3.analysis.polynomials.PolynomialFunction;
import org.dawnsci.ede.CalibrationDetails;
import org.dawnsci.ede.EdePositionType;
import org.dawnsci.ede.PolynomialParser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.annotation.JsonFilter;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import com.fasterxml.jackson.databind.ser.FilterProvider;
import com.fasterxml.jackson.databind.ser.impl.SimpleBeanPropertyFilter;
import com.fasterxml.jackson.databind.ser.impl.SimpleFilterProvider;
import com.fasterxml.jackson.dataformat.xml.XmlMapper;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;

import gda.device.DeviceException;
import gda.factory.FactoryException;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.scan.XmlSerializationMappers;
import gda.scan.ede.position.EdeScanMotorPositions;
import gda.scan.ede.position.EdeScanPosition;
import uk.ac.gda.ede.data.DetectorSetupType;
import uk.ac.gda.exafs.experiment.trigger.TFGTrigger;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

/**
 * Class to contain all parameters/settings needed to setup a TimeResolved/Cyclic experiment.
 * This is designed for easy serialisation and saving to/loading from xml text file. A new TimeResolvedExperiment object
 * to run a scan can be created from the current set of parameters using {@link#createTimeResolvedExperiment()}.
 */
@SuppressWarnings("restriction") //using Jackson x-internal classes from com.fasterxml.jackson.databind.ser.impl
@JsonFilter("LemoFilter")
@JsonInclude(Include.NON_NULL)
@JsonPropertyOrder({ "fileNameSuffix", "sampleDetails", "useFastShutter", "fastShutterName",
	"generateAsciiData", "i0AccumulationTime", "i0NumAccumulations", "numberOfRepetition", "timeBetweenRepetitions",
	"detectorName", "topupMonitorName", "beamShutterScannableName",
	"itTimingGroups", "itTriggerOptions", "i0ScanPosition", "itScanPosition",
	"doIref", "irefIntegrationTime", "i0ForIRefNoOfAccumulations", "irefNoOfAccumulations",
	"energyCalibrationPolynomial", "energyCalibrationReferenceFile", "energyCalibrationFile",
	"hideLemoFields", "scannablesToMonitorDuringScan",
	"collectMultipleItSpectra", "scannableToMoveForItScan", "positionsForItScan"
})
public class TimeResolvedExperimentParameters {

	private static final Logger logger = LoggerFactory.getLogger(TimeResolvedExperimentParameters.class);
	public static final String XML_HEADER = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";

	private String fileNameSuffix = "";
	private String sampleDetails = "";
	private boolean useFastShutter;
	private String fastShutterName;
	private boolean generateAsciiData;

	private double i0AccumulationTime;
	private int i0NumAccumulations;
	private int numberOfRepetition = 1;	 // 1 = Timeresolved, >1 Cyclic
	private double timeBetweenRepetitions;

	private String detectorName;
	private String topupMonitorName;
	private String beamShutterScannableName;

	@JacksonXmlElementWrapper(useWrapping = true, localName = "itTimingGroups")
	@JsonProperty("TimingGroup") // to specify wrapper name of each element in the list
	private List<TimingGroup> itTimingGroups;
	private TFGTrigger itTriggerOptions;

	private EdeScanMotorPositions i0ScanPosition;
	private EdeScanMotorPositions itScanPosition;

	private Map<String, Double> i0MotorPositions;
	private Map<String, Double> itMotorPositions;

	// IRef parameters
	private boolean doIref = false;
	private Map<String, Double> iRefMotorPositions;
	private EdeScanPosition irefScanPosition;
	private double irefIntegrationTime;
	private int i0ForIRefNoOfAccumulations;
	private int irefNoOfAccumulations;

	// Energy calibration parameters
	private String energyCalibrationPolynomial;
	/** Full path to reference data file used to perform the energy-position calibration */
	private String energyCalibrationReferenceFile;
	/** Full path to data file of measurement used to perform the energy-position calibration */
	private String energyCalibrationFile;

	private boolean hideLemoFields;

	@JsonSerialize(using = TimeResolvedExperimentParameters.MapSerializerStringString.class)
	@JsonDeserialize(using = TimeResolvedExperimentParameters.MapDeserializerStringString.class)
	private Map<String, String> scannablesToMonitorDuringScan;

	private boolean collectMultipleItSpectra;
	private String scannableToMoveForItScan;

	@JsonSerialize(using = XmlSerializationMappers.NestedListSerializer.class)
	@JsonDeserialize(using = XmlSerializationMappers.NestedListDeserializer.class)
	private List<List<Double>> positionsForItScan;

	public Map<String, String> getScannablesToMonitorDuringScan() {
		return scannablesToMonitorDuringScan;
	}

	public void setScannablesToMonitorDuringScan(Map<String, String> scannablesToMonitorDuringScan) {
		this.scannablesToMonitorDuringScan = scannablesToMonitorDuringScan;
	}

	public EdeScanMotorPositions getI0ScanPosition() {
		return i0ScanPosition;
	}
	public void setI0ScanPosition(EdeScanMotorPositions i0ScanPosition) {
		this.i0ScanPosition = i0ScanPosition;
	}
	public EdeScanPosition getItScanPosition() {
		return itScanPosition;
	}
	public void setItScanPosition(EdeScanMotorPositions itScanPosition) {
		this.itScanPosition = itScanPosition;
	}
	public double getI0AccumulationTime() {
		return i0AccumulationTime;
	}
	public void setI0AccumulationTime(double i0AccumulationTime) {
		this.i0AccumulationTime = i0AccumulationTime;
	}
	public int getI0NumAccumulations() {
		return i0NumAccumulations;
	}
	public void setI0NumAccumulations(int i0NumAccumulcations) {
		this.i0NumAccumulations = i0NumAccumulcations;
	}
	public List<TimingGroup> getItTimingGroups() {
		return itTimingGroups;
	}
	public void setItTimingGroups(List<TimingGroup> itTimingGroups) {
		this.itTimingGroups = itTimingGroups;
	}
	public TFGTrigger getItTriggerOptions() {
		return itTriggerOptions;
	}
	public void setItTriggerOptions(TFGTrigger itTriggerOptions) {
		this.itTriggerOptions = itTriggerOptions;
	}
	public int getNumberOfRepetition() {
		return numberOfRepetition;
	}
	public void setNumberOfRepetition(int numberOfRepetition) {
		this.numberOfRepetition = numberOfRepetition;
	}

	public double getTimeBetweenRepetitions() {
		return timeBetweenRepetitions;
	}
	public void setTimeBetweenRepetitions(double timeBetweenRepetitions) {
		this.timeBetweenRepetitions = timeBetweenRepetitions;
	}
	@JsonIgnore
	public Map<String, Double> getI0MotorPositions() {
		return i0MotorPositions;
	}
	public void setI0MotorPositions(Map<String, Double> i0MotorPositions) throws DeviceException {
		this.i0MotorPositions = i0MotorPositions;
		i0ScanPosition = new EdeScanMotorPositions(EdePositionType.OUTBEAM, i0MotorPositions);
	}
	@JsonIgnore
	public Map<String, Double> getItMotorPositions() {
		return itMotorPositions;
	}
	public void setItMotorPositions(Map<String, Double> iTMotorPositions) throws DeviceException {
		this.itMotorPositions = iTMotorPositions;
		itScanPosition = new EdeScanMotorPositions(EdePositionType.INBEAM, iTMotorPositions);
	}
	public String getDetectorName() {
		return detectorName;
	}
	public void setDetectorName(String detectorName) {
		this.detectorName = detectorName;
	}
	public String getTopupMonitorName() {
		return topupMonitorName;
	}
	public void setTopupMonitorName(String topupMonitorName) {
		this.topupMonitorName = topupMonitorName;
	}
	public String getBeamShutterScannableName() {
		return beamShutterScannableName;
	}
	public void setBeamShutterScannableName(String beamShutterScannableName) {
		this.beamShutterScannableName = beamShutterScannableName;
	}

	public String getFileNameSuffix() {
		return fileNameSuffix;
	}
	public void setFileNameSuffix(String fileNameSuffix) {
		this.fileNameSuffix = fileNameSuffix;
	}
	public String getSampleDetails() {
		return sampleDetails;
	}
	public void setSampleDetails(String sampleDetails) {
		this.sampleDetails = sampleDetails;
	}
	public boolean getUseFastShutter() {
		return useFastShutter;
	}
	public void setUseFastShutter(boolean useFastShutter) {
		this.useFastShutter = useFastShutter;
	}
	public String getFastShutterName() {
		return fastShutterName;
	}
	public void setFastShutterName(String fastShutterName) {
		this.fastShutterName = fastShutterName;
	}
	public boolean getGenerateAsciiData() {
		return generateAsciiData;
	}
	public void setGenerateAsciiData(boolean generateAsciiData) {
		this.generateAsciiData = generateAsciiData;
	}

	// Iref parameters
	public boolean getDoIref() {
		return doIref;
	}
	public void setDoIref(boolean doIref) {
		this.doIref = doIref;
	}
	public Map<String, Double> getiRefMotorPositions() {
		return iRefMotorPositions;
	}
	public void setiRefMotorPositions(Map<String, Double> iRefMotorPositions) throws DeviceException {
		this.iRefMotorPositions = iRefMotorPositions;
		irefScanPosition = new EdeScanMotorPositions(EdePositionType.REFERENCE, iRefMotorPositions);
	}
	public EdeScanPosition getiRefScanPosition() {
		return irefScanPosition;
	}
	public double getIrefIntegrationTime() {
		return irefIntegrationTime;
	}
	public void setIrefIntegrationTime(double irefIntegrationTime) {
		this.irefIntegrationTime = irefIntegrationTime;
	}
	public int getI0ForIRefNoOfAccumulations() {
		return i0ForIRefNoOfAccumulations;
	}
	public void setI0ForIRefNoOfAccumulations(int i0ForIRefNoOfAccumulations) {
		this.i0ForIRefNoOfAccumulations = i0ForIRefNoOfAccumulations;
	}
	public int getIrefNoOfAccumulations() {
		return irefNoOfAccumulations;
	}
	public void setIrefNoOfAccumulations(int irefNoOfAccumulations) {
		this.irefNoOfAccumulations = irefNoOfAccumulations;
	}

	public void setHideLemoFields(boolean hideLemoFields) {
		this.hideLemoFields = hideLemoFields;
	}
	public boolean getHideLemoFields() {
		return this.hideLemoFields;
	}

	public String getEnergyCalibrationPolynomial() {
		return energyCalibrationPolynomial;
	}

	public void setEnergyCalibrationPolynomial(String energyCalibrationPolynomial) {
		this.energyCalibrationPolynomial = energyCalibrationPolynomial;
	}

	public String getEnergyCalibrationReferenceFile() {
		return energyCalibrationReferenceFile;
	}

	public void setEnergyCalibrationReferenceFile(String energyCalibrationReferenceFile) {
		this.energyCalibrationReferenceFile = energyCalibrationReferenceFile;
	}

	public String getEnergyCalibrationFile() {
		return energyCalibrationFile;
	}

	public void setEnergyCalibrationFile(String energyCalibrationFile) {
		this.energyCalibrationFile = energyCalibrationFile;
	}

	/**
	 * Return {@link TimeResolvedExperimentParameters} object created from xml string.
	 * @param xmlString
	 * @return
	 * @throws JsonProcessingException
	 * @throws
	 */
	public static TimeResolvedExperimentParameters fromXML(String xmlString) throws IOException {

		logger.debug("Creating parameters from XML string {}", xmlString);
		xmlString = sanitizeXmlString(xmlString);

		XmlMapper mapper = getXmlMapper();

		// Examine the XML string to determine the detector type and add the
		// Serialization field filters if using the Frelon detector.
		String[] splitString = xmlString.split("\n");
		Stream.of(splitString)
				.filter(str -> str.contains("detector"))
				.findFirst()
				.ifPresent(detToken ->
					addMapperFilters(mapper, detToken.contains(DetectorSetupType.FRELON.getDetectorName()))
				);

		TimeResolvedExperimentParameters parameters = mapper.readValue(xmlString, TimeResolvedExperimentParameters.class);

		//Setup the I0, It scan position (maps with scannable motor as key and and position as the value)
		// and copy over to parameters.
		EdeScanMotorPositions motorPos = new EdeScanMotorPositions();
		try {
			motorPos = (EdeScanMotorPositions) parameters.getI0ScanPosition();
			if (motorPos != null) {
				motorPos.setupScannablePositionMap();
				parameters.setI0MotorPositions(motorPos.getPositionMap());
			}
			motorPos = (EdeScanMotorPositions) parameters.getItScanPosition();
			if (motorPos != null) {
				motorPos.setupScannablePositionMap();
				parameters.setItMotorPositions(motorPos.getPositionMap());
			}
			motorPos = (EdeScanMotorPositions) parameters.getiRefScanPosition();
			if (motorPos != null) {
				motorPos.setupScannablePositionMap();
				parameters.setiRefMotorPositions(motorPos.getPositionMap());
			}
		} catch (DeviceException e) {
			logger.warn("Problem setting up {} scannable position map.", motorPos.getType(), e);
		}
		return parameters;
	}

	/**
	 * Remove any class="..." and resolves-to="..." text from field declarations
	 *
	 * @param xmlString
	 * @return sanitised XML string
	 */
	public static String sanitizeXmlString(String xmlString) {
		xmlString = xmlString.replaceAll(" class=\"\\S+\"", "");
		return xmlString.replaceAll(" resolves-to=\"\\S+\"", "");
	}

	public String toXML() throws IOException {
		XmlMapper mapper = getXmlMapper();
		// Remove lemo trigger fields if using frelon detector (only needed for Xh, Xstrip)
		addMapperFilters(mapper, isRemoveXhFields());
		return mapper.writeValueAsString(this);
	}

	public static TimeResolvedExperimentParameters loadFromFile(String fname) throws IOException {
		logger.debug("Loading parameters from file {}", fname);
		try {
			String xmlString = FileUtils.readFileToString(Paths.get(fname).toFile(), Charset.defaultCharset());
			return TimeResolvedExperimentParameters.fromXML(xmlString);
		} catch(IOException e) {
			InterfaceProvider.getTerminalPrinter().print("Problem loading data from file "+fname+" : "+e.getMessage());
			throw new IOException("Problem loading serialized object from file "+fname, e);
		}
	}

	private boolean isRemoveXhFields() {
		return hideLemoFields || detectorName.equals(DetectorSetupType.FRELON.getDetectorName());
	}

	/**
	 * Serialize current object to xml file
	 * @param filePath
	 */
	public void saveToFile(String filePath) throws IOException {
		try {
			logger.debug("Saving current parameters to file {}", filePath);
			XmlMapper mapper = getXmlMapper();

			// Remove lemo trigger fields if using frelon detector (only needed for Xh, Xstrip)
			addMapperFilters(mapper, isRemoveXhFields());

			String xmlString = mapper.writeValueAsString(this);
			FileUtils.writeStringToFile(Paths.get(filePath).toFile(), xmlString, Charset.defaultCharset());
		} catch (IOException e) {
			InterfaceProvider.getTerminalPrinter().print("Problem saving data to file "+filePath+" : "+e.getMessage());
			throw new IOException("Problem saving serialized object to file "+filePath, e);
		}
	}

	/**
	 * Add filters to remove XH specific fields from XmlMapper object
	 *
	 * @param mapper
	 * @param filterOutXh if true, XH fields are added to filterproviders of the mapper
	 */
	private static void addMapperFilters(XmlMapper mapper, boolean filterOutXh) {
		SimpleBeanPropertyFilter filter;
		if (filterOutXh) {
			filter = SimpleBeanPropertyFilter.serializeAllExcept(getXhFields());
		} else {
			filter = SimpleBeanPropertyFilter.serializeAllExcept("class");
		}
		FilterProvider filterProvider = new SimpleFilterProvider().addFilter("LemoFilter", filter);
		mapper.setFilterProvider(filterProvider);
	}

	private static XmlMapper getXmlMapper() {
		return XmlSerializationMappers.getXmlMapper();
	}

	/** Some fields from {@link TimingGroup} and {@link EdeScanParameters} that relate only Xh/XStrip triggering options
	 * and are not needed for Frelon detector.
	 * Removing these fields during serialization helps simplify the output.
	 *
	 * @return List of XH/XStrip specific fields to ignore during serialization
	 */
	private static Set<String> getXhFields() {
		Set<String> fieldsToIgnore = new LinkedHashSet<>();

		// Remove several fields in a loop - these all have 0...8 appended to them.
		// e.g. outLemo0, outLemo1, ...
		List<String> fieldToRemove = Arrays.asList("outLemo", "outputsChoice", "outputsWidth");
		for (String field : fieldToRemove) {
			for (int i = 0; i < 8; i++) {
				String num = String.valueOf(i);
				fieldsToIgnore.add(field+num);
			}
		}

		// Remove trig related fields (defaults are ok)...
		// Keep groupTrig though, since that is used to indicate scan that uses Tfg triggering
		List<String> ignoreXhFields = Arrays.asList("allFramesTrig", "framesExclFirstTrig", "scansTrig", "groupTrigLemo",
				"allFramesTrigLemo", "framesExclFirstTrigLemo", "scansTrigLemo", "groupTrigRisingEdge",
				"allFramesTrigRisingEdge", "framesExclFirstTrigRisingEdge", "scansTrigRisingEdge");

		fieldsToIgnore.addAll(ignoreXhFields);
		fieldsToIgnore.add("class");
		return fieldsToIgnore;
	}

	/**
	 * Take new TimeResolvedExperimentParameters and set everything up (also for cyclic, if numberOfRepetitions >1)
	 * @param params
	 * @throws DeviceException
	 * @throws FactoryException
	 */
	static public TimeResolvedExperiment createTimeResolvedExperiment(TimeResolvedExperimentParameters params) throws DeviceException, FactoryException {

		logger.debug("Creating TimeResolvedExperiment from parameter bean");

		TimeResolvedExperiment theExperiment = 	new TimeResolvedExperiment(params.getI0AccumulationTime(), params.getItTimingGroups(),
													params.getI0MotorPositions(), params.getItMotorPositions(),
													params.getDetectorName(), params.getTopupMonitorName(), params.getBeamShutterScannableName());

		params.setEdeExperimentParameters(theExperiment);

		// Time resolved specific parameters.
		theExperiment.setWriteAsciiData(params.getGenerateAsciiData());
		theExperiment.setItTriggerOptions(params.getItTriggerOptions());
		if (params.getI0NumAccumulations()>0) { //I0 num accumulations != It num accumulations
			theExperiment.setNumberI0Accumulations(params.getI0NumAccumulations());
		}

		if (params.getNumberOfRepetition()>1) {
			theExperiment.setRepetitions(params.getNumberOfRepetition());
			theExperiment.setTimeBetweenRepetitions(params.getTimeBetweenRepetitions());
		}

		return theExperiment;
	}

	/**
	 * Create new CalibrationDetails object from stored calibration parameters.
	 * This is used by EdeDetectors to convert from channel to energy.
	 * @param params
	 * @return CalibrationDetails object if polynomial has been set; otherwise null.
	 */
	public CalibrationDetails createEnergyCalibration() {
		CalibrationDetails calibDetails = null;

		if (StringUtils.isNotEmpty(getEnergyCalibrationPolynomial())) {
			calibDetails = new CalibrationDetails();

			// set the sample and reference data file names
			calibDetails.setSampleDataFileName(getEnergyCalibrationFile());
			calibDetails.setReferenceDataFileName(getEnergyCalibrationReferenceFile());

			// Set the PolynomialFunction by converting the polynomial string
			double[] polyCoeffs = PolynomialParser.extractCoefficientsFromString(getEnergyCalibrationPolynomial());
			PolynomialFunction polynomial = new PolynomialFunction(polyCoeffs);
			calibDetails.setCalibrationResult(polynomial);
		}

		return calibDetails;
	}

	/**
	 * Set the reference, sample filenames and energy calibration polynomial parameters from supplied CalibrationDetails object.
	 * If null is passed in, these parameters are set to empty strings (i.e. settings for no energy calibration).
	 * @param calibrationDetails
	 */
	public void setCalibrationDetails(CalibrationDetails calibrationDetails) {
		if (calibrationDetails != null) {
			setEnergyCalibrationFile(calibrationDetails.getSampleDataFileName());
			setEnergyCalibrationReferenceFile(calibrationDetails.getReferenceDataFileName());
			setEnergyCalibrationPolynomial(calibrationDetails.getCalibrationResult().toString());
		} else {
			// No calibration
			setEnergyCalibrationFile("");
			setEnergyCalibrationReferenceFile("");
			setEnergyCalibrationPolynomial("");
		}
	}

	private void addScannablesToMonitor(EdeExperiment edeExperiment) throws FactoryException {
		if (scannablesToMonitorDuringScan!=null) {
			for(String name : scannablesToMonitorDuringScan.keySet() ) {
				String nameOfPv = scannablesToMonitorDuringScan.get(name);
				if (StringUtils.isEmpty(nameOfPv)) {
					// Name of scannable
					edeExperiment.addScannableToMonitorDuringScan(name);
				} else {
					// PV to monitor and name to use for scannable
					edeExperiment.addScannableToMonitorDuringScan(nameOfPv, name);
				}
			}
		}
	}

	public TimeResolvedExperiment createTimeResolvedExperiment() throws DeviceException, FactoryException {
		return createTimeResolvedExperiment(this);
	}

	/**
	 * Create single spectrum scan (use first timing group for It settings)
	 * @param params
	 * @return
	 * @throws DeviceException
	 * @throws FactoryException
	 */
	static public SingleSpectrumScan createSingleSpectrumScan(TimeResolvedExperimentParameters params) throws DeviceException, FactoryException {

		logger.debug("Creating SingleSpectrumScan from parameter bean");

		List<TimingGroup> timingGroups = params.getItTimingGroups();
		if (timingGroups==null || timingGroups.size()==0) {
			return null;
		}

		// Use first timing group to get: It accumulation time, number of It accumulations and 'use topup' flag
		double itAccumulationTimes = timingGroups.get(0).getTimePerScan();
		int itNumAccumulations = timingGroups.get(0).getNumberOfScansPerFrame();
		boolean useTopupChecker = timingGroups.get(0).getUseTopupChecker();

		SingleSpectrumScan theExperiment = new SingleSpectrumScan(params.getI0AccumulationTime(), params.getI0NumAccumulations(),
				itAccumulationTimes, itNumAccumulations, params.getI0MotorPositions(), params.getItMotorPositions(),
				params.getDetectorName(), params.getTopupMonitorName(), params.getBeamShutterScannableName() );

		params.setEdeExperimentParameters(theExperiment);

		//Single spectrum specific parameters
		theExperiment.setUseTopupChecker(useTopupChecker);

		return theExperiment;
	}

	public SingleSpectrumScan createSingleSpectrumScan() throws DeviceException, FactoryException {
		return createSingleSpectrumScan(this);
	}

	/**
	 * Set values common to all {@link EdeExperiment}s. (i.e. {@link SingleSpectrumScan}s and {@link TimeResolvedExperiment}s).
	 * <li> Iref parameters
	 * <li> Sample name and suffix
	 * <li> Fast shutter name, use fast shutter
	 * <li> Energy name
	 * <li> Parameter bean
	 * <li> List of any scannables being monitored
	 * @param theExperiment
	 * @throws FactoryException
	 * @throws DeviceException
	 */
	public void setEdeExperimentParameters(EdeExperiment theExperiment) throws FactoryException, DeviceException {
		if (getDoIref()) {
			theExperiment.setIRefParameters(getI0MotorPositions(), getiRefMotorPositions(),
					getIrefIntegrationTime(), getI0ForIRefNoOfAccumulations(),
					getIrefIntegrationTime(), getIrefNoOfAccumulations());
		}

		theExperiment.setUseFastShutter(getUseFastShutter());
		theExperiment.setFastShutterName(getFastShutterName());
		theExperiment.setFileNameSuffix(getFileNameSuffix());
		theExperiment.setSampleDetails(getSampleDetails());
		theExperiment.getDetector().setEnergyCalibration(createEnergyCalibration());
		theExperiment.setParameterBean(this);
		addScannablesToMonitor(theExperiment);
		if (collectMultipleItSpectra && positionsForItScan != null) {
			EdeScanMotorPositions motorPos = theExperiment.getItScanPositions();
			List<Object> positionValues = getPositionArray(positionsForItScan);
			motorPos.setMotorPositionsDuringScan(positionValues);
			motorPos.setScannableToMoveDuringScan(Finder.find(scannableToMoveForItScan));
		}
	}

	/**
	 * Make a {@code List<Object>} from {@code List<List<Double>>}. The i'th element in the Object list is an
	 * array with i'th element from each List of doubles
	 *
	 * @param list
	 * @return
	 */
	public static List<Object> getPositionArray(List<List<Double>> list) {
		if (list == null || list.isEmpty()) {
			return Collections.emptyList();
		}

		// Return list of positions
		if (list.size()==1) {
			return list.get(0).stream()
					.map(val -> (Object)val)
					.collect(Collectors.toList());
		}

		// return list of arrays with positions
		List<Object> positions = new ArrayList<>();
		int numValues = list.size();
		for(int index=0; index<list.get(0).size(); index++) {
			double[] vals = new double[numValues];
			for(int i=0; i<numValues; i++) {
				vals[i] = list.get(i).get(index);
			}
			positions.add(vals);
		}
		return positions;
	}

	public boolean isCollectMultipleItSpectra() {
		return collectMultipleItSpectra;
	}

	public void setCollectMultipleItSpectra(boolean collectMultipleItSpectra) {
		this.collectMultipleItSpectra = collectMultipleItSpectra;
	}

	public String getScannableToMoveForItScan() {
		return scannableToMoveForItScan;
	}

	public void setScannableToMoveForItScan(String scannableToMoveForItScan) {
		this.scannableToMoveForItScan = scannableToMoveForItScan;
	}

	public List<List<Double>> getPositionsForItScan() {
		return positionsForItScan;
	}

	public void setPositionsForItScan(List<List<Double>> positionsForItScan) {
		this.positionsForItScan = positionsForItScan;
	}

	public static class MapSerializerStringDouble extends XmlSerializationMappers.MapSerializer {
		public MapSerializerStringDouble() {
			super();
			keyFieldName = "string";
			valueFieldName = "double";
			entryFieldName = "entry";
		}
	}

	public static class MapDeserializerStringDouble extends XmlSerializationMappers.MapDeserializer {
		public MapDeserializerStringDouble() {
			super();
			keyFieldName = "string";
			valueFieldName = "double";
			entryFieldName = "entry";
		}
	}


	public static class MapSerializerStringString extends XmlSerializationMappers.MapSerializer {
		public MapSerializerStringString() {
			super();
			keyFieldName = "string";
			valueFieldName = "string";
			entryFieldName = "entry";
		}
	}

	public static class MapDeserializerStringString extends XmlSerializationMappers.MapDeserializer {
		public MapDeserializerStringString() {
			super();
			keyFieldName = "string";
			valueFieldName = "string";
			entryFieldName = "entry";
		}
	}
}
