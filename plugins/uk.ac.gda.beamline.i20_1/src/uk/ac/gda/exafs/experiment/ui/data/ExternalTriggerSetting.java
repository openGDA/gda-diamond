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

import org.eclipse.core.databinding.observable.list.IListChangeListener;
import org.eclipse.core.databinding.observable.list.ListChangeEvent;
import org.eclipse.core.databinding.observable.list.ListDiffVisitor;
import org.eclipse.core.databinding.observable.list.ObservableList;
import org.eclipse.core.databinding.observable.list.WritableList;

import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.exafs.experiment.trigger.TFGTrigger;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject;

public class ExternalTriggerSetting extends ObservableModel {
	private final TFGTrigger tfgTrigger;
	private final ObservableList sampleEnvironment;

	public ExternalTriggerSetting(final TFGTrigger tfgTrigger) {
		this.tfgTrigger = tfgTrigger;
		sampleEnvironment = new WritableList(tfgTrigger.getSampleEnvironment(), TriggerableObject.class);
		// TODO Refactor this
		updateListeners(tfgTrigger);
	}

	private void updateListeners(final TFGTrigger tfgTrigger) {
		for (TriggerableObject obj : tfgTrigger.getSampleEnvironment()) {
			obj.addPropertyChangeListener(tfgTrigger.getTotalTimeChangeListener());
		}
		sampleEnvironment.addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				event.diff.accept(new ListDiffVisitor() {
					@Override
					public void handleRemove(int index, Object element) {
						((TriggerableObject) element).addPropertyChangeListener(tfgTrigger.getTotalTimeChangeListener());
						tfgTrigger.updateTotalTime();
					}

					@Override
					public void handleAdd(int index, Object element) {
						((TriggerableObject) element).removePropertyChangeListener(tfgTrigger.getTotalTimeChangeListener());
						tfgTrigger.updateTotalTime();
					}
				});
			}
		});
	}

	public TFGTrigger getTfgTrigger() {
		return tfgTrigger;
	}

	public ObservableList getSampleEnvironment() {
		return sampleEnvironment;
	}
}
