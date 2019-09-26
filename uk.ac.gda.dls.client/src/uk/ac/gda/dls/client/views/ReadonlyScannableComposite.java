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
import gda.device.EnumPositionerStatus;
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
	private Display parentDisplay;
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
		this.parentDisplay = parent.getDisplay();
		this.scannable = scannable;
		this.decimalPlaces = decimalPlaces;

		// Cache name here to avoid excessive RMI calls (especially in logging)
		final String scannableName = scannable.getName();

		if (StringUtils.hasLength(units)) {
			suffix = " " + units;
		}

		formats = scannable.getOutputFormat();
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(this);
		GridDataFactory.fillDefaults().applyTo(this);

		final Label lbl = new Label(this, SWT.NONE | SWT.CENTER);
		lbl.setText(StringUtils.hasLength(label) ? label : scannableName);
		lbl.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));

		final int textStyle = SWT.SINGLE | SWT.BORDER | SWT.READ_ONLY | SWT.CENTER;
		text = new Text(this, textStyle);
		text.setEditable(false);
		text.setText("000000");
		text.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		EclipseWidgetUtils.forceLayoutOfTopParent(ReadonlyScannableComposite.this);

		setTextRunnable = () -> {
			if (text.isDisposed()) {
				logger.trace("Attempting to update text for disposed widget {}", scannableName);
				return;
			}
			beforeUpdateText(text, val);
			final int currentLength = text.getText().length();
			final String valPlusUnits = val + suffix;
			text.setText(valPlusUnits);
			final int diff = valPlusUnits.length() - currentLength;
			if ((diff > 0 || diff < -3) && resize) {
				EclipseWidgetUtils.forceLayoutOfTopParent(ReadonlyScannableComposite.this);
			}
			if (colourMap != null) {
				final Integer colorId = colourMap.get(val);
				if (colorId != null) {
					text.setForeground(Display.getCurrent().getSystemColor(colorId));
				}
			}
			textUpdateScheduled = false;
			afterUpdateText(text, val);
		};

		observer = (source, arg) -> {
			logger.trace("Update to {}: source = {}, arg = {}", scannableName, source, arg);
			if (arg instanceof ScannablePositionChangeEvent) {
				// ScannablePositionChangeEvent - can get current position directly from the event
				final ScannablePositionChangeEvent event = (ScannablePositionChangeEvent) arg;
				setVal(new ScannableGetPositionWrapper(event.newPosition, formats).getStringFormattedValues()[0]);
			} else if ((arg instanceof ScannableStatus && (ScannableStatus) arg == ScannableStatus.IDLE)
					|| (arg instanceof EnumPositionerStatus && (EnumPositionerStatus) arg == EnumPositionerStatus.IDLE)) {
				// Scannable is idle - get current position from the scannable
				try {
					final ScannableGetPositionWrapper wrapper = new ScannableGetPositionWrapper(scannable.getPosition(), formats);
					setVal(wrapper.getStringFormattedValues()[0]);
				} catch (DeviceException e1) {
					setVal("Error");
					logger.error("Error getting position for {}", scannableName, e1);
				}
			} else if (arg instanceof String) {
				// String - assume this is the position
				setVal((String) arg);
			} else {
				// Anything else - assume the argument is the position
				final ScannableGetPositionWrapper wrapper = new ScannableGetPositionWrapper(arg, formats);
				setVal(wrapper.getStringFormattedValues()[0]);
			}
		};

		try {
			final ScannableGetPositionWrapper wrapper = new ScannableGetPositionWrapper(scannable.getPosition(), formats);
			setVal(wrapper.getStringFormattedValues()[0]);
		} catch (DeviceException e1) {
			setVal("Error");
			logger.error("Error getting position for {}", scannableName, e1);
		}

		scannable.addIObserver(observer);
	}

	protected void setVal(String newVal) {
		val = newVal;
		if (decimalPlaces != null) {
			final Scanner sc = new Scanner(newVal.trim());
			if (sc.hasNextDouble()) {
				final NumberFormat format = NumberFormat.getInstance();
				format.setMaximumFractionDigits(decimalPlaces.intValue());
				val = format.format(sc.nextDouble());
			}
			sc.close();
		}

		if (!isDisposed()) {
			if (minPeriodMS != null) {
				if (!textUpdateScheduled) {
					textUpdateScheduled = true;
					parentDisplay.asyncExec(() -> parentDisplay.timerExec(minPeriodMS, setTextRunnable));
				}
			} else {
				parentDisplay.asyncExec(setTextRunnable);
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
		// by default, do nothing
	}

	@SuppressWarnings("unused")
	protected void afterUpdateText(Text text, String value) {
		// by default, do nothing
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
