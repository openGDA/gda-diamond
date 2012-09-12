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

import gda.device.DeviceException;
import gda.device.detector.areadetector.v17.FfmpegStream;
import gda.device.detector.areadetector.v17.NDPluginBase;
import gda.device.detector.areadetector.v17.NDProcess;
import gda.device.scannable.ScannableStatus;
import gda.device.scannable.ScannableUtils;
import gda.images.camera.DummySwtVideoReceiver;
import gda.images.camera.MotionJpegOverHttpReceiverSwt;
import gda.images.camera.VideoReceiver;
import gda.jython.InterfaceProvider;
import gda.observable.IObserver;

import java.lang.reflect.InvocationTargetException;

import org.apache.commons.math.linear.MatrixUtils;
import org.apache.commons.math.linear.RealVector;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.draw2d.Figure;
import org.eclipse.draw2d.geometry.Rectangle;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.jface.dialogs.IInputValidator;
import org.eclipse.jface.dialogs.InputDialog;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.dialogs.ProgressMonitorDialog;
import org.eclipse.jface.operation.IRunnableWithProgress;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.graphics.Cursor;
import org.eclipse.swt.graphics.ImageData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.MenuItem;
import org.eclipse.ui.IActionBars;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.SDAPlotter;
import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.IntegerDataset;
import uk.ac.diamond.scisoft.analysis.dataset.Stats;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.tools.IImagePositionEvent;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.tools.ImagePositionListener;
import uk.ac.gda.beamline.i13i.I13IBeamlineActivator;
import uk.ac.gda.client.viewer.ImageViewer;

/**
 * View to display the live images from the camera Used in alignment and monitoring
 */
public class CameraViewPart extends ViewPart implements NewImageListener {

	static final Logger logger = LoggerFactory.getLogger(CameraViewPart.class);

	static public String ID = "uk.ac.gda.client.tomo.CameraView";
	private CameraComposite cameraComposite;

	private CameraViewPartConfig cameraConfig;
	private VideoReceiver<ImageData> videoReceiver;

	private boolean moveOnClickEnabled;

	public CameraViewPart() {
	}

	int imageWidth = 4008;
	int imageHeight = 2672;
	static RealVector createVectorOf(double... data) {
		return MatrixUtils.createRealVector(data);
	}
	private Menu rightClickMenu;

	private MenuItem setRotationAxisX;

	protected boolean changeRotationAxisX;

