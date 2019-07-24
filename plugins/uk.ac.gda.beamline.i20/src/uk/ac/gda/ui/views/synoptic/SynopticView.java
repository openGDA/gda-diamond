/*-
 * Copyright © 2016 Diamond Light Source Ltd.
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

package uk.ac.gda.ui.views.synoptic;

import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SynopticView extends ViewPart {
	public static final String Id = "uk.ac.gda.ui.views.synoptic.SynopticView";
	private static final Logger logger = LoggerFactory.getLogger(SynopticView.class);

	private String className = ""; //Full name of class with composite to be opened

	private HardwareDisplayComposite viewComposite;

	public SynopticView() {
		super();
	}

	private Class<?extends HardwareDisplayComposite> getClassMatchingName(String classIdToFind) throws ClassNotFoundException {
		Class<?> clazz = Class.forName(classIdToFind);
		if (clazz != null && HardwareDisplayComposite.class.isAssignableFrom(clazz)) {
			return (Class<? extends HardwareDisplayComposite>) clazz;
		}
		return null;
	}

	@Override
	public void createPartControl(Composite parent) {
		String fullClassName = getViewSite().getSecondaryId();
		if (!className.isEmpty()) {
			fullClassName = className;
		}
		// If no class name specified, use 'beamline overview' view.
		if (fullClassName == null) {
			fullClassName = OverviewButtonsView.class.getCanonicalName();
		}
		try {
			Class<? extends HardwareDisplayComposite> classFromName = getClassMatchingName(fullClassName);
			if (classFromName == null) {
				throw new Exception("Could not create class with name " + fullClassName);
			}
			// Constructor parameter types : parent composite, swt options :
			Class<? extends HardwareDisplayComposite>[] constructorParamTypes = new Class[] { Composite.class, int.class };
			// Create new instance of class, passing the constructor params :
			Object obj = classFromName.getDeclaredConstructor(constructorParamTypes).newInstance(parent, SWT.NONE);
			viewComposite = (HardwareDisplayComposite) obj;
		} catch (Exception e) {
			logger.error("Problem occured when tring to create view for id {}", fullClassName, e);
			MessageDialog.openWarning(parent.getShell(), "Problem opening syntopic view", "Problem occured when tring to create view for "+fullClassName);

		}

		// Set label used in tab for view
		if (viewComposite != null) {
			setPartName(viewComposite.getViewName());
		}
	}

	@Override
	public void setFocus() {
		if (viewComposite != null) {
			viewComposite.setFocus();
		}
	}

	/**
	 * Utility function to open the named 'Synoptic view', catching any PartInitException thrown.
	 * @param className fully qualified name of class of view to open
	 */
	public static void openView(String className) {
		try {
			PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(SynopticView.Id, className, IWorkbenchPage.VIEW_ACTIVATE);
		} catch (PartInitException e1) {
			logger.error("Problem opening Synoptic view with name {}", className, e1);
		}
	}

	public String getClassName() {
		return className;
	}

	public void setClassName(String classId) {
		this.className = classId;
	}
}