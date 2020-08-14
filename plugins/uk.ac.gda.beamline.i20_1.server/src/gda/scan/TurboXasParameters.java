/*-
 * Copyright © 2016 Diamond Light Source Ltd.
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

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;

import org.apache.commons.lang.ArrayUtils;
import org.apache.commons.lang.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.thoughtworks.xstream.XStream;
import com.thoughtworks.xstream.annotations.Annotations;
import com.thoughtworks.xstream.annotations.XStreamAlias;
import com.thoughtworks.xstream.converters.Converter;
import com.thoughtworks.xstream.converters.MarshallingContext;
import com.thoughtworks.xstream.converters.UnmarshallingContext;
import com.thoughtworks.xstream.converters.basic.DoubleConverter;
import com.thoughtworks.xstream.io.HierarchicalStreamReader;
import com.thoughtworks.xstream.io.HierarchicalStreamWriter;
import com.thoughtworks.xstream.io.xml.DomDriver;

import gda.device.ContinuousParameters;
import gda.device.Scannable;
import gda.device.detector.BufferedDetector;
import gda.device.scannable.ContinuouslyScannable;
import gda.device.scannable.PVScannable;
import gda.factory.FactoryException;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.scan.ede.TimeResolvedExperimentParameters;


/**
 * Collection of parameters used to define Turbo Xas scan.
 * Also has methods to serialize/deserialize to/from XML. and load object from a file.
 * @since 13/7/2016
 */
@XStreamAlias("TurboXasParameters")
public class TurboXasParameters {

	private static final Logger logger = LoggerFactory.getLogger(TurboXasParameters.class);

	private String sampleName;

	private double startEnergy;

	private double endEnergy;

	@XStreamAlias("energyStep")
	private double energyStepSize;

	private double startPosition;

	private double endPosition;

	private double positionStepSize;

	private boolean usePositionsForScan;

	/**
	 * Polynomial to convert from motor position to energy.
	 * This is typically the Polynomial returned from calibration tool (using x coordinates normalised between 0 and 1).
	 **/
	private String energyCalibrationPolynomial;

	private double energyCalibrationMinPosition;

	private double energyCalibrationMaxPosition;

	/** Full path to reference data file used to perform the energy-position calibration */
	private String energyCalibrationReferenceFile;

	/** Full path to data file of measurement used to perform the energy-position calibration */
	private String energyCalibrationFile;

	/**
	 * Name of scannable motor to be moved during the scan. This scannable should implement {@link ContinuouslyScannable} interface.
	 */
	private String motorToMove;

	/**
	 * Names of {@link BufferedDetector}s to be used during scan.
	 */
	private String[] detectors;

	private boolean useTrajectoryScan;

	private boolean twoWayScan;

	private List<TurboSlitTimingGroup> timingGroups;

	/** Scannables to be monitored during scan : key = name of scannable, value = PV with value to record (optional) */
	private LinkedHashMap<String, String> scannablesToMonitorDuringScan;

	/** Names of any extra scannables that should be added to TurboXasScan object */
	private List<String> extraScannables;

	/**
	 * List of datasets to compute running average of during scan. Names are formatted as : <detector name>/<dataset name>
	 * . e.g. scaler_for_zebra/I0, buffered_xspress3/FFI0 ...
	 */
	private List<String> namesOfDatasetsToAverage;

	private boolean writeAsciiData;

	private String fastShutterName;

	private boolean runMappingScan = false;

	private String scannableToMove;

	private List<List<Double>> scannablePositions;

	private List<SpectrumEvent> spectrumEvents;

	public TurboXasParameters() {
		setDefaults();
	}

