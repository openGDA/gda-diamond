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

package uk.ac.gda.beamline.b21;

import java.net.URL;

import org.eclipse.core.runtime.FileLocator;
import org.eclipse.swt.SWT;
import org.eclipse.swt.browser.Browser;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.WorkbenchException;
import org.eclipse.ui.part.IntroPart;
import org.osgi.framework.FrameworkUtil;

public class B21Intro extends IntroPart {

	@Override
	public void standbyStateChanged(boolean standby) {
	}

	@Override
	public void createPartControl(Composite parent) {
		for (String id : new String[] {
				"uk.ac.gda.pydev.extension.ui.JythonPerspective",	
				"gda.rcp.ncd.perspectives.WaxsPerspective",
				"gda.rcp.ncd.perspectives.SaxsProcessingPerspective",
				"gda.rcp.ncd.perspectives.SaxsPerspective",
				"gda.rcp.ncd.perspectives.NcdDetectorPerspective",
				"gda.rcp.ncd.perspectives.SetupPerspective"
				}) {
			try {
				PlatformUI.getWorkbench().showPerspective(id, PlatformUI.getWorkbench().getActiveWorkbenchWindow());
			} catch (WorkbenchException e) {
					// we see if that fails and it is not the end of the world
			}
		}
	    try {
	    	Browser browser = new Browser(parent, SWT.NONE);
	    	URL entry = FrameworkUtil.getBundle(this.getClass()).getEntry("/help/root.xhtml");
			URL fileURL = FileLocator.toFileURL(entry);
			browser.setUrl(fileURL.toString());
		} catch (Throwable e) {
			// TODO Auto-generated catch block
		}  
	}

	@Override
	public void setFocus() {
	}
}