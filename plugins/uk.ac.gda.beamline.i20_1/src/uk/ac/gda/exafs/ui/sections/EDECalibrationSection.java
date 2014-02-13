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

package uk.ac.gda.exafs.ui.sections;

import gda.device.DeviceException;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.File;
import java.util.ArrayList;
import java.util.Collection;

import org.apache.commons.math3.analysis.polynomials.PolynomialFunction;
import org.apache.commons.math3.util.Pair;
import org.dawnsci.plotting.api.IPlottingSystem;
import org.dawnsci.plotting.api.PlottingFactory;
import org.dawnsci.plotting.api.axis.IAxis;
import org.dawnsci.plotting.api.trace.ILineTrace;
import org.dawnsci.plotting.api.trace.ITrace;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.draw2d.ColorConstants;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.FileDialog;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Spinner;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.DatasetUtils;
import uk.ac.diamond.scisoft.analysis.dataset.Slice;
import uk.ac.diamond.scisoft.spectroscopy.fitting.EdeCalibration;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.DetectorModel.EnergyCalibrationSetObserver;
import uk.ac.gda.exafs.data.EdeCalibrationModel;
import uk.ac.gda.exafs.data.EdeCalibrationModel.ReferenceCalibrationDataModel;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.perspectives.AlignmentPerspective;
import uk.ac.gda.exafs.ui.views.CalibrationPlotViewer;
import uk.ac.gda.exafs.ui.views.EdeManualCalibrationPlotView;

public class EDECalibrationSection extends ResourceComposite {

	private final FormToolkit toolkit;

	private static final Logger logger = LoggerFactory.getLogger(EDECalibrationSection.class);
	private final DataBindingContext dataBindingCtx = new DataBindingContext();
	private Section section;
	private Button manualCalibrationCheckButton;
	private Label polynomialValueLbl;
	private Button runCalibrationButton;
	private PolynomialFunction calibrationResult;


	public EDECalibrationSection(Composite parent, int style) {
		super(parent, style);
		toolkit = new FormToolkit(parent.getDisplay());
		setupUI();
	}

	private void setupUI() {
		this.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		section = toolkit.createSection(this, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		section.setText("EDE Calibration");
		toolkit.paintBordersFor(section);
		section.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		Composite sectionComposite = toolkit.createComposite(section, SWT.NONE);
		toolkit.paintBordersFor(sectionComposite);
		section.setClient(sectionComposite);
		sectionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));

		final Composite dataComposite = toolkit.createComposite(sectionComposite, SWT.None);
		dataComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		dataComposite.setLayout(new GridLayout(3, false));

		final Label lblRefFile = toolkit.createLabel(dataComposite, "Reference file", SWT.NONE);
		lblRefFile.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		final Text lblRefFileValue = toolkit.createText(dataComposite, "", SWT.None);
		lblRefFileValue.setEditable(false);
		GridData gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gridData.widthHint = 140;
		lblRefFileValue.setLayoutData(gridData);

