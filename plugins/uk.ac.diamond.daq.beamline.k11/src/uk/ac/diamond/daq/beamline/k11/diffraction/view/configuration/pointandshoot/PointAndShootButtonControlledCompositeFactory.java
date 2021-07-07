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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.pointandshoot;

import static org.eclipse.swt.events.SelectionListener.widgetSelectedAdapter;
import static uk.ac.gda.ui.tool.ClientMessages.CANNOT_START_POINT_AND_SHOOT_SESSION;
import static uk.ac.gda.ui.tool.ClientMessagesUtility.getMessage;

import java.util.Optional;
import java.util.function.Supplier;

import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.DiffractionConfigurationLayoutFactory;
import uk.ac.diamond.daq.beamline.k11.pointandshoot.PointAndShootController;
import uk.ac.diamond.daq.mapping.api.IMappingExperimentBean;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.gda.api.acquisition.AcquisitionController;
import uk.ac.gda.api.acquisition.AcquisitionControllerException;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.composites.ButtonGroupFactoryBuilder;
import uk.ac.gda.client.exception.GDAClientRestException;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.WidgetUtilities;
import uk.ac.gda.ui.tool.images.ClientImages;
import uk.ac.gda.ui.tool.selectable.ButtonControlledCompositeTemplate;
import uk.ac.gda.ui.tool.selectable.Lockable;
import uk.ac.gda.ui.tool.selectable.NamedCompositeFactory;

/**
 * This Composite allows to edit a {@link ScanningParameters} object.
 *
 * @author Maurizio Nagni
 */
public class PointAndShootButtonControlledCompositeFactory
		implements NamedCompositeFactory, ButtonControlledCompositeTemplate {

	private static final Logger logger = LoggerFactory.getLogger(PointAndShootButtonControlledCompositeFactory.class);

	private static final String RUN_STATE = "runState";
	private enum RUN_BUTTON_STATE {
		READY, RUNNING
	}

	private final AcquisitionController<ScanningAcquisition> acquisitionController;
	private final Supplier<Composite> controlButtonsContainerSupplier;
	private Composite parent;

	private DiffractionConfigurationLayoutFactory acquistionConfigurationFactory;

	private PointAndShootController pointAndShootController;

	public PointAndShootButtonControlledCompositeFactory(AcquisitionController<ScanningAcquisition> acquisitionController,
			Supplier<Composite> controlButtonsContainerSupplier) {
		this.acquisitionController = acquisitionController;
		this.controlButtonsContainerSupplier = controlButtonsContainerSupplier;
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		this.parent = parent;
		return createButtonControlledComposite(parent, style);
	}

	@Override
	public ClientMessages getName() {
		return ClientMessages.POINT_AND_SHOOT;
	}

	@Override
	public ClientMessages getTooltip() {
		return ClientMessages.POINT_AND_SHOOT_TP;
	}

	@Override
	public DiffractionConfigurationLayoutFactory getControlledCompositeFactory() {
		if (acquistionConfigurationFactory == null) {
			this.acquistionConfigurationFactory = new DiffractionConfigurationLayoutFactory(
					getAcquisitionController());
		}
		return acquistionConfigurationFactory;
	}

	@Override
	public CompositeFactory getButtonControlsFactory() {
		return getAcquistionButtonGroupFacoryBuilder().build();
	}

	@Override
	public Supplier<Composite> getButtonControlsContainerSupplier() {
		return controlButtonsContainerSupplier;
	}

	private AcquisitionController<ScanningAcquisition> getAcquisitionController() {
		return acquisitionController;
	}

	/**
	 * Loads the content of the file identified by the fully qualified filename parameter into the mapping bean and
	 * refreshes the UI to dispay the changes. An update of any linked UIs will also be triggered by the controllers
	 *
	 */
	public void load(Optional<IMappingExperimentBean> bean) {
		getControlledCompositeFactory().load(bean);
	}

	private ButtonGroupFactoryBuilder getAcquistionButtonGroupFacoryBuilder() {
		var builder = new ButtonGroupFactoryBuilder();
		builder.addButton(ClientMessages.NEW, ClientMessages.NEW_CONFIGURATION_TP,
				widgetSelectedAdapter(this::newAcquisition),
				ClientImages.ADD);
		builder.addButton(ClientMessages.SAVE, ClientMessages.SAVE_CONFIGURATION_TP,
				widgetSelectedAdapter(this::saveAcquisition),
				ClientImages.SAVE);
		builder.addButton(ClientMessages.START, ClientMessages.START_POINT_AND_SHOOT_TP,
				widgetSelectedAdapter(this::manageSession),
				ClientImages.RUN);
		return builder;
	}

	private void newAcquisition(SelectionEvent event) {
		boolean confirmed = UIHelper.showConfirm("Create new configuration? The existing one will be discarded");
		if (confirmed) {
			getAcquisitionController().createNewAcquisition();
		}
	}

	private void saveAcquisition(SelectionEvent event) {
		if (getAcquisitionController().getAcquisition().getUuid() != null && !UIHelper.showConfirm("Override the existing configuration?")) {
			return;
		}
		try {
			getAcquisitionController().saveAcquisitionConfiguration();
		} catch (AcquisitionControllerException e) {
			UIHelper.showError("Cannot save acquisition", e, logger);
		}
	}

	private void manageSession(SelectionEvent event) {
		RUN_BUTTON_STATE runButtonState = WidgetUtilities.getDataObject(event.widget, RUN_BUTTON_STATE.class, RUN_STATE);
		var startStopButton = (Button)event.widget;
		var lockableClass = WidgetUtilities.getDataObject(this.parent, Lockable.class, Lockable.LOCKABLE_SELECTABLE);

		if ((runButtonState == null || RUN_BUTTON_STATE.READY.equals(runButtonState)) && startPointAndShootSession()) {
			ClientSWTElements.updateButton((Button)event.widget, ClientMessages.STOP, ClientMessages.STOP_POINT_AND_SHOOT_TP,
					ClientImages.STOP);
			startStopButton.setData(RUN_STATE, RUN_BUTTON_STATE.RUNNING);
			// Eventually, locks the selectable container parent of this composite
			Optional.of(lockableClass).ifPresent(l -> l.lock(true));
		} else if (RUN_BUTTON_STATE.RUNNING.equals(runButtonState) && endPointAndShootSession()) {
			ClientSWTElements.updateButton((Button)event.widget, ClientMessages.START, ClientMessages.START_POINT_AND_SHOOT_TP,
					ClientImages.START);
			startStopButton.setData(RUN_STATE, RUN_BUTTON_STATE.READY);
			// Eventually, unlocks the selectable container parent of this composite
			Optional.of(lockableClass).ifPresent(l -> l.lock(false));
		}
	}

	private boolean endPointAndShootSession() {
		try {
			pointAndShootController.endSession();
			return true;
		} catch (GDAClientRestException e) {
			UIHelper.showError("Cannot stop Point and Shoot session", e);
		}
		return false;
	}

	private boolean startPointAndShootSession() {
		try {
			pointAndShootController = new PointAndShootController(getAcquisitionName(), getAcquisitionController());
			pointAndShootController.startSession();
			return true;
		} catch (GDAClientRestException e) {
			UIHelper.showError(getMessage(CANNOT_START_POINT_AND_SHOOT_SESSION), e);
		}
		return false;
	}

	private String getAcquisitionName() {
		return getAcquisition().getName();
	}

	private ScanningAcquisition getAcquisition() {
		return getAcquisitionController().getAcquisition();
	}
}
