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

package uk.ac.gda.exafs.ui.composites;
import java.lang.reflect.InvocationTargetException;

import org.apache.commons.beanutils.PropertyUtils;
import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.databinding.observable.value.IValueChangeListener;
import org.eclipse.core.databinding.observable.value.ValueChangeEvent;
import org.eclipse.core.databinding.validation.IValidator;
import org.eclipse.core.databinding.validation.ValidationStatus;
import org.eclipse.core.runtime.FileLocator;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Path;
import org.eclipse.jface.databinding.fieldassist.ControlDecorationSupport;
import org.eclipse.jface.databinding.swt.ISWTObservableValue;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StackLayout;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.FocusEvent;
import org.eclipse.swt.events.FocusListener;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.events.MouseListener;
import org.eclipse.swt.events.MouseTrackListener;
import org.eclipse.swt.events.TraverseEvent;
import org.eclipse.swt.events.TraverseListener;
import org.eclipse.swt.events.VerifyEvent;
import org.eclipse.swt.events.VerifyListener;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.Cursor;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Text;

import uk.ac.gda.beamline.i20_1.Activator;
import uk.ac.gda.exafs.data.ObservableModel;

public class NumberEditorControl extends Composite {

	private static final int DEFAULT_DECIMAL_PLACES = 2;
	protected final Object object;
	private final String propertyName;

	private Label viewerText;
	private Label incrementLabel;
	private Label decrementLabel;
	private final StackLayout layout;
	private Image upArrowIcon;
	private Image downArrowIcon;
	private Composite editorComposite;
	private Text stepText;
	private MotorPositionEditorText motorPositionEditorText;

	private Binding numberValueBinding;
	private Binding incrementValueBinding;

	private boolean commitOnOutOfFocus = true;

	protected final MotorPositionWidgetModel controlModel;

	protected final DataBindingContext ctx = new DataBindingContext();
	private final boolean useSpinner;

	public NumberEditorControl(final Composite parent, int style, Object object, String propertyName, boolean userSpinner) throws Exception {
		super(parent, style);
		this.object = object;
		this.propertyName = propertyName;
		controlModel = new MotorPositionWidgetModel();
		useSpinner = userSpinner;
		try {
			Class<?> objectType = PropertyUtils.getPropertyType(object, propertyName);
			if (objectType.equals(double.class)) {
				controlModel.setBindingPropertyType(objectType);
				controlModel.setDigits(DEFAULT_DECIMAL_PLACES);
				controlModel.setIncrement(1 * (int) Math.pow(10, controlModel.getDigits()));
			} else if  (objectType.equals(int.class)) {
				controlModel.setBindingPropertyType(objectType);
				controlModel.setIncrement(1);
			} else {
				throw new Exception("Unsupported property type");
			}
		} catch (Exception e) {
			throw new Exception("Unable to process the perperty", e);
		}
		layout = new StackLayout();
		this.setLayout(layout);
		setupControls();
		bind();
	}

	private String roundDoubletoString(double value, int digits) {
		return String.format("%." + digits + "f", value);
	}

	protected String getFormattedText(Object value) {
		String formattedValue = null;
		if (controlModel.getBindingPropertyType().equals(double.class)) {
			formattedValue = roundDoubletoString((double) value, controlModel.getDigits());
		} else if (controlModel.getBindingPropertyType().equals(int.class)) {
			formattedValue = Integer.toString((int) value);
		}
		if (controlModel.getUnit() != null) {
			return formattedValue + " " + controlModel.getUnit();
		}
		return formattedValue;
	}

	private void bind() {
		IObservableValue objectValue = BeanProperties.value(propertyName).observe(object);
		ISWTObservableValue textValue = WidgetProperties.text().observe(viewerText);
		numberValueBinding = ctx.bindValue(textValue, objectValue, null, new UpdateValueStrategy() {
			@Override
			public Object convert(Object value) {
				return getFormattedText(value);
			}
		});
		if (useSpinner) {
			incrementValueBinding = ctx.bindValue(
					WidgetProperties.text(SWT.Modify).observe(stepText),
					BeanProperties.value(MotorPositionWidgetModel.INCREMENT_PROP_NAME).observe(controlModel),
					new UpdateValueStrategy() {
						@Override
						public Object convert(Object value) {
							if (controlModel.getBindingPropertyType().equals(double.class)) {
								return ((double) value * (int) Math.pow(10, controlModel.getDigits()));
							}
							return super.convert(value);
						}
					}, new UpdateValueStrategy() {
						@Override
						public Object convert(Object value) {
							if (controlModel.getBindingPropertyType().equals(double.class)) {
								double incrementValue = controlModel.getIncrement() / Math.pow(10, controlModel.getDigits());
								return roundDoubletoString(incrementValue, controlModel.getDigits());
							}
							return super.convert(value);
						}
					});
			ctx.bindValue(
					WidgetProperties.enabled().observe(stepText),
					BeanProperties.value(MotorPositionWidgetModel.EDITABLE_PROP_NAME).observe(controlModel));
		}
	}

