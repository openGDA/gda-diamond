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

import gda.device.detector.XHROI;
import gda.jython.Jython;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;

import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.beans.BeansObservables;
import org.eclipse.core.databinding.validation.IValidator;
import org.eclipse.core.databinding.validation.ValidationStatus;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jface.databinding.fieldassist.ControlDecorationSupport;
import org.eclipse.jface.databinding.swt.WidgetProperties;
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
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.forms.widgets.TableWrapData;
import org.eclipse.ui.forms.widgets.TableWrapLayout;

import uk.ac.gda.exafs.data.ClientConfig;
import uk.ac.gda.exafs.data.ClientConfig.DetectorSetup;
import uk.ac.gda.exafs.data.ClientConfig.ScannableSetup;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.data.DetectorConfig;
import uk.ac.gda.exafs.data.DetectorUnavailableException;
import uk.ac.gda.exafs.data.SlitScanner;
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.UIHelper.UIMotorControl;

public class FocusingFormComposite {

	private static final int MAX_DECIMAL_PLACE = 2;
	private static final int SPINNER_INCREMENT = (int) Math.pow(10, MAX_DECIMAL_PLACE);
	private static final int ROIS_TABLE_HEIGHT = 150;
	private static final int ROIs_TABLE_WIDTH = 70;

	private ScrolledForm forcusingForm;
	private FormToolkit toolkit;

	private final ArrayList<XHROI> noOfRegionsList = new ArrayList<XHROI>();
	private ComboViewer cmbFirstStripViewer;
	private ComboViewer cmbLastStripViewer;
	private TableViewer roisTableViewer;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	public ScrolledForm getFocusingForm(FormToolkit toolkit, Composite parent) {
		if (forcusingForm == null) {
			this.toolkit = toolkit;
			forcusingForm = createFocusingForm(parent);
		}
		return forcusingForm;
	}

	private ScrolledForm createFocusingForm(Composite parent) {
		ScrolledForm scrolledform = toolkit.createScrolledForm(parent);
		Form form = scrolledform.getForm();
		form.getBody().setLayout(new TableWrapLayout());
		toolkit.decorateFormHeading(form);
		form.setText("Slits scan / Focusing");
		createFormSlitsParametersSection(form);
		createFormRoisSection(form);
		createFormSampleZSection(form);
		createFormBendSection(form);
		createFormCurvatureSection(form);
		return scrolledform;
	}

	@SuppressWarnings("static-access")
	private void createFormBendSection(Form form) {
		final Section bendSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE);
		toolkit.paintBordersFor(bendSection);
		bendSection.setText("Polychromator Benders");
		toolkit.paintBordersFor(bendSection);
		bendSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite bendSelectionComposite = toolkit.createComposite(bendSection, SWT.NONE);
		toolkit.paintBordersFor(bendSelectionComposite);
		bendSelectionComposite.setLayout(new GridLayout(2, false));
		bendSection.setClient(bendSelectionComposite);

		Label lblBend1Name = toolkit.createLabel(bendSelectionComposite, ScannableSetup.POLY_BENDER_1.getLabelForUI(), SWT.NONE);
		lblBend1Name.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		UIHelper.createMotorViewer(toolkit, bendSelectionComposite, ScannableSetup.POLY_BENDER_1, UIMotorControl.ROTATION);

		Label lblBend2Name = toolkit.createLabel(bendSelectionComposite, ScannableSetup.POLY_BENDER_2.getLabelForUI(), SWT.NONE);
		lblBend2Name.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		UIHelper.createMotorViewer(toolkit, bendSelectionComposite, ScannableSetup.POLY_BENDER_2, UIMotorControl.ROTATION);

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
		curvatureSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite curvatureSelectionComposite = toolkit.createComposite(curvatureSection, SWT.NONE);
		toolkit.paintBordersFor(curvatureSelectionComposite);
		curvatureSelectionComposite.setLayout(new GridLayout(2, false));
		curvatureSection.setClient(curvatureSelectionComposite);

		Label lblCurvature = toolkit.createLabel(curvatureSelectionComposite, ScannableSetup.POLY_CURVATURE.getLabelForUI(), SWT.NONE);
		lblCurvature.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		UIHelper.createMotorViewer(toolkit, curvatureSelectionComposite, ScannableSetup.POLY_CURVATURE, UIMotorControl.ROTATION);

