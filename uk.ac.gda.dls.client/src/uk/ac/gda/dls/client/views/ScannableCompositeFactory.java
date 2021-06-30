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

import java.text.NumberFormat;
import java.util.Scanner;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.VerifyKeyListener;
import org.eclipse.swt.events.VerifyEvent;
import org.eclipse.swt.events.VerifyListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.util.StringUtils;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.DummyScannable;
import gda.device.scannable.ScannableGetPositionWrapper;
import gda.device.scannable.ScannablePositionChangeEvent;
import gda.factory.FactoryException;
import gda.observable.IObserver;
import gda.rcp.views.CompositeFactory;
import swing2swt.layout.BorderLayout;
import uk.ac.gda.common.rcp.util.EclipseWidgetUtils;
import uk.ac.gda.ui.utils.SWTUtils;

public class ScannableCompositeFactory implements CompositeFactory, InitializingBean {

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
		return new ScannableComposite(parent, style, scannable,
				label, units, decimalPlaces, labelWidth, contentWidth);
	}

	public static void main(String... args) {
		Display display = new Display();
		Shell shell = new Shell(display);
		shell.setLayout(new BorderLayout());
		DummyScannable dummy = new DummyScannable();
		dummy.setName("dummy");
		try {
			dummy.configure();
		} catch (FactoryException e) {
			// TODO Auto-generated catch block
		}
		ScannableComposite comp = new ScannableComposite(shell, SWT.NONE, dummy, "", "units", 2, 100, 200);
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


class AmountVerifyKeyListener implements VerifyListener, VerifyKeyListener             {

    private static final String REGEX = "^[-+]?[0-9]*[,]?[0-9]{0,2}+$";

    private static final Pattern pattern = Pattern.compile(REGEX);

    @Override
	public void verifyText(VerifyEvent verifyevent) {
        verify(verifyevent);
    }

    @Override
	public void verifyKey(VerifyEvent verifyevent) {
        verify(verifyevent);
    }

    private void verify (VerifyEvent e) {
        String string = e.text;
        char[] chars = new char[string.length()];
        string.getChars(0, chars.length, chars, 0);

        Text text = (Text)e.getSource();

        if ( ( ",".equals(string) || ".".equals(string) ) && text.getText().indexOf(',') >= 0 ) {
            e.doit = false;
            return;
        }

        for (int i = 0; i < chars.length; i++) {
            if (!(('0' <= chars[i] && chars[i] <= '9') || chars[i] == '.' ||  chars[i] == ',' || chars[i] == '-')) {
                e.doit = false;
                return;
            }


            if ( chars[i] == '.' ) {
                chars[i] = ',';
            }
        }

        e.text = new String(chars);

        final String oldS = text.getText();
        String newS = oldS.substring(0, e.start) + e.text + oldS.substring(e.end);
        Matcher matcher = pattern.matcher(newS);
        if ( !matcher.matches() ) {
            e.doit = false;
            return;
        }

    }
}

class ScannableComposite extends Composite {
	private static final Logger logger = LoggerFactory.getLogger(ScannableComposite.class);
	private Text text;
	Scannable scannable;
	IObserver observer;
	String val = "...";
	Display display;
	private Runnable setTextRunnable;
	String [] formats;
	Integer decimalPlaces;
	Integer labelWidth;
	Integer contentWidth;

	ScannableComposite(Composite parent, int style, Scannable scannable, String label, final String units,
			Integer decimalPlaces, Integer labelWidth, Integer contentWidth ) {
		super(parent, style);
		this.display = parent.getDisplay();
		this.scannable = scannable;
		this.decimalPlaces = decimalPlaces;
		this.labelWidth=labelWidth;
		this.contentWidth=contentWidth;


		formats = scannable.getOutputFormat();
		GridLayoutFactory.fillDefaults().numColumns(3).applyTo(this);
		GridDataFactory.fillDefaults().applyTo(this);

//		Label lbl = new Label(this, SWT.NONE | SWT.CENTER);
//		Label lbl = new Label(this, SWT.RIGHT |SWT.WRAP | SWT.BORDER);
		Label lbl = new Label(this, SWT.RIGHT |SWT.WRAP);
		lbl.setText(StringUtils.hasLength(label) ? label : scannable.getName());

		GridData labelGridData = new GridData(GridData.HORIZONTAL_ALIGN_END);
		if(labelWidth != null)
			labelGridData.widthHint = labelWidth.intValue();
        lbl.setLayoutData(labelGridData);


		int textStyle = SWT.SINGLE | SWT.BORDER | SWT.CENTER;
		text = new Text(this,textStyle);
		text.setEditable(true);
		text.setText("     ");

		GridData textGridData = new GridData(GridData.FILL_HORIZONTAL);
		textGridData.horizontalAlignment = GridData.HORIZONTAL_ALIGN_BEGINNING;
		if(contentWidth != null)
			textGridData.widthHint = contentWidth.intValue();
		text.setLayoutData(textGridData);

		Label lbUnit = new Label(this, SWT.LEFT);
		lbUnit.setText(StringUtils.hasLength(units) ? units : " ");

//		text.addVerifyListener(new AmountVerifyKeyListener());

		text.addListener(SWT.DefaultSelection, new Listener() {
			@Override
			public void handleEvent(Event e) {
				System.out.println(e.widget + " - Default selection made");
				valueChanged( (Text)e.widget );
		      }
		    });


		setTextRunnable = new Runnable() {
			@Override
			public void run() {
				int currentLength = text.getText().length();
				String valString = val;
				text.setText(valString);
				int diff = valString.length()-currentLength;
				if ( diff > 0 || diff < -3)
					EclipseWidgetUtils.forceLayoutOfTopParent(ScannableComposite.this);
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

	/**
	   * To change the scannable position when the input text fields changes.
	   *
	   * @param t
	   *            the event source
	   */
	public void valueChanged(Text t) {
		if (!t.isFocusControl())
			return;

		try {
			double newPosition = Double.parseDouble(t.getText());
			this.scannable.asynchronousMoveTo(newPosition);
			logger.info("New value send to the scannable device " + scannable.getName() + " to move to " + newPosition + ".");
		} catch (NumberFormatException e) {
			text.setText("");
			logger.error("Invalid number format: " + t.getText());
	      } catch (DeviceException e) {
			logger.error("Scannable device " + scannable.getName() + " move failed", e);
		}

	  }

	@Override
	public void dispose() {
		scannable.deleteIObserver(observer);
		super.dispose();
	}


}
