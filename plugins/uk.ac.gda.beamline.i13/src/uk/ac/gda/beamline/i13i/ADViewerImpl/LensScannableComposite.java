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

package uk.ac.gda.beamline.i13i.ADViewerImpl;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannablePositionChangeEvent;
import gda.observable.IObserver;

import java.io.Serializable;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.common.rcp.util.GridUtils;

public class LensScannableComposite extends Composite {
	static final Logger logger = LoggerFactory.getLogger(LensScannableComposite.class);
	private Scannable lensScannable;
	private IObserver lensObserver;
	private Label text;
	private Group group;

	public LensScannableComposite(Composite parent, int style) {
		super(parent, style);
		setLayout(new GridLayout(1, false));

		group = new Group(this, SWT.NONE);
		group.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, true, false, 1, 1));
		GridDataFactory.fillDefaults().applyTo(group);
		group.setText("Lens");
		GridLayout gl_group = new GridLayout(1, false);
		gl_group.marginBottom = 1;
		gl_group.marginWidth = 1;
		group.setLayout(gl_group);
		text = new Label(group, SWT.NONE);
		text.setText("x10 2mm x 3mm");
		text.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, true, false, 1, 1));
		GridDataFactory.fillDefaults().applyTo(text);
		
		addDisposeListener(new DisposeListener() {
			
			@Override
			public void widgetDisposed(DisposeEvent e) {
				if( lensScannable != null && lensObserver!=null)
					lensScannable.deleteIObserver(lensObserver);
			}
		});

	}
	
	public void setLensScannable(Scannable s){
		lensScannable =s;
		lensObserver = new IObserver() {

			@Override
			public void update(Object source, final Object arg) {
					Display.getDefault().asyncExec(new Runnable() {

						@Override
						public void run() {
							String val="";
							if( arg instanceof ScannablePositionChangeEvent){
								val = (String) ((ScannablePositionChangeEvent)arg).newPosition;
							} else {
								val = arg.toString();
							}
							text.setText(val);
							GridUtils.layout(group);
						}
					});
			}
		};
		lensScannable.addIObserver(lensObserver);
		try {
			lensObserver.update(lensScannable, new ScannablePositionChangeEvent((Serializable) lensScannable.getPosition()));
		} catch (DeviceException e) {
			logger.error("Error reading lens", e);
		}
	}

}
