/*-
 * Copyright © 2022 Diamond Light Source Ltd.
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
import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.DiffractionComposite;
import uk.ac.diamond.daq.beamline.k11.pointandshoot.PointAndShootController;
import uk.ac.gda.api.acquisition.AcquisitionKeys;
import uk.ac.gda.api.acquisition.AcquisitionPropertyType;
import uk.ac.gda.api.acquisition.AcquisitionSubType;
import uk.ac.gda.api.acquisition.AcquisitionTemplateType;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.composites.ButtonGroupFactoryBuilder;
import uk.ac.gda.client.exception.GDAClientRestException;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.WidgetUtilities;
import uk.ac.gda.ui.tool.images.ClientImages;
import uk.ac.gda.ui.tool.selectable.Lockable;

public class PointAndShootComposite extends DiffractionComposite {

	private static final AcquisitionKeys key = new AcquisitionKeys(AcquisitionPropertyType.DIFFRACTION, AcquisitionSubType.STANDARD, AcquisitionTemplateType.TWO_DIMENSION_POINT);

	private Composite parent;
	private PointAndShootController pointAndShootController;

	public PointAndShootComposite(Supplier<Composite> controlButtonsContainerSupplier) {
		super(controlButtonsContainerSupplier);
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		this.parent = parent;
		return super.createComposite(parent, style);
	}

	@Override
	protected AcquisitionKeys getAcquisitionKey() {
		return key;
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
	protected CompositeFactory getButtonControlsFactory() {
		var buttons = new ButtonGroupFactoryBuilder();
		buttons.addButton(ClientMessages.NEW, ClientMessages.NEW_CONFIGURATION_TP,
				widgetSelectedAdapter(event -> {
					createNewAcquisition();
					getScanControls().reload();
				}),
				ClientImages.ADD);
		buttons.addButton(ClientMessages.SAVE, ClientMessages.SAVE_CONFIGURATION_TP,
				widgetSelectedAdapter(event -> saveAcquisition()),
				ClientImages.SAVE);
		buttons.addButton(ClientMessages.START, ClientMessages.START_POINT_AND_SHOOT_TP,
				widgetSelectedAdapter(this::manageSession),
				ClientImages.RUN);
		return buttons.build();
	}

	private static final String RUN_STATE = "runState";

	private enum RunButtonState {
		READY, RUNNING
	}

	private void manageSession(SelectionEvent event) {
		RunButtonState runButtonState = WidgetUtilities.getDataObject(event.widget, RunButtonState.class, RUN_STATE);
		var startStopButton = (Button)event.widget;
		var lockableClass = WidgetUtilities.getDataObject(this.parent, Lockable.class, Lockable.LOCKABLE_SELECTABLE);

		if ((runButtonState == null || RunButtonState.READY.equals(runButtonState)) && startPointAndShootSession()) {
			ClientSWTElements.updateButton((Button)event.widget, ClientMessages.STOP, ClientMessages.STOP_POINT_AND_SHOOT_TP,
					ClientImages.STOP);
			startStopButton.setData(RUN_STATE, RunButtonState.RUNNING);
			// Eventually, locks the selectable container parent of this composite
			Optional.of(lockableClass).ifPresent(l -> l.lock(true));
		} else if (RunButtonState.RUNNING.equals(runButtonState) && endPointAndShootSession()) {
			ClientSWTElements.updateButton((Button)event.widget, ClientMessages.START, ClientMessages.START_POINT_AND_SHOOT_TP,
					ClientImages.START);
			startStopButton.setData(RUN_STATE, RunButtonState.READY);
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

}
