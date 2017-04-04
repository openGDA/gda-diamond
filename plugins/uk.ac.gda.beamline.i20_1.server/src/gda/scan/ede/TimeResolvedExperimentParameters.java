package gda.scan.ede;

import java.io.BufferedWriter;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.thoughtworks.xstream.XStream;

import gda.device.DeviceException;
import gda.scan.ede.position.EdePositionType;
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

	private String fileNamePrefix = "";
	private String sampleDetails = "";
	private boolean useFastShutter;
	private String fastShutterName;

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
	private double irefIntegrationTime;
	private int i0ForIRefNoOfAccumulations;
	private int irefNoOfAccumulations;

	private boolean hideLemoFields;

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

	public String getFileNamePrefix() {
		return fileNamePrefix;
	}
	public void setFileNamePrefix(String fileNamePrefix) {
		this.fileNamePrefix = fileNamePrefix;
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
	public void setiRefMotorPositions(Map<String, Double> iRefMotorPositions) {
		this.iRefMotorPositions = iRefMotorPositions;
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

	public String toXML() {
		XStream xstream = getXStream();
		// Remove lemo trigger fields if using frelon detector (only needed for Xh, Xstrip)
		if (hideLemoFields || detectorName.equals(DetectorSetupType.FRELON.getDetectorName())) {
			removeXhLemoTriggerFields(xstream);
		}
		return xstream.toXML(this);
	}

	public static TimeResolvedExperimentParameters loadFromFile(String fname) throws FileNotFoundException {
		InputStream in = new FileInputStream(fname);
		XStream xstream = getXStream();
		TimeResolvedExperimentParameters newParams = (TimeResolvedExperimentParameters)xstream.fromXML(in);
		
		//Setup the I0, It scan position (maps with scannable motor as key and and position as the value)
		EdeScanMotorPositions motorPos = new EdeScanMotorPositions();
		try {
			motorPos = (EdeScanMotorPositions) newParams.getI0ScanPosition();
			if (motorPos!=null) {
				motorPos.setupScannablePositionMap();
			}
			motorPos = (EdeScanMotorPositions) newParams.getItScanPosition();
			if (motorPos!=null) {
				motorPos.setupScannablePositionMap();
			}
		} catch (DeviceException e) {
				logger.warn("Problem setting up {} scannable position map.", motorPos.getType(), e);
		}

		return newParams;
	}

	
	/**
	 * Serialize current object to xml file
	 * @param filePath
	 */
	public void saveToFile(String filePath) {
		try {
			XStream xstream = getXStream();
			// Remove lemo trigger fields if using frelon detector (only needed for Xh, Xstrip)
			if (hideLemoFields || detectorName.equals(DetectorSetupType.FRELON.getDetectorName())) {
				removeXhLemoTriggerFields(xstream);
			}
			String xmlString = XML_HEADER+xstream.toXML(this);
			BufferedWriter bufWriter = new BufferedWriter( new FileWriter(filePath) );
			bufWriter.write( xmlString );
			bufWriter.close();
		} catch (IOException e) {
			String message = "Problem saving serialized object to file "+filePath;
			System.out.println( message+"\n"+e );
			logger.error(message,e);
		}
	}
	
	public static XStream getXStream() {
		XStream xstream = new XStream();
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
	 */
	static public TimeResolvedExperiment createTimeResolvedExperiment(TimeResolvedExperimentParameters params) throws DeviceException {		
		
		TimeResolvedExperiment theExperiment = 	new TimeResolvedExperiment(params.getI0AccumulationTime(), params.getItTimingGroups(),
													params.getI0MotorPositions(), params.getItMotorPositions(),
													params.getDetectorName(), params.getTopupMonitorName(), params.getBeamShutterScannableName());			

		// Set the Iref parameters
		if (params.getDoIref()) {
			theExperiment.setIRefParameters(params.getI0MotorPositions(), params.getiRefMotorPositions(), 
					params.getIrefIntegrationTime(), params.getI0ForIRefNoOfAccumulations(),
					params.getIrefIntegrationTime(), params.getIrefNoOfAccumulations());
		}

		theExperiment.setFileNamePrefix(params.getFileNamePrefix());
		theExperiment.setSampleDetails(params.getSampleDetails());
		theExperiment.setUseFastShutter(params.getUseFastShutter());
		theExperiment.setFastShutterName(params.getFastShutterName());
		theExperiment.setItTriggerOptions(params.getItTriggerOptions());
		if (params.getNumberOfRepetition()>1) {
			theExperiment.setRepetitions(params.getNumberOfRepetition());
		}
		
		return theExperiment;
	}
	
	public TimeResolvedExperiment createTimeResolvedExperiment() throws DeviceException {
		return createTimeResolvedExperiment(this);
	}
}
