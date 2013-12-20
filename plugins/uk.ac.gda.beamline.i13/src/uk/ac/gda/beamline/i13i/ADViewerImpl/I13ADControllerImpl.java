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

package uk.ac.gda.beamline.i13i.ADViewerImpl;

import gda.device.Scannable;
import gda.device.ScannableMotionUnits;
import gda.jython.InterfaceProvider;
import gda.rcp.views.CompositeFactory;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;

import uk.ac.gda.beamline.i13i.DisplayScaleProvider;
import uk.ac.gda.epics.adviewer.ADControllerImpl;

public class I13ADControllerImpl extends  ADControllerImpl implements InitializingBean {
	private static final Logger logger = LoggerFactory.getLogger(I13ADControllerImpl.class);

	private String setExposureTimeCmd;

	@Override
	public void setExposure(double d) {
		final String cmd = String.format(getSetExposureTimeCmd(), d);
		try {
			String result = InterfaceProvider.getCommandRunner().evaluateCommand(cmd);
			if( result == null)
				throw new Exception("Error executing command '" + cmd + "'");
		} catch (Exception e) {
			logger.error("Error setting exposure time", e);
		}		
	}

	private String getSetExposureTimeCmd() {
		return setExposureTimeCmd;
	}

	@Override
	public void setSetExposureTimeCmd(String setExposureTimeCmd) {
		this.setExposureTimeCmd = setExposureTimeCmd;
	}

	private Scannable lensScannable;


	public Scannable getLensScannable() {
		return lensScannable;
	}

	public void setLensScannable(Scannable lensScannable) {
		this.lensScannable = lensScannable;
	}


	@Override
	public void afterPropertiesSet() throws Exception {
		super.afterPropertiesSet();
		if (setExposureTimeCmd == null)
			throw new IllegalArgumentException("setExposureTimeCmd == null");		
		
	}


	private Scannable rotationAxisXScannable;
	private DisplayScaleProvider displayScaleProvider;
	private Scannable cameraXYScannable;
	private String autoCentreCmd;
	private String showNormalisedImageCmd;
	private String histogramPlotId;
	private String imagePlotId;

	private DisplayScaleProvider cameraScaleProvider;

	private ScannableMotionUnits sampleCentringXMotor;

	private ScannableMotionUnits sampleCentringYMotor;

	private CompositeFactory stagesCompositeFactory;



	public Scannable getRotationAxisXScannable() {
		return rotationAxisXScannable;
	}

	public void setRotationAxisXScannable(Scannable rotationAxisXScannable) {
		this.rotationAxisXScannable = rotationAxisXScannable;
	}

	public DisplayScaleProvider getDisplayScaleProvider() {
		return displayScaleProvider;
	}

	public void setDisplayScaleProvider(DisplayScaleProvider displayScaleProvider) {
		this.displayScaleProvider = displayScaleProvider;
	}

	public Scannable getCameraXYScannable() {
		return cameraXYScannable;
	}

	public void setCameraXYScannable(Scannable cameraXYScannable) {
		this.cameraXYScannable = cameraXYScannable;
	}

	public String getAutoCentreCmd() {
		return autoCentreCmd;
	}

	public void setAutoCentreCmd(String autoCentreCmd) {
		this.autoCentreCmd = autoCentreCmd;
	}

	public String getShowNormalisedImageCmd() {
		return showNormalisedImageCmd;
	}

	public void setShowNormalisedImageCmd(String showNormalisedImageCmd) {
		this.showNormalisedImageCmd = showNormalisedImageCmd;
	}

	public String getHistogramPlotId() {
		return histogramPlotId;
	}

	public void setHistogramPlotId(String histogramPlotId) {
		this.histogramPlotId = histogramPlotId;
	}

	public String getImagePlotId() {
		return imagePlotId;
	}

	public void setImagePlotId(String imagePlotId) {
		this.imagePlotId = imagePlotId;
	}

	
	public DisplayScaleProvider getCameraScaleProvider() {
		return cameraScaleProvider;
	}

	public void setCameraScaleProvider(DisplayScaleProvider cameraScaleProvider) {
		this.cameraScaleProvider = cameraScaleProvider;
	}

	public ScannableMotionUnits getSampleCentringXMotor() {
		return sampleCentringXMotor;
	}

	public void setSampleCentringXMotor(ScannableMotionUnits sampleCentringXMotor) {
		this.sampleCentringXMotor = sampleCentringXMotor;
	}

	public ScannableMotionUnits getSampleCentringYMotor() {
		return sampleCentringYMotor;
	}

	public void setSampleCentringYMotor(ScannableMotionUnits sampleCentringYMotor) {
		this.sampleCentringYMotor = sampleCentringYMotor;
	}

	public CompositeFactory getStagesCompositeFactory() {
		return stagesCompositeFactory;
	}

	public void setStagesCompositeFactory(CompositeFactory stagesCompositeFactory) {
		this.stagesCompositeFactory = stagesCompositeFactory;
	}

}
