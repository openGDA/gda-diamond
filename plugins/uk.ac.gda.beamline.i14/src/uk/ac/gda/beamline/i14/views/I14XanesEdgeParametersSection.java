/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i14.views;

import static java.util.stream.Collectors.toList;
import static uk.ac.gda.beamline.i14.views.I14XanesEdgeParameters.TrackingMethod.EDGE;
import static uk.ac.gda.beamline.i14.views.I14XanesEdgeParameters.TrackingMethod.REFERENCE;

import java.util.List;
import java.util.Map;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.beans.PojoProperties;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.databinding.observable.value.SelectObservableValue;
import org.eclipse.dawnsci.analysis.api.persistence.IMarshallerService;
import org.eclipse.jface.databinding.swt.ISWTObservableValue;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.scanning.api.points.models.IScanPathModel;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.swtdesigner.SWTResourceManager;

import gda.observable.IObserver;
import uk.ac.diamond.daq.mapping.api.IScanModelWrapper;
import uk.ac.diamond.daq.mapping.ui.experiment.AbstractMappingSection;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanPathEditor;
import uk.ac.gda.beamline.i14.views.I14XanesEdgeParameters.TrackingMethod;

/**
 * View to allow the user to input the additional parameters required for the XANES scanning script.
 * <p>
 * These will be combined with the standard parameters from the Mapping view (x & y coordinates, detector etc.) and
 * passed to the appropriate script.
 */
public class I14XanesEdgeParametersSection extends AbstractMappingSection {
	private static final Logger logger = LoggerFactory.getLogger(I14XanesEdgeParametersSection.class);

	private static final String I14_XANES_SCAN_KEY = "I14XanesScan.json";
	private static final String ENERGY_SCANNABLE = "dcm_enrg";
	private static final int NUM_COLUMNS = 3;

	private ScanPathEditor energyEditor;
	private final IObserver scanPathObserver = this::handleScanPathUpdate;

	private I14XanesEdgeParameters scanParameters;

