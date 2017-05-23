/*-
 * Copyright © 2016 Diamond Light Source Ltd.
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

package uk.ac.gda.ui.views.synoptic;

import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SynopticView extends ViewPart {
	public static final String Id = "uk.ac.gda.ui.views.synoptic.SynopticView";
	private static final Logger logger = LoggerFactory.getLogger(SampleStageView.class);

	HardwareDisplayComposite viewComposite;

	public SynopticView() {
		super();
	}

	@Override
	public void createPartControl(Composite parent) {
		String secondaryId = getViewSite().getSecondaryId();

		if (secondaryId.equals(XesStageView.ID)) {
			viewComposite = new XesStageView(parent, SWT.NONE);
		} else if (secondaryId.equals(SampleStageView.ID)) {
			viewComposite = new SampleStageView(parent, SWT.NONE);
		} else if (secondaryId.equals(XasTableView.ID)) {
			viewComposite = new XasTableView(parent, SWT.NONE);
		} else {
			logger.warn("Cannot create view for {}", secondaryId);
		}
		// Set label used in tab for view
		if (viewComposite != null) {
			setPartName(viewComposite.getViewName());
		}
	}

	@Override
	public void setFocus() {
		if (viewComposite != null) {
			viewComposite.setFocus();
		}
	}
}