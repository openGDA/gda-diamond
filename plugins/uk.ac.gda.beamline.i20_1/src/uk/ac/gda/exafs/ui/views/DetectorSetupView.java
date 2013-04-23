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

package uk.ac.gda.exafs.ui.views;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.IViewReference;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;

import uk.ac.gda.exafs.ui.composites.XHControlComposite;

/**
 * Shows detector controls for use when aligning the beamline.
 * <p>
 * Combobox to choose the detector type to show detector-specific composites.
 */
public class DetectorSetupView extends ViewPart {

	public static String ID = "uk.ac.gda.exafs.ui.views.detectorsetupview";
	
	public static IViewReference findMe() {
		IWorkbenchPage page = PlatformUI.getWorkbench().getWorkbenchWindows()[0].getActivePage();
		final IViewReference viewReference = page.findViewReference(ID);
		return viewReference;
	}

	
	
//	private StackLayout stackLayout;
//	private XHControlComposite xhComposite;
	private Composite detectorControls;
private XHControlComposite xhComposite;

	@Override
	public void createPartControl(Composite parent) {
		parent.setLayout(new GridLayout(1, false));
//		parent.setBackground(PlatformUI.getWorkbench().getDisplay().getSystemColor(SWT.COLOR_MAGENTA));
//		Composite contents = new Composite(parent, SWT.NONE);
//		GridDataFactory.swtDefaults().applyTo(contents);
//		GridLayoutFactory.swtDefaults().applyTo(contents);

		Composite comboCompo = new Composite(parent, SWT.NONE);
		GridDataFactory.swtDefaults().applyTo(comboCompo);
		GridLayoutFactory.swtDefaults().numColumns(2).applyTo(comboCompo);
		Label lbl = new Label(comboCompo, SWT.NONE);
		lbl.setText("Detector");
		GridDataFactory.swtDefaults().applyTo(lbl);

		final Combo cmbDetectorChoice = new Combo(comboCompo, SWT.NONE);
		cmbDetectorChoice.setItems(new String[] { "XH / XStrip", "CCD" });
//		cmbDetectorChoice.addSelectionListener(new SelectionListener() {
//
//			@Override
//			public void widgetSelected(SelectionEvent e) {
//				changeDetectorType(cmbDetectorChoice.getSelectionIndex());
//
//			}
//
//			@Override
//			public void widgetDefaultSelected(SelectionEvent e) {
//				changeDetectorType(0);
//
//			}
//		});

		detectorControls = new Composite(parent, SWT.BORDER);
//		detectorControls.setBackground(PlatformUI.getWorkbench().getDisplay().getSystemColor(SWT.COLOR_DARK_YELLOW));
		GridDataFactory.swtDefaults().applyTo(detectorControls);
		GridLayoutFactory.swtDefaults().numColumns(1).applyTo(detectorControls);
//		GridDataFactory.swtDefaults().grab(true, true).applyTo(detectorControls);
//		GridLayoutFactory.swtDefaults().applyTo(detectorControls);
//		this.stackLayout = new StackLayout();
//		detectorControls.setLayout(stackLayout);

		xhComposite = new XHControlComposite(detectorControls, this);
		// ccdComposite = new CompoisteToWrite(detectorControls, SWT.NONE);
		
		cmbDetectorChoice.select(0);
//		stackLayout.topControl = xhComposite;
//		detectorControls.layout();

	}

//	private void changeDetectorType(int selectionIndex) {
//		switch (selectionIndex) {
//		// case 1:
//		// stackLayout.topControl = ccdComposite;
//		// break;
//		default:
//		case 0:
//			stackLayout.topControl = xhComposite;
//			break;
//		}
//		detectorControls.layout();
//	}

	@Override
	public void setFocus() {
	}

	public void startCollectingRates() {
		xhComposite.startCollectingRates();		
	}

	public void stopCollectingRates() {
		xhComposite.stopCollectingRates();		
	}

}
