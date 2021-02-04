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

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import uk.ac.diamond.daq.server.rcpcontroller.RCPController;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.i18.I18SampleParameters;
import uk.ac.gda.beans.exafs.i18.SampleStageParameters;
import uk.ac.gda.beans.microfocus.MicroFocusScanParameters;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;

public class I18SampleEnvironmentIterator implements SampleEnvironmentIterator {

	private static final Logger logger = LoggerFactory.getLogger(I18SampleEnvironmentIterator.class);

	private final RCPController rcpController;
	private final I18SampleParameters parameters;
	private final IScanParameters scanParameters;

	public I18SampleEnvironmentIterator(IScanParameters scanParameters, I18SampleParameters parameters, RCPController rcpController) {
		this.scanParameters = scanParameters;
		this.parameters = parameters;
		this.rcpController = rcpController;
	}

	@Override
	public int getNumberOfRepeats() {
		return 1;
	}

	@Override
	public void next() throws DeviceException, InterruptedException {

		if (scanParameters instanceof MicroFocusScanParameters) {
			rcpController.openPerspective("uk.ac.gda.microfocus.ui.MicroFocusPerspective");
		} else {
			rcpController.openPerspective("uk.ac.gda.beamline.i18.perspective.plotting");

			SampleStageParameters stage = parameters.getSampleStageParameters();

			Scannable x = Finder.find(stage.getXName());
			Scannable y = Finder.find(stage.getYName());
			Scannable z = Finder.find(stage.getZName());

			try {
				logMove(stage.getXName(), stage.getX());
				x.moveTo(stage.getX());

				logMove(stage.getYName(), stage.getY());
				y.moveTo(stage.getY());

				logMove(stage.getZName(), stage.getZ());
				z.moveTo(stage.getZ());
			} catch (DeviceException e) {
				logger.error("Error moving stage", e);
			}
		}

		parameters.getAttenuators().forEach(bean -> {
			logMove(bean.getName(), bean.getSelectedPosition());
			Scannable attenuator = Finder.find(bean.getName());
			try {
				if (attenuator != null) attenuator.moveTo(bean.getSelectedPosition());
			} catch (DeviceException e) {
				logger.error("Error moving attenuator {}", bean.getName(), e);
			}
		});

		if (parameters.isVfmxActive()) {
			log("Moving kb_vfm_x to:" + parameters.getVfmx());
			Scannable kbX = Finder.find("kb_vfm_x");
			kbX.moveTo(parameters.getVfmx());
		}
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

	private void logMove(String scannableName, Object position) {
		log("Moving " + scannableName + " to " + position);
	}

	private void log(String msg) {
		logger.info(msg);
		InterfaceProvider.getTerminalPrinter().print(msg);
	}

}
