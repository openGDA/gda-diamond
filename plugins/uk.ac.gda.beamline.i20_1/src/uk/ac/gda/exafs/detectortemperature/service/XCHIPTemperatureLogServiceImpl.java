/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.detectortemperature.service;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.File;
import java.io.FileFilter;
import java.io.IOException;
import java.nio.file.FileSystems;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.WatchEvent;
import java.nio.file.WatchKey;
import java.nio.file.WatchService;
import java.util.Arrays;
import java.util.Comparator;
import java.util.Date;
import java.util.List;
import java.util.Vector;

import org.apache.commons.io.filefilter.WildcardFileFilter;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.january.dataset.IDataset;
import org.eclipse.ui.IViewPart;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.detectortemperature.XCHIPTemperatureLogParser;
import uk.ac.gda.exafs.ui.views.DetectorTemperatureLogView;

public class XCHIPTemperatureLogServiceImpl implements PropertyChangeListener, XCHIPTemperatureLogService {

	private static Logger logger = LoggerFactory.getLogger(XCHIPTemperatureLogServiceImpl.class);

	private static XCHIPTemperatureLogServiceImpl mInstance;

	private String currentDetectorName;
	private WatchService watcher;
	// private Path logfile;
	private long plottingStartTime;

	private Path logfile;

	public static XCHIPTemperatureLogServiceImpl getInstance() {

		if (mInstance == null) {
			mInstance = new XCHIPTemperatureLogServiceImpl();
		}

		return mInstance;

	}

	private XCHIPTemperatureLogServiceImpl() {
		DetectorModel.INSTANCE.addPropertyChangeListener(this);
		determineLogFilename();
	}

	private void determineLogFilename() {
		String latestDetectorName = DetectorModel.INSTANCE.getCurrentDetector().getName();
		if (currentDetectorName == null || currentDetectorName.isEmpty()
				|| latestDetectorName.compareTo(currentDetectorName) != 0) {
			currentDetectorName = latestDetectorName;
			logfile = fetchCurrentLogFile();
		}
	}

	private Path fetchCurrentLogFile() {
		File[] logFiles = fetchOrderedListOfTempLogFiles();
		return Paths.get(logFiles[0].getAbsolutePath());
	}

	private File[] fetchOrderedListOfTempLogFiles() {

		File dir = getLogDirectory();
		FileFilter fileFilter = new WildcardFileFilter(currentDetectorName + "_temperatures_*");
		File[] files = dir.listFiles(fileFilter);

		Arrays.sort(files, new Comparator<File>() {
			@Override
			public int compare(File f1, File f2) {
				return Long.valueOf(f2.lastModified()).compareTo(f1.lastModified());
			}
		});

		return files;
	}

	/**
	 * Begins a thread to look for updates to the log file and plots new data
	 */
	@Override
	public void startObservingLogFile() {
		// http://docs.oracle.com/javase/tutorial/essential/io/notification.html
		if (watcher == null) {
			try {
				watcher = FileSystems.getDefault().newWatchService();
				plottingStartTime = (new Date()).getTime();
				Path logDir = getLogDirectory().toPath();
				final WatchKey key = logDir.register(watcher, java.nio.file.StandardWatchEventKinds.ENTRY_MODIFY);
				Thread thread = new Thread(() -> processEvents(key), XCHIPTemperatureLogServiceImpl.class.getName());
				thread.setDaemon(true);
				thread.start();
			} catch (IOException e) {
				// TODO Auto-generated catch block
				logger.error("TODO put description of error here", e);
			}
		}
	}

	private File getLogDirectory() {
		return new File("/dls/i20-1/data/2014/cm4975-3/tmp");
	}

	private void processEvents(WatchKey key) {
		for (;;) {

			for (WatchEvent<?> event : key.pollEvents()) {
				File[] logFiles = fetchOrderedListOfTempLogFiles();

				if (logFiles[0].compareTo(logfile.toFile()) != 0) {
					logfile = fetchCurrentLogFile();
				}

				Path name = (Path) event.context();

				if (name.compareTo(logfile.getFileName()) == 0) {

					// Path child = logfile.resolve(name);

					// print out event
					// System.out.format("%s: %s\n", event.kind().name(), child);

					try {
						readAndBroadcastTemperatures();
					} catch (Exception e) {
						// TODO Auto-generated catch block
						logger.error("TODO put description of error here", e);
						stopObservingLogFile();
						break;
					}
				}
			}

			// reset key and remove from set if directory no longer accessible
			boolean valid = key.reset();
			if (!valid) {
				stopObservingLogFile();
				break;
			}
		}
	}

	private synchronized void readAndBroadcastTemperatures() {
		final IDataset[][] temps = readTemperatures();

		PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
			@Override
			public void run() {
				// find the view
				IWorkbenchPage page = PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage();
				IViewPart view = page.findView(DetectorTemperatureLogView.ID);

				// get the adapter
				IPlottingSystem plottingSystem = view.getAdapter(IPlottingSystem.class);

				// plot
				List<IDataset> temperatures = new Vector<IDataset>();
				for (IDataset ds : temps[1]) {
					if (ds != null) {
						temperatures.add(ds);
					}
				}

				if (temperatures.size() > 0) {
					plottingSystem.getSelectedXAxis().setDateFormatEnabled(true);
					plottingSystem.getSelectedXAxis().setFormatPattern("HH:mm:ss.SSS E");
					plottingSystem.getSelectedXAxis().setAutoFormat(false);

					plottingSystem.createPlot1D(temps[0][0], temperatures, null);
				}
			}
		});
	}

	private IDataset[][] readTemperatures() {
		XCHIPTemperatureLogParser parser = new XCHIPTemperatureLogParser(logfile.toString());
		return parser.getTemperaturesSince(plottingStartTime);
	}

	@Override
	public void stopObservingLogFile() {
		try {
			watcher.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			logger.error("TODO put description of error here", e);
		}
		watcher = null;
	}

	@Override
	public void propertyChange(PropertyChangeEvent evt) {
		if (!DetectorModel.INSTANCE.getCurrentDetector().getName().equals(currentDetectorName)) {
			determineLogFilename();
		}
	}

	@Override
	public void extendPlottingHistory() {
		long twoHoursInImilliSeconds = 2*60*60*1000;
		plottingStartTime = plottingStartTime - (twoHoursInImilliSeconds);
		Date startTime = new Date(plottingStartTime);
		System.out.println(startTime.toString());
		if (watcher != null) {
			readAndBroadcastTemperatures();
		}
	}
}