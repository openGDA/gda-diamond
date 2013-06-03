/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.ui.data;

import java.io.Serializable;
import java.net.URL;
import java.util.List;
import java.util.Vector;

import uk.ac.gda.util.beans.xml.XMLHelpers;

/**
 * Defines the collection parameters for linear or cycling experiments on the I20-1 Energy Dispersive EXAFS (EDE)
 * beamline.
 */
public class EdeScanParameters implements Serializable {

	public static final String TRIG_NONE = "none";
	public static final String TRIG_GROUP_BEFORE = "Group start, before delay";
	public static final String TRIG_GROUP_AFTER = "Group start, after delay";
	public static final String TRIG_FRAME_BEFORE = "Frame start, before delay";
	public static final String TRIG_FRAME_AFTER = "Frame start, after delay";
	public static final String TRIG_SCAN_BEFORE = "Scan start, before delay";
	// public static final String TRIG_INTE = "Integration";
	// public static final String TRIG_MID_SCAN = "Mid-scan";

	public static final String[] OUTPUT_TRIG_CHOICES = new String[] { TRIG_NONE, TRIG_GROUP_BEFORE, TRIG_GROUP_AFTER,
			TRIG_FRAME_BEFORE, TRIG_FRAME_AFTER, TRIG_SCAN_BEFORE };

	static public final URL mappingURL = EdeScanParameters.class.getResource("EdeParametersMapping.xml");
	static public final URL schemaURL = EdeScanParameters.class.getResource("EdeParametersMapping.xsd");

	public static EdeScanParameters createFromXML(String filename) throws Exception {
		return (EdeScanParameters) XMLHelpers.createFromXML(mappingURL, EdeScanParameters.class, schemaURL, filename);
	}

	public static void writeToXML(EdeScanParameters scanParameters, String filename) throws Exception {
		XMLHelpers.writeToXML(mappingURL, scanParameters, filename);
	}

	// for repeatableExperiments
	private Integer numberOfRepetitions = 1; // number of times to repeat the sequence of timingGroups, between bookend
												// I0 data
												// collections

	// the timing groups
	private List<TimingGroup> timingGroups = new Vector<TimingGroup>();

	// the TTL outputs. This is fixed per experiment and cannot be configured for each group
	private String outputsChoice0 = OUTPUT_TRIG_CHOICES[0];
	private String outputsChoice1 = OUTPUT_TRIG_CHOICES[0];
	private String outputsChoice2 = OUTPUT_TRIG_CHOICES[0];
	private String outputsChoice3 = OUTPUT_TRIG_CHOICES[0];
	private String outputsChoice4 = OUTPUT_TRIG_CHOICES[0];
	private String outputsChoice5 = OUTPUT_TRIG_CHOICES[0];
	private String outputsChoice6 = OUTPUT_TRIG_CHOICES[0];
	private String outputsChoice7 = OUTPUT_TRIG_CHOICES[0];

	private double outputsWidth0 = 0;
	private double outputsWidth1 = 0;
	private double outputsWidth2 = 0;
	private double outputsWidth3 = 0;
	private double outputsWidth4 = 0;
	private double outputsWidth5 = 0;
	private double outputsWidth6 = 0;
	private double outputsWidth7 = 0;
	
	

	public int getTotalNumberOfFrames() {
		int sum = 0;
		
		for (TimingGroup group : getGroups()){
			sum += group.getNumberOfFrames();
		}
		
		return sum;
	}



	public List<TimingGroup> getGroups() {
		return timingGroups;
	}

	public void addGroup(TimingGroup newGroup) {
		this.timingGroups.add(newGroup);
	}

	public void setGroups(List<TimingGroup> group) {
		this.timingGroups = group;
	}

	public void setNumberOfRepetitions(Integer numberOfRepetitions) {
		this.numberOfRepetitions = numberOfRepetitions;
	}

	public Integer getNumberOfRepetitions() {
		return numberOfRepetitions;
	}

	public List<TimingGroup> getTimingGroups() {
		return timingGroups;
	}

	public void setTimingGroups(List<TimingGroup> timingGroups) {
		this.timingGroups = timingGroups;
	}

