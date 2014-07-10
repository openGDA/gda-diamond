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

package uk.ac.gda.exafs.experiment.trigger;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject.TriggerOutputPort;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentUnit;

import com.google.gson.annotations.Expose;

public class TFGTrigger extends ObservableModel implements Serializable {
	// The first 2 is reserved for photonShutter and detector
	private static final int MAX_PORTS_FOR_SAMPLE_ENV = TriggerableObject.TriggerOutputPort.values().length - 2;

	public static final ExperimentUnit DEFAULT_DELAY_UNIT = ExperimentUnit.SEC;
	public static final double DEFAULT_PULSE_WIDTH_IN_SEC = 0.001d;

	@Expose
	private final List<TriggerableObject> sampleEnvironment = new ArrayList<TriggerableObject>(MAX_PORTS_FOR_SAMPLE_ENV);
	@Expose
	private final PhotonShutter photonShutter = new PhotonShutter();
	@Expose
	private final XhDetector detector = new XhDetector();

	public TriggerableObject getPhotonShutter() {
		return photonShutter;
	}
	public TriggerableObject getDetector() {
		return detector;
	}
	public List<TriggerableObject> getSampleEnvironment() {
		return sampleEnvironment;
	}
	public TriggerableObject createNewSampleEnvEntry() throws Exception {
		if (sampleEnvironment.size() == MAX_PORTS_FOR_SAMPLE_ENV) {
			throw new Exception("Maxium ports reached: " + MAX_PORTS_FOR_SAMPLE_ENV);
		}
		TriggerableObject obj = new TriggerableObject();
		obj.setName("Default");
		obj.setTriggerPulseLength(DEFAULT_PULSE_WIDTH_IN_SEC);
		obj.setTriggerDelay(0.1);
		obj.setTriggerOutputPort(TriggerOutputPort.values()[sampleEnvironment.size() + 2]);
		return obj;
	}
}