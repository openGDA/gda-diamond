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

import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.ProgressBar;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Text;
import org.eclipse.swt.layout.GridData;

import uk.ac.gda.arpes.detector.FlexibleFrameDetector;
import uk.ac.gda.arpes.detector.FrameUpdate;
import uk.ac.gda.richbeans.components.scalebox.IntegerBox;
import uk.ac.gda.richbeans.event.ValueAdapter;
import uk.ac.gda.richbeans.event.ValueEvent;

public class AnalyserProgressView extends ViewPart implements IObserver {
	private Text csweep;
	private Text msweep;
	private IntegerBox sweepEntry;
	private FlexibleFrameDetector analyser;
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
		
		csweep = new Text(parent, SWT.BORDER);
		csweep.setEditable(false);
		csweep.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		
		Label lblMaximumSweep = new Label(parent, SWT.NONE);
		lblMaximumSweep.setLayoutData(new GridData(SWT.RIGHT, SWT.CENTER, false, false, 1, 1));
		lblMaximumSweep.setText("Maximum Sweep");
		
		msweep = new Text(parent, SWT.BORDER);
		msweep.setEditable(false);
		msweep.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		
		Label lblNewMaximum = new Label(parent, SWT.NONE);
		lblNewMaximum.setText("New Maximum");
		
		sweepEntry = new IntegerBox(parent, SWT.BORDER);
		sweepEntry.setMinimum(1);
		sweepEntry.setMaximum(10000);
		sweepEntry.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
		sweepEntry.addValueListener(new ValueAdapter("sweepEntry") {
			@Override
			public void valueChangePerformed(ValueEvent e) {
				analyser.setMaximumFrame(sweepEntry.getIntegerValue());				
			}
		});
		sweepEntry.on();
		
		Button btnCompleteAndStop = new Button(parent, SWT.NONE);
		btnCompleteAndStop.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false, 3, 1));
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
		btnStop.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER, false, false, 3, 1));
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
					csweep.setText(String.valueOf(fu.cFrame));
					msweep.setText(String.valueOf(fu.mFrame));
				}
			});
		}
	}
}