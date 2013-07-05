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

package uk.ac.gda.exafs.ui.composites;

import gda.device.Scannable;
import gda.device.detector.XHROI;
import gda.factory.Finder;

import java.util.ArrayList;

import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.layout.TableColumnLayout;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.CellEditor;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jface.viewers.ColumnWeightData;
import org.eclipse.jface.viewers.ComboViewer;
import org.eclipse.jface.viewers.EditingSupport;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.jface.viewers.TextCellEditor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.CCombo;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Spinner;
import org.eclipse.swt.widgets.Text;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.swt.widgets.ToolItem;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;

import uk.ac.gda.exafs.data.ScannableSetup;
import uk.ac.gda.exafs.data.ScannableSetup.DetectorSetup;
import uk.ac.gda.exafs.data.ScannableSetup.Scannables;
import uk.ac.gda.ui.viewer.RotationViewer;

public class FocusingFormComposite {
	private Form forcusingForm;
	private FormToolkit toolkit;

	// TODO Use static block to generate this
	// TODO Review
	private static final String[] STEPS_IN_MILLI_METER = new String[]{"0.1","0.2","0.3","0.4","0.5","0.6","0.7","0.8","0.9","1.0","2.0","3.0","4.0","5.0","6.0","7.0","8.0","9.0","10.0"};
	private static final int DEFAUALT_STEP_INDEX = 9;
	private static final int DECIMALS = 2;
	private static final int MAX = 100 * (int) Math.pow(10, DECIMALS);

	private final ArrayList<XHROI> noOfRegionsList = new ArrayList<XHROI>();
	private ComboViewer cmbFirstStripViewer;
	private ComboViewer cmbLastStripViewer;

	public Form getFocusingForm(FormToolkit toolkit, Composite parent) {
		if (forcusingForm == null) {
			this.toolkit = toolkit;
			forcusingForm = createFocusingForm(parent);
		}
		return forcusingForm;
	}

	private Form createFocusingForm(Composite parent) {
		Form form = toolkit.createForm(parent);
		form.getBody().setLayout(new GridLayout());
		toolkit.decorateFormHeading(form);
		form.setText("Slits scan / Focusing");
		createFormBendSection(form);
		createFormCurvatureSection(form);
		createFormRoisSection(form);
		createFormSampleZSection(form);
		createFormSlitsParametersSection(form);
		createFormSlitsScanComposite(form);
		return form;
	}

	@SuppressWarnings("static-access")
	private void createFormBendSection(Form form) {
		final Section bendSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE);
		toolkit.paintBordersFor(bendSection);
		bendSection.setText("Polychromator Benders");
		toolkit.paintBordersFor(bendSection);
		bendSection.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		Composite bendSelectionComposite = toolkit.createComposite(bendSection, SWT.NONE);
		toolkit.paintBordersFor(bendSelectionComposite);
		bendSelectionComposite.setLayout(new GridLayout(2, false));
		bendSection.setClient(bendSelectionComposite);
		Label lblBend1Name = toolkit.createLabel(bendSelectionComposite, Scannables.POLY_BENDER_1.getLabelForUI(), SWT.NONE);
		lblBend1Name.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		GridLayoutFactory rotationGroupLayoutFactory = GridLayoutFactory.swtDefaults().numColumns(3).spacing(0, 0).margins(0, 0);
		GridLayoutFactory layoutFactory = GridLayoutFactory.swtDefaults().numColumns(3).spacing(0, 0);
		final Scannable theScannableBender1 = Finder.getInstance().find(Scannables.POLY_BENDER_1.getScannableName());
		RotationViewer rotationViewerBander1 = new RotationViewer(theScannableBender1, "", false);
		rotationViewerBander1.configureStandardStep(1.0);
		rotationViewerBander1.setNudgeSizeBoxDecimalPlaces(DECIMALS);
		rotationViewerBander1.createControls(bendSelectionComposite, SWT.SINGLE, true, rotationGroupLayoutFactory.create(),
				layoutFactory.create(), null);

