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

package uk.ac.gda.dls.client.views;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.enumpositioner.DummyEnumPositioner;
import gda.observable.IObserver;
import gda.rcp.views.CompositeFactory;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Shell;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;

import swing2swt.layout.BorderLayout;
import uk.ac.gda.ui.utils.SWTUtils;

public class EnumCheckboxCompositeFactory implements CompositeFactory, InitializingBean {

	String label;
	String tooltip = "";
	private Scannable scannable;
	private String unselectedString;
	private String selectedString;

	public static Composite createComposite(Composite parent, int style, String label,
			final Scannable scannable, final String selectedString, String unselectedString, String tooltip) {
		return new EnumCheckboxComposite(parent, style, label, scannable, selectedString, unselectedString,
				tooltip);
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		return new EnumCheckboxComposite(parent, style, label, scannable,
				selectedString, unselectedString, tooltip);
	}

	public String getLabel() {
		return label;
	}

	public void setLabel(String label) {
		this.label = label;
	}

	public Scannable getScannable() {
		return scannable;
	}

	public void setScannable(Scannable scannable) {
		this.scannable = scannable;
	}

	public String getUnselectedString() {
		return unselectedString;
	}

	public void setUnselectedString(String unselectedString) {
		this.unselectedString = unselectedString;
	}

	public String getSelectedString() {
		return selectedString;
	}

	public void setSelectedString(String selectedString) {
		this.selectedString = selectedString;
	}

	@Override
	public void afterPropertiesSet() throws Exception {
		if (scannable == null)
			throw new IllegalArgumentException("scannable is null");
		if (unselectedString == null)
			throw new IllegalArgumentException("unselectedString is null");
		if (label == null)
			throw new IllegalArgumentException("label is null");
		if (selectedString == null)
			throw new IllegalArgumentException("selectedString is null");
	}

	public static void main(String... args) {

		Display display = new Display();
		Shell shell = new Shell(display);
		shell.setLayout(new BorderLayout());

		DummyEnumPositioner positioner = new DummyEnumPositioner();
		positioner.setName("positioner");
		positioner.setPositions(new String []{ "on", "off"});
		final EnumCheckboxComposite comp = new EnumCheckboxComposite(shell, SWT.NONE, "My Label", positioner, "on", "off",
				"tooltip");
		comp.setLayoutData(BorderLayout.NORTH);
		comp.setVisible(true);
		final EnumCheckboxComposite comp1 = new EnumCheckboxComposite(shell, SWT.NONE, "My Label", positioner, "on", "off",
		"tooltip");
		comp1.setLayoutData(BorderLayout.SOUTH);
		comp1.setVisible(true);
		shell.pack();
		shell.setSize(400, 400);
		SWTUtils.showCenteredShell(shell);
	}

	public String getTooltip() {
		return tooltip;
	}

	public void setTooltip(String tooltip) {
		this.tooltip = tooltip;
	}

}

class EnumCheckboxComposite extends Composite {
	private static final Logger logger = LoggerFactory.getLogger(EnumCheckboxComposite.class);
	final private Button chkBox;
	final private String selectedString;
	final private Scannable enumScannable;

	EnumCheckboxComposite(Composite parent, int style, String label,
			final Scannable enumScannable, final String selectedString, final String unselectedString, String tooltip) {
		super(parent, style);
		final Display display = parent.getDisplay();
		this.selectedString = selectedString;
		this.enumScannable = enumScannable;
		GridLayoutFactory.fillDefaults().numColumns(1).applyTo(this);
		GridDataFactory.fillDefaults().applyTo(this);

		chkBox = new Button(this, SWT.CHECK);
		chkBox.setText(label);
		chkBox.setToolTipText(tooltip);
		setBtnAutoAlignOnOff();
		chkBox.addSelectionListener(new SelectionAdapter() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				super.widgetSelected(e);
				String position = chkBox.getSelection() ? selectedString : unselectedString;
				try {
					enumScannable.moveTo(position);
				} catch (DeviceException e1) {
					logger.error("Error changing value of " + enumScannable.getName() + " to " + position, e1);
				}
			}
		});
		enumScannable.addIObserver(new IObserver() {

			@Override
			public void update(Object source, Object arg) {
				display.asyncExec(new Runnable() {

					@Override
					public void run() {
						setBtnAutoAlignOnOff();
					}

				});
			}
		});
	}
	
	@Override
	public void setEnabled(boolean isEnabled) {
		super.setEnabled(isEnabled);
		chkBox.setEnabled(isEnabled);
	}

	void setBtnAutoAlignOnOff() {
		try {
			chkBox.setSelection(enumScannable.getPosition().equals(selectedString));
		} catch (DeviceException e) {
			logger.error("Error getting value for " + enumScannable.getName(), e);
		}
	}

}