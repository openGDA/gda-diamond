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

import java.io.File;
import java.util.ArrayList;
import java.util.Collection;

import org.apache.commons.math3.analysis.polynomials.PolynomialFunction;
import org.apache.commons.math3.util.Pair;
import org.apache.commons.math3.util.Precision;
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
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.window.Window;
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
import org.eclipse.ui.dialogs.ListDialog;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.forms.widgets.TableWrapData;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.DatasetUtils;
import uk.ac.diamond.scisoft.analysis.dataset.Slice;
import uk.ac.diamond.scisoft.analysis.io.DataHolder;
import uk.ac.diamond.scisoft.analysis.io.LoaderFactory;
import uk.ac.diamond.scisoft.spectroscopy.fitting.EdeCalibration;
import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.CalibrationData;
import uk.ac.gda.exafs.data.ClientConfig.ElementReference;
import uk.ac.gda.exafs.data.DetectorConfig;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.perspectives.AlignmentPerspective;
import uk.ac.gda.exafs.ui.views.CalibrationPlotViewer;
import uk.ac.gda.exafs.ui.views.EdeDataCalibrationView;

public class EDECalibrationSection {

	public static final EDECalibrationSection INSTANCE = new EDECalibrationSection();
	private static final Logger logger = LoggerFactory.getLogger(EDECalibrationSection.class);
	private final DataBindingContext dataBindingCtx = new DataBindingContext();
	private Section section;
	private Button manualCalibrationCheckButton;
	private Label polynomialValueLbl;
	private Button runCalibrationButton;
	private Button applyCalibrationButton;
	private EDECalibrationSection() {}
	private PolynomialFunction calibrationResult;

