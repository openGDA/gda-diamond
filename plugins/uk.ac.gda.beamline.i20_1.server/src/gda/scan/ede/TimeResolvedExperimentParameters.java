package gda.scan.ede;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.apache.commons.lang.StringUtils;
import org.apache.commons.math3.analysis.polynomials.PolynomialFunction;
import org.dawnsci.ede.CalibrationDetails;
import org.dawnsci.ede.EdePositionType;
import org.dawnsci.ede.PolynomialParser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.thoughtworks.xstream.XStream;
import com.thoughtworks.xstream.io.xml.DomDriver;

import gda.device.DeviceException;
import gda.factory.FactoryException;
import gda.factory.Finder;
import gda.scan.ede.position.EdeScanMotorPositions;
import gda.scan.ede.position.EdeScanPosition;
import gda.scan.ede.position.ExplicitScanPositions;
import uk.ac.gda.exafs.data.DetectorSetupType;
import uk.ac.gda.exafs.experiment.trigger.TFGTrigger;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.TimingGroup;

/**
 * Class to contain all parameters/settings needed to setup a TimeResolved/Cyclic experiment.
 * This is designed for easy serialisation and saving to/loading from xml text file. A new TimeResolvedExperiment object
 * to run a scan can be created from the current set of parameters using {@link#createTimeResolvedExperiment()}.
 */
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

	private String detectorName;
	private String topupMonitorName;
	private String beamShutterScannableName;

	private List<TimingGroup> itTimingGroups;
	private TFGTrigger itTriggerOptions;

	private EdeScanPosition i0ScanPosition;
	private EdeScanPosition itScanPosition;

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

	private Map<String, String> scannablesToMonitorDuringScan;

	private boolean collectMultipleItSpectra;
	private String scannableToMoveForItScan;
	private List<List<Double>> positionsForItScan;

	public Map<String, String> getScannablesToMonitorDuringScan() {
		return scannablesToMonitorDuringScan;
	}

	public void setScannablesToMonitorDuringScan(Map<String, String> scannablesToMonitorDuringScan) {
		this.scannablesToMonitorDuringScan = scannablesToMonitorDuringScan;
	}

	public EdeScanPosition getI0ScanPosition() {
		return i0ScanPosition;
	}
	public void setI0ScanPosition(EdeScanPosition i0ScanPosition) {
		this.i0ScanPosition = i0ScanPosition;
	}
	public EdeScanPosition getItScanPosition() {
		return itScanPosition;
	}
	public void setItScanPosition(EdeScanPosition itScanPosition) {
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
	public Map<String, Double> getI0MotorPositions() {
		return i0MotorPositions;
	}
	public void setI0MotorPositions(Map<String, Double> i0MotorPositions) throws DeviceException {
		this.i0MotorPositions = i0MotorPositions;
		i0ScanPosition = new EdeScanMotorPositions(EdePositionType.OUTBEAM, i0MotorPositions);
	}

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
	public boolean getHideLemoFields(boolean hideLemoFields) {
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
	 */
	public static TimeResolvedExperimentParameters fromXML(String xmlString) {
		logger.debug("Creating parameters from XML string {}", xmlString);

		XStream xstream = getXStream();
		TimeResolvedExperimentParameters parameters = (TimeResolvedExperimentParameters) xstream.fromXML(xmlString);

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

	public String toXML() {
		XStream xstream = getXStream();
		// Remove lemo trigger fields if using frelon detector (only needed for Xh, Xstrip)
		if (hideLemoFields || detectorName.equals(DetectorSetupType.FRELON.getDetectorName())) {
			removeXhLemoTriggerFields(xstream);
		}
		return xstream.toXML(this);
	}

	public static TimeResolvedExperimentParameters loadFromFile(String fname) throws IOException {
		logger.debug("Loading parameters from file {}", fname);

		StringBuilder xmlString = new StringBuilder();
		try(BufferedReader bufferedReader = new BufferedReader(new FileReader(fname))) {
			String line;
			while( (line = bufferedReader.readLine()) != null ) {
				xmlString.append(line);
			}
		} catch (IOException e) {
			logger.error("Problem loading parameters from {}", fname, e);
			throw e;
		}

		return TimeResolvedExperimentParameters.fromXML(xmlString.toString());
	}

	/**
	 * Serialize current object to xml file
	 * @param filePath
	 */
	public void saveToFile(String filePath) {
		try {
			logger.debug("Saving current parameters to file {}", filePath);
			XStream xstream = getXStream();
			// Remove lemo trigger fields if using frelon detector (only needed for Xh, Xstrip)
			if (hideLemoFields || detectorName.equals(DetectorSetupType.FRELON.getDetectorName())) {
				removeXhLemoTriggerFields(xstream);
			}
			String xmlString = XML_HEADER+xstream.toXML(this);
			BufferedWriter bufWriter = new BufferedWriter( new FileWriter(filePath) );
			bufWriter.write( xmlString );
			bufWriter.close();
		} catch (Exception e) {
			String message = "Problem saving serialized object to file "+filePath;
			System.out.println( message+"\n"+e );
			logger.error(message,e);
		}
	}

	public static XStream getXStream() {
		// XStream xstream = new XStream();
		// GDA9 needs to use DomDriver() when creating XStream, to avoid 'java.lang.IllegalArgumentException: XPP3 pull parser library not present'
		// when (de)serializing in unit tests... Why is this needed here but not for TurboXasParameters?
		XStream xstream = new XStream(new DomDriver());

		xstream.setClassLoader(TimeResolvedExperimentParameters.class.getClassLoader());

		xstream.omitField(ExplicitScanPositions.class , "xScannable");
		xstream.omitField(ExplicitScanPositions.class , "yScannable");

		xstream.omitField(TFGTrigger.class, "totalTimeChangeListener");
		xstream.omitField(TFGTrigger.class, "usingExternalScripts4TFG");

		// Ignore fields with scannables (scannable names are used instead for ease of serialization)
		xstream.omitField(EdeScanMotorPositions.class, "scannablePositions");
		xstream.omitField(EdeScanMotorPositions.class, "scannableToMoveDuringScan");

		xstream.omitField(TimeResolvedExperimentParameters.class, "logger");

		xstream.omitField(TimeResolvedExperimentParameters.class,"i0MotorPositions");
		xstream.omitField(TimeResolvedExperimentParameters.class,"itMotorPositions");

		// Class name aliases
		xstream.alias("TriggerableObject" , TriggerableObject.class);
		xstream.alias("TimingGroup",  TimingGroup.class);
		xstream.alias("TimeResolvedExperimentParameters" , TimeResolvedExperimentParameters.class);
		xstream.alias("EdeScanMotorPositions" , EdeScanMotorPositions.class);

		// Implicit list for timingGroup
		xstream.addImplicitCollection(EdeScanParameters.class, "timingGroups");

		return xstream;
	}

	// Remove some fields from TimingGroup and EdeScanParameters that relate to Xh/XStrip triggering options.
	// These are not needed if using Frelon, helps to simplify xml output...
	private void removeXhLemoTriggerFields(XStream xstream) {
		String ignoreFields[] = { "outLemo", "outputsChoice", "outputsWidth" };
		Class<?> ignoreClass[] = { TimingGroup.class, EdeScanParameters.class, EdeScanParameters.class };

		for (int index = 0; index < ignoreClass.length; index++) {
			for (int i = 0; i < 8; i++) {
				String num = String.valueOf(i);
				xstream.omitField(ignoreClass[index], ignoreFields[index] + num);
			}
		}

		// Remove trig related fields (defaults are ok)...
		// Keep groupTrig though, since that is used to indicate scan that uses Tfg triggering
		String[] ignoreXhFields = { "allFramesTrig", "framesExclFirstTrig", "scansTrig", "groupTrigLemo",
				"allFramesTrigLemo", "framesExclFirstTrigLemo", "scansTrigLemo", "groupTrigRisingEdge",
				"allFramesTrigRisingEdge", "framesExclFirstTrigRisingEdge", "scansTrigRisingEdge" };
		for (String field : ignoreXhFields) {
			xstream.omitField(TimingGroup.class, field);
		}
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
		boolean useTopupChecker = timingGroups.get(0).getUseTopChecker();

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
}
