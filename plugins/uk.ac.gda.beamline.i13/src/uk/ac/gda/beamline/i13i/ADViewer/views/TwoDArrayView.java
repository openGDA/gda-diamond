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

package uk.ac.gda.beamline.i13i.ADViewer.views;

import org.dawb.common.ui.plot.tool.IToolPageSystem;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;

import uk.ac.gda.beamline.i13i.I13IBeamlineActivator;
import uk.ac.gda.beamline.i13i.ADViewer.ADController;
import uk.ac.gda.beamline.i13i.ADViewer.composites.TwoDArray;

public class TwoDArrayView extends ViewPart implements InitializingBean{
	private static final Logger logger = LoggerFactory.getLogger(TwoDArrayView.class);

	private TwoDArray areaDetectorViewComposite;
	ADController config;
	
	public TwoDArrayView(ADController config) {
		this.config = config;
	}

	@Override
	public void afterPropertiesSet() throws Exception {
		if( config == null)
			throw new Exception("Config is null");
	}

	@Override
	public void createPartControl(Composite parent) {

		parent.setLayout(new FillLayout());
		areaDetectorViewComposite = new TwoDArray(this, parent, SWT.NONE, config);
		setTitleImage(I13IBeamlineActivator.getImageDescriptor("icons/AreaDetectorProfileView.gif").createImage());
		setPartName(config.getDetectorName() + " Array View" );

	}

	@Override
	public void setFocus() {
		areaDetectorViewComposite.setFocus();
	}

	@Override
	public void dispose() {
		super.dispose();
	}

	@Override
	public Object getAdapter(@SuppressWarnings("rawtypes") Class clazz) {
		if (clazz == IToolPageSystem.class) {
			return this.areaDetectorViewComposite.getPlottingSystem();
		}
		return super.getAdapter(clazz);
	}
	
	
}
