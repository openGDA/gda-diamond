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

package uk.ac.gda.exafs.alignment.ui;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.beans.BeansObservables;
import org.eclipse.core.databinding.observable.list.IListChangeListener;
import org.eclipse.core.databinding.observable.list.ListChangeEvent;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.databinding.viewers.ObservableListContentProvider;
import org.eclipse.jface.databinding.viewers.ViewersObservables;
import org.eclipse.jface.layout.TableColumnLayout;
import org.eclipse.jface.viewers.CellEditor;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jface.viewers.ColumnWeightData;
import org.eclipse.jface.viewers.EditingSupport;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.jface.viewers.TextCellEditor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.forms.widgets.TableWrapData;

import gda.device.detector.Roi;
import uk.ac.gda.client.ResourceComposite;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.data.DetectorModel;
import uk.ac.gda.exafs.data.DetectorModel.ROIsSetObserver;

public class DetectorROIsSection extends ResourceComposite {

	private static final int ROIS_TABLE_HEIGHT = 150;
	private static final int ROIs_TABLE_WIDTH = 70;

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private TableViewer roisTableViewer;
	private final FormToolkit toolkit;

	public DetectorROIsSection(Composite parent, int style) {
		super(parent, style);
		toolkit = new FormToolkit(parent.getDisplay());
		setupUI();
	}

	private void createIncludedStripsSelection() {
		IncludedStripsSectionComposite includedStripsSectionComposite = new IncludedStripsSectionComposite(this, SWT.None, toolkit);
		includedStripsSectionComposite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
	}

	private void setupUI() {
		createIncludedStripsSelection();
		createROISection();
	}


	private void createROISection() {
		this.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		final Section roisSection = toolkit.createSection(this, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		roisSection.setText("Region of Interests (ROIs)");
		toolkit.paintBordersFor(roisSection);
		roisSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		Composite roisSectionComposite = toolkit.createComposite(roisSection, SWT.NONE);
		toolkit.paintBordersFor(roisSectionComposite);
		roisSection.setClient(roisSectionComposite);
		roisSectionComposite.setLayout(new GridLayout());

		Composite regionsComposit = new Composite(roisSectionComposite, SWT.NONE);
		GridData gridData = new GridData(GridData.FILL, GridData.FILL, true, true);
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
		roisTableViewer.setContentProvider(new ObservableListContentProvider());
		roisTableViewer.getTable().setHeaderVisible(true);

		// Region No. column
		TableViewerColumn viewerNumberColumn = new TableViewerColumn(roisTableViewer, SWT.NONE);
		viewerNumberColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public String getText(Object element) {
				return ((Roi) element).getName();
			}
		});
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(2));
		viewerNumberColumn.getColumn().setText("Name");
		// Lower level column
		TableViewerColumn viewerlowerLevelColumn = new TableViewerColumn(roisTableViewer, SWT.NONE);

		viewerlowerLevelColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public String getText(Object element) {
				return Integer.toString(((Roi) element).getLowerLevel());
			}
		});
		// TODO add editing support
		// viewerlowerLevelColumn.setEditingSupport(new RoisStripLevelEditorSupport(roisTableViewer, false));
		layout.setColumnData(viewerlowerLevelColumn.getColumn(),new ColumnWeightData(4));
		viewerlowerLevelColumn.getColumn().setText("Lower level");

		// Upper level column
		TableViewerColumn viewerUpperLevelColumn = new TableViewerColumn(roisTableViewer, SWT.NONE);
		viewerUpperLevelColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public String getText(Object element) {
				return Integer.toString(((Roi) element).getUpperLevel());
			}
		});
		// TODO add editing support
		// viewerUpperLevelColumn.setEditingSupport(new RoisStripLevelEditorSupport(roisTableViewer, true));
		viewerUpperLevelColumn.getColumn().setText("Upper level");
		layout.setColumnData(viewerUpperLevelColumn.getColumn(),new ColumnWeightData(4));

		toolkit.paintBordersFor(regionsTableComposit);

		roisTableViewer.setInput(DetectorModel.INSTANCE.getRois());

		Composite buttonComposit = new Composite(regionsComposit, SWT.NONE);
		buttonComposit.setLayout(new GridLayout());
		buttonComposit.setLayoutData(new GridData(GridData.VERTICAL_ALIGN_FILL));
		final Button butAdd = new Button(buttonComposit, SWT.FLAT);
		butAdd.setText("Add");
		butAdd.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));
		butAdd.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				DetectorModel.INSTANCE.addRIO();
			}
		});

		final Button butRemove = new Button(buttonComposit, SWT.FLAT);
		butRemove.setText("Remove");
		butRemove.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));

		butRemove.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				DetectorModel.INSTANCE.removeRIO();
			}
		});

		Composite roisSectionSeparator = toolkit.createCompositeSeparator(roisSection);
		toolkit.paintBordersFor(roisSectionSeparator);
		roisSection.setSeparatorControl(roisSectionSeparator);

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(butAdd),
				BeansObservables.observeValue(DetectorModel.INSTANCE, DetectorModel.DETECTOR_CONNECTED_PROP_NAME));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(butRemove),
				BeansObservables.observeValue(DetectorModel.INSTANCE, DetectorModel.DETECTOR_CONNECTED_PROP_NAME));

		butRemove.setEnabled(DetectorModel.INSTANCE.getRois().size() > 1);

		DetectorModel.INSTANCE.getRois().addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				butRemove.setEnabled(DetectorModel.INSTANCE.getRois().size() > 1);
			}
		});

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(roisSection),
				BeansObservables.observeValue(DetectorModel.INSTANCE, DetectorModel.DETECTOR_CONNECTED_PROP_NAME));

		dataBindingCtx.bindValue(
				ViewersObservables.observeInput(roisTableViewer),
				BeanProperties.value(ROIsSetObserver.ROIS_PROP_NAME).observe(DetectorModel.INSTANCE.getRoisSetObserver()));
	}

	// TODO Add editor change support
	@SuppressWarnings("unused")
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
				return Integer.toString(((Roi) element).getUpperLevel());
			}
			return Integer.toString(((Roi) element).getLowerLevel());
		}

		@Override
		protected void setValue(Object element, Object value) {
			try {
				// TODO Do validation for overlapping values and boundary checking
				if (isEditingUpperLevel) {
					((Roi) element).setUpperLevel(Integer.parseInt((String) value));
				} else {
					((Roi) element).setLowerLevel(Integer.parseInt((String) value));
				}
				this.getViewer().update(element, null);
			} catch (NumberFormatException e) {
				UIHelper.showWarning("Unable to set value", "value" + " is invalid");
			}
		}
	}

	@Override
	protected void disposeResource() {
		dataBindingCtx.dispose();
	}
}
