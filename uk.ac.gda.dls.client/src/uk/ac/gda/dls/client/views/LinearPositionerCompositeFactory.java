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

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Scale;
import org.eclipse.swt.widgets.Shell;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.util.StringUtils;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.DummyScannable;
import gda.factory.FactoryException;
import gda.jython.InterfaceProvider;
import gda.jython.JythonStatus;
import gda.observable.IObserver;
import gda.rcp.views.CompositeFactory;
import swing2swt.layout.BorderLayout;
import uk.ac.gda.common.rcp.util.EclipseWidgetUtils;
import uk.ac.gda.ui.utils.SWTUtils;

public class LinearPositionerCompositeFactory implements CompositeFactory, InitializingBean {

	private String label;
	private Scannable positioner;
	private Integer labelWidth;
	private Integer contentWidth;
	private Integer lowScale;
	private Integer highScale;

	public String getLabel() {
		return label;
	}

	public void setLabel(String label) {
		this.label = label;
	}

	public Scannable getPositioner() {
		return positioner;
	}

	public void setPositioner(Scannable positioner) {
		this.positioner = positioner;
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

	public Integer getLowScale() {
		return lowScale;
	}

	public Integer getHighScale() {
		return highScale;
	}

	public void setLowScale(Integer lowScale) {
		this.lowScale = lowScale;
	}

	public void setHighScale(Integer highScale) {
		this.highScale = highScale;
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		return new LinearPositionerComposite(parent, style, positioner, label, labelWidth, contentWidth, lowScale, highScale);
	}

	public static void main(String... args) {

		Display display = new Display();
		Shell shell = new Shell(display);
		shell.setLayout(new BorderLayout());

		DummyScannable dummy = new DummyScannable();
		dummy.setName("dummy");
			try {
				dummy.configure();
			} catch (FactoryException e1) {
				// TODO Auto-generated catch block
			}

		try {
			dummy.moveTo(33);
//			dummy.moveTo(1);
		} catch (DeviceException e) {
			System.out.println("Can not move dummy to position 1");
		}

		final LinearPositionerComposite comp = new LinearPositionerComposite(shell, SWT.NONE, dummy, "", new Integer(100), new Integer(200), new Integer(0), new Integer(60));
		comp.setLayoutData(BorderLayout.NORTH);
		comp.setVisible(true);
		shell.pack();
		shell.setSize(400, 400);
		SWTUtils.showCenteredShell(shell);
	}

	@Override
	public void afterPropertiesSet() throws Exception {
		if (positioner == null)
			throw new IllegalArgumentException("positioner is null");

	}
}

class LinearPositionerComposite extends Composite {
	private static final Logger logger = LoggerFactory.getLogger(LinearPositionerComposite.class);
//	private Combo pcom;
	private Scale scale;
	Scannable positioner;
	IObserver observer;
	int selectionValue=-1;
	Integer labelWidth;
	Integer contentWidth;
	Integer lowScale;
	Integer highScale;

	Display display;
	private Runnable setSlideRunnable;
	String [] formats;

	LinearPositionerComposite(Composite parent, int style, Scannable positioner, String label, Integer labelWidth, Integer contentWidth, Integer lowScale, Integer highScale) {
		super(parent, style);
		this.display = parent.getDisplay();
		this.positioner = positioner;
		this.labelWidth=labelWidth;
		this.contentWidth=contentWidth;

		formats = positioner.getOutputFormat();
		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(this);
		GridDataFactory.fillDefaults().applyTo(this);
//		GridDataFactory.fillDefaults().align(GridData.FILL, SWT.FILL).applyTo(this);

//		Label lbl = new Label(this, SWT.RIGHT |SWT.WRAP | SWT.BORDER);
		Label lbl = new Label(this, SWT.RIGHT |SWT.WRAP);
		lbl.setText(StringUtils.hasLength(label) ? label : positioner.getName());

        GridData labelGridData = new GridData(GridData.HORIZONTAL_ALIGN_END);
		if(labelWidth != null)
			labelGridData.widthHint = labelWidth.intValue();
        lbl.setLayoutData(labelGridData);

		scale = new Scale (this, SWT.BORDER|SWT.HORIZONTAL);
		Rectangle clientArea = this.getClientArea ();
		scale.setBounds (clientArea.x, clientArea.y, 200, 64);
		scale.setMaximum(highScale);
		scale.setMinimum(lowScale);
//		scale.setPageIncrement(1);

//		pcom.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));
		GridData textGridData = new GridData(GridData.FILL_HORIZONTAL);
		textGridData.horizontalAlignment = GridData.HORIZONTAL_ALIGN_BEGINNING;
		if(contentWidth != null)
			textGridData.widthHint = contentWidth.intValue();
		scale.setLayoutData(textGridData);

		scale.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				valueChanged((Scale) e.widget);
			}
		});

		setSlideRunnable = new Runnable() {
			@Override
			public void run() {
				scale.setSelection(selectionValue);
				EclipseWidgetUtils.forceLayoutOfTopParent(LinearPositionerComposite.this);
			}
		};

		observer = new IObserver() {
			@Override
			public void update(Object source, Object arg) {
				logger.info("Got the who knows what type event!");
				displayValue();
			}
		};

		displayValue();

		positioner.addIObserver(observer);
	}

	void displayValue() {
		try {
			selectionValue=( (Double) positioner.getPosition()).intValue();
		} catch (DeviceException e) {
			selectionValue=0;
			logger.error("Error getting position for " + positioner.getName(), e);
		}

		if(!isDisposed()){
			display.asyncExec(setSlideRunnable);
		}
	}

	/**
	   * To change the positioner position when the input text fields changes.
	   *
	   * @param c
	   *            the event source
	   */
	public void valueChanged(Scale c) {
//		if (!c.isFocusControl())
//			return;

		try {
			int np=c.getSelection();
			this.positioner.asynchronousMoveTo( np );
			moveTo(this.positioner.getName(), np);
			logger.info("New value '" + np + "' send to " + positioner.getName() + ".");
			selectionValue = np;
		} catch (NumberFormatException e) {
			//logger.error("Invalid number format: " + c.getText());
	      } catch (DeviceException e) {
			logger.error("LinearPositioner device " + positioner.getName() + " move failed", e);
		}

	  }

	private void moveTo(String deviceName, double value){
		if( InterfaceProvider.getScanStatusHolder().getScanStatus() != JythonStatus.IDLE){
			logger.warn("Can not run scan because there is a scan running or paused");
			return;
		}

		String commandText=deviceName + ".moveTo(" + value +")";
		InterfaceProvider.getCommandRunner().runCommand(commandText);
		logger.info("Command sent: " + commandText);
	}

	@Override
	public void dispose() {
		positioner.deleteIObserver(observer);
		super.dispose();
	}
}
