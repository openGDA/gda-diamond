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

package uk.ac.gda.arpes.ui.views;

import gda.observable.IObserver;

import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.ProgressBar;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Text;
import org.eclipse.swt.layout.GridData;

public class AnalyserProgressView extends ViewPart implements IObserver {
	private Text text;
	private Text text_1;
	private Text text_2;
	public AnalyserProgressView() {
	}

	@Override
	public void createPartControl(Composite parent) {
		parent.setLayout(new GridLayout(6, false));
		
		ProgressBar progressBar = new ProgressBar(parent, SWT.NONE);
		progressBar.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, true, false, 6, 1));
		
		Label lblCurrentSweep = new Label(parent, SWT.NONE);
		lblCurrentSweep.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		lblCurrentSweep.setText("Current Sweep");
		
		text = new Text(parent, SWT.BORDER);
		text.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		
		Label lblMaximumSweep = new Label(parent, SWT.NONE);
		lblMaximumSweep.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		lblMaximumSweep.setText("Maximum Sweep");
		
		text_1 = new Text(parent, SWT.BORDER);
		text_1.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		
		Label lblNewMaximum = new Label(parent, SWT.NONE);
		lblNewMaximum.setText("New Maximum");
		
		text_2 = new Text(parent, SWT.BORDER);
		text_2.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		
		Button btnCompleteAndStop = new Button(parent, SWT.NONE);
		btnCompleteAndStop.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false, 3, 1));
		btnCompleteAndStop.setText("Complete and Stop");
		
		Button btnStop = new Button(parent, SWT.NONE);
		btnStop.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false, 3, 1));
		btnStop.setText("Stop");
	}

	@Override
	public void setFocus() {
		// TODO Auto-generated method stub

	}

	@Override
	public void update(Object source, Object arg) {
		// TODO Auto-generated method stub
		
	}

}
