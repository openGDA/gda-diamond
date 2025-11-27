/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package uk.ac.gda.dls.client.views;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;

import gda.rcp.views.CompositeFactory;
import uk.ac.gda.dls.client.Activator;

public class OpenViewCompositeFactory implements CompositeFactory, InitializingBean{

	private String tooltipText;
	private String viewID;
	private String buttonText;
	private String buttonImagePath;

	public void setTooltipText(String tooltipText) {
		this.tooltipText = tooltipText;
	}

	public void setViewID(String viewID) {
		this.viewID = viewID;
	}
	public void setButtonText(String buttonText) {
		this.buttonText = buttonText;
	}

	public void setButtonImagePath(String buttonImagePath) {
		this.buttonImagePath = buttonImagePath;
	}

	@Override
	public void afterPropertiesSet() throws Exception {
		if( tooltipText == null)
			throw new IllegalArgumentException("tooltipText is null");
		if( viewID == null)
			throw new IllegalArgumentException("viewID is null");
		if( buttonText == null)
			throw new IllegalArgumentException("buttonText is null");

	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		Image buttonImage = buttonImagePath != null ? Activator.getImageDescriptor(buttonImagePath).createImage() : null;
		return new OpenViewComposite(parent, style, buttonText, tooltipText, buttonImage, viewID);
	}

}
/**
 * Displays a button with title - when pressed opens the view ID
 */
class OpenViewComposite extends Composite{
	private static final Logger logger = LoggerFactory.getLogger(OpenViewComposite.class);
	public OpenViewComposite(Composite parent, int style, String buttonText, String tooltipText, Image buttonImage, final String viewID) {
		super(parent, style);
		setLayout(new GridLayout(1, false));
		Button button = new Button(this, SWT.PUSH);
		button.setText(buttonText);
		button.setToolTipText(tooltipText);
		button.setImage(buttonImage);
		button.addSelectionListener(new SelectionAdapter() {

			@Override
			public void widgetSelected(SelectionEvent arg0) {
				try {
					PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(viewID);
				} catch (PartInitException e) {
					logger.error("Error opening  view " + viewID, e);
				}
			}
		});
		GridDataFactory.fillDefaults().grab(true, false).applyTo(button);
	}
}
