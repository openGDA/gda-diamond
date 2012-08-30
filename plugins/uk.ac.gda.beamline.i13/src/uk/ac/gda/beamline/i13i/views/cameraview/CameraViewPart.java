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

package uk.ac.gda.beamline.i13i.views.cameraview;

import gda.device.detector.areadetector.v17.NDPluginBase;
import gda.device.detector.areadetector.v17.NDProcess;
import gda.images.camera.MotionJpegOverHttpReceiverSwt;
import gda.jython.InterfaceProvider;

import org.eclipse.draw2d.ColorConstants;
import org.eclipse.draw2d.geometry.Rectangle;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.jface.dialogs.IInputValidator;
import org.eclipse.jface.dialogs.InputDialog;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.ImageData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.IActionBars;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.SDAPlotter;
import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.IntegerDataset;
import uk.ac.diamond.scisoft.analysis.dataset.Stats;
import uk.ac.gda.beamline.i13i.I13IBeamlineActivator;

/**
 * View to display the live images from the camera Used in alignment and monitoring
 */
public class CameraViewPart extends ViewPart implements NewImageListener {

	static final Logger logger = LoggerFactory.getLogger(CameraViewPart.class);

	static public String ID = "uk.ac.gda.client.tomo.CameraView";
	private CameraComposite cameraComposite;

	private CameraViewPartConfig cameraConfig;
	private MotionJpegOverHttpReceiverSwt videoReceiver;

	public CameraViewPart() {
	}

	@Override
	public void createPartControl(Composite parent) {

		cameraConfig = I13IBeamlineActivator.getCameraConfig();

		if (cameraConfig == null) {
			Label lblCamera = new Label(parent, SWT.NONE);
			lblCamera.setText("No CameraViewPartConfig service found");
			return;
		}
		try {
			NDPluginBase arrayBase = cameraConfig.getNdArray().getPluginBase();
			if(!arrayBase.isCallbacksEnabled_RBV())
				arrayBase.enableCallbacks();
			NDProcess ndProcess = cameraConfig.getNdProcess();
			if( ndProcess.getEnableOffsetScale_RBV()!=1)
				ndProcess.setEnableOffsetScale(1);
			if( ndProcess.getDataTypeOut_RBV() != NDProcess.DatatypeOut_UInt8)
				ndProcess.setDataTypeOut(NDProcess.DatatypeOut_UInt8);
			
			ndProcess.setEnableHighClip(1);
			ndProcess.setEnableLowClip(1);
			ndProcess.setHighClip(255);
			ndProcess.setLowClip(0);

			String url = cameraConfig.getFfmpegStream().getMJPG_URL_RBV();
			videoReceiver = new MotionJpegOverHttpReceiverSwt();
			videoReceiver.setUrl(url);
			videoReceiver.configure();
		} catch (Exception e1) {
			logger.error("Error creating controls for camera view", e1);
			return;
		}
		videoReceiver.start();
		
		cameraComposite = new CameraComposite(parent, SWT.NONE, parent.getDisplay(), videoReceiver, this);

		Action setExposureTime = new Action("Set Exposure Time") {
			@Override
			public void run() {
				try {
					setExposureTime();
				} catch (Exception e) {
					logger.error("Error setting exposure time", e);
				}
			}
		};

		Action zoomFit = new Action("Zoom to Fit") {
			@Override
			public void run() {
				zoomToFit();
			}
		};
		Action showRawData = new Action("Show Raw Data") {
			@Override
			public void run() {
				try {
					showRawData();
				} catch (Exception e) {
					logger.error("Error showing raw data", e);
				}
			}
		};
		Action reconnect = new Action("Reconnect") {
			@Override
			public void run() {
				try {
					reconnect();
				} catch (Exception e) {
					logger.error("Error re-connecting to stream", e);
				}
			}

		};
		Action autoBrightnessAction = new Action("Auto-Contrast") {
			@Override
			public void run() {
				try {
					autoBrightness();
				} catch (Exception e) {
					logger.error("Error performing auto-constrast", e);
				}
			}
		};
		imageKeyAction = new Action("Image Key", IAction.AS_CHECK_BOX) {
			@Override
			public void run() {
				//this runs after the state has been changed
				showImageKey(isChecked());
			}
		};
		imageKeyAction.setChecked(false);//do not 
		IActionBars actionBars = getViewSite().getActionBars();
		IMenuManager dropDownMenu = actionBars.getMenuManager();
		dropDownMenu.add(reconnect);
		dropDownMenu.add(imageKeyAction);
		IToolBarManager toolBar = actionBars.getToolBarManager();
		toolBar.add(setExposureTime);
		toolBar.add(autoBrightnessAction);
		toolBar.add(zoomFit);
		toolBar.add(showRawData);

	}
	protected void showRawData() throws Exception {
		AbstractDataset arrayData = getArrayData();
		SDAPlotter.imagePlot("Detector Image", arrayData);
	}

