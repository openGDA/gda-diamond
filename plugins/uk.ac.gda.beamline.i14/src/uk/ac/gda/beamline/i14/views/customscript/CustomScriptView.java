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

package uk.ac.gda.beamline.i14.views.customscript;

import static gda.configuration.properties.LocalProperties.GDA_CONFIG;
import static gda.jython.JythonStatus.RUNNING;
import static org.eclipse.swt.events.SelectionListener.widgetSelectedAdapter;

import java.io.File;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import javax.annotation.PostConstruct;
import javax.inject.Inject;

import org.eclipse.e4.core.contexts.IEclipseContext;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.CellEditor;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jface.viewers.EditingSupport;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.jface.viewers.TextCellEditor;
import org.eclipse.jface.window.IShellProvider;
import org.eclipse.jface.window.Window;
import org.eclipse.scanning.api.script.IScriptService;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.FileDialog;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.MessageBox;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import gda.configuration.properties.LocalProperties;
import gda.jython.JythonServerFacade;
import uk.ac.diamond.daq.concurrent.Async;

/**
 * View to execute an arbitrary script
 * <p>
 * The view consists of:
 * <ul>
 * <li>a text box containing the path to the script file to be run</li>
 * <li>a button that opens a file dialog to browse for the script file</li>
 * <li>a table of parameters to be passed to the script</li>
 * <li>buttons to add, edit & delete parameters from the table, and to call the script</li>
 * </ul>
 * The parameters are serialised to JSON and the resulting string is put into the Jython namespace as "customParams"
 * before calling the script.
 */
public class CustomScriptView {
	private static final Logger logger = LoggerFactory.getLogger(CustomScriptView.class);

	private static final String CLIENT_PLUGIN_ID = "uk.ac.gda.client";
	private static final String BROWSE_ICON_PATH = "icons/folder.png";
	private static final String SCRIPTS_SUBDIRECTORY = "scripts";
	private static final String[] FILTER_NAMES = new String[] { "Python scripts", "All files" };
	private static final String[] FILTER_EXTENSIONS = new String[] { "*.py", "*.*" };
	private static final int TABLE_HEIGHT = 400;
	private static final int NAME_COLUMN_WIDTH = 150;
	private static final int VALUE_COLUMN_WIDTH = 150;

	@Inject
	private IEclipseContext injectionContext;

	private final List<ScriptParameter> params = new ArrayList<>();

	private Text scriptPath;
	private TableViewer parameterTable;
	private Button submitButton;

	@PostConstruct
	public void createView(Composite parent) {
		final Composite mainComposite = new Composite(parent, SWT.NONE);
		GridLayoutFactory.swtDefaults().applyTo(mainComposite);

		createScriptSelector(mainComposite);
		createParameterTable(mainComposite);
		createButtonSection(mainComposite);
	}

	/**
	 * Create the section to define which script should be run.
	 * <p>
	 * The path to the script can be typed directly into a text box or (probably more commonly) chosen using a dialog
	 * box.
	 *
	 * @param parent
	 *            The parent composite for this section
	 */
	private void createScriptSelector(Composite parent) {
		final Composite scriptComposite = new Composite(parent, SWT.NONE);
		GridDataFactory.fillDefaults().grab(true, false).applyTo(scriptComposite);
		GridLayoutFactory.swtDefaults().numColumns(3).applyTo(scriptComposite);

		final Label selectScriptLabel = new Label(scriptComposite, SWT.NONE);
		GridDataFactory.swtDefaults().applyTo(selectScriptLabel);
		selectScriptLabel.setText("Select script");

		scriptPath = new Text(scriptComposite, SWT.BORDER);
		GridDataFactory.fillDefaults().grab(true, false).applyTo(scriptPath);

		final Button browseButton = new Button(scriptComposite, SWT.PUSH);
		final ImageDescriptor iconDescriptor = AbstractUIPlugin.imageDescriptorFromPlugin(CLIENT_PLUGIN_ID, BROWSE_ICON_PATH);
		browseButton.setImage(iconDescriptor.createImage());
		browseButton.setToolTipText("Browse...");
		browseButton.addSelectionListener(widgetSelectedAdapter(e -> browseForScript()));
	}

	/**
	 * Open a dialog box to choose a script and set it in the path box
	 */
	private void browseForScript() {
		final FileDialog fileDialog = new FileDialog(injectionContext.get(IShellProvider.class).getShell(), SWT.OPEN);
		fileDialog.setText("Select script to run");
		fileDialog.setFilterNames(FILTER_NAMES);
		fileDialog.setFilterExtensions(FILTER_EXTENSIONS);

		final String scriptsDirectory = Paths.get(LocalProperties.get(GDA_CONFIG), SCRIPTS_SUBDIRECTORY).toString();
		fileDialog.setFilterPath(scriptsDirectory);

		final String path = fileDialog.open();
		if (path != null) {
			scriptPath.setText(path);
			scriptPath.setToolTipText(path);
		}
	}