	public String getOutputsChoice0() {
		return outputsChoice0;
	}

	public void setOutputsChoice0(String outputsChoice0) {
		this.outputsChoice0 = outputsChoice0;
	}

	public String getOutputsChoice1() {
		return outputsChoice1;
	}

	public void setOutputsChoice1(String outputsChoice1) {
		this.outputsChoice1 = outputsChoice1;
	}

	public String getOutputsChoice2() {
		return outputsChoice2;
	}

	public void setOutputsChoice2(String outputsChoice2) {
		this.outputsChoice2 = outputsChoice2;
	}

	public String getOutputsChoice3() {
		return outputsChoice3;
	}

	public void setOutputsChoice3(String outputsChoice3) {
		this.outputsChoice3 = outputsChoice3;
	}

	public String getOutputsChoice4() {
		return outputsChoice4;
	}

	public void setOutputsChoice4(String outputsChoice4) {
		this.outputsChoice4 = outputsChoice4;
	}

	public String getOutputsChoice5() {
		return outputsChoice5;
	}

	public void setOutputsChoice5(String outputsChoice5) {
		this.outputsChoice5 = outputsChoice5;
	}

	public String getOutputsChoice6() {
		return outputsChoice6;
	}

	public void setOutputsChoice6(String outputsChoice6) {
		this.outputsChoice6 = outputsChoice6;
	}

	public String getOutputsChoice7() {
		return outputsChoice7;
	}

	public void setOutputsChoice7(String outputsChoice7) {
		this.outputsChoice7 = outputsChoice7;
	}

	public double getOutputsWidth0() {
		return outputsWidth0;
	}

	public void setOutputsWidth0(double outputsWidth0) {
		this.outputsWidth0 = outputsWidth0;
	}

	public double getOutputsWidth1() {
		return outputsWidth1;
	}

	public void setOutputsWidth1(double outputsWidth1) {
		this.outputsWidth1 = outputsWidth1;
	}

	public double getOutputsWidth2() {
		return outputsWidth2;
	}

	public void setOutputsWidth2(double outputsWidth2) {
		this.outputsWidth2 = outputsWidth2;
	}

	public double getOutputsWidth3() {
		return outputsWidth3;
	}

	public void setOutputsWidth3(double outputsWidth3) {
		this.outputsWidth3 = outputsWidth3;
	}

	public double getOutputsWidth4() {
		return outputsWidth4;
	}

	public void setOutputsWidth4(double outputsWidth4) {
		this.outputsWidth4 = outputsWidth4;
	}

	public double getOutputsWidth5() {
		return outputsWidth5;
	}

	public void setOutputsWidth5(double outputsWidth5) {
		this.outputsWidth5 = outputsWidth5;
	}

	public double getOutputsWidth6() {
		return outputsWidth6;
	}

	public void setOutputsWidth6(double outputsWidth6) {
		this.outputsWidth6 = outputsWidth6;
	}

	public double getOutputsWidth7() {
		return outputsWidth7;
	}

	public void setOutputsWidth7(double outputsWidth7) {
		this.outputsWidth7 = outputsWidth7;
	}

	public double[] getOutputWidths() {
		return new double[] { getOutputsWidth0(), getOutputsWidth1(), getOutputsWidth2(), getOutputsWidth3(),
				getOutputsWidth4(), getOutputsWidth5(), getOutputsWidth6(), getOutputsWidth7() };
	}

	public String[] getOutputsChoices() {
		return new String[] { getOutputsChoice0(), getOutputsChoice1(), getOutputsChoice2(), getOutputsChoice3(),
				getOutputsChoice4(), getOutputsChoice5(), getOutputsChoice6(), getOutputsChoice7() };
	}

	public void clear() {
		timingGroups.clear();
	}

