/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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
import org.eclipse.swt.widgets.Composite;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beamline.i13i.ADViewerImpl.I13ADControllerImpl;
import uk.ac.gda.beamline.i13i.ADViewerImpl.I13MJPEGViewComposite;
import uk.ac.gda.epics.adviewer.composites.MJPeg;
import uk.ac.gda.epics.adviewer.views.ADActionUtils;
import uk.ac.gda.epics.adviewer.views.MJPegView;

public class I13MJPegView extends MJPegView {
	private static final Logger logger = LoggerFactory.getLogger(I13MJPegView.class);
	protected static final String Id = "uk.ac.gda.beamline.i13i.PCOAreaDetectorLiveView";
	private I13ADControllerImpl i13ADControllerImpl;

	public I13MJPegView() {
		super("i13");
	}

	@Override
	protected MJPeg createPartControlEx(Composite parent) {
		try {
			i13ADControllerImpl = (I13ADControllerImpl) getAdController();
			I13MJPEGViewComposite i13MJPEGViewComposite = new I13MJPEGViewComposite(parent, i13ADControllerImpl.getStagesCompositeFactory());
			i13MJPEGViewComposite.setADController(i13ADControllerImpl, this);
			return i13MJPEGViewComposite.getMJPeg();
		} catch (Exception e) {
			logger.error("Cannot create i13 MJPEG View Composite", e);
		}
		return null;
	}

	@Override
	protected void createShowViewAction() {
		List<IAction> actions = new Vector<IAction>();
		{
			actions.add(ADActionUtils.addShowViewAction("Show Stats", I13PCOHistogramView.Id, null, "Show stats view for selected camera",
					uk.ac.gda.epics.adviewer.Activator.getHistogramViewImage()));
			actions.add(ADActionUtils.addShowViewAction("Show Array", I13PCOArrayView.Id, null, "Show array view for selected camera",
					uk.ac.gda.epics.adviewer.Activator.getTwoDArrayViewImage()));
		}
		for (IAction iAction : actions) {
			getViewSite().getActionBars().getToolBarManager().add(iAction);
		}
	}
}
