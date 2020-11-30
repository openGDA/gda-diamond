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

package uk.ac.diamond.daq.beamline.k11.diffraction.view;

import static uk.ac.gda.ui.tool.ClientMessages.CANNOT_START_POINT_AND_SHOOT_SESSION;
import static uk.ac.gda.ui.tool.ClientMessagesUtility.getMessage;
import static uk.ac.gda.ui.tool.rest.ClientRestServices.getExperimentController;

import java.util.Optional;

import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.swt.widgets.Composite;

import uk.ac.diamond.daq.beamline.k11.pointandshoot.PointAndShootController;
import uk.ac.diamond.daq.experiment.api.structure.ExperimentControllerException;
import uk.ac.diamond.daq.mapping.api.IMappingExperimentBean;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.ui.services.MappingServices;
import uk.ac.gda.api.acquisition.AcquisitionController;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.selectable.NamedComposite;

/**
 * This Composite allows to edit a {@link ScanningParameters} object.
 *
 * @author Maurizio Nagni
 */
public class PointAndShootConfigurationCompositeFactory implements NamedComposite {

	private PointAndShootController pointAndShootController;
	private final AcquisitionController<ScanningAcquisition> controller;

	private final DiffractionConfigurationCompositeBaseFactory diffractionBase;
	public PointAndShootConfigurationCompositeFactory(AcquisitionController<ScanningAcquisition> controller) {
		this.controller = controller;
		diffractionBase = new DiffractionConfigurationCompositeBaseFactory(controller);
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		Composite composite = diffractionBase.createComposite(parent, style);
//		startPointAndShootSession();
//		composite.addDisposeListener(disposedEvent -> {
//			if (Objects.equals(disposedEvent.getSource(), composite)) {
//				endPointAndShootSession();
//			}
//		});
		return composite;
	}

	/**
	 * Loads the content of the file identified by the fully qualified filename parameter into the mapping bean and
	 * refreshes the UI to dispay the changes. An update of any linked UIs will also be triggered by the controllers
	 *
	 */
	public void load(Optional<IMappingExperimentBean> bean) {
		diffractionBase.load(bean);
	}

	private void endPointAndShootSession() {
		if (pointAndShootController == null)
			return;
		try {
			pointAndShootController.endSession();
			pointAndShootController = null;
			//updateButton(pointAndShoot, START, START_POINT_AND_SHOOT_TP, ClientImages.RUN);
			getMapPlottingSystem().setTitle(" ");
		} catch (ExperimentControllerException e) {
			UIHelper.showError("Cannot stop Point and Shoot session", e);
		}
	}

//	private boolean isPointAndShootActive() {
//		return pointAndShootController != null;
//	}

//	private void togglePointAndShoot() {
//		if (isPointAndShootActive()) {
//			// end current session
//			endPointAndShootSession();
//		} else {
//			// start new session
//			startPointAndShootSession();
//		}
//	}

	private void startPointAndShootSession() {
		if (getExperimentController().isExperimentInProgress()) {
			try {
				pointAndShootController = new PointAndShootController(getAcquisitionName());
				getMapPlottingSystem().setTitle("Point and Shoot: Ctrl+Click to scan");
			} catch (ExperimentControllerException e) {
				UIHelper.showError(getMessage(CANNOT_START_POINT_AND_SHOOT_SESSION), e);
			}
		} else {
			UIHelper.showError("Cannot start Point and Shoot session", "An experiment must be started first");
		}
	}

	private String getAcquisitionName() {
		return getAcquisition().getName();
	}

	private ScanningAcquisition getAcquisition() {
		return getController().getAcquisition();
	}

	private AcquisitionController<ScanningAcquisition> getController() {
		return controller;
	}

	private IPlottingSystem<Object> getMapPlottingSystem() {
		return MappingServices.getPlottingService().getPlottingSystem("Map");
	}

	@Override
	public ClientMessages getName() {
		return ClientMessages.POINT_AND_SHOOT;
	}

	@Override
	public ClientMessages getTooltip() {
		return ClientMessages.POINT_AND_SHOOT_TP;
	}
}