	@SuppressWarnings({ "static-access" })
	public void createEdeCalibrationSection(Form form, FormToolkit toolkit) {
		if (section != null) {
			return;
		}
		section = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE | Section.EXPANDED);
		section.setText("EDE Calibration");
		toolkit.paintBordersFor(section);
		section.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite sectionComposite = toolkit.createComposite(section, SWT.NONE);
		toolkit.paintBordersFor(sectionComposite);
		section.setClient(sectionComposite);
		sectionComposite.setLayout(new GridLayout());

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
				BeanProperties.value(ClientConfig.ElementReference.FILE_NAME_PROP_NAME).observe(CalibrationData.INSTANCE.getRefData())
				, null,
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus retult = super.doSet(observableValue, value);
						try {
							CalibrationPlotViewer refView = (CalibrationPlotViewer) PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(EdeDataCalibrationView.REFERENCE_ID);
							refView.setCalibrationDataReference(CalibrationData.INSTANCE.getRefData());
						} catch (PartInitException e) {
							e.printStackTrace();
						}
						return retult;
					}
				});

		final Button loadRefDataButton = toolkit.createButton(dataComposite, "Browse", SWT.None);
		loadRefDataButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));
		loadRefDataButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				showDataFileDialog(loadRefDataButton.getShell(), CalibrationData.INSTANCE.getRefData());
			}
		});

		final Label lblEdeDataFile = toolkit.createLabel(dataComposite, "EDE data file", SWT.NONE);
		lblEdeDataFile.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		final Text lblEdeDataFileValue = toolkit.createText(dataComposite, "", SWT.None);
		lblEdeDataFileValue.setEditable(false);
		lblEdeDataFileValue.setLayoutData(gridData);

		dataBindingCtx.bindValue(
				WidgetProperties.text().observe(lblEdeDataFileValue),
				BeanProperties.value(ClientConfig.ElementReference.FILE_NAME_PROP_NAME).observe(CalibrationData.INSTANCE.getEdeData()),
				null,
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus retult = super.doSet(observableValue, value);
						try {
							CalibrationPlotViewer refView = (CalibrationPlotViewer) PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(EdeDataCalibrationView.EDE_ID);
							refView.setCalibrationDataReference(CalibrationData.INSTANCE.getEdeData());
						} catch (PartInitException e) {
							// TODO Handle this
							e.printStackTrace();
						}
						return retult;
					}
				});
		Button loadEdeDataButton = toolkit.createButton(dataComposite, "Browse", SWT.None);
		loadEdeDataButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));
		loadEdeDataButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				showDataFileDialog(loadRefDataButton.getShell(), CalibrationData.INSTANCE.getEdeData());
			}
		});

		final Label lblPolyOrder = toolkit.createLabel(dataComposite, "Polynomial order", SWT.NONE);
		lblPolyOrder.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		final Spinner kw = new Spinner(dataComposite, SWT.BORDER);
		kw.setMinimum(1);
		kw.setMaximum(5);
		kw.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		toolkit.paintBordersFor(dataComposite);

		Composite plotComposite = toolkit.createComposite(sectionComposite, SWT.None);
		plotComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		plotComposite.setLayout(new GridLayout(2, true));

		manualCalibrationCheckButton = toolkit.createButton(plotComposite, "Manual calibration", SWT.CHECK);
		manualCalibrationCheckButton.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(manualCalibrationCheckButton),
				BeanProperties.value(CalibrationData.MANUAL_PROP_NAME).observe(CalibrationData.INSTANCE));

		runCalibrationButton = toolkit.createButton(plotComposite, "Run EDE Calibration", SWT.None);
		gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		runCalibrationButton.setLayoutData(gridData);
		runCalibrationButton.addSelectionListener(new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				runEdeCalibration(kw.getSelection());
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

		applyCalibrationButton = toolkit.createButton(sectionComposite, "Apply EDE Calibration", SWT.None);
		gridData = new GridData(SWT.FILL, SWT.CENTER, true, false);
		gridData.horizontalSpan = 2;
		applyCalibrationButton.setLayoutData(gridData);
		applyCalibrationButton.addSelectionListener(new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				applyEdeCalibration();
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				this.widgetSelected(e);
			}
		});
		applyCalibrationButton.setEnabled(false);
		toolkit.paintBordersFor(plotComposite);

		Composite roisSectionSeparator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(roisSectionSeparator);
		section.setSeparatorControl(roisSectionSeparator);
	}

	private void showDataFileDialog(final Shell shell, ElementReference dataModel) {
		FileDialog fileDialog = new FileDialog(shell, SWT.OPEN);
		fileDialog.setText("Load data");
		fileDialog.setFilterPath(ElementReference.DEFAULT_DATA_PATH);
		String selected = fileDialog.open();
		if (selected != null) {
			try {
				File refFile = new File(selected);
				if (refFile.exists() && refFile.canRead()) {
					DataHolder dataHolder = LoaderFactory.getData(selected);
					ListDialog dialog = new ListDialog(shell);
					dialog.setContentProvider(new ArrayContentProvider());
					dialog.setTitle("Data set");
					dialog.setMessage("Choose energy node");
					dialog.setInput(dataHolder.getNames());
					dialog.setLabelProvider(new LabelProvider());
					if (dialog.open() == Window.OK) {
						Object[] energy = dialog.getResult();
						if (energy != null && energy.length == 1) {
							dialog.setMessage("Choose data node");
							if (dialog.open() == Window.OK) {
								Object[] data = dialog.getResult();
								if (data != null && data.length == 1) {
									dataModel.setData(selected, dataHolder, (String) energy[0], (String) data[0]);
								}
							}
						}
					}
				} else {
					throw new Exception("Unable to read " + selected + ".");
				}
			} catch (Exception e) {
				UIHelper.showError("Error", e.getMessage());
			}
		}
	}

	private void runEdeCalibration(final int selectedFitOrder) {
		polynomialValueLbl.setText("");
		final EdeCalibration edeCalibration = new EdeCalibration();
		AbstractDataset[] refDatasets = selectDataRange(AlignmentPerspective.REF_PLOT_NAME);
		final AbstractDataset refEnergySlice = refDatasets[0];
		final AbstractDataset refSpectrumSlice = refDatasets[1];
		AbstractDataset[] edeDatasets = selectDataRange(AlignmentPerspective.EDE_PLOT_NAME);
		final AbstractDataset edeIdxSlice = edeDatasets[0];
		final AbstractDataset edeSpectrumSlice = edeDatasets[1];
		edeCalibration.setMaxEdeChannel(CalibrationData.INSTANCE.getEdeData().getRefDataNode().getSize() - 1);
		edeCalibration.setFitOrder(selectedFitOrder);
		edeCalibration.setReferenceData(refEnergySlice, refSpectrumSlice);
		edeCalibration.setEdeSpectrum(edeIdxSlice, edeSpectrumSlice);

		double ref1e, ref2e, ref3e;
		double ede1e, ede2e, ede3e;
		if (manualCalibrationCheckButton.getSelection()) {
			ref1e = CalibrationData.INSTANCE.getRefData().getReferencePoints().get(0);
			ref2e = CalibrationData.INSTANCE.getRefData().getReferencePoints().get(1);
			ref3e = CalibrationData.INSTANCE.getRefData().getReferencePoints().get(2);

			ede1e = CalibrationData.INSTANCE.getEdeData().getReferencePoints().get(0);
			ede2e = CalibrationData.INSTANCE.getEdeData().getReferencePoints().get(1);
			ede3e = CalibrationData.INSTANCE.getEdeData().getReferencePoints().get(2);

			final Pair<Double, Double> refPoint1 = new Pair<Double, Double>(ref1e, ede1e);
			final Pair<Double, Double> refPoint2 = new Pair<Double, Double>(ref2e, ede2e);
			final Pair<Double, Double> refPoint3 = new Pair<Double, Double>(ref3e, ede3e);

			ArrayList<Pair<Double, Double>> refPositions = new ArrayList<Pair<Double, Double>>();
			refPositions.add(refPoint1);
			refPositions.add(refPoint2);
			refPositions.add(refPoint3);
			edeCalibration.setReferencePositions(refPositions);
		}
		polynomialValueLbl.setText("EDE calibration in progress...");
		Job job = new Job("EDE calibration") {
			@Override
			protected void canceling() {
				super.canceling();
				Display.getDefault().syncExec(new Runnable() {
					@Override
					public void run() {
						runCalibrationButton.setEnabled(true);
						polynomialValueLbl.setText("");
						applyCalibrationButton.setEnabled(false);
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
						polynomialValueLbl.setText(calibrationResult.toString());
						
						runCalibrationButton.setEnabled(true);
						applyCalibrationButton.setEnabled(true);
					}
				});
				return Status.OK_STATUS;
			}
		};
		job.schedule();
	}

	protected void applyEdeCalibration() {
		if (calibrationResult != null) {
			try {
				DetectorConfig.INSTANCE.getCurrentDetector().setEnergyCalibration(calibrationResult);
			} catch (DeviceException e) {
				logger.error("DeviceException trying to apply the calibration to the current detector", e);
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

}