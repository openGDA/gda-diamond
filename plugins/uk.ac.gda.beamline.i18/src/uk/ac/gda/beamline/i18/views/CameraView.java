/*-
# * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i18.views;

import org.apache.commons.io.FilenameUtils;
import org.dawnsci.plotting.services.util.SWTImageUtils;
import org.eclipse.draw2d.ColorConstants;
import org.eclipse.draw2d.geometry.Rectangle;
import org.eclipse.january.dataset.DataEvent;
import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.IDataListener;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.IToolBarManager;
import org.eclipse.jface.action.Separator;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.ImageData;
import org.eclipse.swt.graphics.ImageLoader;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.FileDialog;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.epics.CAClient;
import gda.jython.InterfaceProvider;
import gov.aps.jca.CAException;
import uk.ac.gda.beamline.i18.I18BeamlineActivator;
import uk.ac.gda.client.live.stream.LiveStreamWrapper;
import uk.ac.gda.client.live.stream.view.CameraConfiguration;
import uk.ac.gda.client.live.stream.view.StreamType;
import uk.ac.gda.client.microfocus.views.BeamCentreFigure;
import uk.ac.gda.client.viewer.ImageViewer;

public class CameraView extends ViewPart {
	public static final String ID = "uk.ac.gda.beamline.i18.cameraView";
	private static final Logger logger = LoggerFactory.getLogger(CameraView.class);

	private static final String I18_SAMPLE_CAMERA_STREAM_PV = "http://bl18i-di-serv-01.diamond.ac.uk:8081/DCAM.CAM1.mjpg.mjpg";
	private ImageViewer viewer;
	private LiveStreamWrapper stream;
	private String snapDirectory = InterfaceProvider.getPathConstructor().createFromProperty("gda.cameraview.snapshot.dir");


	@Override
	public void createPartControl(Composite parent) {
		viewer = new ImageViewer(parent, SWT.DOUBLE_BUFFERED);

		// Create CameraConfig that just points to the MJPEG stream URL
		CameraConfiguration config = new CameraConfiguration();
		config.setUrl(I18_SAMPLE_CAMERA_STREAM_PV);

		// Connect to the camera stream
		stream = new LiveStreamWrapper(config, StreamType.MJPEG);
		try {
			stream.connect();
			stream.addDataListener(mjpegDataListener);
		} catch (Exception e) {
			logger.warn("Problem connecting to MJPeg stream", e);
		}
		initializeToolBar();
	}

	@Override
	public void setFocus() {
		if (viewer != null) {
			viewer.setFocus();
		}
	}

	@Override
	public void dispose() {
		super.dispose();
		if (viewer != null) {
			viewer.dispose();
		}
		if (stream != null) {
			stream.disconnect();
		}
	}

	private void initializeToolBar() {
		Action openFiles = createAction("Open File", "Opens browser to locate an image file on disk",
				"icons/folder_camera.png", () -> viewer.onFileOpen());

		Action resetView = createAction("Reset view", "Reset panning and zooming", "icons/page_refresh.png",
				() -> viewer.zoomFit());

		Action start = createAction("Start", "Start video capture", "icons/camera.png", this::start);
		Action stop = createAction("Stop", "Stop video capture", "icons/stop.png", this::stop);
		Action snap = createAction("Snapshot", "Snap shot", "icons/folder_camera.png", this::openSnapshotDialog);

		IToolBarManager toolbarManager = getViewSite().getActionBars().getToolBarManager();
		toolbarManager.add(new Separator());
		toolbarManager.add(openFiles);
		toolbarManager.add(resetView);
		toolbarManager.add(new Separator());
		toolbarManager.add(start);
		toolbarManager.add(stop);
		toolbarManager.add(snap);
	}

	private Action createAction(String label, String toolTip, String imageName, Runnable runnable) {
		Action action = new Action() {
			@Override
			public void run() {
				runnable.run();
			}
		};
		action.setText(label);
		action.setToolTipText(toolTip);
		action.setImageDescriptor(I18BeamlineActivator.getImageDescriptor(imageName));
		return action;
	}

	private void openSnapshotDialog() {
		String[] filterExtensions = { "*.jpg", "*.png" };

		FileDialog fileChooser = new FileDialog(viewer.getCanvas().getShell(), SWT.SAVE);
		fileChooser.setText("Save image file");
		fileChooser.setFilterPath(snapDirectory);
		fileChooser.setFilterExtensions(filterExtensions);
		fileChooser.setFilterNames(new String[] { "JPG image (jpg)", "Png image (png)" });
		String filename = fileChooser.open();
		if (filename != null) {
			String fileType = FilenameUtils.getExtension(filename).toUpperCase();
			saveSnapshotImage(filename, fileType);
		}
	}

	private void saveSnapshotImage(String filename, String format) {
		logger.info("Saving snapshot in {} format to {}", format, filename);
		try {
			int formatNum = format.equals("PNG" ) ? SWT.IMAGE_PNG : SWT.IMAGE_JPEG;
			ImageData data = getImageData();
			ImageLoader saver = new ImageLoader();
			saver.data = new ImageData[] { data};
			saver.save(filename, formatNum);
		} catch (Exception e) {
			logger.warn("Problem collecting mjpeg image", e);
		}

	}

	/**
	 * Extract latest dataset from Live stream, and convert to make ImageData
	 * (format suitable for plotting and saving).
	 * @return
	 * @throws Exception
	 */
	private ImageData getImageData() throws Exception {
		Dataset dset = (Dataset) stream.getDataset().getSlice(null, null, null);
		return SWTImageUtils.createImageData(dset, 0, 255, null);
	}

	private IDataListener mjpegDataListener = new IDataListener() {
		private BeamCentreFigure beamCentreFigure;
		private boolean layoutReset = false;

		@Override
		public void dataChangePerformed(DataEvent event) {
			logger.debug("Data changed event : {} , {}", event.getName(), event.getShape());
			if (viewer == null) {
				return;
			}

			try {
				ImageData image = getImageData();
				if (image != null) {
					viewer.loadImage(image);
					initViewer();
				}
			} catch (Exception e) {
				logger.error("Problem collecting mjpeg image", e);
			}
		}

		private void initViewer() {
			// only layout after the first image has been loaded into the view.
			if (!layoutReset) {
				layoutReset = true;
				viewer.getCanvas().getDisplay().asyncExec(() -> {
					viewer.resetView();
					initializeBeamFigures();
					updateBeamCentreFigure();
				});
			}
		}

		private void updateBeamCentreFigure() {
			int x = (viewer.getImageData().width - beamCentreFigure.getCrossHairSize().width) / 2;
			int y = (viewer.getImageData().height - beamCentreFigure.getCrossHairSize().height) / 2;
			Rectangle beamCentreFigurePosition = new Rectangle(x, y, -1, -1);
			viewer.getTopFigure().setConstraint(beamCentreFigure, beamCentreFigurePosition);
		}

		private void initializeBeamFigures() {
			if (beamCentreFigure == null) {
				beamCentreFigure = new BeamCentreFigure();
				beamCentreFigure.setForegroundColor(ColorConstants.red);
				viewer.getTopFigure().add(beamCentreFigure, new Rectangle(0, 0, -1, -1));
			}
		}
	};

	private void start() {
		// only do this if we are connected
		if (viewer != null) {
			CAClient ca = new CAClient();
			try {
				ca.caput("BL18I-DI-DCAM-01:CAM:CAM:Acquire", 1);
			} catch (CAException e) {
				logger.error("Error starting streaming", e);
			} catch (InterruptedException e) {
				logger.error("Interrupted while starting streaming");
				Thread.currentThread().interrupt();
			}
		}
	}

	private void stop() {
		// only do this if we are connected
		if (viewer != null) {
			CAClient ca = new CAClient();
			try {
				ca.caput("BL18I-DI-DCAM-01:CAM:CAM:Acquire", 0);
			} catch (CAException e) {
				logger.error("Error stopping streaming", e);
			} catch (InterruptedException e) {
				logger.error("Interrupted while stoppin streaming");
				Thread.currentThread().interrupt();
			}
		}
	}
}