	// Constructor using values from a ContinuousParameters object
	public TurboXasParameters(ContinuousParameters contparams) {
		setDefaults();
		startEnergy = contparams.getStartPosition();
		endEnergy = contparams.getEndPosition();
		startPosition = startEnergy;
		endPosition = endEnergy;

		energyCalibrationPolynomial = "";

		// energy calibration poly is just motor position, so just set range from scan params:
		energyCalibrationMinPosition = startEnergy*0.8;
		energyCalibrationMaxPosition = endEnergy*1.2;

		energyStepSize = (endEnergy - startEnergy)/(contparams.getNumberDataPoints()+1);
		positionStepSize = energyStepSize;

		double timeForSpectra = contparams.getTotalTime();
		timingGroups.add( new TurboSlitTimingGroup("group1", timeForSpectra, timeForSpectra, 1) );
	}

	public void setDefaults() {
		energyCalibrationPolynomial = "";
		energyCalibrationMinPosition = 900;
		energyCalibrationMaxPosition = 3000;
		energyCalibrationReferenceFile = "";
		energyCalibrationFile = "";
		sampleName = "Default sample name";

		startEnergy=1000;
		endEnergy=2000;
		energyStepSize=10;

		startPosition=0;
		endPosition=10;
		positionStepSize=0.1;
		usePositionsForScan = true;

		timingGroups = new ArrayList<>();
		motorToMove = "turbo_xas_slit";
		useTrajectoryScan = false;
		detectors = new String[]{"scaler_for_zebra"};
		writeAsciiData = false;
		fastShutterName = "fast_shutter";
		twoWayScan = false;
	}

	// Getters, setters...
	public String getSampleName() {
		return sampleName;
	}
	public void setSampleName(String sampleName) {
		this.sampleName = sampleName;
	}

	public double getStartEnergy() {
		return startEnergy;
	}
	public void setStartEnergy(double startEnergy) {
		this.startEnergy = startEnergy;
	}

	public double getEndEnergy() {
		return endEnergy;
	}
	public void setEndEnergy(double endEnergy) {
		this.endEnergy = endEnergy;
	}

	public double getEnergyStep() {
		return energyStepSize;
	}
	public void setEnergyStep(double energyStepSize) {
		this.energyStepSize = energyStepSize;
	}

	public double getStartPosition() {
		return startPosition;
	}
	public void setStartPosition(double startPosition) {
		this.startPosition = startPosition;
	}

	public void setEndPosition(double endPosition) {
		this.endPosition = endPosition;
	}
	public double getEndPosition() {
		return endPosition;
	}

	public double getPositionStepSize() {
		return positionStepSize;
	}
	public void setPositionStepSize(double positionStepSize) {
		this.positionStepSize = positionStepSize;
	}

	public boolean isUsePositionsForScan() {
		return usePositionsForScan;
	}
	public void setUsePositionsForScan(boolean usePositionsForScan) {
		this.usePositionsForScan = usePositionsForScan;
	}

	public void addTimingGroup( TurboSlitTimingGroup group ) {
		timingGroups.add( group );
	}
	public void setTimingGroups( List<TurboSlitTimingGroup> groupList ) {
		timingGroups = new ArrayList<>( groupList );
	}
	public List<TurboSlitTimingGroup> getTimingGroups() {
		return timingGroups;
	}

	public int getNumTimingGroups() {
		return timingGroups != null ? timingGroups.size() : 0;
	}

	public int getTotalNumSpectra() {
		int totNumSpectra = 0;
		for (TurboSlitTimingGroup group : timingGroups) {
			totNumSpectra += group.getNumSpectra();
		}
		return totNumSpectra;
	}

	public String getEnergyCalibrationPolynomial() {
		return energyCalibrationPolynomial;
	}
	public void setEnergyCalibrationPolynomial(String energyCalibrationPolynomial) {
		this.energyCalibrationPolynomial = energyCalibrationPolynomial;
	}

	public double getEnergyCalibrationMinPosition() {
		return energyCalibrationMinPosition;
	}
	public void setEnergyCalibrationMinPosition(double energyCalibrationMinPosition) {
		this.energyCalibrationMinPosition = energyCalibrationMinPosition;
	}

