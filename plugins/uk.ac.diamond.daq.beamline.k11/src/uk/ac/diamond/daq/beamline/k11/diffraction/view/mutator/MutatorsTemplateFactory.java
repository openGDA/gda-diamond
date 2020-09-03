/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.mutator;

import static org.eclipse.swt.events.SelectionListener.widgetSelectedAdapter;
import static uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeHelper.POLICY_NEVER;
import static uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeHelper.scanPathToRandomised;
import static uk.ac.gda.ui.tool.ClientMessages.MUTATORS_MODE;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientCompositeWithGridLayout;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGridDataFactory;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientLabel;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Supplier;

import org.apache.commons.lang3.tuple.ImmutablePair;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.conversion.IConverter;
import org.eclipse.core.databinding.observable.IChangeListener;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.databinding.observable.value.IValueChangeListener;
import org.eclipse.core.databinding.observable.value.SelectObservableValue;
import org.eclipse.jface.databinding.swt.ISWTObservableValue;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.scanning.api.points.models.AbstractPointsModel;
import org.eclipse.scanning.api.points.models.IScanPathModel;
import org.eclipse.scanning.api.points.models.IScanPointGeneratorModel;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;

import gda.mscan.element.Mutator;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeInterface;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.api.document.helper.ScanpathDocumentHelper;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanning.ShapeType;
import uk.ac.diamond.daq.mapping.region.CentredRectangleMappingRegion;
import uk.ac.diamond.daq.mapping.ui.diffraction.model.MutatorType;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController;

/**
 * Components representing the GUI mutators elements
 *
 * @author Maurizio Nagni
 */
public class MutatorsTemplateFactory implements DiffractionCompositeInterface {

	private final SelectObservableValue<ShapeType> selectedShapeObservable;

	private SelectObservableValue<IMappingScanRegionShape> selectedMSRSObservable = new SelectObservableValue<>();
	private Map<MutatorType, ISWTObservableValue> mutatorObservableValues = new EnumMap<>(MutatorType.class);

	private final List<MutatorComposite> mutators = new ArrayList<>();

	private final DataBindingContext viewDBC;
	private final DataBindingContext regionDBC;

	private final RegionAndPathController rapController;
	private final ScanManagementController smController;
	private ScanpathDocumentHelper scanpathDocumentHelper;
	private final Supplier<ScanningAcquisition> acquisitionSupplier;

	public MutatorsTemplateFactory(DataBindingContext viewDBC, DataBindingContext regionDBC,
			Supplier<ScanningAcquisition> acquisitionSupplier, SelectObservableValue<ShapeType> selectedShapeObservable,
			RegionAndPathController rapController, ScanManagementController smController) {
		super();
		this.viewDBC = viewDBC;
		this.regionDBC = regionDBC;
		this.selectedShapeObservable = selectedShapeObservable;
		this.rapController = rapController;
		this.acquisitionSupplier = acquisitionSupplier;
		this.scanpathDocumentHelper = new ScanpathDocumentHelper(this::getScanningParameters);
		this.smController = smController;
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		Composite container = createClientCompositeWithGridLayout(parent, style, 1);
		createClientGridDataFactory().align(SWT.BEGINNING, SWT.BEGINNING).indent(5, SWT.DEFAULT).applyTo(container);

		Label label = createClientLabel(container, style, MUTATORS_MODE);
		createClientGridDataFactory().align(SWT.BEGINNING, SWT.END).span(2, 1).indent(5, SWT.DEFAULT).applyTo(label);

		mutators.add(new AlternatingMutator(widgetSelectedAdapter(this::mutatorListener)));
		mutators.add(new ContinuousMutator(widgetSelectedAdapter(this::mutatorListener)));
		mutators.add(new RandomMutator(widgetSelectedAdapter(this::mutatorListener)));

		mutators.stream().forEach(s -> s.createComposite(container, style));

		bindControls();

		return parent;
	}

	@Override
	public void bindControls() {
		mutators.stream().forEach(m -> bindMutatorCheckboxWidget(m.getMutatorDefinition().getValue(), m.filterShape()));
		selectedShapeObservable.addChangeListener(selectedShapedListener);
	}

	IChangeListener selectedShapedListener = event -> {
		ShapeType shapeType = ShapeType.class.cast(((SelectObservableValue<?>) event.getObservable()).getValue()); // <--
		// ShapeType
		mutators.stream().forEach(m -> {
			Button mutator = m.getMutatorDefinition().getValue();
			mutator.setSelection(false);
			mutator.setVisible(m.acceptShape(shapeType));
			updateMutator(mutator);
		});
	};

	@Override
	public void updateScanPointBindings(final IScanPointGeneratorModel newPathValue, ShapeType shapeType) {
		updateScanPathBindings(newPathValue);
	}

