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
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.thoughtworks.xstream.XStream;
import com.thoughtworks.xstream.annotations.Annotations;
import com.thoughtworks.xstream.annotations.XStreamAlias;
import com.thoughtworks.xstream.converters.basic.DoubleConverter;

import gda.device.ContinuousParameters;


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

	// Polynomial to convert from motor position to energy.
	// Polynomial returned from calibration tool use x coord normalised between 0 and 1.
	private String energyCalibrationPolynomial;

	private double energyCalibrationMinPosition;

	private double energyCalibrationMaxPosition;

	private List<TurboSlitTimingGroup> timingGroups;

	public TurboXasParameters() {
		setDefaults();
	}

	// Constructor using values from a ContinuousParameters object
	public TurboXasParameters(ContinuousParameters contparams) {
		setDefaults();
		startEnergy = contparams.getStartPosition();
		endEnergy = contparams.getEndPosition();

		energyCalibrationPolynomial = "";

		// energy calibration poly is just motor position, so just set range from scan params:
		energyCalibrationMinPosition = startEnergy*0.8;
		energyCalibrationMaxPosition = endEnergy*1.2;

		energyStepSize = (endEnergy - startEnergy)/contparams.getNumberDataPoints();
		double timeForSpectra = contparams.getTotalTime();
		timingGroups.add( new TurboSlitTimingGroup("group1", timeForSpectra, timeForSpectra, 1) );
	}

	public void setDefaults() {
		energyCalibrationPolynomial = "";
		energyCalibrationMinPosition = 900;
		energyCalibrationMaxPosition = 3000;
		sampleName = "Default sample name";
		startEnergy=1000; endEnergy=2000; energyStepSize=10;
		timingGroups = new ArrayList<TurboSlitTimingGroup>();
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

	public void addTimingGroup( TurboSlitTimingGroup group ) {
		timingGroups.add( group );
	}
	public void setTimingGroups( List<TurboSlitTimingGroup> groupList ) {
		timingGroups = new ArrayList<TurboSlitTimingGroup>( groupList );
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

	public TurboXasMotorParameters getMotorParameters() {
		return new TurboXasMotorParameters(this);
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

	public static class CustomDoubleConverter extends DoubleConverter
	{
	    @Override
	    public String toString(Object obj)
	    {
	        return (obj == null ? null : doubleToString((double)obj) );
	    }
	}
	/**
	 * Return new XStream object that can serialize/deserialize {@link TurboXasParameters} objects to/from XML
	 * @return XStream
	 */
	static public XStream getXStream() {
		XStream xstream = new XStream();
		// Most of this can be done automatically from annotations in newer versions of XStream > 1.3...
		Annotations.configureAliases(xstream,  TurboXasParameters.class );
		Annotations.configureAliases(xstream,  TurboSlitTimingGroup.class );
		xstream.addImplicitCollection(TurboXasParameters.class, "timingGroups");
		xstream.omitField(TurboXasParameters.class , "logger");
		xstream.registerConverter(new CustomDoubleConverter(), XStream.PRIORITY_VERY_HIGH);

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
			String message = "Problem loading xml data from file "+filePath;
			System.out.println(message+"\n"+e);
			logger.error(message, e);
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
			String message = "Problem saving serialized object to file "+filePath;
			System.out.println( message+"\n"+e );
			logger.error(message,e);
		}
	}

}
