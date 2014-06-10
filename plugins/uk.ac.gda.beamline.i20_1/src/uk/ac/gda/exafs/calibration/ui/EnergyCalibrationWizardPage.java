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

package uk.ac.gda.exafs.calibration.ui;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.File;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import org.apache.commons.math3.util.Pair;
import org.dawb.common.ui.widgets.ActionBarWrapper;
import org.dawnsci.plotting.api.IPlottingSystem;
import org.dawnsci.plotting.api.PlotType;
import org.dawnsci.plotting.api.PlottingFactory;
import org.dawnsci.plotting.api.axis.IAxis;
import org.dawnsci.plotting.api.region.IROIListener;
import org.dawnsci.plotting.api.region.IRegion;
import org.dawnsci.plotting.api.region.IRegion.RegionType;
import org.dawnsci.plotting.api.region.IRegionSystem;
import org.dawnsci.plotting.api.region.ROIEvent;
import org.dawnsci.plotting.api.trace.ILineTrace;
import org.dawnsci.plotting.api.trace.ITrace;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.draw2d.ColorConstants;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.wizard.WizardPage;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.FileDialog;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Spinner;
import org.eclipse.swt.widgets.Text;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.DatasetUtils;
import uk.ac.diamond.scisoft.analysis.dataset.IDataset;
import uk.ac.diamond.scisoft.analysis.dataset.Slice;
import uk.ac.diamond.scisoft.analysis.roi.LinearROI;
import uk.ac.diamond.scisoft.spectroscopy.fitting.EdeCalibration;
import uk.ac.gda.common.rcp.UIHelper;
import uk.ac.gda.exafs.calibration.data.CalibrationDetails;
import uk.ac.gda.exafs.calibration.data.CalibrationEnergyData;
import uk.ac.gda.exafs.calibration.data.EnergyCalibration;
import uk.ac.gda.exafs.calibration.data.ReferenceData;
import uk.ac.gda.exafs.calibration.data.SampleData;
import uk.ac.gda.exafs.data.ClientConfig;

public class EnergyCalibrationWizardPage extends WizardPage {

	private static final Logger logger = LoggerFactory.getLogger(EnergyCalibrationWizardPage.class);

	private static final String EDE_OVERLAY_TRACE_NAME = "Ede";

	private final DataBindingContext dataBindingCtx = new DataBindingContext();
	private IRegion[] referenceDataPlottingRegions;
	private IRegion[] edeDataPlottingRegions;

	private Button runCalibrationButton;
	private Button manualCalibrationCheckButton;
	private Spinner polynomialFittingOrderSpinner;

	private IPlottingSystem refPlottingSystem;
	private IPlottingSystem edePlottingSystem;

	private final EnergyCalibration calibrationDataModel;
	private final CalibrationEnergyData edeCalibrationDataModel;
	private final CalibrationEnergyData refCalibrationDataModel;

	private Text polynomialValueText;

	protected EnergyCalibrationWizardPage(EnergyCalibration calibrationDataModel) {
		super("Energy calibration");
		this.calibrationDataModel = calibrationDataModel;
		refCalibrationDataModel = calibrationDataModel.getRefData();
		edeCalibrationDataModel = calibrationDataModel.getEdeData();
		this.setTitle("Energy calibration");
		this.setDescription("Energy calibration using reference data");
	}

	@Override
	public void createControl(Composite parent) {
		Composite container = new Composite(parent, SWT.NONE);
		container.setLayout(new GridLayout(2, true));
		try {
			refPlottingSystem = PlottingFactory.createPlottingSystem();
			createDataPlotting(container, "Reference data", refCalibrationDataModel, refPlottingSystem);
			referenceDataPlottingRegions = createRegions(refPlottingSystem, refCalibrationDataModel);
			registerRegionShowHide(refCalibrationDataModel, referenceDataPlottingRegions, refPlottingSystem);

			edePlottingSystem = PlottingFactory.createPlottingSystem();
			createDataPlotting(container, "EDE scan data", edeCalibrationDataModel, edePlottingSystem);
			edeDataPlottingRegions = createRegions(edePlottingSystem, edeCalibrationDataModel);
			registerRegionShowHide(edeCalibrationDataModel, edeDataPlottingRegions, edePlottingSystem);

		} catch (Exception e) {
			logger.error("Unable to create controls", e);
		}
		createCalibrationDetails(container);
		setControl(container);
		setPageComplete(true);
	}