	private void bindMutatorCheckboxWidget(final Button button, IConverter converter) {
		MutatorType buttonMutator = (MutatorType) button.getData();
		ISWTObservableValue buttonCheckedObservable = WidgetProperties.selection().observe(button);
		mutatorObservableValues.put(buttonMutator, buttonCheckedObservable);

		@SuppressWarnings("unchecked")
		IObservableValue<MutatorType> disableButtonIObservableValue = WidgetProperties.visible().observe(button);
		viewDBC.bindValue(selectedShapeObservable, disableButtonIObservableValue, UpdateValueStrategy.create(converter),
				POLICY_NEVER);
	}

	private void mutatorListener(SelectionEvent event) {
		updateMutator(Button.class.cast(event.getSource()));
	}

	private void updateMutator(Button mutatorButton) {
		// updates the mutators list into the templateData collecting data from the selected check boxes
		Mutator mutator = Optional.ofNullable(mutatorButton.getData())
				.map(MutatorType.class::cast)
				.map(MutatorType::getMscanMutator)
				.orElseGet(() -> null);

		if (mutatorButton.getSelection() && mutator != null) {
			scanpathDocumentHelper.addMutators(mutator, new ArrayList<>());
		} else {
			scanpathDocumentHelper.removeMutators(mutator);
		}
	}

	/**
	 * Rewrites the bindings that link the mutator checkbox controls to the appropriate properties on the mapping bean's
	 * path model
	 *
	 * @param newPathValue
	 *            The {@link IScanPointGeneratorModel} currently selected on the mapping bean
	 */
	@SuppressWarnings("unchecked")
	private void updateScanPathBindings(final IScanPointGeneratorModel newPathValue) {
		if (AbstractPointsModel.supportsRandomOffset(newPathValue.getClass())) {
			doRandomOffsetSpecialHandling();
		}
		if (AbstractPointsModel.supportsContinuous(newPathValue.getClass())) {
			IObservableValue<Boolean> pathContinuousObservableValue = BeanProperties.value("continuous")
					.observe(newPathValue);
			regionDBC.bindValue(getMutatorObservableValue(MutatorType.CONTINUOUS), pathContinuousObservableValue);
		}
		if (AbstractPointsModel.supportsAlternating(newPathValue.getClass())) {
			IObservableValue<Boolean> pathAlternatingObservableValue = BeanProperties.value("alternating")
					.observe(newPathValue);
			regionDBC.bindValue(getMutatorObservableValue(MutatorType.ALTERNATING), pathAlternatingObservableValue);
		}
		mutators.stream().map(MutatorComposite::getMutatorDefinition).map(ImmutablePair::getValue)
				.forEach(this::updateMutator);
	}

	@SuppressWarnings("unchecked")
	private void doRandomOffsetSpecialHandling() {
		// Because of this, changes to the scan
		// path (when the selected region is rectangular) need to be reflected by the Random Offset checkbox.

		IObservableValue<IScanPathModel> mbPathObservableValue = getMappingBeanPathObservableValue();
		UpdateValueStrategy strategy = UpdateValueStrategy.create(scanPathToRandomised);
		regionDBC.bindValue(getMutatorObservableValue(MutatorType.RANDOM), mbPathObservableValue, POLICY_NEVER,
				strategy);

		// In addition selection of the Random Offset checkbox needs to manually trigger a RegionSelectorListener
		// update without changing the actual shape, hence this nasty bit of code.
		getMutatorObservableValue(MutatorType.RANDOM).addValueChangeListener(randomOffsetListener);
	}

	private final IValueChangeListener<Boolean> randomOffsetListener = event -> {
		if (getRapController().getScanRegionShape().getClass().equals(CentredRectangleMappingRegion.class)) {
			getSmController().updateGridModelIndex((boolean) event.getObservableValue().getValue());

			// Manually trigger the switch between GridModels
			getRapController().triggerRegionUpdate(selectedMSRSObservable);
		}
	};

	@SuppressWarnings("unchecked")
	private IObservableValue<IScanPathModel> getMappingBeanPathObservableValue() {
		return BeanProperties.value("scanPath").observe(rapController.getScanRegionFromBean());
	}

	private ISWTObservableValue getMutatorObservableValue(MutatorType mutator) {
		return getMutatorObservablesValue().get(mutator);
	}

	public Map<MutatorType, ISWTObservableValue> getMutatorObservablesValue() {
		return mutatorObservableValues;
	}

	private RegionAndPathController getRapController() {
		return rapController;
	}

	private ScanManagementController getSmController() {
		return smController;
	}

	private ScanningParameters getScanningParameters() {
		return this.acquisitionSupplier.get().getAcquisitionConfiguration().getAcquisitionParameters();
	}
}
