/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package gda.exafs.scan;

import gda.device.CurrentAmplifier;
import gda.factory.Finder;
import gda.jython.scriptcontroller.event.ScriptProgressEvent;
import gda.observable.ObservableComponent;

import java.util.List;

import uk.ac.gda.beans.exafs.DetectorParameters;
import uk.ac.gda.beans.exafs.IonChamberParameters;

/**
 * Sets up detector parameters for I20. Expected that this would be used within a script
 */
public class DetectorParametersManager extends ParametersManager {

	private final DetectorParameters detectorParameters;
	private final ObservableComponent controller;

	public DetectorParametersManager(DetectorParameters detectorParameters, ObservableComponent controller) {
		this.detectorParameters = detectorParameters;
		this.controller = controller;
	}

	@Override
	public void init() throws Exception {
		if (detectorParameters.getIonChambers().get(0).getChangeSensitivity()){
			setAmplifierGain();
		}
	}

	private void setAmplifierGain() throws Exception {

		final List<IonChamberParameters> ionChambers = detectorParameters.getIonChambers();

		controller.notifyIObservers("Status", new ScriptProgressEvent("Setting ion chambers gain"));
		for (IonChamberParameters ic : ionChambers) {
			final CurrentAmplifier amp = Finder.getInstance().find(ic.getCurrentAmplifierName());
			amp.setGain(getGainValue(ic.getGain()));
			amp.setGainUnit(getGainUnit(ic.getGain()));
		}
	}

	private static String getGainValue(String currentAmpSetting) {
		return currentAmpSetting.substring(0, currentAmpSetting.indexOf(' '));
	}

	private static String getGainUnit(String currentAmpSetting) {
		return currentAmpSetting.substring(currentAmpSetting.indexOf(' ') + 1);
	}

}
