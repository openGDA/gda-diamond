/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.view;

import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.daq.beamline.k11.view.control.StageController;
import uk.ac.gda.tomography.base.TomographyParameters;
import uk.ac.gda.tomography.scan.editor.view.TomographyConfigurationCompositeFactory;
import uk.ac.gda.tomography.ui.controller.TomographyPerspectiveController;
import uk.ac.gda.ui.tool.spring.SpringApplicationContextProxy;

/**
 * This Composite allows to edit a {@link TomographyParameters} object.
 *
 * @author Maurizio Nagni
 */
public class TomographyConfigurationView extends ViewPart {

	public static final String ID = "uk.ac.diamond.daq.beamline.k11.view.TomographyConfigurationView";
	private static final Logger logger = LoggerFactory.getLogger(TomographyConfigurationView.class);

	@Override
	public void createPartControl(Composite parent) {
		new TomographyConfigurationCompositeFactory(getPerspectiveController().getTomographyAcquisitionController(),
				getStageController()).createComposite(parent, SWT.NULL);
	}

	@Override
	public void setFocus() {
		// Do not necessary
	}

	private TomographyPerspectiveController getPerspectiveController() {
		return SpringApplicationContextProxy.getBean(TomographyPerspectiveController.class);
	}

	private StageController getStageController() {
		return SpringApplicationContextProxy.getBean(StageController.class);
	}
}