		dataBindingCtx.bindValue(
				WidgetProperties.text().observe(lblRefFileValue),
				BeanProperties.value(ReferenceCalibrationDataModel.FILE_NAME_PROP_NAME).observe(EdeCalibrationModel.INSTANCE.getRefData())
				, null,
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus result = super.doSet(observableValue, value);
						if (value == null) {
							return result;
						}
						try {
							CalibrationPlotViewer refView = (CalibrationPlotViewer) PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(EdeManualCalibrationPlotView.REFERENCE_ID);
							refView.setCalibrationData(EdeCalibrationModel.INSTANCE.getRefData());
						} catch (PartInitException e) {
							logger.error("Unable to update reference data plot", e);
						}
						return result;
					}
				});

		final Button loadRefDataButton = toolkit.createButton(dataComposite, "Browse", SWT.None);
		loadRefDataButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));
		loadRefDataButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				showDataFileDialog(loadRefDataButton.getShell(), EdeCalibrationModel.INSTANCE.getRefData());
			}
		});

		final Label lblEdeDataFile = toolkit.createLabel(dataComposite, "EDE data file", SWT.NONE);
		lblEdeDataFile.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		final Text lblEdeDataFileValue = toolkit.createText(dataComposite, "", SWT.None);
		lblEdeDataFileValue.setEditable(false);
		lblEdeDataFileValue.setLayoutData(gridData);

		dataBindingCtx.bindValue(
				WidgetProperties.text().observe(lblEdeDataFileValue),
				BeanProperties.value(ReferenceCalibrationDataModel.FILE_NAME_PROP_NAME).observe(EdeCalibrationModel.INSTANCE.getEdeData()),
				null,
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus result = super.doSet(observableValue, value);
						if (value == null) {
							return result;
						}
						try {
							CalibrationPlotViewer refView = (CalibrationPlotViewer) PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(EdeManualCalibrationPlotView.EDE_ID);
							refView.setCalibrationData(EdeCalibrationModel.INSTANCE.getEdeData());
						} catch (PartInitException e) {
							UIHelper.showError("Unable to set data file", e.getMessage());
							logger.error("Unable to set data file", e);
						}
						return result;
					}
				});
		Button loadEdeDataButton = toolkit.createButton(dataComposite, "Browse", SWT.None);
		loadEdeDataButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));
		loadEdeDataButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				showDataFileDialog(loadRefDataButton.getShell(), EdeCalibrationModel.INSTANCE.getEdeData());
			}
		});

		final Label lblPolyOrder = toolkit.createLabel(dataComposite, "Polynomial order", SWT.NONE);
		lblPolyOrder.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		final Spinner polynomialFittingOrderSpinner = new Spinner(dataComposite, SWT.BORDER);
		polynomialFittingOrderSpinner.setMinimum(1);
		polynomialFittingOrderSpinner.setMaximum(5);
		polynomialFittingOrderSpinner.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		toolkit.paintBordersFor(dataComposite);

		Composite plotComposite = toolkit.createComposite(sectionComposite, SWT.None);
		plotComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		plotComposite.setLayout(new GridLayout(3, true));

		manualCalibrationCheckButton = toolkit.createButton(plotComposite, "Manual calibration", SWT.CHECK);
		manualCalibrationCheckButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(manualCalibrationCheckButton),
				BeanProperties.value(EdeCalibrationModel.MANUAL_PROP_NAME).observe(EdeCalibrationModel.INSTANCE));

		runCalibrationButton = toolkit.createButton(plotComposite, "Run EDE Calibration", SWT.None);
		gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		runCalibrationButton.setLayoutData(gridData);
		runCalibrationButton.addSelectionListener(new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				runEdeCalibration(polynomialFittingOrderSpinner.getSelection());
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				this.widgetSelected(e);
			}
		});

		Composite polyLabelComposite = toolkit.createComposite(sectionComposite, SWT.None);
		polyLabelComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		polyLabelComposite.setLayout(new GridLayout(2, false));

		final Label polynomialLbl = toolkit.createLabel(polyLabelComposite, "Calibration polynomial", SWT.NONE);
		polynomialLbl.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		polynomialValueLbl = toolkit.createLabel(polyLabelComposite, "", SWT.BORDER);
		polynomialValueLbl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		DetectorModel.INSTANCE.getEnergyCalibrationSetObserver().addPropertyChangeListener(
				EnergyCalibrationSetObserver.ENERGY_CALIBRATION_SET_PROP_NAME,calibrationSetListener);

		updateEnergyCalibrationPolynomialText();

		toolkit.paintBordersFor(plotComposite);

		Composite roisSectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(roisSectionSeparator);
		section.setSeparatorControl(roisSectionSeparator);
	}

	private final PropertyChangeListener calibrationSetListener = new PropertyChangeListener() {
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			Display.getDefault().asyncExec(new Runnable() {
				@Override
				public void run() {
					updateEnergyCalibrationPolynomialText();
				}
			});
		}
	};

	private void showDataFileDialog(final Shell shell, ReferenceCalibrationDataModel dataModel) {
		FileDialog fileDialog = new FileDialog(shell, SWT.OPEN);
		fileDialog.setText("Load data");
		fileDialog.setFilterPath(ClientConfig.DEFAULT_DATA_PATH);
		String selected = fileDialog.open();
		if (selected != null) {
			try {
				File refFile = new File(selected);
				if (refFile.exists() && refFile.canRead()) {
					dataModel.setData(selected);
				} else {
					throw new Exception("Unable to read " + selected + ".");
				}
			} catch (Exception e) {
				UIHelper.showError("Error setting data model", e.getMessage());
				logger.error("Error setting data model", e);
			}
		}
	}

	private void runEdeCalibration(final int selectedFitOrder) {
		try {
			final EdeCalibration edeCalibration = new EdeCalibration();
			AbstractDataset[] refDatasets = selectDataRange(AlignmentPerspective.REF_PLOT_NAME);
			final AbstractDataset refEnergySlice = refDatasets[0];
			final AbstractDataset refSpectrumSlice = refDatasets[1];
			AbstractDataset[] edeDatasets = selectDataRange(AlignmentPerspective.EDE_PLOT_NAME);
			final AbstractDataset edeIdxSlice = edeDatasets[0];
			final AbstractDataset edeSpectrumSlice = edeDatasets[1];
			edeCalibration.setMaxEdeChannel(EdeCalibrationModel.INSTANCE.getEdeData().getRefDataNode().getSize() - 1);
			edeCalibration.setFitOrder(selectedFitOrder);
			edeCalibration.setReferenceData(refEnergySlice, refSpectrumSlice);
			edeCalibration.setEdeSpectrum(edeIdxSlice, edeSpectrumSlice);

			double ref1e, ref2e, ref3e;
			double ede1e, ede2e, ede3e;
			if (manualCalibrationCheckButton.getSelection()) {
				ref1e = EdeCalibrationModel.INSTANCE.getRefData().getReferencePoints().get(0);
				ref2e = EdeCalibrationModel.INSTANCE.getRefData().getReferencePoints().get(1);
				ref3e = EdeCalibrationModel.INSTANCE.getRefData().getReferencePoints().get(2);

				ede1e = EdeCalibrationModel.INSTANCE.getEdeData().getReferencePoints().get(0);
				ede2e = EdeCalibrationModel.INSTANCE.getEdeData().getReferencePoints().get(1);
				ede3e = EdeCalibrationModel.INSTANCE.getEdeData().getReferencePoints().get(2);

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
							IPlottingSystem plottingSystemRef = PlottingFactory.getPlottingSystem(AlignmentPerspective.REF_PLOT_NAME);
							plottingSystemRef.clear();

							ILineTrace refTrace = plottingSystemRef.createLineTrace("Ref");
							refTrace.setData(refEnergySlice, refSpectrumSlice);
							refTrace.setTraceColor(ColorConstants.red);
							plottingSystemRef.addTrace(refTrace);

							ILineTrace edeTrace = plottingSystemRef.createLineTrace("Ede");
							edeTrace.setData(resEnergyDataset, edeSpectrumSlice);
							edeTrace.setTraceColor(ColorConstants.blue);
							plottingSystemRef.addTrace(edeTrace);

							plottingSystemRef.repaint();

							calibrationResult = edeCalibration.getEdeCalibrationPolynomial();
							applyEdeCalibration();

							runCalibrationButton.setEnabled(true);
						}
					});
					return Status.OK_STATUS;
				}
			};
			job.schedule();
		} catch(Exception e) {
			UIHelper.showError("Unable to run calibration", e.getMessage());
			logger.error("Unable to run calibration", e);
		}
	}

	protected void applyEdeCalibration() {
		if (calibrationResult != null) {
			try {
				DetectorModel.INSTANCE.getCurrentDetector().setEnergyCalibration(calibrationResult);
			} catch (DeviceException e) {
				logger.error("Trying to apply the calibration to the current detector", e);
			}
		}
	}

	private AbstractDataset[] selectDataRange(String plotName) {
		final AbstractDataset dataE, dataI;
		IPlottingSystem plottingSystemRef = PlottingFactory.getPlottingSystem(plotName);
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

	private void updateEnergyCalibrationPolynomialText() {
		if (DetectorModel.INSTANCE.getCurrentDetector() == null) {
			return;
		}
		try {
			polynomialValueLbl.setText(DetectorModel.INSTANCE.getCurrentDetector().getEnergyCalibration().toString());
		} catch (DeviceException e) {
			logger.error("Unable to get the energy calibration function for the detector", e);
		}
	}

	@Override
	protected void disposeResource() {
		dataBindingCtx.dispose();
		DetectorModel.INSTANCE.getEnergyCalibrationSetObserver().removePropertyChangeListener(
				EnergyCalibrationSetObserver.ENERGY_CALIBRATION_SET_PROP_NAME,calibrationSetListener);
	}

}