	public double getEnergyCalibrationMaxPosition() {
		return energyCalibrationMaxPosition;
	}
	public void setEnergyCalibrationMaxPosition(double energyCalibrationMaxPosition) {
		this.energyCalibrationMaxPosition = energyCalibrationMaxPosition;
	}

	public String getMotorToMove() {
		return motorToMove;
	}

	/**
	 * Set name of motor to be moved during scan. This should implement the {@link ContinuouslyScannable} interface.
	 * @param motorToMove
	 */
	public void setMotorToMove(String motorToMove) {
		this.motorToMove = motorToMove;
	}

	public String[] getDetectors() {
		return detectors;
	}

	/**
	 * Set names of detectors to be used during scan - these should be {@link BufferedDetector}s.
	 * @param detectors
	 */
	public void setDetectors(String[] detectors) {
		this.detectors = detectors;
	}

	public void setExtraScannables(List<String> extraScannables) {
		this.extraScannables = new ArrayList<>(extraScannables);
	}

	public List<String> getExtraScannables() {
		return extraScannables;
	}

	public boolean getUseTrajectoryScan() {
		return useTrajectoryScan;
	}

	public void setUseTrajectoryScan(boolean useTrajectoryScan) {
		this.useTrajectoryScan = useTrajectoryScan;
	}

	public boolean isTwoWayScan() {
		return twoWayScan;
	}

	public void setTwoWayScan(boolean twoWayScan) {
		this.twoWayScan = twoWayScan;
	}

	/**
	 * @return Name of calibration file used as reference data during energy calibration.
	 */
	public String getEnergyCalibrationReferenceFile() {
		return energyCalibrationReferenceFile;
	}

	public void setEnergyCalibrationReferenceFile(String energyCalibrationReferenceFile) {
		this.energyCalibrationReferenceFile = energyCalibrationReferenceFile;
	}

	/**
	 * @return Name of scan file used during energy calibration.
	 */
	public String getEnergyCalibrationFile() {
		return energyCalibrationFile;
	}

	public void setEnergyCalibrationFile(String energyCalibrationFile) {
		this.energyCalibrationFile = energyCalibrationFile;
	}

	public TurboXasMotorParameters getMotorParameters() {
		return new TurboXasMotorParameters(this);
	}

	public Map<String, String> getScannablesToMonitorDuringScan() {
		return scannablesToMonitorDuringScan;
	}

	public void setScannablesToMonitorDuringScan(Map<String, String> scannablesToMonitorDuringScan) {
		if (scannablesToMonitorDuringScan!=null && !scannablesToMonitorDuringScan.isEmpty()) {
			this.scannablesToMonitorDuringScan = new LinkedHashMap<>();
			this.scannablesToMonitorDuringScan.putAll(scannablesToMonitorDuringScan);
		} else {
			//set to null if empty, so field does not appear in serialized xml string and cause problems with de-serialization
			this.scannablesToMonitorDuringScan = null;
		}
	}

	public boolean getWriteAsciiData() {
		return writeAsciiData;
	}

	public void setWriteAsciiData(boolean writeAsciiData) {
		this.writeAsciiData = writeAsciiData;
	}

	public String getFastShutterName() {
		return fastShutterName;
	}

	public void setFastShutterName(String fastShutterName) {
		this.fastShutterName = fastShutterName;
	}

	public boolean isRunMappingScan() {
		return runMappingScan;
	}

	public void setRunMappingScan(boolean runMappingScan) {
		this.runMappingScan = runMappingScan;
	}

	public String getScannableToMove() {
		return scannableToMove;
	}

	public void setScannableToMove(String scannableToMove) {
		this.scannableToMove = scannableToMove;
	}

	public List<List<Double>> getScannablePositions() {
		return scannablePositions;
	}

	public void setScannablePositions(List<List<Double>> scannablePositions) {
		this.scannablePositions = new ArrayList<>(scannablePositions);
	}

