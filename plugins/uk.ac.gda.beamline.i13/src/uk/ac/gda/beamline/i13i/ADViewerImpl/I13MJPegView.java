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

package uk.ac.gda.beamline.i13i.ADViewerImpl;

import gda.device.DeviceException;
import gda.device.ScannableMotionUnits;
import gda.device.scannable.ScannablePositionChangeEvent;
import gda.device.scannable.ScannableStatus;
import gda.device.scannable.ScannableUtils;
import gda.jython.InterfaceProvider;
import gda.observable.IObserver;

import java.lang.reflect.InvocationTargetException;
import java.util.Vector;

import org.apache.commons.math.linear.MatrixUtils;
import org.apache.commons.math.linear.RealVector;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.draw2d.ColorConstants;
import org.eclipse.draw2d.Figure;
import org.eclipse.draw2d.geometry.Rectangle;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IAction;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.jface.dialogs.IInputValidator;
import org.eclipse.jface.dialogs.InputDialog;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.dialogs.ProgressMonitorDialog;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.operation.IRunnableWithProgress;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.graphics.Cursor;
import org.eclipse.swt.graphics.ImageData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.MenuItem;
import org.eclipse.ui.IActionBars;
import org.eclipse.ui.PlatformUI;

import uk.ac.gda.beamline.i13i.DisplayScaleProvider;
import uk.ac.gda.beamline.i13i.views.cameraview.CrossHairFigure;
import uk.ac.gda.epics.adviewer.composites.imageviewer.IImagePositionEvent;
import uk.ac.gda.epics.adviewer.composites.imageviewer.ImagePositionListener;
import uk.ac.gda.epics.adviewer.views.MJPegView;

public class I13MJPegView extends MJPegView {

	I13ADControllerImpl adControllerImpl = null;
	boolean changeRotationAxisX, changeImageMarker, moveOnClickEnabled;
	private CrossHairFigure rotationAxisFigure;
	private CrossHairFigure imageMarkerFigure;

	public I13MJPegView(I13ADControllerImpl config) {
		super(config);
		adControllerImpl = config;
	}

	@Override
	public void createPartControl(Composite parent) {
		super.createPartControl(parent);
		
		addSpecialisation();
	}

	@Override
	protected void createTopRowControls(Composite composite_1) {
		Composite c = new Composite(composite_1, SWT.NONE);
		c.setLayout(new GridLayout(2, false));
		LensScannableComposite lensScannableComposite = new LensScannableComposite(c, SWT.NONE);
		lensScannableComposite.setLensScannable(adControllerImpl.getLensScannable());
		GridDataFactory.swtDefaults().applyTo(lensScannableComposite);
		adControllerImpl.getCompositeFactory().createComposite(c, SWT.NONE, null);

	}

	@Override
	protected void hookGlobalActions() {
	}

	@Override
	protected void createContextMenu() {

		
	}

	@Override
	protected void createToolbar() {
	}

	@Override
	protected void createMenu() {
	}

	@Override
	protected void createActions() {
	}	
	
	static RealVector createVectorOf(double... data) {
		return MatrixUtils.createRealVector(data);
	}
	
