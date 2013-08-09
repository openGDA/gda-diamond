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

import gda.device.detector.StripDetector;
import gda.device.detector.XHDetector;
import gda.device.detector.XHROI;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.beans.BeansObservables;
import org.eclipse.core.databinding.observable.list.IListChangeListener;
import org.eclipse.core.databinding.observable.list.ListChangeEvent;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.databinding.viewers.ObservableListContentProvider;
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
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.forms.widgets.TableWrapData;

import uk.ac.gda.exafs.data.DetectorConfig;
import uk.ac.gda.exafs.ui.data.UIHelper;

public class DetectorROIsSesion {
	private static final int ROIS_TABLE_HEIGHT = 150;
	private static final int ROIs_TABLE_WIDTH = 70;
	public static final DetectorROIsSesion INSTANCE = new DetectorROIsSesion();

	private DataBindingContext dataBindingCtx = null;

	private ComboViewer cmbFirstStripViewer;
	private ComboViewer cmbLastStripViewer;
	private TableViewer roisTableViewer;

	private DetectorROIsSesion() {}

	@SuppressWarnings({ "static-access" })
	public void createSection(Form form, FormToolkit toolkit) {
		dataBindingCtx = new DataBindingContext();
		final Section roisSection = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE);
		roisSection.setText("Region of Interests (ROIs)");
		toolkit.paintBordersFor(roisSection);
		roisSection.setLayoutData(new TableWrapData(TableWrapData.FILL_GRAB));
		Composite roisSectionComposite = toolkit.createComposite(roisSection, SWT.NONE);
		toolkit.paintBordersFor(roisSectionComposite);
		roisSection.setClient(roisSectionComposite);
		roisSectionComposite.setLayout(new GridLayout());

		Composite stripsComposite = new Composite(roisSectionComposite, SWT.NONE);
		GridData gridData = new GridData(GridData.FILL, GridData.BEGINNING, true, true);

		stripsComposite.setLayoutData(gridData);
		stripsComposite.setLayout(new GridLayout(4, false));

		final Label lblFirstStrip = toolkit.createLabel(stripsComposite, "First strip:", SWT.NONE);
		lblFirstStrip.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		CCombo cmbFirstStrip = new CCombo(stripsComposite, SWT.BORDER | SWT.FLAT);
		cmbFirstStrip.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		cmbFirstStripViewer = new ComboViewer(cmbFirstStrip);
		cmbFirstStripViewer.setContentProvider(new ArrayContentProvider());
		cmbFirstStripViewer.setLabelProvider(new LabelProvider());
		cmbFirstStripViewer.setInput(XHDetector.getStrips());

		Label lblLastStrip = toolkit.createLabel(stripsComposite, "Last strip:", SWT.NONE);
		lblLastStrip.setLayoutData(new GridData(GridData.BEGINNING, GridData.CENTER, false, false));
		CCombo cmbLastStrip = new CCombo(stripsComposite, SWT.BORDER | SWT.FLAT);
		cmbLastStrip.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		cmbLastStripViewer = new ComboViewer(cmbLastStrip);
		cmbLastStripViewer.setContentProvider(new ArrayContentProvider());
		cmbLastStripViewer.setLabelProvider(new LabelProvider());
		cmbLastStripViewer.setInput(XHDetector.getStrips());

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
		roisTableViewer.setContentProvider(new ObservableListContentProvider());
		roisTableViewer.getTable().setHeaderVisible(true);

