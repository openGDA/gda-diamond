/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

import org.eclipse.dawnsci.plotting.api.IPlottingService;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.PlatformUI;

import gda.rcp.views.CompositeFactory;
import gda.rcp.views.ReservableControl;
import gda.rcp.views.TabCompositeFactory;
import gda.rcp.views.TabCompositeFactoryImpl;
import gda.rcp.views.TabFolderBuilder;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController.DiffractionAcquisitionMode;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientMessagesUtility;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.images.ClientImages;

public class DiffractionExecutionControl extends Composite {

	public DiffractionExecutionControl(Composite parent, int style, ScanManagementController controller) {
		super(parent, style);

		CompositeFactory cf = createTabFactory(controller);
		GridLayoutFactory.swtDefaults().applyTo(this);
		cf.createComposite(this, SWT.NONE);
	}

	private CompositeFactory createTabFactory(ScanManagementController controller) {
		TabFolderBuilder builder = new TabFolderBuilder();
		builder.addTab(createSimpleDiffractionControlFactory(controller));
		builder.addTab(createPointAndShootControlFactory(controller));
		return builder.build();
	}

	private final TabCompositeFactory createSimpleDiffractionControlFactory(ScanManagementController controller) {
		TabCompositeFactoryImpl group = new TabCompositeFactoryImpl();
		CompositeFactory cf = new SimpleDiffractionCompositeFactory(controller);
		group.setCompositeFactory(cf);
		group.setLabel(ClientMessagesUtility.getMessage(ClientMessages.DIFFRACTION));
		return group;
	}

	private final TabCompositeFactory createPointAndShootControlFactory(ScanManagementController controller) {
		TabCompositeFactoryImpl group = new TabCompositeFactoryImpl();
		CompositeFactory cf = new PointAndShootcompositeFactory(controller);
		group.setCompositeFactory(cf);
		group.setLabel(ClientMessagesUtility.getMessage(ClientMessages.POINT_AND_SHOOT));
		return group;
	}

	private class SimpleDiffractionCompositeFactory implements CompositeFactory {
		private Button submit;
		private final ScanManagementController controller;

		public SimpleDiffractionCompositeFactory(ScanManagementController controller) {
			super();
			this.controller = controller;
		}

		@Override
		public Composite createComposite(Composite parent, int style) {
			Composite container = ClientSWTElements.createComposite(parent, style);
			submit = ClientSWTElements.createButton(container, style, ClientMessages.RUN,
					ClientMessages.RUN_ACQUISITION_TP, ClientImages.RUN);
			addBindings();
			return container;
		}

		private void addBindings() {
			submit.addListener(SWT.Selection, e -> controller.submitScan());
		}
	}

	private class PointAndShootcompositeFactory implements CompositeFactory {
		private Button startStop;
		private final ScanManagementController controller;

		public PointAndShootcompositeFactory(ScanManagementController controller) {
			super();
			this.controller = controller;
		}

		@Override
		public Composite createComposite(Composite parent, int style) {
			Composite container = ClientSWTElements.createComposite(parent, style, 2);
			startStop = ClientSWTElements.createButton(container, style, ClientMessages.START,
					ClientMessages.START_POINT_AND_SHOOT_TP, ClientImages.RUN);
			addBindings(container);
			return container;
		}

		private void updateStatus(Composite container) {
			ReservableControl lock = (ReservableControl)container.getData(TabFolderBuilder.LOCK_TAB);
			if (lock.isReserved() && !lock.isOwner(container)) {
				return;
			}

			IPlottingService plottingService = PlatformUI.getWorkbench().getService(IPlottingService.class);
			IPlottingSystem<Object> mapPlottingSystem = plottingService.getPlottingSystem("Map");

			if (lock.isReserved()) {
				lock.release(container);
				ClientSWTElements.updateButton(startStop, ClientMessages.START, ClientMessages.START_POINT_AND_SHOOT_TP,
						ClientImages.RUN);
				mapPlottingSystem.setTitle(" ");
				controller.setAcquisitionMode(null);
			} else {
				lock.reserve(container);
				ClientSWTElements.updateButton(startStop, ClientMessages.STOP, ClientMessages.STOP_POINT_AND_SHOOT_TP,
						ClientImages.STOP);
				mapPlottingSystem.setTitle("Point and Shoot: Ctrl+Click to scan");
				controller.setAcquisitionMode(DiffractionAcquisitionMode.POINT_AND_SHOOT);
			}
		}

		private void addBindings(Composite container) {
			startStop.addListener(SWT.Selection, e -> updateStatus(container));
		}
	}
}
