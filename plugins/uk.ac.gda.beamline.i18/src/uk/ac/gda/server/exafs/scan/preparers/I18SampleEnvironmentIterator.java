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

import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.Scannable;
import gda.gui.RCPController;
import gda.jython.InterfaceProvider;

import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beans.exafs.i18.AttenuatorParameters;
import uk.ac.gda.beans.exafs.i18.I18SampleParameters;
import uk.ac.gda.beans.exafs.i18.SampleStageParameters;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;

public class I18SampleEnvironmentIterator implements SampleEnvironmentIterator {

	private static final Logger logger = LoggerFactory.getLogger(I18SampleEnvironmentIterator.class);

	private final RCPController rcpController;
	private final Scannable sc_MicroFocusSampleX;
	private final Scannable sc_MicroFocusSampleY;
	private final Scannable sc_sample_z;
	private final EnumPositioner d7a;
	private final EnumPositioner d7b;
	private final Scannable kb_vfm_x;
	private final I18SampleParameters parameters;

	public I18SampleEnvironmentIterator(I18SampleParameters parameters, RCPController rcpController,
			Scannable sc_MicroFocusSampleX, Scannable sc_MicroFocusSampleY, Scannable sc_sample_z, EnumPositioner D7A,
			EnumPositioner D7B, Scannable kb_vfm_x) {
		this.parameters = parameters;
		this.rcpController = rcpController;
		this.sc_MicroFocusSampleX = sc_MicroFocusSampleX;
		this.sc_MicroFocusSampleY = sc_MicroFocusSampleY;
		this.sc_sample_z = sc_sample_z;
		d7a = D7A;
		d7b = D7B;
		this.kb_vfm_x = kb_vfm_x;
	}

	@Override
	public int getNumberOfRepeats() {
		return 1;
	}

	@Override
	public void next() throws DeviceException, InterruptedException {

		rcpController.openPerspective("org.diamond.exafs.ui.PlottingPerspective");

		SampleStageParameters stage = parameters.getSampleStageParameters();
		log( "Moving stage x to:" + stage.getX());
		sc_MicroFocusSampleX.moveTo(stage.getX());
		log( "Moving stage y to:" + stage.getY());
		sc_MicroFocusSampleY.moveTo(stage.getY());
		log( "Moving stage z to:" + stage.getZ());
		sc_sample_z.moveTo(stage.getZ());

		AttenuatorParameters att1 = parameters.getAttenuatorParameter1();
		AttenuatorParameters att2 = parameters.getAttenuatorParameter2();
		
		log( "Moving D7A to:" + att1.getSelectedPosition());
		d7a.moveTo(att1.getSelectedPosition());
		log( "Moving D7B to:" + att2.getSelectedPosition());
		d7b.moveTo(att2.getSelectedPosition());
		
		if (parameters.isVfmxActive()){
			log( "Moving kb_vfm_x to:" + parameters.getVfmx());
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
