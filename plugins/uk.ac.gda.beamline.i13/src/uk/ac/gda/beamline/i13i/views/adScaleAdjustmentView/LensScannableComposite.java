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

package uk.ac.gda.beamline.i13i.views.adScaleAdjustmentView;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableUtils;
import gda.factory.Finder;
import gda.observable.IObserver;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LensScannableComposite extends Composite {
	static final Logger logger = LoggerFactory.getLogger(LensScannableComposite.class);
	private Combo pcom;
	private Scannable lensScannable;
	private IObserver lensObserver;

	public LensScannableComposite(Composite parent, int style) {
		super(parent, style);
		setLayout(new GridLayout(1, false));

		Group group = new Group(this, SWT.NONE);
		group.setText("Lens");
		group.setLayout(new RowLayout());
		pcom = new Combo(group, SWT.SINGLE | SWT.BORDER | SWT.CENTER | SWT.READ_ONLY);
		pcom.setItems(new String[] { "X2 7.4mm * 4.9mm", "X4 3.7mm * 2.5mm", "X10 1.5mm * 1.0mm", "Unknown" });
		pcom.setVisible(true);
		
		addDisposeListener(new DisposeListener() {
			
			@Override
			public void widgetDisposed(DisposeEvent e) {
				if( lensScannable != null && lensObserver!=null)
					lensScannable.deleteIObserver(lensObserver);
			}
		});

	}
	
	void setLensScannable(Scannable s){
		lensScannable =s;
		lensObserver = new IObserver() {

			@Override
			public void update(Object source, Object arg) {
				try {
					final double pos = ScannableUtils.getCurrentPositionArray(lensScannable)[0];
					Display.getDefault().asyncExec(new Runnable() {

						@Override
						public void run() {
							pcom.select((int) pos);
						}
					});

				} catch (DeviceException e) {
					logger.error("Error getting position of " + lensScannable.getName(), e);
				}

			}
		};
		lensScannable.addIObserver(lensObserver);

		pcom.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				valueChanged((Combo) e.widget);
			}

			public void valueChanged(Combo c) {
				int npi = c.getSelectionIndex();
				try {
					lensScannable.asynchronousMoveTo(npi);
				} catch (DeviceException e) {
					logger.error("Error setting value for " + lensScannable.getName() + " to " + npi, e);
				}

			}
		});

		
		int npi = 0;
		try {
			npi = (int) ScannableUtils.getCurrentPositionArray(lensScannable)[0];
			pcom.select(npi);
		} catch (DeviceException e1) {
			pcom.select(3);
			logger.error("Error setting value for " + lensScannable.getName() + " to " + npi, e1);
		}
		
	}

}
