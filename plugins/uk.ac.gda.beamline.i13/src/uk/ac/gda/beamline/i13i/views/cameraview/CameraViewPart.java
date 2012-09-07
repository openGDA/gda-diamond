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
import gda.images.camera.DummySwtVideoReceiver;
import gda.images.camera.MotionJpegOverHttpReceiverSwt;
import gda.images.camera.VideoReceiver;
import gda.jython.InterfaceProvider;
import gda.observable.IObserver;

import java.lang.reflect.InvocationTargetException;

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.draw2d.Figure;
import org.eclipse.draw2d.geometry.Point;
import org.eclipse.draw2d.geometry.Rectangle;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.action.IMenuManager;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.jface.dialogs.IInputValidator;
import org.eclipse.jface.dialogs.InputDialog;
import org.eclipse.jface.dialogs.ProgressMonitorDialog;
import org.eclipse.jface.operation.IRunnableWithProgress;
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
import uk.ac.diamond.scisoft.analysis.rcp.plotting.tools.IImagePositionEvent;
import uk.ac.diamond.scisoft.analysis.rcp.plotting.tools.ImagePositionListener;
import uk.ac.gda.beamline.i13i.I13IBeamlineActivator;

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
			if (!arrayBase.isCallbacksEnabled_RBV())
				arrayBase.enableCallbacks();
			NDProcess ndProcess = cameraConfig.getNdProcess();
			if (ndProcess.getEnableOffsetScale_RBV() != 1)
				ndProcess.setEnableOffsetScale(1);
			if (ndProcess.getDataTypeOut_RBV() != NDProcess.DatatypeOut_UInt8)
				ndProcess.setDataTypeOut(NDProcess.DatatypeOut_UInt8);

			ndProcess.setEnableHighClip(1);
			ndProcess.setEnableLowClip(1);
			ndProcess.setHighClip(255);
			ndProcess.setLowClip(0);
			int imgWidth = ndProcess.getPluginBase().getArraySize0_RBV();
			int imgHeight = ndProcess.getPluginBase().getArraySize1_RBV();
			FfmpegStream ffmpegStream = cameraConfig.getFfmpegStream();
			ffmpegStream.setMAXW(imgWidth / 2);
			ffmpegStream.setMAXH(imgHeight / 2);
			ffmpegStream.setQUALITY(100.);

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
					// TODO Auto-generated method stub

				}

				@Override
				public void imageFinished(IImagePositionEvent event) {
					if (moveOnClickEnabled)
						try {
							cameraConfig.getImageViewerListener().imageFinished(event, cameraComposite.getViewer());
						} catch (DeviceException e) {
							logger.error("Error processing imageFinished", e);
						}

				}

				@Override
				public void imageDragged(IImagePositionEvent event) {
					// TODO Auto-generated method stub

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
		if (cameraConfig.getBeamCenterProvider() != null) {
			final Action centreMarkerAction = new Action("Centre Marker", IAction.AS_CHECK_BOX) {
				@Override
				public void run() {
					showCentreMarker(isChecked(), isChecked() ? cameraConfig.getBeamCenterProvider().getBeamCenter()
							: null);
				}
			};
			showCentreMarker(true, cameraConfig.getBeamCenterProvider().getBeamCenter());
			centreMarkerAction.setChecked(true);// do not
			cameraConfig.getBeamCenterProvider().addIObserver(new IObserver() {

				@Override
				public void update(Object source, final Object arg) {
					if (arg instanceof Point && centreMarkerAction.isChecked()) {
						getViewSite().getShell().getDisplay().asyncExec(new Runnable() {

							@Override
							public void run() {
								showCentreMarker(true, (Point) arg);

							}

						});
					}

				}
			});
			dropDownMenu.add(centreMarkerAction);
		}

		Action beamScaleAction = new Action("Show Beam Scale", IAction.AS_CHECK_BOX) {
			@Override
			public void run() {
				// this runs after the state has been changed
				showBeamScale(isChecked());
			}
		};
		showBeamScale(false);
		beamScaleAction.setChecked(false);// do not

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
		IToolBarManager toolBar = actionBars.getToolBarManager();
		toolBar.add(autoExposureAction);
		toolBar.add(setExposureTime);
		toolBar.add(autoBrightnessAction);
		toolBar.add(zoomFit);
		toolBar.add(showRawData);

	}

	protected void toggleMoveOnClick(boolean checked) {
		moveOnClickEnabled = checked;

	}

	protected void showRawData() throws Exception {
		AbstractDataset arrayData = getArrayData();
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
			String cmd = String.format(cameraConfig.getSetExposureTimeCmd(), dlg.getValue());
			InterfaceProvider.getCommandRunner().evaluateCommand(cmd);
		}
	}

	protected void reconnect() throws Exception {
		if (videoReceiver != null)
			videoReceiver.closeConnection();

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
		videoReceiver.start();

	}

	protected void autoBrightness(final boolean autoExposureTime) throws Exception {

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

				if( monitor.isCanceled())
					return;
				monitor.subTask("Reading image");
				AbstractDataset dataset = getArrayData();

				
				monitor.subTask("Analysis image");
				double[] m = Stats.quantile(dataset, 0.1, 0.9);

				if (Double.compare(m[1], m[0]) <= 0) {
					if (m[0] > 10000) {
						double acquireTime = cameraConfig.getAdBase().getAcquireTime_RBV();
						double desiredAcquireTime = acquireTime / 2;
						String desiredAcquireTimeS = Double.toString(desiredAcquireTime);
						String cmd = String.format(cameraConfig.getSetExposureTimeCmd(),
								desiredAcquireTimeS);
						InterfaceProvider.getCommandRunner().evaluateCommand(cmd);
						monitor.subTask("The current exposure time is too high for auto adjustment. The exposure time is being set to " + desiredAcquireTimeS);
						Thread.sleep(1000);
						autoExposureTask(autoExposureTime, monitor);

					}
					return;
				}
				double max = m[1];
				double min = m[0];
				double offset = -min;
				double scale = 255 / (max - min);

				if (autoExposureTime) {
					double factor = 10000 / max;
					double acquireTime = cameraConfig.getAdBase().getAcquireTime_RBV();
					double desiredAcquireTime = factor * acquireTime;
					String desireAcquireTimeS = Double.toString(desiredAcquireTime);
					String cmd = String.format(cameraConfig.getSetExposureTimeCmd(),
							desireAcquireTimeS);
					monitor.subTask("Setting exposure to " + desireAcquireTimeS);
					InterfaceProvider.getCommandRunner().evaluateCommand(cmd);
					Thread.sleep(1000);

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
	private CrossHairFigure centreMarkerFigure;
	private Figure beamScaleFigure;

	private void showImageKey(boolean showImage) {
		if (showImage) {
			Rectangle imageKeyBounds = new Rectangle(5, 5, -1, -1);
			cameraComposite.getTopFigure().add(getImageKeyFigure(), imageKeyBounds);
		} else {
			cameraComposite.getTopFigure().remove(getImageKeyFigure());

		}
	}

	private void showCentreMarker(boolean show, Point beamCentre) {
		Figure centreMarkerFigure = getCentreMarkerFigure();
		if (centreMarkerFigure.getParent() == cameraComposite.getTopFigure())
			cameraComposite.getTopFigure().remove(centreMarkerFigure);
		if (show) {
			Rectangle bounds = centreMarkerFigure.getBounds();
			Rectangle imageKeyBounds = new Rectangle(beamCentre.x - bounds.width / 2, beamCentre.y - bounds.height / 2,
					-1, -1);
			cameraComposite.getTopFigure().add(centreMarkerFigure, imageKeyBounds);
		}
	}

	private Figure getCentreMarkerFigure() {
		if (centreMarkerFigure == null) {
			centreMarkerFigure = new CrossHairFigure();
			centreMarkerFigure.setSize(200, 100);
		}
		return centreMarkerFigure;
	}

	private Figure getBeamScaleFigure() {
		return beamScaleFigure != null ? beamScaleFigure : (beamScaleFigure = new BeamScaleFigure());
	}

	private void showBeamScale(boolean show) {
		Figure beamScaleFigure2 = getBeamScaleFigure();
		if( beamScaleFigure2.getParent() == cameraComposite.getTopFigure())
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