	private void addSpecialisation() {
		mJPeg.getTopFigure().add(new CrossHairFigure());

		Menu rightClickMenu = new Menu(mJPeg.getCanvas());
		MenuItem setRotationAxisX = new MenuItem(rightClickMenu, SWT.PUSH);
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
				widgetSelected(event);
			}
		});
		
		MenuItem setImageMarker = new MenuItem(rightClickMenu, SWT.PUSH);
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

		

		mJPeg.getCanvas().setMenu(rightClickMenu);

		mJPeg.addImagePositionListener(new ImagePositionListener() {

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
							ImageData imageData = mJPeg.getImageData();
							final RealVector imageDataSize = createVectorOf(imageData.width, imageData.height);
							final RealVector imageSize = createVectorOf(adControllerImpl.getImageWidth(), adControllerImpl.getImageHeight());

							final RealVector clickPointInImage = actualClickPoint.ebeMultiply(imageSize).ebeDivide(
									imageDataSize);

							adControllerImpl.getRotationAxisXScannable().asynchronousMoveTo(clickPointInImage.getEntry(0));
						} catch (Exception e) {
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
							ImageData imageData = mJPeg.getImageData();
							final RealVector imageDataSize = createVectorOf(imageData.width, imageData.height);
							final RealVector imageSize = createVectorOf(adControllerImpl.getImageWidth(), adControllerImpl.getImageHeight());

							final RealVector clickPointInImage = actualClickPoint.ebeMultiply(imageSize).ebeDivide(
									imageDataSize);

							adControllerImpl.getCameraXYScannable().asynchronousMoveTo(
									new double[] { clickPointInImage.getEntry(0), clickPointInImage.getEntry(1) });
						} catch (Exception e) {
							reportErrorToUserAndLog("Error setting beam centre marker", e);
						}
					}
					changeImageMarker = false;
					final Cursor cursorWait = new Cursor(Display.getCurrent(), SWT.CURSOR_ARROW);
					Display.getDefault().getActiveShell().setCursor(cursorWait);
				} else if (moveOnClickEnabled) {
					try {
						final int[] clickCoordinates = event.getImagePosition();
						final RealVector actualClickPoint = createVectorOf(clickCoordinates[0], clickCoordinates[1]);		
						ImageData imageData = mJPeg.getImageData();
						final RealVector imageDataSize = createVectorOf(imageData.width, imageData.height);
						final RealVector imageSize = createVectorOf(adControllerImpl.getImageWidth(), adControllerImpl.getImageHeight());
						
						final RealVector clickPointInImage = actualClickPoint.ebeMultiply(imageSize).ebeDivide(imageDataSize);		
						double beamCenterX = ScannableUtils.getCurrentPositionArray(
								adControllerImpl.getRotationAxisXScannable())[0];
						double beamCenterY = ScannableUtils.getCurrentPositionArray(adControllerImpl.getCameraXYScannable())[1];
						final RealVector beamCenterV = createVectorOf(beamCenterX, beamCenterY);
						final RealVector pixelOffset = beamCenterV.subtract(clickPointInImage);

						DisplayScaleProvider scale = adControllerImpl.getCameraScaleProvider();
						
							double moveInX = -pixelOffset.getEntry(0) / scale.getPixelsPerMMInX();
							double moveInY = -pixelOffset.getEntry(1) / scale.getPixelsPerMMInY();

						ScannableMotionUnits sampleCentringXMotor = adControllerImpl.getSampleCentringXMotor();
						sampleCentringXMotor.asynchronousMoveTo(ScannableUtils
								.getCurrentPositionArray(sampleCentringXMotor)[0] + moveInX);
						ScannableMotionUnits sampleCentringYMotor = adControllerImpl.getSampleCentringYMotor();
						sampleCentringYMotor.asynchronousMoveTo(ScannableUtils
								.getCurrentPositionArray(sampleCentringYMotor)[0] + moveInY);							

						
					} catch (Exception e) {
						reportErrorToUserAndLog("Error processing imageFinished", e);
					}
				}

			}

			@Override
			public void imageDragged(IImagePositionEvent event) {
			}
		}, null);

		Vector<Action> showActions = new Vector<Action>();
		Action showNormalisedImageAction = new Action("Show Normalied Image") {
			@Override
			public void run() {
				try {
					showNormalisedImage();
				} catch (Exception e) {
					reportErrorToUserAndLog("Error performing showNormalisedImage", e);
				}
			}

			private void showNormalisedImage() throws InvocationTargetException, InterruptedException {
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
				final String cmd = String.format(adControllerImpl.getShowNormalisedImageCmd() , value);
				
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
		};
		Action zoomFit = new Action("Zoom to Fit") {
			@Override
			public void run() {
				zoomToFit();
			}
		};
		
		final Action rotationAxisAction = new Action("Show rotation axis", IAction.AS_CHECK_BOX) {
			@Override
			public void run() {
				try {
					showRotationAxis(isChecked());
				} catch (Exception e) {
					reportErrorToUserAndLog("Error showing rotation axis", e);
				}
			}
		};
		try {
			showRotationAxis(true);
			rotationAxisAction.setChecked(true);// do not
		} catch (Exception e) {
			reportErrorToUserAndLog("Error showing rotation axis", e);
		}		
		final Action showImageMarkerAction = new Action("Show beam centre", IAction.AS_CHECK_BOX) {
			@Override
			public void run() {
				try {
					showImageMarker(isChecked());
				} catch (Exception e) {
					reportErrorToUserAndLog("Error showing beam centre", e);
				}
			}
		};
		try {
			showImageMarker(true);
			showImageMarkerAction.setChecked(true);// do not
		} catch (Exception e) {
			reportErrorToUserAndLog("Error showing beam centre", e);
		}		
		
		showActions.add(showNormalisedImageAction);
		showActions.add(zoomFit);
		showActions.add(rotationAxisAction);
		showActions.add(showImageMarkerAction);

		MenuCreator showMenu = new MenuCreator("Show",
				"Actions that lead to items shown on the image or in other views", showActions);

		Action moveOnClickAction = new Action("Move Sample On Click", IAction.AS_CHECK_BOX) {
			@Override
			public void run() {
				moveOnClickEnabled = !moveOnClickEnabled;
			}
		};
		moveOnClickAction.setChecked(false);// do not


		Vector<Action> moveActions= new Vector<Action>();
		moveActions.add(moveOnClickAction);
		
		MenuCreator moveMenu = new MenuCreator("Alignment","Actions that move the camera and sample stages",moveActions);
		
		IActionBars actionBars = getViewSite().getActionBars();
		IToolBarManager toolBar = actionBars.getToolBarManager();
		toolBar.add(showMenu);
		toolBar.add(moveMenu);

		adControllerImpl.getRotationAxisXScannable().addIObserver(new IObserver() {

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
		
		adControllerImpl.getCameraXYScannable().addIObserver(new IObserver() {

			@Override
			public void update(Object source, final Object arg) {
				if ((arg instanceof ScannableStatus && (((ScannableStatus) arg).status == ScannableStatus.IDLE))
						|| (arg instanceof ScannablePositionChangeEvent)) {
					showImageMarkerFromNonUIThread(showImageMarkerAction);
				}
			}

		});
		
	}
	
	private void showRotationAxisFromNonUIThread(final Action rotationAxisAction) {
		if (rotationAxisAction.isChecked()) {

			getViewSite().getShell().getDisplay().asyncExec(new Runnable() {

				@Override
				public void run() {
					try {
						showRotationAxis(true);
					} catch (Exception e) {
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
					} catch (Exception e) {
						reportErrorToUserAndLog("Error showing beam centre", e);
					}

				}
			});
		}
	}

	private void showRotationAxisFromUIThread(final Action rotationAxisAction) throws Exception {
		if (rotationAxisAction.isChecked()) {
			showRotationAxis(true);
		}
	}
	private void showImageMarkerFromUIThread(final Action showImageMarkerAction) throws Exception {
		if (showImageMarkerAction.isChecked()) {
			showImageMarker(true);
		}
	}
	
	
	private void showRotationAxis(boolean show) throws Exception {
		Figure rotationAxisFigure = getRotationAxisFigure();
		if (rotationAxisFigure.getParent() == mJPeg.getTopFigure())
			mJPeg.getTopFigure().remove(rotationAxisFigure);
		if (show) {
			int rotationAxisX = (int) ScannableUtils.getCurrentPositionArray(adControllerImpl.getRotationAxisXScannable())[0];
			Rectangle bounds = rotationAxisFigure.getBounds();
			Rectangle imageKeyBounds = new Rectangle((rotationAxisX * mJPeg.getImageData().width
					/ adControllerImpl.getImageWidth() - bounds.width / 2), 0, -1, -1);
			mJPeg.getTopFigure().add(rotationAxisFigure, imageKeyBounds);
		}
	}

	private Figure getRotationAxisFigure() throws Exception {
		if (rotationAxisFigure == null) {
			rotationAxisFigure = new CrossHairFigure();
			rotationAxisFigure.setSize(3, adControllerImpl.getImageHeight());
		}
		return rotationAxisFigure;
	}
	
	private void showImageMarker(boolean show) throws Exception {
		Figure imageMarkerFigure = getImageMarkerFigure();
		if (imageMarkerFigure.getParent() == mJPeg.getTopFigure())
			mJPeg.getTopFigure().remove(imageMarkerFigure);
		if (show) {
			double[] pos = ScannableUtils.getCurrentPositionArray(adControllerImpl.getCameraXYScannable());
			int rotationAxisX = (int) pos[0];
			int rotationAxisY = (int) pos[1];
			Rectangle bounds = imageMarkerFigure.getBounds();
			ImageData imageData = mJPeg.getImageData();
			Rectangle imageKeyBounds = new Rectangle((rotationAxisX * imageData.width
					/ adControllerImpl.getImageWidth() - bounds.width / 2), (rotationAxisY
					* imageData.height / adControllerImpl.getImageHeight() - bounds.height / 2), -1, -1);
			mJPeg.getTopFigure().add(imageMarkerFigure, imageKeyBounds);
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
	
	
	
	public void zoomToFit() {
		mJPeg.zoomFit();
	}
}