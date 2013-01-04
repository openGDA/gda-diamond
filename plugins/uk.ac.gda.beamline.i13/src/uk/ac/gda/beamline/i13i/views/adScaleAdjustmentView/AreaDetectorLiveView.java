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

package uk.ac.gda.beamline.i13i.views.adScaleAdjustmentView;

import org.dawb.common.ui.plot.tool.IToolPageSystem;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.IPartListener2;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchPart;
import org.eclipse.ui.IWorkbenchPartReference;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;

import uk.ac.gda.beamline.i13i.I13IBeamlineActivator;

public class AreaDetectorLiveView extends ViewPart implements InitializingBean{
	private static final Logger logger = LoggerFactory.getLogger(AreaDetectorLiveView.class);

	private AreaDetectorLiveComposite areaDetectorLiveComposite;
	ADController config;
	
	public AreaDetectorLiveView(ADController config) {
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
		areaDetectorLiveComposite = new AreaDetectorLiveComposite(parent, SWT.NONE, config);
		setTitleImage(I13IBeamlineActivator.getImageDescriptor("icons/AreaDetectorLiveView.gif").createImage());
		setPartName(config.getDetectorName() + " Live View" );
		
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
				if( part == AreaDetectorLiveView.this){
					((AreaDetectorLiveView)part).toString();
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
		areaDetectorLiveComposite.setFocus();
	}

	@Override
	public void dispose() {
		super.dispose();
		if(partListener != null){
			getSite().getPage().removePartListener(partListener);
			partListener = null;
		}
	}

}