	@Override
	public void dispose() {
		if (downArrowIcon != null && !downArrowIcon.isDisposed()) {
			downArrowIcon.dispose();
		}
		if (upArrowIcon != null && !upArrowIcon.isDisposed()) {
			upArrowIcon.dispose();
		}
		super.dispose();
	}

	public void setRange(int minValue, int maxValue) {
		controlModel.setMaxValue(maxValue);
		controlModel.setMinValue(minValue);
	}

	public void setDigits(int value) {
		controlModel.setDigits(value);
		numberValueBinding.updateModelToTarget();
		if (useSpinner) {
			incrementValueBinding.updateModelToTarget();
		}
	}

	public void setIncrement(int value) {
		controlModel.setIncrement(value);
	}


	public void setUnit(String value) {
		controlModel.setUnit(value);
		numberValueBinding.updateModelToTarget();
	}

	@Override
	public void setToolTipText(String toolTopText) {
		viewerText.setToolTipText(toolTopText);
	}

	public boolean isEditable() {
		return controlModel.isEditable();
	}

	public void setEditable(boolean value) {
		controlModel.setEditable(value);
	}

	public boolean isCommitOnOutOfFocus() {
		return commitOnOutOfFocus;
	}

	public void setCommitOnOutOfFocus(boolean commitOnOutOfFocus) {
		this.commitOnOutOfFocus = commitOnOutOfFocus;
	}

