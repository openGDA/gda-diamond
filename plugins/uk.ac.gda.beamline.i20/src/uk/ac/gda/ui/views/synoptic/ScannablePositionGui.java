/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

package uk.ac.gda.ui.views.synoptic;

import org.apache.commons.lang.StringUtils;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.events.KeyListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Text;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.factory.Finder;
import gda.observable.IObserver;

public class ScannablePositionGui implements IObserver {

	private static final Logger logger = LoggerFactory.getLogger(ScannablePositionGui.class);

	private Scannable scannable;
	private Composite parent;
	private Text textbox;

	public ScannablePositionGui(Composite parent, String scannableName) {
		this.parent = parent;
		scannable = Finder.getInstance().find(scannableName);
	}

	private String getPosition(Scannable scn) {
		try {
			double dbl = Double.parseDouble((String) scn.getPosition());
			return String.format(scn.getOutputFormat()[0], dbl);
		} catch (DeviceException e) {
			return "";
		}
	}

	private void setPosition(String newPosition) {
		try {
			if (!scannable.isBusy() && !StringUtils.isEmpty(newPosition)) {
				double doublePosition = Double.parseDouble((String)newPosition);
				scannable.asynchronousMoveTo((Object)doublePosition);
			}
		} catch (DeviceException e) {
			logger.error("Problem moving scannable to new  scannable position", e);
		}
	}

	/**
	 * Add combo box to parent composite
	 * @throws DeviceException
	 */
	public void createTextbox() throws DeviceException {
		textbox = new Text(parent, SWT.BORDER);
		textbox.setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, false, 1, 1));
		textbox.setText( getPosition(scannable) );

		addListenerObservers();
	}

	private void addListenerObservers() {
		// update position when textbox widget changes
		textbox.addKeyListener(new KeyListener() {
			@Override
			public void keyReleased(KeyEvent e) {
			}

			@Override
			public void keyPressed(KeyEvent e) {
				if (e.keyCode==SWT.CR && !updatingTextFromObserver) {
					setPosition(textbox.getText());
				}
			}
		});

		scannable.addIObserver(this);
	}

	private volatile boolean updatingTextFromObserver = false;

	@Override
	public void update(Object source, Object arg) {
		Display.getDefault().asyncExec( new Runnable() {
			@Override
			public void run() {
				updatingTextFromObserver = true;
				textbox.setText(getPosition(scannable));
				textbox.update();
				updatingTextFromObserver = false;
			}

		});
	}
}
