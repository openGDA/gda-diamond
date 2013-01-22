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

import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.layout.GridDataFactory;
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

import uk.ac.gda.beamline.i13i.views.cameraview.CrossHairFigure;
import uk.ac.gda.epics.adviewer.composites.imageviewer.IImagePositionEvent;
import uk.ac.gda.epics.adviewer.composites.imageviewer.ImagePositionListener;
import uk.ac.gda.epics.adviewer.views.MJPegView;

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
						// try {
						final int[] clickCoordinates = event.getImagePosition();
						// final RealVector actualClickPoint = createVectorOf(clickCoordinates[0], clickCoordinates[1]);
						ImageData imageData = mJPeg.getImageData();
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
		mJPeg.zoomFit();
	}
}