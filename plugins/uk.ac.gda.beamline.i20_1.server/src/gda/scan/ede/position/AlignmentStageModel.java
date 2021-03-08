/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package gda.scan.ede.position;

import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

import com.thoughtworks.xstream.XStream;
import com.thoughtworks.xstream.io.xml.DomDriver;

/**
 * This is used for serialization of alignment stage locations to/from XML using XStream
 * by {@link AlignmentStageCalibrationView}
 */
public class AlignmentStageModel {

	private List<Position> positions = Collections.emptyList();

	public AlignmentStageModel() {
		// No args constructor - for serialization
	}
	public AlignmentStageModel(Collection<Location> deviceLocations) {
		setDeviceLocations(deviceLocations);
	}

	public List<Location> getDeviceLocations() {
		return positions
				.stream()
				.map(Position::getLocation)
				.collect(Collectors.toList());
	}

	public void setDeviceLocations(Collection<Location> collection) {
		this.positions = collection
				.stream().map(Position::new)
				.collect(Collectors.toList());
	}

	public List<Position> getPositions() {
		return positions;
	}

	public String toXml() {
		return getXStream().toXML(this);
	}

	public static AlignmentStageModel fromXml(String xmlString) {
		return (AlignmentStageModel) getXStream().fromXML(xmlString);
	}

	private static XStream getXStream() {
		XStream xstream = new XStream( new DomDriver());
		xstream.setClassLoader(AlignmentStageModel.class.getClassLoader());
		xstream.addImplicitCollection(AlignmentStageModel.class, "positions");
		xstream.alias("Position", Position.class);
		xstream.alias("AlignmentStageModel", AlignmentStageModel.class);
		return xstream;
	}

	protected static class Position {

		private String name = "";
		private String displayLabel = "";

		private double xPosition = 0.0;
		private double yPosition = 0.0;
		private boolean relative;

		public Position() {
		}

		public Position(Location location) {
			name = location.getName();
			displayLabel = location.getDisplayLabel();
			xPosition = location.getxPosition();
			yPosition = location.getyPosition();
		}

		public Location getLocation() {
			return Location.create(name, displayLabel, xPosition, yPosition);
		}

		public String getName() {
			return name;
		}

		public void setName(String name) {
			this.name = name;
		}

		public String getDisplayLabel() {
			return displayLabel;
		}

		public void setDisplayLabel(String displayLabel) {
			this.displayLabel = displayLabel;
		}

		public double getxPosition() {
			return xPosition;
		}

		public void setxPosition(double xPosition) {
			this.xPosition = xPosition;
		}

		public double getyPosition() {
			return yPosition;
		}

		public void setyPosition(double yPosition) {
			this.yPosition = yPosition;
		}

		public boolean isRelative() {
			return relative;
		}

		public void setRelative(boolean relative) {
			this.relative = relative;
		}
	}
}
