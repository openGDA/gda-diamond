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
import gov.aps.jca.Channel;
import gov.aps.jca.dbr.DBR_Int;
import gov.aps.jca.event.MonitorEvent;
import gov.aps.jca.event.MonitorListener;

import java.util.Vector;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.devices.vgscienta.EntranceSlitInformationProvider;

public class I05EntranceSlit implements EntranceSlitInformationProvider, Configurable, MonitorListener{
	private static final Logger logger = LoggerFactory.getLogger(I05EntranceSlit.class);

	// BL05I-EA-SLITS-01:POS
	private String labelPV = "BL05I-EA-SLITS-01";
	private EpicsController epicsController;
	private Number rawValue;
	private Double size;
	private String shape;
	private String label;
	private Vector<String> positions = new Vector<String>(12);
	
	@Override
	public void configure() throws FactoryException {
		epicsController = EpicsController.getInstance();
		try {
			String[] channelNames = new String[12];
			channelNames[0] = "ZRST";
			channelNames[1] = "ONST";
			channelNames[2] = "TWST";
			channelNames[3] = "THST";
			channelNames[4] = "FRST";
			channelNames[5] = "FVST";
			channelNames[6] = "SXST";
			channelNames[7] = "SVST";
			channelNames[8] = "EIST";
			channelNames[9] = "NIST";
			channelNames[10] = "TEST";
			channelNames[11] = "ELST";

			// loop over the pv's in the record
			for (int i = 0; i < 12; i++) {
				try {
					Channel thisStringChannel = epicsController.createChannel(labelPV + ":SELECT." + channelNames[i]);
					String positionName = epicsController.cagetString(thisStringChannel);
					epicsController.destroy(thisStringChannel);

//					// if the string is not "" then save it to the array
//					if (positionName.compareTo("") != 0) {
					positions.add(positionName);
//					}
				} catch (Throwable th) {
					logger.error("failed to get position name for " + labelPV);
				}
			}
			
			epicsController.addMonitor(epicsController.createChannel(labelPV+":POS"));
		} catch (Exception e) {
			throw new FactoryException("error setting up entract slit monitoring", e);
		}
	}
	
	@Override
	public Number getRawValue() {
		return rawValue;
	}

	@Override
	public String getLabel() {
		return label;
	}

	@Override
	public Double getSizeInMM() {
		return size;
	}

	@Override
	public String getShape() {
		return shape;
	}
	@Override
	public void monitorChanged(MonitorEvent ev) {
		if (ev.getDBR() instanceof DBR_Int) {
			int pos = ((DBR_Int) ev.getDBR()).getIntValue()[0];
			label = positions.get(pos);
			String[] strings = label.split(" ");
			rawValue = Integer.valueOf(strings[0]);
			size = Double.valueOf(strings[1]);
			shape = strings[2];
			logger.debug(String.format("processed updates for entrance slit %s: %s",labelPV, label));
		}
	}

	public String getLabelPV() {
		return labelPV;
	}

	public void setLabelPV(String labelPV) {
		this.labelPV = labelPV;
	}
}