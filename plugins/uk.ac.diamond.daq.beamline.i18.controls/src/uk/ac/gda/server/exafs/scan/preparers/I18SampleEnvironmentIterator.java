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
import gda.gui.RCPController;
import gda.jython.InterfaceProvider;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.i18.I18SampleParameters;
import uk.ac.gda.beans.exafs.i18.SampleStageParameters;
import uk.ac.gda.beans.microfocus.MicroFocusScanParameters;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;

public class I18SampleEnvironmentIterator implements SampleEnvironmentIterator {

	private static final Logger logger = LoggerFactory.getLogger(I18SampleEnvironmentIterator.class);

	private final RCPController rcpController;
	private final Scannable stage_x;
	private final Scannable stage_y;
	private final Scannable stage_z;
	private final Scannable kb_vfm_x;
	private final I18SampleParameters parameters;

	private IScanParameters scanParameters;

	// TODO all these scannables should be removed from the constructor
	// and retrieved through the Finder using the names in I18SampleParameters
	public I18SampleEnvironmentIterator(IScanParameters scanParameters, I18SampleParameters parameters,
 RCPController rcpController, Scannable stage_x,
			Scannable stage_y, Scannable stage_z, Scannable kb_vfm_x) {
		this.scanParameters = scanParameters;
		this.parameters = parameters;
		this.rcpController = rcpController;
		this.stage_x = stage_x;
		this.stage_y = stage_y;
		this.stage_z = stage_z;
		this.kb_vfm_x = kb_vfm_x;
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
			rcpController.openPerspective("org.diamond.exafs.ui.PlottingPerspective");

			SampleStageParameters stage = parameters.getSampleStageParameters();
			log("Moving stage x to:" + stage.getX());
			stage_x.moveTo(stage.getX());
			log("Moving stage y to:" + stage.getY());
			stage_y.moveTo(stage.getY());
			log("Moving stage z to:" + stage.getZ());
			stage_z.moveTo(stage.getZ());
		}

		Finder finder = Finder.getInstance();

		parameters.getAttenuators().forEach(bean -> {
			log("Moving " + bean.getName() + " to:" + bean.getSelectedPosition());
			Scannable attenuator = finder.find(bean.getName());
			try {
				if (attenuator != null) attenuator.moveTo(bean.getSelectedPosition());
			} catch (DeviceException e) {
				logger.error("Error moving attenuator {}", bean.getName(), e);
			}
		});

		if (parameters.isVfmxActive()) {
			log("Moving kb_vfm_x to:" + parameters.getVfmx());
			kb_vfm_x.moveTo(parameters.getVfmx());
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

	private void log(String msg) {
		logger.info(msg);
		InterfaceProvider.getTerminalPrinter().print(msg);
	}

}