		// Region No. column
		TableViewerColumn viewerNumberColumn = new TableViewerColumn(roisTableViewer, SWT.NONE);
		viewerNumberColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public String getText(Object element) {
				return ((XHROI) element).getName();
			}
		});
		layout.setColumnData(viewerNumberColumn.getColumn(), new ColumnWeightData(2));
		viewerNumberColumn.getColumn().setText("Name");
		// Lower level column
		TableViewerColumn viewerlowerLevelColumn = new TableViewerColumn(roisTableViewer, SWT.NONE);

		viewerlowerLevelColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public String getText(Object element) {
				return Integer.toString(((XHROI) element).getLowerLevel());
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
				return Integer.toString(((XHROI) element).getUpperLevel());
			}
		});
		// TODO add editing support
		// viewerUpperLevelColumn.setEditingSupport(new RoisStripLevelEditorSupport(roisTableViewer, true));
		viewerUpperLevelColumn.getColumn().setText("Upper level");
		layout.setColumnData(viewerUpperLevelColumn.getColumn(),new ColumnWeightData(4));
		toolkit.paintBordersFor(regionsTableComposit);

		roisTableViewer.setInput(DetectorConfig.INSTANCE.getRois());

		Composite buttonComposit = new Composite(regionsComposit, SWT.NONE);
		buttonComposit.setLayout(new GridLayout());
		buttonComposit.setLayoutData(new GridData(GridData.VERTICAL_ALIGN_FILL));
		final Button butAdd = new Button(buttonComposit, SWT.FLAT);
		butAdd.setText("Add");
		butAdd.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));
		butAdd.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				DetectorConfig.INSTANCE.addRIO();
			}
		});

		final Button butRemove = new Button(buttonComposit, SWT.FLAT);
		butRemove.setText("Remove");
		butRemove.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));

		butRemove.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				DetectorConfig.INSTANCE.removeRIO();
			}
		});

		Composite roisSectionSeparator = toolkit.createCompositeSeparator(roisSection);
		toolkit.paintBordersFor(roisSectionSeparator);
		roisSection.setSeparatorControl(roisSectionSeparator);

		DetectorConfig.INSTANCE.addPropertyChangeListener(DetectorConfig.CURRENT_DETECTOR_SETUP_PROP_NAME, new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				Object value = evt.getNewValue();
				if (value != null) {
					StripDetector detector = (StripDetector) value;
					cmbFirstStripViewer.setSelection(new StructuredSelection(detector.getLowerChannel()));
					cmbLastStripViewer.setSelection(new StructuredSelection(detector.getUpperChannel()));
				}
			}
		});

		cmbFirstStripViewer.addSelectionChangedListener(new ISelectionChangedListener() {
			@Override
			public void selectionChanged(SelectionChangedEvent event) {
				// TODO User data binding validation
				IStructuredSelection selection = (IStructuredSelection) event.getSelection();
				if (!selection.isEmpty()) {
					DetectorConfig.INSTANCE.getCurrentDetector().setLowerChannel((int) selection.getFirstElement());
					DetectorConfig.INSTANCE.reloadROIs();
				} else {
					String value = ((ComboViewer) event.getSource()).getCCombo().getText();
					try {
						int strip = Integer.parseInt(value);
						if (strip > 0 & strip < DetectorConfig.INSTANCE.getCurrentDetector().getUpperChannel()) {
							DetectorConfig.INSTANCE.getCurrentDetector().setLowerChannel(strip);
							DetectorConfig.INSTANCE.reloadROIs();
						} else {
							throw new NumberFormatException("Out of range");
						}
					} catch(NumberFormatException e) {
						UIHelper.showError("Unable to update", "Unvalid number");
					}
				}
			}
		});

		cmbLastStripViewer.addSelectionChangedListener(new ISelectionChangedListener() {
			@Override
			public void selectionChanged(SelectionChangedEvent event) {
				// TODO User data binding validation
				IStructuredSelection selection = (IStructuredSelection) event.getSelection();
				if (!selection.isEmpty()) {
					DetectorConfig.INSTANCE.getCurrentDetector().setUpperChannel((int) selection.getFirstElement());
					DetectorConfig.INSTANCE.reloadROIs();
				} else {
					String value = ((ComboViewer) event.getSource()).getCCombo().getText();
					try {
						int strip = Integer.parseInt(value);
						if (strip < DetectorConfig.INSTANCE.getCurrentDetector().getNumberChannels() & strip > DetectorConfig.INSTANCE.getCurrentDetector().getLowerChannel()) {
							DetectorConfig.INSTANCE.getCurrentDetector().setUpperChannel(strip);
							DetectorConfig.INSTANCE.reloadROIs();
						} else {
							throw new NumberFormatException("Out of range");
						}
					} catch(NumberFormatException e) {
						UIHelper.showError("Unable to update", "Unvalid number");
					}
				}
			}
		});

		if (DetectorConfig.INSTANCE.getCurrentDetector() != null) {
			cmbFirstStripViewer.setSelection(new StructuredSelection(DetectorConfig.INSTANCE.getCurrentDetector().getLowerChannel()));
			cmbLastStripViewer.setSelection(new StructuredSelection(DetectorConfig.INSTANCE.getCurrentDetector().getUpperChannel()));
		}

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(cmbFirstStripViewer.getControl()),
				BeansObservables.observeValue(DetectorConfig.INSTANCE, DetectorConfig.DETECTOR_CONNECTED_PROP_NAME));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(cmbLastStripViewer.getControl()),
				BeansObservables.observeValue(DetectorConfig.INSTANCE, DetectorConfig.DETECTOR_CONNECTED_PROP_NAME));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(butAdd),
				BeansObservables.observeValue(DetectorConfig.INSTANCE, DetectorConfig.DETECTOR_CONNECTED_PROP_NAME));

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(butRemove),
				BeansObservables.observeValue(DetectorConfig.INSTANCE, DetectorConfig.DETECTOR_CONNECTED_PROP_NAME));

		butRemove.setEnabled(DetectorConfig.INSTANCE.getRois().size() > 1);

		DetectorConfig.INSTANCE.getRois().addListChangeListener(new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				butRemove.setEnabled(DetectorConfig.INSTANCE.getRois().size() > 1);
			}
		});

		dataBindingCtx.bindValue(
				WidgetProperties.enabled().observe(roisSection),
				BeansObservables.observeValue(DetectorConfig.INSTANCE, DetectorConfig.DETECTOR_CONNECTED_PROP_NAME));


	}

	// TODO Add editor change support
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
}
