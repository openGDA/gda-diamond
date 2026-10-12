/*-
 * Copyright © 2026 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i09_2.views.e4;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;

import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.ProgressBar;

import gda.jython.InterfaceProvider;
import gda.observable.IObserver;
import gda.scan.Scan.ScanStatus;
import gda.scan.ScanEvent;

public class ScanProgressView {
	private ProgressBar progressBar;
	private Label taskLabel;
	private int totalNumberOfPoints;

	@PostConstruct
	public void createComposite(Composite parent) {
		parent.setLayout(new GridLayout(1, false));

		taskLabel = new Label(parent, SWT.NONE);
		taskLabel.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		taskLabel.setText("Scan progress:  No scan is running");

		progressBar = new ProgressBar(parent, SWT.HORIZONTAL | SWT.SMOOTH);
		progressBar.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		progressBar.setMaximum(100);

		InterfaceProvider.getScanDataPointProvider().addScanEventObserver(serverObserver);
	}

	private IObserver serverObserver = (source, arg) -> {
		if (!(arg instanceof ScanEvent scanEvent)) {
			return;
		}

		if (scanEvent.getCurrentPointNumber() > -1) {
			int point = scanEvent.getCurrentPointNumber() + 1;
			long progress =  Math.round(100.0*point/totalNumberOfPoints);
			Display.getDefault().asyncExec(() -> {
				if (!progressBar.isDisposed()) {
					taskLabel.setText(String.format("Scan '%s' progress: %d%% ", scanEvent.getLatestInformation().getScanNumber(), progress));
					progressBar.setSelection((int) progress);
				}
			});
			return;
		}

		if (scanEvent.getLatestStatus() != ScanStatus.NOTSTARTED) {
			totalNumberOfPoints = scanEvent.getLatestInformation().getNumberOfPoints();
			Display.getDefault().asyncExec(() -> {
				if (!progressBar.isDisposed()) {
					progressBar.setSelection(0);
				}
			});
		}
	};

	@PreDestroy
	public void cleanUp() {
		InterfaceProvider.getScanDataPointProvider().deleteScanEventObserver(serverObserver);
	}
}