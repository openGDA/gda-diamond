/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i20.scannable;

import java.io.IOException;

public interface ILakeshore340 {
	void configure();
	Double getTempReadback(int index) throws IOException;
	void setSetpoint(Double setpoint) throws IOException;
	Double getSetpoint() throws IOException;
	void setRange(Double range) throws IOException;
	Double getRange() throws IOException;
	String getRangeString() throws IOException;
	void setControlmode(Double controlmode) throws IOException;
	Double getControlmode() throws IOException;
	void setManualOutput(Double manualOutput) throws IOException;
	Double getManualOutput() throws IOException;
	void setpValue(Double pValue) throws IOException;
	Double getpValue() throws IOException;
	void setiValue(Double iValue) throws IOException;
	Double getiValue() throws IOException;
	void setdValue(Double dValue) throws IOException;
	Double getdValue() throws IOException;
	void setSetpointControl(double setpointControl) throws IOException;
}
