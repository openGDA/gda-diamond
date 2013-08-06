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

package uk.ac.gda.exafs.ui.sections;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.util.ArrayList;
import java.util.Arrays;

import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeansObservables;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Text;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.swt.widgets.ToolItem;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.dialogs.ListSelectionDialog;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import uk.ac.gda.exafs.data.DetectorConfig;
import uk.ac.gda.exafs.ui.data.UIHelper;

public class DetectorConfigSection {

	private static Logger logger = LoggerFactory.getLogger(DetectorConfigSection.class);

	public static DetectorConfigSection INSTANCE = new DetectorConfigSection();

	private Text txtBiasVoltage;
	private Text txtExcludedStrips;
	private Section detectorSetupSection;
	private final DataBindingContext dataBindingCtx = new DataBindingContext();

	@SuppressWarnings({ "unused" })
	public void setupDetectorConfigSection(Section detectorSetupSection, FormToolkit toolkit) {
		this.detectorSetupSection = detectorSetupSection;
		detectorSetupSection.setText("Detector configuration");
		detectorSetupSection.setLayoutData(new GridData(GridData.FILL_HORIZONTAL));

		Composite selectionComposite = toolkit.createComposite(detectorSetupSection, SWT.NONE);
		toolkit.paintBordersFor(selectionComposite);
		selectionComposite.setLayout(new GridLayout(2, false));
		detectorSetupSection.setClient(selectionComposite);

		Label lblBiasVoltage = toolkit.createLabel(selectionComposite, UnitSetup.VOLTAGE.addUnitSuffixForLabel("Voltage"), SWT.NONE);
		lblBiasVoltage.setLayoutData(new GridData(GridData.BEGINNING, GridData.BEGINNING, false, false));

		txtBiasVoltage = toolkit.createText(selectionComposite, "", SWT.NONE);
		txtBiasVoltage.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));

		Label lblexcludedStrips = toolkit.createLabel(selectionComposite, "Excluded strips:", SWT.NONE);
		lblexcludedStrips.setLayoutData(new GridData(GridData.BEGINNING, GridData.BEGINNING, false, false));

		txtExcludedStrips = toolkit.createText(selectionComposite, "", SWT.NONE);
		txtExcludedStrips.setLayoutData(new GridData(GridData.FILL, GridData.BEGINNING, true, false));
		txtExcludedStrips.setEditable(false);

		Listener excludedStripsTxtListener = new Listener() {
			@Override
			public void handleEvent(Event event) {
				if (event.type == SWT.MouseUp | event.type == SWT.KeyUp) {
					showExcludedStripsDialog();
				}
			}
		};

		txtExcludedStrips.addListener(SWT.MouseUp, excludedStripsTxtListener);
		txtExcludedStrips.addListener(SWT.KeyUp, excludedStripsTxtListener);

		Composite defaultSectionSeparator = toolkit.createCompositeSeparator(detectorSetupSection);
		toolkit.paintBordersFor(defaultSectionSeparator);
		detectorSetupSection.setSeparatorControl(defaultSectionSeparator);

		ToolBar defaultSectionTbar = new ToolBar(detectorSetupSection, SWT.FLAT | SWT.HORIZONTAL);
		new ToolItem(defaultSectionTbar, SWT.SEPARATOR);
		ToolItem saveDefaultTBarItem = new ToolItem(defaultSectionTbar, SWT.NULL);
		saveDefaultTBarItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ETOOL_SAVE_EDIT));
		saveDefaultTBarItem.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				//updateDetectorDefaultValues();
				bindingValues();
			}
		});
		detectorSetupSection.setTextClient(defaultSectionTbar);

		bindingValues();
	}

	private final ArrayList<Integer> excludedStrips = new ArrayList<Integer>();
	private Binding bindTxtBiasVoltage = null;
	private Binding bindExcludedStrips = null;

	private void bindingValues() {
		try {
			DetectorConfig.INSTANCE.addPropertyChangeListener(DetectorConfig.DETECTOR_CONNECTED_PROP_NAME, new PropertyChangeListener() {
				@Override
				public void propertyChange(PropertyChangeEvent evt) {
					boolean isDetectorConnected = (boolean) evt.getNewValue();
					detectorSetupSection.setExpanded(isDetectorConnected);
					if (isDetectorConnected) {
						bindTxtBiasVoltage = dataBindingCtx.bindValue(
								WidgetProperties.enabled().observe(txtBiasVoltage),
								BeansObservables.observeValue(DetectorConfig.INSTANCE, DetectorConfig.BIAS_PROP_NAME), new UpdateValueStrategy(UpdateValueStrategy.POLICY_ON_REQUEST), null);
						bindExcludedStrips = dataBindingCtx.bindValue(
								WidgetProperties.enabled().observe(txtExcludedStrips),
								BeansObservables.observeValue(DetectorConfig.INSTANCE, DetectorConfig.CURRENT_DETECTOR_EXCLUDED_STRIPS_PROP_NAME),
								new UpdateValueStrategy(UpdateValueStrategy.POLICY_ON_REQUEST),
								new UpdateValueStrategy() {
									@Override
									public Object convert(Object value) {
										Integer[] values = (Integer[]) value;
										return DataHelper.toString(values);
									}
								});
					} else {
						if (bindTxtBiasVoltage != null) {
							dataBindingCtx.removeBinding(bindTxtBiasVoltage);
							bindTxtBiasVoltage = null;
						}
						if (bindExcludedStrips != null) {
							dataBindingCtx.removeBinding(bindExcludedStrips);
							bindExcludedStrips = null;
						}
						txtBiasVoltage.setText("Unavailable");
						txtExcludedStrips.setText("Unavailable");
					}

				}
			});

			dataBindingCtx.bindValue(
					WidgetProperties.enabled().observe(detectorSetupSection),
					BeansObservables.observeValue(DetectorConfig.INSTANCE, DetectorConfig.DETECTOR_CONNECTED_PROP_NAME));

		} catch (Exception e) {
			String errorMessage = "Unable to update Detector configuration. ";
			logger.error(errorMessage, e);
			UIHelper.showError(errorMessage, e.getMessage());
		}
	}

	private void updateExcludedStripsText() {
		txtExcludedStrips.setText(DataHelper.toString(DetectorConfig.INSTANCE.getExcludedStrips()));
	}

	private void showExcludedStripsDialog() {
		ListSelectionDialog dialog =
				new ListSelectionDialog(
						Display.getDefault().getActiveShell(),
						DetectorConfig.INSTANCE.getStrips(),
						new ArrayContentProvider(),
						new LabelProvider(),
						"Select excluded strips");
		dialog.setInitialElementSelections(Arrays.asList(DetectorConfig.INSTANCE.getExcludedStrips()));
		if (dialog.open() == Window.OK) {
			Object[] selection = dialog.getResult();
			excludedStrips.clear();
			if (selection.length > 0) {
				for (Object selected : selection) {
					Integer stringNo = (Integer) selected;
					excludedStrips.add(stringNo);
				}
			}
			updateExcludedStripsText();
		}
	}

	//	private void updateDetectorDefaultValues() {
	//		try {
	//			if (txtBiasVoltage.getText().isEmpty()) {
	//				throw new Exception("Empty voltage value");
	//			}
	//			double voltage = Double.valueOf(txtBiasVoltage.getText());
	//			if (!DetectorConfig.INSTANCE.getCurrentDetectorSetup().isVoltageInRange(voltage)) {
	//				throw new Exception("Voltage out of range");
	//			}
	//			DetectorConfig.INSTANCE.getCurrentDetectorSetup().getDetectorScannable().setBias(voltage);
	//			DetectorConfig.INSTANCE.getCurrentDetectorSetup().getDetectorScannable().setExcludedStrips(ArrayUtils.toPrimitive(excludedStrips.toArray(new Integer[excludedStrips.size()])));
	//		} catch (Exception e) {
	//			String errorMessage = "Unable to save Detector parameter ";
	//			logger.error(errorMessage, e);
	//			UIHelper.showError(errorMessage, e.getMessage());
	//		}
	//	}
}
