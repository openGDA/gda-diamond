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

package uk.ac.gda.ui.views.synoptic;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.ImageData;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.RGB;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.factory.Finder;
import gda.observable.IObserver;
import uk.ac.diamond.daq.concurrent.Async;

class HighlightImageLabel implements IObserver {

	private static final Logger logger = LoggerFactory.getLogger(HighlightImageLabel.class);

	private final Composite parent;
	private Label nameLabel;
	private Scannable scannable;

	/** Position of widget relative to origin of background image (percent). */
	private Point relativePosition = new Point(0,0);

	/** Absolute position of label in parent composite */
	private Point position = new Point(0,0);

	/** Image when scannable is not busy */
	private Image normalImage;

	/** Image shown when scannable is busy */
	private Image busyImage;

	/** Highlight colour used to modify normalImage to create busyImage (default = red)*/
	private RGB highlightColor = new RGB(255,0,0);


	public HighlightImageLabel(final Composite parent) {
		this.parent = parent;
		setLayout();
		scannable = null;
	}

	public HighlightImageLabel(Composite parent, Scannable scannable) {
		this.parent = parent;
		setLayout();
		setScannable(scannable);
	}

	public HighlightImageLabel(Composite parent, String scannableName) {
		this.parent = parent;
		setLayout();
		scannable = Finder.getInstance().find(scannableName);
		setScannable(scannable);
	}

	private void setLayout() {
		nameLabel = new Label(parent, SWT.NONE);
		nameLabel.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true, 3, 1));
	}

	public void setScannable(Scannable scannable) {
		this.scannable = scannable;
		scannable.addIObserver(this);
		nameLabel.setToolTipText("Scannable : "+scannable.getName());
	}

	/** Create busyImage from normalImage by making a copy of it and changing all black pixels to highlightColor */
	public void makeHighLightImage() {

		ImageData imageData = (ImageData) normalImage.getImageData().clone();
		int highlightPixel = imageData.palette.getPixel(highlightColor);
		int blackPixel = imageData.palette.getPixel(new RGB(0,0,0));

		for(int i=0; i<imageData.width; i++) {
			for(int j=0; j<imageData.height; j++) {
				int val = imageData.getPixel(i, j);
				if (val==blackPixel) {
					imageData.setPixel(i, j, highlightPixel);
				}
			}
		}
		busyImage = new Image(parent.getDisplay(), imageData);
	}

	public void setImage(Image image) {
		this.normalImage = image;
		setLabelImage(normalImage);
	}

	public void setLabelImage() {
		setLabelImage(normalImage);
	}

	/**
	 * Set label to use specified image
	 * @param image
	 */
	public void setLabelImage(final Image image) {
		if (!parent.isDisposed()) {
			parent.getDisplay().syncExec(new Runnable() {
				@Override
				public void run() {
					logger.debug("Update label image");

					if (!nameLabel.isDisposed()) {
						nameLabel.setImage(image);
					}
				}
			});
		}
	}

	/** Wait for scannable to finishe being busy, update between busy and idle label images */
	private void updateLabelWaitForScannable() {
		if (scannable==null) {
			return;
		}
		updateInProgress = true;
		logger.debug("LineLabel update called");
		try {
			setLabelImage(busyImage);
			do {
				logger.debug("Wait while scannable is busy");
				Thread.sleep(250);
			} while (scannable.isBusy() );
			logger.debug("Scannable movement finished");
			setLabelImage(normalImage);

		} catch (InterruptedException | DeviceException e) {
			logger.warn("Problem waiting for scannable to finish", e);
		}
		updateInProgress = false;
	}

	private volatile boolean updateInProgress = false;

	@Override
	public void update(Object source, Object arg) {
		if (updateInProgress)
			return;

		Async.execute(this::updateLabelWaitForScannable);
	}

	public void setLabelText(String text) {
		nameLabel.setText(text);
	}

	public void setHighlightImage(Image highlightImage) {
		this.busyImage = highlightImage;
	}

	public Image getHighlightImage() {
		return busyImage;
	}

	public Control getControl() {
		return nameLabel;
	}
}