	@Override
	public void createPartControl(Composite parent) {

		cameraConfig = I13IBeamlineActivator.getCameraConfig();

		if (cameraConfig == null) {
			Label lblCamera = new Label(parent, SWT.NONE);
			lblCamera.setText("No CameraViewPartConfig service found");
			return;
		}
		try {
			NDProcess ndProcess = cameraConfig.getNdProcess();
			if (ndProcess.getEnableOffsetScale_RBV() != 1)
				ndProcess.setEnableOffsetScale(1);
			if (ndProcess.getDataTypeOut_RBV() != NDProcess.DatatypeOut_UInt8)
				ndProcess.setDataTypeOut(NDProcess.DatatypeOut_UInt8);

			ndProcess.setEnableHighClip(1);
			ndProcess.setEnableLowClip(1);
			ndProcess.setHighClip(255);
			ndProcess.setLowClip(0);
			NDPluginBase procBase = ndProcess.getPluginBase();
			if (!procBase.isCallbacksEnabled_RBV())
				procBase.enableCallbacks();

			FfmpegStream ffmpegStream = cameraConfig.getFfmpegStream();
			ffmpegStream.setMAXW(cameraConfig.getfFMpegImgWidthRequired());
			ffmpegStream.setMAXH(cameraConfig.getfFMpegImgHeightRequired());
			ffmpegStream.setQUALITY(100.);
			NDPluginBase ffmpegBase = ffmpegStream.getPluginBase();
			String procPortName_RBV = procBase.getPortName_RBV();
			if(!ffmpegBase.getNDArrayPort_RBV().equals(procPortName_RBV) )
				ffmpegBase.setNDArrayPort(procPortName_RBV);
			if (!ffmpegBase.isCallbacksEnabled_RBV())
				ffmpegBase.enableCallbacks();

			NDPluginBase arrayBase = cameraConfig.getNdArray().getPluginBase();
			String procNdArrayPort_RBV = procBase.getNDArrayPort_RBV();
			if(!arrayBase.getNDArrayPort_RBV().equals(procNdArrayPort_RBV) )
				arrayBase.setNDArrayPort(procNdArrayPort_RBV);
			if (!arrayBase.isCallbacksEnabled_RBV())
				arrayBase.enableCallbacks();
			
			
			reconnect();
		} catch (Exception e1) {
			logger.error("Error creating controls for camera view", e1);
			return;
		}

		cameraComposite = new CameraComposite(parent, SWT.NONE, parent.getDisplay(), videoReceiver, this);

		if (cameraConfig.getImageViewerListener() != null) {
			cameraComposite.getViewer().getPositionTool().addImagePositionListener(new ImagePositionListener() {

				@Override
				public void imageStart(IImagePositionEvent event) {
				}

				@Override
				public void imageFinished(IImagePositionEvent event) {
					if (changeRotationAxisX) {
						int beamCentreX = event.getImagePosition()[0];
						int beamCentreY = event.getImagePosition()[1];
						boolean changeCentre = MessageDialog.openQuestion(PlatformUI.getWorkbench().getDisplay().getActiveShell(),
								"Change Beam Centre", "Are you sure you wish to change the roation axis to this position ("
								+ Integer.toString(beamCentreX) + "," + Integer.toString(beamCentreY) + "?");
						if (changeCentre) {
							try {
								final int[] clickCoordinates = event.getImagePosition();
								final RealVector actualClickPoint = createVectorOf(clickCoordinates[0], clickCoordinates[1]);		
								ImageData imageData = cameraComposite.getViewer().getImageData();
								final RealVector imageDataSize = createVectorOf(imageData.width, imageData.height);
								final RealVector imageSize = createVectorOf(imageWidth, imageHeight );
								
								final RealVector clickPointInImage = actualClickPoint.ebeMultiply(imageSize).ebeDivide(imageDataSize);		
								
								
								
								cameraConfig.getRotationAxisXScannable().asynchronousMoveTo(clickPointInImage.getEntry(0));
							} catch (DeviceException e) {
								logger.error("Error setting rotationAxis", e);
							}
						}
						changeRotationAxisX = false;
						final Cursor cursorWait = new Cursor(Display.getCurrent(), SWT.CURSOR_ARROW);
						Display.getDefault().getActiveShell().setCursor(cursorWait);
					}					
					else if (moveOnClickEnabled){
						try {
							cameraConfig.getImageViewerListener().imageFinished(event, cameraComposite.getViewer());
						} catch (DeviceException e) {
							logger.error("Error processing imageFinished", e);
						}
					}

				}

				@Override
				public void imageDragged(IImagePositionEvent event) {
				}
			}, null);

		}

		IActionBars actionBars = getViewSite().getActionBars();
		IMenuManager dropDownMenu = actionBars.getMenuManager();

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
		dropDownMenu.add(new Action("Reconnect") {
			@Override
			public void run() {
				try {
					reconnect();
				} catch (Exception e) {
					logger.error("Error re-connecting to stream", e);
				}
			}

		});

		Action autoExposureAction = new Action("Auto-Exposure") {
			@Override
			public void run() {
				try {
					autoBrightness(true);
				} catch (Exception e) {
					logger.error("Error performing auto-exposure", e);
				}
			}
		};

		Action autoBrightnessAction = new Action("Auto-Contrast") {
			@Override
			public void run() {
				try {
					autoBrightness(false);
				} catch (Exception e) {
					logger.error("Error performing auto-constrast", e);
				}
			}
		};
		/*
		 * if (cameraConfig.getBeamCenterProvider() != null) { final Action centreMarkerAction = new
		 * Action("Centre Marker", IAction.AS_CHECK_BOX) {
		 * @Override public void run() { showCentreMarker(isChecked(), isChecked() ?
		 * cameraConfig.getBeamCenterProvider().getBeamCenter() : null); } }; showCentreMarker(true,
		 * cameraConfig.getBeamCenterProvider().getBeamCenter()); centreMarkerAction.setChecked(true);// do not
		 * cameraConfig.getBeamCenterProvider().addIObserver(new IObserver() {
		 * @Override public void update(Object source, final Object arg) { if (arg instanceof Point &&
		 * centreMarkerAction.isChecked()) { getViewSite().getShell().getDisplay().asyncExec(new Runnable() {
		 * @Override public void run() { showCentreMarker(true, (Point) arg); } }); } } });
		 * dropDownMenu.add(centreMarkerAction); }
		 */
		final Action rotationAxisAction = new Action("Show rotation center", IAction.AS_CHECK_BOX) {
			@Override
			public void run() {
				try {
					showRotationAxis(isChecked());
				} catch (DeviceException e) {
					logger.error("Error showing rotation axis", e);
				}
			}
		};
		try {
			showRotationAxis(true);
			rotationAxisAction.setChecked(true);// do not
		} catch (DeviceException e) {
			logger.error("Error showing rotation axis", e);
		}
		cameraConfig.getRotationAxisXScannable().addIObserver(new IObserver() {

			@Override
			public void update(Object source, final Object arg) {
				if (rotationAxisAction.isChecked()) {
					if( arg instanceof ScannableStatus){
						if(((ScannableStatus)arg).status == ScannableStatus.IDLE){
							getViewSite().getShell().getDisplay().asyncExec(new Runnable() {

								@Override
								public void run() {
									try {
										showRotationAxis(true);
									} catch (DeviceException e) {
										logger.error("Error showing rotation axis", e);
									}

								}
							});
						}
					}
				}

			}
		});
		dropDownMenu.add(rotationAxisAction);

		final Action beamScaleAction = new Action("Show Beam Scale", IAction.AS_CHECK_BOX) {
			@Override
			public void run() {
				// this runs after the state has been changed
				try {
					showBeamScale(isChecked());
				} catch (DeviceException e) {
					logger.error("Error showing beamscale", e);
				}
			}
		};
		beamScaleAction.setChecked(false);// do not
		try {
			showBeamScale(beamScaleAction.isChecked());
		} catch (DeviceException e) {
			logger.error("Error showing beamscale", e);
		}
		
		

		Action imageKeyAction = new Action("Show Image Key", IAction.AS_CHECK_BOX) {
			@Override
			public void run() {
				// this runs after the state has been changed
				showImageKey(isChecked());
			}
		};
		imageKeyAction.setChecked(false);// do not

		Action moveOnClickAction = new Action("MoveOnClick", IAction.AS_CHECK_BOX) {
			@Override
			public void run() {
				// this runs after the state has been changed
				toggleMoveOnClick(isChecked());
			}
		};
		moveOnClickAction.setChecked(false);// do not

		dropDownMenu.add(imageKeyAction);
		dropDownMenu.add(moveOnClickAction);
		dropDownMenu.add(beamScaleAction);
		IToolBarManager toolBar = actionBars.getToolBarManager();
		toolBar.add(autoExposureAction);
		toolBar.add(setExposureTime);
		toolBar.add(autoBrightnessAction);
		toolBar.add(zoomFit);
		toolBar.add(showRawData);

		ImageViewer viewer = cameraComposite.getViewer();
		rightClickMenu = new Menu(viewer.getCanvas());
		setRotationAxisX = new MenuItem(rightClickMenu, SWT.PUSH);
		setRotationAxisX.setText("Mark next click position as rotationAxisX");
		setRotationAxisX.addSelectionListener(new SelectionListener() {
			
			@Override
			public void widgetSelected(SelectionEvent event) {
				final Cursor cursorWait = new Cursor(Display.getDefault(), SWT.CURSOR_HAND);
				Display.getDefault().getActiveShell().setCursor(cursorWait);
				changeRotationAxisX = true;
			}
			
			@Override
			public void widgetDefaultSelected(SelectionEvent event) {
				final Cursor cursorWait = new Cursor(Display.getCurrent(), SWT.CURSOR_HAND);
				Display.getDefault().getActiveShell().setCursor(cursorWait);
				changeRotationAxisX = true;
			}
		});
		
		viewer.getCanvas().setMenu(rightClickMenu);		
		
		
		cameraConfig.getDisplayScaleProvider().addIObserver(new IObserver(){

			@Override
			public void update(Object source, Object arg) {
				Display.getDefault().asyncExec(new Runnable(){
					@Override
					public void run() {
						try {
							if( beamScaleAction.isChecked())
								showBeamScale(true);
						} catch (DeviceException e) {
							logger.error("Error showing beamscale", e);
						}
						try {
							if( rotationAxisAction.isChecked())
								showRotationAxis(true);
						} catch (DeviceException e) {
							logger.error("Error showing rotation axis", e);
						}
					}				
				});
			}});
	}