		//		Spinner spnBend1 = new Spinner(bendSelectionComposite, SWT.BORDER | SWT.FLAT);
		//		spnBend1.setDigits(DECIMALS);
		//		spnBend1.setMaximum(MAX);
		//		spnBend1.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		//		Label lblBend1Step = toolkit.createLabel(bendSelectionComposite, "Step:", SWT.NONE);
		//		lblBend1Step.setLayoutData(new GridData(GridData.END, GridData.CENTER, false, false));
		//		CCombo cmbBend1Steps = new CCombo(bendSelectionComposite, SWT.FLAT);
		//		cmbBend1Steps.setEditable(false);
		//		cmbBend1Steps.setLayoutData(new GridData(GridData.END, GridData.CENTER, false, false));
		//		cmbBend1Steps.setItems(STEPS_IN_MILLI_METER);
		//		cmbBend1Steps.setText(STEPS_IN_MILLI_METER[DEFAUALT_STEP_INDEX]);
		//		cmbBend1Steps.addListener(SWT.Selection, new StepChangeListener(spnBend1));

		Label lblBend2Name = toolkit.createLabel(bendSelectionComposite, Scannables.POLY_BENDER_2.getLabelForUI(), SWT.NONE);
		lblBend2Name.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		final Scannable theScannableBender2 = Finder.getInstance().find(Scannables.POLY_BENDER_2.getScannableName());
		RotationViewer rotationViewerBander2 = new RotationViewer(theScannableBender2, "", false);
		rotationViewerBander2.configureStandardStep(1.0);
		rotationViewerBander2.setNudgeSizeBoxDecimalPlaces(DECIMALS);
		rotationViewerBander2.createControls(bendSelectionComposite, SWT.SINGLE, true, rotationGroupLayoutFactory.create(),
				layoutFactory.create(), null);

		//		Spinner spnBend2 = new Spinner(bendSelectionComposite, SWT.BORDER | SWT.FLAT);
		//		spnBend2.setDigits(DECIMALS);
		//		spnBend2.setMaximum(MAX);
		//		spnBend2.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		//		Label lblBend2Step = toolkit.createLabel(bendSelectionComposite, "Step:", SWT.NONE);
		//		lblBend2Step.setLayoutData(new GridData(GridData.END, GridData.CENTER, false, false));
		//		CCombo cmbBend2Steps = new CCombo(bendSelectionComposite, SWT.FLAT);
		//		cmbBend2Steps.setEditable(false);
		//		cmbBend2Steps.setLayoutData(new GridData(GridData.END, GridData.CENTER, false, false));
		//		cmbBend2Steps.setItems(STEPS_IN_MILLI_METER);
		//		cmbBend2Steps.setText(STEPS_IN_MILLI_METER[DEFAUALT_STEP_INDEX]);
		//		cmbBend2Steps.addListener(SWT.Selection, new StepChangeListener(spnBend2));

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(bendSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		bendSection.setSeparatorControl(defaultSectionSeparator);
	}

	@SuppressWarnings("static-access")
	private void createFormCurvatureSection(Form form) {
		final Section curvatureSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE);
		toolkit.paintBordersFor(curvatureSection);
		curvatureSection.setText("Curvature/Ellipticity");
		toolkit.paintBordersFor(curvatureSection);
		curvatureSection.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		Composite curvatureSelectionComposite = toolkit.createComposite(curvatureSection, SWT.NONE);
		toolkit.paintBordersFor(curvatureSelectionComposite);
		curvatureSelectionComposite.setLayout(new GridLayout(4, false));
		curvatureSection.setClient(curvatureSelectionComposite);

