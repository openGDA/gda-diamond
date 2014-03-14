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

import gda.device.scannable.AlignmentStageScannable;
import gda.factory.Finder;
import gda.jython.InterfaceProvider;
import gda.jython.Jython;
import gda.jython.JythonServerFacade;
import gda.jython.JythonServerStatus;
import gda.observable.IObservable;
import gda.observable.IObserver;
import gda.scan.ede.EdeExperiment;
import gda.util.exafs.Element;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import org.eclipse.core.databinding.Binding;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.swt.widgets.Display;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beamline.i20_1.utils.ExperimentTimeHelper;
import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.experiment.ExperimentDataModel;
import uk.ac.gda.exafs.ui.data.experiment.ExperimentMotorPostion;
import uk.ac.gda.exafs.ui.data.experiment.SampleStageMotors;
import uk.ac.gda.exafs.ui.data.experiment.SampleStageMotors.ExperimentMotorPostionType;

import com.google.gson.annotations.Expose;

public class SingleSpectrumUIModel extends ObservableModel {

	private static final Logger logger = LoggerFactory.getLogger(SingleSpectrumUIModel.class);

	private final AlignmentStageScannable.Location holeLocationForAlignment = new AlignmentStageScannable.Location();
	private final AlignmentStageScannable.Location foilLocationForAlignment = new AlignmentStageScannable.Location();

	private static final String SINGLE_JYTHON_DRIVER_OBJ = "singletimeresolveddriver";

	public static final String IT_INTEGRATION_TIME_PROP_NAME = "itIntegrationTime";
	@Expose
	private double itIntegrationTime = 1.0;

	public static final String IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME = "itNumberOfAccumulations";
	@Expose
	private int itNumberOfAccumulations = 1;

	public static final String ALIGNMENT_STAGE_SELECTION = "selectAlignmentStage";
	@Expose
	private boolean selectAlignmentStage;

	public static final String FILE_NAME_PROP_NAME = "fileName";
	private String fileName;

	public static final String SCANNING_PROP_NAME = "scanning";
	private boolean scanning;

	private ScanJob job;

	public static final String FILE_TEMPLATE_PROP_NAME = "fileTemplate";
	private String fileTemplate;

	private String elementSymbol;

	private String filePefix = "%s";

	@Expose
	private ExperimentDataModel experimentDataModel;

	protected Binding binding;

	private static final String SINGLE_SPECTRUM_MODEL_DATA_STORE_KEY = "SINGLE_SPECTRUM_DATA";

