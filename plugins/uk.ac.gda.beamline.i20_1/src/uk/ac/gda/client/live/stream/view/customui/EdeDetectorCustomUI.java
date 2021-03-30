/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

package uk.ac.gda.client.live.stream.view.customui;

import java.util.Optional;

import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.detector.EdeDetector;
import gda.device.detector.FrelonDetector;
import gda.device.detector.frelon.FrelonCcdDetectorData;
import gda.device.frelon.Frelon;
import gda.device.lima.LimaCCD;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.observable.IObserver;
import gda.scan.Scan.ScanStatus;
import gda.scan.ScanEvent;
import uk.ac.diamond.daq.concurrent.Async;
import uk.ac.gda.client.live.stream.simulator.connector.ImageDatasetConnector;
import uk.ac.gda.exafs.ui.NumberBoxWithUnits;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;


public class EdeDetectorCustomUI extends AbstractLiveStreamViewCustomUi {
	private static final Logger logger = LoggerFactory.getLogger(EdeDetectorCustomUI.class);

	private String detectorName = "";
	private EdeDetector edeDetector = null;
	private double accumulationTimeMs = 100.0;
	private int numAccumulations = 1;

	private NumberBoxWithUnits accumulationTimeBox;
	private NumberBoxWithUnits numAccumulationsBox;
	private Button startButton;
	private Button stopButton;

	private volatile boolean collectionRunning = false;
	private volatile boolean stopCollection;

	@Override
	public void createUi(Composite composite) {
		findDetector();
		if (edeDetector == null) {
			String message = "Warning : could not create controls - no detector called '"+detectorName+"' was found!";
			logger.warn(message);
			new Text(composite, SWT.NONE).setText(message);
			return;
		}

		getAccumulationParamsFromDetector();

		addButtons(composite);

		enableWidgets(true);

		// Make plot axes visible
		getPlottingSystem().getAxes().get(0).setVisible(true);
		getPlottingSystem().getAxes().get(1).setVisible(true);

		InterfaceProvider.getScanDataPointProvider().addScanEventObserver(serverObserver);

		composite.addDisposeListener( l -> InterfaceProvider.getScanDataPointProvider().addScanEventObserver(serverObserver));
	}


	IObserver serverObserver = (source, arg) -> {
		if (!(arg instanceof ScanEvent)) {
			return;
		}

		ScanEvent scanEvent = (ScanEvent) arg;
		String[] detectorNames = scanEvent.getLatestInformation().getDetectorNames();

		// Don't do anything if scan doesn't involve the detector
//		if (!Arrays.asList(detectorNames).contains(edeDetector.getName())) {
//			return;
//		}

		// disable start, stop buttons at scan start/if scan is running
		ScanStatus status = scanEvent.getLatestStatus();
		if (status.isRunning()) { // NB isRunning == *false* when cscan is running! (status = 'Not started')
				// stop the live collection loop
				if (collectionRunning) {
				logger.info("Listener : stop collection widgets");
				stopCollectionAndWait();
				}
				enableWidgets(false, false);
		} else if (status.isComplete()) {
			logger.info("Listener : Enable widgets");
			enableWidgets(true);
		}
	};

	private void stopCollectionAndWait() {

		stopCollection = true;
		while(collectionRunning) {
			try {
				Thread.sleep(100);
			} catch (InterruptedException e) {
				logger.error("Interrupted while waiting for collection to finish", e);
			}
		}
		logger.debug("Finished waiting");
	}
	private void findDetector() {
		Optional<EdeDetector> det = Finder.findOptionalOfType(detectorName, EdeDetector.class);
		if (det.isPresent()) {
			edeDetector = det.get();
		}
	}

	private void addButtons(Composite parent) {

		Composite mainComposite = new Composite(parent, SWT.NONE);
		GridLayoutFactory.fillDefaults().numColumns(4).applyTo(mainComposite);

		GridDataFactory gdFactory = GridDataFactory.fillDefaults().hint(100, SWT.DEFAULT);

		Label accumulationText = new Label(mainComposite, SWT.NONE);
		accumulationText.setText("Accumulation time : ");
		accumulationTimeBox =new NumberBoxWithUnits(mainComposite, SWT.NONE);
		accumulationTimeBox.setDisplayIntegers(false);
		accumulationTimeBox.setMinimum(0.001);
		accumulationTimeBox.setMaximum(5000.0);
		accumulationTimeBox.setFormat("0.####");
		accumulationTimeBox.setUnits("ms");
		accumulationTimeBox.setValue(accumulationTimeMs);
		gdFactory.applyTo(accumulationTimeBox);

		Label numAccumulationsText = new Label(mainComposite, SWT.NONE);
		numAccumulationsText.setText("Number of accumulations : ");
		numAccumulationsBox = new NumberBoxWithUnits(mainComposite, SWT.NONE);
		numAccumulationsBox.setDisplayIntegers(true);
		numAccumulationsBox.setMinimum(1.0);
		numAccumulationsBox.setMaximum(1000.0);
		numAccumulationsBox.setValue((double)numAccumulations);
		gdFactory.applyTo(numAccumulationsBox);

		Composite mainComposite2 = new Composite(parent, SWT.NONE);
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(mainComposite2);

		startButton = new Button(mainComposite2, SWT.PUSH);
		startButton.setText("Start");
		startButton.addListener(SWT.Selection, e -> Async.execute(this::startDetector));
		gdFactory.applyTo(startButton);

		stopButton = new Button(mainComposite2, SWT.PUSH);
		stopButton.setText("Stop");
		stopButton.addListener(SWT.Selection, e -> stopDetector());
		gdFactory.applyTo(stopButton);

//		Button quitButton = new Button(mainComposite2, SWT.PUSH);
//		quitButton.setText("Quit!");
//		quitButton.addListener(SWT.Selection, e -> {
//			PlatformUI.getWorkbench().getDisplay().asyncExec(() -> {
//				PlatformUI.getWorkbench().saveAllEditors(false);
//				PlatformUI.getWorkbench().close();
//			});
//		});

	}