	/**
	 * Create a table to hold the script parameters (name & value)
	 * <p>
	 * Backed by an array of {@link ScriptParameter}
	 *
	 * @param parent
	 *            The parent composite for this section
	 */
	private void createParameterTable(Composite parent) {
		final Composite tableComposite = new Composite(parent, SWT.NONE);
		GridDataFactory.fillDefaults().applyTo(tableComposite);
		GridLayoutFactory.swtDefaults().applyTo(tableComposite);

		final Label tableTitle = new Label(tableComposite, SWT.NONE);
		GridDataFactory.swtDefaults().applyTo(tableTitle);
		tableTitle.setText("Parameters");

		parameterTable = new TableViewer(tableComposite, SWT.BORDER | SWT.FULL_SELECTION | SWT.MULTI | SWT.V_SCROLL | SWT.H_SCROLL);
		final Table table = parameterTable.getTable();
		GridDataFactory.fillDefaults().hint(SWT.DEFAULT, TABLE_HEIGHT).grab(true, false).applyTo(table);
		table.setHeaderVisible(true);
		table.setLinesVisible(true);

		final TableViewerColumn nameColumn = new TableViewerColumn(parameterTable, SWT.LEFT);
		nameColumn.getColumn().setText("Name");
		nameColumn.getColumn().setWidth(NAME_COLUMN_WIDTH);
		nameColumn.setEditingSupport(new NameEditingSupport(parameterTable));
		nameColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public String getText(Object element) {
				return ((ScriptParameter) element).getName();
			}
		});

		final TableViewerColumn valueColumn = new TableViewerColumn(parameterTable, SWT.LEFT);
		valueColumn.getColumn().setText("Value");
		valueColumn.getColumn().setWidth(VALUE_COLUMN_WIDTH);
		valueColumn.setEditingSupport(new ValueEditingSupport(parameterTable));
		valueColumn.setLabelProvider(new ColumnLabelProvider() {
			@Override
			public String getText(Object element) {
				return ((ScriptParameter) element).getValue();
			}
		});

		parameterTable.setContentProvider(ArrayContentProvider.getInstance());
		parameterTable.setInput(params);
		parameterTable.addDoubleClickListener(e -> editParameter(e.getSelection()));
	}

	/**
	 * Create a section containing buttons to add & delete parameters and to submit them to the script
	 *
	 * @param parent
	 *            The parent composite for this section
	 */
	private void createButtonSection(Composite parent) {
		final Composite buttonComposite = new Composite(parent, SWT.NONE);
		GridDataFactory.fillDefaults().grab(true, false).applyTo(buttonComposite);
		GridLayoutFactory.swtDefaults().numColumns(4).applyTo(buttonComposite);

		final Button addButton = new Button(buttonComposite, SWT.PUSH);
		GridDataFactory.swtDefaults().applyTo(addButton);
		addButton.setText("&Add...");
		addButton.addSelectionListener(widgetSelectedAdapter(e -> addParameter()));

		final Button deleteButton = new Button(buttonComposite, SWT.PUSH);
		GridDataFactory.swtDefaults().applyTo(deleteButton);
		deleteButton.setText("&Delete...");
		deleteButton.addSelectionListener(widgetSelectedAdapter(e -> deleteParameters()));

		final Button editButton = new Button(buttonComposite, SWT.PUSH);
		GridDataFactory.swtDefaults().applyTo(editButton);
		editButton.setText("&Edit...");
		editButton.addSelectionListener(widgetSelectedAdapter(e -> editParameter(parameterTable.getSelection())));

		submitButton = new Button(buttonComposite, SWT.PUSH);
		GridDataFactory.swtDefaults().grab(true, false).align(SWT.END, SWT.CENTER).applyTo(submitButton);
		submitButton.setText("&Submit");
		submitButton.addSelectionListener(widgetSelectedAdapter(e -> submitScan()));
	}

	/**
	 * Open a dialog to add a new parameter.
	 * <p>
	 * See also {@link #editParameter(ISelection)}
	 */
	private void addParameter() {
		final Shell shell = injectionContext.get(IShellProvider.class).getShell();
		final EditParameterDialog dialog = new EditParameterDialog(shell);
		if (dialog.open() == Window.OK) {
			final ScriptParameter param = dialog.getParameter();
			if (isValidParameter(param)) {
				params.add(param);
				parameterTable.refresh();
			}
		}
	}

	/**
	 * Open a dialog to edit the parameter.
	 * <p>
	 * This is the same dialog used by {@link #addParameter()}, but initialised with the current parameter name & value.
	 *
	 * @param selection
	 *            the currently-selected table row (may be empty)
	 */
	private void editParameter(ISelection selection) {
		if (!(selection instanceof IStructuredSelection) || ((IStructuredSelection) selection).size() == 0) {
			return;
		}
		final ScriptParameter selectedParameter = (ScriptParameter) ((IStructuredSelection) selection).getFirstElement();
		final Shell shell = injectionContext.get(IShellProvider.class).getShell();
		final EditParameterDialog dialog = new EditParameterDialog(shell);

		dialog.setParameter(new ScriptParameter(selectedParameter.getName(), selectedParameter.getValue()));
		if (dialog.open() == Window.OK) {
			final ScriptParameter newParam = dialog.getParameter();
			if (isValidParameter(newParam)) {
				selectedParameter.setName(newParam.getName());
				selectedParameter.setValue(newParam.getValue());
				parameterTable.refresh();
			}
		}
	}

	/**
	 * Delete the currently-selected parameter(s), asking the user to confirm the deletion.
	 */
	private void deleteParameters() {
		final ISelection selection = parameterTable.getSelection();
		if (!(selection instanceof IStructuredSelection) || ((IStructuredSelection) selection).size() == 0) {
			return;
		}
		final IStructuredSelection structSel = (IStructuredSelection) selection;
		final int numRowsSelected = structSel.size();

		// Ask user for confirmation
		final String message = "Do you want to delete " + numRowsSelected + " row(s)?";
		final Shell shell = injectionContext.get(IShellProvider.class).getShell();
		final MessageBox messageBox = new MessageBox(shell, SWT.ICON_QUESTION | SWT.YES | SWT.NO);
		messageBox.setMessage(message);

		if (messageBox.open() == SWT.YES) {
			@SuppressWarnings("unchecked")
			final Iterator<ScriptParameter> iter = structSel.iterator();
			while (iter.hasNext()) {
				final ScriptParameter param = iter.next();
				params.remove(param);
				parameterTable.refresh();
			}
		}
	}

	private void submitScan() {
		final String scriptFilePath = scriptPath.getText();
		if (scriptFilePath == null || scriptFilePath.isEmpty()) {
			displayError("Script file missing", "No script file has been defined");
			return;
		}

		final File scriptFile = new File(scriptFilePath);
		if (!scriptFile.exists()) {
			displayError("Script file does not exist", "Script file '" + scriptFilePath + "' does not exist");
			return;
		}

		try {
			final ObjectMapper mapper = new ObjectMapper();
			final IScriptService scriptService = injectionContext.get(IScriptService.class);
			scriptService.setNamedValue(IScriptService.VAR_NAME_CUSTOM_PARAMS, mapper.writeValueAsString(params));
		} catch (JsonProcessingException e) {
			displayError("Error serialising parameters", "Error serialising script parameters - see log for details");
			logger.error("Error serialising script parameters", e);
		}

		Async.execute(() -> runScript(scriptFile));
	}

	/**
	 * Run the script, disabling the submit button while it is running
	 *
	 * @param scriptFile
	 *            file containing script to run
	 */
	private void runScript(File scriptFile) {
		final JythonServerFacade jythonServerFacade = JythonServerFacade.getInstance();
		try {
			setSubmitButtonEnabled(false);
			logger.info("Running script: {}", scriptFile);
			jythonServerFacade.runScript(scriptFile);
			while (jythonServerFacade.getScriptStatus() == RUNNING) {
				Thread.sleep(500);
			}
			logger.info("Finished running script");
		} catch (Exception e) {
			logger.error("Error running script", e);
		} finally {
			setSubmitButtonEnabled(true);
		}
	}

	private boolean isValidParameter(ScriptParameter param) {
		return param != null && param.getName() != null && !param.getName().isEmpty();
	}

	private void setSubmitButtonEnabled(boolean enabled) {
		Display.getDefault().asyncExec(() -> submitButton.setEnabled(enabled));
	}

	private void displayError(String title, String message) {
		final Shell activeShell = injectionContext.get(IShellProvider.class).getShell();
		MessageDialog.openError(activeShell, title, message);
	}

	/**
	 * Editing support for a field in the parameter table.
	 */
	private abstract static class CellEditingSupport extends EditingSupport {
		private final TableViewer viewer;
	    private final CellEditor editor;

	    public CellEditingSupport(TableViewer viewer) {
			super(viewer);
			this.viewer = viewer;
			editor = new TextCellEditor(viewer.getTable());
		}

		@Override
		protected CellEditor getCellEditor(Object element) {
			return editor;
		}

		@Override
		protected boolean canEdit(Object element) {
			return true;
		}

		@Override
		protected void setValue(Object element, Object value) {
			setStringValue((ScriptParameter) element, String.valueOf(value));
			viewer.update(element, null);
		}

		protected abstract void setStringValue(ScriptParameter parameter, String value);
	}

	/**
	 * Editing support for the name of a parameter
	 */
	private static class NameEditingSupport extends CellEditingSupport {

		public NameEditingSupport(TableViewer viewer) {
			super(viewer);
		}

		@Override
		protected Object getValue(Object element) {
			return ((ScriptParameter) element).getName();
		}

		@Override
		protected void setStringValue(ScriptParameter parameter, String value) {
			parameter.setName(value);
		}
	}

	/**
	 * Editing support for the value of a parameter
	 */
	private static class ValueEditingSupport extends CellEditingSupport {

		public ValueEditingSupport(TableViewer viewer) {
			super(viewer);
		}

		@Override
		protected Object getValue(Object element) {
			return ((ScriptParameter) element).getValue();
		}

		@Override
		protected void setStringValue(ScriptParameter parameter, String value) {
			parameter.setValue(value);
		}
	}
}
