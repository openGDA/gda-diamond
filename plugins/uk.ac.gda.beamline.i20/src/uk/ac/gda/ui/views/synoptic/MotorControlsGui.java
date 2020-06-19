/*-
 * Copyright © 2016 Diamond Light Source Ltd.
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

import org.eclipse.jface.dialogs.IInputValidator;
import org.eclipse.jface.dialogs.InputDialog;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.events.KeyListener;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.events.VerifyEvent;
import org.eclipse.swt.events.VerifyListener;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.MenuItem;
import org.eclipse.swt.widgets.Text;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.ScannableMotionUnits;
import gda.factory.Finder;
import gda.observable.IObserver;
import gda.rcp.GDAClientActivator;
import uk.ac.diamond.daq.concurrent.Async;

/**
 * Class to provide GUI elements for moving a motor and includes :
 * <li> Buttons to increase and decrease position using small steps.
 * Step size can be adjust via a context menu from the increase and decrease buttons.
 * <li> A 'demand position' textbox to manually enter a new position.
 * <li> The current position of the motor is also displayed
 * <li> A 'Stop motion' button which can be used to stop motion. This is active
 * when the motor changes position (either from gui controls due to change from Jython, Epics etc)  *
 *
 *@author Iain Hall
 * @since 20/10/2016
 */
public class MotorControlsGui implements IObserver {

	private static final Logger logger = LoggerFactory.getLogger(MotorControlsGui.class);

	private final Composite parent;
	private final Scannable scannableMotor;

	private Composite group;
	private Label nameLabel;
	private Text demandPositionTextbox;
	private Text actualPositionTextbox;
	private Button stopButton;
	private Button increaseButton;
	private Button decreaseButton;

	private double minPos;
	private double maxPos;
	private String unitString;

	/** Motor position increment/decrement size used when clicking the increase, decrease position buttons*/
	private double motorStepSize;

	/** Position of widget relative to origin of background image (percent). */
	private Point relativePosition;

	/** Time interval between label updates during motor moves [ms]*/
	private int motorPosLabelUpdateIntervalMs = 100;

	/** Current update status of the widget - i.e. updating labels due to motor moves, moving motor to new position */
	private volatile Status currentWidgetStatus;

	public final static int FULL_LAYOUT = 0;
	public final static int COMPACT_LAYOUT = 1;
	public final static int HIDE_BORDER = 2;
	public final static int HIDE_STOP_CONTROLS = 4;
	private int layoutOptions = FULL_LAYOUT;

	/** States that the gui can be in */
	enum Status {
		IDLE, // Nothing happening
		MOTOR_IS_MOVING; // Motor is currently moving, GUI updating to show new position
	}

	public MotorControlsGui(Composite parent, String scannableMotorName) throws DeviceException {
		this(parent, scannableMotorName, false);
	}

	public MotorControlsGui(Composite parent, Scannable scannableMotor) throws DeviceException {
		this(parent, scannableMotor, false);
	}

	public MotorControlsGui(Composite parent, String scannableMotorName, int options) throws DeviceException {
		this.parent = parent;
		layoutOptions = options;
		scannableMotor = Finder.find(scannableMotorName);
		setup();
	}

	public MotorControlsGui(Composite parent, String scannableMotorName, boolean useCompactLayout) throws DeviceException {
		this.parent = parent;
		layoutOptions = useCompactLayout==true ? COMPACT_LAYOUT : FULL_LAYOUT;
		scannableMotor = Finder.find(scannableMotorName);
		setup();
	}

	public MotorControlsGui(Composite parent, Scannable scannableMotor, boolean useCompactLayout) throws DeviceException {
		this.parent = parent;
		layoutOptions = useCompactLayout==true ? COMPACT_LAYOUT : FULL_LAYOUT;
		this.scannableMotor = scannableMotor;
		setup();
	}