	/**
	 * Update number of accumulations and accumulation time using values from the detector
	 * (for Frelon only)
	 */
	private void getAccumulationParamsFromDetector() {
		if (!(edeDetector instanceof FrelonDetector)) {
			return;
		}

		edeDetector.fetchDetectorSettings();
		FrelonCcdDetectorData detData = (FrelonCcdDetectorData) edeDetector.getDetectorData();
		if (detData.getAcqMode()==LimaCCD.AcqMode.SINGLE) {
			numAccumulations = 1;
			accumulationTimeMs = detData.getExposureTime();
		} else {
			accumulationTimeMs = 1000*detData.getAccumulationMaximumExposureTime();
			double timePerSpectrum = 1000*detData.getExposureTime(); // total time per spectrum
			numAccumulations = (int) Math.floor(timePerSpectrum/accumulationTimeMs);
		}

	}

	/**
	 * Enable/disable accumulation widgets and start button
	 * (this is called when the start, stop buttons are pressed).
	 *
	 * @param enable
	 */
	private void enableWidgets(boolean enable, boolean enableStop) {
		Display.getDefault().asyncExec( () -> {
			accumulationTimeBox.setEnabled(enable);
			numAccumulationsBox.setEnabled(enable);
			startButton.setEnabled(enable);
			stopButton.setEnabled(enableStop);
		});
	}
	private void enableWidgets(boolean enable) {
		enableWidgets(enable, !enable);
	}

	private void startDetector() {
		if (collectionRunning) {
			logger.info("Collection thread already running");
			return;
		}
		try {
			enableWidgets(false);

			accumulationTimeMs = accumulationTimeBox.getValue();
			numAccumulations = numAccumulationsBox.getValue().intValue();

			configureDetector();
			double timePerSpectrum = accumulationTimeMs*numAccumulations;
			collectionRunning = true;
			stopCollection = false;
			while(!stopCollection) {
				logger.debug("Starting collection loop");

				edeDetector.waitWhileBusy();

				logger.debug("Collecting data from {}", edeDetector.getName());

				edeDetector.collectData();

				// Wait for image to be recorded
				long startTime = System.currentTimeMillis();
				while(edeDetector.isBusy() && edeDetector.getLastImageAvailable()<0) {
					Thread.sleep(50);
				}
				updateDataset();

				// Wait for a bit (dummy mode 'collectData' returns immediately).
				long timeTaken = System.currentTimeMillis() - startTime;
				logger.debug("Time taken = {} ms", timeTaken);
				if (timeTaken < timePerSpectrum) {
					Thread.sleep((long)timePerSpectrum - timeTaken);
				}
			}
		} catch (DeviceException | InterruptedException e) {
			Thread.currentThread().interrupt();
			logger.error("Problem collecting data", e);
		} finally {
			collectionRunning = false;
			stopCollection = false;
			enableWidgets(true);
		}
	}

	private void stopDetector() {
		stopCollection = true;
	}

	/**
	 * Setup the detector to record 1 frame with the current accumulation time and number of accumulations.
	 * (For Frelon, ROI is set to give full CCD image).
	 *
	 * @throws DeviceException
	 */
	private void configureDetector() throws DeviceException {
		logger.debug("Setting up {} detector : accumulation time = {} ms, num accumulations = {}", edeDetector.getName(), accumulationTimeMs, numAccumulations);
		edeDetector.stop();
		EdeScanParameters params = EdeScanParameters.createSingleFrameScan(accumulationTimeMs*0.001, numAccumulations);
		if (edeDetector instanceof FrelonDetector) {
			FrelonDetector det = (FrelonDetector) edeDetector;
			det.setRoiMode(Frelon.ROIMode.NONE);

			edeDetector.configureDetectorForROI(1, 0);
			edeDetector.configureDetectorForTimingGroup(params.getGroups().get(0));
		} else {
			edeDetector.prepareDetectorwithScanParameters(params);
		}
	}

	/**
	 * Read data from detector and pass the Dataset to the Live stream connection.
	 * @throws DeviceException
	 */
	private void updateDataset() throws DeviceException {
		 // same as 'collectImage' in script
		logger.info("Reading detector data");
		int[] data = edeDetector.readoutFrames(0, 0);
		int xsize = edeDetector.getMaxPixel();
		int ysize = data.length / xsize;
		if(getLiveStreamConnection().getStream() instanceof ImageDatasetConnector) {
			logger.info("Sending data to live stream view (dimensions = {} x {} pixels)", xsize, ysize);
			Dataset detData = DatasetFactory.createFromObject(data, ysize, xsize);
			ImageDatasetConnector simDataset = (ImageDatasetConnector) getLiveStreamConnection().getStream();
			simDataset.setDataset(detData);
		}
	}

	public void setDetectorName(String detectorName) {
		this.detectorName = detectorName;
	}

}