	/**
	 * Custom converter for double precision numbers, so have full control over double to string conversion
	 * used when serializing.
	 * @param doubleVal
	 * @return double formatted as string
	 */
public static String doubleToString( double doubleVal ) {
		return Double.toString(doubleVal);
	}

	public static class CustomDoubleConverter extends DoubleConverter {
		@Override
		public String toString(Object obj) {
			return (obj == null ? null : doubleToString((double) obj));
		}
	}

	/** Custom converter used for (de)serialization of Maps, so that the XML string output is more informative and less verbose.
	 * Instead of series of series of lines for items in map e.g.:
	 * <pre>
	 * {@code
	 * <entry>
	 *    <value>nameOfScannable</value>
	 *    <value>pvForScannable</value>
	 * </entry>
	 * }</pre>
	 *
	 * This formatter instead produced just two lines for each item :
	 * <pre>{@code
	 * <scannableName>nameOfScannable</scannableName>
	 * <pv>pvForScannable</pv>
	 * }</pre>
	 *
	 * See <a href= "http://x-stream.github.io/converter-tutorial.html"/>http://x-stream.github.io/converter-tutorial.html</a> for a useful tutorial on Converters
	 * @see TurboXasParametersTest
	 */
	public static class MapConverter implements Converter {

		public static final String keyNodeName = "scannableName";
		public static final String valueNodeName = "pv";

		@Override
		public boolean canConvert(Class clazz) {
			return clazz.equals(LinkedHashMap.class) || clazz.equals(HashMap.class);
		}

		@Override
		public void marshal(Object value, HierarchicalStreamWriter writer, MarshallingContext context) {
			Map<String, String> map = (Map<String, String>) value;
			for(Entry<String,String> item : map.entrySet()) {
				writer.startNode(keyNodeName);
				writer.setValue(item.getKey());
				writer.endNode();
				writer.startNode(valueNodeName);
				writer.setValue(item.getValue());
				writer.endNode();
			}
		}

		@Override
		public Object unmarshal(HierarchicalStreamReader reader, UnmarshallingContext context) {
			Map<String, String> map = new LinkedHashMap<String, String>();
			reader.moveDown();
			while( reader.getNodeName().equals(keyNodeName) ) {
				String scnName = reader.getValue();
				reader.moveUp();

				reader.moveDown();
				String scnPv = reader.getValue();
				reader.moveUp();

				map.put(scnName,  scnPv);
				if (reader.hasMoreChildren()) {
					reader.moveDown();
				}
			}
			return map;
		}
	}

	/**
	 * Return new XStream object that can serialize/deserialize {@link TurboXasParameters} objects to/from XML
	 * @return XStream
	 */
	static public XStream getXStream() {
		XStream xstream = new XStream( new DomDriver() );
		xstream.setClassLoader(TurboXasParameters.class.getClassLoader());
		// Most of this can be done automatically from annotations in newer versions of XStream > 1.3...
		Annotations.configureAliases(xstream,  TurboXasParameters.class );
		Annotations.configureAliases(xstream,  TurboSlitTimingGroup.class );
		xstream.addImplicitCollection(TurboXasParameters.class, "timingGroups");

		xstream.omitField(TurboXasParameters.class , "logger");
		xstream.registerConverter(new CustomDoubleConverter(), XStream.PRIORITY_VERY_HIGH);
		xstream.registerConverter(new MapConverter(), XStream.PRIORITY_VERY_HIGH);
		xstream.alias("scannablesToMonitorDuringScan", LinkedHashMap.class);

		xstream.alias("SpectrumEvent", SpectrumEvent.class);

		return xstream;
	}

	/**
	 * Serialize supplied {@link TurboXasParameters} object to XML.
	 * @param params
	 * @return String with XML serialized object
	 */
	static public String toXML( TurboXasParameters params ) {
		XStream xstream = TurboXasParameters.getXStream();
		return xstream.toXML( params );
	}

	public String toXML() {
		return toXML( this );
	}

