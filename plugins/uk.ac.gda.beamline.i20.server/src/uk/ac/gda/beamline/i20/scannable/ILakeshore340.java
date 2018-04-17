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
	public void configure();
	public Double getTempReadback(int index) throws IOException;
	public void setSetpoint(Double setpoint) throws IOException;
	public Double getSetpoint() throws IOException;
	public void setRange(Double range) throws IOException;
	public Double getRange() throws IOException;
	public String getRangeString() throws IOException;
	public void setControlmode(Double controlmode) throws IOException;
	public Double getControlmode() throws IOException;
	public void setManualOutput(Double manualOutput) throws IOException;
	public Double getManualOutput() throws IOException;
	public void setpValue(Double pValue) throws IOException;
	public Double getpValue() throws IOException;
	public void setiValue(Double iValue) throws IOException;
	public Double getiValue() throws IOException;
	public void setdValue(Double dValue) throws IOException;
	public Double getdValue() throws IOException;
	public void setSetpointControl(double setpointControl) throws IOException;
}
