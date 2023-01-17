/**
 * Copyright © 2023 Diamond Light Source Ltd.
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

package gda.device.detector;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.january.dataset.Dataset;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.nexus.extractor.NexusGroupData;
import gda.data.nexus.tree.INexusTree;
import gda.device.Detector;
import gda.device.DeviceException;
import uk.ac.gda.beans.medipix.ROIRegion;

/**
 * Detector class that processes a 2-dimensional dataset from a detector and computes the sum over
 * one or more ROIs.
 * The readout value is an array containing the sum over each ROI.
 */
public class RoiExtractor extends DetectorBase {

	private static final Logger logger = LoggerFactory.getLogger(RoiExtractor.class);

	private List<ROIRegion> roiList = new ArrayList<>();
	private String outputFormatTemplate = "%.4g";
	private Detector detector;

	public RoiExtractor() {
		setInputNames(new String[] {});
	}

	public String getOutputFormatTemplate() {
		return outputFormatTemplate;
	}

	public void setOutputFormatTemplate(String outputFormatTemplate) {
		this.outputFormatTemplate = outputFormatTemplate;
	}

	public Detector getDetector() {
		return detector;
	}

	public void setDetector(Detector detector) {
		this.detector = detector;
	}

	@Override
	public String[] getOutputFormat() {
		return roiList.stream().map(roi -> outputFormatTemplate).toArray(String[]::new);
	}

	@Override
	public String[] getExtraNames() {
		return roiList.stream().map(ROIRegion::getRoiName).toArray(String[]::new);
	}

	public void clearRois() {
		roiList.clear();
	}

	/**
	 * Add a new ROI to be processed
	 * @param name
	 * @param startX
	 * @param startY
	 * @param endX
	 * @param endY
	 */
	public void addRoi(String name, int startX, int startY, int endX, int endY) {
		roiList.add(new ROIRegion(name, startX, startY, endX, endY));
	}

	/**
	 *
	 * @return List of ROIs to be processed
	 */
	public List<ROIRegion> getRois() {
		return roiList;
	}

	/**
	 * Readout the latest detector data, process the ROIs, and return an array of the ROI sum values.
	 */
	@Override
	public Object readout() throws DeviceException {
		Dataset latestDetectorData = readoutDetectorData();
		return roiList.stream()
				.map(roi -> processRoi(roi, latestDetectorData))
				.toArray(Double[]::new);
	}

	/**
	 * Readout latest detector data and extract a Dataset.
	 *
	 * @return
	 * @throws DeviceException
	 */
	public Dataset readoutDetectorData() throws DeviceException {
		Object detectorData = detector.readout();
		if (detectorData instanceof NXDetectorData detData) {
			return extractDataset(detData);
		} else if (detectorData instanceof Dataset detData) {
			return detData;
		}
		logger.warn("Cannot extract ROIs - no suitable detector has been set");
		return null;
	}

	/**
	 * Extract a Dataset from NXDetectorData object by searching through the detector tree
	 * for the currently set detector and finding the first data that is 2-dimensional.
	 *
	 * @param nxdata
	 * @return Dataset extracted from Nexus tree; null if none was found.
	 */
	private Dataset extractDataset(NXDetectorData nxdata) {
		logger.info("Tring to extract 2d dataset from detector data from {}", detector.getName());
		String detectorName = detector.getName();
		INexusTree tree = nxdata.getDetTree(detectorName);
		for(int i=0; i<tree.getNumberOfChildNodes(); i++) {
			NexusGroupData data = tree.getChildNode(i).getData();
			if (data.getDimensions().length == 2) {
				logger.debug("Returning data from Nexus tree : {}", tree.getChildNode(i).getName());
				return data.toDataset();
			}
		}
		logger.warn("No suitable data found in Nexus tree");
		return null;
	}

	/**
	 * Compute the sum over the ROI using the given dataset
	 *
	 * @param roi
	 * @param detectorData
	 * @return sum of dataset values over the ROI; 0 if detectorData is null
	 */
	private double processRoi(ROIRegion roi, Dataset detectorData) {
		if (detectorData == null) {
			return 0;
		}

		logger.debug("Processing counts for ROI : {}", roi.getRoiName());

		// Extract slice from dataset using range set by ROI :
		int[] start = {roi.getXRoi().getRoiStart(), roi.getYRoi().getRoiStart()};
		int[] stop = {roi.getXRoi().getRoiEnd()+1, roi.getYRoi().getRoiEnd()+1};
		var ds = detectorData.getSlice(start, stop, new int[] {1,1});

		// sum over all values in the slice
		var sum = (Number) ds.sum(true);

		return sum.doubleValue();
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

	@Override
	public void collectData() throws DeviceException {
	}

	@Override
	public int getStatus() throws DeviceException {
		return 0;
	}

	@Override
	public boolean createsOwnFiles() throws DeviceException {
		return false;
	}
}
