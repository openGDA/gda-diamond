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

import java.beans.Transient;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.stream.Collectors;

import org.apache.commons.io.FileUtils;
import org.apache.commons.lang.ArrayUtils;
import org.apache.commons.lang.StringUtils;
import org.apache.commons.math3.util.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.annotation.JsonSetter;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;

import gda.device.ContinuousParameters;
import gda.device.Scannable;
import gda.device.detector.BufferedDetector;
import gda.device.scannable.ContinuouslyScannable;
import gda.device.scannable.PVScannable;
import gda.factory.FactoryException;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.scan.XmlSerializationMappers.ListDeserializer;
import gda.scan.XmlSerializationMappers.ListSerializer;
import gda.scan.XmlSerializationMappers.MapDeserializer;
import gda.scan.XmlSerializationMappers.MapSerializer;
import gda.scan.XmlSerializationMappers.NestedListDeserializer;
import gda.scan.XmlSerializationMappers.NestedListSerializer;
import gda.scan.ede.TimeResolvedExperimentParameters;
import gda.scan.ede.position.EnergyPositionCalculator;

/**
 * Collection of parameters used to define Turbo Xas scan.
 * Also has methods to serialize/deserialize to/from XML. and load object from a file.
 * @since 13/7/2016
 */
@JsonInclude(Include.NON_NULL)
@JsonPropertyOrder({ "sampleName", "startEnergy", "endEnergy", "energyStep",
	"startPosition", "endPosition", "positionStepSize", "usePositionsForScan",
	"energyCalibrationPolynomial", "energyCalibrationMinPosition", "energyCalibrationMaxPosition",
	"energyCalibrationReferenceFile", "energyCalibrationFile",
	"motorToMove", "detectors", "useTrajectoryScan", "twoWayScan", "TimingGroup",
	"scannablesToMonitorDuringScan", "extraScannables", "namesOfDatasetsToAverage"
})
public class TurboXasParameters {

	private static final Logger logger = LoggerFactory.getLogger(TurboXasParameters.class);

	private String sampleName;

	private double startEnergy;

	private double endEnergy;

	private double energyStep;

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
	@JsonDeserialize(using=ListDeserializer.class)
	@JsonSerialize(using=ListSerializer.class)
	private List<String> detectors;

	private boolean useTrajectoryScan;

	private boolean twoWayScan;

	@JsonProperty("TimingGroup")
	private List<TurboSlitTimingGroup> timingGroups;

	/** Scannables to be monitored during scan : key = name of scannable, value = PV with value to record (optional) */
	@JsonSerialize(using = MapSerializer.class)
	@JsonDeserialize(using = MapDeserializer.class)
	private LinkedHashMap<String, String> scannablesToMonitorDuringScan;

	/** Names of any extra scannables that should be added to TurboXasScan object */
	@JsonDeserialize(using=ListDeserializer.class)
	@JsonSerialize(using=ListSerializer.class)
	private List<String> extraScannables;

	/**
	 * List of datasets to compute running average of during scan. Names are formatted as : <detector name>/<dataset name>
	 * . e.g. scaler_for_zebra/I0, buffered_xspress3/FFI0 ...
	 */
	@JsonDeserialize(using=ListDeserializer.class)
	@JsonSerialize(using=ListSerializer.class)
	private List<String> namesOfDatasetsToAverage;

	private boolean writeAsciiData;

	private String fastShutterName;

	private boolean runMappingScan = false;

	private String scannableToMove;

	@JsonDeserialize(using=NestedListDeserializer.class)
	@JsonSerialize(using=NestedListSerializer.class)
	private List<List<Double>> scannablePositions;

	@JacksonXmlElementWrapper(useWrapping = true, localName="spectrumEvents")
	@JsonProperty("SpectrumEvent")
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

		energyStep = (endEnergy - startEnergy)/(contparams.getNumberDataPoints()+1);
		positionStepSize = energyStep;

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
		energyStep=10;

		startPosition=0;
		endPosition=10;
		positionStepSize=0.1;
		usePositionsForScan = true;