	private void setupControls() {
		editorComposite = new Composite(this, SWT.None);
		editorComposite.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));
		int columns = (useSpinner) ? 3 : 1;
		GridLayout grid = new GridLayout(columns, false);
		removeMargins(grid);
		editorComposite.setLayout(grid);
		viewerText = createTextControl(editorComposite);
		GridData gridData = new GridData(GridData.FILL,GridData.BEGINNING, true, false);
		gridData.heightHint = 23;
		viewerText.setLayoutData(gridData);
		viewerText.addMouseTrackListener(new MouseTrackListener() {
			private Cursor cursor;
			@Override
			public void mouseHover(MouseEvent e) {}

			@Override
			public void mouseExit(MouseEvent e) {
				((Control) e.getSource()).setCursor(cursor);
			}

			@Override
			public void mouseEnter(MouseEvent e) {
				cursor = ((Control) e.getSource()).getCursor();
				((Control) e.getSource()).setCursor(Display.getDefault().getSystemCursor(SWT.CURSOR_HAND));
			}
		});
		if (useSpinner) {
			Composite spinners = new Composite(editorComposite, SWT.None);
			grid = new GridLayout(1, false);
			removeMargins(grid);
			spinners.setLayout(grid);
			gridData = new GridData(GridData.END, GridData.BEGINNING, false, false);
			gridData.heightHint = 27;
			gridData.widthHint = 25;
			spinners.setLayoutData(gridData);
			incrementLabel = new Label(spinners, SWT.BORDER);
			upArrowIcon = getImageDescriptor("up_arrow.png").createImage();
			incrementLabel.setImage(upArrowIcon);
			incrementLabel.setLayoutData(new GridData(GridData.FILL_BOTH));
			incrementLabel.addMouseListener(new StepMouseListener(true));
			decrementLabel = new Label(spinners, SWT.BORDER);
			decrementLabel.setLayoutData(new GridData(GridData.FILL_BOTH));
			downArrowIcon = getImageDescriptor("down_arrow.png").createImage();
			decrementLabel.setImage(downArrowIcon);
			decrementLabel.addMouseListener(new StepMouseListener(false));
			stepText = new Text(editorComposite, SWT.BORDER);
			gridData = new GridData(SWT.END, SWT.BEGINNING, false, false);
			gridData.widthHint = 25;
			stepText.setLayoutData(gridData);
			stepText.addVerifyListener(new VerifyListener() {
				@Override
				public void verifyText(final VerifyEvent event) {
					switch (event.keyCode) {
					case SWT.BS:           // Backspace
					case SWT.DEL:          // Delete
					case SWT.HOME:         // Home
					case SWT.END:          // End
					case SWT.ARROW_LEFT:   // Left arrow
					case SWT.ARROW_RIGHT:  // Right arrow
						return;
					}
					if (Character.UNASSIGNED == event.character) {
						event.doit = true;
						return;
					}
					if (controlModel.getBindingPropertyType().equals(double.class)) {
						if (Character.isDigit(event.character)) {
							event.doit = true;
						} else if (event.character == '.') {
							event.doit = (stepText.getText().indexOf('.') == -1);
						} else {
							event.doit = false;
						}
					}
				}
			});
		}
		layout.topControl = editorComposite;
	}

	private ImageDescriptor getImageDescriptor(String imageFileName) {
		return ImageDescriptor.createFromURL(
				FileLocator.find(Activator.getDefault().getBundle(),
						new Path("icons/" + imageFileName),null));
	}

	@Override
	public boolean setFocus() {
		return viewerText.setFocus();
	}

	private class StepMouseListener implements MouseListener {
		private Color color;
		private final boolean isIncrement;
		public StepMouseListener(boolean isIncrement) {
			this.isIncrement = isIncrement;
		}
		@Override
		public void mouseUp(MouseEvent e) {
			if (controlModel.isEditable()) {
				((Control) e.getSource()).setBackground(color);
				try {

					if (controlModel.getBindingPropertyType().equals(double.class)) {
						double value = (double) PropertyUtils.getProperty(object, propertyName);
						double increment =  Double.parseDouble(stepText.getText());
						if (isIncrement) {
							if (!controlModel.isRangeSet()) {
								PropertyUtils.setProperty(object, propertyName, value + increment);
							} else  {
								double incremented = value + increment;
								if (incremented <= controlModel.getMaxValue()) {
									PropertyUtils.setProperty(object, propertyName, incremented);
								}
							}
						} else {
							if (!controlModel.isRangeSet()) {
								PropertyUtils.setProperty(object, propertyName, value - increment);
							} else  {
								double decremented = value - increment;
								if (decremented >= controlModel.getMinValue()) {
									PropertyUtils.setProperty(object, propertyName, decremented);
								}
							}
						}
					} else if (controlModel.getBindingPropertyType().equals(int.class)) {
						int value = (int) PropertyUtils.getProperty(object, propertyName);
						int increment =  Integer.parseInt(stepText.getText());
						if (isIncrement) {
							if (!controlModel.isRangeSet()) {
								PropertyUtils.setProperty(object, propertyName, value + increment);
							} else  {
								double incremented = value + increment;
								if (incremented <= controlModel.getMaxValue()) {
									PropertyUtils.setProperty(object, propertyName, (int) incremented);
								}
							}
						} else {
							if (!controlModel.isRangeSet()) {
								PropertyUtils.setProperty(object, propertyName, value - increment);
							} else  {
								double decremented = value - increment;
								if (decremented >= controlModel.getMinValue()) {
									PropertyUtils.setProperty(object, propertyName, (int) decremented);
								}
							}
						}
					}
				} catch (IllegalAccessException | InvocationTargetException
						| NoSuchMethodException e1) {
					// TODO Handle this
					e1.printStackTrace();
				}
			}
		}
		@Override
		public void mouseDown(MouseEvent e) {
			if (controlModel.isEditable()) {
				color = ((Control) e.getSource()).getBackground();
				((Control) e.getSource()).setBackground(Display.getDefault().getSystemColor(SWT.COLOR_DARK_GRAY));
			}
		}
		@Override
		public void mouseDoubleClick(MouseEvent e) {}
	}

	private Label createTextControl(Composite parent) {
		Label numberTextLabel = new Label(parent, SWT.BORDER);
		numberTextLabel.setBackground(Display.getDefault().getSystemColor(SWT.COLOR_WHITE));
		Listener openEditorListener = new Listener() {
			@Override
			public void handleEvent(Event event) {
				if (controlModel.isEditable()) {
					motorPositionEditorText = new MotorPositionEditorText(NumberEditorControl.this, SWT.None);
					GridData gridData = new GridData(SWT.FILL,SWT.BEGINNING, true, false);
					motorPositionEditorText.setLayoutData(gridData);
					layout.topControl = motorPositionEditorText;
					NumberEditorControl.this.layout();
					NumberEditorControl.this.getParent().layout();
					motorPositionEditorText.addDisposeListener(new DisposeListener() {
						@Override
						public void widgetDisposed(DisposeEvent e) {
							motorPositionEditorText = null;
							layout.topControl = editorComposite;
							NumberEditorControl.this.layout(true, true);
						}
					});
				}
			}
		};
		numberTextLabel.addListener(SWT.MouseUp, openEditorListener);
		return numberTextLabel;
	}

	private static void removeMargins(GridLayout grid) {
		grid.marginBottom = 0;
		grid.marginTop = 0;
		grid.marginHeight = 0;
		grid.marginLeft = 0;
		grid.marginRight = 0;
		grid.verticalSpacing = 0;
		grid.horizontalSpacing = 0;
	}

	protected class MotorPositionWidgetModel extends ObservableModel {
		public static final String EDITABLE_PROP_NAME = "editable";
		private boolean editable = true;

		public static final String MAX_VALUE_PROP_NAME = "maxValue";
		private int maxValue;

		public static final String MIN_VALUE_PROP_NAME = "minValue";
		private int minValue;

		public static final String RANGE_SET_PROP_NAME = "rangeSet";
		private boolean rangeSet;

		public static final String DIGITS_PROP_NAME = "digits";
		private int digits;

		public static final String INCREMENT_PROP_NAME = "increment";
		private int increment;

		public static final String UNIT_PROP_NAME = "unit";
		private String unit;

		private Object bindingPropertyType;

		public boolean isEditable() {
			return editable;
		}
		public void setEditable(boolean value) {
			firePropertyChange(EDITABLE_PROP_NAME, editable, editable = value);
		}
		public int getMaxValue() {
			return maxValue;
		}
		public void setMaxValue(int value) {
			firePropertyChange(MAX_VALUE_PROP_NAME, maxValue, maxValue = value);
			firePropertyChange(RANGE_SET_PROP_NAME, rangeSet, rangeSet = true);
		}
		public int getMinValue() {
			return minValue;
		}
		public void setMinValue(int value) {
			firePropertyChange(MIN_VALUE_PROP_NAME, minValue, minValue = value);
			firePropertyChange(RANGE_SET_PROP_NAME, rangeSet, rangeSet = true);
		}
		public boolean isRangeSet() {
			return rangeSet;
		}
		public int getDigits() {
			return digits;
		}
		public void setDigits(int value) {
			firePropertyChange(DIGITS_PROP_NAME, digits, digits = value);
		}
		public int getIncrement() {
			return increment;
		}
		public void setIncrement(int value) {
			firePropertyChange(INCREMENT_PROP_NAME, increment, increment = value);
		}
		public String getUnit() {
			return unit;
		}
		public void setUnit(String value) {
			firePropertyChange(UNIT_PROP_NAME, unit, unit = value);
		}
		public Object getBindingPropertyType() {
			return bindingPropertyType;
		}
		public void setBindingPropertyType(Object bindingPropertyType) {
			this.bindingPropertyType = bindingPropertyType;
		}
	}

	private class MotorPositionEditorText extends Composite {
		private final Text editorText;
		private final Button editorAcceptButton;
		private final Button editorCancelButton;
		private final DataBindingContext editorCtx = new DataBindingContext();
		private Binding binding;
		private final Image cancelImage;
		private final Image acceptImage;
		protected boolean lostFocus;
		protected boolean cancelOrCommit;
		private final Listener inFocus;
		private final FocusListener textOutFocus;
		public MotorPositionEditorText(Composite parent, int style) {
			super(parent, style);
			GridLayout grid = new GridLayout(3, false);
			removeMargins(grid);
			this.setLayout(grid);
			editorText = new Text(this, SWT.BORDER);
			GridData gridData = new GridData(SWT.FILL, SWT.BEGINNING, true, false);
			editorText.setLayoutData(gridData);
			editorCancelButton = new Button(this, SWT.NONE);
			ImageDescriptor myImage = ImageDescriptor.createFromURL(
					FileLocator.find(Activator.getDefault().getBundle(),
							new Path("icons/cancel.png"),null));
			cancelImage = myImage.createImage();
			editorCancelButton.setImage(myImage.createImage());
			gridData = new GridData(SWT.END, SWT.BEGINNING, false, false);
			editorCancelButton.setLayoutData(gridData);
			editorAcceptButton = new Button(this, SWT.NONE);
			editorAcceptButton.setLayoutData(gridData);
			myImage = ImageDescriptor.createFromURL(
					FileLocator.find(Activator.getDefault().getBundle(),
							new Path("icons/accept.png"),null));
			acceptImage = myImage.createImage();
			editorAcceptButton.setImage(acceptImage);
			editorCancelButton.addListener(SWT.Selection, new Listener() {
				@Override
				public void handleEvent(Event event) {
					cancelOrCommit = true;
					updateChangesAndDispose(false);
				}
			});

			editorAcceptButton.addListener(SWT.Selection, new Listener() {
				@Override
				public void handleEvent(Event event) {
					cancelOrCommit = true;
					updateChangesAndDispose(true);
				}
			});

			bind();
			editorText.selectAll();
			editorText.setFocus();
			inFocus = new Listener() {
				@Override
				public void handleEvent(Event event) {
					if (lostFocus & event.widget != editorText & event.widget != editorCancelButton & event.widget != editorAcceptButton & !cancelOrCommit) {
						MotorPositionEditorText.this.updateChangesAndDispose(commitOnOutOfFocus);
					}
				}
			};
			textOutFocus = new FocusListener() {
				@Override
				public void focusLost(FocusEvent e) {
					lostFocus = true;
				}

				@Override
				public void focusGained(FocusEvent e) {
					// Do nothing
				}
			};
			getDisplay().addFilter(SWT.FocusIn, inFocus);
			editorText.addFocusListener(textOutFocus);
		}

		private void bind() {
			IObservableValue objectValue = BeanProperties.value(propertyName).observe(object);
			ISWTObservableValue textValue = WidgetProperties.text().observe(editorText);
			UpdateValueStrategy updateStrategy = new UpdateValueStrategy(UpdateValueStrategy.POLICY_ON_REQUEST);
			binding = editorCtx.bindValue(textValue, objectValue, updateStrategy, new UpdateValueStrategy() {
				@Override
				public Object convert(Object value) {
					if (controlModel.getBindingPropertyType().equals(double.class)) {
						return roundDoubletoString((double) value, controlModel.getDigits());
					}
					return super.convert(value);
				}
			});
			if (controlModel.isRangeSet()) {
				updateStrategy.setBeforeSetValidator(new IValidator() {
					@Override
					public IStatus validate(Object value) {
						// TODO Max and min are int, review
						if (controlModel.getBindingPropertyType().equals(double.class)) {
							if (((double) value) >= controlModel.getMinValue() & ((double) value) <= controlModel.getMaxValue()) {
								return ValidationStatus.ok();
							}
							return ValidationStatus.error("Out of range");
						} else if (controlModel.getBindingPropertyType().equals(int.class)) {
							if (((int) value) >= controlModel.getMinValue() & ((int) value) <= controlModel.getMaxValue()) {
								return ValidationStatus.ok();
							}
							return ValidationStatus.error("Out of range");
						}
						return ValidationStatus.error("Unknown type");
					}
				});
			}
			editorText.addModifyListener(new ModifyListener() {
				@Override
				public void modifyText(ModifyEvent e) {
					binding.validateTargetToModel();
				}
			});
			editorText.addTraverseListener(new TraverseListener() {
				@Override
				public void keyTraversed(TraverseEvent event) {
					if (event.detail == SWT.TRAVERSE_RETURN) {
						updateChangesAndDispose(true);
					}
					if (event.detail == SWT.TRAVERSE_ESCAPE) {
						updateChangesAndDispose(false);
					}
				}
			});
			ControlDecorationSupport.create(binding, SWT.TOP | SWT.LEFT);
			binding.getValidationStatus().addValueChangeListener(new IValueChangeListener() {
				@Override
				public void handleValueChange(ValueChangeEvent event) {
					IStatus status = (IStatus) binding.getValidationStatus().getValue();
					editorAcceptButton.setEnabled(status.isOK());
				}
			});
		}

		@Override
		public void dispose() {
			getDisplay().removeFilter(SWT.FocusIn, inFocus);
			editorText.removeFocusListener(textOutFocus);
			editorCtx.dispose();
			acceptImage.dispose();
			cancelImage.dispose();
			super.dispose();
		}

		private void updateChangesAndDispose(boolean commit) {
			if (commit) {
				binding.updateTargetToModel();
			} else {
				binding.updateModelToTarget();
			}
			MotorPositionEditorText.this.dispose();
		}
	}
}