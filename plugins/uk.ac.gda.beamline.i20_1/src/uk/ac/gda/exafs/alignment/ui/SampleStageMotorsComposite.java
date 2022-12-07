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

package uk.ac.gda.exafs.alignment.ui;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.ui.dialogs.ListSelectionDialog;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.observablemodels.ScannableWrapper;
import uk.ac.gda.ede.data.ClientConfig;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentMotorPostion;
import uk.ac.gda.exafs.experiment.ui.data.SampleStageMotors;
import uk.ac.gda.ui.components.NumberEditorControl;

public class SampleStageMotorsComposite extends Composite {

	private static final Logger logger = LoggerFactory.getLogger(SampleStageMotorsComposite.class);

	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	private final Button selectSampleStageMotors;
	private final Composite sampleI0PositionComposite;
	private final Composite sampleItPositionComposite;
	private final PropertyChangeListener selectionChangeListener;

	private final FormToolkit toolkit;

	private final Button useIrefCheckButton;

	private final Composite sampleIRefPositionComposite;

	public SampleStageMotorsComposite(Composite parent, int style, FormToolkit toolkit) {
		this(parent, style, toolkit, false);
	}

	public SampleStageMotorsComposite(Composite parent, int style, FormToolkit toolkit, boolean doubleSpan) {
		super(parent, style);
		this.toolkit = toolkit;
		final int span = (doubleSpan) ? 3 : 1;
		this.setLayout(UIHelper.createGridLayoutWithNoMargin(span, false));
		this.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));

		Composite topControlComposite = toolkit.createComposite(this);
		topControlComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		GridData gridData = new GridData(SWT.FILL, SWT.FILL, true, false);
		gridData.horizontalSpan = span;
		topControlComposite.setLayoutData(gridData);

		useIrefCheckButton = toolkit.createButton(topControlComposite, "Use Iref", SWT.CHECK);
		useIrefCheckButton.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, true, false));

		dataBindingCtx.bindValue(
				WidgetProperties.selection().observe(useIrefCheckButton),
				BeanProperties.value(SampleStageMotors.USE_IREF_PROP_NAME).observe(SampleStageMotors.INSTANCE));

		selectSampleStageMotors = toolkit.createButton(topControlComposite, "Select sample stage motors", SWT.None);
		selectSampleStageMotors.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		selectSampleStageMotors.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				showAvailableMotorsDialog();
			}
		});

		final Section i0section = toolkit.createSection(this, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		i0section.setText("I0 sample position");
		i0section.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		sampleI0PositionComposite = toolkit.createComposite(i0section, SWT.NONE);
		sampleI0PositionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		toolkit.paintBordersFor(sampleI0PositionComposite);
		i0section.setClient(sampleI0PositionComposite);

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(i0section);
		toolkit.paintBordersFor(defaultSectionSeparator);
		i0section.setSeparatorControl(defaultSectionSeparator);

		final Section itSection = toolkit.createSection(this, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		itSection.setText("It sample position");
		itSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		sampleItPositionComposite = toolkit.createComposite(itSection, SWT.NONE);
		sampleItPositionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		toolkit.paintBordersFor(sampleItPositionComposite);
		itSection.setClient(sampleItPositionComposite);

		final Section iRefSection = toolkit.createSection(this, ExpandableComposite.TITLE_BAR | ExpandableComposite.TWISTIE | ExpandableComposite.EXPANDED);
		iRefSection.setText("IRef sample position");
		iRefSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		sampleIRefPositionComposite = toolkit.createComposite(iRefSection, SWT.NONE);
		sampleIRefPositionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(1, false));
		toolkit.paintBordersFor(sampleIRefPositionComposite);
		iRefSection.setClient(sampleIRefPositionComposite);

		dataBindingCtx.bindValue(
				WidgetProperties.visible().observe(iRefSection),
				BeanProperties.value(SampleStageMotors.USE_IREF_PROP_NAME).observe(SampleStageMotors.INSTANCE),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy() {
					@Override
					protected IStatus doSet(IObservableValue observableValue, Object value) {
						IStatus status = super.doSet(observableValue, (boolean) value);
						((GridData) iRefSection.getLayoutData()).exclude = !((boolean) value);
						UIHelper.revalidateLayout(iRefSection);
						return status;
					}
				});

		defaultSectionSeparator = toolkit.createCompositeSeparator(itSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		itSection.setSeparatorControl(defaultSectionSeparator);

		selectionChangeListener = new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
				selectionSampleStageMotorListChange();
			}
		};
		selectionSampleStageMotorListChange();
		SampleStageMotors.INSTANCE.addPropertyChangeListener(SampleStageMotors.SELECTED_MOTORS_PROP_NAME, selectionChangeListener);
		this.addDisposeListener(new DisposeListener() {
			@Override
			public void widgetDisposed(DisposeEvent e) {
				disposeResources();
			}
		});
	}

	private void disposeResources() {
		SampleStageMotors.INSTANCE.removePropertyChangeListener(SampleStageMotors.SELECTED_MOTORS_PROP_NAME, selectionChangeListener);
		dataBindingCtx.dispose();
	}

	private void showAvailableMotorsDialog() {
		ListSelectionDialog dialog =
				new ListSelectionDialog(
						Display.getDefault().getActiveShell(),
						SampleStageMotors.scannables,
						new ArrayContentProvider(),
						new LabelProvider() {
							@Override
							public String getText(Object element) {
								return ((ExperimentMotorPostion) element).getScannableSetup().getLabel();
							}
						},
						"Select motors to include in the scanning");
		dialog.setInitialSelections(SampleStageMotors.INSTANCE.getSelectedMotors());
		if (dialog.open() == Window.OK) {
			SampleStageMotors.INSTANCE.setSelectedMotors(Arrays.asList(dialog.getResult()).toArray(new ExperimentMotorPostion[dialog.getResult().length]));
		}
	}

	private final List<Composite> sampleStageMotorComposites = new ArrayList<Composite>();

	private void selectionSampleStageMotorListChange() {
		for (Composite composite : sampleStageMotorComposites) {
			composite.dispose();
		}
		sampleStageMotorComposites.clear();
		try {
			for(final ExperimentMotorPostion experimentMotorPostion : SampleStageMotors.INSTANCE.getSelectedMotors()) {
				Composite composite = createMotorPositionComposite(sampleI0PositionComposite, experimentMotorPostion,
						ExperimentMotorPostion.TARGET_I0_POSITION,
						experimentMotorPostion.getScannableSetup().getLabel(), new Listener() {
					@Override
					public void handleEvent(Event event) {
						try {
							experimentMotorPostion.setTargetI0Position((double) experimentMotorPostion.getScannableSetup().getScannable().getPosition());
						} catch (Exception e) {
							UIHelper.showError("Unable to update current motor postion", e.getMessage());
							logger.error("Unable to update current motor postion", e.getMessage());
						}
					}
				});
				sampleStageMotorComposites.add(composite);
				composite = createMotorPositionComposite(sampleItPositionComposite, experimentMotorPostion,
						ExperimentMotorPostion.TARGET_IT_POSITION,
						experimentMotorPostion.getScannableSetup().getLabel(), new Listener() {
					@Override
					public void handleEvent(Event event) {
						try {
							experimentMotorPostion.setTargetItPosition((double) experimentMotorPostion.getScannableSetup().getScannable().getPosition());
						} catch (Exception e) {
							UIHelper.showError("Unable to update current motor postion", e.getMessage());
							logger.error("Unable to update current motor postion", e.getMessage());
						}
					}
				});
				sampleStageMotorComposites.add(composite);
				sampleStageMotorComposites.add(composite);
				composite = createMotorPositionComposite(sampleIRefPositionComposite, experimentMotorPostion,
						ExperimentMotorPostion.TARGET_IREF_POSITION,
						experimentMotorPostion.getScannableSetup().getLabel(), new Listener() {
					@Override
					public void handleEvent(Event event) {
						try {
							experimentMotorPostion.setTargetItPosition((double) experimentMotorPostion.getScannableSetup().getScannable().getPosition());
						} catch (Exception e) {
							UIHelper.showError("Unable to update current motor postion", e.getMessage());
							logger.error("Unable to update current motor postion", e.getMessage());
						}
					}
				});
				sampleStageMotorComposites.add(composite);
			}
			UIHelper.revalidateLayout(this);
		} catch (Exception e) {
			UIHelper.showError("Unable to update selected motor positions", e.getMessage());
			logger.error("Unable to update selected motor positions", e);
		}
	}

	private Composite createMotorPositionComposite(Composite parent, ExperimentMotorPostion experimentMotorPostion, String propertyName, String label, Listener listener) throws Exception {
		Composite positionAllComposite = toolkit.createComposite(parent, SWT.NONE);
		toolkit.paintBordersFor(positionAllComposite);
		positionAllComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		int columns = (listener != null) ? 2 : 1;
		positionAllComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(columns, false));

		Composite positionComposite = toolkit.createComposite(positionAllComposite, SWT.NONE);
		toolkit.paintBordersFor(positionComposite);
		positionComposite.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		positionComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));

		Label xPosLabel = toolkit.createLabel(positionComposite, label, SWT.None);
		GridData gridData = new GridData(SWT.BEGINNING, SWT.CENTER, false, false);
		gridData.widthHint = 120;
		xPosLabel.setLayoutData(gridData);

		final NumberEditorControl positionControl = new NumberEditorControl(positionComposite, SWT.None, experimentMotorPostion, propertyName, false);
		positionControl.setDigits(ClientConfig.DEFAULT_DECIMAL_PLACE);
		positionControl.setUnit(ClientConfig.UnitSetup.MILLI_METER.getText());
		positionControl.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
		ScannableWrapper scannableWrapper = experimentMotorPostion.getScannableSetup().getScannableWrapper();
		if (scannableWrapper.getLowerLimit() != null && scannableWrapper.getUpperLimit() != null) {
			positionControl.setRange(scannableWrapper.getLowerLimit(), scannableWrapper.getUpperLimit());
			positionControl.setToolTipText("Lower :" + scannableWrapper.getLowerLimit() + " Upper: " + scannableWrapper.getUpperLimit());
		}

		if (listener != null) {
			Button readCurrentPositionButton = toolkit.createButton(positionAllComposite, "Read", SWT.PUSH);
			readCurrentPositionButton.setToolTipText("Read current position for " + label);
			readCurrentPositionButton.addListener(SWT.Selection, listener);
			readCurrentPositionButton.setLayoutData(new GridData(SWT.END, SWT.CENTER, false, false));
		}
		return positionAllComposite;
	}
}
