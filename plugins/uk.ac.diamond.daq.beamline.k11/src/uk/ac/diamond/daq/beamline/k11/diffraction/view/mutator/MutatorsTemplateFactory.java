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

import static uk.ac.gda.ui.tool.ClientMessages.MUTATORS_MODE;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientCompositeWithGridLayout;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGridDataFactory;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientLabel;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;

import org.eclipse.core.databinding.observable.value.IValueChangeListener;
import org.eclipse.jface.databinding.swt.ISWTObservableValue;
import org.eclipse.jface.databinding.swt.typed.WidgetProperties;
import org.eclipse.scanning.api.points.models.IScanPointGeneratorModel;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Widget;
import org.springframework.context.ApplicationListener;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeInterface;
import uk.ac.diamond.daq.mapping.api.document.AcquisitionTemplateType;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent;
import uk.ac.diamond.daq.mapping.api.document.helper.ScanpathDocumentHelper;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.region.CentredRectangleMappingRegion;
import uk.ac.diamond.daq.mapping.ui.diffraction.model.MutatorType;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.WidgetUtilities;


/**
 * Components representing the GUI mutators elements
 *
 * @author Maurizio Nagni
 */
public class MutatorsTemplateFactory implements DiffractionCompositeInterface {

	public static final String MUTATOR_TYPE = "MutatorType";
	public static final String MUTATOR_CHECKED_OBSERVABLE = "MutatorCheckedObservable";
	public static final String MUTATOR_BINDING = "MutatorBinding";

	private final List<Button> mutators = new ArrayList<>();

	private final RegionAndPathController rapController;
	private final ScanManagementController smController;
	private ScanpathDocumentHelper scanpathDocumentHelper;
	private final Supplier<ScanningAcquisition> acquisitionSupplier;

	public MutatorsTemplateFactory(Supplier<ScanningAcquisition> acquisitionSupplier,
			RegionAndPathController rapController,
			 ScanManagementController smController) {
		super();
		this.rapController = rapController;
		this.acquisitionSupplier = acquisitionSupplier;
		this.scanpathDocumentHelper = new ScanpathDocumentHelper(this::getScanningParameters);
		this.smController = smController;
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		Composite container = createClientCompositeWithGridLayout(parent, style, 1);
		createClientGridDataFactory().align(SWT.FILL, SWT.TOP).applyTo(container);

		Label label = createClientLabel(container, style, MUTATORS_MODE);
		createClientGridDataFactory().align(SWT.FILL, SWT.TOP).applyTo(label);

		mutators.add(createMutatorTypeCheckBox(container, MutatorType.ALTERNATING, ClientMessages.ALTERNATING_MUTATOR,
				ClientMessages.ALTERNATING_MUTATOR_TP));
		mutators.add(createMutatorTypeCheckBox(container, MutatorType.CONTINUOUS, ClientMessages.CONTINUOUS_MUTATOR,
				ClientMessages.CONTINUOUS_MUTATOR_TP));
		mutators.add(createMutatorTypeCheckBox(container, MutatorType.RANDOM, ClientMessages.RANDOM_MUTATOR,
				ClientMessages.RANDOM_MUTATOR_TP));
		SpringApplicationContextFacade.addDisposableApplicationListener(this, listenToScanningAcquisitionChanges);

		// Releases resources before dispose
		container.addDisposeListener(event -> dispose()	);
		return container;
	}

	@Override
	public void initialiseElements() {
		mutators.stream()
			.forEach(mutator -> {
				mutator.setSelection(false);
				mutator.setEnabled(true);
				MutatorType mutatorType = getDataObject(mutator, MutatorType.class, MUTATOR_TYPE);
				mutator.setSelection(getScanningParameters().getScanpathDocument().getMutators()
										.containsKey(mutatorType.getMscanMutator()));
				if (AcquisitionTemplateType.TWO_DIMENSION_POINT.equals(getSelectedAcquisitionTemplateType())
						&& (mutatorType.equals(MutatorType.ALTERNATING) || mutatorType.equals(MutatorType.CONTINUOUS))) {
					mutator.setEnabled(false);
			}
		});
	}

	@Override
	public void initializeBinding() {
		scanPointListenToMutatorSelection();
	}

	private void dispose() {
		SpringApplicationContextFacade.removeApplicationListener(listenToScanningAcquisitionChanges);
	}

