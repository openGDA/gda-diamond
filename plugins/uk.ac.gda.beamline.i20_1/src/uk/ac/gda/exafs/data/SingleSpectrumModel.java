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

package uk.ac.gda.exafs.data;

import gda.device.Scannable;
import gda.device.scannable.AlignmentStage;
import gda.device.scannable.AlignmentStageScannable;
import gda.device.scannable.AlignmentStageScannable.AlignmentStageDevice;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.Jython;
import gda.jython.JythonServerFacade;
import gda.jython.JythonServerStatus;
import gda.observable.IObservable;
import gda.observable.IObserver;
import gda.scan.AxisSpec;
import gda.scan.ede.EdeExperiment;
import gda.scan.ede.EdeExperimentProgressBean;
import gda.scan.ede.EdeScanProgressBean;
import gda.util.exafs.Element;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.client.liveplot.LivePlotView;
import uk.ac.gda.exafs.ui.data.UIHelper;

import com.google.gson.annotations.Expose;

public class SingleSpectrumModel extends ObservableModel {
	public static final SingleSpectrumModel INSTANCE = new SingleSpectrumModel(0);

	private static final Logger logger = LoggerFactory.getLogger(SingleSpectrumModel.class);

	public static final String I0_X_POSITION_PROP_NAME = "i0xPosition";
	private double i0xPosition;

	public static final String I0_Y_POSITION_PROP_NAME = "i0yPosition";
	private double i0yPosition;

	public static final String IT_X_POSITION_PROP_NAME = "iTxPosition";
	private double iTxPosition;

	public static final String IT_Y_POSITION_PROP_NAME = "iTyPosition";
	private double iTyPosition;

	public static final String I0_INTEGRATION_TIME_PROP_NAME = "i0IntegrationTime";
	@Expose
	private double i0IntegrationTime;

	public static final String I0_NUMBER_OF_ACCUMULATIONS_PROP_NAME = "i0NumberOfAccumulations";
	@Expose
	private int i0NumberOfAccumulations;

	public static final String IT_INTEGRATION_TIME_PROP_NAME = "itIntegrationTime";
	@Expose
	private double itIntegrationTime;

	public static final String IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME = "itNumberOfAccumulations";
	@Expose
	private int itNumberOfAccumulations;

	public static final String FILE_NAME_PROP_NAME = "fileName";
	private String fileName;

	public static final String IREF_X_POSITION_PROP_NAME = "iRefxPosition";
	private double iRefxPosition;

	public static final String IREF_Y_POSITION_PROP_NAME = "iRefyPosition";
	private double iRefyPosition;

	public static final String SCANNING_PROP_NAME = "scanning";
	private boolean scanning;

	private final ScanJob job;

	private String fileTemplate = "Unknown_cal_";

	private static final String SINGLE_SPECTRUM_MODEL_DATA_STORE_KEY = "SINGLE_SPECTRUM_DATA";