	public String getScannableName() {
		// no moving parts (I know of yet)...
		return null;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + ((numberOfRepetitions == null) ? 0 : numberOfRepetitions.hashCode());
		result = prime * result + ((outputsChoice0 == null) ? 0 : outputsChoice0.hashCode());
		result = prime * result + ((outputsChoice1 == null) ? 0 : outputsChoice1.hashCode());
		result = prime * result + ((outputsChoice2 == null) ? 0 : outputsChoice2.hashCode());
		result = prime * result + ((outputsChoice3 == null) ? 0 : outputsChoice3.hashCode());
		result = prime * result + ((outputsChoice4 == null) ? 0 : outputsChoice4.hashCode());
		result = prime * result + ((outputsChoice5 == null) ? 0 : outputsChoice5.hashCode());
		result = prime * result + ((outputsChoice6 == null) ? 0 : outputsChoice6.hashCode());
		result = prime * result + ((outputsChoice7 == null) ? 0 : outputsChoice7.hashCode());
		long temp;
		temp = Double.doubleToLongBits(outputsWidth0);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		temp = Double.doubleToLongBits(outputsWidth1);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		temp = Double.doubleToLongBits(outputsWidth2);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		temp = Double.doubleToLongBits(outputsWidth3);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		temp = Double.doubleToLongBits(outputsWidth4);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		temp = Double.doubleToLongBits(outputsWidth5);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		temp = Double.doubleToLongBits(outputsWidth6);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		temp = Double.doubleToLongBits(outputsWidth7);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		result = prime * result + ((timingGroups == null) ? 0 : timingGroups.hashCode());
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		EdeScanParameters other = (EdeScanParameters) obj;
		if (numberOfRepetitions == null) {
			if (other.numberOfRepetitions != null)
				return false;
		} else if (!numberOfRepetitions.equals(other.numberOfRepetitions))
			return false;
		if (outputsChoice0 == null) {
			if (other.outputsChoice0 != null)
				return false;
		} else if (!outputsChoice0.equals(other.outputsChoice0))
			return false;
		if (outputsChoice1 == null) {
			if (other.outputsChoice1 != null)
				return false;
		} else if (!outputsChoice1.equals(other.outputsChoice1))
			return false;
		if (outputsChoice2 == null) {
			if (other.outputsChoice2 != null)
				return false;
		} else if (!outputsChoice2.equals(other.outputsChoice2))
			return false;
		if (outputsChoice3 == null) {
			if (other.outputsChoice3 != null)
				return false;
		} else if (!outputsChoice3.equals(other.outputsChoice3))
			return false;
		if (outputsChoice4 == null) {
			if (other.outputsChoice4 != null)
				return false;
		} else if (!outputsChoice4.equals(other.outputsChoice4))
			return false;
		if (outputsChoice5 == null) {
			if (other.outputsChoice5 != null)
				return false;
		} else if (!outputsChoice5.equals(other.outputsChoice5))
			return false;
		if (outputsChoice6 == null) {
			if (other.outputsChoice6 != null)
				return false;
		} else if (!outputsChoice6.equals(other.outputsChoice6))
			return false;
		if (outputsChoice7 == null) {
			if (other.outputsChoice7 != null)
				return false;
		} else if (!outputsChoice7.equals(other.outputsChoice7))
			return false;
		if (Double.doubleToLongBits(outputsWidth0) != Double.doubleToLongBits(other.outputsWidth0))
			return false;
		if (Double.doubleToLongBits(outputsWidth1) != Double.doubleToLongBits(other.outputsWidth1))
			return false;
		if (Double.doubleToLongBits(outputsWidth2) != Double.doubleToLongBits(other.outputsWidth2))
			return false;
		if (Double.doubleToLongBits(outputsWidth3) != Double.doubleToLongBits(other.outputsWidth3))
			return false;
		if (Double.doubleToLongBits(outputsWidth4) != Double.doubleToLongBits(other.outputsWidth4))
			return false;
		if (Double.doubleToLongBits(outputsWidth5) != Double.doubleToLongBits(other.outputsWidth5))
			return false;
		if (Double.doubleToLongBits(outputsWidth6) != Double.doubleToLongBits(other.outputsWidth6))
			return false;
		if (Double.doubleToLongBits(outputsWidth7) != Double.doubleToLongBits(other.outputsWidth7))
			return false;
		if (timingGroups == null) {
			if (other.timingGroups != null)
				return false;
		} else if (!timingGroups.equals(other.timingGroups))
			return false;
		return true;
	}
}
