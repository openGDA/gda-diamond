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

import java.text.NumberFormat;
import java.util.Map;
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

import com.swtdesigner.SWTResourceManager;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableGetPositionWrapper;
import gda.device.scannable.ScannablePositionChangeEvent;
import gda.device.scannable.ScannableStatus;
import gda.observable.IObserver;
import uk.ac.gda.common.rcp.util.EclipseWidgetUtils;

public class ReadonlyScannableComposite extends Composite {
	private static final Logger logger = LoggerFactory.getLogger(ReadonlyScannableComposite.class);
	private Text text;
	private Scannable scannable;
	private IObserver observer;
	private String val = "...";
	private Display display;
	private Runnable setTextRunnable;
	private String[] formats;
	private String suffix = "";
	private Integer decimalPlaces;
	private Integer minPeriodMS = null;
	private Boolean textUpdateScheduled = false;
	private Map<String, Integer> colourMap;

	public ReadonlyScannableComposite(Composite parent, int style, final Scannable scannable, String label, final String units, Integer decimalPlaces) {
		this(parent, style, scannable, label, units, decimalPlaces, true);
	}

	public ReadonlyScannableComposite(Composite parent, int style, final Scannable scannable, String label, final String units, Integer decimalPlaces, final boolean resize) {
		super(parent, style);
		this.display = parent.getDisplay();
		this.scannable = scannable;
		this.decimalPlaces = decimalPlaces;

		if (StringUtils.hasLength(units)) {
			suffix = " " + units;
		}

		formats = scannable.getOutputFormat();
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(this);
		GridDataFactory.fillDefaults().applyTo(this);

		Label lbl = new Label(this, SWT.NONE | SWT.CENTER);
		lbl.setText(StringUtils.hasLength(label) ? label : scannable.getName());
		lbl.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));

		int textStyle = SWT.SINGLE | SWT.BORDER | SWT.READ_ONLY | SWT.CENTER;
		text = new Text(this, textStyle);
		text.setEditable(false);
		text.setText("000000");
		text.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		EclipseWidgetUtils.forceLayoutOfTopParent(ReadonlyScannableComposite.this);
		setTextRunnable = new Runnable() {

			@Override
			public void run() {
				beforeUpdateText(text, val);
				int currentLength = text.getText().length();
				String valPlusUnits = val + suffix;
				text.setText(valPlusUnits);
				int diff = valPlusUnits.length() - currentLength;
				if ((diff > 0 || diff < -3) && resize) {
					EclipseWidgetUtils.forceLayoutOfTopParent(ReadonlyScannableComposite.this);
				}
				if (colourMap != null) {
					Integer colorId = colourMap.get(val);
					if (colorId != null) {
						text.setForeground(Display.getCurrent().getSystemColor(colorId));
					}
				}
				textUpdateScheduled = false;
				afterUpdateText(text, val);
			}
		};

		observer = new IObserver() {

			@Override
			public void update(Object source, Object arg) {
				if (arg instanceof ScannablePositionChangeEvent) {
					final ScannablePositionChangeEvent event = (ScannablePositionChangeEvent) arg;
					setVal(new ScannableGetPositionWrapper(event.newPosition, formats).getStringFormattedValues()[0]);
				} else if (arg instanceof ScannableStatus && ((ScannableStatus) arg) == ScannableStatus.IDLE) {
					try {
						ScannableGetPositionWrapper wrapper = new ScannableGetPositionWrapper(scannable.getPosition(), formats);
						val = wrapper.getStringFormattedValues()[0];
					} catch (DeviceException e1) {
						val = "Error";
						logger.error("Error getting position for " + scannable.getName(), e1);
					}
					setVal(val);
				} else if (arg instanceof String) {
					setVal((String) arg);
				} else {
					ScannableGetPositionWrapper wrapper = new ScannableGetPositionWrapper(arg, formats);
					setVal(wrapper.getStringFormattedValues()[0]);
				}
			}
		};

		try {
			ScannableGetPositionWrapper wrapper = new ScannableGetPositionWrapper(scannable.getPosition(), formats);
			val = wrapper.getStringFormattedValues()[0];
		} catch (DeviceException e1) {
			val = "Error";
			logger.error("Error getting position for " + scannable.getName(), e1);
		}
		setVal(val);

		scannable.addIObserver(observer);
	}

	private void setVal(String newVal) {
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
		if (!isDisposed()) {
			if (minPeriodMS != null) {
				if (!textUpdateScheduled) {
					textUpdateScheduled = true;
					display.asyncExec(new Runnable() {

						@Override
						public void run() {
							display.timerExec(minPeriodMS, setTextRunnable);
						}
					});
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

	@SuppressWarnings("unused")
	protected void beforeUpdateText(Text text, String value) {
	}

	@SuppressWarnings("unused")
	protected void afterUpdateText(Text text, String value) {
	}

	public Map<String, Integer> getColourMap() {
		return colourMap;
	}

	/**
	 * @param colourMap
	 *            map of ids to pass to Display.getSystemColor to allow setting of foreground based on value Useful for enums
	 */
	public void setColourMap(Map<String, Integer> colourMap) {
		this.colourMap = colourMap;
	}

	public Integer getMinPeriodMS() {
		return minPeriodMS;
	}

	public void setMinPeriodMS(Integer minPeriodMS) {
		this.minPeriodMS = minPeriodMS;
	}

}
