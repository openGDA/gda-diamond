/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

import java.io.Serializable;

import org.apache.commons.configuration.PropertiesConfiguration;

import com.google.gson.Gson;

import uk.ac.gda.beans.ObservableModel;

public class Location extends ObservableModel implements Serializable {

	private static final long serialVersionUID = 1L;
	private String name = "";
	private String displayLabel = "";

	public static final String X_POS_PROP_NAME = "xPosition";
	private double xPosition = 0.0;
	public static final String Y_POS_PROP_NAME = "yPosition";
	private double yPosition = 0.0;
	public static final String RELATIVE_PROP_NAME = "relative";
	private boolean relative;

	private static final Gson GSON = new Gson();

	public Location(String name, String label) {
		this.name = name;
		this.displayLabel = label;
	}

	public static Location create(String name, String label, double xPos, double yPos) {
		Location loc = new Location(name,  label);
		loc.setxPosition(xPos);
		loc.setyPosition(yPos);
		return loc;
	}

	public double getxPosition() {
		return xPosition;
	}
	public void setxPosition(double value) {
		this.firePropertyChange(X_POS_PROP_NAME, xPosition, xPosition = value);
	}
	public double getyPosition() {
		return yPosition;
	}
	public void setyPosition(double value) {
		this.firePropertyChange(Y_POS_PROP_NAME, yPosition, yPosition = value);
	}
	public void setRelative(boolean value) {
		this.firePropertyChange(Y_POS_PROP_NAME, relative, relative = value);
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

	public static Location fromJson(String locationString) {
		Location loc = GSON.fromJson(locationString, Location.class);
		// ObservableModel part of Location is not recreated when de-serializing from Json
		// - create new Location to correctly create new object :
		return Location.create(loc.getName(), loc.getDisplayLabel(), loc.getxPosition(), loc.getyPosition());
	}

	public static String toJson(Location location) {
		StringBuilder json = new StringBuilder();
		 GSON.toJson(location, json);
		 return json.toString();
	}
	public String toJson() {
		return toJson(this);
	}

	public void save(PropertiesConfiguration config) {
		config.setProperty(getName(), toJson());
	}

	@Override
	public String toString() {
		return "Location [name=" + name + ", displayLabel=" + displayLabel + ", xPosition=" + xPosition + ", yPosition="
				+ yPosition + ", relative=" + relative + "]";
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + ((displayLabel == null) ? 0 : displayLabel.hashCode());
		result = prime * result + ((name == null) ? 0 : name.hashCode());
		result = prime * result + (relative ? 1231 : 1237);
		long temp;
		temp = Double.doubleToLongBits(xPosition);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		temp = Double.doubleToLongBits(yPosition);
		result = prime * result + (int) (temp ^ (temp >>> 32));
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
		Location other = (Location) obj;
		if (displayLabel == null) {
			if (other.displayLabel != null)
				return false;
		} else if (!displayLabel.equals(other.displayLabel))
			return false;
		if (name == null) {
			if (other.name != null)
				return false;
		} else if (!name.equals(other.name))
			return false;
		if (relative != other.relative)
			return false;
		if (Double.doubleToLongBits(xPosition) != Double.doubleToLongBits(other.xPosition))
			return false;
		if (Double.doubleToLongBits(yPosition) != Double.doubleToLongBits(other.yPosition))
			return false;
		return true;
	}
}
