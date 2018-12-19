/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i14.views;

import java.util.Collections;
import java.util.List;

import org.eclipse.scanning.api.points.models.IScanPathModel;
import org.eclipse.swt.widgets.Composite;

import uk.ac.diamond.daq.mapping.api.IMappingExperimentBean;
import uk.ac.diamond.daq.mapping.api.IScanModelWrapper;
import uk.ac.diamond.daq.mapping.ui.experiment.StatusPanel;

/**
 * Version of {@link StatusPanel} to use in XANES scanning GUI
 * <p>
 * As the energy scannable is not added to the GDA mapping bean, the standard StatusPanel does not know anything about
 * it. This version overrides getOuterScannables() so that the XANES GUI can set the outer scannable(s) (typically just
 * the energy scannable).
 */
public class XanesStatusPanel extends StatusPanel {

	private List<IScanModelWrapper<IScanPathModel>> outerScannables = Collections.emptyList();

	public XanesStatusPanel(Composite parent, int style, IMappingExperimentBean mappingBean) {
		super(parent, style, mappingBean);
	}

	public void setOuterScannables(List<IScanModelWrapper<IScanPathModel>> outerScannables) {
		this.outerScannables = outerScannables;
	}

	@Override
	protected List<IScanModelWrapper<IScanPathModel>> getOuterScannables() {
		return outerScannables;
	}
}
