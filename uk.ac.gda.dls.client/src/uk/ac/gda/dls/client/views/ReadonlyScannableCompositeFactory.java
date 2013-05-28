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

import gda.device.Scannable;
import gda.device.monitor.DummyMonitor;
import gda.rcp.views.CompositeFactory;

import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.IWorkbenchPartSite;
import org.springframework.beans.factory.InitializingBean;

import swing2swt.layout.BorderLayout;
import uk.ac.gda.ui.utils.SWTUtils;

public class ReadonlyScannableCompositeFactory implements CompositeFactory, InitializingBean {

	private String label;
	private Scannable scannable;
	private String units;
	private Integer decimalPlaces;

	public String getLabel() {
		return label;
	}

	public void setLabel(String label) {
		this.label = label;
	}

	public String getUnits() {
		return units;
	}

	public void setUnits(String units) {
		this.units = units;
	}

	public Scannable getScannable() {
		return scannable;
	}

	public void setScannable(Scannable scannable) {
		this.scannable = scannable;
	}

	public Integer getDecimalPlaces() {
		return decimalPlaces;
	}
	
	public void setDecimalPlaces(Integer decimalPlaces) {
		this.decimalPlaces = decimalPlaces;
	}
	
	Boolean forceLayoutOnLengthChange=true;

	public Boolean getForceLayoutOnLengthChange() {
		return forceLayoutOnLengthChange;
	}

	public void setForceLayoutOnLengthChange(Boolean forceLayoutOnLengthChange) {
		this.forceLayoutOnLengthChange = forceLayoutOnLengthChange;
	}	
	
	private Integer minPeriodMS;
	

	
	public Integer getMinPeriodMS() {
		return minPeriodMS;
	}

	/**
	 * 
	 * @param minPeriodMS
	 * 
	 * Is set the composite is updated at max once every minPeriodMS (ms)
	 */
	public void setMinPeriodMS(Integer minPeriodMS) {
		this.minPeriodMS = minPeriodMS;
	}

	@Override
	public Composite createComposite(Composite parent, int style, IWorkbenchPartSite iWorkbenchPartSite) {
		ReadonlyScannableComposite readonlyScannableComposite = new ReadonlyScannableComposite(parent, style, iWorkbenchPartSite.getShell().getDisplay(), scannable,
				label, units, decimalPlaces);
		readonlyScannableComposite.setMinPeriodMS(minPeriodMS);
		return readonlyScannableComposite;
	}

	public static void main(String... args) {

		Display display = new Display();
		Shell shell = new Shell(display);
		shell.setLayout(new BorderLayout());

		DummyMonitor dummy = new DummyMonitor();
		dummy.setName("dummy");
		dummy.configure();
		final ReadonlyScannableComposite comp = new ReadonlyScannableComposite(shell, SWT.NONE, display, dummy, "", "units", new Integer(2));
		comp.setLayoutData(BorderLayout.NORTH);
		comp.setVisible(true);
		shell.pack();
		shell.setSize(400, 400);
		SWTUtils.showCenteredShell(shell);
	}

	@Override
	public void afterPropertiesSet() throws Exception {
		if (scannable == null)
			throw new IllegalArgumentException("scannable is null");

	}
}