	protected void toggleMoveOnClick(boolean checked) {
		moveOnClickEnabled = checked;

	}

	protected void showRawData() throws Exception {
		AbstractDataset arrayData = getArrayData();
		if (arrayData != null)
			SDAPlotter.imagePlot("Detector Image", arrayData);
	}

	protected void setExposureTime() throws Exception {
		double acquireTime = cameraConfig.getAdBase().getAcquireTime_RBV();
		InputDialog dlg = new InputDialog(Display.getCurrent().getActiveShell(), "Set exposure time",
				"Enter a new value for the exposure time in secs:", Double.toString(acquireTime),
				new IInputValidator() {

					@Override
					public String isValid(String newText) {
						try {
							Double.valueOf(newText);
						} catch (Exception e) {
							return "Value is not recognised as a number '" + newText + "'";
						}
						return null;
					}

				});
		if (dlg.open() == Window.OK) {
			final String value = dlg.getValue();
			final String cmd = String.format(cameraConfig.getSetExposureTimeCmd(), value);
			
			ProgressMonitorDialog pd = new ProgressMonitorDialog(getSite().getShell());
			pd.run(true /* fork */, true /* cancelable */, new IRunnableWithProgress() {
				@Override
				public void run(IProgressMonitor monitor) throws InvocationTargetException, InterruptedException {
					String title = "Setting exposure time to "+ value;

					monitor.beginTask(title, 100);

					try {
						InterfaceProvider.getCommandRunner().evaluateCommand(cmd);
					} catch (Exception e) {
						logger.error("Error in " + title, e);
					}

					monitor.done();
				}
			
			});
		}
	}

