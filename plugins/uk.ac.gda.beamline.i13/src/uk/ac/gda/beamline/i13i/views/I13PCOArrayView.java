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

package uk.ac.gda.beamline.i13i.views;

import java.util.List;
import java.util.Vector;

import org.eclipse.jface.action.IAction;

import uk.ac.gda.epics.adviewer.views.ADActionUtils;
import uk.ac.gda.epics.adviewer.views.TwoDArrayView;

public class I13PCOArrayView extends TwoDArrayView {

	final static String Id = "uk.ac.gda.beamline.i13i.PCOAreaDetectorArrayView";

	public I13PCOArrayView() {
		super("i13");
	}

	@Override
	protected void createShowViewAction() {
		List<IAction> actions = new Vector<IAction>();
		{
			actions.add(ADActionUtils.addShowViewAction("Show Stats", I13PCOHistogramView.Id, null, "Show stats view for selected camera",
					uk.ac.gda.epics.adviewer.Activator.getHistogramViewImage()));
			actions.add(ADActionUtils.addShowViewAction("Show MPeg", I13MJPegView.Id, null, "Show MPeg view for selected camera",
					uk.ac.gda.epics.adviewer.Activator.getMJPegViewImage()));

		}
		for (IAction iAction : actions) {
			getViewSite().getActionBars().getToolBarManager().add(iAction);
		}
	}

}
