/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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

import java.text.NumberFormat;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.apache.commons.lang.StringUtils;
import org.eclipse.jface.bindings.keys.IKeyLookup;
import org.eclipse.jface.bindings.keys.KeyLookupFactory;
import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.CellEditor;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jface.viewers.ColumnViewer;
import org.eclipse.jface.viewers.ColumnViewerEditor;
import org.eclipse.jface.viewers.ColumnViewerEditorActivationEvent;
import org.eclipse.jface.viewers.ColumnViewerEditorActivationStrategy;
import org.eclipse.jface.viewers.EditingSupport;
import org.eclipse.jface.viewers.FocusCellOwnerDrawHighlighter;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.jface.viewers.TableViewerEditor;
import org.eclipse.jface.viewers.TableViewerFocusCellManager;
import org.eclipse.jface.viewers.TextCellEditor;
import org.eclipse.jface.viewers.ViewerCell;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.swt.widgets.Text;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.scannable.ScannableUtils;

/**
 * Class to present a editable list of positions in a table. Rows of values can be added, deleted, and cells edited individually.
 * Multi-select can be used to select multiple rows to be removed.
 *
 * <li> To use the table, the names of the columns must first be set by calling {@link #setColumnNames(List)};
 * values may then be load into the table by calling {@link #setTableValues(List)}.
 * <li> Several rows covering a range of values for one of the columns specified by start, stop, step can also be added.
 * In this case the selected cell is copied and values in the specified column takes the range values.
 * <li> Values to be used when adding new row of values can be set using {@link #setNewRowValues(Double[])}. Zeros are used by default.
 *
 *
 */
public class NumberTableEditor extends Dialog {
	private static final Logger logger = LoggerFactory.getLogger(NumberTableEditor.class);


	/**
	 * Model viewed by Jface table. Each element in the list is a row in the table; each element in the array is a value in a column
	 */
	private List< Double[]> tableValues = new ArrayList<>();

	/**
	 * Names of the columns in the table. This should be same length as number of items in each row...
	 */
	private List<String> columnNames = Collections.emptyList();
	private List<String> columnFormats = Collections.emptyList();
	private String windowTitle = "Edit table of numbers";

	/** Values to be used when adding a new row to table */
	private Double[] newRowValue;

	/** Index in table of each column name */
	private Map<String, Integer> indexForColumn;

	private TableViewer tableView;

	/** Initial size of the dialog */
	private Point initialSize = new Point(700, 400);

	public NumberTableEditor(Shell parentShell) {
		super(parentShell);
	}

	@Override
	protected Control createDialogArea(Composite parent) {
		Composite mainDialogArea = (Composite) super.createDialogArea(parent);

		tableView = new TableViewer(mainDialogArea,  SWT.MULTI | SWT.BORDER | SWT.HIDE_SELECTION | SWT.FULL_SELECTION);
		tableView.getTable().setHeaderVisible(true);
		tableView.getTable().setLinesVisible(true);
		tableView.setContentProvider(ArrayContentProvider.getInstance());
		tableView.getTable().setLayout(new FillLayout());
		GridDataFactory.fillDefaults().grab(true, true).applyTo(tableView.getTable());

		addTableColumns();

		tableView.setInput(tableValues);

		setupForCursorNavigation(tableView);

		addButtons(mainDialogArea);

		setDefaultRowValue();

		// Add row to table if it is initially empty
		if (tableValues.isEmpty()) {
			addDefaultRowValue();
		}

		return mainDialogArea;
	}


	@Override
	protected Point getInitialSize() {
		return initialSize;
	}

	protected void setInitialSize(Point initialSize) {
		this.initialSize = initialSize;
	}

	/**
	 * Create default values for new row of data if not already set, or it mismatches the number of columns
	 */
	private void setDefaultRowValue() {
		if (newRowValue == null || newRowValue.length != columnNames.size()) {
			newRowValue = new Double[columnNames.size()];
			Arrays.fill(newRowValue, 0.0);
		}
	}

	@Override
	protected void configureShell(Shell shell) {
		super.configureShell(shell);
		shell.setText(windowTitle);
	}

	@Override
	protected boolean isResizable() {
		return true;
	}