	/**
	 * Create new {@link TurboXasParameters} object deserialized from supplied XML string.
	 * @param xmlString
	 * @return TurboXasScanParameters object
	 */
	static public TurboXasParameters fromXML( String xmlString ) {
		XStream xstream = TurboXasParameters.getXStream();
		return (TurboXasParameters) xstream.fromXML( xmlString );
	}

	static public TurboXasParameters loadFromFile( String filePath ) {
		try {
			BufferedReader bufferedReader = new BufferedReader( new FileReader(filePath) );
			String line;
			StringBuilder xmlString = new StringBuilder();
			while( (line = bufferedReader.readLine()) != null ) {
				xmlString.append(line);
			}
			bufferedReader.close();
			return TurboXasParameters.fromXML( xmlString.toString() );

		} catch ( IOException e ) {
			logger.error("Problem loading xml data from file {}", filePath, e);
			InterfaceProvider.getTerminalPrinter().print("Problem loading data from file "+filePath+" : "+e.getMessage());
		}

		return null;
	}

	/**
	 * Serialize current object to xml file
	 * @param filePath
	 */
	public void saveToFile(String filePath) {
		try {
			String xmlString = this.toXML();
			BufferedWriter bufWriter = new BufferedWriter( new FileWriter(filePath) );
			bufWriter.write( xmlString );
			bufWriter.close();
		} catch (IOException e) {
			logger.error("Problem saving serialized object to file {}", e);
		}
	}

	/** Create list of Scannables from the {@link#scannablesToMonitorDuringScan} map by searching for/creating scannables
	 * depending on content of values in the map :
	 * <li> value = empty/null -> use key as name of scannable and locate it using Finder.
	 * <li> value != empty ->create new {@link PVScannable} with : scannable name = map key, PV = map value
	*/
	public List<Scannable> getScannablesToMonitor() {
		final List<Scannable> scannableList = new ArrayList<>();
		if (scannablesToMonitorDuringScan != null) {
			for (Map.Entry<String, String> entry : scannablesToMonitorDuringScan.entrySet() ) {
				final String nameOfScannable = entry.getKey();
				final String nameOfPv = entry.getValue();
				Scannable scn = null;
				if (StringUtils.isEmpty(nameOfPv)) {
					scn = Finder.getInstance().find(nameOfScannable);
					if (scn == null) {
						logger.warn("Unable to find scannable called {} on server", nameOfScannable);
					}
				} else {
					final PVScannable monitorForPv = new PVScannable(nameOfScannable, nameOfPv);
					monitorForPv.setCanMove(false);
					try {
						monitorForPv.configure();
						scn = monitorForPv;
					} catch (FactoryException e) {
						logger.warn("Problem creating scannable called {} for PV {} : {}", nameOfScannable, nameOfPv, e.getMessage());
					}
				}
				if (scn != null) {
					logger.debug("Adding scannable to be monitored : {}", scn.getName());
					scannableList.add(scn);
				}
			}
		}
		return scannableList;
	}

	/**
	 * Create list of scannable objects using the Finder.
	 * @param scannableNames names of scannables to look for
	 * @return
	 */
	private List<Scannable> findScannableObjects(List<String> scannableNames) {
		final List<Scannable> scannableList = new ArrayList<>();
		if (scannableNames != null) {
			scannableNames.forEach(name -> {
				Optional<Scannable> optionalScannable = Finder.getInstance().findOptional(name);
				if (optionalScannable.isPresent()) {
					Scannable scannable = optionalScannable.get();
					scannableList.add(scannable);
					logger.debug("Adding scannable {}", scannable.getName());
				} else {
					logger.warn("Unable to find scannable called {} on server", name);
				}
			});
		}
		return scannableList;
	}

