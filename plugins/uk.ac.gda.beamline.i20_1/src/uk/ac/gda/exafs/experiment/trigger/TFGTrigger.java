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

import java.util.ArrayList;
import java.util.List;

import uk.ac.gda.beans.ObservableModel;

public class TFGTrigger extends ObservableModel {
	private static final int MAX_PORTS_FOR_SAMPLE_ENV = 6;
	private final List<TriggerableObject> sampleEnvironment = new ArrayList<TriggerableObject>(MAX_PORTS_FOR_SAMPLE_ENV);
	private final PhotonShutter photonShutter = new PhotonShutter();
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

	private static class PhotonShutter extends TriggerableObject {
		public PhotonShutter() {
			this.setName("PhotoShutter");
			this.setTriggerOutputPort(TriggerableObject.TriggerOutputPort.USR_OUT_0);
		}
	}

	private static class XhDetector extends TriggerableObject {
		public XhDetector() {
			this.setName("Xh Detector");
			this.setTriggerOutputPort(TriggerableObject.TriggerOutputPort.USR_OUT_1);
		}
	}
}