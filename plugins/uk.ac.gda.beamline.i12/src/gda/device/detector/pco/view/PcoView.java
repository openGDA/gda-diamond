/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package gda.device.detector.pco.view;

import org.dawnsci.plotting.jreality.overlay.Overlay2DConsumer;
import org.dawnsci.plotting.jreality.overlay.Overlay2DProvider;
import org.dawnsci.plotting.jreality.overlay.OverlayProvider;
import org.dawnsci.plotting.jreality.overlay.OverlayType;
import org.dawnsci.plotting.jreality.overlay.VectorOverlayStyles;
import org.dawnsci.plotting.jreality.overlay.primitives.PrimitiveType;
import org.dawnsci.plotting.jreality.tool.IImagePositionEvent;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.MouseAdapter;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.plotserver.GuiPlotMode;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.IPlotUI;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.Plot2DUI;
import uk.ac.diamond.scisoft.analysis.rcp.views.PlotView;
import uk.ac.diamond.scisoft.analysis.rcp.views.SidePlotView;
/**
 *
 */
public class PcoView extends ViewPart implements Overlay2DConsumer {
	private static final Logger logger = LoggerFactory.getLogger(PcoView.class);

	Overlay2DProvider provider;
	PlotView plotView;
	SidePlotView sidePlotView;
	
	int boxPrimID = -1;
	
	double sx, sy, ex, ey;
	
	public PcoView() {
		
	}
	
	@Override
	public void createPartControl(Composite parent) {
		parent.setLayout(new GridLayout(1, false));
		{
			Button button = new Button(parent, SWT.NONE);
			button.addMouseListener(new MouseAdapter() {
				@Override
				public void mouseUp(MouseEvent e) {
					if(sidePlotView != null) {
						sidePlotView.deactivateAllOverlays();
						showOverlays();
						
					}

				}
			});
			button.setText("Select ROI");
		}

		try {
			// get an instance of the plotView we want to use
			plotView = (PlotView) getSite().getPage().showView("uk.ac.gda.beamline.i12.pcoplotview",
					null, IWorkbenchPage.VIEW_CREATE);
			
			plotView.updatePlotMode(GuiPlotMode.TWOD);
			
			// then register this with the plot.
			plotView.getMainPlotter().registerOverlay(this);
			
			IPlotUI plotUI = plotView.getPlotUI();
			if(plotUI instanceof Plot2DUI) {
				sidePlotView = ((Plot2DUI)plotUI).getSidePlotView();
			}			
			
		} catch (PartInitException e) {
			logger.error("Error creating pco view",e);
		} 

	}

	@Override
	public void setFocus() {
		// TODO Auto-generated method stub

	}

	@Override
	public void hideOverlays() {
		System.out.println("Calling Hide");
		if(provider != null) {
			provider.setPrimitiveVisible(boxPrimID, false);
		}

	}

	@Override
	public void showOverlays() {
		System.out.println("Calling Show");
		if(provider != null) {
			boxPrimID = provider.registerPrimitive(PrimitiveType.BOX);
			provider.setPrimitiveVisible(boxPrimID, true);
		}
	}

	@Override
	public void registerProvider(OverlayProvider provider) {
		this.provider = (Overlay2DProvider) provider; 
		boxPrimID = provider.registerPrimitive(PrimitiveType.BOX);
		System.out.println("BoxID =" +boxPrimID);
	}

	@Override
	public void removePrimitives() {
		System.out.println("Calling this");
		boxPrimID = -1;
	}

	@Override
	public void unregisterProvider() {
		System.out.println("Calling this2");
		// TODO Auto-generated method stub
		// internal cleanup.
	}

	@Override
	public void imageDragged(IImagePositionEvent event) {
		updateROI(event);		
	}

	@Override
	public void imageFinished(IImagePositionEvent event) {
		updateROI(event);	
	}

	@Override
	public void imageStart(IImagePositionEvent event) {
		if(boxPrimID == -1) {
			boxPrimID = provider.registerPrimitive(PrimitiveType.BOX);
			System.out.println("Reregistering BoxID =" +boxPrimID);
		}
		provider.setPrimitiveVisible(boxPrimID, true);
		sx = event.getImagePosition()[0];
		sy = event.getImagePosition()[1];
	}
	
	private void updateROI(IImagePositionEvent event) {
		
		ex = event.getImagePosition()[0];
		ey = event.getImagePosition()[1];
		
		drawROI();
	}
	
	private void drawROI() {
		
		System.out.println("("+sx+","+sy+","+ex+","+ey+")"+boxPrimID);
		if(boxPrimID != -1) {
			provider.begin(OverlayType.VECTOR2D);
			provider.setColour(boxPrimID, java.awt.Color.pink);
			//provider.setTransparency(boxPrimID, 0.5);
			provider.setStyle(boxPrimID, VectorOverlayStyles.OUTLINE);
			//provider.setLineThickness(boxPrimID, 2);
			provider.drawBox(boxPrimID, (int)sx, (int)sy, (int)ex, (int)ey);
			provider.end(OverlayType.VECTOR2D);	
		}
		
	}

}
