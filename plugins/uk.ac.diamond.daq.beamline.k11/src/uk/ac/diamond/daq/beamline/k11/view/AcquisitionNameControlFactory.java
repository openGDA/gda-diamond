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

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.Activator;
import uk.ac.diamond.daq.mapping.ui.experiment.MetadataController;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientMessagesUtility;
import uk.ac.gda.ui.tool.ClientSWTElements;

public class AcquisitionNameControlFactory implements CompositeFactory {

	private Text acquisitionName;
	private MetadataController controller;

	public AcquisitionNameControlFactory() {
		controller = Activator.getService(MetadataController.class);
		controller.initialise();
		controller.addListener(this::updateName);
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		Composite container = ClientSWTElements.createComposite(parent, style, 2, SWT.FILL, SWT.FILL);
		new Label(container, SWT.NONE).setText(ClientMessagesUtility.getMessage(ClientMessages.ACQUISITION));
		acquisitionName = ClientSWTElements.createText(container, SWT.NONE, null, null,
				ClientMessages.ACQUISITION_NAME_TP, GridDataFactory.fillDefaults().grab(true, false).align(SWT.FILL, SWT.FILL));

		acquisitionName.setText(controller.getAcquisitionName());
		acquisitionName.addListener(SWT.Modify, event -> controller.setAcquisitionName(acquisitionName.getText()));

		return container;
	}

	public void updateName(MetadataController.MetadataUpdateEvent update) {
		if (update.getAcquisitionName().equals(acquisitionName.getText())) {
			return; // no need to update (or cause a stack overflow!)
		}
		acquisitionName.setText(update.getAcquisitionName());
	}
}