		Label lblEllipticity = toolkit.createLabel(curvatureSelectionComposite, ScannableSetup.POLY_Y_ELLIPTICITY.getLabelForUI(), SWT.NONE);
		lblEllipticity.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		UIHelper.createMotorViewer(toolkit, curvatureSelectionComposite, ScannableSetup.POLY_Y_ELLIPTICITY, UIMotorControl.ROTATION);

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
		sampleZSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite sampleZSelectionComposite = toolkit.createComposite(sampleZSection, SWT.NONE);
		toolkit.paintBordersFor(sampleZSelectionComposite);
		sampleZSelectionComposite.setLayout(new GridLayout(2, false));
		sampleZSection.setClient(sampleZSelectionComposite);

		Label lblSampleZ = toolkit.createLabel(sampleZSelectionComposite, ScannableSetup.SAMPLE_Z_POSITION.getLabelForUI(), SWT.NONE);
		lblSampleZ.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		UIHelper.createMotorViewer(toolkit, sampleZSelectionComposite, ScannableSetup.SAMPLE_Z_POSITION, UIMotorControl.POSITION);

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(sampleZSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		sampleZSection.setSeparatorControl(defaultSectionSeparator);
	}

	@SuppressWarnings({ "unused", "static-access" })
	private void createFormRoisSection(Form form) {
		final Section roisSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE);
		roisSection.setText("Region of Interests (ROIs)");
		toolkit.paintBordersFor(roisSection);
		roisSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite roisSectionComposite = toolkit.createComposite(roisSection, SWT.NONE);
		toolkit.paintBordersFor(roisSectionComposite);
		roisSection.setClient(roisSectionComposite);
		roisSectionComposite.setLayout(new GridLayout());

		Composite stripsComposit = new Composite(roisSectionComposite, SWT.NONE);
		GridData gridData = new GridData(GridData.FILL, GridData.BEGINNING, true, true);

		stripsComposit.setLayoutData(gridData);
		stripsComposit.setLayout(new GridLayout(4, false));

		final Label lblFirstStrip = toolkit.createLabel(stripsComposit, "First strip:", SWT.NONE);
		lblFirstStrip.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		CCombo cmbFirstStrip = new CCombo(stripsComposit, SWT.BORDER | SWT.FLAT);
		cmbFirstStrip.setEditable(false);
		cmbFirstStrip.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		cmbFirstStripViewer = new ComboViewer(cmbFirstStrip);
		cmbFirstStripViewer.setContentProvider(new ArrayContentProvider());
		cmbFirstStripViewer.setLabelProvider(new LabelProvider());

		Label lblLastStrip = toolkit.createLabel(stripsComposit, "Last strip:", SWT.NONE);
		lblLastStrip.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		CCombo cmbLastStrip = new CCombo(stripsComposit, SWT.BORDER | SWT.FLAT);
		cmbLastStrip.setEditable(false);
		cmbLastStrip.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		cmbLastStripViewer = new ComboViewer(cmbLastStrip);
		cmbLastStripViewer.setContentProvider(new ArrayContentProvider());
		cmbLastStripViewer.setLabelProvider(new LabelProvider());

		Composite regionsComposit = new Composite(roisSectionComposite, SWT.NONE);
		gridData = new GridData(GridData.FILL, GridData.FILL, true, true);
		gridData.heightHint = ROIS_TABLE_HEIGHT;
		regionsComposit.setLayoutData(gridData);
		regionsComposit.setLayout(new GridLayout(2,false));

