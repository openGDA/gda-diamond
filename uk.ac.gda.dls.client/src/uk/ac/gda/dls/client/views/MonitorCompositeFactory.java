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
import gda.observable.IObserver;
import gda.rcp.views.CompositeFactory;

import java.text.NumberFormat;
import java.util.Scanner;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.util.StringUtils;

import swing2swt.layout.BorderLayout;
import uk.ac.gda.common.rcp.util.EclipseWidgetUtils;
import uk.ac.gda.ui.utils.SWTUtils;

public class MonitorCompositeFactory implements CompositeFactory, InitializingBean {
	private String label;
	private Scannable scannable;
	private String units;
	private Integer decimalPlaces;
	private Integer labelWidth;
	private Integer contentWidth;

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

	public Integer getLabelWidth() {
		return labelWidth;
	}

	public Integer getContentWidth() {
		return contentWidth;
	}

	public void setContentWidth(Integer contentWidth) {
		this.contentWidth = contentWidth;
	}

	public void setLabelWidth(Integer labelWidth) {
		this.labelWidth = labelWidth;
	}
	
	@Override
	public Composite createComposite(Composite parent, int style) {
		return new MonitorComposite(parent, style, scannable,
				label, units, decimalPlaces, labelWidth, contentWidth);
	}

	public static void main(String... args) {
		Display display = new Display();
		Shell shell = new Shell(display);
		shell.setLayout(new BorderLayout());

		DummyMonitor dummy = new DummyMonitor();
		dummy.setName("dummy");
		dummy.configure();
		final MonitorComposite comp = new MonitorComposite(shell, SWT.NONE, dummy, "", "units", new Integer(2), new Integer(100), new Integer(200));
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

class MonitorComposite extends Composite {
	private static final Logger logger = LoggerFactory.getLogger(MonitorComposite.class);
	private Text text;
	Scannable scannable;
	IObserver observer;
	String val = "...";
	Display display;
	private Runnable setTextRunnable;
	String [] formats;
	String suffix="";
	Integer decimalPlaces;
	Integer labelWidth;
	Integer contentWidth;

	MonitorComposite(Composite parent, int style, Scannable scannable, String label, final String units,
			Integer decimalPlaces, Integer labelWidth, Integer contentWidth) {
		super(parent, style);
		this.scannable = scannable;
		this.decimalPlaces = decimalPlaces;
		this.labelWidth=labelWidth;
		this.contentWidth=contentWidth;
		this.display=parent.getDisplay();

		if( StringUtils.hasLength(units))
			suffix = " " + units;
		
		formats = scannable.getOutputFormat();
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(this);
		GridDataFactory.fillDefaults().applyTo(this);		

		Label lbl = new Label(this, SWT.RIGHT |SWT.WRAP);
		lbl.setText(StringUtils.hasLength(label) ? label : scannable.getName());
		GridData labelGridData = new GridData(GridData.HORIZONTAL_ALIGN_END);

		if(labelWidth != null)
			labelGridData.widthHint = labelWidth.intValue();
        lbl.setLayoutData(labelGridData);
		
		text = new Text(this, SWT.READ_ONLY | SWT.BORDER | SWT.CENTER);
		text.setEditable(false);
		
		GridData textGridData = new GridData(GridData.FILL_HORIZONTAL);
		textGridData.horizontalAlignment = GridData.HORIZONTAL_ALIGN_BEGINNING;
		if(contentWidth != null)
			textGridData.widthHint = contentWidth.intValue();
		text.setLayoutData(textGridData);
		
		setTextRunnable = new Runnable() {
			@Override
			public void run() {
				int currentLength = text.getText().length();
				String valPlusUnits = val+suffix;
				text.setText(valPlusUnits);
				int diff = valPlusUnits.length()-currentLength;
				if ( diff > 0 || diff < -3)
					EclipseWidgetUtils.forceLayoutOfTopParent(MonitorComposite.this);
			}
		};		
		
		observer = new IObserver() {
			
			@Override
			public void update(Object source, Object arg) {
				if( arg instanceof ScannablePositionChangeEvent){
					final ScannablePositionChangeEvent event = (ScannablePositionChangeEvent)arg;
					setVal(event.newPosition.toString());
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
			sc.close();
		}
		val = newVal;
		if(!isDisposed())
			display.asyncExec(setTextRunnable);
	}

	@Override
	public void dispose() {
		scannable.deleteIObserver(observer);
		super.dispose();
	}

}
