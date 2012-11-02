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
import gda.device.Scannable;
import gda.device.detector.areadetector.v17.FfmpegStream;
import gda.device.detector.areadetector.v17.NDPluginBase;
import gda.device.detector.areadetector.v17.NDProcess;
import gda.device.scannable.ScannablePositionChangeEvent;
import gda.device.scannable.ScannableStatus;
import gda.device.scannable.ScannableUtils;
import gda.factory.Finder;
import gda.images.camera.DummySwtVideoReceiver;
import gda.images.camera.MotionJpegOverHttpReceiverSwt;
import gda.images.camera.VideoReceiver;
import gda.jython.InterfaceProvider;
import gda.observable.IObserver;

import java.lang.reflect.InvocationTargetException;
import java.text.DateFormat;
import java.util.Date;
import java.util.List;
import java.util.Vector;

import org.apache.commons.math.linear.MatrixUtils;
import org.apache.commons.math.linear.RealVector;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.draw2d.ColorConstants;
import org.eclipse.draw2d.Figure;
import org.eclipse.draw2d.geometry.Rectangle;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.ActionContributionItem;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.action.IMenuCreator;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.jface.dialogs.IInputValidator;
import org.eclipse.jface.dialogs.InputDialog;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.dialogs.ProgressMonitorDialog;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.operation.IRunnableWithProgress;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.graphics.Cursor;
import org.eclipse.swt.graphics.ImageData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.MenuItem;
import org.eclipse.swt.widgets.MessageBox;
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


	public CameraViewPart() {
	}

	int imageWidth = 4008;
	int imageHeight = 2672;

	static RealVector createVectorOf(double... data) {
		return MatrixUtils.createRealVector(data);
	}

	private boolean layoutReset = false;

	private Action moveOnClickAction, rotationAxisAction, reconnectAction, showImageMarkerAction;

	private Composite cmp;

	private Button reconnectButton;

	private Menu rightClickMenu;

	private MenuCreator moveMenu, exposureMenu, showMenu;

	private MenuItem setRotationAxisX, setImageMarker;

	protected boolean changeRotationAxisX, changeImageMarker, moveOnClickEnabled;

	private Label connectedLbl;


	@Override
	public void createPartControl(Composite parent) {

		cameraConfig = I13IBeamlineActivator.getCameraConfig();

		if (cameraConfig == null) {
			Label lblCamera = new Label(parent, SWT.NONE);
			lblCamera.setText("No CameraViewPartConfig service found");
			return;
		}
		
		cmp = new Composite(parent,SWT.NONE);
		cmp.setLayout(new GridLayout());

		Composite btnCmp = new Composite(cmp, SWT.NONE);
		RowLayout layout = new RowLayout();
		btnCmp.setLayout(layout);
		GridDataFactory.fillDefaults().grab(true,false).applyTo(btnCmp);

		Group statusGroup = new Group(btnCmp,SWT.NONE);
		statusGroup.setText("IOC Status");
		statusGroup.setLayout( new RowLayout());
		
		
		reconnectButton = new Button(statusGroup, SWT.PUSH);
		reconnectButton.setText("Camera not found. Press to try again.");
		reconnectButton.setForeground(Display.getCurrent().getSystemColor(SWT.COLOR_RED));
		//use grabHoriz to get the composite to ask its children for their size
//		GridDataFactory.fillDefaults().grab(false,false).applyTo(reconnectButton);
		reconnectButton.addSelectionListener(new SelectionListener() {
			
			@Override
			public void widgetSelected(SelectionEvent e) {
				reconnectIOC();
			}
			
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});
		reconnectButton.setVisible(true);

		connectedLbl = new Label(statusGroup,SWT.NONE);
		connectedLbl.setText("IOC Connected");
		connectedLbl.setForeground(Display.getDefault().getSystemColor(SWT.COLOR_DARK_GREEN));
	//	GridDataFactory.fillDefaults().grab(false,false).applyTo(connectedLbl);
		connectedLbl.setVisible(false);
		
		Group latestImageGroup = new Group(btnCmp,SWT.NONE);
		latestImageGroup.setText("Time of last image");
		latestImageGroup.setLayout( new RowLayout());
		imageDateLabel = new Label(latestImageGroup,SWT.NONE);
		imageDateLabel.setText("Waiting for image...");

		Group group = new Group(btnCmp,SWT.NONE);
		group.setText("Lens");
		group.setLayout( new RowLayout());
		pcom = new Combo(group, SWT.SINGLE|SWT.BORDER|SWT.CENTER|SWT.READ_ONLY);
		pcom.setItems(new String[]{"X2 7.4mm * 4.9mm", "X4 3.7mm * 2.5mm", "X10 1.5mm * 1.0mm", "Unknown"});
	//	GridDataFactory.fillDefaults().grab(false,false).applyTo(pcom);
		
		pcom.addSelectionListener(new SelectionAdapter() {
		      @Override
			public void widgetSelected(SelectionEvent e) {
		    	  valueChanged((Combo)e.widget);
		        }
		      });		
		
		pcom.setVisible(true);
//		group.pack();
		lensScannable = Finder.getInstance().find("lensScannable");
		lensScannable.addIObserver(new IObserver(){

			@Override
			public void update(Object source, Object arg) {
				try {
					final double pos = ScannableUtils.getCurrentPositionArray(lensScannable)[0];
					Display.getDefault().asyncExec(new Runnable() {

						@Override
						public void run() {
							pcom.select((int) pos);
						}});
					
				} catch (DeviceException e) {
					logger.error("Error getting position of "+lensScannable.getName(), e);
				}
				
			}});
		
		int npi=0;
		try {
			npi  = (int) ScannableUtils.getCurrentPositionArray(lensScannable)[0];
			pcom.select(npi);
		} catch (DeviceException e1) {
			pcom.select(3);
			logger.error("Error setting value for " + lensScannable.getName() + " to " +npi, e1);
		}
		
		cameraComposite = new CameraComposite(cmp, SWT.NONE, parent.getDisplay(), this);
		GridDataFactory.fillDefaults().grab(true, true).applyTo(cameraComposite);
		cameraComposite.setVisible(false);

		cameraComposite.getViewer().getPositionTool().addImagePositionListener(new ImagePositionListener() {

			@Override
			public void imageStart(IImagePositionEvent event) {
			}

			@Override
			public void imageFinished(IImagePositionEvent event) {
				if (changeRotationAxisX) {
					int beamCentreX = event.getImagePosition()[0];
					int beamCentreY = event.getImagePosition()[1];
					boolean changeCentre = MessageDialog.openQuestion(
							PlatformUI.getWorkbench().getDisplay().getActiveShell(),
							"Change Beam Centre",
							"Are you sure you wish to change the rotation axis to this position ("
									+ Integer.toString(beamCentreX) + "," + Integer.toString(beamCentreY) + "?");
					if (changeCentre) {
						try {
							final int[] clickCoordinates = event.getImagePosition();
							final RealVector actualClickPoint = createVectorOf(clickCoordinates[0], clickCoordinates[1]);
							ImageData imageData = cameraComposite.getViewer().getImageData();
							final RealVector imageDataSize = createVectorOf(imageData.width, imageData.height);
							final RealVector imageSize = createVectorOf(imageWidth, imageHeight);

							final RealVector clickPointInImage = actualClickPoint.ebeMultiply(imageSize).ebeDivide(
									imageDataSize);

							cameraConfig.getRotationAxisXScannable().asynchronousMoveTo(clickPointInImage.getEntry(0));
						} catch (DeviceException e) {
							reportErrorToUserAndLog("Error setting rotationAxis", e);
						}
					}
					changeRotationAxisX = false;
					final Cursor cursorWait = new Cursor(Display.getCurrent(), SWT.CURSOR_ARROW);
					Display.getDefault().getActiveShell().setCursor(cursorWait);
				} else if (changeImageMarker) {
					int beamCentreX = event.getImagePosition()[0];
					int beamCentreY = event.getImagePosition()[1];
					boolean changeCentre = MessageDialog.openQuestion(
							PlatformUI.getWorkbench().getDisplay().getActiveShell(),
							"Change beam centre marker",
							"Are you sure you wish to change the beam centre marker to this position ("
									+ Integer.toString(beamCentreX) + "," + Integer.toString(beamCentreY) + "?");
					if (changeCentre) {
						try {
							final int[] clickCoordinates = event.getImagePosition();
							final RealVector actualClickPoint = createVectorOf(clickCoordinates[0], clickCoordinates[1]);
							ImageData imageData = cameraComposite.getViewer().getImageData();
							final RealVector imageDataSize = createVectorOf(imageData.width, imageData.height);
							final RealVector imageSize = createVectorOf(imageWidth, imageHeight);

							final RealVector clickPointInImage = actualClickPoint.ebeMultiply(imageSize).ebeDivide(
									imageDataSize);

							cameraConfig.getCameraXYScannable().asynchronousMoveTo(
									new double[] { clickPointInImage.getEntry(0), clickPointInImage.getEntry(1) });
						} catch (DeviceException e) {
							reportErrorToUserAndLog("Error setting beam centre marker", e);
						}
					}
					changeImageMarker = false;
					final Cursor cursorWait = new Cursor(Display.getCurrent(), SWT.CURSOR_ARROW);
					Display.getDefault().getActiveShell().setCursor(cursorWait);
				} else if (moveOnClickEnabled) {
					try {
						cameraConfig.getImageViewerListener().imageFinished(event, cameraComposite.getViewer());
					} catch (DeviceException e) {
						reportErrorToUserAndLog("Error processing imageFinished", e);
					}
				}

			}

			@Override
			public void imageDragged(IImagePositionEvent event) {
			}
		}, null);

		

		final Action setExposureTime = new Action("Start Camera or Change Exposure Time") {
			@Override
			public void run() {
				try {
					setExposureTime();
				} catch (Exception e) {
					reportErrorToUserAndLog("Error setting exposure time", e);
				}
			}
		};

		Action zoomFit = new Action("Zoom to Fit") {
			@Override
			public void run() {
				zoomToFit();
			}
		};
		Action showRawData = new Action("Show Hi Res Image") {
			@Override
			public void run() {
				try {
					showRawData();
				} catch (Exception e) {
					reportErrorToUserAndLog("Error showing raw data", e);
				}
			}
		};
		showRawData.setToolTipText("Displays hi resolution image in 'Detector Image' window");
		
		reconnectAction = new Action("Reconnect to Image Stream") {
			@Override
			public void run() {
				try {
					reconnectStream();
				} catch (Exception e) {
					reportErrorToUserAndLog("Error re-connecting to stream", e);
				}
			}

		};

		Action autoExposureAction = new Action("Auto-Exposure") {
			@Override
			public void run() {
				try {
					autoBrightness(true);
				} catch (Exception e) {
					reportErrorToUserAndLog("Error performing auto-exposure", e);
				}
			}
		};

		Action autoCentreAction = new Action("Align camera and rotation axis on beam center") {
			@Override
			public void run() {
				try {
					autoCentre();
				} catch (Exception e) {
					reportErrorToUserAndLog("Error performing auto-centre", e);
				}
			}
		};

		Action readyForLoadAction = new Action("Move to sample load position") {
			@Override
			public void run() {
				try {
					autoCentre();
				} catch (Exception e) {
					reportErrorToUserAndLog("Error performing auto-centre", e);
				}
			}
		};

		Action autoBrightnessAction = new Action("Auto-Contrast") {
			@Override
			public void run() {
				try {
					autoBrightness(false);
				} catch (Exception e) {
					reportErrorToUserAndLog("Error performing auto-constrast", e);
				}
			}
		};

		Action showNormalisedImageAction = new Action("Show Normalied Image") {
			@Override
			public void run() {
				try {
					showNormalisedImage();
				} catch (Exception e) {
					reportErrorToUserAndLog("Error performing showNormalisedImage", e);
				}
			}
		};

		
		
		rotationAxisAction = new Action("Show rotation axis", IAction.AS_CHECK_BOX) {
			@Override
			public void run() {
				try {
					showRotationAxis(isChecked());
				} catch (DeviceException e) {
					reportErrorToUserAndLog("Error showing rotation axis", e);
				}
			}
		};
		try {
			showRotationAxis(true);
			rotationAxisAction.setChecked(true);// do not
		} catch (DeviceException e) {
			reportErrorToUserAndLog("Error showing rotation axis", e);
		}
		cameraConfig.getRotationAxisXScannable().addIObserver(new IObserver() {

			@Override
			public void update(Object source, final Object arg) {
				if (rotationAxisAction.isChecked()) {
					if ((arg instanceof ScannableStatus && (((ScannableStatus) arg).status == ScannableStatus.IDLE))
							|| (arg instanceof ScannablePositionChangeEvent)) {
						showRotationAxisFromNonUIThread(rotationAxisAction);
					}
				}
			}

		});

		showImageMarkerAction = new Action("Show beam centre", IAction.AS_CHECK_BOX) {
			@Override
			public void run() {
				try {
					showImageMarker(isChecked());
				} catch (DeviceException e) {
					reportErrorToUserAndLog("Error showing beam centre", e);
				}
			}
		};
		try {
			showImageMarker(true);
			showImageMarkerAction.setChecked(true);// do not
		} catch (DeviceException e) {
			reportErrorToUserAndLog("Error showing beam centre", e);
		}
		cameraConfig.getCameraXYScannable().addIObserver(new IObserver() {

			@Override
			public void update(Object source, final Object arg) {
				if ((arg instanceof ScannableStatus && (((ScannableStatus) arg).status == ScannableStatus.IDLE))
						|| (arg instanceof ScannablePositionChangeEvent)) {
					showImageMarkerFromNonUIThread(showImageMarkerAction);
				}
			}

		});

		final Action beamScaleAction = new Action("Show scale", IAction.AS_CHECK_BOX) {
			@Override
			public void run() {
				// this runs after the state has been changed
				try {
					showBeamScale(isChecked());
				} catch (DeviceException e) {
					reportErrorToUserAndLog("Error showing scale", e);
				}
			}
		};
		beamScaleAction.setChecked(false);// do not
		try {
			showBeamScale(beamScaleAction.isChecked());
		} catch (DeviceException e) {
			reportErrorToUserAndLog("Error showing beamscale", e);
		}


		moveOnClickAction = new Action("Move Sample On Click", IAction.AS_CHECK_BOX) {
			@Override
			public void run() {
				// this runs after the state has been changed
				toggleMoveOnClick(isChecked());
			}
		};
		moveOnClickAction.setChecked(false);// do not


		Vector<Action> moveActions= new Vector<Action>();
		moveActions.add(autoCentreAction);
		moveActions.add(moveOnClickAction);
		
		moveMenu = new MenuCreator("Alignment","Actions that move the camera and sample stages",moveActions);

		
		Vector<Action> exposureActions= new Vector<Action>();
		exposureActions.add(reconnectAction);
		exposureActions.add(setExposureTime);
		exposureActions.add(autoExposureAction);
		exposureActions.add(autoBrightnessAction);
		
		exposureMenu = new MenuCreator("Camera","Actions that effect the camera",exposureActions);
		
		Vector<Action> showActions= new Vector<Action>();
//do not add as this scale is wrong		showActions.add(beamScaleAction);
		showActions.add(showImageMarkerAction);
		showActions.add(rotationAxisAction);
		showActions.add(showRawData);
		showActions.add(showNormalisedImageAction);
		showActions.add(zoomFit);
		
		showMenu = new MenuCreator("Show","Actions that lead to items shown on the image or in other views",showActions);

		IActionBars actionBars = getViewSite().getActionBars();
        IToolBarManager toolBar = actionBars.getToolBarManager();
        toolBar.add(moveMenu);
        toolBar.add(exposureMenu);
        toolBar.add(showMenu);
		
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

		setImageMarker = new MenuItem(rightClickMenu, SWT.PUSH);
		setImageMarker.setText("Mark next click position as beam centre");
		setImageMarker.addSelectionListener(new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent event) {
				final Cursor cursorWait = new Cursor(Display.getDefault(), SWT.CURSOR_HAND);
				Display.getDefault().getActiveShell().setCursor(cursorWait);
				changeImageMarker = true;
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent event) {
				final Cursor cursorWait = new Cursor(Display.getCurrent(), SWT.CURSOR_HAND);
				Display.getDefault().getActiveShell().setCursor(cursorWait);
				changeImageMarker = true;
			}
		});

		viewer.getCanvas().setMenu(rightClickMenu);

		cameraConfig.getDisplayScaleProvider().addIObserver(new IObserver() {

			@Override
			public void update(Object source, Object arg) {
				showImageMarkerFromNonUIThread(showImageMarkerAction);
				showRotationAxisFromNonUIThread(rotationAxisAction);
				Display.getDefault().asyncExec(new Runnable() {
					@Override
					public void run() {
						try {
							if (beamScaleAction.isChecked())
								showBeamScale(true);
						} catch (DeviceException e) {
							logger.error("Error showing beamscale", e);
						}
					}
				});
			}
		});
		getSite().getShell().getDisplay().asyncExec(new Runnable(){

			@Override
			public void run() {
				reconnectIOC();
				try {
					autoBrightness(false);
				} catch (Exception e) {
					logger.error("Error setting brightness", e);
				}
			}});
	}

	public void valueChanged(Combo c) {
		int npi=c.getSelectionIndex();
		try {
			lensScannable.asynchronousMoveTo( npi );
		} catch (DeviceException e) {
			logger.error("Error setting value for " + lensScannable.getName() + " to " +npi, e);
		}
	    
	  }
	public static void reportErrorToUserAndLog(String s, Throwable th){
		logger.error(s, th);
		MessageBox messageBox = new MessageBox(PlatformUI.getWorkbench().getActiveWorkbenchWindow().getShell(), SWT.ICON_ERROR);
		messageBox.setMessage(s + ":" + th.getMessage());
		messageBox.open();
		
	}
	public static void reportErrorToUserAndLog(String s){
		logger.error(s);
		MessageBox messageBox = new MessageBox(PlatformUI.getWorkbench().getActiveWorkbenchWindow().getShell(), SWT.ICON_ERROR);
		messageBox.setMessage(s );
		messageBox.open();
		
	}

	protected void toggleMoveOnClick(boolean checked) {
		moveOnClickEnabled = checked;
	}

	
	private void showRotationAxisFromNonUIThread(final Action rotationAxisAction) {
		if (rotationAxisAction.isChecked()) {

			getViewSite().getShell().getDisplay().asyncExec(new Runnable() {

				@Override
				public void run() {
					try {
						showRotationAxis(true);
					} catch (DeviceException e) {
						reportErrorToUserAndLog("Error showing rotation axis", e);
					}

				}
			});
		}
	}
	private void showImageMarkerFromNonUIThread(final Action showImageMarkerAction) {
		if (showImageMarkerAction.isChecked()) {
			getViewSite().getShell().getDisplay().asyncExec(new Runnable() {

				@Override
				public void run() {
					try {
						showImageMarker(true);
					} catch (DeviceException e) {
						reportErrorToUserAndLog("Error showing beam centre", e);
					}

				}
			});
		}
	}

	private void showRotationAxisFromUIThread(final Action rotationAxisAction) throws DeviceException {
		if (rotationAxisAction.isChecked()) {
			showRotationAxis(true);
		}
	}
	private void showImageMarkerFromUIThread(final Action showImageMarkerAction) throws DeviceException {
		if (showImageMarkerAction.isChecked()) {
			showImageMarker(true);
		}
	}

	protected void showRawData() throws Exception {
		
		ProgressMonitorDialog pd = new ProgressMonitorDialog(getSite().getShell());
		try {
			pd.run(true /* fork */, true /* cancelable */, new IRunnableWithProgress() {
				@Override
				public void run(IProgressMonitor monitor) throws InvocationTargetException, InterruptedException {
					String title = "Reading image to display in 'Detector Image' view";

					monitor.beginTask(title, 100);

					
					try {
						AbstractDataset arrayData = getArrayData(monitor);
						if (arrayData != null)
							SDAPlotter.imagePlot("Detector Image", arrayData);
						
					} catch (Exception e) {
						throw new InvocationTargetException(e, "Error in " + title);
					}

					monitor.done();
				}

			});
		} catch (Exception e) {
			reportErrorToUserAndLog("Error showing data");
		}
		
		
		
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
					String title = "Setting exposure time to " + value;

					monitor.beginTask(title, 100);

					try {
						String evaluateCommand = InterfaceProvider.getCommandRunner().evaluateCommand(cmd);
						if(evaluateCommand ==null){
							throw new Exception("Error setting exposure using command:'" + cmd +"'. See server log for details");
						}
						autoExposureTask(false, 0., monitor);
					} catch (Exception e) {
						throw new InvocationTargetException(e, "Error in " + title);
					}

					monitor.done();
				}

			});
		}
	}

	protected void reconnectIOC() {

		ProgressMonitorDialog pd = new ProgressMonitorDialog(getSite().getShell());
		try {
			pd.run(true /* fork */, true /* cancelable */, new IRunnableWithProgress() {
				@Override
				public void run(IProgressMonitor monitor) throws InvocationTargetException, InterruptedException {
					String title = "Connecting to detector IOC";

					monitor.beginTask(title, 100);

					
					try {
						reconnectEx(true, monitor);
						
					} catch (Exception e) {
						throw new InvocationTargetException(e, "Error in " + title);
					}

					monitor.done();
				}

			});
		} catch (Exception e) {
			reportErrorToUserAndLog("Error connected to the camera. Ensure IOC is running");
		}
		boolean connected= videoReceiver != null;
		reconnectButton.setVisible(!connected);
		connectedLbl.setVisible(connected);
		cameraComposite.setVisible(connected);
		moveMenu.setEnabled(connected);
		showMenu.setEnabled(connected);
		exposureMenu.setEnabled(connected);
		cmp.layout();
	}

	protected void reconnectStream() {

		ProgressMonitorDialog pd = new ProgressMonitorDialog(getSite().getShell());
		try {
			pd.run(true /* fork */, true /* cancelable */, new IRunnableWithProgress() {
				@Override
				public void run(IProgressMonitor monitor) throws InvocationTargetException, InterruptedException {
					String title = "Connecting to image stream";

					monitor.beginTask(title, 100);

					
					try {
						reconnectEx(false, monitor);
						
					} catch (Exception e) {
						throw new InvocationTargetException(e, "Error in " + title);
					}

					monitor.done();
				}

			});
		} catch (Exception e) {
			reportErrorToUserAndLog("Error connected to the camera. Ensure IOC is running");
		}
	
	}
	
	
	protected void reconnectEx(boolean resetPVFields, IProgressMonitor monitor) throws Exception {

		monitor.beginTask("Reconnecting to IOC and image stream", 100);
		if (videoReceiver != null) {
			videoReceiver.closeConnection();
			videoReceiver = null;
			cameraComposite.setVideoReceiver(null);
		}
		FfmpegStream ffmpegStream = cameraConfig.getFfmpegStream();

		if( resetPVFields){
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

			ffmpegStream.setMAXW(cameraConfig.getfFMpegImgWidthRequired());
			ffmpegStream.setMAXH(cameraConfig.getfFMpegImgHeightRequired());
			ffmpegStream.setQUALITY(100.);
			NDPluginBase ffmpegBase = ffmpegStream.getPluginBase();
			String procPortName_RBV = procBase.getPortName_RBV();
			if (!ffmpegBase.getNDArrayPort_RBV().equals(procPortName_RBV))
				ffmpegBase.setNDArrayPort(procPortName_RBV);
			if (!ffmpegBase.isCallbacksEnabled_RBV())
				ffmpegBase.enableCallbacks();

			NDPluginBase arrayBase = cameraConfig.getNdArray().getPluginBase();
			String procNdArrayPort_RBV = procBase.getNDArrayPort_RBV();
			if (!arrayBase.getNDArrayPort_RBV().equals(procNdArrayPort_RBV))
				arrayBase.setNDArrayPort(procNdArrayPort_RBV);
			if (!arrayBase.isCallbacksEnabled_RBV())
				arrayBase.enableCallbacks();		
			
		}
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
		cameraComposite.setVideoReceiver(videoReceiver);
		videoReceiver.start();

	}

	protected void autoBrightness(final boolean autoExposureTime) throws Exception {
		double topQuantileVal = 20000;
		if (autoExposureTime) {
			InputDialog dlg = new InputDialog(Display.getCurrent().getActiveShell(), "Auto-exposure",
					"Enter a desired value for 90% quantile:", Double.toString(topQuantileVal), new IInputValidator() {

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
		IRunnableWithProgress runnable1 = new IRunnableWithProgress() {
			@Override
			public void run(IProgressMonitor monitor) throws InvocationTargetException, InterruptedException {
				String title = autoExposureTime ? "Adjusting exposure" : "Adjusting constrast";

				monitor.beginTask(title, 100);

				try {
					autoExposureTask(autoExposureTime, topQuantileValToUse, monitor);
				} catch (Exception e) {
					throw new InvocationTargetException(e, "Error in autoExposureTask");
				}
				monitor.done();
			}

		};
		try{
			pd.run(true /* fork */, true /* cancelable */, runnable1);
		} catch(Exception e){
			reportErrorToUserAndLog("Error in adjusting exposure or contrast", e);
		}

	}

	private void autoExposureTask(final boolean autoExposureTime, double topQuantileValToUse, IProgressMonitor monitor) throws Exception  {

		if (monitor.isCanceled())
			return;
		double acquireTime = cameraConfig.getAdBase().getAcquireTime_RBV();
		monitor.subTask("Reading image");
		AbstractDataset dataset = getArrayData(monitor);
		monitor.subTask("Analysing image");

		if (dataset == null) {
			if( !autoExposureTime)
				throw new Exception("Unable to read array data for image");
			double expoTime = 0.1;
			String desiredAcquireTimeS = Double.toString(expoTime);
			String cmd = String.format(cameraConfig.getSetExposureTimeCmd(), desiredAcquireTimeS);
			InterfaceProvider.getCommandRunner().evaluateCommand(cmd);
			monitor.subTask("The current image is empty. The exposure time is being set to "
					+ desiredAcquireTimeS);
			autoExposureTask(autoExposureTime, topQuantileValToUse, monitor);
			return;
		}
		double[] m = Stats.quantile(dataset, 0.1, 0.9);

		if (Double.compare(m[1], m[0]) <= 0) {
			throw new Exception("The current exposure time is too high for auto adjustment.");
		}
		double max = m[1];
		double min = m[0];
		double offset = -min;
		double scale = 255 / (max - min);
		boolean autoBrightnessOnceAgain=false;
		if (autoExposureTime) {
			double factor = topQuantileValToUse / max;
			;
			double desiredAcquireTime = factor * acquireTime;
			if( desiredAcquireTime > 5){
				autoBrightnessOnceAgain = true;
				desiredAcquireTime=5.;
			}
			factor = desiredAcquireTime / acquireTime;
			String desireAcquireTimeS = Double.toString(desiredAcquireTime);
			String cmd = String.format(cameraConfig.getSetExposureTimeCmd(), desireAcquireTimeS);
			monitor.subTask("Setting exposure to " + desireAcquireTimeS);
			InterfaceProvider.getCommandRunner().evaluateCommand(cmd);
			Thread.sleep((long) (2 * 1000 * desiredAcquireTime));

			offset = offset * factor;
			scale = scale / factor;
		}
		if( autoBrightnessOnceAgain){
			autoExposureTask(false, topQuantileValToUse, monitor);
		} else {
			monitor.subTask("Setting up ffmjeg proc plugin for best constrast");
			cameraConfig.getNdProcess().setScale(scale);
			cameraConfig.getNdProcess().setOffset(offset);
		}
		reconnectEx(false, monitor);

	}
	
	
	protected void autoCentre() throws Exception {

		MessageBox box = new MessageBox(getSite().getShell());
		box.setMessage("Are you sure?. " +
				"The camera and base will be moved so that the beam center and rotation axis will be in the middle of the image");
		int response = box.open();
		if(response == SWT.OK){
			ProgressMonitorDialog pd = new ProgressMonitorDialog(getSite().getShell());
			pd.run(true /* fork */, true /* cancelable */, new IRunnableWithProgress() {
				@Override
				public void run(IProgressMonitor monitor) throws InvocationTargetException, InterruptedException {
					String title = "Auto-centring. Running command '" + cameraConfig.getAutoCentreCmd() + "'";

					monitor.beginTask(title, 100);

					try {
						InterfaceProvider.getCommandRunner().evaluateCommand(cameraConfig.getAutoCentreCmd());
					} catch (Exception e) {
						throw new InvocationTargetException(e, "Error in " + title);
					}

					monitor.done();
				}
			});
		}
	}

	protected void showNormalisedImage() throws Exception {

		InputDialog dlg = new InputDialog(Display.getCurrent().getActiveShell(), "Show Normalised Image",
				"Enter the out of beam position", Double.toString(0.),
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
		final String value = dlg.getValue();
		final String cmd = String.format(cameraConfig.getShowNormalisedImageCmd() , value);
		
		ProgressMonitorDialog pd = new ProgressMonitorDialog(getSite().getShell());
		pd.run(true /* fork */, true /* cancelable */, new IRunnableWithProgress() {
			@Override
			public void run(IProgressMonitor monitor) throws InvocationTargetException, InterruptedException {
				String title = "Running command '" + cmd+ "'";

				monitor.beginTask(title, 100);

				try {
					String result = InterfaceProvider.getCommandRunner().evaluateCommand(cmd);
					if( result == null)
						throw new Exception("Error executing command '" + cmd + "'");
				} catch (Exception e) {
					throw new InvocationTargetException(e, "Error in " + title);
				}

				monitor.done();
			}
		});

	}
	
	private AbstractDataset getArrayData(IProgressMonitor monitor) throws Exception  {
		/*
		 * get data and send to histogram code
		 */
		//if not enabled enable and wait and monitor frame
		NDPluginBase arrayBase = cameraConfig.getNdArray().getPluginBase();
		boolean arraysEnabled = arrayBase.isCallbacksEnabled_RBV();
		if (!arraysEnabled){
			monitor.beginTask("enable array callback and waiting for the array to contain an image",100);
			arrayBase.enableCallbacks();	
			double acquireTime = cameraConfig.getAdBase().getAcquireTime_RBV();
			Thread.sleep((long) (acquireTime*2*1000));//ensure a frame is taken
		}
		
		int arraySize0_RBV = cameraConfig.getNdArray().getPluginBase().getArraySize0_RBV();
		int arraySize1_RBV = cameraConfig.getNdArray().getPluginBase().getArraySize1_RBV();
		int expectedNumPixels = arraySize0_RBV * arraySize1_RBV;
		if (expectedNumPixels == 0)
			return null;
		// as only 14 bits we can just use shorts
		short[] shortArrayData = cameraConfig.getNdArray().getShortArrayData(expectedNumPixels);

		if(!arraysEnabled)
			arrayBase.disableCallbacks();		
		int cd[] = new int[expectedNumPixels];
		for (int i = 0; i < expectedNumPixels; i++) {
			cd[i] = (shortArrayData[i] & 0xffff);
		}

		AbstractDataset dataset = new IntegerDataset(cd, arraySize1_RBV, arraySize0_RBV);
		return dataset;
	}

	private CrossHairFigure rotationAxisFigure, imageMarkerFigure;
	private BeamScaleFigure beamScaleFigure;

	private Scannable lensScannable;

	private Combo pcom;

	Label imageDateLabel;

	DateFormat df = DateFormat.getDateTimeInstance(DateFormat.SHORT, DateFormat.LONG);


	private void showRotationAxis(boolean show) throws DeviceException {
		Figure rotationAxisFigure = getRotationAxisFigure();
		if (rotationAxisFigure.getParent() == cameraComposite.getTopFigure())
			cameraComposite.getTopFigure().remove(rotationAxisFigure);
		if (show) {
			int rotationAxisX = (int) ScannableUtils.getCurrentPositionArray(cameraConfig.getRotationAxisXScannable())[0];
			Rectangle bounds = rotationAxisFigure.getBounds();
			Rectangle imageKeyBounds = new Rectangle((rotationAxisX * cameraComposite.getViewer().getImageData().width
					/ imageWidth - bounds.width / 2), 0, -1, -1);
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

	private void showImageMarker(boolean show) throws DeviceException {
		Figure imageMarkerFigure = getImageMarkerFigure();
		if (imageMarkerFigure.getParent() == cameraComposite.getTopFigure())
			cameraComposite.getTopFigure().remove(imageMarkerFigure);
		if (show) {
			double[] pos = ScannableUtils.getCurrentPositionArray(cameraConfig.getCameraXYScannable());
			int rotationAxisX = (int) pos[0];
			int rotationAxisY = (int) pos[1];
			Rectangle bounds = imageMarkerFigure.getBounds();
			Rectangle imageKeyBounds = new Rectangle((rotationAxisX * cameraComposite.getViewer().getImageData().width
					/ imageWidth - bounds.width / 2), (rotationAxisY
					* cameraComposite.getViewer().getImageData().height / imageHeight - bounds.height / 2), -1, -1);
			cameraComposite.getTopFigure().add(imageMarkerFigure, imageKeyBounds);
		}
	}

	private Figure getImageMarkerFigure() {
		if (imageMarkerFigure == null) {
			imageMarkerFigure = new CrossHairFigure();
			imageMarkerFigure.setSize(100, 100);
			imageMarkerFigure.setColor(ColorConstants.blue);
		}
		return imageMarkerFigure;
	}

	private BeamScaleFigure getBeamScaleFigure(boolean resetScales) throws DeviceException {
		if (beamScaleFigure == null) {
			beamScaleFigure = new BeamScaleFigure();
			ImageData imageData = cameraComposite.getViewer().getImageData();
			int width = imageData.width / 10;
			beamScaleFigure.setBeamSize(width, width);
			beamScaleFigure.setXScale(1000 / cameraConfig.getDisplayScaleProvider().getPixelsPerMMInX());
			beamScaleFigure.setYScale(1000 / cameraConfig.getDisplayScaleProvider().getPixelsPerMMInY());
		}
		if (resetScales) {
			ImageData imageData = cameraComposite.getViewer().getImageData();
			int width = imageData.width / 10;
			beamScaleFigure.setBeamSize(width, width);
			beamScaleFigure.setXScale(1000 / cameraConfig.getDisplayScaleProvider().getPixelsPerMMInX());
			beamScaleFigure.setYScale(1000 / cameraConfig.getDisplayScaleProvider().getPixelsPerMMInY());
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


	@Override
	public void setFocus() {
	}

	
	protected Action getReconnectAction(){
		return reconnectAction;
	}

	@Override
	public void handlerNewImageNotification(ImageData newImage) throws DeviceException {
		// On the first image, ensure we reset the display to match incoming image dimensions
		if (!layoutReset) {
			layoutReset = true;
			showRotationAxisFromUIThread(rotationAxisAction);
			showImageMarkerFromUIThread(showImageMarkerAction);
		}
		imageDateLabel.setText(df.format(new Date()));
/*		getViewSite().getShell().getDisplay().asyncExec(new Runnable() {

			@Override
			public void run() {
				imageDateLabel.setText(df.format(new Date()));
				
			}});
*/	}

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
class MenuCreator extends Action implements IMenuCreator {

    private Menu fMenu;
	private List<Action> actions;

    public MenuCreator(String title, String tooltip, List<Action> actions) {
    	this.actions = actions;
		fMenu = null;
        setText(title);
        setToolTipText(tooltip);
        setMenuCreator(this);
        setEnabled(true);
    }

    @Override
	public Menu getMenu(Menu parent) {
        return null;
    }

    @Override
	public Menu getMenu(Control parent) {
        if (fMenu != null) {
            fMenu.dispose();
        }
        fMenu= new Menu(parent);
        for( Action act : actions){
    		addActionToMenu(fMenu, act);
        }
        return fMenu;
    }

    @Override
	public void dispose() {
    	actions = null;
        if (fMenu != null) {
            fMenu.dispose();
            fMenu = null;
        }
    }

    protected void addActionToMenu(Menu parent, Action action) {
        ActionContributionItem item = new ActionContributionItem(action);
        item.fill(parent, -1);
    }

    @Override
	public void run() {
    }
}
