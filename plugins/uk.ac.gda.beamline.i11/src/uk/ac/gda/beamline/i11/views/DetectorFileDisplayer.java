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

package uk.ac.gda.beamline.i11.views;

import java.io.File;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.apache.commons.io.FilenameUtils;
import org.eclipse.dawnsci.analysis.api.io.ScanFileHolderException;
import org.eclipse.dawnsci.plotting.api.PlotType;
import org.eclipse.january.dataset.IDataset;
import org.eclipse.ui.IViewPart;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;

import gda.analysis.io.MACLoader;
import gda.device.detector.mythen.data.MythenMergedDataset;
import gda.device.detector.mythen.data.MythenProcessedDataset;
import gda.device.detectorfilemonitor.FileProcessor;
import gda.factory.ConfigurableBase;
import gda.factory.FactoryException;
import gda.factory.Findable;
import uk.ac.diamond.scisoft.analysis.io.DataHolder;
import uk.ac.diamond.scisoft.analysis.io.HDF5Loader;
import uk.ac.diamond.scisoft.analysis.io.SRSLoader;
import uk.ac.diamond.scisoft.analysis.io.TIFFImageLoader;
import uk.ac.gda.beamline.synoptics.api.PlotConfigurable;
import uk.ac.gda.beamline.synoptics.views.DetectorFilePlotView;

/**
 * A configurable detector file processor to display detector file content as plot, using generic plot view such as
 * {@link DetectorFilePlotView}
 * <ul>
 * <li>support Mythen, MAC, Pixium detector data file format,</li>
 * <li>permit configurable plot type (see {@link PlotType} for type available) for the same data sets,</li>
 * <li>allow both new plot of each data file or plot over of multiple data files.</li>
 * </ul>
 */
public class DetectorFileDisplayer extends ConfigurableBase implements FileProcessor, PlotConfigurable, InitializingBean, Findable {

	private String viewName;
	public PlotType plotType;
	public Boolean newPlot;
	private String viewID;
	private String name;
	private DetectorFilePlotView plotView;
	private static final Logger logger = LoggerFactory.getLogger(DetectorFileDisplayer.class);
	private Set<String> dataFilesPlotted = new HashSet<>();

	@Override
	public void configure() throws FactoryException {
		if (!isConfigured()) {
			// openView();
			setConfigured(true);
		}
	}

	void openView() {
		if (plotView == null || plotView.isDisposed()) {
			plotView = null;
			IWorkbenchPage page = PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage();
			IViewPart showView = null;
			try {
				showView = page.showView(viewID);
			} catch (PartInitException e) {
				logger.error("Unable to show view plot view " +viewID, e);
			}
			if (showView != null && showView instanceof DetectorFilePlotView) {
				plotView = (DetectorFilePlotView) showView;
				page.activate(plotView);
			}
		}
	}

	private boolean isAlreadyPlotted(String filename) {
		return dataFilesPlotted.contains(filename);
	}

	@Override
	public void processFile(String filename) {
		if (isNewPlot()) {
			dataFilesPlotted.clear();
		}
		if (filename != null && !filename.isEmpty() && !isAlreadyPlotted(filename)) {
			IDataset xds = null;
			IDataset yds = null;
			List<IDataset> others = new ArrayList<>();
			String name = FilenameUtils.getName(filename);
			if (name.contains("mythen")) {
				if (FilenameUtils.getName(filename).contains("summed")) {
					MythenMergedDataset mergedDataset = new MythenMergedDataset(new File(filename));
					xds = mergedDataset.getAngleDataSet();
					yds = mergedDataset.getCountDataSet();
				} else {
					MythenProcessedDataset mythenProcessedDataset = new MythenProcessedDataset(new File(filename));
					xds = mythenProcessedDataset.getAngleDataset();
					yds = mythenProcessedDataset.getCountDataset();
				}
				xds.setName("delta");
				yds.setName(name);
			} else if (name.contains("mac")) {
				try {
					DataHolder loadFile = new MACLoader(filename).loadFile();
					xds = loadFile.getDataset(0);
					xds.setName("tth");
					yds = loadFile.getDataset(1);
					yds.setName(name);
				} catch (ScanFileHolderException e) {
					logger.error("Error load MAC data file" + filename, e);
				}

			} else if (name.contains("pixium")) {
				if (FilenameUtils.isExtension(filename, "dat")) {
					// get integrated data from .dat file
					try {
						DataHolder loadFile = new SRSLoader(filename).loadFile();
						xds = loadFile.getDataset(0);
						xds.setName("angle");
						yds = loadFile.getDataset(1);
						yds.setName(name);
					} catch (ScanFileHolderException e) {
						logger.error("Error load pixium .dat file", e);
					}
				} else if (FilenameUtils.isExtension(filename, "tif")) {
					try {
						DataHolder loadFile = new TIFFImageLoader(filename).loadFile();
						xds = loadFile.getDataset(0);
					} catch (ScanFileHolderException e) {
						logger.error("Error load pixium .tif file", e);
					}
				} else if (FilenameUtils.isExtension(filename, "nxs")) {
					try {
						DataHolder loadFile = new HDF5Loader(filename).loadFile();
						if (getPlotType() == PlotType.IMAGE || getPlotType() == PlotType.SURFACE) {
							xds = loadFile.getDataset("image");
						} else {
							xds = loadFile.getDataset("angle");
							xds.setName("angle");
							yds = loadFile.getDataset("integrated");
						}
					} catch (ScanFileHolderException e) {
						logger.error("Error load pixium .nxs file", e);
					}
				}
			} else {
				// TODO add support for native mythen data file collected using EPICS or QT-GUI
				if (FilenameUtils.isExtension(filename, "dat")) {
					// Plot 'normal' scan data from SRS files
					try {
						DataHolder loadFile = new SRSLoader(filename).loadFile();
						String[] names = loadFile.getNames();
						xds = loadFile.getDataset(0);
						yds = loadFile.getDataset(1);
						for (int i = 2; i < names.length; i++) {
							others.add(loadFile.getDataset(i));
						}
					} catch (ScanFileHolderException e) {
						logger.error("Error loading .dat file '{}'", filename, e);
					}
				}
			}

			if (xds != null && yds != null) {
				dataFilesPlotted.add(filename);
				openView();
				plotView.updatePlot(xds, yds, "Plots of selected detector data files",
						xds.getName(), yds.getName(), isNewPlot(), getPlotType());
				for (IDataset data: others) {
					plotView.updatePlot(xds, data, null, xds.getName(), data.getName(), false, getPlotType());
				}
			}
		} else {
			openView();
			plotView.updatePlot(null, null, "Plots of selected detector data files",
					"angle (degree)", "counts", isNewPlot(), getPlotType());
		}
	}

	public String getViewName() {
		return viewName;
	}

	public void setViewName(String viewName) {
		this.viewName = viewName;
	}

	public String getViewID() {
		return viewID;
	}

	public void setViewID(String viewID) {
		this.viewID = viewID;
	}

	@Override
	public boolean isNewPlot() {
		return newPlot;
	}

	@Override
	public void setNewPlot(boolean value) {
		this.newPlot = value;
	}

	@Override
	public void setPlotType(PlotType type) {
		this.plotType = type;
	}

	@Override
	public PlotType getPlotType() {
		return plotType;
	}

	@Override
	public void setName(String name) {
		this.name = name;
	}

	@Override
	public String getName() {
		return name;
	}

	@Override
	public void afterPropertiesSet() throws Exception {
		if (viewName == null)
			throw new IllegalArgumentException("viewName is null");
		if (viewID == null) {
			throw new IllegalArgumentException("viewID == null");
		}
	}

}
