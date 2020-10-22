/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

import static org.eclipse.swt.events.SelectionListener.widgetSelectedAdapter;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Optional;

import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.jface.dialogs.IInputValidator;
import org.eclipse.jface.dialogs.InputDialog;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.CellEditor;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jface.viewers.ColumnViewer;
import org.eclipse.jface.viewers.ComboBoxCellEditor;
import org.eclipse.jface.viewers.DialogCellEditor;
import org.eclipse.jface.viewers.EditingSupport;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.jface.viewers.TextCellEditor;
import org.eclipse.jface.window.Window;
import org.eclipse.richbeans.widgets.cell.SpinnerCellEditor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.KeyAdapter;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.swt.widgets.Text;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.device.Scannable;
import gda.factory.Findable;
import gda.factory.Finder;
import gda.scan.SpectrumEvent;
import gda.scan.TurboSlitTimingGroup;

public class SpectrumEventsEditor extends Dialog {

	private static final Logger logger = LoggerFactory.getLogger(SpectrumEventsEditor.class);

	private TableViewer tableView;
	private List<SpectrumEvent> tableValues = new ArrayList<>();
	/** Initial size of the dialog */
	private Point initialSize = new Point(700, 400);
	private SpectrumEvent defaultRow = new SpectrumEvent(1, "test", 10);

	public SpectrumEventsEditor(Shell parentShell) {
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

		addButtons(mainDialogArea);
		addTableColumns();

		tableView.setInput(tableValues);

		NumberTableEditor.setupForCursorNavigation(tableView);

		return mainDialogArea;
	}

	public List<SpectrumEvent> getTableValues() {
		return tableValues;
	}

	public void setTableValues(List<SpectrumEvent> tableValues) {
		this.tableValues = new ArrayList<>();
		if (tableValues != null) {
			this.tableValues.addAll(tableValues);
		}
	}

	@Override
	protected boolean isResizable() {
		return true;
	}

	@Override
	protected Point getInitialSize() {
		return initialSize;
	}

	@Override
	protected void createButtonsForButtonBar(Composite parent) {
		// create OK and Cancel buttons by default
		// same as in Dialog, but defaultButton set to false (so dialog doesn't close when enter is pressed)
		createButton(parent, IDialogConstants.OK_ID, IDialogConstants.OK_LABEL, false);
		createButton(parent, IDialogConstants.CANCEL_ID, IDialogConstants.CANCEL_LABEL, false);
	}

	@Override
	public boolean close() {
		getReturnCode();
		return super.close();
	}

	@Override
	protected void handleShellCloseEvent() {
		if (tableView.isCellEditorActive() || !tableView.getSelection().isEmpty()) {
			return; // do nothing
		}
		setReturnCode(CANCEL);
		close();
	}

	@Override
	protected void cancelPressed() {
		setReturnCode(CANCEL);
		close();
	}

