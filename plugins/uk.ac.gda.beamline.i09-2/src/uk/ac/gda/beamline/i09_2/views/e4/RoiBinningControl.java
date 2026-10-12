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

import java.util.Map;

import javax.annotation.PostConstruct;
import javax.inject.Inject;
import javax.inject.Named;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Scale;
import org.eclipse.swt.widgets.Spinner;
import org.eclipse.swt.widgets.Text;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.factory.Finder;
import gda.observable.IObserver;

public class RoiBinningControl {
	private static final Logger logger = LoggerFactory.getLogger(RoiBinningControl.class);
	protected static final int DEBOUNCE_TIME_MS = 500;

	private Composite parent;
    private Runnable pendingTask;

	Map<String, Scannable> scannablesMap;

	@Inject
	@Named("roiStartScannableName")
	String roiStartScannableName;

	@Inject
	@Named("roiSizeScannableName")
	String roiSizeScannableName;

	@Inject
	@Named("roiBinningScannableName")
	String roiBinningScannableName;

    @PostConstruct
    public void createControls(Composite parent) {
        this.parent = parent;
        scannablesMap = Finder.getFindablesOfType(Scannable.class);

		logger.debug("Populating context variables");

        if (parent == null) {
	    	logger.debug("Not initialised: no parent");
            return;
        }
        if (scannablesMap == null) {
	    	logger.debug("Not initialised: no scannablesMap");
            return;
        }
        if (roiSizeScannableName==null) {
	    	logger.debug("Not initialised: no roiSizeScannableName");
        	return;
        }
        if (roiBinningScannableName==null) {
	    	logger.debug("Not initialised: no roiBinningScannableName");
        	return;
        }
        if (roiStartScannableName==null) {
	    	logger.debug("Not initialised: no roiStartScannableName");
        	return;
        }

		logger.debug("Got scannablesMap {}", scannablesMap);
		logger.debug("Got roiSizeScannableName name {}", roiSizeScannableName);
		logger.debug("Got roiBinningScannableName name {}", roiBinningScannableName);
		logger.debug("Got roiStartScannableName name {}", roiStartScannableName);

		createView();
	}

	private void createView() {

        logger.debug("Creating view");

		Scannable roiStartScannable = scannablesMap.get(roiStartScannableName);
		logger.debug("Got a roi start scannable {}", roiStartScannable.getClass());

		Scannable roiSizeScannable = scannablesMap.get(roiSizeScannableName);
		logger.debug("Got a roi size scannable {}", roiSizeScannable.getClass());

		Scannable roiBinningScannable = scannablesMap.get(roiBinningScannableName);
		logger.debug("Got a roi binning scannable {}", roiBinningScannable.getClass());

		Composite controls = new Composite(parent, SWT.NONE);
		controls.setLayout(new GridLayout(1, false));
		controls.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

		// label above border
        Group group = new Group(controls, SWT.SHADOW_ETCHED_IN);
        GridLayout layout = new GridLayout(5, false);
        layout.marginWidth = 10;
        layout.horizontalSpacing = 10;
        group.setLayout(layout);
        group.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

        logger.debug("Creating roiStart");

        Label roiStartLabel = new Label(group, SWT.NONE);
        roiStartLabel.setText("ROI START:");
        // Slider
        Scale roiStartScale = new Scale(group, SWT.HORIZONTAL);
        roiStartScale.setMinimum(0);
        roiStartScale.setMaximum(1200);
        roiStartScale.setSelection(50);
        roiStartScale.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));

        // Integer input
        Spinner roiStartSpinner = new Spinner(group, SWT.BORDER);
        roiStartSpinner.setMinimum(0);
        roiStartSpinner.setMaximum(1200);
        roiStartSpinner.setSelection(50);

        // Slider -> Spinner & EPICS
        roiStartScale.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
            	int value = roiStartScale.getSelection();
            	if (roiStartSpinner.getSelection()!=value) {
            		roiStartSpinner.setSelection(value);
            	}
                debounce(() -> moveScannable(roiStartScannable, value),DEBOUNCE_TIME_MS);
            }
        });

        // Spinner -> Slider & EPICS
        roiStartSpinner.addSelectionListener(new SelectionAdapter() {
            @Override
            public void widgetSelected(SelectionEvent e) {
            	int value = roiStartSpinner.getSelection();
            	if (roiStartScale.getSelection()!=value) {
                    roiStartScale.setSelection(value);
            	}
                debounce(() -> moveScannable(roiStartScannable, value), DEBOUNCE_TIME_MS);
            }
        });

        // EPICS -> UI
	    IObserver roiStartobserver = (source,arg) ->
	        Display.getDefault().asyncExec(() -> {
	            if (!roiStartScale.isDisposed() && !roiStartSpinner.isDisposed()) {
	                int value = getScannablePosition(roiStartScannable);
		            if (roiStartScale.getSelection() != value) {
		            	roiStartScale.setSelection(value);
		            	roiStartSpinner.setSelection(value);
		            }
	            }
	        });
	    roiStartScannable.addIObserver(roiStartobserver);
	    roiStartScale.addDisposeListener(e -> roiStartScannable.deleteIObserver(roiStartobserver));

	    // ROI SIZE AND BINNING CONTROL
        logger.debug("Creating roi Size");
        Label roiSizeLabel = new Label(group, SWT.NONE);
        roiSizeLabel.setText("ROI SIZE:");
        Text roiSizeInputText = new Text(group, SWT.BORDER);
        GridData gd = new GridData(SWT.FILL, SWT.CENTER, true, false);
        gd.widthHint = 10;
        roiSizeInputText.setLayoutData(gd);

        // UI -> EPICS
        roiSizeInputText.addListener(SWT.DefaultSelection, e -> {
	    		int value = (int) Double.parseDouble(roiSizeInputText.getText());
                moveScannable(roiSizeScannable, value);
                moveScannable(roiBinningScannable, value);
			}
	    );

	    // EPICS -> UI
	    IObserver roiSizeObserver = (source,arg) ->
	        Display.getDefault().asyncExec(() -> {
	            if (!roiSizeInputText.isDisposed()) {
	                int value = getScannablePosition(roiSizeScannable);
		            if ((int) Double.parseDouble(roiSizeInputText.getText()) != value) {
		            	roiSizeInputText.setText(String.valueOf(value));
		            }
	            }
	        });
	    roiSizeScannable.addIObserver(roiSizeObserver);
	    roiSizeInputText.addDisposeListener(e -> roiSizeScannable.deleteIObserver(roiSizeObserver));

	    // Set initial values on start
	    roiSizeInputText.setText(String.valueOf(getScannablePosition(roiSizeScannable)));
	    roiStartScale.setSelection(getScannablePosition(roiStartScannable));
	    logger.debug("Done creating view");
	}

	private int getScannablePosition(Scannable scannable) {
		int position = 0;
		try {
			position = (int) Double.parseDouble(scannable.getPosition().toString());
		} catch (DeviceException e) {
			logger.error("Failed to parse scannable position", e);
		}
		return position;
	}

    private void debounce(Runnable task, int delayMs) {

        Display display = Display.getDefault();

        // cancel previous task
        if (pendingTask != null) {
            display.timerExec(-1, pendingTask);
        }

        pendingTask = task;

        // schedule new task
        display.timerExec(delayMs, pendingTask);
    }

    private void moveScannable(Scannable sc, int value) {
    	logger.debug("Final value after pause: {}",value);
    	try {
    		sc.asynchronousMoveTo(value);
		} catch (DeviceException e1) {
			logger.error("Failed to set new value ", e1);
		}
    }
}
