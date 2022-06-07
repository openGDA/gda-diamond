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

import org.apache.commons.lang.StringUtils;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.factory.Finder;
import uk.ac.gda.client.livecontrol.LiveControl;

public class SynopticView extends ViewPart {
	public static final String ID = "uk.ac.gda.ui.views.synoptic.SynopticView";
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

		var viewConfig = Finder.findOptionalOfType(fullClassName, SynopticViewConfiguration.class);
		if (viewConfig.isPresent()) {
			logger.info("Creating synoptic view from client configuration {}", viewConfig.get().getName());
			createPartControl(parent, viewConfig.get());
			return;
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
			logger.error("Problem occured when trying to create view for id {}", fullClassName, e);
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
			PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(SynopticView.ID, className, IWorkbenchPage.VIEW_ACTIVATE);
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


	public void createPartControl(Composite parent, SynopticViewConfiguration viewConfig) {
		setPartName(viewConfig.getViewName());
		SynopticGuiComposite composite = new SynopticGuiComposite();
		composite.setViewConfig(viewConfig);
		composite.createControls(parent, null);
	}

	private class SynopticGuiComposite extends HardwareDisplayComposite {
		private SynopticViewConfiguration viewConfig;

		public void setViewConfig(SynopticViewConfiguration viewConfig) {
			this.viewConfig = viewConfig;
		}

		@Override
		protected void createControls(Composite parent) throws Exception {
			this.parent = parent;
			super.setViewName(viewConfig.getViewName());
			if (!StringUtils.isEmpty(viewConfig.getBackgroundImage())) {
				super.setBackgroundImage(getImageFromPlugin(viewConfig.getBackgroundImage()), viewConfig.getImageStart());
			}
			parent.setBackgroundMode(SWT.INHERIT_FORCE);

			for(var liveControl : viewConfig.getControls().entrySet()) {
				LiveControl cont = liveControl.getKey();

				Composite group;
				if (StringUtils.isNotEmpty(cont.getGroup())) {
					group = new Group(parent, SWT.NONE);
					((Group)group).setText(cont.getGroup());
				} else {
					group = new Composite(parent, SWT.NONE);
				}

				group.setLayout(new GridLayout());

				cont.createControl(group);

				Point position = liveControl.getValue();
				setAbsoluteWidgetPosition(group, position.x, position.y);
			}

			addResizeListener(parent);

			if (viewConfig.isShowCoordinates()) {
				addMousePositionOutput(parent);
			}
		}
	}


}