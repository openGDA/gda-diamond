/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.arpes.ui.views;

import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.wb.swt.ResourceManager;

public class CryoView extends ViewPart {

	public static final String ID = "uk.ac.gda.arpes.ui.views.CryoView"; //$NON-NLS-1$

	public CryoView() {
	}

	/**
	 * Create contents of the view part.
	 * @param parent
	 */
	@Override
	public void createPartControl(Composite parent) {
		Composite container = new Composite(parent, SWT.NONE);
		container.setLayout(null);
		container.setBounds(0, 0, 720, 750);
		{
			Label lblSay = new Label(container, SWT.NONE);
			lblSay.setBounds(350, 166, 66, 18);
			lblSay.setText("say");
		}
		{
			Label lblSaz = new Label(container, SWT.NONE);
			lblSaz.setBounds(242, 61, 66, 18);
			lblSaz.setText("saz");
		}
		{
			Label lblSax = new Label(container, SWT.NONE);
			lblSax.setBounds(120, 166, 66, 18);
			lblSax.setText("sax");
		}
		{
			Label lblSatilt = new Label(container, SWT.NONE);
			lblSatilt.setBounds(38, 487, 66, 18);
			lblSatilt.setText("satilt");
		}
		{
			Label lblSaploar = new Label(container, SWT.NONE);
			lblSaploar.setBounds(232, 596, 66, 18);
			lblSaploar.setText("saploar");
		}
		{
			Label lblSaazimuth = new Label(container, SWT.NONE);
			lblSaazimuth.setBounds(355, 596, 66, 18);
			lblSaazimuth.setText("saazimuth");
		}
		{
			Label lblEnergy = new Label(container, SWT.NONE);
			lblEnergy.setBounds(613, 424, 66, 18);
			lblEnergy.setText("energy");
		}
		{
			Label lblPolarisation = new Label(container, SWT.NONE);
			lblPolarisation.setBounds(613, 393, 66, 18);
			lblPolarisation.setText("polarisation");
		}
		{
			Label lblEntranceslit = new Label(container, SWT.NONE);
			lblEntranceslit.setBounds(565, 498, 66, 18);
			lblEntranceslit.setText("entranceslit");
		}
		{
			Label lblSampletemp = new Label(container, SWT.NONE);
			lblSampletemp.setBounds(613, 61, 66, 18);
			lblSampletemp.setText("sampletemp");
		}
		
		Label lblNewLabel = new Label(container, SWT.BACKGROUND);
		lblNewLabel.setImage(ResourceManager.getPluginImage("uk.ac.gda.beamline.i05", "icons/cryo.png"));
		lblNewLabel.setBounds(0, 0, 720, 750);
		

		createActions();
		initializeToolBar();
		initializeMenu();
	}

	/**
	 * Create the actions.
	 */
	private void createActions() {
		// Create the actions
	}

	/**
	 * Initialize the toolbar.
	 */
	private void initializeToolBar() {
		IToolBarManager toolbarManager = getViewSite().getActionBars().getToolBarManager();
	}

	/**
	 * Initialize the menu.
	 */
	private void initializeMenu() {
		IMenuManager menuManager = getViewSite().getActionBars().getMenuManager();
	}

	@Override
	public void setFocus() {
		// Set the focus
	}
}