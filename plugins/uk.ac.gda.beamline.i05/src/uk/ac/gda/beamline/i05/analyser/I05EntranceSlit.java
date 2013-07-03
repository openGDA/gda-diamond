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

package uk.ac.gda.beamline.i05.analyser;

import gda.epics.connection.EpicsController;
import gda.factory.Configurable;
import gda.factory.FactoryException;
import gov.aps.jca.event.MonitorEvent;
import gov.aps.jca.event.MonitorListener;
import uk.ac.gda.devices.vgscienta.EntranceSlitInformationProvider;

public class I05EntranceSlit implements EntranceSlitInformationProvider, Configurable, MonitorListener{

	// BL05I-EA-SLITS-01:RBV BL05I-EA-SLITS-01:POS
	private String rawPV, labelPV;
	private EpicsController epicsController;
	
	@Override
	public void configure() throws FactoryException {
		epicsController = EpicsController.getInstance();
//		epicsController.
		
	}
	@Override
	public Number getRawValue() {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public String getLabel() {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public Double getSizeInMM() {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public boolean isCurved() {
		// TODO Auto-generated method stub
		return false;
	}
	@Override
	public void monitorChanged(MonitorEvent ev) {
		// TODO Auto-generated method stub
		
	}

}
