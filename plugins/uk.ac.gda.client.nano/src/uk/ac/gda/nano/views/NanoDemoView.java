/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package uk.ac.gda.nano.views;

import java.util.List;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.factory.Findable;
import gda.factory.Finder;
import gda.rcp.GDAClientActivator;
import gda.rcp.views.CompositeFactory;
import gda.rcp.views.FindableGroupCompositeFactory;

public class NanoDemoView extends ViewPart {

	public static final String ID = "uk.ac.gda.nano.views.SuperConductingMagnetView";
	private static final Logger logger = LoggerFactory.getLogger(NanoDemoView.class);

	private Composite guiBase;

	Combo motor;
	String[] motorNames=new String[]{"test1", "test2"};

	List<CompositeFactory> compositeFactories= null;


	public NanoDemoView() {
		super();
		//To register itself to be updated by the command server
//		InterfaceProvider.getJSFObserver().addIObserver(this);

	}

	@Override
	public void createPartControl(Composite parent) {
		parent.setLayout(new FillLayout());
		ScrolledComposite sbase = new ScrolledComposite(parent, SWT.H_SCROLL | SWT.V_SCROLL);
		sbase.setLayout(new FillLayout());

		guiBase = new Composite(sbase, SWT.NONE);
//		guiBase = new Composite(parent, SWT.SCROLL_LINE);
		sbase.setContent(guiBase);
		sbase.setMinSize(600, 600);
		sbase.setExpandHorizontal(true);
		sbase.setExpandVertical(true);

		this.createMagnetGUI(guiBase);

	}


	@Override
	public void setFocus() {
		guiBase.setFocus();
	}


	public void createMagnetGUI(Composite base) {
		GridLayout baseLayout = new GridLayout();
		baseLayout.numColumns = 3;
		base.setLayout(baseLayout);

		this.createComposite(guiBase, "demoGUI");
		this.createComposite(guiBase, "demoGUI");
		}



	public Composite createComposite(Composite base, String findableGroupCompositeFactoryName) {
		// to setup a CompositeFactories
		Findable findable = Finder.getInstance().find(findableGroupCompositeFactoryName);
		if( findable == null || !(findable instanceof FindableGroupCompositeFactory))
			try {
				throw new CoreException(new Status(IStatus.ERROR, GDAClientActivator.PLUGIN_ID, "Unable to find a FindableExecutableExtension called"));
			} catch (CoreException e) {
				logger.error("Unable to find the composite factory " + findableGroupCompositeFactoryName, e);
			}

		Composite c=((FindableGroupCompositeFactory)(findable)).createComposite(base, SWT.NONE);

		return c;
	}


	public void createMotionGUI(Composite base) {
		Group motionGroup = new Group(base, SWT.NONE);
		motionGroup.setText("Motion");
		GridData gridData = new GridData(GridData.FILL, GridData.CENTER, true, false);
		motionGroup.setLayoutData(gridData);
		addMotionSetting(motionGroup);
	}

	private void addMotionSetting(Group motionGroup){
		GridLayout gridLayout = new GridLayout();
		gridLayout.numColumns = 4;
		motionGroup.setLayout(gridLayout);

		new Label(motionGroup, SWT.NONE).setText("motor");
		motor = new Combo(motionGroup, SWT.NONE);
		motor.setItems(motorNames);
		motor.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		motor.select(0);
//		motor.setText(motor.getItem(0));
	}


}
