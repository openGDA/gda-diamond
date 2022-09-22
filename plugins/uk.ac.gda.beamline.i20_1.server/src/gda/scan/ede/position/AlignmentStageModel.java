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

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.dataformat.xml.XmlMapper;

import gda.exafs.xml.XmlSerializationMappers;

/**
 * This is used for serialization of alignment stage locations to/from XML
 * by {@link AlignmentStageCalibrationView}
 */
public class AlignmentStageModel {

	@JsonProperty("Position")
	private List<Position> positions = Collections.emptyList();

	public AlignmentStageModel() {
		// No args constructor - for serialization
	}
	public AlignmentStageModel(Collection<Location> deviceLocations) {
		setDeviceLocations(deviceLocations);
	}

	@JsonIgnore
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

	public void setPositions(List<Position> positions) {
		this.positions = new ArrayList<>(positions);
	}

	public List<Position> getPositions() {
		return positions;
	}

	public String toXml() throws IOException {
		try {
			return getXmlMapper().writeValueAsString(this);
		} catch (JsonProcessingException e) {
			throw new IOException("Problem converting "+AlignmentStageModel.class.getSimpleName()+" to string", e);
		}
	}

	public static AlignmentStageModel fromXml(String xmlString) throws IOException {
		try {
			return getXmlMapper().readValue(xmlString, AlignmentStageModel.class);
		} catch (JsonProcessingException e) {
			throw new IOException("Problem converting Json string to "+AlignmentStageModel.class.getSimpleName()+" object", e);
		}
	}

	private static XmlMapper getXmlMapper() {
		return XmlSerializationMappers.getXmlMapper();
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

		@JsonIgnore
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
