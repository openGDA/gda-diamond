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

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;

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
	private static final Logger logger = LoggerFactory.getLogger(SampleStageView.class);

	private List< Class<?>> idToClassMap = new ArrayList< Class<?>>();

	// Composite classes that can be opened by createPartControl
	private Class<?>[] synopticViews = new Class<?>[]{ OverviewButtonsView.class, SampleStageView.class, XasTableView.class,
		XesCalibrationView.class, XesCrystalAnalysersView.class, XesStageView.class, HutchFilterView.class  };

	private HardwareDisplayComposite viewComposite;

	public SynopticView() {
		super();
	}

	private Class<?> getClassMatchingId(String classIdToFind) throws Exception {
		for (Class clazz : synopticViews) {
			Field fieldForId = clazz.getDeclaredField("ID");
			if (fieldForId != null) {
				String idValueFromClass = (String) fieldForId.get(null);
				if (classIdToFind.equals(idValueFromClass)) {
					return clazz;
				}
			}
		}
		return null;
	}

	@Override
	public void createPartControl(Composite parent) {
		String secondaryId = getViewSite().getSecondaryId();

		try {
			if (secondaryId==null) {
				viewComposite = new OverviewButtonsView(parent, SWT.NONE);
			} else  {
				Class<?> classFromId = getClassMatchingId(secondaryId);
				Class[] constructorParamTypes = new Class[] { Composite.class, int.class };
				Object obj = classFromId.getDeclaredConstructor(constructorParamTypes).newInstance(parent, SWT.NONE);
				viewComposite = (HardwareDisplayComposite) obj;
			}
		} catch (Exception e) {
			logger.error("Problem occured when tring to create view for id {}", secondaryId, e);
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
	 * @param secondaryId ID of view to open (i.e. {@link XesStageView#ID}, {@link SampleStageView#ID} etc.)
	 */
	public static void openView(String secondaryId) {
		try {
			PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(SynopticView.Id, secondaryId, IWorkbenchPage.VIEW_ACTIVATE);
		} catch (PartInitException e1) {
			logger.error("Problem opening Synoptic view with name {}", secondaryId, e1);
		}
	}
}