	protected void setExposureTime() throws Exception {
		double acquireTime = cameraConfig.getAdBase().getAcquireTime_RBV();
		InputDialog dlg = new InputDialog(Display.getCurrent().getActiveShell(), "Set exposure time",
				"Enter a new value for the exposure time in secs:", Double.toString(acquireTime), new IInputValidator(){

					@Override
					public String isValid(String newText) {
						try{
							Double.valueOf(newText);
						} catch(Exception e){
							return "Value is not recognised as a number '" + newText + "'";
						}
						return null;
					}
			
		});
		if (dlg.open() == Window.OK) {
			String cmd = String.format(cameraConfig.getSetExposureTimeCmd(), dlg.getValue());
			InterfaceProvider.getCommandRunner().evaluateCommand(cmd);
		}
	}

	protected void reconnect() throws Exception {
		if( videoReceiver != null)
			videoReceiver.closeConnection();
		else 
			videoReceiver = new MotionJpegOverHttpReceiverSwt();
		String url = cameraConfig.getFfmpegStream().getMJPG_URL_RBV();
		videoReceiver.setUrl(url);
		videoReceiver.configure();
		videoReceiver.start();
		
	}

	protected void autoBrightness() throws Exception {
		AbstractDataset dataset = getArrayData();

		double[] m = Stats.quantile(dataset, 0.1, 0.9);
		
		if (Double.compare(m[1], m[0]) <= 0)
			return;

		double max = m[1];
		double min = m[0];
		double offset = -min;
		double scale = 255/(max-min);
		
		cameraConfig.getNdProcess().setScale(scale);
		cameraConfig.getNdProcess().setOffset(offset);
		
	}

	private AbstractDataset getArrayData() throws Exception {
		/*
		 * get data and send to histogram code
		 */
		int arraySize0_RBV = cameraConfig.getNdArray().getPluginBase().getArraySize0_RBV();
		int arraySize1_RBV = cameraConfig.getNdArray().getPluginBase().getArraySize1_RBV();
		int expectedNumPixels = arraySize0_RBV*arraySize1_RBV;
		//as only 14 bits we can just use shorts
		short[] shortArrayData = cameraConfig.getNdArray().getShortArrayData(expectedNumPixels);
		
		int cd[] = new int[expectedNumPixels];
		for (int i = 0; i < expectedNumPixels; i++) {
			cd[i] = (shortArrayData[i] & 0xffff);
		}		

		AbstractDataset dataset = new IntegerDataset(cd, arraySize1_RBV, arraySize0_RBV);
		return dataset;
	}
	private ImageKeyFigure imageKeyFigure;

	private void showImageKey(boolean showImage) {
		if(showImage){
			Rectangle imageKeyBounds = new Rectangle(5, 5, -1, -1);
			cameraComposite.getTopFigure().add(getImageKeyFigure(), imageKeyBounds);
		} else {
			cameraComposite.getTopFigure().remove(getImageKeyFigure());
			
		}
	}

	private ImageKeyFigure getImageKeyFigure() {
		return imageKeyFigure != null ? imageKeyFigure : (imageKeyFigure= new ImageKeyFigure());
	}
	
	
	
	@Override
	public void setFocus() {
	}

	private BeamScaleFigure beamScaleFigure;


	private boolean layoutReset = false;

	private Action imageKeyAction;

	@Override
	public void handlerNewImageNotification(ImageData newImage) {
		// On the first image, ensure we reset the display to match incoming image dimensions
		if (!layoutReset) {
			layoutReset = true;

			// add figures
/*			int offset = 200;
			Rectangle imageBounds = cameraComposite.getViewer().getImageBounds();
*//*			Rectangle scaleBounds = new Rectangle(imageBounds.width - offset, imageBounds.height - offset, -1, -1);
*/			beamScaleFigure = new BeamScaleFigure();
			beamScaleFigure.setBeamSize(100, 100);
			beamScaleFigure.setXScale(1.0);
			beamScaleFigure.setYScale(1.0);
			beamScaleFigure.setBackgroundColor(ColorConstants.darkGray);
//do not add yet			cameraComposite.getTopFigure().add(beamScaleFigure, scaleBounds);
		}
		getImageKeyFigure().newImage(newImage);

	}

	@Override
	public void dispose() {
		super.dispose();
		if (cameraComposite != null) {
			cameraComposite.dispose();
		}
	}

	public void zoomToFit() {
		if (cameraComposite != null)
			cameraComposite.zoomFit();

	}

}
