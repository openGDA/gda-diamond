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

import java.util.ArrayList;

import org.eclipse.jface.dialogs.MessageDialog;
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
import uk.ac.gda.exafs.ui.data.UIHelper;
import uk.ac.gda.exafs.ui.data.UIHelper.UIMotorControl;

public class FocusingFormComposite {

	private static final int ROIS_TABLE_HEIGHT = 150;
	private static final int ROIs_TABLE_WIDTH = 70;

	private ScrolledForm forcusingForm;
	private FormToolkit toolkit;

	private final ArrayList<XHROI> noOfRegionsList = new ArrayList<XHROI>();
	private ComboViewer cmbFirstStripViewer;
	private ComboViewer cmbLastStripViewer;
	private TableViewer roisTableViewer;

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
		cmbFirstStripViewer.setInput(DetectorSetup.STRIPS);

		Label lblLastStrip = toolkit.createLabel(stripsComposit, "Last strip:", SWT.NONE);
		lblLastStrip.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		CCombo cmbLastStrip = new CCombo(stripsComposit, SWT.BORDER | SWT.FLAT);
		cmbLastStrip.setEditable(false);
		cmbLastStrip.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		cmbLastStripViewer = new ComboViewer(cmbLastStrip);
		cmbLastStripViewer.setContentProvider(new ArrayContentProvider());
		cmbLastStripViewer.setLabelProvider(new LabelProvider());
		cmbLastStripViewer.setInput(DetectorSetup.STRIPS);

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
			}
		});

		butRemove.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				noOfRegionsList.remove(noOfRegionsList.size() - 1);
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
				roisSection.setExpanded(false);
			}
		});
		saveRoisTBarItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ETOOL_SAVE_EDIT));
		roisSection.setTextClient(roisSectionTbar);

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
	}

	protected void checkAndUpdateFirstAndLastStrips() {
		int first = (Integer) ((IStructuredSelection) cmbFirstStripViewer.getSelection()).getFirstElement();
		int last = (Integer) ((IStructuredSelection) cmbLastStripViewer.getSelection()).getFirstElement();
		if (last > first && (last - (first -1)) >= noOfRegionsList.size()) {
			// TODO Update to model
			distributeNoOfRegionsValues();
		} else {
			UIHelper.showWarning( "Unable to set strip value", "First strip is higher than last strip OR to many regions for usable number of strips");
			// TODO Update from model
			cmbFirstStripViewer.setSelection(new StructuredSelection(DetectorSetup.STRIPS[0]));
			cmbLastStripViewer.setSelection(new StructuredSelection(DetectorSetup.STRIPS[DetectorSetup.MAX_STRIPS - 1]));
		}
	}

	private void populateRegions() {
		// TODO Update from model
		cmbFirstStripViewer.setSelection(new StructuredSelection(DetectorSetup.STRIPS[0]));
		cmbLastStripViewer.setSelection(new StructuredSelection(DetectorSetup.STRIPS[DetectorSetup.MAX_STRIPS - 1]));
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
				MessageDialog.openWarning(Display.getDefault().getActiveShell(), "Warning", "Unable to set value" + "\n\nReason:\n" + "value" + " is invalid");
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
		UIHelper.createMotorViewer(toolkit, slitsParametersSelectionComposite, ScannableSetup.SLIT_3_HORIZONAL_GAP, UIMotorControl.ROTATION);

		lbl = toolkit.createLabel(slitsParametersSelectionComposite, ClientConfig.ScannableSetup.SLIT_3_HORIZONAL_OFFSET.getLabelForUI(), SWT.NONE);
		lbl.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		UIHelper.createMotorViewer(toolkit, slitsParametersSelectionComposite, ScannableSetup.SLIT_3_HORIZONAL_OFFSET, UIMotorControl.ROTATION);

		Composite scanButtons = toolkit.createComposite(slitsParametersSelectionComposite);
		GridData gridData = new GridData(GridData.HORIZONTAL_ALIGN_FILL);
		gridData.horizontalSpan = 2;
		scanButtons.setLayoutData(gridData);
		scanButtons.setLayout(new GridLayout(2, true));
		Button startPauseButton = new Button(scanButtons, SWT.FLAT);
		startPauseButton.setText("Start Scan");
		startPauseButton.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));

		Button stopButton = new Button(scanButtons, SWT.FLAT);
		stopButton.setText("Stop");
		stopButton.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		stopButton.setEnabled(false);

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(slitsParametersSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		slitsParametersSection.setSeparatorControl(defaultSectionSeparator);
	}
}