	@Override
	public void dispose() {
		if (refPlottingSystem != null && !refPlottingSystem.isDisposed()) {
			refPlottingSystem.dispose();
		}
		if (edePlottingSystem != null && !edePlottingSystem.isDisposed()) {
			edePlottingSystem.dispose();
		}
		calibrationDataModel.clearListeners();
		refCalibrationDataModel.clearListeners();
		edeCalibrationDataModel.clearListeners();
		super.dispose();
	}

	private void registerRegionShowHide(final CalibrationEnergyData calibrationDataModel,
			final IRegion[] dataPlottingRegions, final IPlottingSystem plottingSystem) {
		calibrationDataModel.addPropertyChangeListener(new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if (evt.getPropertyName().equals(CalibrationEnergyData.FILE_NAME_PROP_NAME)) {
					for (int i = 0; i < dataPlottingRegions.length; i++) {
						double index = calibrationDataModel.getReferencePoints()[i];
						dataPlottingRegions[i].setROI(new LinearROI(new double[] { index, 0 }, new double[] { index, 1 }));
					}
				}
				plottingSystem.repaint(false);
			}
		});
	}

	private IRegion[] createRegions(IPlottingSystem plottingSystem, CalibrationEnergyData calibrationDataModel) throws Exception {
		IRegion[] dataPlottingRegions = new IRegion[3];

		dataPlottingRegions[0] = makeVertLine("0", plottingSystem, calibrationDataModel.getReferencePoints()[0], ColorConstants.red);
		dataPlottingRegions[0].addROIListener(referencePointListener);
		dataPlottingRegions[0].setUserObject(calibrationDataModel);

		dataPlottingRegions[1] = makeVertLine("1", plottingSystem, calibrationDataModel.getReferencePoints()[1], ColorConstants.green);
		dataPlottingRegions[1].addROIListener(referencePointListener);
		dataPlottingRegions[1].setUserObject(calibrationDataModel);

		dataPlottingRegions[2] = makeVertLine("2", plottingSystem, calibrationDataModel.getReferencePoints()[2], ColorConstants.blue);
		dataPlottingRegions[2].addROIListener(referencePointListener);
		dataPlottingRegions[2].setUserObject(calibrationDataModel);
		return dataPlottingRegions;
	}

	private final IROIListener referencePointListener = new IROIListener() {
		boolean dragged = false;
		@Override
		public void roiDragged(ROIEvent evt) {
			dragged = true;
		}

		@Override
		public void roiChanged(ROIEvent evt) {
			if (!dragged) {
				return;
			}
			CalibrationEnergyData model = (CalibrationEnergyData) ((IRegion) evt.getSource()).getUserObject();
			if (model instanceof ReferenceData) {
				model.setReferencePoints(
						referenceDataPlottingRegions[0].getROI().getPointX(),
						referenceDataPlottingRegions[1].getROI().getPointX(),
						referenceDataPlottingRegions[2].getROI().getPointX());
			} else if (model instanceof SampleData) {
				model.setReferencePoints(
						edeDataPlottingRegions[0].getROI().getPointX(),
						edeDataPlottingRegions[1].getROI().getPointX(),
						edeDataPlottingRegions[2].getROI().getPointX());
			}
			dragged = false;
		}

		@Override
		public void roiSelected(ROIEvent evt) {}
	};


	private IRegion makeVertLine(String name, IRegionSystem plottingSystem, double pos, Color color) throws Exception {
		IRegion ref = plottingSystem.createRegion(name, RegionType.XAXIS_LINE);
		ref.setRegionColor(color);
		ref.setLineWidth(3);
		ref.setMobile(false);
		ref.setVisible(false);
		ref.setUserRegion(false);
		plottingSystem.addRegion(ref);
		ref.setROI(new LinearROI(new double[] { pos, 0 }, new double[] { pos, 1 }));
		return ref;
	}

	private void createDataPlotting(Composite container, String title, CalibrationEnergyData calibrationDataModel, IPlottingSystem plottingSystem) {
		Group group = new Group(container, SWT.None);
		group.setText(title);
		group.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		group.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));

		createFileBrowsingComposite(group, calibrationDataModel);
		createPlottingComposite(group, calibrationDataModel, plottingSystem);
	}

	private void createPlottingComposite(Group group, final CalibrationEnergyData calibrationDataModel, final IPlottingSystem plottingSystem) {
		Composite plotParent = new Composite(group, SWT.None);
		plotParent.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		plotParent.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		ActionBarWrapper actionbarWrapper = ActionBarWrapper.createActionBars(plotParent, null);
		try {
			plottingSystem.createPlotPart(plotParent,
					getTitle(),
					actionbarWrapper,
					PlotType.XY,
					null);
			plottingSystem.getPlotComposite().setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		} catch (Exception e) {
			logger.error("Unable to create plotting system", e);
		}
		calibrationDataModel.addPropertyChangeListener(CalibrationEnergyData.FILE_NAME_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				plottingSystem.clear();
				if (evt.getNewValue() != null) {
					loadPlot(calibrationDataModel, plottingSystem);
				}
			}
		});
		if (calibrationDataModel.getFileName() != null) {
			loadPlot(calibrationDataModel, plottingSystem);
		}
	}

	private void loadPlot(final CalibrationEnergyData calibrationDataModel, final IPlottingSystem plottingSystem) {
		List<IDataset> spectra = new ArrayList<IDataset>(1);
		spectra.add(calibrationDataModel.getEdeDataset());
		plottingSystem.getSelectedXAxis().setRange(calibrationDataModel.getStartEnergy(), calibrationDataModel.getEndEnergy());
		plottingSystem.createPlot1D(calibrationDataModel.getRefEnergyDataset(), spectra, new NullProgressMonitor());
	}

	private void createFileBrowsingComposite(Group group, final CalibrationEnergyData calibrationDataModel) {
		final Composite dataComposite = new Composite(group, SWT.None);
		dataComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		dataComposite.setLayout(new GridLayout(3, false));

		final Label lblDataFile = new Label(dataComposite, SWT.NONE);
		lblDataFile.setText("File");
		lblDataFile.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		final Text lblFileValue = new Text(dataComposite, SWT.None);
		lblFileValue.setEditable(false);
		GridData gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gridData.widthHint = 140;
		lblFileValue.setLayoutData(gridData);

		final Button loadDataFileButton = new Button(dataComposite, SWT.None);
		loadDataFileButton.setText("Browse");
		loadDataFileButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));
		loadDataFileButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				showDataFileDialog(loadDataFileButton.getShell(), calibrationDataModel);
			}
		});
		dataBindingCtx.bindValue(
				WidgetProperties.text().observe(lblFileValue),
				BeanProperties.value(CalibrationEnergyData.FILE_NAME_PROP_NAME).observe(calibrationDataModel));
	}

	private void showDataFileDialog(final Shell shell, CalibrationEnergyData dataModel) {
		FileDialog fileDialog = new FileDialog(shell, SWT.OPEN);
		fileDialog.setText("Load data");
		fileDialog.setFilterPath(ClientConfig.DEFAULT_DATA_PATH);
		String selected = fileDialog.open();
		if (selected != null) {
			try {
				File refFile = new File(selected);
				if (refFile.exists() && refFile.canRead()) {
					if (dataModel instanceof ReferenceData) {
						calibrationDataModel.setRefData(selected);
					} else if (dataModel instanceof SampleData) {
						calibrationDataModel.setEdeData(selected);
					}
				} else {
					throw new Exception("Unable to read " + selected + ".");
				}
			} catch (Exception e) {
				UIHelper.showError("Error setting data model", e.getMessage());
			}
		}
	}

	private void createCalibrationDetails(Composite container) {
		final Composite calibrationDetailsComposite = new Composite(container, SWT.None);
		GridData gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gridData.horizontalSpan = 2;
		calibrationDetailsComposite.setLayoutData(gridData);
		calibrationDetailsComposite.setLayout(new GridLayout(5, false));
		final Label lblPolyOrder = new Label(calibrationDetailsComposite, SWT.NONE);
		lblPolyOrder.setText("Polynomial order");
		lblPolyOrder.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		polynomialFittingOrderSpinner = new Spinner(calibrationDetailsComposite, SWT.None);
		polynomialFittingOrderSpinner.setMinimum(1);
		polynomialFittingOrderSpinner.setMaximum(5);
		polynomialFittingOrderSpinner.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(polynomialFittingOrderSpinner),
				BeanProperties.value(EnergyCalibration.POLYNOMIAL_ORDER_PROP_NAME).observe(calibrationDataModel));

		manualCalibrationCheckButton = new Button(calibrationDetailsComposite, SWT.CHECK);
		manualCalibrationCheckButton.setText("Manual calibration");
		manualCalibrationCheckButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		runCalibrationButton = new Button(calibrationDetailsComposite, SWT.None);
		runCalibrationButton.setText("Run EDE Calibration");
		gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		runCalibrationButton.setLayoutData(gridData);

		runCalibrationButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				runEdeCalibration();
			}
		});

		Button clearCalibrationButton = new Button(calibrationDetailsComposite, SWT.None);
		clearCalibrationButton.setText("Clear");
		gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		clearCalibrationButton.setLayoutData(gridData);

		Label polynomialValueLabel = new Label(calibrationDetailsComposite, SWT.None);
		polynomialValueLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		polynomialValueLabel.setText("Polynomial value");

		polynomialValueText = new Text(calibrationDetailsComposite, SWT.BORDER);
		gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gridData.horizontalSpan = 4;
		polynomialValueText.setEditable(false);
		polynomialValueText.setLayoutData(gridData);

		dataBindingCtx.bindValue(
				WidgetProperties.text().observe(polynomialValueText),
				BeanProperties.value(CalibrationDetails.CALIBRATION_RESULT_PROP_NAME).observe(calibrationDataModel.getCalibrationDetails()));

		clearCalibrationButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				refPlottingSystem.clear();
				loadPlot(refCalibrationDataModel, refPlottingSystem);
			}
		});

		dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(manualCalibrationCheckButton),
				BeanProperties.value(CalibrationEnergyData.MANUAL_CALIBRATION_PROP_NAME).observe(refCalibrationDataModel),
				refUpdateValueStrategy, refUpdateValueStrategy);

		dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(manualCalibrationCheckButton),
				BeanProperties.value(CalibrationEnergyData.MANUAL_CALIBRATION_PROP_NAME).observe(edeCalibrationDataModel),
				edeUpdateValueStrategy, edeUpdateValueStrategy);

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(manualCalibrationCheckButton),
				BeanProperties.value(EnergyCalibration.DATA_READY_PROP_NAME).observe(calibrationDataModel));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(runCalibrationButton),
				BeanProperties.value(EnergyCalibration.DATA_READY_PROP_NAME).observe(calibrationDataModel));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(clearCalibrationButton),
				BeanProperties.value(EnergyCalibration.DATA_READY_PROP_NAME).observe(calibrationDataModel));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(polynomialValueText),
				BeanProperties.value(EnergyCalibration.DATA_READY_PROP_NAME).observe(calibrationDataModel));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(polynomialFittingOrderSpinner),
				BeanProperties.value(EnergyCalibration.DATA_READY_PROP_NAME).observe(calibrationDataModel));
	}

	private final UpdateValueStrategy refUpdateValueStrategy = new UpdateValueStrategy() {
		@Override
		protected IStatus doSet(IObservableValue observableValue, Object value) {
			IStatus result = super.doSet(observableValue, value);
			for (int i = 0; i < referenceDataPlottingRegions.length; i++) {
				referenceDataPlottingRegions[i].setVisible((boolean) value);
			}
			return result;
		}
	};

	private final UpdateValueStrategy edeUpdateValueStrategy = new UpdateValueStrategy() {
		@Override
		protected IStatus doSet(IObservableValue observableValue, Object value) {
			IStatus result = super.doSet(observableValue, value);
			for (int i = 0; i < edeDataPlottingRegions.length; i++) {
				edeDataPlottingRegions[i].setVisible((boolean) value);
			}
			return result;
		}
	};

	private void runEdeCalibration() {
		try {
			final EdeCalibration edeCalibration = new EdeCalibration();
			AbstractDataset[] refDatasets = selectDataRange(refPlottingSystem);
			final AbstractDataset refEnergySlice = refDatasets[0];
			final AbstractDataset refSpectrumSlice = refDatasets[1];
			AbstractDataset[] edeDatasets = selectDataRange(edePlottingSystem);
			final AbstractDataset edeIdxSlice = edeDatasets[0];
			final AbstractDataset edeSpectrumSlice = edeDatasets[1];
			edeCalibration.setMaxEdeChannel(edeCalibrationDataModel.getEdeDataset().getSize() - 1);
			edeCalibration.setFitOrder(polynomialFittingOrderSpinner.getSelection());
			edeCalibration.setReferenceData(refEnergySlice, refSpectrumSlice);
			edeCalibration.setEdeSpectrum(edeIdxSlice, edeSpectrumSlice);

			double ref1e, ref2e, ref3e;
			double ede1e, ede2e, ede3e;
			if (manualCalibrationCheckButton.getSelection()) {
				ref1e = refCalibrationDataModel.getReferencePoints()[0];
				ref2e = refCalibrationDataModel.getReferencePoints()[1];
				ref3e = refCalibrationDataModel.getReferencePoints()[2];

				ede1e = edeCalibrationDataModel.getReferencePoints()[0];
				ede2e = edeCalibrationDataModel.getReferencePoints()[1];
				ede3e = edeCalibrationDataModel.getReferencePoints()[2];

				final Pair<Double, Double> refPoint1 = new Pair<Double, Double>(ref1e, ede1e);
				final Pair<Double, Double> refPoint2 = new Pair<Double, Double>(ref2e, ede2e);
				final Pair<Double, Double> refPoint3 = new Pair<Double, Double>(ref3e, ede3e);

				ArrayList<Pair<Double, Double>> refPositions = new ArrayList<Pair<Double, Double>>();
				refPositions.add(refPoint1);
				refPositions.add(refPoint2);
				refPositions.add(refPoint3);
				edeCalibration.setReferencePositions(refPositions);
			}
			Job job = new Job("EDE calibration") {
				@Override
				protected void canceling() {
					super.canceling();
					Display.getDefault().syncExec(new Runnable() {
						@Override
						public void run() {
							runCalibrationButton.setEnabled(true);
						}
					});
				}

				@Override
				protected IStatus run(IProgressMonitor monitor) {
					Display.getDefault().syncExec(new Runnable() {
						@Override
						public void run() {
							runCalibrationButton.setEnabled(false);
						}
					});

					edeCalibration.calibrate(true);
					final AbstractDataset resEnergyDataset = edeCalibration.calibrateEdeChannels(edeIdxSlice);
					Display.getDefault().syncExec(new Runnable() {

						@Override
						public void run() {
							refPlottingSystem.clear();

							ILineTrace refTrace = refPlottingSystem.createLineTrace("Ref");
							refTrace.setData(refEnergySlice, refSpectrumSlice);

							refTrace.setTraceColor(ColorConstants.blue);
							refPlottingSystem.addTrace(refTrace);

							ILineTrace edeTrace = refPlottingSystem.createLineTrace(EDE_OVERLAY_TRACE_NAME);
							edeTrace.setData(resEnergyDataset, edeSpectrumSlice);
							edeTrace.setTraceColor(ColorConstants.red);
							refPlottingSystem.addTrace(edeTrace);

							refPlottingSystem.repaint();

							calibrationDataModel.getCalibrationDetails().setCalibrationResult(edeCalibration.getEdeCalibrationPolynomial());

							runCalibrationButton.setEnabled(true);
						}
					});
					return Status.OK_STATUS;
				}
			};
			job.schedule();
		} catch(Exception e) {
			UIHelper.showError("Unable to run calibration", e.getMessage());
		}
	}

	private AbstractDataset[] selectDataRange(IPlottingSystem plottingSystemRef) {
		final AbstractDataset dataE, dataI;
		IAxis selAxis = plottingSystemRef.getSelectedXAxis();
		double lowerAxis = selAxis.getLower();
		double upperAxis = selAxis.getUpper();
		Collection<ITrace> traces = plottingSystemRef.getTraces();
		ITrace tmpTrace = null;
		if (traces != null && !(traces.isEmpty())) {
			tmpTrace = traces.iterator().next();
		}

		if (!(tmpTrace instanceof ILineTrace)) {
			UIHelper.showWarning("Unable to process data", "Invalid input data. Please plot absorption spectrum data.");
			return null;
		}
		ILineTrace dataTrace = (ILineTrace) tmpTrace;
		AbstractDataset dataXDataset = (AbstractDataset)dataTrace.getXData();
		int idxLower = Math.min(dataXDataset.getSize() - 1, DatasetUtils.findIndexGreaterThanOrEqualTo(dataXDataset, lowerAxis));
		int idxUpper = Math.min(dataXDataset.getSize() - 1, DatasetUtils.findIndexGreaterThanOrEqualTo(dataXDataset, upperAxis));
		if (idxLower == idxUpper) {
			UIHelper.showWarning("Unable to process data", "Invalid data range. Please check plot settings");
			return null;
		}
		dataE = dataXDataset.getSlice(new Slice(idxLower, idxUpper));
		dataI = ((AbstractDataset)dataTrace.getYData()).getSlice(new Slice(idxLower, idxUpper));
		return new AbstractDataset[] {dataE, dataI};
	}

}