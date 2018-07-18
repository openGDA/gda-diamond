/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.experiment.ui;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;

import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.CellEditor;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jface.viewers.ColumnViewer;
import org.eclipse.jface.viewers.EditingSupport;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.jface.viewers.TextCellEditor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.TableItem;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.scan.TurboSlitTimingGroup;
import gda.scan.TurboXasParameters;

/**
 * Class to provide GUI controls to edit timing groups stored in {@link TurboXasParameters} object.
 * A JFace {@link TableViewer} instance is used to perform the editing so that binding between
 * timing group model and gui is handled automatically.
 * @since May2017
 */
public class TurboXasTimingGroupTableView {

	private static Logger logger = LoggerFactory.getLogger(TurboXasTimingGroupTableView.class);

	private TableViewer tableView;
	private List<TurboSlitTimingGroup> timingGroups;

	private final Composite parent;

	public TurboXasTimingGroupTableView(Composite parent) {
		this.parent = parent;
	}

	public enum TimingGroupParamType {
		NAME("Group name"),
		TIME_PER_SPECTRUM("Time per. spectrum [s]"),
		TIME_BETWEEN_SPECTRA("Time between spectra [s]"),
		NUM_SPECTRA("Number of spectra");

		private final String enumName;
		private TimingGroupParamType(String name) {
			enumName = name;
		}

		public String getName() {
			return enumName;
		}
	};

	private class ParameterLabelProvider extends ColumnLabelProvider  {
		final TimingGroupParamType paramType;
		public ParameterLabelProvider(TimingGroupParamType paramIndex) {
			this.paramType = paramIndex;
		}
		@Override
		public String getText(Object element) {
			TurboSlitTimingGroup param = (TurboSlitTimingGroup) element;
			return getDataForColumn(param, paramType).toString();
		}
	};

	/**
	 * Get parameter from timing group object to go in column of table
	 *
	 * @param param
	 * @param paramIndex
	 * @return
	 */
	private Object getDataForColumn(TurboSlitTimingGroup param, TimingGroupParamType paramType) {
		String stringVal = "";
		switch (paramType) {
		case NAME:
			stringVal = param.getName();
			break;
		case TIME_PER_SPECTRUM:
			stringVal = String.valueOf(param.getTimePerSpectrum());
			break;
		case TIME_BETWEEN_SPECTRA:
			stringVal = String.valueOf(param.getTimeBetweenSpectra());
			break;
		case NUM_SPECTRA:
			stringVal = String.valueOf(param.getNumSpectra());
			break;
		}
		return stringVal;
	}

	private class ParameterValueEditingSupport extends EditingSupport {
		final TimingGroupParamType paramType;

		public ParameterValueEditingSupport(ColumnViewer viewer, TimingGroupParamType typeIndex) {
			super(viewer);
			this.paramType = typeIndex;
		}

		// Called to update value in model from value in edited cell of table
		@Override
		public void setValue(Object element, Object value) {
			TurboSlitTimingGroup param = (TurboSlitTimingGroup) element;
			setParameterFromColumnData(param, value, paramType);
			getViewer().update(param, null);
		}

		@Override
		protected CellEditor getCellEditor(Object element) {
			return new TextCellEditor((Composite) getViewer().getControl());
		}

		@Override
		protected boolean canEdit(Object element) {
			return true;
		}

		@Override
		protected Object getValue(Object element) {
			TurboSlitTimingGroup param = (TurboSlitTimingGroup) element;
			return getDataForColumn(param, paramType);
		}
	}

	/**
	 * Set new parameter using supplied string from column in table.
	 *
	 * @param param
	 * @param value
	 * @param columnNumber
	 */
	private void setParameterFromColumnData(TurboSlitTimingGroup paramForScan, Object value, TimingGroupParamType typeIndex) {
		String strValue = (String) value;
		if (strValue==null || strValue.trim().length()==0) {
			return;
		}
		try {
			switch (typeIndex) {
			case NAME:
				paramForScan.setName(strValue);
				break;
			case TIME_PER_SPECTRUM:
				paramForScan.setTimePerSpectrum(Double.parseDouble(strValue));
				break;
			case TIME_BETWEEN_SPECTRA:
				paramForScan.setTimeBetweenSpectra(Double.parseDouble(strValue));
				break;
			case NUM_SPECTRA:
				paramForScan.setNumSpectra(Integer.parseInt(strValue));
				break;
			}
		} catch (NumberFormatException nfe) {
			logger.warn("Problem converting {} to value {}", typeIndex.getName(), strValue, nfe);
		}
	}

