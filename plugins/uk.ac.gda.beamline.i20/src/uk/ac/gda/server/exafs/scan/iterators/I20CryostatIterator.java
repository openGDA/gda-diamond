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

package uk.ac.gda.server.exafs.scan.iterators;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import gda.device.DeviceException;
import gda.device.Scannable;
import uk.ac.gda.beans.exafs.i20.CryostatParameters;
import uk.ac.gda.beans.exafs.i20.CryostatProperties;
import uk.ac.gda.beans.exafs.i20.CryostatSampleDetails;
import uk.ac.gda.beans.exafs.i20.I20SampleParameters;
import uk.ac.gda.doe.DOEUtils;

public class I20CryostatIterator implements SampleEnvironmentIterator {

//	private static final Logger  = LoggerFactory.getLogger(I20CryostatIterator.class);

	private Scannable cryostat;
	private Scannable cryostick_pos;
	private CryostatParameters parameters;
	private Set<I20CryostatIteratorEntry> entries;
	private Iterator<I20CryostatIteratorEntry> entriesIterator;
	private I20CryostatIteratorEntry currentCollection;

	public I20CryostatIterator(I20SampleParameters i20Bean, Scannable cryostat, Scannable cryostick_pos) {
		this.cryostat = cryostat;
		this.cryostick_pos = cryostick_pos;
		this.parameters = i20Bean.getCryostatParameters();

		List<Double> temperatures_array = new ArrayList<Double>();
		if (DOEUtils.isRange(parameters.getTemperature(), null)) {
			temperatures_array = DOEUtils.expand(parameters.getTemperature(), Double.class);
		} else if (DOEUtils.isList(parameters.getTemperature(), null)) {
			String[] temps = parameters.getTemperature().split(",");
			temperatures_array = new ArrayList<Double>();
			for (String temp : temps) {
				temperatures_array.add(Double.parseDouble(temp));
			}
		} else {
			temperatures_array = new ArrayList<Double>();
			temperatures_array.add(Double.parseDouble(parameters.getTemperature()));
		}

		boolean loopSampleFirst = parameters.getLoopChoice() == CryostatProperties.LOOP_OPTION[0];

		entries = new LinkedHashSet<I20CryostatIteratorEntry>();
		if (loopSampleFirst) {
			for (CryostatSampleDetails sample : parameters.getSamples()) {
				for (Double temp : temperatures_array) {
					entries.add(new I20CryostatIteratorEntry(sample,temp));
				}
			}
		} else {
			for (Double temp : temperatures_array) {
				for (CryostatSampleDetails sample : parameters.getSamples()) {
					entries.add(new I20CryostatIteratorEntry(sample,temp));
				}
			}
		}

		entriesIterator = entries.iterator();
	}

	@Override
	public int getNumberOfRepeats() {
		return entries.size();
	}

	@Override
	public void next() throws DeviceException, InterruptedException {
		currentCollection = entriesIterator.next();
//		log("Moving cryostick_pos to " + cryostick_pos);
		Double motorPosition = currentCollection.details.getPosition();
		cryostick_pos.asynchronousMoveTo(motorPosition);
		Double temperature = currentCollection.temperature;
//		log("Setting cryostat to " + temperature + "K...");
		cryostat.asynchronousMoveTo(temperature);
//		log("Waiting for cryostick_pos to move");
		cryostick_pos.waitWhileBusy();
//		log("cryostick_pos move complete.");
//		log("Waiting for Cryostat to set temperature");
		cryostat.waitWhileBusy();
//		log("Cryostat temperature change complete.");
	}

	@Override
	public void resetIterator() {
		entriesIterator = entries.iterator();
	}

	@Override
	public String getNextSampleName() {
		return currentCollection.details.getSample_name();
	}

	@Override
	public List<String> getNextSampleDescriptions() {
		List<String> descriptions = new ArrayList<String>();
		descriptions.add(currentCollection.details.getSampleDescription());
		return descriptions;
	}

//	private void log(String msg) {
//		logger.info(msg);
//		InterfaceProvider.getTerminalPrinter().print(msg);
//	}

	private class I20CryostatIteratorEntry{
		CryostatSampleDetails details;
		Double temperature;
		public I20CryostatIteratorEntry(CryostatSampleDetails details, Double temperature) {
			super();
			this.details = details;
			this.temperature = temperature;
		}
		@Override
		public int hashCode() {
			final int prime = 31;
			int result = 1;
			result = prime * result + getOuterType().hashCode();
			result = prime * result + ((details == null) ? 0 : details.hashCode());
			result = prime * result + ((temperature == null) ? 0 : temperature.hashCode());
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
			I20CryostatIteratorEntry other = (I20CryostatIteratorEntry) obj;
			if (!getOuterType().equals(other.getOuterType()))
				return false;
			if (details == null) {
				if (other.details != null)
					return false;
			} else if (!details.equals(other.details))
				return false;
			if (temperature == null) {
				if (other.temperature != null)
					return false;
			} else if (!temperature.equals(other.temperature))
				return false;
			return true;
		}

		private I20CryostatIterator getOuterType() {
			return I20CryostatIterator.this;
		}
	}

}


