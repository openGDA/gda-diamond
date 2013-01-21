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

import java.util.Vector;

import org.dawnsci.plotting.jreality.tool.IImagePositionEvent;
import org.dawnsci.plotting.jreality.tool.ImagePositionListener;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.graphics.Cursor;
import org.eclipse.swt.graphics.ImageData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.MenuItem;
import org.eclipse.ui.IActionBars;
import org.eclipse.ui.PlatformUI;

import uk.ac.gda.beamline.i13i.ADViewer.views.MJPegView;
import uk.ac.gda.beamline.i13i.views.cameraview.CrossHairFigure;

public class I13MJPegView extends MJPegView {

	I13ADControllerImpl adControllerImpl = null;
	boolean changeRotationAxisX = false;

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
		LensScannableComposite lensScannableComposite = new LensScannableComposite(composite_1, SWT.NONE);
		lensScannableComposite.setLensScannable(adControllerImpl.getLensScannable());

	}

	protected void hookGlobalActions() {
	}

	protected void createContextMenu() {

		
	}

	protected void createToolbar() {
	}

	protected void createMenu() {
	}

	protected void createActions() {
	}	
	
	
	private void addSpecialisation() {
		areaDetectorLiveComposite.getTopFigure().add(new CrossHairFigure());

		Menu rightClickMenu = new Menu(areaDetectorLiveComposite.getCanvas());
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

		areaDetectorLiveComposite.getCanvas().setMenu(rightClickMenu);

		areaDetectorLiveComposite.addImagePositionListener(new ImagePositionListener() {

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
						// try {
						final int[] clickCoordinates = event.getImagePosition();
						// final RealVector actualClickPoint = createVectorOf(clickCoordinates[0], clickCoordinates[1]);
						ImageData imageData = areaDetectorLiveComposite.getImageData();
						// final RealVector imageDataSize = createVectorOf(imageData.width, imageData.height);
						// final RealVector imageSize = createVectorOf(imageWidth, imageHeight);

						// final RealVector clickPointInImage = actualClickPoint.ebeMultiply(imageSize).ebeDivide(
						// imageDataSize);

						// cameraConfig.getRotationAxisXScannable().asynchronousMoveTo(clickPointInImage.getEntry(0));
						// } catch (DeviceException e) {
						// reportErrorToUserAndLog("Error setting rotationAxis", e);
						// }
					}
					changeRotationAxisX = false;
					final Cursor cursorWait = new Cursor(Display.getCurrent(), SWT.CURSOR_ARROW);
					Display.getDefault().getActiveShell().setCursor(cursorWait);
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

			private void showNormalisedImage() {
				// TODO Auto-generated method stub

			}
		};
		Action zoomFit = new Action("Zoom to Fit") {
			@Override
			public void run() {
				zoomToFit();
			}
		};
		showActions.add(showNormalisedImageAction);
		showActions.add(zoomFit);

		MenuCreator showMenu = new MenuCreator("Show",
				"Actions that lead to items shown on the image or in other views", showActions);

		IActionBars actionBars = getViewSite().getActionBars();
		IToolBarManager toolBar = actionBars.getToolBarManager();
		toolBar.add(showMenu);

	}

	public void zoomToFit() {
		areaDetectorLiveComposite.zoomFit();
	}
}