		Label lblCurvature = toolkit.createLabel(curvatureSelectionComposite, "Curvature:", SWT.NONE);
		lblCurvature.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		Spinner spnCurvature = new Spinner(curvatureSelectionComposite, SWT.BORDER | SWT.FLAT);
		spnCurvature.setDigits(DECIMALS);
		spnCurvature.setMaximum(MAX);
		spnCurvature.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		Label lblCurvatureStep = toolkit.createLabel(curvatureSelectionComposite, "Step:", SWT.NONE);
		lblCurvatureStep.setLayoutData(new GridData(GridData.END, GridData.CENTER, false, false));
		CCombo cmbCurvatureSteps = new CCombo(curvatureSelectionComposite, SWT.BORDER | SWT.FLAT);
		cmbCurvatureSteps.setEditable(false);

		cmbCurvatureSteps.setLayoutData(new GridData(GridData.END, GridData.CENTER, false, false));
		cmbCurvatureSteps.setItems(STEPS_IN_MILLI_METER);
		cmbCurvatureSteps.setText(STEPS_IN_MILLI_METER[DEFAUALT_STEP_INDEX]);
		cmbCurvatureSteps.addListener(SWT.Selection, new StepChangeListener(spnCurvature));

		Label lblEllipticity = toolkit.createLabel(curvatureSelectionComposite, "Ellipticity:", SWT.NONE);
		lblEllipticity.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		Spinner spnEllipticity = new Spinner(curvatureSelectionComposite, SWT.BORDER | SWT.FLAT);
		spnEllipticity.setDigits(DECIMALS);
		spnEllipticity.setMaximum(MAX);
		spnEllipticity.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		Label lblEllipticityStep = toolkit.createLabel(curvatureSelectionComposite, "Step:", SWT.NONE);
		lblEllipticityStep.setLayoutData(new GridData(GridData.END, GridData.CENTER, false, false));
		CCombo cmbEllipticitySteps = new CCombo(curvatureSelectionComposite, SWT.BORDER | SWT.FLAT);
		cmbEllipticitySteps.setEditable(false);
		cmbEllipticitySteps.setLayoutData(new GridData(GridData.END, GridData.CENTER, false, false));
		cmbEllipticitySteps.setItems(STEPS_IN_MILLI_METER);
		cmbEllipticitySteps.setText(STEPS_IN_MILLI_METER[DEFAUALT_STEP_INDEX]);
		cmbEllipticitySteps.addListener(SWT.Selection, new StepChangeListener(spnEllipticity));

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(curvatureSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		curvatureSection.setSeparatorControl(defaultSectionSeparator);
	}

	@SuppressWarnings("static-access")
	private void createFormSampleZSection(Form form) {
		final Section sampleZSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE);
		toolkit.paintBordersFor(sampleZSection);
		sampleZSection.setText("Sample position");
		toolkit.paintBordersFor(sampleZSection);
		sampleZSection.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		Composite sampleZSelectionComposite = toolkit.createComposite(sampleZSection, SWT.NONE);
		toolkit.paintBordersFor(sampleZSelectionComposite);
		sampleZSelectionComposite.setLayout(new GridLayout(4, false));
		sampleZSection.setClient(sampleZSelectionComposite);
		Label lblSampleZ = toolkit.createLabel(sampleZSelectionComposite, "Sample_z:", SWT.NONE);
		lblSampleZ.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		Spinner spnSampleZ = new Spinner(sampleZSelectionComposite, SWT.BORDER | SWT.FLAT);
		spnSampleZ.setDigits(DECIMALS);
		spnSampleZ.setMaximum(MAX);
		spnSampleZ.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		Label lblSampleZStep = toolkit.createLabel(sampleZSelectionComposite, "Step:", SWT.NONE);
		lblSampleZStep.setLayoutData(new GridData(GridData.END, GridData.CENTER, false, false));
		CCombo cmbSampleZSteps = new CCombo(sampleZSelectionComposite, SWT.BORDER | SWT.FLAT);
		cmbSampleZSteps.setEditable(false);
		cmbSampleZSteps.setLayoutData(new GridData(GridData.END, GridData.CENTER, false, false));
		cmbSampleZSteps.setItems(STEPS_IN_MILLI_METER);
		cmbSampleZSteps.setText(STEPS_IN_MILLI_METER[DEFAUALT_STEP_INDEX]);
		cmbSampleZSteps.addListener(SWT.Selection, new StepChangeListener(spnSampleZ));

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(sampleZSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		sampleZSection.setSeparatorControl(defaultSectionSeparator);
	}


