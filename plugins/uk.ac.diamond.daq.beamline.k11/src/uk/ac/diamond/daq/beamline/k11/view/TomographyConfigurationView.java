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

import java.net.URL;
import java.util.Optional;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.rcp.views.AcquisitionCompositeFactoryBuilder;
import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.view.control.StageController;
import uk.ac.diamond.daq.experiment.api.structure.ExperimentController;
import uk.ac.diamond.daq.experiment.api.structure.ExperimentControllerException;
import uk.ac.gda.api.acquisition.AcquisitionController;
import uk.ac.gda.api.acquisition.AcquisitionControllerException;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.composites.AcquisitionsBrowserCompositeFactory;
import uk.ac.gda.tomography.base.TomographyParameterAcquisition;
import uk.ac.gda.tomography.base.TomographyParameters;
import uk.ac.gda.tomography.browser.TomoBrowser;
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

	private AcquisitionController<TomographyParameterAcquisition> controller;

	@Override
	public void createPartControl(Composite parent) {
		controller = getPerspectiveController().getTomographyAcquisitionController();
		AcquisitionCompositeFactoryBuilder builder = new AcquisitionCompositeFactoryBuilder();
		builder.addTopArea(getTopArea());
		builder.addBottomArea(getBottomArea());
		builder.addSaveSelectionListener(getSaveListener());
		builder.addRunSelectionListener(getRunListener());
		builder.build().createComposite(parent, SWT.NONE);
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

	private CompositeFactory getTopArea() {
		return new TomographyConfigurationCompositeFactory(controller, getStageController());
	}

	private CompositeFactory getBottomArea() {
		return new AcquisitionsBrowserCompositeFactory<TomographyParameterAcquisition>(new TomoBrowser());
	}

	private SelectionListener getSaveListener() {
		return new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent event) {
				try {
					controller.saveAcquisitionConfiguration();
				} catch (AcquisitionControllerException e) {
					UIHelper.showError("Cannot save the file", e);
					logger.error("Cannot save the file", e);
				}
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent event) {
				// not necessary
			}
		};
	}

	private SelectionListener getRunListener() {
		return new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent event) {
				try {
					controller.runAcquisition(getOutputPath());
				} catch (AcquisitionControllerException e) {
					UIHelper.showError("Run Acquisition", e.getMessage());
					logger.error("Cannot run the acquisition", e);
				} catch (ExperimentControllerException e) {
					UIHelper.showError("Run Acquisition", e.getMessage());
					logger.error(e.getMessage(), e);
				}
			}

			private URL getOutputPath() throws ExperimentControllerException {
				if (getExperimentController().isPresent()) {
					return getExperimentController().get().prepareAcquisition(controller.getAcquisition().getName());
				}
				return null;
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent event) {
				logger.debug("widgetDefaultSelected");
			}
		};
	}

	private Optional<ExperimentController> getExperimentController() {
		return SpringApplicationContextProxy.getOptionalBean(ExperimentController.class);
	}
}
