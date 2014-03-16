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

import gda.device.Scannable;
import gda.factory.Finder;
import gda.rcp.views.MotorPositionViewerComposite;
import gda.rcp.views.NudgePositionerComposite;

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
		Composite comp = new Composite(parent, SWT.NONE);
		comp.setLayout(null);
		comp.setBounds(0, 0, 720, 750);
		
		NudgePositionerComposite saxBox = new NudgePositionerComposite(comp, SWT.RIGHT, (Scannable)(Finder.getInstance().find("sax")), false);
		saxBox.setBounds(72, 166, 97, 85);
		
		NudgePositionerComposite sayBox = new NudgePositionerComposite(comp, SWT.RIGHT, (Scannable)(Finder.getInstance().find("say")), false);
		sayBox.setBounds(350, 166, 97, 85);
		
		NudgePositionerComposite sazBox = new NudgePositionerComposite(comp, SWT.RIGHT, (Scannable)(Finder.getInstance().find("saz")), false);
		sazBox.setBounds(150, 21, 97, 85);
		
		NudgePositionerComposite tiltBox = new NudgePositionerComposite(comp, SWT.RIGHT, (Scannable)(Finder.getInstance().find("satilt")), false);
		tiltBox.setBounds(8, 497, 97, 85);
		
		NudgePositionerComposite ploarBox = new NudgePositionerComposite(comp, SWT.RIGHT, (Scannable)(Finder.getInstance().find("sapolar")), false);
		ploarBox.setBounds(212, 596, 97, 85);
		
		NudgePositionerComposite azimuthBox = new NudgePositionerComposite(comp, SWT.RIGHT, (Scannable)(Finder.getInstance().find("saazimuth")), false);
		azimuthBox.setBounds(333, 584, 97, 85);
		
		NudgePositionerComposite energyBox = new NudgePositionerComposite(comp, SWT.RIGHT, (Scannable)(Finder.getInstance().find("pgm_energy")), false);
		energyBox.setBounds(590, 380, 97, 85);
		
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