	@SuppressWarnings("unchecked")
	@Override
	public void createControls(Composite parent) {
		parent.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));

		dataBindingContext = new DataBindingContext();

		// If loadState() has not loaded saved parameters, create empty object
		if (scanParameters == null) {
			scanParameters = new I14XanesEdgeParameters();
		}

		final Composite content = new Composite(parent, SWT.NONE);
		GridDataFactory.swtDefaults().applyTo(content);
		GridLayoutFactory.swtDefaults().numColumns(2).applyTo(content);
		content.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));

		// Title
		createLabel(content, "XANES scan parameters", 2);

		// Energy parameters
		final Group grpEnergy = createGroup(content, String.format("Energy (%s)", ENERGY_SCANNABLE), NUM_COLUMNS);
		GridDataFactory.swtDefaults().align(SWT.BEGINNING, SWT.BEGINNING).grab(true, false).applyTo(grpEnergy);

		// Find the model wrapper for the energy scannable
		final List<IScanModelWrapper<IScanPathModel>> energyScannables = getMappingBean().getScanDefinition()
				.getOuterScannables()
				.stream()
				.filter(scannable -> scannable.getName().equals(ENERGY_SCANNABLE))
				.collect(toList());

		if (energyScannables.isEmpty()) {
			logger.error("No energy scannable '{}' is defined", ENERGY_SCANNABLE);
			return;
		}

		final IScanModelWrapper<IScanPathModel> energyScannable = energyScannables.get(0);
		energyScannable.setIncludeInScan(true);
		energyEditor = new ScanPathEditor(grpEnergy, SWT.NONE, energyScannable);
		energyEditor.addIObserver(scanPathObserver);
		scanParameters.setEnergySteps(energyEditor.getAxisText());

		// Tracking parameters
		final Group grpTracking = createGroup(content, "Tracking", NUM_COLUMNS);
		createTextInput(grpTracking, "Lines to track", "e.g. Au-La", "linesToTrack", scanParameters.getLinesToTrack());

		final Composite cmpTrackingMethod = new Composite(grpTracking, SWT.NONE);
		GridDataFactory.swtDefaults().span(NUM_COLUMNS, 1).applyTo(cmpTrackingMethod);
		GridLayoutFactory.swtDefaults().numColumns(2).applyTo(cmpTrackingMethod);
		cmpTrackingMethod.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));

		final SelectObservableValue<String> radioButtonObservable = new SelectObservableValue<>();
		final Button btnUseReference = createRadioButton(cmpTrackingMethod, "Use reference");
		radioButtonObservable.addOption(REFERENCE.toString(), WidgetProperties.selection().observe(btnUseReference));
		final Button btnUseEdge = createRadioButton(cmpTrackingMethod, "Use edge");
		radioButtonObservable.addOption(EDGE.toString(), WidgetProperties.selection().observe(btnUseEdge));

		final IObservableValue<I14XanesEdgeParameters> modelObservable = PojoProperties.value(I14XanesEdgeParameters.class, "trackingMethod", TrackingMethod.class).observe(scanParameters);
		dataBindingContext.bindValue(radioButtonObservable, modelObservable);

		if (scanParameters.getTrackingMethod().equals(REFERENCE.toString())) {
			btnUseReference.setSelection(true);
		} else if (scanParameters.getTrackingMethod().equals(EDGE.toString())) {
			btnUseEdge.setSelection(true);
		}
	}

	private static Button createRadioButton(Composite parent, String text) {
		final Button button = new Button(parent, SWT.RADIO);
		button.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		button.setText(text);
		return button;
	}

	private static Label createLabel(Composite parent, String text, int numColumns) {
		final Label label = new Label(parent, SWT.WRAP);
		GridDataFactory.swtDefaults().span(numColumns, 1).applyTo(label);
		label.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		label.setText(text);
		return label;
	}

	private static Group createGroup(Composite parent, String name, int columns) {
		final Group group = new Group(parent, SWT.NONE);
		GridDataFactory.swtDefaults().applyTo(group);
		GridLayoutFactory.swtDefaults().numColumns(columns).applyTo(group);
		group.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		group.setText(name);
		return group;
	}

	private void handleScanPathUpdate(Object source, @SuppressWarnings("unused") Object arg) {
		final ScanPathEditor scanPathEditor = (ScanPathEditor) source;
		scanParameters.setEnergySteps(scanPathEditor.getAxisText());
		updateStatusLabel();
	}

	/**
	 * Create text input (comprising label, text box itself and hint), and bind to the model
	 *
	 * @param parent
	 *            Parent composite for the controls
	 * @param name
	 *            Name of input (to be shown in label)
	 * @param hint
	 *            Hint for filling in value (shown after the text box)
	 * @param modelProperty
	 *            Property to bind this value to
	 */
	private void createTextInput(Composite parent, String name, String hint, String modelProperty, String initialText) {
		createLabel(parent, name, 1);
		final Text textBox = new Text(parent, SWT.BORDER);
		GridDataFactory.swtDefaults().minSize(80, SWT.DEFAULT).grab(true, false).applyTo(textBox);
		if (initialText != null) {
			textBox.setText(initialText);
		}
		createLabel(parent, hint, 1);

		final ISWTObservableValue txtObservable = WidgetProperties.text(SWT.Modify).observe(textBox);
		@SuppressWarnings("unchecked")
		final IObservableValue<I14XanesEdgeParameters> modelObservable = PojoProperties.value(modelProperty).observe(scanParameters);
		dataBindingContext.bindValue(txtObservable, modelObservable);
	}

	@Override
	protected void saveState(Map<String, String> persistedState) {
		try {
			logger.debug("Saving XANES parameters");
			final IMarshallerService marshaller = getService(IMarshallerService.class);
			persistedState.put(I14_XANES_SCAN_KEY, marshaller.marshal(scanParameters));
		} catch (Exception e) {
			logger.error("Error saving XANES scan parameters", e);
		}
	}

	@Override
	protected void loadState(Map<String, String> persistedState) {
		final String json = persistedState.get(I14_XANES_SCAN_KEY);
		if (json == null || json.isEmpty()) { // This happens when client is reset || if no detectors are configured.
			logger.debug("No XANES parameters to load");
			return;
		}

		try {
			logger.debug("Loading XANES parameters");
			final IMarshallerService marshaller = getService(IMarshallerService.class);
			scanParameters = marshaller.unmarshal(json, I14XanesEdgeParameters.class);
		} catch (Exception e) {
			logger.error("Error restoring XANES scan parameters", e);
		}
	}

	public I14XanesEdgeParameters getScanParameters() {
		return scanParameters;
	}

	@Override
	public void dispose() {
		energyEditor.dispose();
		super.dispose();
	}
}