	protected void reconnect() throws Exception {
		if (videoReceiver != null) {
			videoReceiver.closeConnection();
			if (videoReceiver instanceof MotionJpegOverHttpReceiverSwt) {
				((MotionJpegOverHttpReceiverSwt) videoReceiver).createConnection();
			}
		} else {
			FfmpegStream ffmpegStream = cameraConfig.getFfmpegStream();
			String url = ffmpegStream.getMJPG_URL_RBV();
			if (url.equals("DummySwtVideoReceiver")) {
				DummySwtVideoReceiver dummySwtVideoReceiver = new DummySwtVideoReceiver();
				dummySwtVideoReceiver.setDesiredFrameRate(10);
				videoReceiver = dummySwtVideoReceiver;

			} else {
				MotionJpegOverHttpReceiverSwt motionJpegOverHttpReceiverSwt = new MotionJpegOverHttpReceiverSwt();
				motionJpegOverHttpReceiverSwt.setUrl(url);
				motionJpegOverHttpReceiverSwt.configure();
				motionJpegOverHttpReceiverSwt.start();
				videoReceiver = motionJpegOverHttpReceiverSwt;
			}
		}
		videoReceiver.start();

	}

	protected void autoBrightness(final boolean autoExposureTime) throws Exception {
		double topQuantileVal=20000;
		if(autoExposureTime){
			InputDialog dlg = new InputDialog(Display.getCurrent().getActiveShell(), "Auto-exposure",
					"Enter a desired value for 90% quantile:", Double.toString(topQuantileVal),
					new IInputValidator() {

						@Override
						public String isValid(String newText) {
							try {
								Double.valueOf(newText);
							} catch (Exception e) {
								return "Value is not recognised as a number '" + newText + "'";
							}
							return null;
						}

					});
			if (dlg.open() != Window.OK) {
				return;
			}
			topQuantileVal = Double.valueOf(dlg.getValue());
		}
		
		
		final double topQuantileValToUse = topQuantileVal;

		ProgressMonitorDialog pd = new ProgressMonitorDialog(getSite().getShell());
		pd.run(true /* fork */, true /* cancelable */, new IRunnableWithProgress() {
			@Override
			public void run(IProgressMonitor monitor) throws InvocationTargetException, InterruptedException {
				String title = autoExposureTime ? "Adjusting exposure" : "Adjusting constrast";

				monitor.beginTask(title, 100);

				try {
					autoExposureTask(autoExposureTime, monitor);
				} catch (Exception e) {
					logger.error("Error in " + title, e);
				}

				monitor.done();
			}

			private void autoExposureTask(final boolean autoExposureTime, IProgressMonitor monitor) throws Exception {

				if (monitor.isCanceled())
					return;
				monitor.subTask("Reading image");
				monitor.subTask("Analysis image");
				AbstractDataset dataset = getArrayData();

				if (dataset == null) {
					double expoTime = 0.1;
					String desiredAcquireTimeS = Double.toString(expoTime);
					String cmd = String.format(cameraConfig.getSetExposureTimeCmd(), desiredAcquireTimeS);
					InterfaceProvider.getCommandRunner().evaluateCommand(cmd);
					monitor.subTask("The current image is empty. The exposure time is being set to "
							+ desiredAcquireTimeS);
					Thread.sleep((long) (2*1000*expoTime));
					autoExposureTask(autoExposureTime, monitor);
					return;
				}
				double[] m = Stats.quantile(dataset, 0.1, 0.9);

				if (Double.compare(m[1], m[0]) <= 0) {
					if (m[0] > 10000) {
						double acquireTime = cameraConfig.getAdBase().getAcquireTime_RBV();
						double desiredAcquireTime = acquireTime / 2;
						String desiredAcquireTimeS = Double.toString(desiredAcquireTime);
						String cmd = String.format(cameraConfig.getSetExposureTimeCmd(), desiredAcquireTimeS);
						InterfaceProvider.getCommandRunner().evaluateCommand(cmd);
						monitor.subTask("The current exposure time is too high for auto adjustment. The exposure time is being set to "
								+ desiredAcquireTimeS);
						Thread.sleep((long) (2*1000*desiredAcquireTime));
						autoExposureTask(autoExposureTime, monitor);

					}
					return;
				}
				double max = m[1];
				double min = m[0];
				double offset = -min;
				double scale = 255 / (max - min);

				if (autoExposureTime) {
					
					
					
					double factor = topQuantileValToUse / max;
					double acquireTime = cameraConfig.getAdBase().getAcquireTime_RBV();
					double desiredAcquireTime = Math.min(5.0, factor * acquireTime);
					factor = desiredAcquireTime/acquireTime;
					String desireAcquireTimeS = Double.toString(desiredAcquireTime);
					String cmd = String.format(cameraConfig.getSetExposureTimeCmd(), desireAcquireTimeS);
					monitor.subTask("Setting exposure to " + desireAcquireTimeS);
					InterfaceProvider.getCommandRunner().evaluateCommand(cmd);

					offset = offset * factor;
					scale = scale / factor;
				}

				monitor.subTask("Setting up ffmjeg proc plugin for best constrast");
				cameraConfig.getNdProcess().setScale(scale);
				cameraConfig.getNdProcess().setOffset(offset);
			}
		});

	}

