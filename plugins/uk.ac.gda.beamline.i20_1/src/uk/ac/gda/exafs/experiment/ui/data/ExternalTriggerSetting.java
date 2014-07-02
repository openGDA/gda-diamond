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

package uk.ac.gda.exafs.experiment.ui.data;

import org.eclipse.core.databinding.observable.list.ObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;

import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.exafs.experiment.trigger.TFGTrigger;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject;

public class ExternalTriggerSetting extends ObservableModel {
	private final TFGTrigger tfgTrigger;
	private final ObservableList sampleEnvironment;

	public ExternalTriggerSetting(TFGTrigger tfgTrigger) {
		this.tfgTrigger = tfgTrigger;
		sampleEnvironment = new WritableList(tfgTrigger.getSampleEnvironment(), TriggerableObject.class);
	}

	public TFGTrigger getTfgTrigger() {
		return tfgTrigger;
	}

	public ObservableList getSampleEnvironment() {
		return sampleEnvironment;
	}
}
