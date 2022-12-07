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

package uk.ac.gda.server.exafs.scan.preparers;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.eclipse.scanning.api.points.MapPosition;
import org.eclipse.scanning.api.scan.ScanningException;
import org.eclipse.scanning.api.scan.event.IPositioner;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.ServiceHolder;
import gda.device.DeviceException;
import uk.ac.gda.beans.exafs.ScannableConfiguration;
import uk.ac.gda.beans.exafs.i18.I18SampleParameters;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;

public class I18SampleEnvironmentIterator implements SampleEnvironmentIterator {

	private static final Logger logger = LoggerFactory.getLogger(I18SampleEnvironmentIterator.class);
	private final I18SampleParameters parameters;

	public I18SampleEnvironmentIterator(I18SampleParameters parameters) {
		this.parameters = parameters;
	}

	@Override
	public int getNumberOfRepeats() {
		return 1;
	}

	@Override
	public void next() throws DeviceException, InterruptedException {
		try {
			IPositioner positioner = ServiceHolder.getRunnableDeviceService().createPositioner(I18SampleEnvironmentIterator.class.getName());
			Map<String, Object> position = getPositionMap(parameters.getScannableConfigurations());
			positioner.setPosition(new MapPosition(position));
		} catch (ScanningException e) {
			logger.error("Error moving to scan start position", e);
		}

	}

	private Map<String, Object> getPositionMap(List<ScannableConfiguration> scannableConfigurations) {
		return scannableConfigurations.stream()
			.collect(Collectors.toMap(ScannableConfiguration::getScannableName, ScannableConfiguration::getPosition));
	}

	@Override
	public void resetIterator() {
		// not applicable
	}

	@Override
	public String getNextSampleName() {
		return parameters.getName();
	}

	@Override
	public List<String> getNextSampleDescriptions() {
		return parameters.getDescriptions();
	}

}