	private void addTableColumns() {
		// Add column for spectrum number
		TableViewerColumn spectrumNumColumn = new TableViewerColumn(tableView, SWT.NONE);
		spectrumNumColumn.getColumn().setWidth(200);
		spectrumNumColumn.getColumn().setText("Spectrum Number");
		spectrumNumColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
		    public String getText(Object element) {
				SpectrumEvent event = (SpectrumEvent) element;
				return Integer.toString(event.getSpectrumNumber());
		    }
		});

		spectrumNumColumn.setEditingSupport(new SpectrumNumberEditingSupport(tableView));
		addSelectionListener(spectrumNumColumn, 0);

		// Add column for spectrum number
		TableViewerColumn spectrumTimeColumn = new TableViewerColumn(tableView, SWT.NONE);
		spectrumTimeColumn.getColumn().setWidth(200);
		spectrumTimeColumn.getColumn().setText("Event start time");
		spectrumTimeColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
		    public String getText(Object element) {
				SpectrumEvent event = (SpectrumEvent) element;
				double timeAtSpectrumStart = getTimeAtSpectrumEnd(event.getSpectrumNumber());
				return String.format("%.4g s", timeAtSpectrumStart);
		    }
		});

		// Add column for name of scannable
		TableViewerColumn scannableNameColumn = new TableViewerColumn(tableView, SWT.NONE);
		scannableNameColumn.getColumn().setWidth(200);
		scannableNameColumn.getColumn().setText("Scannable Name");
		scannableNameColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
		    public String getText(Object element) {
				SpectrumEvent event = (SpectrumEvent) element;
		        return event.getScannableName();
		    }
		});
		scannableNameColumn.setEditingSupport(new ScannableNameEditingSupport(tableView));
		addSelectionListener(scannableNameColumn, 1);

		// Add column for scannable position
		TableViewerColumn scannablePositionColumn = new TableViewerColumn(tableView, SWT.NONE);
		scannablePositionColumn.getColumn().setWidth(200);
		scannablePositionColumn.getColumn().setText("Position");
		scannablePositionColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
		    public String getText(Object element) {
				SpectrumEvent event = (SpectrumEvent) element;
		        return event.getPosition().toString();
		    }
		});
		scannablePositionColumn.setEditingSupport(new PositionEditingSupport(tableView));
	}

	private void addButtons(Composite parent) {
		Composite composite = new Composite(parent, SWT.None);
		composite.setLayout(new GridLayout(3,  true));

		GridDataFactory gridDataFactory = GridDataFactory.fillDefaults().align(SWT.FILL, SWT.CENTER).grab(true, true);

		// Button to add new row to table (with default values)
		Button addButton = new Button(composite, SWT.PUSH);
		addButton.setText("Add new row");
		addButton.setToolTipText("Add a new row of values to the table after the currently selected row. Values are added to the end of the table if nothing is selected.");
		gridDataFactory.applyTo(addButton);
		addButton.addListener(SWT.Selection, event -> {
			tableValues.add(new SpectrumEvent(defaultRow));
			tableView.refresh();
		});

		// Button to copy selected row(s) to bottom of table
		Button addRangeButton = new Button(composite, SWT.PUSH);
		addRangeButton.setText("Copy row(s)");
		gridDataFactory.applyTo(addRangeButton);
		addRangeButton.addListener(SWT.Selection, e -> copyRows());

		// Button to remove row(s) from the table
		Button removeButton = new Button(composite, SWT.PUSH);
		removeButton.setText("Remove row(s)");
		removeButton.setToolTipText("Remove the currently selected row(s) from the table");
		gridDataFactory.applyTo(removeButton);
		removeButton.addListener(SWT.Selection, e -> removeItems());
	}

	/**
	 * @return List of SpectrumEvents currently selected in the Table
	 */
	private List<SpectrumEvent> getSelectedItems() {
		List<SpectrumEvent> items = Collections.emptyList();
		TableItem[] selectedItems = tableView.getTable().getSelection();
		if (selectedItems != null && selectedItems.length > 0) {
			items = new ArrayList<>();
			for(TableItem item : selectedItems) {
				SpectrumEvent event = (SpectrumEvent)item.getData();
				items.add(new SpectrumEvent(event.getSpectrumNumber(), event.getScannableName(), event.getPosition()));
			}
		}
		return items;
	}

	/**
	 * Return currently selected SpectrumEvents from the Table
	 */
	private void removeItems() {
		List<SpectrumEvent> selectedItems = getSelectedItems();
		if (selectedItems.isEmpty()) {
			return;
		}

		Iterator<SpectrumEvent> iter = tableValues.iterator();
		while (iter.hasNext()) {
			SpectrumEvent ev = iter.next();
			if (selectedItems.contains(ev)) {
				iter.remove();
			}
		}
		tableView.refresh();
	}

	/**
	 * Copy the currently selected SpectrumEvent(s) to the end of the table
	 */
	private void copyRows() {
		List<SpectrumEvent> selectedItems = getSelectedItems();
		if (selectedItems.isEmpty()) {
			return;
		}

		InputDialog numberInput = new InputDialog(getParentShell(), "Copy trigger parameters", "Enter start spectrum number to place copied triggers : ", "0.0", doubleValidator);
		if(numberInput.open() == Window.OK) {
			int startIndex = Integer.parseInt(numberInput.getValue());
			int minIndex = Collections.min(selectedItems, (v1, v2) -> Integer.compare(v1.getSpectrumNumber(), v2.getSpectrumNumber())).getSpectrumNumber();
			for(SpectrumEvent item : selectedItems) {
				int origIndex = item.getSpectrumNumber();
				item.setSpectrumNumber( startIndex + origIndex - minIndex);
				tableValues.add(item);
			}
		}
		tableView.refresh();
	}

	/**
	 * Validator used to check floating point number input (collection time dialog box)
	 */
	private IInputValidator doubleValidator =  newText -> {
		Integer value = null;
		try {
			value = Integer.valueOf(newText);
		} catch (NumberFormatException nfe) {
			// swallow, value==null
		}
		if (value == null || value < 0) {
			return "Text should be a number >= 0";
		}
		return null;
	};

	/** Sort direction of items in the table */
	private int direction = 1;

	/**
	 * Add selection listener to a TableColumn to sort the table contents.
	 * Sorting is based on spectrum number (index = 0), or scannable name (index = 1).
	 * @param viewerColumn
	 * @param index of the selected column
	 */
    private void addSelectionListener(final TableViewerColumn viewerColumn,
            final int index) {

    	TableColumn column = viewerColumn.getColumn();
        SelectionAdapter selectionAdapter = new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
            	if (index == 0) {
                	tableValues.sort(( s1, s2) -> direction*(s1.getSpectrumNumber() - s2.getSpectrumNumber()));
                } else {
                	tableValues.sort(( s1, s2) -> direction*s1.getScannableName().compareTo(s2.getScannableName()));
                }

                tableView.refresh();
                direction *= -1;
            }
        };
        column.addSelectionListener(selectionAdapter);
    }

    /**
     * Editing support to change name of selected scannable.
     */
	private static class ScannableNameEditingSupport extends EditingSupport {

	    public ScannableNameEditingSupport(TableViewer viewer) {
	        super(viewer);
	    }

	    @Override
	    protected CellEditor getCellEditor(Object element) {
	        return new ScannableNameCellEditor((Composite)getViewer().getControl());
	    }

	    @Override
	    protected boolean canEdit(Object element) {
	        return true;
	    }

	    @Override
	    protected Object getValue(Object element) {
	        return ((SpectrumEvent) element).getScannableName(); // needs to be string for the TextCellEditor
	    }

	    @Override
	    protected void setValue(Object element, Object userInputValue) {
	    	SpectrumEvent event = (SpectrumEvent) element;
	    	String newName = userInputValue.toString();
	    	if (!event.getScannableName().equals(newName)) {
		    	event.setScannableName(userInputValue.toString());
		        Object currentPosition = getCurrentPosition(event);
		        event.setPosition(currentPosition);
		        getViewer().update(element, null);
	    	}
	    }

		/**
		 * @param SpectrumEvent
		 * @return Current position of scannable named in SpectrumEvent; return 0.0 if no scannable was found or there was an exception.
		 */
		private Object getCurrentPosition(SpectrumEvent e) {
			Object defaultPosition = 0.0;
			Optional<Findable> scn = Finder.findOptional(e.getScannableName());
	    	if (scn.isPresent()) {
	    		try {
					return ((Scannable)scn.get()).getPosition();
				} catch (DeviceException e1) {
					logger.warn("Problem getting current position for {}. Using {} instead", scn.get().getName(), defaultPosition);
					return 0;
				}

	    	}
			logger.warn("No scannable called {} found - cannot get it's current position!", e.getScannableName());
	    	return defaultPosition;
		}
	}

	/**
	 * Textbox and button for typing/selecting the name of scannable.
	 * Clicking on the button opens up a dialog to select the name of a scannable from the list of all selected scannables.
	 */
	private static class ScannableNameCellEditor extends DialogCellEditor {
		private Text textBox;
		private Button button;

		public ScannableNameCellEditor(Composite parent) {
			super(parent);
		}

		@Override
		protected Control createContents(Composite cell) {
			textBox = new Text(cell, SWT.LEFT);
			textBox.addListener(SWT.FocusOut, focusEvent -> focusLost() );

			textBox.addKeyListener(new KeyAdapter() {
				@Override
				public void keyPressed(KeyEvent event) {
					keyReleaseOccured(event);
				}
			});
			return textBox;
		}

		@Override
		protected void keyReleaseOccured(KeyEvent keyEvent) {
			if (keyEvent.keyCode == SWT.CR || keyEvent.keyCode == SWT.KEYPAD_CR) { // Enter key
				setValueToModel();
			}
			super.keyReleaseOccured(keyEvent);
		}

		protected void setValueToModel() {
		 	String newValue = textBox.getText();
	        boolean newValidState = isCorrect(newValue);
	        if (newValidState) {
	            markDirty();
	            doSetValue(newValue);
	        }
		}

		@Override
	    protected Button createButton(Composite parent) {
	        button = super.createButton(parent);
	        button.setToolTipText("Select scannable from list");
	        button.addSelectionListener(widgetSelectedAdapter(event -> {
	        	logger.info("Button clicked");
	        }
	        ));
	        return button;
	    }

		@Override
		protected Object openDialogBox(Control cellEditorWindow) {
			List<String> safeScannables = ScannableListEditor.getSafeScannableNames();
			final String name = ScannableListEditor.showSelectScannableDialog(cellEditorWindow.getParent(), safeScannables);
			if (name != null) {
				textBox.setText(name);
				setValueToModel();
			}
			return null;
		}

		@Override
		protected void doSetFocus() {
			// Override so we can set focus to the Text widget instead of the Button.
			textBox.setFocus();
			textBox.selectAll();
		}

		@Override
		protected void updateContents(Object value) {
			String label = "";
			if (value != null) {
				label = value.toString();
			}
			textBox.setText(label);
			textBox.setFocus();
			textBox.forceFocus();
		}

		@Override
		protected void focusLost() {
			if (button != null && !button.isDisposed()) {
				return;
			}
			if (isActivated()) {
				setValueToModel();
				deactivate();
			}
		}
	}

	/**
	 * Editing support for changing spectrum number for an event (uses {@link SpinnerCellEditor}).
	 */
	private class SpectrumNumberEditingSupport extends EditingSupport {

		public SpectrumNumberEditingSupport(ColumnViewer viewer) {
			super(viewer);
		}

		// Called to update value in model from value in edited cell of table
		@Override
		public void setValue(Object element, Object userInputValue) {
	    	int val = Integer.parseInt(userInputValue.toString());
	        ((SpectrumEvent) element).setSpectrumNumber(val);
	        getViewer().update(element, null);
		}

		@Override
		protected CellEditor getCellEditor(Object element) {
			SpinnerCellEditor ce = new SpinnerCellEditor((Composite) getViewer().getControl());
			ce.setMinimum(0);
			ce.setMaximum(10000);
			return ce;
		}

		@Override
		protected boolean canEdit(Object element) {
			return true;
		}

		@Override
		protected Object getValue(Object element) {
			SpectrumEvent param = (SpectrumEvent) element;
			return param.getSpectrumNumber(); // needs to be an int for the SpinnerCellEditor
		}
	}
	/**
	 * Editing support for changing scannable position for an event.
	 */
	private static class PositionEditingSupport extends EditingSupport {

	    public PositionEditingSupport(TableViewer viewer) {
	        super(viewer);
	    }
	    private boolean isEnum;
	    private List<String> enumPositions;

	    private void setIsEnum(SpectrumEvent se) {
	    	enumPositions = Collections.emptyList();
	    	isEnum = false;

	    	Optional<Findable> scn = Finder.findOptional(se.getScannableName());
	    	if (scn.isPresent() && scn.get() instanceof EnumPositioner) {
	    		try {
	    			enumPositions = ((EnumPositioner)scn.get()).getPositionsList();
	    			isEnum = true;
	    		} catch (DeviceException e) {
					logger.warn("Problem determining if {} is enum positioner - assuming it's not.", se.getScannableName(), e);
	    		}
	    	}
	    }

	    @Override
	    protected CellEditor getCellEditor(Object element) {
	    	setIsEnum((SpectrumEvent) element);
	    	if (isEnum) {
				return new ComboBoxCellEditor((Composite) getViewer().getControl(), enumPositions.toArray(new String[] {}));
	    	} else {
	    		return new TextCellEditor((Composite)getViewer().getControl());
	    	}
	    }

	    @Override
	    protected boolean canEdit(Object element) {
	        return true;
	    }

	    @Override
	    protected Object getValue(Object element) {
	    	Object position = ((SpectrumEvent) element).getPosition();
	    	if (isEnum) {
	    		// index of value to select in combo box
	    		int index = enumPositions.indexOf(position.toString());
	    		return Math.max(0, index);
	    	} else {
	    		return position.toString(); // needs to be string for the TextCellEditor
	    	}
	    }

	    @Override
	    protected void setValue(Object element, Object value) {
	    	SpectrumEvent selectedElement = (SpectrumEvent)element;
	    	if (isEnum) {
	    		// Combo cell editor returns index of item selected by user
	    		String valInEnum = enumPositions.get((int)value);
	    		selectedElement.setPosition(valInEnum);
	    	} else {
	    		selectedElement.setPosition(value.toString());
	    	}
	        getViewer().update(element, null);
	    }
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

		List<SpectrumEvent> events = new ArrayList<>();
		events.add(new SpectrumEvent(1, "scn1", "100"));
		events.add(new SpectrumEvent(1, "scn2", "250"));
		events.add(new SpectrumEvent(2, "scn1", "300"));
		events.add(new SpectrumEvent(3, "scn1", "500"));

		SpectrumEventsEditor viewer = new SpectrumEventsEditor(shell);
		viewer.setTableValues(events);
		viewer.createDialogArea(shell);

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

	private List<Double> timeAtSpectrumEnd = Collections.emptyList();

	/** Using List of TurboSlitTimingGroups to make list of the end times of each spectrum, across all groups
	 *
	 * @param timingGroups
	 */
	public void setSpectrumTimes(List<TurboSlitTimingGroup> timingGroups) {
		if (timingGroups == null || timingGroups.isEmpty()) {
			MessageDialog.openInformation(Display.getDefault().getActiveShell(),
					"No timing groups have been set",
					"No timing groups have been set - time start times will be incorrect");
			logger.warn("No timing groups have been set - spectrum start times will be incorrect");
			return;
		}

		double totalTime = 0;
		timeAtSpectrumEnd = new ArrayList<>();
		for(TurboSlitTimingGroup timingGroup : timingGroups) {
			for(int i=0; i<timingGroup.getNumSpectra(); i++) {
				totalTime += timingGroup.getTimePerSpectrum();
				timeAtSpectrumEnd.add(totalTime);
				totalTime += timingGroup.getTimeBetweenSpectra();
			}
		}
	}

	private double getTimeAtSpectrumEnd(int spectrumNumber) {
		if (spectrumNumber > timeAtSpectrumEnd.size()-1) {
			MessageDialog.openWarning(this.getParentShell(), "Warning!", "Time for spectrum "+spectrumNumber +" will be incorrect - it is after the last spectrum in the timing groups");
			logger.warn("Time for spectrum {} will be incorrect - it is after the last spectrum in the timing groups", spectrumNumber);
			if (timeAtSpectrumEnd.isEmpty()) {
				return 0;
			} else {
				return timeAtSpectrumEnd.get(timeAtSpectrumEnd.size()-1);
			}
		}
		return timeAtSpectrumEnd.get(spectrumNumber);
	}

}
