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
import org.eclipse.ui.IPartListener2;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchPart;
import org.eclipse.ui.IWorkbenchPartReference;
import org.eclipse.ui.IWorkbenchPartSite;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;

import uk.ac.gda.beamline.i13i.I13IBeamlineActivator;
import uk.ac.gda.beamline.i13i.ADViewer.ADController;
import uk.ac.gda.beamline.i13i.ADViewer.composites.Histogram;

public class HistogramView extends ViewPart implements InitializingBean{
	private static final Logger logger = LoggerFactory.getLogger(HistogramView.class);

	private Histogram areaDetectorProfileComposite;
	ADController config;
	
	public HistogramView(ADController config) {
		this.config = config;
	}

	@Override
	public void afterPropertiesSet() throws Exception {
		if( config == null)
			throw new Exception("Config is null");
		
	}
	private IPartListener2 partListener;
	

	@Override
	public void createPartControl(Composite parent) {

		parent.setLayout(new FillLayout());
		areaDetectorProfileComposite = new Histogram(this, parent, SWT.NONE, config);
		try {
			areaDetectorProfileComposite.start();
		} catch (Exception e) {
			logger.error("Error starting  areaDetectorProfileComposite", e);
		}
		setTitleImage(I13IBeamlineActivator.getImageDescriptor("icons/AreaDetectorProfileView.gif").createImage());
		setPartName(config.getDetectorName() + " Profile View" );
		
		partListener = new IPartListener2() {
			
			@Override
			public void partVisible(IWorkbenchPartReference partRef) {
				// TODO Auto-generated method stub
				
			}
			
			@Override
			public void partOpened(IWorkbenchPartReference partRef) {
				// TODO Auto-generated method stub
				
			}
			
			@Override
			public void partInputChanged(IWorkbenchPartReference partRef) {
				// TODO Auto-generated method stub
				
			}
			
			@Override
			public void partHidden(IWorkbenchPartReference partRef) {
				IWorkbenchPage page = partRef.getPage();
				page.toString();
				IWorkbenchPart part = partRef.getPart(false);
				part.toString();
				if( part == HistogramView.this){
					((HistogramView)part).toString();
				}
				
			}
			
			@Override
			public void partDeactivated(IWorkbenchPartReference partRef) {
				// TODO Auto-generated method stub
				
			}
			
			@Override
			public void partClosed(IWorkbenchPartReference partRef) {
				// TODO Auto-generated method stub
				
			}
			
			@Override
			public void partBroughtToTop(IWorkbenchPartReference partRef) {
				// TODO Auto-generated method stub
				
			}
			
			@Override
			public void partActivated(IWorkbenchPartReference partRef) {
				// TODO Auto-generated method stub
				
			}
		};
		getSite().getPage().addPartListener(partListener);
		
	}

	@Override
	public void setFocus() {
		areaDetectorProfileComposite.setFocus();
	}

	@Override
	public void dispose() {
		super.dispose();
		if(partListener != null){
			getSite().getPage().removePartListener(partListener);
			partListener = null;
		}
	}

	@Override
	public Object getAdapter(@SuppressWarnings("rawtypes") Class clazz) {
		if (clazz == IToolPageSystem.class) {
			return this.areaDetectorProfileComposite.getPlottingSystem();
		}
		return super.getAdapter(clazz);
	}


	
	
}
