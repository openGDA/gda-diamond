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

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.DiffractionConfigurationLayoutFactory;
import uk.ac.diamond.daq.beamline.k11.pointandshoot.PointAndShootController;
import uk.ac.diamond.daq.mapping.api.IMappingExperimentBean;
import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.composites.ButtonGroupFactoryBuilder;
import uk.ac.gda.client.exception.AcquisitionControllerException;
import uk.ac.gda.client.exception.GDAClientRestException;
import uk.ac.gda.client.properties.acquisition.AcquisitionKeys;
import uk.ac.gda.client.properties.acquisition.AcquisitionPropertyType;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.WidgetUtilities;
import uk.ac.gda.ui.tool.document.ScanningAcquisitionTemporaryHelper;
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

	private static final String RUN_STATE = "runState";
	private enum RUN_BUTTON_STATE {
		READY, RUNNING
	}

	private final Supplier<Composite> controlButtonsContainerSupplier;
	private Composite parent;

	private DiffractionConfigurationLayoutFactory acquistionConfigurationFactory;

	private PointAndShootController pointAndShootController;

	public PointAndShootButtonControlledCompositeFactory(Supplier<Composite> controlButtonsContainerSupplier) {
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
			this.acquistionConfigurationFactory = new DiffractionConfigurationLayoutFactory();
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

	@Override
	public AcquisitionKeys getAcquisitionKeys() {
		return new AcquisitionKeys(AcquisitionPropertyType.DIFFRACTION, AcquisitionTemplateType.TWO_DIMENSION_POINT);
	}

	@Override
	public void createNewAcquisitionInController() throws AcquisitionControllerException {
		getScanningAcquisitionTemporaryHelper()
			.setNewScanningAcquisition(getAcquisitionKeys());
	}

	/**
	 * Loads the content of the file identified by the fully qualified filename parameter into the mapping bean and
	 * refreshes the UI to display the changes. An update of any linked UIs will also be triggered by the controllers
	 *
	 */
	public void load(Optional<IMappingExperimentBean> bean) {
		getControlledCompositeFactory().load(bean);
	}

	private ButtonGroupFactoryBuilder getAcquistionButtonGroupFacoryBuilder() {
		var builder = new ButtonGroupFactoryBuilder();
		builder.addButton(ClientMessages.NEW, ClientMessages.NEW_CONFIGURATION_TP,
				widgetSelectedAdapter(event -> newAcquisitionButtonAction()),
				ClientImages.ADD);
		builder.addButton(ClientMessages.SAVE, ClientMessages.SAVE_CONFIGURATION_TP,
				widgetSelectedAdapter(event -> getScanningAcquisitionTemporaryHelper().saveAcquisition()),
				ClientImages.SAVE);
		builder.addButton(ClientMessages.START, ClientMessages.START_POINT_AND_SHOOT_TP,
				widgetSelectedAdapter(this::manageSession),
				ClientImages.RUN);
		return builder;
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
			pointAndShootController = new PointAndShootController();
			pointAndShootController.startSession();
			return true;
		} catch (GDAClientRestException e) {
			UIHelper.showError(getMessage(CANNOT_START_POINT_AND_SHOOT_SESSION), e);
		}
		return false;
	}

	// ------------ UTILS ----
	private ScanningAcquisitionTemporaryHelper getScanningAcquisitionTemporaryHelper() {
		return SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class);
	}
}