	/**
	 * Observes the value of the radios so the rapController.regionSelectorListener can listen at it
	 */
	private void scanPointListenToMutatorSelection() {
		IScanPointGeneratorModel scanPointGeneratorModel = rapController.getScanPathModel();

		mutators.stream()
			.filter(w -> !w.isDisposed())
			.forEach(mutator -> {
			switch (getDataObject(mutator, MutatorType.class, MUTATOR_TYPE)) {
				case CONTINUOUS:
					scanPointGeneratorModel.setContinuous(mutator.getSelection());
					break;
				case ALTERNATING:
					scanPointGeneratorModel.setAlternating(mutator.getSelection());
					break;
				case RANDOM:
					mutator.setEnabled(false); // TODO FIXME enable the button when appropriate and add a random offset
					break;
				default:
					break;
				}
		});
	}

	private void mutatorListener(SelectionEvent event) {
		Optional.ofNullable(event.getSource())
			.map(Button.class::cast)
			.ifPresent(mutator -> {
				MutatorType mutatorType = getDataObject(mutator, MutatorType.class, MUTATOR_TYPE);
				if (mutator.getSelection()) {
					scanpathDocumentHelper.addMutators(mutatorType.getMscanMutator(), new ArrayList<>());
				} else {
					scanpathDocumentHelper.removeMutators(mutatorType.getMscanMutator());
				}
				SpringApplicationContextFacade.publishEvent(
						new ScanningAcquisitionChangeEvent(this, getScanningAcquisition()));
			});
	}

	private final IValueChangeListener<Boolean> randomOffsetListener = event -> {
		if (getRapController().getScanRegionShape().getClass().equals(CentredRectangleMappingRegion.class)) {
			getSmController().updateGridModelIndex((boolean) event.getObservableValue().getValue());
		}
	};

	private RegionAndPathController getRapController() {
		return rapController;
	}

	private ScanManagementController getSmController() {
		return smController;
	}

	// At the moment is not possible to use anonymous lambda expression because it
	// generates a class cast exception
	private ApplicationListener<ScanningAcquisitionChangeEvent> listenToScanningAcquisitionChanges
			= new ApplicationListener<ScanningAcquisitionChangeEvent>() {
		@Override
		public void onApplicationEvent(ScanningAcquisitionChangeEvent event) {
			UUID eventUUID = Optional.ofNullable(event.getScanningAcquisition())
					.map(ScanningAcquisition::getUuid)
					.orElseGet(UUID::randomUUID);

			UUID scanningAcquisitionUUID = Optional.ofNullable(acquisitionSupplier.get())
					.map(ScanningAcquisition::getUuid)
					.orElseGet(UUID::randomUUID);

			if (eventUUID.equals(scanningAcquisitionUUID)) {
				initialiseElements();
				scanPointListenToMutatorSelection();
			}
		}
	};

	// ------------ UTILS ----

	private ScanningAcquisition getScanningAcquisition() {
		return this.acquisitionSupplier.get();
	}

	private ScanningParameters getScanningParameters() {
		return getScanningAcquisition().getAcquisitionConfiguration().getAcquisitionParameters();
	}

	private AcquisitionTemplateType getSelectedAcquisitionTemplateType() {
		return getScanningParameters().getScanpathDocument().getModelDocument();
	}

	private Button createMutatorTypeCheckBox(Composite parent, MutatorType mutatorType, ClientMessages title,
			ClientMessages tooltip) {
		Button button = ClientSWTElements.createClientButton(parent, SWT.CHECK, title, tooltip);
		// Sets the mutator type. In this way is easier to have the type should the element be selected
		button.setData(MUTATOR_TYPE, mutatorType);
		WidgetUtilities.addWidgetDisposableListener(button, SelectionListener.widgetSelectedAdapter(this::mutatorListener));

		ISWTObservableValue<Boolean> checkedObservable = WidgetProperties.buttonSelection().observe(button);
		button.setData(MUTATOR_CHECKED_OBSERVABLE, checkedObservable);

		if (MutatorType.RANDOM.equals(mutatorType)) {
			checkedObservable.addValueChangeListener(randomOffsetListener);
		}

		return button;
	}

	// To replace with WidgetUtilities.getDataObject when available (K11-837)
	private static <T> T getDataObject(Widget widget, Class<T> clazz, String dataKey) {
		return Optional.ofNullable(widget.getData(dataKey))
				.map(clazz::cast)
				.orElseGet(() -> null);
	}
}