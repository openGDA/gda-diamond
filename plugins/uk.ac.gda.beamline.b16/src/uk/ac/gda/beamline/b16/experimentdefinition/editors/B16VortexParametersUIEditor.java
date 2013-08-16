/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.b16.experimentdefinition.editors;

import gda.configuration.properties.LocalProperties;
import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.XmapDetector;
import gda.factory.Finder;
import gda.jython.gui.JythonGuiConstants;
import gda.jython.scriptcontroller.ScriptExecutor;

import java.io.File;
import java.io.IOException;
import java.io.Serializable;
import java.lang.reflect.InvocationTargetException;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.operation.IRunnableWithProgress;
import org.eclipse.ui.progress.IProgressService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beans.ElementCountsData;
import uk.ac.gda.exafs.ui.detector.vortex.VortexParametersUIEditor;
import uk.ac.gda.richbeans.editors.DirtyContainer;

public class B16VortexParametersUIEditor extends VortexParametersUIEditor {

	private static final Logger logger = LoggerFactory.getLogger(B16VortexParametersUIEditor.class);

	public B16VortexParametersUIEditor(String path, URL mappingURL, DirtyContainer dirtyContainer, Object editingBean) {
		super(path, mappingURL, dirtyContainer, editingBean);
	}

	@Override
	protected void upload(Object... upLoadbean) throws Exception {
		final Serializable bean;
		if (upLoadbean.length == 0) {
			// We save
			bean = (Serializable) updateFromUIAndReturnEditingBean();
		} else {
			bean = (Serializable) upLoadbean[0];
		}

		// need some fix to ExafsValidator.validate()
//		try {
//			DetectorValidator.getInstance().validate((VortexParameters) bean);
//		} catch (InvalidBeanException ne) {
//
////			try {
////				EclipseUtils.getActivePage().showView("org.eclipse.ui.views.ProblemView");
////			} catch (PartInitException e) {
////				logger.error("Cannot open view " + "org.eclipse.ui.views.ProblemView");
////			}
////
////			MessageDialog.openError(getSite().getShell(), "Cannot Configure Detector", "The current configuration of '"
////					+ getPartName() + "' is not valid.\n\nPlease check problems view for the problems.");
//			
//			// TODO if not adding a marker then no point showing the problems view...
//			
//			MessageDialog.openError(getSite().getShell(), "Cannot Configure Detector", "The current configuration of '"
//					+ getPartName() + "' is not valid.\n\n" + ne.getMessage());
//
//			return;
//		}

		final boolean ok = MessageDialog
				.openConfirm(
						getSite().getShell(),
						"Confirm Configure",
						"Are you sure you would like to permanently change the detector configuration?\n\n"
								+ "Please note, this will overwrite the detector configuration and ask the detector to reconfigure."
								+ "\n\n(A local copy of the file has been saved if you choose to cancel.)");
		if (!ok)
			return;

		IProgressService service = (IProgressService) getSite().getService(IProgressService.class);
		service.run(true, false, new IRunnableWithProgress() {
			@Override
			public void run(IProgressMonitor monitor) throws InvocationTargetException, InterruptedException {

				monitor.beginTask("Configure Detector", 100);

				try {
					final Map<String, Serializable> data = new HashMap<String, Serializable>(1);
					data.put("VortexParametersToLoad", bean);
					monitor.worked(10);
					ScriptExecutor.Run("ExafsScriptObserver", createObserver(), data, command
							+ "(VortexParametersToLoad)", JythonGuiConstants.TERMINALNAME);
					monitor.worked(50);

				} catch (Exception e) {
					logger.error("Internal error cannot get data from detector.", e);
				} finally {
					monitor.done();
				}
			}
		});
	}
	
	/**
	 * Not called in UI thread. This needs to be protected if data
	 * is obtained from ui objects.
	 * 
	 * @param monitor
	 */
	@Override
	protected void acquire(final IProgressMonitor monitor, final double collectionTimeValue) {

		if (monitor != null)
			monitor.beginTask("Acquire xMap data", 100);

		final XmapDetector xmapDetector = (XmapDetector) Finder.getInstance().find(vortexParameters.getDetectorName());
		// final Timer tfg = (Timer) Finder.getInstance().find(vortexParameters.getTfgName());

//		double deadTime = 0d;
		try {
			if (monitor != null)
				xmapDetector.setAcquisitionTime(collectionTimeValue);
			if (monitor != null)
				xmapDetector.clearAndStart();
			if (monitor != null)
				monitor.worked(10);
			// tfg.countAsync(collectionTimeValue);
			if (monitor != null)
				monitor.worked(10);
			while (xmapDetector.getStatus() != Detector.IDLE) {
				try {
					Thread.sleep(100);
					if (monitor!=null)  {
						if (monitor.isCanceled()) {
							xmapDetector.stop();
							return;
						}
						monitor.worked(5);
					}
				} catch (InterruptedException e) {
				}
			}
			if (monitor!=null)  if (monitor.isCanceled()) return;

			if (monitor!=null)  logger.debug("Stopping xmap detector " + xmapDetector.getStatus());
			if (monitor!=null)  xmapDetector.stop();
			if (monitor!=null)  monitor.worked(10);
			
			final int [][] data = xmapDetector.getData();
			if (monitor!=null)  monitor.worked(10);
		
			final int [][][] data3d = get3DArray(data);
			getDataWrapper().setValue(ElementCountsData.getDataFor(data3d));
			detectorData = getData(data3d);

			if (monitor!=null)  monitor.worked(10);
			
//			final double realTime = xmapDetector.getRealTime()*1000d;
//			deadTime              = realTime-collectionTimeValue;
			if(writeToDisk && monitor != null)
			{
				String spoolDirPath = LocalProperties.get("gda.device.vortex.spoolDir");
				final File filePath = File.createTempFile("mca", ".mca", new File(spoolDirPath));
				save(detectorData,filePath.getAbsolutePath() );
				logger.info("Saved to filePath " + filePath);
				// Get res grade for calibration.
				getSite().getShell().getDisplay().syncExec(new Runnable() {
					@Override
					public void run() {
						acquireFileLabel.setText("Saved to: " + filePath.getAbsolutePath());
					}
				});
				
			}
			
		} catch (DeviceException e) {
			logger.error("Internal errror cannot get xMap data from Vortex detector.",e);
			return;
		} catch (IOException e) {
			logger.error("Unable to save the acquired data to file ", e);
		} finally {
			if (monitor!=null)  monitor.done();
			sashPlotForm.appendStatus("Collected data from detector successfully.", logger);
		}

		// Note: currently has to be in this order.
		getSite().getShell().getDisplay().asyncExec(new Runnable() {
			@Override
			public void run() {
				getDetectorElementComposite().setEndMaximum(detectorData[0][0].length-1);
				plot(getDetectorList().getSelectedIndex(), true);
				setEnabled(true);
			}
		});

	}
}
