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

package gda.device.zebra;

import gda.device.detector.areadetector.v17.NDFile;
import gda.device.detector.areadetector.v17.NDFile.FileWriteMode;
import gda.device.detector.areadetector.v17.NDFileHDF5;
import gda.device.detector.areadetector.v17.NDPluginBase;
import gda.device.detector.areadetector.v17.impl.ADBaseImpl;
import gda.device.detector.areadetector.v17.impl.NDFileImpl;
import gda.scan.TurboXasScan;
import gda.spring.V17NDFileFactoryBean;
import gda.spring.V17NDFileHDF5FactoryBean;

/**
 * This class can be used to set up the area detector part of a Zebra to produce
 * an hdf file with timing and encoder values for each captured frame. 
 * This can be used as part of a {@link TurboXasScan}.
 * 
 * @since 20/9/2016
 */
public class ZebraAreaDetectorPreparer {

	private String fileDirectory;
	private String filenameTemplate = "%s%s.hdf";
	private String filename = "zebraDetector";

	/** Suffix used for HDF related PVs in the NDFile plugin.
	 * Zebra area detector on i20-1 uses "HDF:" - 'normal' area detectors use "HDF5:" ...*/
	private String hdfPvSuffix = "HDF5:";
	private String camPvSuffix = "CAM:";

	/** base PV for area detector, including : at end (e.g. 'BL20J-EA-ZEBRA-01:', 'ws146-AD-SIM-01:' */
	private String adBasePv;

	private NDFileHDF5 ndFileHdf5;
	private ADBaseImpl adBaseImpl;

	public ZebraAreaDetectorPreparer( String adBasePv ) {
		this.adBasePv = adBasePv;
	}

	/**
	 * Create new set of NDFile, NDFileHdf5, ADBaseImpl objects for area detector hdf writer.
	 * @throws Exception
	 */
	private void createNewPlugins() throws Exception {

		// Create NDFile object using factory bean
		V17NDFileFactoryBean nfileFactory = new V17NDFileFactoryBean();
		nfileFactory.setResetToInitialValues(false);
		nfileFactory.setPrefix(adBasePv+hdfPvSuffix);
		nfileFactory.afterPropertiesSet();
		NDFile ndFile = nfileFactory.getObject();

		// Create NDFileHDF5 object using factory bean
		V17NDFileHDF5FactoryBean hdfFileFactory = new V17NDFileHDF5FactoryBean();
		hdfFileFactory.setNdFileImpl( (NDFileImpl) ndFile);
		hdfFileFactory.afterPropertiesSet();
		ndFileHdf5 = hdfFileFactory.getObject();

		// ADBase
		adBaseImpl = new ADBaseImpl();
		adBaseImpl.setBasePVName(adBasePv+camPvSuffix);
		//adBaseImpl.setDeviceName(adBasePv);
		adBaseImpl.afterPropertiesSet();

	}

	private void checkCreatePlugins() throws Exception {
		if (adBaseImpl == null || ndFileHdf5 == null ) {
			createNewPlugins();
		}
	}

	/**
	 * Set up HDF part of area detector to make several captures of data.
	 * Sets the number of captures, file output name and directory, filename format, and some other parameters.
	 * capture mode is set to 'stream', so that captured data is written straight to file.
	 *
	 * @param numCaptures
	 * @throws Exception
	 */
	public void configure(int numCaptures) throws Exception {
		checkCreatePlugins();

		// Get refs to ndFile and pluginBase from ndFileHdf5
		NDFile ndFile = ndFileHdf5.getFile();
		NDPluginBase ndPluginBase = ndFile.getPluginBase();

		// Need have capture stopped to allow configuring
		ndFile.stopCapture();

		adBaseImpl.setNumImages(numCaptures);

		ndFile.setFilePath(fileDirectory);
		ndFile.setFileName(filename);
		ndFile.setFileTemplate(filenameTemplate);
		ndFile.setNumCapture(numCaptures);
		ndFile.setFileWriteMode(FileWriteMode.STREAM);

		ndFileHdf5.setNumExtraDims(numCaptures);
		ndFileHdf5.setAutoSave(1);
		ndFileHdf5.setWriteFile(1);
		ndFileHdf5.setNumRowChunks(25);
		ndFileHdf5.setNumColChunks(5);

		ndPluginBase.enableCallbacks();
		ndPluginBase.setBlockingCallbacks(0);
	}

	/**
	 * 'Arm' the writer to make it ready to capture data (equivalent to clicking the 'Start' button)
	 * @throws Exception
	 */
	public void arm() throws Exception {
		checkCreatePlugins();

		NDFile ndFile = ndFileHdf5.getFile();
		ndFile.startCapture();
	}

	public String getFilenameTemplate() {
		return filenameTemplate;
	}

	public void setFilenameTemplate(String filenameTemplate) {
		this.filenameTemplate = filenameTemplate;
	}

	public String getFileDirectory() {
		return fileDirectory;
	}

	public void setFileDirectory(String fileDirectory) {
		this.fileDirectory = fileDirectory;
	}

	public String getFilename() {
		return filename;
	}

	public void setFilename(String filename) {
		this.filename = filename;
	}

	public String getHdfPvSuffix() {
		return hdfPvSuffix;
	}

	public void setHdfPvSuffix(String hdfPvSuffix) {
		this.hdfPvSuffix = hdfPvSuffix;
	}

	public String getCamPvSuffix() {
		return camPvSuffix;
	}

	public void setCamPvSuffix(String camPvSuffix) {
		this.camPvSuffix = camPvSuffix;
	}
}