	public void setup() {
		job = new ScanJob("Performing Single spectrum scan");
		((IObservable) Finder.getInstance().findNoWarn(EdeExperiment.PROGRESS_UPDATER_NAME)).addIObserver(job);
		InterfaceProvider.getJSFObserver().addIObserver(job);
		job.setUser(true);
		AlignmentParametersModel.INSTANCE.addPropertyChangeListener(AlignmentParametersModel.ELEMENT_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if (evt.getNewValue() != null) {
					SingleSpectrumUIModel.this.setCurrentElement(((Element) evt.getNewValue()).getSymbol());
				}
			}
		});
		if (AlignmentParametersModel.INSTANCE.getElement() != null) {
			SingleSpectrumUIModel.this.setCurrentElement(AlignmentParametersModel.INSTANCE.getElement().getSymbol());
		}

		loadSingleSpectrumData();



		experimentDataModel.addPropertyChangeListener(new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				saveSingleSpectrumData();
			}
		});
		this.addPropertyChangeListener(new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if (evt.getPropertyName().equals(ALIGNMENT_STAGE_SELECTION) ||
						evt.getPropertyName().equals(IT_INTEGRATION_TIME_PROP_NAME) ||
						evt.getPropertyName().equals(IT_NUMBER_OF_ACCUMULATIONS_PROP_NAME)) {
					saveSingleSpectrumData();
				}
			}
		});
	}

	private void loadSingleSpectrumData() {
		SingleSpectrumUIModel singleSpectrumData = ClientConfig.EdeDataStore.INSTANCE.loadConfiguration(SINGLE_SPECTRUM_MODEL_DATA_STORE_KEY, SingleSpectrumUIModel.class);
		if (singleSpectrumData == null) {
			experimentDataModel = new ExperimentDataModel();
			return;
		}
		experimentDataModel = singleSpectrumData.getExperimentDataModel();
		this.setItIntegrationTime(singleSpectrumData.getItIntegrationTime());
		this.setItNumberOfAccumulations(singleSpectrumData.getItNumberOfAccumulations());

		// TODO For now just load sample_x and sample_y by default
		SampleStageMotors.INSTANCE.setSelectedMotors(new ExperimentMotorPostion[] {SampleStageMotors.scannables[0], SampleStageMotors.scannables[1]});
	}

	private void saveSingleSpectrumData() {
		ClientConfig.EdeDataStore.INSTANCE.saveConfiguration(SINGLE_SPECTRUM_MODEL_DATA_STORE_KEY, this);
	}

	private String buildScanCommand() {
		StringBuilder builder = new StringBuilder("from gda.scan.ede import EdeSingleExperiment; \n");
		int noOfAccumulations;
		if (experimentDataModel.isUseNoOfAccumulationsForI0()) {
			noOfAccumulations = experimentDataModel.getI0NumberOfAccumulations();
		} else {
			noOfAccumulations = itNumberOfAccumulations;
		}
		builder.append(
				String.format(SINGLE_JYTHON_DRIVER_OBJ + " = EdeSingleExperiment(%f, %d, %f, %d, mapToJava(%s), mapToJava(%s), \"%s\", \"%s\", \"%s\"); \n",
						ExperimentTimeHelper.fromMilliToSec(experimentDataModel.getI0IntegrationTime()),
						noOfAccumulations,
						ExperimentTimeHelper.fromMilliToSec(itIntegrationTime),
						itNumberOfAccumulations,
						SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.I0),
						SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.It),
						DetectorModel.INSTANCE.getCurrentDetector().getName(),
						DetectorModel.TOPUP_CHECKER,
						DetectorModel.SHUTTER_NAME));

		if (SampleStageMotors.INSTANCE.isUseIref()) {
			builder.append(String.format(SINGLE_JYTHON_DRIVER_OBJ + ".setIRefParameters(mapToJava(%s), %f, %d);",
					SampleStageMotors.INSTANCE.getFormattedSelectedPositions(ExperimentMotorPostionType.IRef),
					ExperimentTimeHelper.fromMilliToSec(experimentDataModel.getIrefIntegrationTime()), experimentDataModel.getIrefNoOfAccumulations()));
		}
		builder.append(String.format(SINGLE_JYTHON_DRIVER_OBJ + ".setFilenameTemplate(\"%s\");", filePefix));
		return builder.toString();
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
				if (SingleSpectrumUIModel.this.isScanning() && Jython.RUNNING == status.scanStatus) {
					monitor.subTask(scanJobName.getText());
					if (scanJobName.ordinal() <  ScanJobName.values().length - 1) {
						scanJobName = ScanJobName.values()[scanJobName.ordinal() + 1];
					}
				}
				if (SingleSpectrumUIModel.this.isScanning() && Jython.IDLE == status.scanStatus) {
					monitor.worked(1);
				}
			}
		}

		@Override
		protected IStatus run(IProgressMonitor monitor) {
			this.monitor = monitor;
			Display.getDefault().syncExec(new Runnable() {
				@Override
				public void run() {
					SingleSpectrumUIModel.this.setScanning(true);
				}
			});
			monitor.beginTask("Starting " + ScanJobName.values().length + " tasks.", ScanJobName.values().length);
			try {
				String command = buildScanCommand();
				logger.info("Sending command: " + command);

				InterfaceProvider.getCommandRunner().runCommand(command);
				// give the previous command a chance to run before calling doCollection()
				Thread.sleep(150);
				final String resultFileName = InterfaceProvider.getCommandRunner().evaluateCommand(SINGLE_JYTHON_DRIVER_OBJ + ".runExperiment()");
				if (resultFileName == null) {
					throw new Exception("Unable to do collection.");
				}
				Display.getDefault().syncExec(new Runnable() {
					@Override
					public void run() {
						try {
							SingleSpectrumUIModel.this.setFileName(resultFileName);
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
					SingleSpectrumUIModel.this.setScanning(false);
				}
			});
			return Status.OK_STATUS;
		}

		@Override
		protected void canceling() {
			doStop();
		}
	}

	public ExperimentDataModel getExperimentDataModel() {
		return experimentDataModel;
	}

	public void doCollection(boolean forExperiment) throws Exception {
		if (forExperiment) {
			filePefix = fileTemplate + "_%s";
		} else {
			filePefix = elementSymbol + "_cal" + "_%s";
		}
		if (DetectorModel.INSTANCE.getCurrentDetector() == null) {
			throw new DetectorUnavailableException();
		}
		job.schedule();
	}

	public void setCurrentElement(String elementSymbol) {
		this.elementSymbol = elementSymbol;
	}


	public boolean isSelectAlignmentStage() {
		return selectAlignmentStage;
	}

	public void setSelectAlignmentStage(boolean selectAlignmentStage) {
		this.firePropertyChange(ALIGNMENT_STAGE_SELECTION, this.selectAlignmentStage, this.selectAlignmentStage = selectAlignmentStage);
	}

	public void setFileName(String value) {
		firePropertyChange(FILE_NAME_PROP_NAME, fileName, fileName = value);
	}

	public String getFileName() {
		return fileName;
	}

	public String getFileTemplate() {
		return fileTemplate;
	}

	public void setFileTemplate(String fileTemplate) {
		this.firePropertyChange(FILE_TEMPLATE_PROP_NAME, this.fileTemplate, this.fileTemplate = fileTemplate);
	}

	public boolean isScanning() {
		return scanning;
	}

	protected void setScanning(boolean value) {
		this.firePropertyChange(SCANNING_PROP_NAME, scanning, scanning = value);
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


	public AlignmentStageScannable.Location getHoleLocationForAlignment() {
		return holeLocationForAlignment;
	}

	public AlignmentStageScannable.Location getFoilLocationForAlignment() {
		return foilLocationForAlignment;
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