	private void addTableColumns() {
		// Add a column to show the row number
		TableColumn rcolumn = new TableColumn(tableView.getTable(), SWT.NONE);
		rcolumn.setWidth(50);
		TableViewerColumn rowColumn = new TableViewerColumn(tableView, rcolumn);
		rowColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public void update(ViewerCell cell) {
				cell.setText(tableView.getTable().indexOf((TableItem)cell.getItem())+"");
			}
		});

		for(int i=0; i<columnNames.size(); i++) {
			String name = columnNames.get(i);
			TableColumn column = new TableColumn(tableView.getTable(), SWT.NONE);
			column.setText(name);
			column.setWidth(100);
			TableViewerColumn columnViewer = new TableViewerColumn(tableView, column);
			columnViewer.setEditingSupport(new StringValueEditingSupport(tableView, name));
			if (columnFormats.size()>i) {
				columnViewer.setLabelProvider(new StringValueLabelProvider(name, columnFormats.get(i)));
			} else {
				columnViewer.setLabelProvider(new StringValueLabelProvider(name));

			}
		}
	}

	private void addButtons(Composite parent) {
		Composite composite = new Composite(parent, SWT.NONE);
		composite.setLayout(new GridLayout(3, true));
		GridDataFactory.fillDefaults().grab(true, false).hint(SWT.DEFAULT, 50).applyTo(composite);

		GridDataFactory gridDataFactory = GridDataFactory.fillDefaults().align(SWT.FILL, SWT.CENTER).grab(true, true);
		Button addButton = new Button(composite, SWT.PUSH);
		addButton.setText("Add row");
		addButton.setToolTipText("Add a new row of values to the table after the currently selected row. Values are added to the end of the table if nothing is selected.");
		gridDataFactory.applyTo(addButton);
		addButton.addListener(SWT.Selection, event -> addDefaultRowValue());

		Button addRangeButton = new Button(composite, SWT.PUSH);
		addRangeButton.setText("Add/insert range of values");
		gridDataFactory.applyTo(addRangeButton);
		addRangeButton.addListener(SWT.Selection, e -> addInsertRange());

		Button removeButton = new Button(composite, SWT.PUSH);
		removeButton.setText("Remove row(s)");
		removeButton.setToolTipText("Remove the currently selected row(s) from the table");
		gridDataFactory.applyTo(removeButton);
		removeButton.addListener(SWT.Selection, e -> removeItems());
	}

	private void addInsertRange() {
		RangeDialog rangeDialog = new RangeDialog(getParentShell());
		rangeDialog.setAxesNames(columnNames);
		rangeDialog.setBlockOnOpen(true);
		if (rangeDialog.open() == Window.OK) {
			List<Double> rangeValues = rangeDialog.getValues();
			String selectedAxis = rangeDialog.getSelectedAxisName();
			Double[] selectedItem = getSelectedItem();
			int axisIndex = indexForColumn.get(selectedAxis);

			// Generate the new list of row values
			List<Double[]> valuesToAdd = new ArrayList<>();
			for (Double value : rangeValues) {
				Double[] newRow = selectedItem.clone();
				newRow[axisIndex] = value;
				valuesToAdd.add(newRow);
			}

			// Get index of where the values should be added to table - after currently selected item
			int insertionIndex = 1 + tableView.getTable().getSelectionIndex();
			tableValues.addAll(insertionIndex, valuesToAdd);
			tableView.refresh();
			// select last item added
			setSelectedItem(insertionIndex+valuesToAdd.size()-1);
		}
	}

	/**
	 *
	 * @return values in the currently selected row; Return {@link #newRowValue} if nothing is selected.
	 */
	private Double[] getSelectedItem() {
		int selectedIndex = tableView.getTable().getSelectionIndex();
		if (selectedIndex!=-1) {
			return tableValues.get(selectedIndex);
		} else {
			return newRowValue.clone();
		}
	}

	/**
	 * Set the selected (highlighted) row in the table.
	 * @param index of the item in the tableViewer model to be selected
	 */
	private void setSelectedItem(int index) {
		int selectedIndex = Math.min(index, tableValues.size()-1);
		selectedIndex = Math.max(0,  selectedIndex);
		// cast selected item object, since we are are selecting a single item but each item is an array.
		ISelection selection = new StructuredSelection((Object)tableValues.get(selectedIndex));
		tableView.setSelection(selection, true);
	}

	private void addDefaultRowValue() {
		addInsertItem(newRowValue.clone());
	}

	/**
	 * Add/new row to table. If something is selected, new item is added after it.
	 * Otherwise item is added to the start of the table.
	 * New item is selected after it has been added
	 * @param item
	 */
	private void addInsertItem(Double[] item) {
		int selectedIndex = tableView.getTable().getSelectionIndex();
		if (selectedIndex!=-1) {
			int newSelectedIndex = selectedIndex+1;
			if (selectedIndex < tableValues.size()-1) {
				// add after currently selected item
				tableValues.add(newSelectedIndex, item);
			} else {
				// last item selected, add to end
				tableValues.add(item);
				newSelectedIndex=tableValues.size()-1;
			}
			tableView.refresh();
			setSelectedItem(newSelectedIndex);
		} else {
			// Nothing selected, add to end of table
			tableValues.add(item);
			tableView.refresh();
			setSelectedItem(tableValues.size()-1);
		}
	}

	/**
	 * Remove selected item(s) from the table.
	 */
	private void removeItems() {
		TableItem[] selectedItems = tableView.getTable().getSelection();
		logger.debug("Removing {} from table ", Arrays.asList(selectedItems));
		if (selectedItems == null || selectedItems.length == 0) {
			return; // nothing to do
		}

		// Make list of the the values in the rows selected to be removed
		List<Double[]> positionsToRemove = Arrays.stream(selectedItems)
				.map(val -> (Double[])val.getData())
				.collect(Collectors.toList());

		// Remove selected rows from model
		int count = 0;
		int lastRemovedIndex = 0;
		Iterator<Double[]> iter = tableValues.iterator();
		while (iter.hasNext()) {
			Double[] rowValues = iter.next();
			if (positionsToRemove.contains(rowValues)) {
				iter.remove();
				lastRemovedIndex = count;
			}
			count++;
		}

		tableView.refresh();
		setSelectedItem(Math.min(lastRemovedIndex, tableValues.size()-1));
	}



	/**
	 * Set the names of the columns in the table. If data has been set using {@link #setTableValues(List)}, the number of column
	 * names should match the actual number of columns of data.
	 * @param columnNames
	 */
	public void setColumnNames(List<String> columnNames) {
		this.columnNames = columnNames;
		// Make map from name of column to index
		indexForColumn = new HashMap<>();
		IntStream.range(0, columnNames.size())
				  .forEach( index -> indexForColumn.put(columnNames.get(index), index));
		setDefaultRowValue();
	}

	public void setColumnFormats(List<String> columnFormats) {
		this.columnFormats = new ArrayList<>(columnFormats);
	}

	public List< List<Double>> getTableValues() {
		int numColumns = tableValues.get(0).length;
		int numRows = tableValues.size();
		List< List<Double> > values = new ArrayList<>(tableValues.get(0).length);
		for(int col=0; col<numColumns; col++) {
			List<Double> colValues = new ArrayList<>();
			for(int row=0; row<numRows; row++) {
				colValues.add(tableValues.get(row)[col]);
			}
			values.add(colValues);
		}
		return values;
	}

	/**
	 * Set values in the table.
	 * @param values List of lists - each list is set of values to go in a column.
	 */
	public void setTableValues(List< List<Double>> values) {
		if (values == null || values.isEmpty()) {
			return;
		}
		if (values.size() != columnNames.size())  {
			tableValues = new ArrayList<>();
			return;
		}
		int numColumns = values.size();
		int numRows = values.get(0).size();
		tableValues = new ArrayList<>(numRows);
		for(int i=0; i<numRows; i++) {
			Double[] rowValues = new Double[numColumns];
			for(int j=0; j<numColumns; j++) {
				rowValues[j] = values.get(j).get(i);
			}
			tableValues.add(rowValues);
		}
	}

	/**
	 * Set the values to be used when adding a new row to the table.
	 * @param newRowValue
	 */
	public void setNewRowValues(Double[] newRowValue) {
		this.newRowValue = newRowValue;
	}

	public void setWindowTitle(String windowTitle) {
		this.windowTitle = windowTitle;
	}

	/**
	 * Label provider for string parameter value
	 */
	private class StringValueLabelProvider extends ColumnLabelProvider  {
		private final String columnName;
		private final String format;

		public StringValueLabelProvider(String columnName) {
			this.columnName = columnName;
			format = "";
		}

		public StringValueLabelProvider(String columnName, String columnFormat) {
			this.columnName = columnName;
			this.format = columnFormat;
		}

		@Override
		public String getText(Object element) {
			Double[] values = (Double[]) element;
			Double value = values[indexForColumn.get(columnName)];
			logger.debug("GetText {}", value);
			if (StringUtils.isNotEmpty(format)) {
				return String.format(format, value.doubleValue());
			} else {
				return value.toString();
			}
		}
	}

	/**
	 *  Editing support for entering parameter value as text string
	 */
	private class StringValueEditingSupport extends EditingSupport {
		private final String columnName;

		public StringValueEditingSupport(ColumnViewer viewer, String columnName) {
			super(viewer);
			this.columnName = columnName;
		}

		// Called to update value in model from value in edited cell of table
		@Override
		public void setValue(Object element, Object newValue) {
			Double[] elementInModel = (Double[]) element;
			int index = indexForColumn.get(columnName);
			if (newValue == null || newValue.toString().isEmpty()) {
				elementInModel[index] = 0.0;
			} else {
				elementInModel[index] = parseNumber(newValue.toString());
			}
			logger.debug("setValue({}, {})", elementInModel, newValue.toString());

			getViewer().update(element, null);
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
			Double[] param = (Double[]) element;
			logger.debug("getValue({})", element);
			return param[ indexForColumn.get(columnName)].toString();
		}
	}

	/**
	 * Parse the supplied text string into a number. It is fairly forgiving and will discard
	 * any trailing non numeric input.
	 * 0 is returned if the number cannot be converted.
	 * @param numberText
	 * @return
	 */
	private static double parseNumber(String numberText) {
		double number = 0;
		try {
			if (!StringUtils.isEmpty(numberText)) {
				number = NumberFormat.getInstance().parse(numberText.toUpperCase()).doubleValue();
			}
		} catch (ParseException e) {
			logger.error("Problem parsing number {}. Using zero instead", numberText, e);
		}
		return number;
	}

	/**
	 * Dialog used for generating a sequence of evenly spaced value from user specified start, stop, step values.
	 * {@link #getValues()} returns the list of the values in the sequence.
	 *
	 */
	private static class RangeDialog extends Dialog {

		private Text startText;
		private Text endText;
		private Text stepSizeText;
		private Combo axisSelectionCombo;

		private List<String> axesNames = Collections.emptyList();

		private double start;
		private double stop;
		private double step;
		private String selectedAxisName = "";

		public RangeDialog(Shell parentShell) {
			super(parentShell);
		}

		@Override
		protected Control createDialogArea(Composite parent) {
			Composite mainComposite = (Composite) super.createDialogArea(parent);
			mainComposite.setLayout(new GridLayout(2, false));
			mainComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, true, 1, 1));

			GridDataFactory labelGridFactory = GridDataFactory.fillDefaults().align(SWT.LEFT,  SWT.CENTER).grab(false, true);
			GridDataFactory textBoxGridFactory = GridDataFactory.fillDefaults().align(SWT.FILL, SWT.CENTER).grab(true, true);

			Label startLabel = new Label(mainComposite, SWT.NONE);
			startLabel.setText("Start value");
			labelGridFactory.applyTo(startLabel);

			startText = new Text(mainComposite, SWT.NONE);
			textBoxGridFactory.applyTo(startText);

			Label endLabel = new Label(mainComposite, SWT.NONE);
			endLabel.setText("End value");
			labelGridFactory.applyTo(endLabel);

			endText = new Text(mainComposite, SWT.NONE);
			textBoxGridFactory.applyTo(endText);

			Label stepSizeLabel = new Label(mainComposite, SWT.NONE);
			stepSizeLabel.setText("Step size");
			labelGridFactory.applyTo(stepSizeLabel);

			stepSizeText = new Text(mainComposite, SWT.NONE);
			stepSizeText.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, true, 1, 1));
			textBoxGridFactory.applyTo(stepSizeText);

			if (!axesNames.isEmpty()) {
				Label axisSelectionLabel = new Label(mainComposite, SWT.NONE);
				axisSelectionLabel.setText("Apply values to column : ");

				axisSelectionCombo = new Combo(mainComposite, SWT.READ_ONLY);
				axisSelectionCombo.setItems(axesNames.toArray(new String[0]));
				axisSelectionCombo.setToolTipText("Column the generated values should be applied to. Values in other columns are constant (same values as in selected row)");
				axisSelectionCombo.select(0);
			}

			return mainComposite;
		}

		@Override
		protected void okPressed() {
			start = parseNumber(startText.getText());
			stop = parseNumber(endText.getText());
			step = parseNumber(stepSizeText.getText());
			if (axisSelectionCombo != null) {
				selectedAxisName = axisSelectionCombo.getText();
			}
			super.okPressed();
		}

		public String getSelectedAxisName() {
			return selectedAxisName;
		}

		/**
		 *
		 * @return List of values between start, stop evenly spaced by the stepsize.
		 */
		public List<Double> getValues() {
			int numberPoints = 1+ScannableUtils.getNumberSteps(start, stop, step);
			List<Double> points = new ArrayList<>();
			double stepSize = stop > start ? Math.abs(step) : -1.0*Math.abs(step);
			for (int i = 0; i < numberPoints; i++) {
				points.add(start + i*stepSize);
			}
			return points;
		}

		public void setAxesNames(List<String> axesNames) {
			this.axesNames = axesNames;
		}

		@Override
		protected Point getInitialSize() {
			return new Point(350, 250);
		}

		@Override
		protected boolean isResizable() {
			return true;
		}
	}


	// Magic tweaks so to allow cursor keys to be used to navigate between elements in the table...
	// (from Snippet035TableCursorCellHighlighter)
	public static void setupForCursorNavigation(TableViewer v) {
		TableViewerFocusCellManager focusCellManager = new TableViewerFocusCellManager(v, new FocusCellOwnerDrawHighlighter(v));
		ColumnViewerEditorActivationStrategy actSupport = new ColumnViewerEditorActivationStrategy(v) {
			@Override
			protected boolean isEditorActivationEvent(ColumnViewerEditorActivationEvent event) {
				return super.isEditorActivationEvent(event)
						|| (event.eventType == ColumnViewerEditorActivationEvent.KEY_PRESSED
						&& (event.keyCode == KeyLookupFactory.getDefault().formalKeyLookup(IKeyLookup.ENTER_NAME)));
			}
		};

		int features = ColumnViewerEditor.TABBING_HORIZONTAL | ColumnViewerEditor.TABBING_MOVE_TO_ROW_NEIGHBOR
					 | ColumnViewerEditor.TABBING_VERTICAL | ColumnViewerEditor.KEYBOARD_ACTIVATION;

		TableViewerEditor.create(v, focusCellManager, actSupport, features);
	}

	/**
	 * Useful for testing
	 * @param args
	 */
	public static void main(String[] args) {
		Display display = new Display();
		final Shell shell = new Shell(display);
		shell.setLayout(new GridLayout(1, true));
		shell.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, true, 1, 1));

		NumberTableEditor numberTable = new NumberTableEditor(shell);
		numberTable.setColumnNames(Arrays.asList("column1", "column2"));
		List< List<Double>> tableValues = new ArrayList<>();
		tableValues.add(Arrays.asList(1.0, 2.0,3.0,4.0,5.0,6.0));
		tableValues.add(Arrays.asList(1.1,2.2,3.3,4.4,5.5,6.6));

		numberTable.setTableValues(tableValues);
		numberTable.createDialogArea(shell);

		shell.open();

		// Set up the event loop.
		while (!shell.isDisposed()) {
			if (!display.readAndDispatch()) {
				// If no more entries in event queue
				display.sleep();
			}
		}
		display.dispose();
	}

}
