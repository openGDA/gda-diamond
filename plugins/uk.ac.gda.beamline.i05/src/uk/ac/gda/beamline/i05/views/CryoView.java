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

package uk.ac.gda.beamline.i05.views;

import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.wb.swt.ResourceManager;

import gda.device.Scannable;
import gda.factory.Finder;
import gda.rcp.views.MotorPositionViewerComposite;

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
		Composite comp = new Composite(parent, SWT.NONE);
		comp.setLayout(null);
		comp.setBounds(0, 0, 720, 750);
		{
			MotorPositionViewerComposite lblSay = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("say")), true, "photonEnergy", 4, null, true, true);
			lblSay.setBounds(350, 166, 120, 24);
		}
		{
			MotorPositionViewerComposite lblSaz = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("saz")), true, "photonEnergy", 4, null, true, true);
			lblSaz.setBounds(212, 61, 120, 24);
		}
		{
			MotorPositionViewerComposite lblSax = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("sax")), true, "photonEnergy", 4, null, true, true);
			lblSax.setBounds(72, 166, 120, 24);
		}
		{
			MotorPositionViewerComposite lblSatilt = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("satilt")), true, "photonEnergy", 4, null, true, true);
			lblSatilt.setBounds(8, 497, 120, 24);
		}
		{
			MotorPositionViewerComposite lblSaploar = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("sapolar")), true, "photonEnergy", 4, null, true, true);
			lblSaploar.setBounds(212, 596, 120, 24);
		}
		{
			MotorPositionViewerComposite lblSaazimuth = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("saazimuth")), true, "photonEnergy", 4, null, true, true);
			lblSaazimuth.setBounds(333, 584, 120, 24);
		}
		{
			MotorPositionViewerComposite lblEnergy = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("pgm_energy")), true, "photonEnergy", 4, null, true, true);
			lblEnergy.setBounds(590, 418, 120, 24);
		}
//		{
//			MotorPositionViewerComposite lblPolarisation = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("energy")), true, "photonEnergy", 4, null, true, true);
//			lblPolarisation.setBounds(590, 393, 120, 24);
//		}
//		{
//			MotorPositionViewerComposite lblEntranceslit = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("analyser_slit")), true, "photonEnergy", 4, null, true, true);
//			lblEntranceslit.setBounds(565, 498, 120, 24);
//		}
//		{
//			MotorPositionViewerComposite lblSampletemp = new MotorPositionViewerComposite(comp, SWT.RIGHT, (Scannable) (Finder.getInstance().find("sample_temp")), true, "photonEnergy", 4, null, true, true);
//			lblSampletemp.setBounds(590, 61, 120, 24);
//		}

		Label lblNewLabel = new Label(comp, SWT.BACKGROUND);
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