	/** Default column order in the table */
	private TimingGroupParamType[] columnOrderInTable = {TimingGroupParamType.NAME, TimingGroupParamType.NUM_SPECTRA,
			TimingGroupParamType.TIME_PER_SPECTRUM, TimingGroupParamType.TIME_BETWEEN_SPECTRA};

	public void setColumnOrderInTable(TimingGroupParamType[] arr) {
		columnOrderInTable = arr;
	}

	private void addColumnsToTable(TableViewer viewer) {
		int minWidth = 75;

		for(TimingGroupParamType columnType : columnOrderInTable) {
			TableColumn column = new TableColumn(viewer.getTable(), SWT.NONE);
			column.setText(columnType.getName());
			column.setWidth(minWidth);
			TableViewerColumn columnViewer = new TableViewerColumn(viewer, column);
			columnViewer.setLabelProvider(new ParameterLabelProvider(columnType));
			columnViewer.setEditingSupport(new ParameterValueEditingSupport(viewer, columnType));
		}
	}

	/**
	 * Create the JFace {@link TableViewer} to edit timing groups. Adds columns to the table, sets up up listener used to initiate editing.
	 * @return TableViewer object
	 */
	public TableViewer createTable() {
		int style = SWT.BORDER | SWT.FULL_SELECTION |SWT.MULTI;
		tableView = new TableViewer(parent, style);
		tableView.getTable().setHeaderVisible(true);
		tableView.getTable().setLinesVisible(true);
		tableView.setContentProvider(new ArrayContentProvider());
		// set layout on the Table so it fills rest of composite
		tableView.getTable().setLayout(new FillLayout());
		tableView.getTable().setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true, 1, 1));

		addColumnsToTable(tableView);

		// Listener used to edit items in table
		tableView.getTable().addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				// Retrieve the model from the TableItem
				TableItem item = tableView.getTable().getSelection()[0];
				TurboSlitTimingGroup model = (TurboSlitTimingGroup) item.getData();
				// Invoke editing of the element
				tableView.editElement(model, 0);
			}
		});

		return tableView;
	}

	/**
	 * Set the timing groups to be viewed by the table from the {@link TurboXasParameters} parameters;
	 * @param params
	 */
	public void setTimingGroups(TurboXasParameters params) {
		timingGroups = params.getTimingGroups();
		tableView.setInput(timingGroups);
	}


	/**
	 * Remove timing group currently selected in table from the model; update the table view.
	 */
	public void removeSelectedTimingGroupFromModel() {
		TableItem[] selectedItems = tableView.getTable().getSelection();
		if (selectedItems == null || selectedItems.length == 0) {
			return; // nothing selected
		}

		// Make list of selected TurboSlitTimingGroups from array of TableItems
		List<TurboSlitTimingGroup> selectedGroups = new ArrayList<TurboSlitTimingGroup>();
		Arrays.asList(selectedItems).forEach(tableitem -> selectedGroups.add((TurboSlitTimingGroup)tableitem.getData()));

		// Remove selected group from timing group list
		Iterator<TurboSlitTimingGroup> iter = timingGroups.iterator();
		int selectionIndex = 0;
		while (iter.hasNext()) {
			TurboSlitTimingGroup overrides = iter.next();
			if (selectedGroups.contains(overrides)) {
				iter.remove();
			}else {
				selectionIndex++;
			}
		}
		selectionIndex = Math.max(0, selectionIndex-1);
		// Update viewer
		tableView.refresh();
		tableView.getTable().setSelection(selectionIndex);
	}

	/**
	 * Refresh the table to show current state of timingGroups.
	 */
	public void refresh() {
		tableView.refresh();
	}

	public TableViewer getTableViewer() {
		return this.tableView;
	}
}