		Composite regionsTableComposit = new Composite(regionsComposit, SWT.NONE);
		gridData = new GridData(GridData.FILL, GridData.FILL, true, true);
		gridData.widthHint = ROIs_TABLE_WIDTH;
		regionsTableComposit.setLayoutData(gridData);
		TableColumnLayout layout = new TableColumnLayout();
		regionsTableComposit.setLayout(layout);
		roisTableViewer = new TableViewer(regionsTableComposit,  SWT.BORDER | SWT.FLAT);
		roisTableViewer.getTable().setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
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
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(1));

		// Lower level column
		TableViewerColumn viewerlowerLevelColumn = new TableViewerColumn(roisTableViewer, SWT.NONE);

		viewerlowerLevelColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public String getText(Object element) {
				return Integer.toString(((XHROI) element).getLowerLevel());
			}
		});
		viewerlowerLevelColumn.setEditingSupport(new RoisStripLevelEditorSupport(roisTableViewer, false));
		layout.setColumnData(viewerlowerLevelColumn.getColumn(),new ColumnWeightData(4));
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
		layout.setColumnData(viewerUpperLevelColumn.getColumn(),new ColumnWeightData(4));
		toolkit.paintBordersFor(regionsTableComposit);
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
			}
		});

		butRemove.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				noOfRegionsList.remove(noOfRegionsList.size() - DetectorSetup.MIN_ROIs);
				butRemove.setEnabled(!noOfRegionsList.isEmpty());
				distributeNoOfRegionsValues();
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
				saveROIsChanges();
			}
		});
		saveRoisTBarItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ETOOL_SAVE_EDIT));
		roisSection.setTextClient(roisSectionTbar);

		DetectorConfig.INSTANCE.addPropertyChangeListener(DetectorConfig.CURRENT_DETECTOR_SETUP_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				Object value = evt.getNewValue();
				showROIs(value);
			}
		});

		showROIs(DetectorConfig.INSTANCE.getCurrentDetectorSetup());

		cmbFirstStripViewer.addSelectionChangedListener(new ISelectionChangedListener() {
			@Override
			public void selectionChanged(SelectionChangedEvent event) {
				checkAndUpdateFirstAndLastStrips();
			}
		});

		cmbLastStripViewer.addSelectionChangedListener(new ISelectionChangedListener() {
			@Override
			public void selectionChanged(SelectionChangedEvent event) {
				checkAndUpdateFirstAndLastStrips();
			}
		});

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(roisSection),
				BeansObservables.observeValue(DetectorConfig.INSTANCE, DetectorConfig.DETECTOR_CONNECTED_PROP_NAME),
				null,
				null);
	}

	private void checkAndUpdateFirstAndLastStrips() {
		IStructuredSelection firstSelection = (IStructuredSelection) cmbFirstStripViewer.getSelection();
		IStructuredSelection  lastSelection = (IStructuredSelection) cmbLastStripViewer.getSelection();
		if (firstSelection.isEmpty() | lastSelection.isEmpty()){
			return;
		}
		int first = (int) firstSelection.getFirstElement();
		int last = (int) lastSelection.getFirstElement();
		if (last > first && (last - (first -1)) >= noOfRegionsList.size()) {
			// TODO Update to model
			distributeNoOfRegionsValues();
		} else {
			setDefaultSelection();
		}
	}

	private void setDefaultSelection() {
		Integer[] input = DetectorConfig.INSTANCE.getCurrentDetectorSetup().getStrips();
		cmbFirstStripViewer.setSelection(new StructuredSelection(input[0]));
		cmbLastStripViewer.setSelection(new StructuredSelection(input[input.length - 1]));
	}

	private void showROIs(Object detectorSetup) {
		if (detectorSetup == null) {
			cmbFirstStripViewer.setInput(new Integer[]{});
			cmbLastStripViewer.setInput(new Integer[]{});
			noOfRegionsList.clear();
			return;
		}

		Integer[] input = ((DetectorSetup) detectorSetup).getStrips();
		cmbFirstStripViewer.setInput(input);
		cmbLastStripViewer.setInput(((DetectorSetup) detectorSetup).getStrips());
		setDefaultSelection();

		XHROI[] rois = ((DetectorSetup) detectorSetup).getDetectorScannable().getRois();
		if (rois != null && rois.length > 0) {
			for (int i = 0; i < rois.length; i++) {
				noOfRegionsList.add(rois[i]);
			}
		} else {
			for (int i = 0; i < DetectorSetup.DEFAULT_NO_OF_REGIONS; i++) {
				noOfRegionsList.add(new XHROI(Integer.toString(i)));
			}
		}

		distributeNoOfRegionsValues();
	}

	protected void saveROIsChanges() {

		IStructuredSelection firstSelection = (IStructuredSelection) cmbFirstStripViewer.getSelection();
		IStructuredSelection  lastSelection = (IStructuredSelection) cmbLastStripViewer.getSelection();
		if (firstSelection.isEmpty() | lastSelection.isEmpty()){
			return;
		}
		DetectorConfig.INSTANCE.getCurrentDetectorSetup().getDetectorScannable().setLowerChannel((int) firstSelection.getFirstElement());
		DetectorConfig.INSTANCE.getCurrentDetectorSetup().getDetectorScannable().setUpperChannel((int) lastSelection.getFirstElement());
		DetectorConfig.INSTANCE.getCurrentDetectorSetup().getDetectorScannable().setRois(noOfRegionsList.toArray(new XHROI[]{}));
	}

	private void distributeNoOfRegionsValues() {
		IStructuredSelection firstSelection = (IStructuredSelection) cmbFirstStripViewer.getSelection();
		IStructuredSelection  lastSelection = (IStructuredSelection) cmbLastStripViewer.getSelection();
		if (firstSelection.isEmpty() | lastSelection.isEmpty() | noOfRegionsList.isEmpty()){
			return;
		}
		int first = (int) firstSelection.getFirstElement();
		int last = (int) lastSelection.getFirstElement();
		int useableRegion = last - (first - 1); // Inclusive of the first
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
		roisTableViewer.refresh();
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
				UIHelper.showWarning("Unable to set value", "value" + " is invalid");
			}
		}
	}

	@SuppressWarnings("static-access")
	private void createFormSlitsParametersSection(Form form) {
		final Section slitsParametersSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE);
		toolkit.paintBordersFor(slitsParametersSection);
		slitsParametersSection.setText("Slits scan");
		toolkit.paintBordersFor(slitsParametersSection);
		slitsParametersSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite slitsParametersSelectionComposite = toolkit.createComposite(slitsParametersSection, SWT.NONE);
		toolkit.paintBordersFor(slitsParametersSelectionComposite);
		slitsParametersSelectionComposite.setLayout(new GridLayout(2, false));
		slitsParametersSection.setClient(slitsParametersSelectionComposite);

		Label lbl = toolkit.createLabel(slitsParametersSelectionComposite, ClientConfig.ScannableSetup.SLIT_3_HORIZONAL_GAP.getLabelForUI(), SWT.NONE);
		lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

		final Text txtGap = toolkit.createText(slitsParametersSelectionComposite, "", SWT.None);
		txtGap.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));

		Binding bindValue = dataBindingCtx.bindValue(
				WidgetProperties.text(SWT.Modify).observe(txtGap),
				BeanProperties.value(SlitScanner.GAP_PROP_NAME).observe(SlitScanner.getInstance()),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_UPDATE).setBeforeSetValidator(new IValidator() {
					@Override
					public IStatus validate(Object value) {
						if (value instanceof Double) {
							if (SlitScanner.isGapInRange((double)value)) {
								return ValidationStatus.ok();
							}
							return ValidationStatus.error("Gap too large");
						}
						return ValidationStatus.error("Not a valid decimal value");
					}
				}),
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return ClientConfig.roundDoubletoString((double) value);
					}
				});
		ControlDecorationSupport.create(bindValue, SWT.TOP | SWT.RIGHT);

		lbl = toolkit.createLabel(slitsParametersSelectionComposite, UnitSetup.MILLI_METER.addUnitSuffixForLabel("From Offset"), SWT.NONE);
		lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

		// TODO Load from saved value
		final Spinner spnFromOffset = new Spinner(slitsParametersSelectionComposite, SWT.BORDER);
		spnFromOffset.setDigits(MAX_DECIMAL_PLACE);
		spnFromOffset.setIncrement(SPINNER_INCREMENT);
		spnFromOffset.setMaximum((int) SlitScanner.MAX_OFFSET * SPINNER_INCREMENT);
		spnFromOffset.setMinimum((int) SlitScanner.MIN_OFFSET * SPINNER_INCREMENT);
		spnFromOffset.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		toolkit.paintBordersFor(spnFromOffset);

		bindValue = dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(spnFromOffset),
				BeanProperties.value(SlitScanner.FROM_OFFSET_PROP_NAME).observe(SlitScanner.getInstance()),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_UPDATE) {
					@Override
					public Object convert(Object value) {
						return ((int) value) / SPINNER_INCREMENT;
					}
				}, null);
		ControlDecorationSupport.create(bindValue, SWT.TOP | SWT.RIGHT);


		lbl = toolkit.createLabel(slitsParametersSelectionComposite, "Steps: ", SWT.NONE);
		lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

		final Text txtStep = toolkit.createText(slitsParametersSelectionComposite, "", SWT.None);
		txtStep.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));

		bindValue = dataBindingCtx.bindValue(
				WidgetProperties.text(SWT.Modify).observe(txtStep),
				BeanProperties.value(SlitScanner.STEP_PROP_NAME).observe(SlitScanner.getInstance()),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_UPDATE).setBeforeSetValidator(new IValidator() {
					@Override
					public IStatus validate(Object value) {
						if (value instanceof Double) {
							return ValidationStatus.ok();
						}
						return ValidationStatus.error("Not a value decimal value");
					}
				}),
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return ClientConfig.roundDoubletoString((double) value);
					}
				});
		ControlDecorationSupport.create(bindValue, SWT.TOP | SWT.RIGHT);

		lbl = toolkit.createLabel(slitsParametersSelectionComposite, UnitSetup.MILLI_METER.addUnitSuffixForLabel("To Offset"), SWT.NONE);
		lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

		final Spinner spnToOffset = new Spinner(slitsParametersSelectionComposite, SWT.BORDER);
		spnToOffset.setDigits(MAX_DECIMAL_PLACE);
		spnToOffset.setIncrement(SPINNER_INCREMENT);
		spnToOffset.setMaximum((int) SlitScanner.MAX_OFFSET * SPINNER_INCREMENT);
		spnToOffset.setMinimum((int) SlitScanner.MIN_OFFSET * SPINNER_INCREMENT);
		spnToOffset.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		toolkit.paintBordersFor(spnToOffset);

		bindValue = dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(spnToOffset),
				BeanProperties.value(SlitScanner.TO_OFFSET_PROP_NAME).observe(SlitScanner.getInstance()),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_UPDATE){
					@Override
					public Object convert(Object value) {
						return ((Integer) value) / SPINNER_INCREMENT;
					}
				},
				null);
		ControlDecorationSupport.create(bindValue, SWT.TOP | SWT.RIGHT);

		lbl = toolkit.createLabel(slitsParametersSelectionComposite, UnitSetup.MILLI_SEC.addUnitSuffixForLabel("Integration Time"), SWT.NONE);
		lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));

		final Spinner integrationTime = new Spinner(slitsParametersSelectionComposite, SWT.BORDER);
		integrationTime.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		integrationTime.setMaximum(SlitScanner.MAX_INTEGRATION_TIME);
		integrationTime.setMinimum(SlitScanner.MIN_INTEGRATION_TIME);
		toolkit.paintBordersFor(integrationTime);

		bindValue = dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(integrationTime),
				BeanProperties.value(SlitScanner.INTEGRATION_TIME_PROP_NAME).observe(SlitScanner.getInstance()),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_UPDATE),
				null);
		ControlDecorationSupport.create(bindValue, SWT.TOP | SWT.RIGHT);

		Composite scanButtons = toolkit.createComposite(slitsParametersSelectionComposite);
		GridData gridData = new GridData(GridData.HORIZONTAL_ALIGN_FILL);
		gridData.horizontalSpan = 2;
		scanButtons.setLayoutData(gridData);
		scanButtons.setLayout(new GridLayout(2, true));

		Button startPauseButton = toolkit.createButton(scanButtons, "Start Scan", SWT.FLAT);
		startPauseButton.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(startPauseButton),
				BeanProperties.value(SlitScanner.STATE_PROP_NAME).observe(SlitScanner.getInstance()),
				null,
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return ((int) value == Jython.IDLE);
					}
				});

		startPauseButton.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				try {
					SlitScanner.getInstance().doScan();
				} catch (DetectorUnavailableException e) {
					UIHelper.showError("Unable to scan", e.getMessage());
				}
			}
		});

		Button stopButton = new Button(scanButtons, SWT.FLAT);
		stopButton.setText("Stop");
		stopButton.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(stopButton),
				BeanProperties.value(SlitScanner.STATE_PROP_NAME).observe(SlitScanner.getInstance()),
				null,
				new UpdateValueStrategy() {
					@Override
					public Object convert(Object value) {
						return ((int) value != Jython.IDLE);
					}
				});

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(slitsParametersSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		slitsParametersSection.setSeparatorControl(defaultSectionSeparator);

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(slitsParametersSection),
				BeansObservables.observeValue(DetectorConfig.INSTANCE, DetectorConfig.DETECTOR_CONNECTED_PROP_NAME),
				null,
				null);
	}
}