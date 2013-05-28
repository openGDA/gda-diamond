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

package uk.ac.gda.dls.client.views;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableGetPositionWrapper;
import gda.device.scannable.ScannablePositionChangeEvent;
import gda.device.scannable.ScannableStatus;
import gda.observable.IObserver;

import java.text.NumberFormat;
import java.util.Scanner;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.StringUtils;

import uk.ac.gda.common.rcp.util.EclipseWidgetUtils;

public class ReadonlyScannableComposite extends Composite {
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
	private Integer minPeriodMS=null;
	private Boolean textUpdateScheduled=false;

	public Integer getMinPeriodMS() {
		return minPeriodMS;
	}

	public void setMinPeriodMS(Integer minPeriodMS) {
		this.minPeriodMS = minPeriodMS;
	}

	public ReadonlyScannableComposite(Composite parent, int style, final Display display, final Scannable scannable, String label, final String units, 
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
				textUpdateScheduled=false;
			}
		};		
		
		observer = new IObserver() {
			
			@Override
			public void update(Object source, Object arg) {
				if( arg instanceof ScannablePositionChangeEvent){
					final ScannablePositionChangeEvent event = (ScannablePositionChangeEvent)arg;
					setVal(new ScannableGetPositionWrapper(event.newPosition, formats).getStringFormattedValues()[0]);
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
			if( minPeriodMS != null){
				if( !textUpdateScheduled){
					textUpdateScheduled=true;
					display.asyncExec(new Runnable(){

						@Override
						public void run() {
							display.timerExec(minPeriodMS, setTextRunnable);
						}});
				}
			} else {
				display.asyncExec(setTextRunnable);
			}
		}
	}

	@Override
	public void dispose() {
		scannable.deleteIObserver(observer);
		super.dispose();
	}
	

}
