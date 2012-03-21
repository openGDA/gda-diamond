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

package uk.ac.gda.exafs.ui.views.commandhandlers;

import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Dialog;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Spinner;

public class IntegerInputDialog extends Dialog {
	Integer initialValue;
	Integer maximum = Integer.MIN_VALUE;
	Integer minimum = Integer.MAX_VALUE;
	String labelString = "Please enter a valid number:";
	String title = "IntegerInputDialog";
	Integer selectedValue = 0;

	public IntegerInputDialog(Shell parent) {
		super(parent);
	}

	public IntegerInputDialog(Shell parent, int style) {
		super(parent, style);
	}

	public Integer open() {
		Shell parent = getParent();
		final Shell shell = new Shell(parent, SWT.TITLE | SWT.BORDER | SWT.APPLICATION_MODAL);
		shell.setText(title);

		shell.setLayout(new GridLayout(2, true));

		Label label = new Label(shell, SWT.NULL);
		label.setText(labelString);

		final Spinner spinner = new Spinner(shell, SWT.SINGLE | SWT.BORDER);
		spinner.setMaximum(maximum);
		spinner.setMinimum(minimum);
		spinner.setIncrement(1);
		spinner.setSelection(initialValue);

		final Button buttonOK = new Button(shell, SWT.PUSH);
		buttonOK.setText("Ok");
		buttonOK.setLayoutData(new GridData(GridData.HORIZONTAL_ALIGN_END));
		buttonOK.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				selectedValue = spinner.getSelection();
				shell.dispose();
			}
		});
		
		shell.addListener(SWT.Traverse, new Listener() {
			@Override
			public void handleEvent(Event event) {
				if (event.detail == SWT.TRAVERSE_ESCAPE)
					event.doit = false;
			}
		});

		shell.pack();
		shell.open();

		Display display = parent.getDisplay();
		while (!shell.isDisposed()) {
			if (!display.readAndDispatch())
				display.sleep();
		}

		return selectedValue;
	}

	public Integer getMaximum() {
		return maximum;
	}

	public void setMaximum(Integer maximum) {
		this.maximum = maximum;
	}

	public Integer getMinimum() {
		return minimum;
	}

	public void setMinimum(Integer minimum) {
		this.minimum = minimum;
	}

	public String getLabelString() {
		return labelString;
	}

	public void setLabelString(String labelString) {
		this.labelString = labelString;
	}

	public String getTitle() {
		return title;
	}

	public void setTitle(String title) {
		this.title = title;
	}

	public Integer getInitialValue() {
		return initialValue;
	}

	public void setInitialValue(Integer initialValue) {
		this.initialValue = initialValue;
	}

	public static void main(String[] args) {
		Shell shell = new Shell();
		IntegerInputDialog dialog = new IntegerInputDialog(shell);
		System.out.println(dialog.open());
	}
}