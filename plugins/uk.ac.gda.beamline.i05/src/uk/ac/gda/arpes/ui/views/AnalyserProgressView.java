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

import gda.factory.Finder;
import gda.jython.JythonServerFacade;
import gda.observable.IObserver;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.ProgressBar;
import org.eclipse.swt.widgets.Spinner;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.part.ViewPart;

import uk.ac.gda.arpes.detector.FlexibleFrameDetector;
import uk.ac.gda.arpes.detector.FrameUpdate;

public class AnalyserProgressView extends ViewPart implements IObserver {
	private Text csweep;
	private FlexibleFrameDetector analyser;
	private Spinner sweepSpinner;
	private int oldMax = -1, compSweep = -1;
	public AnalyserProgressView() {
	}

	@Override
	public void createPartControl(Composite parent) {
		GridLayout gl_parent = new GridLayout(4, true);
		gl_parent.verticalSpacing = 15;
		gl_parent.marginTop = 5;
		gl_parent.marginRight = 5;
		gl_parent.marginLeft = 5;
		gl_parent.marginBottom = 5;
		parent.setLayout(gl_parent);
		
		ProgressBar progressBar = new ProgressBar(parent, SWT.FILL);
		progressBar.setSelection(100);
		progressBar.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 4, 1));
		
		Label lblCurrentSweep = new Label(parent, SWT.NONE);
		lblCurrentSweep.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		lblCurrentSweep.setText("Sweeps");
		
		csweep = new Text(parent, SWT.BORDER | SWT.RIGHT);
		csweep.setEditable(false);
		csweep.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		
		Label lblNewMaximum = new Label(parent, SWT.NONE);
		GridData gd_lblNewMaximum = new GridData(SWT.LEFT, SWT.CENTER, false, false, 1, 1);
		gd_lblNewMaximum.horizontalIndent = 15;
		lblNewMaximum.setLayoutData(gd_lblNewMaximum);
		lblNewMaximum.setText("Maximum");
		
		sweepSpinner = new Spinner(parent, SWT.BORDER);
		sweepSpinner.setIncrement(1);
		sweepSpinner.setMinimum(1);		
		sweepSpinner.setMaximum(1000);
		sweepSpinner.setSelection(1);
		sweepSpinner.addModifyListener(new ModifyListener() {
			
			@Override
			public void modifyText(ModifyEvent e) {
				int newMax = sweepSpinner.getSelection();
				if (newMax < compSweep)
					return;
				oldMax = newMax;
				analyser.setMaximumFrame(oldMax);
			}
		});
		
		Button btnCompleteAndStop = new Button(parent, SWT.NONE);
		btnCompleteAndStop.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false, 2, 1));
		btnCompleteAndStop.setText("Complete and Stop");
		btnCompleteAndStop.addSelectionListener(new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				JythonServerFacade.getInstance().haltCurrentScan();
				analyser.setMaximumFrame(analyser.getCurrentFrame());
			}
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});
		
		Button btnStop = new Button(parent, SWT.NONE);
		btnStop.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false, 2, 1));
		btnStop.setText("Stop");
		btnStop.addSelectionListener(new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				JythonServerFacade.getInstance().panicStop();
			}
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});
		
		analyser = (FlexibleFrameDetector) Finder.getInstance().find("analyser");
		if (analyser != null) {
			analyser.addIObserver(this);
		}
	}

	@Override
	public void setFocus() {
		// TODO Auto-generated method stub
	}

	@Override
	public void update(Object source, Object arg) {
		if (arg instanceof FrameUpdate) {
			final FrameUpdate fu = (FrameUpdate) arg;
			Display.getDefault().asyncExec(new Runnable() {
				@Override
				public void run() {
					compSweep = fu.cFrame;
					csweep.setText(String.valueOf(compSweep));
					if (fu.mFrame != oldMax) {
						sweepSpinner.setSelection(fu.mFrame);
					}
				}
			});
		}
	}
}