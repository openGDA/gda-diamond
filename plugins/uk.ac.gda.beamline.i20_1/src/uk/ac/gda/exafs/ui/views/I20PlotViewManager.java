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

import org.eclipse.ui.IViewReference;
import org.eclipse.ui.IWorkbenchPartSite;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.PlotException;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.exafs.ui.data.EdeTimingCalculator;
import uk.ac.gda.exafs.ui.data.TFGParameters;
import uk.ac.gda.exafs.ui.data.TFGTimingCalculator;

/**
 * Controls what is plotted in the XHAndTFGEditorPlotView depending on the last items selected in the HorizontalList
 */
public class I20PlotViewManager {
	
	public static I20PlotViewManager getInstance() {
		if (theInstance == null){
			theInstance = new I20PlotViewManager();
		}
		return theInstance;
	}

	private static volatile Boolean showSingleTimingGroup = false;	
	private static final Logger logger = LoggerFactory.getLogger(I20PlotViewManager.class);
	private static I20PlotViewManager theInstance = null;
	
	private static boolean edeWasLast = false;
	private static EdeScanParameters lastBean = null;
	private static IWorkbenchPartSite lastSite = null;
	private static int lastSelectedGroup = 0;
	
	private I20PlotViewManager(){
	}

	public static Boolean getShowSingleTimingGroup() {
		return showSingleTimingGroup;
	}

	public static void setShowSingleTimingGroup(Boolean showSingleTimingGroup) {
		I20PlotViewManager.showSingleTimingGroup = showSingleTimingGroup;
		
		if (edeWasLast){
			getInstance().updateGraphFromStoredValues();
		}
	}

	private void updateGraphFromStoredValues() {
		if (lastBean != null && lastSite != null){
			updateGraph(lastBean,lastSite,lastSelectedGroup);
		}
	}

	public void updateGraph(EdeScanParameters bean, IWorkbenchPartSite site, int selectedGroup){
		
		// find an instanceof the view
		IViewReference[] views = site.getPage().getViewReferences();
		
		for (IViewReference view : views){
			if (view.getId().equals(XHAndTFGEditorPlotView.ID)){
				try {
					storeValues(bean, site, selectedGroup);
					
					DoubleDataset[] points = null;
					String plotTitle = "Acquisition Timing Profile";
					if (showSingleTimingGroup) {
						plotTitle = bean.getGroups().get(selectedGroup).getLabel();
						if (plotTitle == null || plotTitle.isEmpty()){
							plotTitle = "Selected Timing Group";
						}
						points = EdeTimingCalculator.calculateTimingGroupPoints(bean, selectedGroup);
					} else {
						points = EdeTimingCalculator.calculateTimePoints(bean);
					}					
					((XHAndTFGEditorPlotView)view.getView(false)).updateEDEPoints(points,plotTitle);
				} catch (PlotException e) {
					// TODO Auto-generated catch block
					logger.error("TODO put description of error here", e);
				}
			}
		}		
	}

	private void storeValues(EdeScanParameters bean, IWorkbenchPartSite site, int selectedGroup) {
		edeWasLast = true;
		lastBean = bean;
		lastSite = site;
		lastSelectedGroup = selectedGroup;
	}

	public void updateGraph(TFGParameters scanBean, IWorkbenchPartSite site, int frameToReturn) {
		// find an instanceof the view
		IViewReference[] views = site.getPage().getViewReferences();
		
		for (IViewReference view : views){
			if (view.getId().equals(XHAndTFGEditorPlotView.ID)){
				edeWasLast = false;
				final AbstractDataset[] points = TFGTimingCalculator.calculateTimePoints(scanBean,frameToReturn);
				try {
					String plotTitle = scanBean.getTimeFrames().get(frameToReturn).getLabel();
					((XHAndTFGEditorPlotView)view.getView(false)).updateTFGPoints(points,plotTitle);
				} catch (PlotException e) {
					// TODO Auto-generated catch block
					logger.error("TODO put description of error here", e);
				}
			}
		}		
	}
}
