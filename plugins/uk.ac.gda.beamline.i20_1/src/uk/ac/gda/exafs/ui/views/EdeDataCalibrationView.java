/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.List;

import org.dawnsci.plotting.api.IPlottingSystem;
import org.dawnsci.plotting.api.PlotType;
import org.dawnsci.plotting.api.PlottingFactory;
import org.dawnsci.plotting.api.region.IROIListener;
import org.dawnsci.plotting.api.region.IRegion;
import org.dawnsci.plotting.api.region.IRegion.RegionType;
import org.dawnsci.plotting.api.region.IRegionSystem;
import org.dawnsci.plotting.api.region.ROIEvent;
import org.dawnsci.plotting.api.tool.IToolPageSystem;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.draw2d.ColorConstants;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;

import uk.ac.diamond.scisoft.analysis.dataset.IDataset;
import uk.ac.diamond.scisoft.analysis.roi.LinearROI;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.CalibrationData;
import uk.ac.gda.exafs.data.ClientConfig.ElementReference;

public class EdeDataCalibrationView  extends ViewPart implements CalibrationPlotViewer {

	public static final String REFERENCE_ID = "uk.ac.gda.exafs.ui.views.calibrationreference";
	public static final String EDE_ID = "uk.ac.gda.exafs.ui.views.calibrationEdeData";

	private final IPlottingSystem plottingSystemRef;

	private ElementReference referenceData;
	private IRegion ref1;
	private IRegion ref2;
	private IRegion ref3;

	public EdeDataCalibrationView() throws Exception {
		plottingSystemRef = PlottingFactory.createPlottingSystem();
	}

	@Override
	public void setCalibrationDataReference(ElementReference referenceData) {
		if (this.referenceData != null) {
			return;
		}
		this.referenceData = referenceData;
		this.referenceData.addPropertyChangeListener(ClientConfig.ElementReference.FILE_NAME_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				try {
					updateDdata();
				} catch (Exception e) {
					// TODO Handle this
					e.printStackTrace();
				}
			}
		});
		try {
			updateDdata();
		} catch (Exception e) {
			// TODO Handle this
			e.printStackTrace();
		}
	}

	@Override
	public void createPartControl(Composite parent) {
		plottingSystemRef.createPlotPart(parent,
				getTitle(),
				// unique id for plot.
				getViewSite().getActionBars(),
				PlotType.XY,
				this);
	}

	private void updateDdata() throws Exception {
		if (referenceData.getRefFile() == null) {
			plottingSystemRef.clear();
			return;
		}
		List<IDataset> spectra = new ArrayList<IDataset>(1);
		spectra.add(referenceData.getRefDataNode());

		plottingSystemRef.clear();
		plottingSystemRef.createPlot1D(referenceData.getRefEnergyNode(), spectra, new NullProgressMonitor());
		showReferencePoints();
		plottingSystemRef.repaint();
	}

	private void showReferencePoints() throws Exception {
		// TODO Review to remove hard coded index
		ref1 = plottingSystemRef.getRegion("Ref1");
		if (ref1 == null) {
			ref1 = makeVertLine("Ref1", plottingSystemRef, referenceData.getReferencePoints().get(0),
					ColorConstants.red);
			ref1.addROIListener(referencePointListener);
		}

		ref2 = plottingSystemRef.getRegion("Ref2");
		if (ref2 == null) {
			ref2 = makeVertLine("Ref2", plottingSystemRef,referenceData.getReferencePoints().get(1),
					ColorConstants.green);
			ref2.addROIListener(referencePointListener);
		}

		ref3 = plottingSystemRef.getRegion("Ref3");
		if (ref3 == null) {
			ref3 = makeVertLine("Ref3", plottingSystemRef,referenceData.getReferencePoints().get(2),
					ColorConstants.blue);
			ref3.addROIListener(referencePointListener);
		}

		CalibrationData.INSTANCE.addPropertyChangeListener(CalibrationData.MANUAL_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				updateVisiability();
			}
		});
		updateVisiability();
	}

	private void updateVisiability() {
		ref1.setVisible(CalibrationData.INSTANCE.isManual());
		ref2.setVisible(CalibrationData.INSTANCE.isManual());
		ref3.setVisible(CalibrationData.INSTANCE.isManual());
		plottingSystemRef.repaint();
	}

	private IRegion makeVertLine(String name, IRegionSystem plottingSystem, double pos, Color color) throws Exception {
		IRegion ref = plottingSystem.createRegion(name, RegionType.XAXIS_LINE);
		ref.setRegionColor(color);
		ref.setLineWidth(3);
		ref.setMobile(false);
		ref.setVisible(false);
		ref.setUserRegion(false);
		plottingSystem.addRegion(ref);
		ref.setROI(new LinearROI(new double[] { pos, 0 }, new double[] { pos, 1 }));
		return ref;
	}

	private final IROIListener referencePointListener = new IROIListener() {

		@Override
		public void roiDragged(ROIEvent evt) {
		}

		@Override
		public void roiChanged(ROIEvent evt) {
			List<Double> references = new ArrayList<Double>();
			references.add(ref1.getROI().getPointX());
			references.add(ref2.getROI().getPointX());
			references.add(ref3.getROI().getPointX());
			referenceData.setReferencePoints(references);
		}

		@Override
		public void roiSelected(ROIEvent evt) {
		}
	};


	@Override
	public void setFocus() {
		// TODO Auto-generated method stub
	}

	@Override
	public Object getAdapter(@SuppressWarnings("rawtypes") Class clazz) {
		if (clazz == IToolPageSystem.class) {
			return plottingSystemRef;
		}
		return super.getAdapter(clazz);
	}
}
