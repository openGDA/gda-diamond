/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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


import gda.jython.JythonServerFacade;

import java.util.List;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.FileDialog;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;

import uk.ac.gda.richbeans.components.FieldComposite;
import uk.ac.gda.richbeans.components.wrappers.TextWrapper;

public final class UserOptionsComposite extends Composite {

	private TextWrapper scriptName;

	public UserOptionsComposite(final Composite parent, int style) {
		super(parent, style);
		setLayout(new GridLayout(2, false));

//		Label label = new Label(this, SWT.NONE);
//		label.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
//		label.setText("scriptName");
//		this.scriptName = new TextWrapper(this, SWT.NONE);
//		scriptName.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));

		final Group jythonScriptGroup = new Group(this, SWT.NONE);
		jythonScriptGroup.setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, false));
		jythonScriptGroup.setText("Jython Script");
		GridLayout gridLayout2 = new GridLayout();
		gridLayout2.numColumns = 3;
		jythonScriptGroup.setLayout(gridLayout2);

		Label scriptNameLabel = new Label(jythonScriptGroup, SWT.NONE);
		scriptNameLabel.setToolTipText("A Jython script to run immediately before each scan");
		scriptNameLabel.setText("Script Name");

		
		scriptName = new TextWrapper(jythonScriptGroup, SWT.BORDER);
		scriptName.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		scriptName.setTextType(TextWrapper.TEXT_TYPE.FILENAME);

		Button button = new Button(jythonScriptGroup, SWT.PUSH);
		button.setText("...");
		button.addSelectionListener(new SelectionAdapter() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				showDialog();
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				showDialog();
			}

			private void showDialog() {
				FileDialog dialog = new FileDialog(parent.getShell(), SWT.OPEN);
				String[] filterNames = new String[] { "Jython Script Files", "All Files (*)" };
				dialog.setFilterNames(filterNames);
				String[] filterExtensions = new String[] { "*.py", "*" };
				dialog.setFilterExtensions(filterExtensions);
				String filterPath = findDefaultFilterPath();
				dialog.setFilterPath(filterPath);
				final String filename = dialog.open();
				if (filename != null) {
					parent.getShell().getDisplay().asyncExec(new Runnable() {
						@Override
						public void run() {
							scriptName.setValue(filename);
						}
					});
				}
			}

			private String findDefaultFilterPath() {
				List<String> jythonProjectFolders = JythonServerFacade.getInstance().getAllScriptProjectFolders();
				String filterPath = System.getenv("user.home");

				for (String path : jythonProjectFolders) {
					if (JythonServerFacade.getInstance().projectIsUserType(path)) {
						filterPath = path;
						continue;
					}
				}
				return filterPath;
			}
		});

	}

	public FieldComposite getScriptName() {
		return scriptName;
	}

	@Override
	public boolean setFocus() {
		return scriptName.setFocus();
	}
}
