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
import gda.device.monitor.DummyMonitor;
import gda.device.scannable.ScannableGetPositionWrapper;
import gda.device.scannable.ScannablePositionChangeEvent;
import gda.device.scannable.ScannableStatus;
import gda.observable.IObserver;
import gda.rcp.views.CompositeFactory;

import java.text.NumberFormat;
import java.util.Scanner;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.IWorkbenchPartSite;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.util.StringUtils;

import swing2swt.layout.BorderLayout;
import uk.ac.gda.common.rcp.util.EclipseWidgetUtils;
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
	
	@Override
	public Composite createComposite(Composite parent, int style, IWorkbenchPartSite iWorkbenchPartSite) {
		return new ReadonlyScannableComposite(parent, style, iWorkbenchPartSite.getShell().getDisplay(), scannable,
				label, units, decimalPlaces);
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

class ReadonlyScannableComposite extends Composite {
	private static final Logger logger = LoggerFactory.getLogger(ReadonlyScannableComposite.class);
	private Text text;
	Scannable scannable;
	IObserver observer;
	String val = "...";
	Display display;
	private Runnable setTextRunnable;
	String [] formats;
	String suffix="";
	Integer decimalPlaces;

	ReadonlyScannableComposite(Composite parent, int style, final Display display, final Scannable scannable, String label, final String units, 
			Integer decimalPlaces) {
		super(parent, style);
		this.display = display;
		this.scannable = scannable;
		this.decimalPlaces = decimalPlaces;
		
		if( StringUtils.hasLength(units)){
			suffix = " " + units;
		}
		
		formats = scannable.getOutputFormat();
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(this);
		GridDataFactory.fillDefaults().applyTo(this);		
		
		Label lbl = new Label(this, SWT.NONE | SWT.CENTER);
		lbl.setText(StringUtils.hasLength(label) ? label : scannable.getName());
		
		int textStyle = SWT.SINGLE | SWT.BORDER | SWT.READ_ONLY | SWT.CENTER;
		text = new Text(this,textStyle);
		text.setEditable(false);
		setTextRunnable = new Runnable() {
			@Override
			public void run() {
				int currentLength = text.getText().length();
				String valPlusUnits = val+suffix;
				text.setText(valPlusUnits);
				int diff = valPlusUnits.length()-currentLength;
				if ( diff > 0 || diff < -3)
					EclipseWidgetUtils.forceLayoutOfTopParent(ReadonlyScannableComposite.this);
			}
		};		
		
		observer = new IObserver() {
			
			@Override
			public void update(Object source, Object arg) {
				if( arg instanceof ScannablePositionChangeEvent){
					final ScannablePositionChangeEvent event = (ScannablePositionChangeEvent)arg;
					setVal(event.newPosition.toString());
				} else if( arg instanceof ScannableStatus && ((ScannableStatus)arg).status == ScannableStatus.IDLE){
					try {
						ScannableGetPositionWrapper wrapper = new ScannableGetPositionWrapper(scannable.getPosition(),formats );
						val = wrapper.getStringFormattedValues()[0];
					} catch (DeviceException e1) {
						val = "Error";
						logger.error("Error getting position for " + scannable.getName(),e1);
					}
					setVal(val);
				} else if( arg instanceof String){
					setVal((String)arg);
				} else {
					ScannableGetPositionWrapper wrapper = new ScannableGetPositionWrapper(arg,formats );
					setVal(wrapper.getStringFormattedValues()[0]);
				}
			}
		};
		
		try {
			ScannableGetPositionWrapper wrapper = new ScannableGetPositionWrapper(scannable.getPosition(),formats );
			val = wrapper.getStringFormattedValues()[0];
		} catch (DeviceException e1) {
			val = "Error";
			logger.error("Error getting position for " + scannable.getName(),e1);
		}
		setVal(val);

		scannable.addIObserver(observer);
	}

	void setVal(String newVal) {
		if (decimalPlaces != null) {
			Scanner sc = new Scanner(newVal.trim());
			
			if (sc.hasNextDouble()) {
				NumberFormat format = NumberFormat.getInstance();
				format.setMaximumFractionDigits(decimalPlaces.intValue());
				newVal = format.format(sc.nextDouble());
			}
		}
		val = newVal;
		if(!isDisposed()){
			display.asyncExec(setTextRunnable);
		}
	}

	@Override
	public void dispose() {
		scannable.deleteIObserver(observer);
		super.dispose();
	}
	

}