	private AbstractDataset getArrayData() throws Exception {
		/*
		 * get data and send to histogram code
		 */
		int arraySize0_RBV = cameraConfig.getNdArray().getPluginBase().getArraySize0_RBV();
		int arraySize1_RBV = cameraConfig.getNdArray().getPluginBase().getArraySize1_RBV();
		int expectedNumPixels = arraySize0_RBV * arraySize1_RBV;
		if (expectedNumPixels == 0)
			return null;
		// as only 14 bits we can just use shorts
		short[] shortArrayData = cameraConfig.getNdArray().getShortArrayData(expectedNumPixels);

		int cd[] = new int[expectedNumPixels];
		for (int i = 0; i < expectedNumPixels; i++) {
			cd[i] = (shortArrayData[i] & 0xffff);
		}

		AbstractDataset dataset = new IntegerDataset(cd, arraySize1_RBV, arraySize0_RBV);
		return dataset;
	}

	private ImageKeyFigure imageKeyFigure;
	private CrossHairFigure rotationAxisFigure;
	private BeamScaleFigure beamScaleFigure;

	private void showImageKey(boolean showImage) {
		if (showImage) {
			Rectangle imageKeyBounds = new Rectangle(5, 5, -1, -1);
			cameraComposite.getTopFigure().add(getImageKeyFigure(), imageKeyBounds);
		} else {
			cameraComposite.getTopFigure().remove(getImageKeyFigure());

		}
	}