	/**
	 * Create a {@link TurboXasScan} object from the current set of scan parameters.
	 * It attempts to get scannables to be used from {@link #motorToMove} and {@link #detectors} strings
	 * using the {@link Finder}. It also attempts to validate the positions and speeds to be used
	 * for the scan against the motor limits, sending warnings to logpanel if necessary.
	 * @return TurboXasScan object
	 * @throws InterruptedException If motor to move cannot be found, or if no detectors could be found.
	 * @throws Exception
	 */
	public TurboXasScan createScan() throws Exception {

		Map<String, ContinuouslyScannable> continuouslyScannables = Finder.getInstance().getFindablesOfType(ContinuouslyScannable.class);
		Map<String, BufferedDetector> bufferedDetector = Finder.getInstance().getFindablesOfType(BufferedDetector.class);

		// Try to find the continuouslyScannable motor to be moved ...
		ContinuouslyScannable motor = continuouslyScannables.get( getMotorToMove() );
		if (motor == null) {
			throw new Exception("Cannot find motor called "+motorToMove+" to be moved during scan");
		}

		// Try to find the buffered detectors ...
		BufferedDetector[] bufDetectors = new BufferedDetector[]{};
		for(String detname : detectors) {
			BufferedDetector det = bufferedDetector.get(detname);
			if (det!=null) {
				bufDetectors = (BufferedDetector[]) ArrayUtils.add(bufDetectors, det);
			} else {
				logger.warn("Can't find detector {} to use for scan");
			}
		}
		if (bufDetectors.length==0) {
			throw new Exception("No suitable detectors available to use for scan");
		}

		TurboXasMotorParameters motorParams = getMotorParameters();
		motorParams.setMotorLimits(motor);
		motorParams.setMotorParametersForTimingGroup(0);
		motorParams.validateParameters(); // shows warnings about limits being exceeded etc.

		TurboXasScan scan = new TurboXasScan(motor, motorParams, bufDetectors);
		scan.setScannablesToMonitor(getScannablesToMonitor());
		scan.getAllScannables().addAll(findScannableObjects(extraScannables));
		scan.setWriteAsciiDataAfterScan(writeAsciiData);

		// Set the fast shutter if found on server
		Optional<Scannable> fastShutter = Finder.getInstance().findOptional(fastShutterName);
		if (fastShutter.isPresent()) {
			scan.setShutter(fastShutter.get());
		}

		scan.setTwoWayScan(twoWayScan);

		scan.setDatasetNamesToAverage(namesOfDatasetsToAverage);

		// Add the scannable to be moved and the positions
		if (runMappingScan && !StringUtils.isEmpty(scannableToMove)) {
			Optional<Scannable> scnToMove = Finder.getInstance().findOptional(scannableToMove);
			if(scnToMove.isPresent()) {
				scan.setScannableToMove(scnToMove.get());
				if (scannablePositions == null) {
					logger.warn("Scannable positions have not been set");
				} else {
					scan.setPositionsForScan(TimeResolvedExperimentParameters.getPositionArray(scannablePositions));
					scan.getScannablesToMonitor().add(scnToMove.get());
					logger.info("Moving scannable '{}' to {} different position during scan.", scannableToMove, scannablePositions.size());
				}
			} else {
				logger.warn("Can't set scannableToMove - scannable '{}' not found on server", scannableToMove);
			}
		}

		if (spectrumEvents != null) {
			for(SpectrumEvent event : spectrumEvents) {
				scan.addSpectrumEvent(event.getSpectrumNumber(), event.getScannableName(), event.getPosition());
			}
		}
		return scan;
	}

	public List<String> getNamesOfDatasetsToAverage() {
		return namesOfDatasetsToAverage;
	}

	public void setNamesOfDatasetsToAverage(List<String> namesOfDatasetsToAverage) {
		this.namesOfDatasetsToAverage = new ArrayList<>(namesOfDatasetsToAverage);
	}

	public List<SpectrumEvent> getSpectrumEvents() {
		return spectrumEvents;
	}

	public void setSpectrumEvents(List<SpectrumEvent> spectrumEvents) {
		this.spectrumEvents = new ArrayList<>(spectrumEvents);
	}
}
