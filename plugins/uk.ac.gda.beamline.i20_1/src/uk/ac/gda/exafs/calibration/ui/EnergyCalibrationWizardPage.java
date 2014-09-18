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

import org.apache.commons.math3.util.Pair;
import org.dawb.common.ui.widgets.ActionBarWrapper;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.dawnsci.analysis.api.dataset.Slice;
import org.eclipse.dawnsci.analysis.dataset.impl.Dataset;
import org.eclipse.dawnsci.analysis.dataset.impl.DatasetUtils;
import org.eclipse.dawnsci.analysis.dataset.roi.LinearROI;
import org.eclipse.dawnsci.analysis.dataset.roi.RectangularROI;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.dawnsci.plotting.api.PlotType;
import org.eclipse.dawnsci.plotting.api.PlottingFactory;
import org.eclipse.dawnsci.plotting.api.region.IROIListener;
import org.eclipse.dawnsci.plotting.api.region.IRegion;
import org.eclipse.dawnsci.plotting.api.region.IRegion.RegionType;
import org.eclipse.dawnsci.plotting.api.region.ROIEvent;
import org.eclipse.dawnsci.plotting.api.trace.ILineTrace;
import org.eclipse.dawnsci.plotting.api.trace.ITrace;
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

import uk.ac.diamond.scisoft.spectroscopy.fitting.EdeCalibration;
import uk.ac.diamond.scisoft.spectroscopy.fitting.XafsFittingUtils;
import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.client.UIHelper;
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
	private IRegion referenceRegion;

	private IRegion[] edeDataPlottingRegions;
	private IRegion edeRegion;

	private Button runCalibrationButton;
	private Button manualCalibrationCheckButton;
	private Spinner polynomialFittingOrderSpinner;

	private IPlottingSystem refPlottingSystem;
	private IPlottingSystem edePlottingSystem;

	private final EnergyCalibration calibrationDataModel;
	private final CalibrationEnergyData edeCalibrationDataModel;
	private final CalibrationEnergyData refCalibrationDataModel;
	private final XafsFittingUtils xafsFittingUtils = new XafsFittingUtils();

	private Text polynomialValueText;
	private Text goodnessOfFitValueText;

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
			Composite groupParent = createDataPlotting(container, "Reference data", refCalibrationDataModel, refPlottingSystem);
			referenceDataPlottingRegions = createManualCalibrationMarkersAsRegions(refPlottingSystem, refCalibrationDataModel);
			referenceRegion = createSelectedDataRegion("data_region", refPlottingSystem);
			setupRegions(refCalibrationDataModel, referenceDataPlottingRegions, referenceRegion, refPlottingSystem);

			registerRegionChanges(groupParent, referenceRegion);

			edePlottingSystem = PlottingFactory.createPlottingSystem();
			groupParent = createDataPlotting(container, "EDE scan data", edeCalibrationDataModel, edePlottingSystem);
			edeDataPlottingRegions = createManualCalibrationMarkersAsRegions(edePlottingSystem, edeCalibrationDataModel);
			edeRegion = createSelectedDataRegion("data_region", edePlottingSystem);
			setupRegions(edeCalibrationDataModel, edeDataPlottingRegions, edeRegion, edePlottingSystem);

			registerRegionChanges(groupParent, edeRegion);

		} catch (Exception e) {
			logger.error("Unable to create controls", e);
		}
		createCalibrationDetails(container);
		setControl(container);
		setPageComplete(true);
	}

	private void registerRegionChanges(Composite groupParent, IRegion referenceRegion) {
		Composite parent = new Composite(groupParent, SWT.None);
		parent.setLayoutData(new GridData(SWT.FILL, SWT.END, true, false));
		parent.setLayout(UIHelper.createGridLayoutWithNoMargin(2, true));
		final Label startValueLabel = new Label(parent, SWT.None);
		startValueLabel.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		final Label endValueLabel = new Label(parent, SWT.None);
		endValueLabel.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		referenceRegion.addROIListener(new IROIListener() {
			@Override
			public void roiDragged(ROIEvent evt) {
				updateValues(evt);
			}
			@Override
			public void roiChanged(ROIEvent evt) {
				updateValues(evt);
			}
			private void updateValues(ROIEvent evt) {
				double start = ((RectangularROI) evt.getROI()).getPoint()[0];
				double end = start + ((RectangularROI) evt.getROI()).getLength(0);
				startValueLabel.setText(DataHelper.roundDoubletoString(start, 3));
				endValueLabel.setText(DataHelper.roundDoubletoString(end, 3));
			}
			@Override
			public void roiSelected(ROIEvent evt) {}
		});
	}

	private IRegion createSelectedDataRegion(String name, IPlottingSystem plottingSystem) throws Exception {
		IRegion ref = plottingSystem.createRegion(name, IRegion.RegionType.XAXIS);
		ref.setRegionColor(ColorConstants.lightGray);
		ref.setPlotType(plottingSystem.getPlotType());
		ref.setShowPosition(true);
		plottingSystem.addRegion(ref);
		return ref;
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

	private void setupRegions(final CalibrationEnergyData calibrationDataModel,
			final IRegion[] dataPlottingRegions, final IRegion selectionRegion, final IPlottingSystem plottingSystem) {
		calibrationDataModel.addPropertyChangeListener(new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				if (evt.getPropertyName().equals(CalibrationEnergyData.FILE_NAME_PROP_NAME)) {
					updateRegions(calibrationDataModel, dataPlottingRegions, selectionRegion);
				}
				plottingSystem.repaint(false);
			}
		});
		updateRegions(calibrationDataModel, dataPlottingRegions, selectionRegion);
		plottingSystem.repaint(false);
	}

	private void updateRegions(final CalibrationEnergyData calibrationDataModel, final IRegion[] dataPlottingRegions,
			final IRegion selectionRegion) {
		if (calibrationDataModel.getFileName() != null) {
			for (int i = 0; i < dataPlottingRegions.length; i++) {
				double index = calibrationDataModel.getReferencePoints()[i];
				dataPlottingRegions[i].setROI(new LinearROI(new double[] { index, 0 }, new double[] { index, 1 }));
			}
			selectionRegion.setROI(new RectangularROI(calibrationDataModel.getReferencePoints()[0], 10, calibrationDataModel.getReferencePoints()[2] - calibrationDataModel.getReferencePoints()[0], 1, 0));
			selectionRegion.setVisible(true);
		}
	}

	private IRegion[] createManualCalibrationMarkersAsRegions(IPlottingSystem plottingSystem, CalibrationEnergyData calibrationDataModel) throws Exception {
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

	private IRegion makeVertLine(String name, IPlottingSystem plottingSystem, double pos, Color color) throws Exception {
		IRegion ref = plottingSystem.createRegion(name, RegionType.XAXIS_LINE);
		ref.setRegionColor(color);
		ref.setLineWidth(3);
		ref.setUserRegion(false);
		plottingSystem.addRegion(ref);
		ref.setVisible(false);
		ref.setROI(new LinearROI(new double[] { pos, 0 }, new double[] { pos, 1 }));
		return ref;
	}

	private Composite createDataPlotting(Composite container, String title, CalibrationEnergyData calibrationDataModel, IPlottingSystem plottingSystem) {
		Group group = new Group(container, SWT.None);
		group.setText(title);
		group.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		group.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));

		createFileBrowsingComposite(group, calibrationDataModel);
		createPlottingComposite(group, calibrationDataModel, plottingSystem);
		return group;
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
			plottingSystem.getSelectedXAxis().setAxisAutoscaleTight(true);
			plottingSystem.getSelectedYAxis().setAxisAutoscaleTight(true);
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
		plottingSystem.getSelectedXAxis().setRange(calibrationDataModel.getStartEnergy(), calibrationDataModel.getEndEnergy());
		ILineTrace trace = plottingSystem.createLineTrace(calibrationDataModel.getEdeDataset().getName());
		trace.setData(calibrationDataModel.getRefEnergyDataset(), calibrationDataModel.getEdeDataset());
		if (calibrationDataModel instanceof SampleData) {
			trace.setTraceColor(ColorConstants.red);
			plottingSystem.getSelectedXAxis().setTitle("Strip");
		} else {
			trace.setTraceColor(ColorConstants.blue);
			plottingSystem.getSelectedXAxis().setTitle("Energy");
		}
		plottingSystem.addTrace(trace);
		plottingSystem.repaint();
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

		Label goodnessOfFit = new Label(calibrationDetailsComposite, SWT.None);
		goodnessOfFit.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));
		goodnessOfFit.setText("Goodness of fit");
		goodnessOfFitValueText = new Text(calibrationDetailsComposite, SWT.BORDER);
		gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		goodnessOfFitValueText.setEditable(false);
		goodnessOfFitValueText.setLayoutData(gridData);

		dataBindingCtx.bindValue(
				WidgetProperties.text().observe(polynomialValueText),
				BeanProperties.value(CalibrationDetails.CALIBRATION_RESULT_PROP_NAME).observe(calibrationDataModel.getCalibrationDetails()),
				null,
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						String poly = (String) value;
						if (!poly.isEmpty()) {
							referenceRegion.setROI(new RectangularROI(calibrationDataModel.getCalibrationDetails().getRefRangeStart(), 10, calibrationDataModel.getCalibrationDetails().getRefRangeEnd(), 1, 0));
							edeRegion.setROI(new RectangularROI(calibrationDataModel.getCalibrationDetails().getSampleRangeStart(), 10, calibrationDataModel.getCalibrationDetails().getSampleRangeEnd(), 1, 0));
							goodnessOfFitValueText.setText(DataHelper.roundDoubletoString(calibrationDataModel.getCalibrationDetails().getGoodnessOfFit(), 3));
							poly = calibrationDataModel.getCalibrationDetails().getFormattedPolinormal();
						}
						return super.doSet(observableValue, poly);
					}
				});

		clearCalibrationButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				refPlottingSystem.clear();
				runCalibrationButton.setEnabled(true);
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

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(goodnessOfFitValueText),
				BeanProperties.value(EnergyCalibration.DATA_READY_PROP_NAME).observe(calibrationDataModel));
	}

	private final UpdateValueStrategy refUpdateValueStrategy = new UpdateValueStrategy() {
		@Override
		protected IStatus doSet(IObservableValue observableValue, Object value) {
			IStatus result = super.doSet(observableValue, value);
			boolean manualChecked = (boolean) value;
			for (int i = 0; i < referenceDataPlottingRegions.length; i++) {
				referenceDataPlottingRegions[i].setVisible(manualChecked);
			}
			if (manualChecked) {
				referenceRegion.toBack();
			} else {
				referenceRegion.toFront();
			}
			referenceRegion.setMobile(!manualChecked);
			return result;
		}
	};

	private final UpdateValueStrategy edeUpdateValueStrategy = new UpdateValueStrategy() {
		@Override
		protected IStatus doSet(IObservableValue observableValue, Object value) {
			IStatus result = super.doSet(observableValue, value);
			boolean manualChecked = (boolean) value;
			for (int i = 0; i < edeDataPlottingRegions.length; i++) {
				edeDataPlottingRegions[i].setVisible(manualChecked);
			}
			if (manualChecked) {
				edeRegion.toBack();
			} else {
				edeRegion.toFront();
			}
			edeRegion.setMobile(!manualChecked);
			return result;
		}
	};

	private void runEdeCalibration() {
		try {
			refPlottingSystem.clear();
			loadPlot(refCalibrationDataModel, refPlottingSystem);
			final EdeCalibration edeCalibration = new EdeCalibration();
			Dataset[] refDatasets = selectDataRange(refPlottingSystem, referenceRegion);
			final Dataset refEnergySlice = refDatasets[0];
			final Dataset refSpectrumSlice = refDatasets[1];
			Dataset[] edeDatasets = selectDataRange(edePlottingSystem, edeRegion);
			final Dataset edeIdxSlice = edeDatasets[0];
			final Dataset edeSpectrumSlice = edeDatasets[1];
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
					final Dataset resEnergyDataset = edeCalibration.calibrateEdeChannels(edeIdxSlice);
					Display.getDefault().syncExec(new Runnable() {

						@Override
						public void run() {
							try {
								refPlottingSystem.clear();

								xafsFittingUtils.setPostEdgeOrder(1);
								xafsFittingUtils.setPreEdgeGap(15);

								ILineTrace refTrace = refPlottingSystem.createLineTrace("Ref");
								Dataset[] exafs = xafsFittingUtils.getNormalisedIntensityAndSpline(refEnergySlice, refSpectrumSlice);
								exafs[0].setName("ref-energy");
								exafs[1].setName("ref-spectrum");
								exafs[2].setName("ref-spectrum-spline");
								refTrace.setData(exafs[0], exafs[1]);
								refTrace.setTraceColor(ColorConstants.blue);
								refPlottingSystem.addTrace(refTrace);

								// TODO Show spline on/off
								//								ILineTrace refTraceSpline = refPlottingSystem.createLineTrace("RefSpline");
								//								refTraceSpline.setData(exafs[0], exafs[2]);
								//								refTraceSpline.setTraceColor(ColorConstants.blue);
								//								refPlottingSystem.addTrace(refTraceSpline);

								ILineTrace edeTrace = refPlottingSystem.createLineTrace(EDE_OVERLAY_TRACE_NAME);

								Dataset[] exafsede = xafsFittingUtils.getNormalisedIntensityAndSpline(resEnergyDataset, edeSpectrumSlice);
								exafsede[0].setName("sample-energy");
								exafsede[1].setName("sample-spectrum");
								exafsede[2].setName("sample-spectrum-spline");
								edeTrace.setData(exafsede[0], exafsede[1]);
								edeTrace.setTraceColor(ColorConstants.red);
								refPlottingSystem.addTrace(edeTrace);

								// TODO Show spline on/off
								//								ILineTrace edeTraceSpline = refPlottingSystem.createLineTrace("EdeSpline");
								//								edeTraceSpline.setData(exafsede[0], exafsede[2]);
								//								edeTraceSpline.setTraceColor(ColorConstants.red);
								//								refPlottingSystem.addTrace(edeTraceSpline);

								refPlottingSystem.repaint();

								calibrationDataModel.getCalibrationDetails().setRefRangeStart(((RectangularROI) referenceRegion.getROI()).getPoint()[0]);
								calibrationDataModel.getCalibrationDetails().setRefRangeEnd(((RectangularROI) referenceRegion.getROI()).getLength(0));
								calibrationDataModel.getCalibrationDetails().setSampleRangeStart(((RectangularROI) edeRegion.getROI()).getPoint()[0]);
								calibrationDataModel.getCalibrationDetails().setSampleRanceEnd(((RectangularROI) edeRegion.getROI()).getLength(0));
								calibrationDataModel.getCalibrationDetails().setCalibrationResult(edeCalibration.getEdeCalibrationPolynomial());
								calibrationDataModel.getCalibrationDetails().setGoodnessOfFit(edeCalibration.getGoodnessOfFit());

							} catch(Exception e) {
								UIHelper.showError("Unable to run calibration", e.getMessage());
							} finally {
								runCalibrationButton.setEnabled(true);
							}
						}
					});
					return Status.OK_STATUS;
				}
			};
			job.schedule();
		} catch(Exception e) {
			UIHelper.showError("Unable to run calibration", e.getMessage());
		} finally {
			runCalibrationButton.setEnabled(true);
		}
	}

	private Dataset[] selectDataRange(IPlottingSystem plottingSystemRef, IRegion selectedRegion) {
		final Dataset dataE, dataI;
		double lowerAxis = ((RectangularROI) selectedRegion.getROI()).getPoint()[0];
		double upperAxis = lowerAxis + ((RectangularROI) selectedRegion.getROI()).getLength(0);
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
		Dataset dataXDataset = (Dataset)dataTrace.getXData();
		int idxLower = Math.min(dataXDataset.getSize() - 1, DatasetUtils.findIndexGreaterThanOrEqualTo(dataXDataset, lowerAxis));
		int idxUpper = Math.min(dataXDataset.getSize() - 1, DatasetUtils.findIndexGreaterThanOrEqualTo(dataXDataset, upperAxis));
		if (idxLower == idxUpper) {
			UIHelper.showWarning("Unable to process data", "Invalid data range. Please check plot settings");
			return null;
		}
		dataE = dataXDataset.getSlice(new Slice(idxLower, idxUpper));
		dataI = ((Dataset)dataTrace.getYData()).getSlice(new Slice(idxLower, idxUpper));
		return new Dataset[] {dataE, dataI};
	}

}