	private void setup() throws DeviceException {
		minPos = 0.0;
		maxPos = 0.0;
		motorStepSize = 0.5;
		unitString = "mm";

		createControls();
		addListeners();

		currentWidgetStatus = Status.IDLE;
	}

	private void addMoveButtons(Composite parent) {
		decreaseButton = new Button(parent, SWT.PUSH);
		decreaseButton.setText("-");

		increaseButton = new Button(parent, SWT.PUSH);
		increaseButton.setText("+");
	}

	/**
	 * Create GUI elements
	 * @throws DeviceException
	 */
	private void createControls() throws DeviceException {
		boolean useCompactLayout = (layoutOptions & COMPACT_LAYOUT) > 0;

		int numColumns = useCompactLayout ? 4 : 3;

		if ((layoutOptions & HIDE_BORDER)>0) {
			group = new Composite(parent, SWT.NONE);
		} else {
			group = new Group(parent, SWT.NONE);
		}

		group.setLayout(new GridLayout(numColumns, false));
		group.setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, false, 1, 1));

		nameLabel = new Label(group, SWT.SINGLE);
		nameLabel.setText(scannableMotor.getName());
		// Namelabel on first row on its own
		if (!useCompactLayout) {
			nameLabel.setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, false, numColumns, 1));
		}

		addMoveButtons(group);

		int ysize = 30;
		demandPositionTextbox = new Text(group, SWT.SINGLE | SWT.BORDER);
		demandPositionTextbox.setText(getFormattedScannablePos(scannableMotor));
		demandPositionTextbox.setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, false, 1, 1));
		demandPositionTextbox.setSize(demandPositionTextbox.computeSize(SWT.DEFAULT, ysize));

		GridDataFactory gridDataForButton = GridDataFactory.fillDefaults().align(SWT.FILL, SWT.TOP).grab(true, false).hint(25, ysize);
		gridDataForButton.applyTo(increaseButton);
		gridDataForButton.applyTo(decreaseButton);

		// Show stop button, current position (if not hidden)
		if ((layoutOptions & HIDE_STOP_CONTROLS)==0) {

			// Fill empty space below name label
			if (useCompactLayout) {
				new Label(group, SWT.NONE);
			}

			stopButton = new Button(group, SWT.ICON_CANCEL);
			Image stopButtonImage = GDAClientActivator.getImageDescriptor("icons/stop.png").createImage();
			stopButton.setImage(stopButtonImage);
			stopButton.setEnabled(false);
			gridDataForButton.applyTo(stopButton);

			actualPositionTextbox = new Text(group, SWT.SINGLE);
			actualPositionTextbox.setText("0");
			actualPositionTextbox.setEditable(false);
			// fill up to end of parent group
			actualPositionTextbox.setLayoutData(new GridData(SWT.FILL, SWT.TOP, true, false, 2, 1));

			// Set initial value of position textboxes using position of scannable
			actualPositionTextbox.setText(getFormattedScannablePos(scannableMotor));
			demandPositionTextbox.setText(actualPositionTextbox.getText());
		}

		// Resize the group to fit the widgets
		Point totalSize = group.computeSize(150, SWT.DEFAULT);
		group.setSize(totalSize);

		// Context menu to allow size of tweak step to be adjusted
		Menu popupMenu = new Menu(increaseButton);
	    MenuItem newItem = new MenuItem(popupMenu, SWT.PUSH);
	    newItem.setText("Change tweak step size");
	    newItem.addSelectionListener( new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				setTweakStepFromDialog();
			}
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});

		// Add tweak context menu to increase, decrease motor position buttons
		increaseButton.setMenu(popupMenu);
		decreaseButton.setMenu(popupMenu);

		setLimits();
		setToolTips();
	}

	/**
	 * Automatically set motor limits and movement units by using {@link Scannable#getAttribute(String)} .
	 */
	public void setLimits() {

		if (scannableMotor==null) {
			return;
		}
		try {
			double lowerMotorLimit = (double) scannableMotor.getAttribute("lowerMotorLimit");
			double upperMotorLimit = (double) scannableMotor.getAttribute("upperMotorLimit");

			// If limits from upper/lowerMotorLimit are very big, server is probably running in dummy mode
			// and should instead try to use gda limits.
			final double numberTooBig = 1e100;
			if (Math.abs(lowerMotorLimit) > numberTooBig || Math.abs(upperMotorLimit) > numberTooBig ) {
				// gdaLimits returns Double[] as an Object
				Double[] val = (Double[])scannableMotor.getAttribute("lowerGdaLimits");
				if (val!=null) {
					lowerMotorLimit = val[0];
				}
				val = (Double[])scannableMotor.getAttribute("upperGdaLimits");
				if (val!=null) {
					upperMotorLimit = val[0];
				}
			}
			minPos = lowerMotorLimit;
			maxPos = upperMotorLimit;

			unitString = (String) scannableMotor.getAttribute(ScannableMotionUnits.USERUNITS);

			setToolTips();

		} catch (DeviceException| NullPointerException e) {
			logger.warn("Problem setting motor limits from scannable {}. Using range 0, 100000.",scannableMotor.getName(), e);
			minPos = 0;
			maxPos = 100000;
		}
	}

	/** Setup tooltip strings for controls.
	 * Shows name of scannable, motor limits and units, and motor tweak step size.
	 */
	private void setToolTips() {
		Control[] comps = new Control[]{ demandPositionTextbox, actualPositionTextbox};
		String text = String.format("Scannable : %s\nLimits : %.4g ... %.4g %s\nMotor tweak step size : %.4g", scannableMotor.getName(), minPos, maxPos, unitString, motorStepSize);
		for( Control c : comps) {
			if (c!=null) {
				c.setToolTipText(text);
			}
		}
	}

	/**
	 * Add listeners to the GUI elements
	 */
	private void addListeners() {
		// Button to decrease motor position by 1 unit
		decreaseButton.addSelectionListener(new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				double newpos = getDemandPositionFromTextbox() - motorStepSize;
				moveToDemandPosition(newpos);
			}
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});

		// Button to increase motor position by 1 unit
		increaseButton.addSelectionListener(new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				double newpos = getDemandPositionFromTextbox() + motorStepSize;
				moveToDemandPosition(newpos);
			}
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});

		if ((layoutOptions & HIDE_STOP_CONTROLS)>0) {
			return;
		}

		// Button to nicely try and stop current motor move
		stopButton.addSelectionListener(new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				logger.debug("Stop motor button pressed. Status = {}", currentWidgetStatus);
				try {
					scannableMotor.stop();
				} catch (DeviceException e1) {
					logger.error("Problem stopping scannable {}", scannableMotor.getName(), e1);
				}
			}
			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});

		// Move motor to demand position when enter key pressed from inside demand textbox,
		// if position text length > 0
		demandPositionTextbox.addKeyListener(new KeyListener() {
			@Override
			public void keyPressed(KeyEvent e) {
				logger.debug("Key pressed : " + e.keyCode);
				if (e.keyCode == SWT.CR || e.keyCode == SWT.KEYPAD_CR && demandPositionTextbox.getText().length() > 0) {
					double newpos = getDemandPositionFromTextbox();
					moveToDemandPosition(newpos);
				}
			}
			@Override
			public void keyReleased(KeyEvent e) {
			}
		});

		// Validate new demand position input to make sure it's numeric and within valid range.
		// This is run every time content of textbox changes (i.e. 'live' when typing).
		demandPositionTextbox.addVerifyListener(new VerifyListener() {
			@Override
			public void verifyText(VerifyEvent event) {
				logger.debug("Demand position verifyListener. Status = {}", currentWidgetStatus);
				verifyDemandPositionText(event);
			}
		});

		// Add this class as observer of scannable, so that will be notified of position changes via. 'update' method.
		scannableMotor.addIObserver(this);
	}

	/**
	 * Move motor to new position, update the 'demand position' label.
	 * {@link #update(Object, Object)} takes care of updating current motor position label, stop button status.
	 * @param newPosition
	 */
	private synchronized void moveToDemandPosition(double newPosition) {
		logger.debug("New demand position {} - current status = {}", newPosition, currentWidgetStatus);

		if (currentWidgetStatus != Status.IDLE || !getPositionWithinLimits(newPosition))
			return;

		updateTextboxLabel(demandPositionTextbox, Double.toString(newPosition));

		try {
			scannableMotor.asynchronousMoveTo(newPosition);
		} catch (DeviceException e) {
			logger.warn("Problem moving motor {} to position {}", scannableMotor.getName(), newPosition, e);
		}
	}

	/**
	 * Update motor position label when the scannable position changes.
	 *
	 */
	@Override
	public void update(Object source, Object arg) {
		logger.debug("Update motor position during motor move started, Status = {}",currentWidgetStatus);

		if (currentWidgetStatus != Status.IDLE)
			return;

		currentWidgetStatus = Status.MOTOR_IS_MOVING;
		Async.execute(this::waitWhileScannableBusyAndUpdateGui);

		logger.debug("Update motor position during motor move thread started");
	}

	public void waitWhileScannableBusyAndUpdateGui() {
		updateStopMotorButton();
		try {
			// Periodically get position of scannable and update the motor position label
			do {
				Thread.sleep(motorPosLabelUpdateIntervalMs);
				updateMotorPositionTextboxFromScannable();
			} while (scannableMotor.isBusy());

			// Update demand position with final position of scannable
			updateTextboxLabel(demandPositionTextbox, getFormattedScannablePos(scannableMotor));

		} catch (DeviceException | InterruptedException e) {
			logger.warn("Problem updating motor position during external move ", e);
		}

		currentWidgetStatus = Status.IDLE;
		updateStopMotorButton();
		logger.debug("Update motor position during motor move finished");
	}

	/**
	 * Update the 'stop' button : enable it if motor move is currently taking place; otherwise disable it..
	 *
	 */
	private void updateStopMotorButton() {
		final boolean buttonEnabled = currentWidgetStatus == Status.MOTOR_IS_MOVING;

		// Checks to avoid 'widget is disposed' errors that occur if reopen same view a 2nd time. Behaviour is ok though...
		if (parent.isDisposed() || stopButton.isDisposed()) {
			return;
		}

		parent.getDisplay().asyncExec(new Runnable() {
			@Override
			public void run() {
				stopButton.setEnabled(buttonEnabled);
			}
		});
	}

	/** Update motor position label with current scannable position */
	private void updateMotorPositionTextboxFromScannable() throws DeviceException {
		String formattedPos = getFormattedScannablePos(scannableMotor);
		logger.debug("Updating motor position label from scannable : " + formattedPos);
		updateTextboxLabel(actualPositionTextbox, formattedPos);
	}

	/**
	 * Return formatted position string from the scannable, using format from {@link Scannable#getOutputFormat()}
	 * @param scannable
	 * @return
	 * @throws DeviceException
	 */
	private String getFormattedScannablePos(Scannable scannable) throws DeviceException {
		String scannablePos = scannable.getPosition().toString();
		double num =  Double.parseDouble(scannablePos);
		return String.format(scannable.getOutputFormat()[0], num );
	}

	public String getFormattedPosition() throws DeviceException {
		return getFormattedScannablePos(scannableMotor);
	}

	/** Update label in a textbox using gui thread
	 *
	 * @param textbox
	 * @param newText
	 */
	private void updateTextboxLabel(final Text textbox, final String newText) {
		if (parent.isDisposed() || textbox==null) {
			return;
		}
		parent.getDisplay().asyncExec(new Runnable() {
			@Override
			public void run() {
				textbox.setText(newText);
			}
		});
	}

	/**
	 * @param position
	 * @return True if position is within limits
	 */
	private boolean getPositionWithinLimits(double position) {
		return (position >= minPos && position <= maxPos);
	}

	/**
	 * Validate new input to in demand position textbox - make sure it's a valid number and within limits,
	 * and set 'doit' flag appropriately. Also allow zero length strings,
	 * @param verifyEvent
	 */
	private void verifyDemandPositionText(VerifyEvent verifyEvent) {
		logger.debug("Demand position verifyListener. Status = {}", currentWidgetStatus);

		final String oldString = demandPositionTextbox.getText();
		final String newString = oldString.substring(0, verifyEvent.start) + verifyEvent.text + oldString.substring(verifyEvent.end);
		verifyEvent.doit = true;

		// also allow zero length strings.
		if (newString.length()==0)
			return;

		try {
			Double value = Double.parseDouble(newString);
			if (!getPositionWithinLimits(value))
				verifyEvent.doit = false;
		} catch (NumberFormatException | NullPointerException excp) {
			verifyEvent.doit = false;
		}
	}

	/**
	 *
	 * @return Double representation of the string value in the 'demand position' textbox
	 */
	private double getDemandPositionFromTextbox() {
		double val = 0;
		try {
			val = Double.parseDouble(demandPositionTextbox.getText());
		} catch (NumberFormatException | NullPointerException excp) {
		}
		return val;
	}

	private Image getTransparentImage() {
		final Image image = new Image(parent.getDisplay(), 1, 1);
		image.getImageData().setAlpha(0,0,0);
		return image;
	}

	public void setBackGroundColour(int swtColour) {
		Color color = parent.getDisplay().getSystemColor(swtColour);
		group.setBackground(color);
	}

	/**
	 * Display dialog box to allow new value for motor tweak to be entered.
	 */
	private void setTweakStepFromDialog() {
		InputDialog dlg = new InputDialog(parent.getShell(), "Set motor 'tweak' step size",
				"Size of motor step",
				String.valueOf(motorStepSize), new FloatValidator());
		if (dlg.open() == Window.OK) {
			// User clicked OK; update the label with the input
			Double userInputInteger = Double.valueOf(dlg.getValue());
			if (userInputInteger == null) {
				logger.info("Problem converting user input {} into number", dlg.getValue());
			} else {
				motorStepSize=userInputInteger;
				setToolTips();
			}
		}
	}

	/**
	 * Validator used to check user input values of tweak step size.
	 */
	class FloatValidator implements IInputValidator {
		/** Validates a string to make sure it's floating point > 0.
		 * Returns null for no error, or string with error message
		 * @param newText
		 * @return String
		 */
		@Override
		public String isValid(String newText) {
			Double value = null;
			try{
				value = Double.valueOf(newText);
			} catch(NumberFormatException nfe) {
				// swallow, value==null
			}
			if (value==null || value<=0) {
				return "Value should be > 0";
			}
			return null;
		}
	}

	/** Set label to display at top of controls (default is name of scannable)
	 *
	 * @param label
	 */
	public void setLabel(String label) {
		nameLabel.setText(label);
	}

	/**
	 * Set motor limits
	 * @param minPos
	 * @param maxPos
	 */
	public void setLimits(double minPos, double maxPos) {
		this.minPos = minPos;
		this.maxPos = maxPos;
		setToolTips();
	}
	/** Set motor units string
	 *
	 * @param unitString
	 */
	public void setUnitString(String unitString) {
		this.unitString = unitString;
		setToolTips();
	}

	public String getUnitString() {
		return this.unitString;
	}

	public double getMotorStepSize() {
		return motorStepSize;
	}

	public void setMotorStepSize(double motorStepSize) {
		this.motorStepSize = motorStepSize;
	}

	public Control getControls() {
		return group;
	}
}