	@SuppressWarnings({ "unused", "static-access" })
	private void createFormRoisSection(Form form) {
		final Section roisSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE);
		roisSection.setText("Region of Interests (ROIs)");
		toolkit.paintBordersFor(roisSection);
		roisSection.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		Composite roisSectionComposite = toolkit.createComposite(roisSection, SWT.NONE);
		toolkit.paintBordersFor(roisSectionComposite);
		roisSection.setClient(roisSectionComposite);
		roisSectionComposite.setLayout(new GridLayout());

		Composite stripsComposit = new Composite(roisSectionComposite, SWT.NONE);
		GridData gridData = new GridData(GridData.FILL, GridData.BEGINNING, true, true);
		stripsComposit.setLayoutData(gridData);
		stripsComposit.setLayout(new GridLayout(4, false));

		Label lblFirstStrip = toolkit.createLabel(stripsComposit, "First strip:", SWT.NONE);
		lblFirstStrip.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		CCombo cmbFirstStrip = new CCombo(stripsComposit, SWT.BORDER | SWT.FLAT);
		cmbFirstStrip.setEditable(false);
		cmbFirstStrip.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		cmbFirstStripViewer = new ComboViewer(cmbFirstStrip);
		cmbFirstStripViewer.setContentProvider(new ArrayContentProvider());
		cmbFirstStripViewer.setLabelProvider(new LabelProvider());
		cmbFirstStripViewer.setInput(ScannableSetup.STRIPS);
		toolkit.paintBordersFor(cmbFirstStrip);

		Label lblLastStrip = toolkit.createLabel(stripsComposit, "Last strip:", SWT.NONE);
		lblLastStrip.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		CCombo cmbLastStrip = new CCombo(stripsComposit, SWT.BORDER | SWT.FLAT);
		cmbLastStrip.setEditable(false);
		cmbLastStrip.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		cmbLastStripViewer = new ComboViewer(cmbLastStrip);
		cmbLastStripViewer.setContentProvider(new ArrayContentProvider());
		cmbLastStripViewer.setLabelProvider(new LabelProvider());
		cmbLastStripViewer.setInput(ScannableSetup.STRIPS);
		toolkit.paintBordersFor(cmbLastStrip);


		Composite regionsComposit = new Composite(roisSectionComposite, SWT.NONE);
		gridData = new GridData(GridData.FILL, GridData.FILL, true, true);
		gridData.heightHint = 150;
		regionsComposit.setLayoutData(gridData);
		regionsComposit.setLayout(new GridLayout(2,false));

		Composite regionsTableComposit = new Composite(regionsComposit, SWT.NONE);
		regionsTableComposit.setLayoutData(new GridData(GridData.FILL, GridData.FILL, true, true));
		TableColumnLayout layout = new TableColumnLayout();
		regionsTableComposit.setLayout(layout);
		final TableViewer roisTableViewer = new TableViewer(regionsTableComposit,  SWT.BORDER | SWT.FLAT);
		roisTableViewer.getTable().setLayoutData(new GridData(GridData.FILL_BOTH));
		roisTableViewer.setContentProvider(new ArrayContentProvider());
		roisTableViewer.getTable().setHeaderVisible(true);