	private SingleSpectrumModel(@SuppressWarnings("unused") int dummy) {
		Scannable scannable = Finder.getInstance().find("alignment_stage");
		if (scannable != null && scannable instanceof AlignmentStage) {
			AlignmentStage alignmentStageScannable = (AlignmentStage) scannable;
			AlignmentStageDevice hole = alignmentStageScannable.getAlignmentStageDevice(AlignmentStageScannable.AlignmentStageDevice.hole.name());
			this.setI0xPosition(hole.getLocation().getxPosition());
			this.setI0yPosition(hole.getLocation().getyPosition());

			AlignmentStageDevice foil = alignmentStageScannable.getAlignmentStageDevice(AlignmentStageScannable.AlignmentStageDevice.hole.name());
			this.setiTxPosition(foil.getLocation().getxPosition());
			this.setiTyPosition(foil.getLocation().getyPosition());
		}
		job = new ScanJob("Performing Single spectrum scan");
		((IObservable) Finder.getInstance().findNoWarn(EdeExperiment.PROGRESS_UPDATER_NAME)).addIObserver(job);
		InterfaceProvider.getJSFObserver().addIObserver(job);
		job.setUser(true);
		AlignmentParametersModel.INSTANCE.addPropertyChangeListener(AlignmentParametersModel.ELEMENT_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if (evt.getNewValue() != null) {
					SingleSpectrumModel.this.setCurrentElement(((Element) evt.getNewValue()).getSymbol());
				}
			}
		});
		if (AlignmentParametersModel.INSTANCE.getElement() != null) {
			SingleSpectrumModel.this.setCurrentElement(AlignmentParametersModel.INSTANCE.getElement().getSymbol());
		}
		loadSingleSpectrumData();
		this.addPropertyChangeListener(new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				String changedProperty = evt.getPropertyName();
				if (changedProperty.equals(I0_INTEGRATION_TIME_PROP_NAME) |
						changedProperty.equals(IT_INTEGRATION_TIME_PROP_NAME) |
						changedProperty.equals(I0_NUMBER_OF_ACCUMULATIONS_PROP_NAME) |
						changedProperty.equals(IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME)) {
					saveSingleSpectrumData();
				}
			}
		});
	}

	private void loadSingleSpectrumData() {
		SingleSpectrumModel test = ClientConfig.EdeDataStore.INSTANCE.loadConfiguration(SINGLE_SPECTRUM_MODEL_DATA_STORE_KEY, SingleSpectrumModel.class);
		if (test == null) {
			return;
		}
		this.setI0IntegrationTime(test.getI0IntegrationTime());
		this.setI0NumberOfAccumulations(test.getI0NumberOfAccumulations());
		this.setItIntegrationTime(test.getItIntegrationTime());
		this.setItNumberOfAccumulations(test.getItNumberOfAccumulations());
	}

	private void saveSingleSpectrumData() {
		ClientConfig.EdeDataStore.INSTANCE.saveConfiguration(SINGLE_SPECTRUM_MODEL_DATA_STORE_KEY, this);
	}

	private String buildScanCommand() {
		return String.format("from gda.scan.ede.drivers import SingleSpectrumDriver; \n" +
				"scan_driver = SingleSpectrumDriver(\"%s\",\"%s\",%f,%d,%f,%d,\"%s\",%s); \n" +
				"scan_driver.setInBeamPosition(%f,%f);" +
				"scan_driver.setOutBeamPosition(%f,%f)",
				DetectorModel.INSTANCE.getCurrentDetector().getName(),
				DetectorModel.TOPUP_CHECKER,
				i0IntegrationTime / 1000, // Converts to Seconds
				i0NumberOfAccumulations,
				itIntegrationTime / 1000, // Converts to Seconds
				itNumberOfAccumulations,
				fileTemplate,
				DetectorModel.SHUTTER_NAME,
				iTxPosition, iTyPosition,
				i0xPosition, i0yPosition);
	}

	private static enum ScanJobName {
		DARK_I0("Running I0 Dark scan"),
		DAR_It("Running It Dark scan"),
		I0("Running I0 scan"),
		It("Running It scan");
		String text;
		private ScanJobName(String value) {
			text = value;
		}

		public String getText() {
			return text;
		}
	}

	public void setCurrentElement(String elementSymbol) {
		fileTemplate = elementSymbol + "_cal_%s";
	}

	private class ScanJob extends Job implements IObserver {
		private IProgressMonitor monitor;
		private ScanJobName scanJobName;
		public ScanJob(String name) {
			super(name);
			scanJobName = ScanJobName.DARK_I0;
		}

		@Override
		public void update(Object source, Object arg) {
			if (arg instanceof JythonServerStatus) {
				JythonServerStatus status = (JythonServerStatus) arg;
				if (SingleSpectrumModel.this.isScanning() && Jython.RUNNING == status.scanStatus) {
					monitor.subTask(scanJobName.getText());
					if (scanJobName.ordinal() <  ScanJobName.values().length - 1) {
						scanJobName = ScanJobName.values()[scanJobName.ordinal() + 1];
					}
				}
				if (SingleSpectrumModel.this.isScanning() && Jython.IDLE == status.scanStatus) {
					monitor.worked(1);
				}
			} else if (arg instanceof EdeExperimentProgressBean) {
				final EdeExperimentProgressBean edeExperimentProgress = (EdeExperimentProgressBean) arg;

				final EdeScanProgressBean edeScanProgress = edeExperimentProgress.getProgress();
				final String scanIdentifier = edeScanProgress.getThisPoint().getScanIdentifier();
				final String scanfilename =  edeScanProgress.getThisPoint().getCurrentFilename();
				//				String scanType = edeScanProgress.getScanType().toString();
				//				String posType = edeScanProgress.getPositionType().toString();
				final String label = edeExperimentProgress.getDataLabel();
				final AxisSpec spec = new AxisSpec("counts");

				final DoubleDataset currentNormalisedItData = edeExperimentProgress.getData();
				final DoubleDataset currentEnergyData = edeExperimentProgress.getEnergyData();

				Display.getDefault().asyncExec(new Runnable() {
					@Override
					public void run() {

						try {
							final IWorkbenchPage page = PlatformUI.getWorkbench().getActiveWorkbenchWindow()
									.getActivePage();
							LivePlotView part = (LivePlotView) page.findView(LivePlotView.ID);
							if (part == null) {
								part = (LivePlotView) page.showView(LivePlotView.ID);
							}

							part.addData(scanIdentifier, scanfilename, label, currentEnergyData, currentNormalisedItData, true, true, spec);

						} catch (Exception e) {
							UIHelper.showError("Unable to plot the data", e.getMessage());
						}
					}
				});
			}
		}

		@Override
		protected IStatus run(IProgressMonitor monitor) {
			this.monitor = monitor;
			Display.getDefault().syncExec(new Runnable() {
				@Override
				public void run() {
					SingleSpectrumModel.this.setScanning(true);
				}
			});
			monitor.beginTask("Starting " + ScanJobName.values().length + " tasks.", ScanJobName.values().length);
			try {
				String command = buildScanCommand();
				logger.info("Sending command: " + command);
				InterfaceProvider.getCommandRunner().runCommand(command);
				// give the previous command a chance to run before calling doCollection()
				Thread.sleep(50);
				final String resultFileName = InterfaceProvider.getCommandRunner().evaluateCommand("scan_driver.doCollection()");
				if (resultFileName == null) {
					throw new Exception("Unable to do collection.");
				}
				Display.getDefault().syncExec(new Runnable() {
					@Override
					public void run() {
						try {
							SingleSpectrumModel.this.setFileName(resultFileName);
						} catch (Exception e) {
							UIHelper.showWarning("Error while loading data from saved file", e.getMessage());
						}
					}
				});
			} catch (Exception e) {
				UIHelper.showWarning("Error while scanning or canceled", e.getMessage());
			}
			monitor.done();
			Display.getDefault().syncExec(new Runnable() {
				@Override
				public void run() {
					SingleSpectrumModel.this.setScanning(false);
				}
			});
			return Status.OK_STATUS;
		}

		@Override
		protected void canceling() {
			doStop();
		}
	}

	public void doCollection() throws Exception {
		if (DetectorModel.INSTANCE.getCurrentDetector() == null) {
			throw new DetectorUnavailableException();
		}
		job.schedule();
	}

	public void setFileName(String value) {
		firePropertyChange(FILE_NAME_PROP_NAME, fileName, fileName = value);
	}

	public String getFileName() {
		return fileName;
	}

	public boolean isScanning() {
		return scanning;
	}

	protected void setScanning(boolean value) {
		this.firePropertyChange(SCANNING_PROP_NAME, scanning, scanning = value);
	}

	public double getI0xPosition() {
		return i0xPosition;
	}

	public void setI0xPosition(double value) {
		firePropertyChange(I0_X_POSITION_PROP_NAME, i0xPosition, i0xPosition = value);
	}

	public double getI0yPosition() {
		return i0yPosition;
	}

	public void setI0yPosition(double value) {
		firePropertyChange(I0_Y_POSITION_PROP_NAME, i0yPosition, i0yPosition = value);
	}

	public double getI0IntegrationTime() {
		return i0IntegrationTime;
	}

	public void setI0IntegrationTime(double value) {
		firePropertyChange(I0_INTEGRATION_TIME_PROP_NAME, i0IntegrationTime, i0IntegrationTime = value);
	}

	public int getI0NumberOfAccumulations() {
		return i0NumberOfAccumulations;
	}

	public void setI0NumberOfAccumulations(int value) {
		firePropertyChange(I0_NUMBER_OF_ACCUMULATIONS_PROP_NAME, i0NumberOfAccumulations, i0NumberOfAccumulations = value);
	}

	public double getItIntegrationTime() {
		return itIntegrationTime;
	}

	public void setItIntegrationTime(double value) {
		firePropertyChange(IT_INTEGRATION_TIME_PROP_NAME, itIntegrationTime, itIntegrationTime = value);
	}

	public int getItNumberOfAccumulations() {
		return itNumberOfAccumulations;
	}

	public void setItNumberOfAccumulations(int value) {
		firePropertyChange(IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME, itNumberOfAccumulations, itNumberOfAccumulations = value);
	}

	public double getiTxPosition() {
		return iTxPosition;
	}

	public void setiTxPosition(double value) {
		firePropertyChange(IT_X_POSITION_PROP_NAME, iTxPosition, iTxPosition = value);
	}

	public double getiTyPosition() {
		return iTyPosition;
	}

	public void setiTyPosition(double value) {
		firePropertyChange(IT_Y_POSITION_PROP_NAME, iTyPosition, iTyPosition = value);
	}

	public double getiRefxPosition() {
		return iRefxPosition;
	}

	public void setiRefxPosition(double value) {
		firePropertyChange(IREF_X_POSITION_PROP_NAME, iRefxPosition, iRefxPosition = value);
	}

	public double getiRefyPosition() {
		return iRefyPosition;
	}

	public void setiRefyPosition(double value) {
		firePropertyChange(IREF_Y_POSITION_PROP_NAME, iRefyPosition, iRefyPosition = value);
	}

	public void save() throws DetectorUnavailableException {
		if (DetectorModel.INSTANCE.getCurrentDetector() == null) {
			throw new DetectorUnavailableException();
		}
		InterfaceProvider.getCommandRunner().runCommand("alignment_stage.saveDeviceFromCurrentMotorPositions(\"slits\")");
	}

	public void doStop() {
		if (this.isScanning()) {
			JythonServerFacade.getInstance().haltCurrentScan();
		}
	}
}