	/*
	 * private void showCentreMarker(boolean show, Point beamCentre) { Figure centreMarkerFigure =
	 * getCentreMarkerFigure(); if (centreMarkerFigure.getParent() == cameraComposite.getTopFigure())
	 * cameraComposite.getTopFigure().remove(centreMarkerFigure); if (show) { Rectangle bounds =
	 * centreMarkerFigure.getBounds(); Rectangle imageKeyBounds = new Rectangle(beamCentre.x - bounds.width / 2,
	 * beamCentre.y - bounds.height / 2, -1, -1); cameraComposite.getTopFigure().add(centreMarkerFigure,
	 * imageKeyBounds); } } private Figure getCentreMarkerFigure() { if (centreMarkerFigure == null) {
	 * centreMarkerFigure = new CrossHairFigure(); centreMarkerFigure.setSize(200, 100); } return centreMarkerFigure; }
	 */
	private void showRotationAxis(boolean show) throws DeviceException {
		Figure rotationAxisFigure = getRotationAxisFigure();
		if (rotationAxisFigure.getParent() == cameraComposite.getTopFigure())
			cameraComposite.getTopFigure().remove(rotationAxisFigure);
		if (show) {
			int rotationAxisX = (int) ScannableUtils.getCurrentPositionArray(cameraConfig.getRotationAxisXScannable())[0];
			Rectangle bounds = rotationAxisFigure.getBounds();
			Rectangle imageKeyBounds = new Rectangle((rotationAxisX*cameraComposite.getViewer().getImageData().width/imageWidth - bounds.width / 2), 0, -1, -1);
			cameraComposite.getTopFigure().add(rotationAxisFigure, imageKeyBounds);
		}
	}

	private Figure getRotationAxisFigure() {
		if (rotationAxisFigure == null) {
			rotationAxisFigure = new CrossHairFigure();
			rotationAxisFigure.setSize(3, imageHeight);
		}
		return rotationAxisFigure;
	}

	private BeamScaleFigure getBeamScaleFigure(boolean resetScales) throws DeviceException {
		if(beamScaleFigure ==null){
			beamScaleFigure = new BeamScaleFigure();
			beamScaleFigure.setXScale(1000/cameraConfig.getDisplayScaleProvider().getPixelsPerMMInX());
			beamScaleFigure.setYScale(1000/cameraConfig.getDisplayScaleProvider().getPixelsPerMMInY());
		}
		if(resetScales){
			beamScaleFigure.setXScale(1000/cameraConfig.getDisplayScaleProvider().getPixelsPerMMInX());
			beamScaleFigure.setYScale(1000/cameraConfig.getDisplayScaleProvider().getPixelsPerMMInY());
		}
		return beamScaleFigure;
	}

	private void showBeamScale(boolean show) throws DeviceException {
		BeamScaleFigure beamScaleFigure2 = getBeamScaleFigure(true);
		if (beamScaleFigure2.getParent() == cameraComposite.getTopFigure())
			cameraComposite.getTopFigure().remove(beamScaleFigure2);
		if (show) {
			Rectangle beamScaleBounds = new Rectangle(5, 5, -1, -1);
			cameraComposite.getTopFigure().add(beamScaleFigure2, beamScaleBounds);
		}
	}

	private ImageKeyFigure getImageKeyFigure() {
		return imageKeyFigure != null ? imageKeyFigure : (imageKeyFigure = new ImageKeyFigure());
	}

	@Override
	public void setFocus() {
	}

	private boolean layoutReset = false;

	@Override
	public void handlerNewImageNotification(ImageData newImage) {
		// On the first image, ensure we reset the display to match incoming image dimensions
		if (!layoutReset) {
			layoutReset = true;
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