		// Region No. column
		TableViewerColumn viewerNumberColumn = new TableViewerColumn(roisTableViewer, SWT.NONE);
		viewerNumberColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public String getText(Object element) {
				return ((XHROI) element).getName();
			}
		});
		layout.setColumnData(viewerNumberColumn.getColumn(),new ColumnWeightData(10));

		// Lower level column
		TableViewerColumn viewerlowerLevelColumn = new TableViewerColumn(roisTableViewer, SWT.NONE);

		viewerlowerLevelColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public String getText(Object element) {
				return Integer.toString(((XHROI) element).getLowerLevel());
			}
		});
		viewerlowerLevelColumn.setEditingSupport(new RoisStripLevelEditorSupport(roisTableViewer, false));
		layout.setColumnData(viewerlowerLevelColumn.getColumn(),new ColumnWeightData(50));
		viewerlowerLevelColumn.getColumn().setText("Lower level");

		// Upper level column
		TableViewerColumn viewerUpperLevelColumn = new TableViewerColumn(roisTableViewer, SWT.NONE);
		viewerUpperLevelColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public String getText(Object element) {
				return Integer.toString(((XHROI) element).getUpperLevel());
			}
		});
		viewerUpperLevelColumn.setEditingSupport(new RoisStripLevelEditorSupport(roisTableViewer, true));
		viewerUpperLevelColumn.getColumn().setText("Upper level");
		layout.setColumnData(viewerUpperLevelColumn.getColumn(),new ColumnWeightData(50));
		toolkit.paintBordersFor(regionsTableComposit);
		populateRegions();
		roisTableViewer.setInput(noOfRegionsList);

		Composite buttonComposit = new Composite(regionsComposit, SWT.NONE);
		buttonComposit.setLayout(new GridLayout());
		buttonComposit.setLayoutData(new GridData(GridData.VERTICAL_ALIGN_FILL));
		final Button butAdd = new Button(buttonComposit, SWT.FLAT);
		butAdd.setText("Add");
		butAdd.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));

		final Button butRemove = new Button(buttonComposit, SWT.FLAT);
		butRemove.setText("Remove");
		butRemove.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));

		final Button butReset = new Button(buttonComposit, SWT.FLAT);
		butReset.setText("Reset");
		butReset.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));


		butAdd.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				noOfRegionsList.add(new XHROI(Integer.toString(noOfRegionsList.size() + 1)));
				butRemove.setEnabled(noOfRegionsList.size() > 1);
				distributeNoOfRegionsValues();
				roisTableViewer.refresh();
			}
		});

		butRemove.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				noOfRegionsList.remove(noOfRegionsList.size() - 1);
				butRemove.setEnabled(!noOfRegionsList.isEmpty());
				distributeNoOfRegionsValues();
				roisTableViewer.refresh();
			}
		});

		butReset.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				distributeNoOfRegionsValues();

			}
		});

		Composite roisSectionSeparator = toolkit.createCompositeSeparator(roisSection);
		toolkit.paintBordersFor(roisSectionSeparator);
		roisSection.setSeparatorControl(roisSectionSeparator);

		ToolBar roisSectionTbar = new ToolBar(roisSection, SWT.FLAT | SWT.HORIZONTAL);
		new ToolItem(roisSectionTbar, SWT.SEPARATOR);
		ToolItem saveRoisTBarItem = new ToolItem(roisSectionTbar, SWT.NULL);
		saveRoisTBarItem.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				roisSection.setExpanded(false);
			}
		});
		saveRoisTBarItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ETOOL_SAVE_EDIT));
		roisSection.setTextClient(roisSectionTbar);

		cmbFirstStripViewer.addSelectionChangedListener(new ISelectionChangedListener() {
			@Override
			public void selectionChanged(SelectionChangedEvent event) {
				distributeNoOfRegionsValues();
				roisTableViewer.refresh();
			}
		});

		cmbLastStripViewer.addSelectionChangedListener(new ISelectionChangedListener() {
			@Override
			public void selectionChanged(SelectionChangedEvent event) {
				int first = (Integer) ((IStructuredSelection) cmbFirstStripViewer.getSelection()).getFirstElement();
				int last = (Integer) ((IStructuredSelection) cmbLastStripViewer.getSelection()).getFirstElement();
				if (last > first) {
					// TODO Update model
					distributeNoOfRegionsValues();
					roisTableViewer.refresh();
				} else {
					MessageDialog.openWarning(Display.getDefault().getActiveShell(), "Warning", "Unable to set Last script" + "\n\nReason:\n" + "Value lower than First strip");
					// TODO Reset selection
				}
			}
		});
	}

	private void populateRegions() {
		// TODO Update from model
		cmbFirstStripViewer.setSelection(new StructuredSelection(ScannableSetup.STRIPS[0]));
		cmbLastStripViewer.setSelection(new StructuredSelection(ScannableSetup.STRIPS[DetectorSetup.MAX_STRIPS - 1]));
		noOfRegionsList.add(new XHROI("1"));
		noOfRegionsList.add(new XHROI("2"));
		noOfRegionsList.add(new XHROI("3"));
		noOfRegionsList.add(new XHROI("4"));
		distributeNoOfRegionsValues();
		// TODO Update butRemove enable state
	}

	private void distributeNoOfRegionsValues() {
		int first = (Integer) ((IStructuredSelection) cmbFirstStripViewer.getSelection()).getFirstElement();
		int last = (Integer) ((IStructuredSelection) cmbLastStripViewer.getSelection()).getFirstElement();
		int useableRegion = last - (first - 1);
		int increment = useableRegion / noOfRegionsList.size();
		int start = first;
		for (int i = 0; i < noOfRegionsList.size(); i++) {
			noOfRegionsList.get(i).setLowerLevel(start);
			noOfRegionsList.get(i).setUpperLevel(start + increment - 1);
			start = start + increment;
		}
		// TODO What to do with odd or decimal regions?
		if (noOfRegionsList.get(noOfRegionsList.size() - 1).getUpperLevel() < last) {
			noOfRegionsList.get(noOfRegionsList.size() - 1).setUpperLevel(last);
		}
	}

	private static class RoisStripLevelEditorSupport extends EditingSupport {

		private final TableViewer viewer;
		private final boolean isEditingUpperLevel;

		public RoisStripLevelEditorSupport(TableViewer viewer, boolean isEditingUpperLevel) {
			super(viewer);
			this.viewer = viewer;
			this.isEditingUpperLevel = isEditingUpperLevel;
		}

		@Override
		protected CellEditor getCellEditor(Object element) {
			return new TextCellEditor(viewer.getTable());
		}

		@Override
		protected boolean canEdit(Object element) {
			return true;
		}

		@Override
		protected Object getValue(Object element) {
			if (isEditingUpperLevel) {
				return Integer.toString(((XHROI) element).getUpperLevel());
			}
			return Integer.toString(((XHROI) element).getLowerLevel());
		}

		@Override
		protected void setValue(Object element, Object value) {
			try {
				// TODO Do validation for overlapping values and boundary checking
				if (isEditingUpperLevel) {
					((XHROI) element).setUpperLevel(Integer.parseInt((String) value));
				} else {
					((XHROI) element).setLowerLevel(Integer.parseInt((String) value));
				}
				this.getViewer().update(element, null);
			} catch (NumberFormatException e) {
				MessageDialog.openWarning(Display.getDefault().getActiveShell(), "Warning", "Unable to set value" + "\n\nReason:\n" + "value" + " is invalid");
			}
		}
	}

	@SuppressWarnings("static-access")
	private void createFormSlitsParametersSection(Form form) {
		final Section slitsParametersSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE);
		toolkit.paintBordersFor(slitsParametersSection);
		slitsParametersSection.setText("Slits scan parameters");
		toolkit.paintBordersFor(slitsParametersSection);
		slitsParametersSection.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));
		Composite slitsParametersSelectionComposite = toolkit.createComposite(slitsParametersSection, SWT.NONE);
		toolkit.paintBordersFor(slitsParametersSelectionComposite);
		slitsParametersSelectionComposite.setLayout(new GridLayout(4, false));
		slitsParametersSection.setClient(slitsParametersSelectionComposite);

		Label lblGap = toolkit.createLabel(slitsParametersSelectionComposite, "Gap:", SWT.NONE);
		lblGap.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		Text txtGap = toolkit.createText(slitsParametersSelectionComposite, "", SWT.NONE);
		txtGap.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));

		Label lblIntegrationTime = toolkit.createLabel(slitsParametersSelectionComposite, "Integration:", SWT.NONE);
		lblIntegrationTime.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		Text txtIntegrationTime = toolkit.createText(slitsParametersSelectionComposite, "", SWT.NONE);
		txtIntegrationTime.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));

		Label lblOffsetStart = toolkit.createLabel(slitsParametersSelectionComposite, "Offset Start:", SWT.NONE);
		lblOffsetStart.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		Spinner spnOffsetStart = new Spinner(slitsParametersSelectionComposite, SWT.BORDER | SWT.FLAT);
		spnOffsetStart.setDigits(DECIMALS);
		spnOffsetStart.setMaximum(MAX);
		spnOffsetStart.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		Label lblOffsetStartStep = toolkit.createLabel(slitsParametersSelectionComposite, "Step:", SWT.NONE);
		lblOffsetStartStep.setLayoutData(new GridData(GridData.END, GridData.CENTER, false, false));
		CCombo cmbOffsetStartSteps = new CCombo(slitsParametersSelectionComposite, SWT.BORDER | SWT.FLAT);
		cmbOffsetStartSteps.setEditable(false);
		cmbOffsetStartSteps.setLayoutData(new GridData(GridData.END, GridData.CENTER, false, false));
		cmbOffsetStartSteps.setItems(STEPS_IN_MILLI_METER);
		cmbOffsetStartSteps.setText(STEPS_IN_MILLI_METER[DEFAUALT_STEP_INDEX]);
		cmbOffsetStartSteps.addListener(SWT.Selection, new StepChangeListener(spnOffsetStart));

		Label lblOffsetEnd = toolkit.createLabel(slitsParametersSelectionComposite, "Offset End:", SWT.NONE);
		lblOffsetEnd.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		Spinner spnOffsetEnd = new Spinner(slitsParametersSelectionComposite, SWT.BORDER | SWT.FLAT);
		spnOffsetEnd.setDigits(DECIMALS);
		spnOffsetEnd.setMaximum(MAX);
		spnOffsetEnd.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		Label lblOffsetEndStep = toolkit.createLabel(slitsParametersSelectionComposite, "Step:", SWT.NONE);
		lblOffsetEndStep.setLayoutData(new GridData(GridData.END, GridData.CENTER, false, false));
		CCombo cmbOffsetEndSteps = new CCombo(slitsParametersSelectionComposite, SWT.BORDER | SWT.FLAT);
		cmbOffsetEndSteps.setEditable(false);
		cmbOffsetEndSteps.setLayoutData(new GridData(GridData.END, GridData.CENTER, false, false));
		cmbOffsetEndSteps.setItems(STEPS_IN_MILLI_METER);
		cmbOffsetEndSteps.setText(STEPS_IN_MILLI_METER[DEFAUALT_STEP_INDEX]);
		cmbOffsetEndSteps.addListener(SWT.Selection, new StepChangeListener(spnOffsetEnd));

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(slitsParametersSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		slitsParametersSection.setSeparatorControl(defaultSectionSeparator);
	}

	private void createFormSlitsScanComposite(Form form) {
		Composite scanButtons = toolkit.createComposite(form.getBody());
		scanButtons.setLayoutData(new GridData(GridData.HORIZONTAL_ALIGN_FILL));
		scanButtons.setLayout(new GridLayout(2, true));
		Button startPauseButton = new Button(scanButtons, SWT.FLAT);
		startPauseButton.setText("Start Scan");
		startPauseButton.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));

		Button stopButton = new Button(scanButtons, SWT.FLAT);
		stopButton.setText("Stop");
		stopButton.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		stopButton.setEnabled(false);
		toolkit.paintBordersFor(scanButtons);
	}

	private static class StepChangeListener implements Listener {
		private final Spinner spinner;
		public StepChangeListener(Spinner spinner) {
			this.spinner = spinner;
		}
		@Override
		public void handleEvent(Event event) {
			float step = Float.parseFloat(((CCombo) event.widget).getText());
			spinner.setIncrement((int) (step * 100));
		}
	}
}