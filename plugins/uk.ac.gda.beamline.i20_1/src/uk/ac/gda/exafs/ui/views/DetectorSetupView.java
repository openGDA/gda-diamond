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

import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IViewReference;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;

import uk.ac.gda.exafs.ui.composites.XHControlComposite;

public class DetectorSetupView extends ViewPart {

	public static String ID = "uk.ac.gda.exafs.ui.views.detectorsetupview";

	public static IViewReference findMe() {
		IWorkbenchPage page = PlatformUI.getWorkbench().getWorkbenchWindows()[0].getActivePage();
		final IViewReference viewReference = page.findViewReference(ID);
		return viewReference;
	}

	private XHControlComposite xhComposite;

	@Override
	public void createPartControl(Composite parent) {
		xhComposite = new XHControlComposite(parent, this);
		xhComposite.setLayoutData(new GridData(GridData.FILL_BOTH));
		parent.setBackground(Display.getCurrent().getSystemColor(SWT.COLOR_BLUE));
	}

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