		timingGroups = new ArrayList<>();
		motorToMove = "turbo_xas_slit";
		useTrajectoryScan = false;
		detectors = Arrays.asList("scaler_for_zebra");
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
		return energyStep;
	}
	public void setEnergyStep(double energyStepSize) {
		this.energyStep = energyStepSize;
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

	@JsonIgnore
	public int getNumTimingGroups() {
		return timingGroups != null ? timingGroups.size() : 0;
	}

	@JsonIgnore
	public int getTotalNumSpectra() {
		int totNumSpectra = 0;
		for (TurboSlitTimingGroup group : timingGroups) {
			totNumSpectra += group.getNumSpectra();
		}
		return totNumSpectra;
	}

	/**
	 * Return group and spectrum index for given absolute spectrum index in whole collection.
	 * (this cycles around to first group again if specNumber > {@#getTotalNumSpectra()})
	 * @param specNumber absolute spectrum index.
	 * @return Group and spectrum indices.
	 */
	public Pair<Integer,Integer> getGroupSpectrumIndices(int absIndex) {
		absIndex %= getTotalNumSpectra(); // Ensure index is between 0 and total num spectra
		int groupStartIndex = 0;
		for(int i=0; i<timingGroups.size(); i++) {
			int numSpectraInGroup = timingGroups.get(i).getNumSpectra();
			if (absIndex < groupStartIndex+numSpectraInGroup) {
				return Pair.create(i,  absIndex - groupStartIndex);
			} else {
				groupStartIndex += numSpectraInGroup;
			}
		}
		logger.warn("Could not get group, spectrum indices for spectrum with absolute index {}. Using (-1, -1) instead.", absIndex);
		return Pair.create(-1, -1);
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

	public List<String> getDetectors() {
		return detectors;
	}

	@JsonSetter("detectors")
	public void setDetectors(List<String> detectors) {
		this.detectors = new ArrayList<>(detectors);
	}

	/**
	 * Set names of detectors to be used during scan - these should be {@link BufferedDetector}s.
	 * @param detectors
	 */
	public void setDetectors(String[] detectors) {
		this.detectors = Arrays.stream(detectors).collect(Collectors.toList());
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

	@Transient
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
	 * Serialize supplied {@link TurboXasParameters} object to XML.
	 * @param params
	 * @return String with XML serialized object
	 * @throws JsonProcessingException
	 */
	public static String toXML(TurboXasParameters params ) throws IOException {
		try {
			return XmlSerializationMappers.getXmlMapper().writeValueAsString( params );
		} catch(JsonProcessingException e) {
			throw new IOException("Problem converting TurboXasParameters to XML", e);
		}
	}

	public String toXML() throws IOException {
		return toXML(this);
	}

	/**
	 * Create new {@link TurboXasParameters} object deserialized from supplied XML string.
	 * @param xmlString
	 * @return TurboXasScanParameters object
	 * @throws JsonProcessingException
	 * @throws JsonMappingException
	 */
	public static TurboXasParameters fromXML(String xmlString) throws IOException {
		try {
			return XmlSerializationMappers.getXmlMapper().readValue(xmlString, TurboXasParameters.class);
		} catch(JsonProcessingException e) {
			throw new IOException("Problem converting XML string to TurboXasParameters", e);
		}
	}

	public static TurboXasParameters loadFromFile(String filePath) throws IOException {
		try {
			String xmlString = FileUtils.readFileToString(Paths.get(filePath).toFile(), Charset.defaultCharset());
			return TurboXasParameters.fromXML(xmlString);
		} catch (IOException e) {
			InterfaceProvider.getTerminalPrinter().print("Problem loading data from file "+filePath+" : "+e.getMessage());
			throw new IOException("Problem loading xml data from file "+filePath, e);
		}
	}

	/**
	 * Serialize current object to xml file
	 * @param filePath
	 */
	public void saveToFile(String filePath) throws IOException {
		try {
			String xmlString = this.toXML();
			FileUtils.writeStringToFile(Paths.get(filePath).toFile(), xmlString, Charset.defaultCharset());
		} catch (IOException e) {
			InterfaceProvider.getTerminalPrinter().print("Problem saving data to file "+filePath+" : "+e.getMessage());
			throw new IOException("Problem saving serialized object to file "+filePath, e);
		}
	}

	/** Create list of Scannables from the {@link#scannablesToMonitorDuringScan} map by searching for/creating scannables
	 * depending on content of values in the map :
	 * <li> value = empty/null -> use key as name of scannable and locate it using Finder.
	 * <li> value != empty ->create new {@link PVScannable} with : scannable name = map key, PV = map value
	*/
	private List<Scannable> getScannablesToMonitor() {
		final List<Scannable> scannableList = new ArrayList<>();
		if (scannablesToMonitorDuringScan != null) {
			for (Map.Entry<String, String> entry : scannablesToMonitorDuringScan.entrySet() ) {
				final String nameOfScannable = entry.getKey();
				final String nameOfPv = entry.getValue();
				Scannable scn = null;
				if (StringUtils.isEmpty(nameOfPv)) {
					scn = Finder.find(nameOfScannable);
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
				Optional<Scannable> optionalScannable = Finder.findOptionalOfType(name, Scannable.class);
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

		Map<String, ContinuouslyScannable> continuouslyScannables = Finder.getFindablesOfType(ContinuouslyScannable.class);
		Map<String, BufferedDetector> bufferedDetector = Finder.getFindablesOfType(BufferedDetector.class);

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
		Finder.findOptionalOfType(fastShutterName, Scannable.class)
				.ifPresent(scan::setShutter);

		scan.setTwoWayScan(twoWayScan);

		scan.setDatasetNamesToAverage(namesOfDatasetsToAverage);

		// Add the scannable to be moved and the positions
		if (runMappingScan && !StringUtils.isEmpty(scannableToMove)) {
			Optional<Scannable> scnToMove = Finder.findOptionalOfType(scannableToMove, Scannable.class);
			if(scnToMove.isPresent()) {
				scan.setScannableToMove(scnToMove.get());
				if (scannablePositions == null) {
					logger.warn("Scannable positions have not been set");
				} else {
					scan.setPositionsForScan(TimeResolvedExperimentParameters.getPositionArray(scannablePositions));
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

	@JsonIgnore
	public EnergyPositionCalculator getEnergyPositionCalculator() {
		EnergyPositionCalculator calculator = new EnergyPositionCalculator();
		calculator.setPositionRange(getEnergyCalibrationMinPosition(), getEnergyCalibrationMaxPosition());
		calculator.setPolynomial(getEnergyCalibrationPolynomial());
		return calculator;
	}

	@Override
	public int hashCode() {
		return Objects.hash(detectors, endEnergy, endPosition, energyCalibrationFile, energyCalibrationMaxPosition,
				energyCalibrationMinPosition, energyCalibrationPolynomial, energyCalibrationReferenceFile, energyStep,
				extraScannables, fastShutterName, motorToMove, namesOfDatasetsToAverage, positionStepSize,
				runMappingScan, sampleName, scannablePositions, scannableToMove, scannablesToMonitorDuringScan,
				spectrumEvents, startEnergy, startPosition, timingGroups, twoWayScan, usePositionsForScan,
				useTrajectoryScan, writeAsciiData);
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		TurboXasParameters other = (TurboXasParameters) obj;
		return Objects.equals(detectors, other.detectors)
				&& Double.doubleToLongBits(endEnergy) == Double.doubleToLongBits(other.endEnergy)
				&& Double.doubleToLongBits(endPosition) == Double.doubleToLongBits(other.endPosition)
				&& Objects.equals(energyCalibrationFile, other.energyCalibrationFile)
				&& Double.doubleToLongBits(energyCalibrationMaxPosition) == Double
						.doubleToLongBits(other.energyCalibrationMaxPosition)
				&& Double.doubleToLongBits(energyCalibrationMinPosition) == Double
						.doubleToLongBits(other.energyCalibrationMinPosition)
				&& Objects.equals(energyCalibrationPolynomial, other.energyCalibrationPolynomial)
				&& Objects.equals(energyCalibrationReferenceFile, other.energyCalibrationReferenceFile)
				&& Double.doubleToLongBits(energyStep) == Double.doubleToLongBits(other.energyStep)
				&& Objects.equals(extraScannables, other.extraScannables)
				&& Objects.equals(fastShutterName, other.fastShutterName)
				&& Objects.equals(motorToMove, other.motorToMove)
				&& Objects.equals(namesOfDatasetsToAverage, other.namesOfDatasetsToAverage)
				&& Double.doubleToLongBits(positionStepSize) == Double.doubleToLongBits(other.positionStepSize)
				&& runMappingScan == other.runMappingScan && Objects.equals(sampleName, other.sampleName)
				&& Objects.equals(scannablePositions, other.scannablePositions)
				&& Objects.equals(scannableToMove, other.scannableToMove)
				&& Objects.equals(scannablesToMonitorDuringScan, other.scannablesToMonitorDuringScan)
				&& Objects.equals(spectrumEvents, other.spectrumEvents)
				&& Double.doubleToLongBits(startEnergy) == Double.doubleToLongBits(other.startEnergy)
				&& Double.doubleToLongBits(startPosition) == Double.doubleToLongBits(other.startPosition)
				&& Objects.equals(timingGroups, other.timingGroups) && twoWayScan == other.twoWayScan
				&& usePositionsForScan == other.usePositionsForScan && useTrajectoryScan == other.useTrajectoryScan
				&& writeAsciiData == other.writeAsciiData;
	}
}
