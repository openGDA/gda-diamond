/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction;

import static uk.ac.gda.ui.tool.ClientSWTElements.createClientCompositeWithGridLayout;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGridDataFactory;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGroup;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientLabel;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientText;
import static uk.ac.gda.ui.tool.ClientSWTElements.standardMarginHeight;
import static uk.ac.gda.ui.tool.ClientSWTElements.standardMarginWidth;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.function.Consumer;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.observable.value.SelectObservableValue;
import org.eclipse.dawnsci.plotting.api.IPlottingService;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.dawnsci.plotting.api.trace.ITraceListener;
import org.eclipse.dawnsci.plotting.api.trace.TraceEvent;
import org.eclipse.scanning.api.points.models.IScanPathModel;
import org.eclipse.scanning.api.points.models.IScanPointGeneratorModel;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Scale;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.ApplicationListener;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeInterface;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.TemplateDataHelper;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.density.DensityCompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.mutator.MutatorsTemplateFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.shape.AcquisitionTemplateTypeCompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.summary.SummaryCompositeFactory;
import uk.ac.diamond.daq.beamline.k11.view.CalibrationFileComposite;
import uk.ac.diamond.daq.mapping.api.IMappingExperimentBean;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController.RegionPathState;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController;
import uk.ac.gda.api.acquisition.AcquisitionController;
import uk.ac.gda.api.acquisition.resource.event.AcquisitionConfigurationResourceLoadEvent;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.Reloadable;

/**
 * This Composite allows to edit a {@link ScanningParameters} object.
 *
 * @author Maurizio Nagni
 */
public class DiffractionConfigurationLayoutFactory implements CompositeFactory, Reloadable {

	private static final Logger logger = LoggerFactory.getLogger(DiffractionConfigurationLayoutFactory.class);

	// ----- Model GUI ------//
	/** Scan prefix **/
	private Text name;

	// ----- Helper ------//
	private AcquisitionTemplateTypeCompositeFactory stf;
	private final AcquisitionController<ScanningAcquisition> controller;
	private TemplateDataHelper templateHelper;
	private RegionAndPathController rapController = PlatformUI.getWorkbench().getService(RegionAndPathController.class);
	private Consumer<RegionPathState> viewUpdater;

	private SelectObservableValue<IMappingScanRegionShape> selectedMSRSObservable = new SelectObservableValue<>();

	private DataBindingContext viewDBC = new DataBindingContext(); // for bindings valid for the view's lifetime

	private ScanManagementController smController;

	private DiffractionCompositeInterface summaryCompositeFactory;

	private final List<DiffractionCompositeInterface> components = new ArrayList<>();

	private Composite mainComposite;

	public DiffractionConfigurationLayoutFactory(AcquisitionController<ScanningAcquisition> controller) {
		this.controller = controller;
	}

	private void prepareSupport() {
		components.clear();
		this.templateHelper = new TemplateDataHelper(controller::getAcquisition);
		// create and initialise the controller to manage updates to the selected region and path
		viewUpdater = this::updateView;
		rapController = PlatformUI.getWorkbench().getService(RegionAndPathController.class);
		rapController.initialise(Optional.of(viewUpdater), Optional.empty());
		smController = PlatformUI.getWorkbench().getService(ScanManagementController.class);
		smController.initialise();

		stf = new AcquisitionTemplateTypeCompositeFactory(controller::getAcquisition, rapController);
		DiffractionCompositeInterface dcf = new DensityCompositeFactory(controller::getAcquisition, rapController);
		MutatorsTemplateFactory mcf = new MutatorsTemplateFactory(controller::getAcquisition, rapController, smController);
		summaryCompositeFactory = new SummaryCompositeFactory(controller::getAcquisition);

		components.add(stf);
		components.add(dcf);
		components.add(mcf);
	}

	private void dispose() {
		Optional.ofNullable(viewUpdater)
			.ifPresent(rapController::detachViewUpdater);
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		logger.trace("Creating {}", this);
		prepareSupport();
		mainComposite = createClientCompositeWithGridLayout(parent, style, 1);
		createClientGridDataFactory().align(SWT.FILL, SWT.FILL).applyTo(mainComposite);

		createElements(mainComposite, SWT.NONE);
		loadElements();

		SpringApplicationContextFacade.publishEvent(
				new ScanningAcquisitionChangeEvent(this, getScanningAcquisition()));
		standardMarginHeight(mainComposite.getLayout());
		standardMarginWidth(mainComposite.getLayout());

		// Releases resources before dispose
		mainComposite.addDisposeListener(event -> dispose()	);
		return mainComposite;
	}

	@Override
	public void reload() {
		loadElements();
		templateHelper.updateIMappingScanRegionShape();
		rapController.updatePlotRegion();
		mainComposite.getShell().layout(true, true);
	}

	private final ModifyListener modifyNameListener = event -> updateAcquisitionName();

	private void updateAcquisitionName() {
		getController().getAcquisition().setName(name.getText());
	}

	/**
	 * Loads the content of the file identified by the fully qualified filename parameter into the mapping bean and
	 * refreshes the UI to dispay the changes. An update of any linked UIs will also be triggered by the controllers
	 *
	 */
	public void load(Optional<IMappingExperimentBean> bean) {
		// When load is called, the existing mapping bean has bindings from
		// 1. its region shape to selectedShapeObservable
		// 2. its scanpath to the corresponding mutator checkboxes and the summary text
		// 3. its xaxis points count to the readout, scale and summary text
		// all under regionDBC which will need to be released along with the associated observable values.
		// This happens automatically in updateView i.e. when the RegionAndPathController's RegionSelector Listener is
		// triggered which in turn happens as a result of setting the value of selectedMSRSObservable. When this
		// happens,
		// the new mapping bean needs to be in place as the observable values are regenerated then. Also,
		// updateRegionShapeBindings (which is called by updateView) uses the controller cached version of ScanRegion
		// Shape so this too must be up to date by then

		if (bean.isPresent()) {

			// after this point we have now received a newly loaded mapping bean which will need to be substituted for
			// the existing one so that all the configured bindings (that don't belong to regionDBC) can be used

			// First we must update the values of the regions referenced by the selectedMSRSObservable to include the
			// one from the newly loaded bean. These objects will be the beans that were created by Spring at startup
			// (until the first load takes place). Because you cannot change the options within a SelectObservable, the
			// update must be done by creating a new instance of the observable having already replaced the
			// corresponding region shape object in the list of those created at startup with the new one.

			IMappingScanRegionShape loadedShape = bean.get().getScanDefinition().getMappingScanRegion().getRegion();
			boolean noShapeChange = selectedMSRSObservable.getValue().getClass().equals(loadedShape.getClass());

			// make a new observable using the new shape
			stf.refreshSelectedMSRSObservable(Optional.of(loadedShape));

			// Now refresh the mapping bean provider and trigger the refreshed observable to propagate the update. For
			// the time being also need to update the grid model index.
			rapController.setMappingBean(bean.get());
			rapController.refreshFromMappingBean();
			smController.updateGridModelIndex();
			selectedMSRSObservable.setValue(loadedShape);

			// if the shape has not changed, the observable will not propagate the change automatically, so have to do
			// it manually. It does however update its selection state and selected index which is why we always have
			// to call it.
			if (noShapeChange) {
				rapController.triggerRegionUpdate(selectedMSRSObservable);
			}
			rapController.updatePlotRegion();
		}
	}

	private AcquisitionController<ScanningAcquisition> getController() {
		return controller;
	}

	private void createElements(Composite parent, int labelStyle) {
		createConfiguration(parent, labelStyle);
		createSummary(parent, labelStyle);
		createCalibration(parent, labelStyle);

		SpringApplicationContextFacade.addDisposableApplicationListener(this, listenToScanningAcquisitionChanges);
	}

	private void createConfiguration(Composite parent, int labelStyle) {
		int columns = components.size();
		Composite externalContainer = createClientCompositeWithGridLayout(parent, labelStyle, columns);
		createClientGridDataFactory().align(SWT.FILL, SWT.FILL).applyTo(externalContainer);

		Label label = createClientLabel(externalContainer, labelStyle, ClientMessages.NAME);
		createClientGridDataFactory().applyTo(label);

		name = createClientText(externalContainer, labelStyle, ClientMessages.NAME_TOOLTIP);
		createClientGridDataFactory().span(columns - 1,1).applyTo(name);
		name.addModifyListener(modifyNameListener);

		components.forEach(c -> {
				Composite composite = c.createComposite(externalContainer, labelStyle);
				standardMarginWidth(composite.getLayout());
		});

		Composite summary = summaryCompositeFactory.createComposite(externalContainer, labelStyle);
		createClientGridDataFactory().span(columns,1).applyTo(summary);
	}

	private void createSummary(Composite parent, int labelStyle) {
		if (summaryCompositeFactory == null)
			return;
		Group summaryContainer = createClientGroup(parent, SWT.NONE, 1, ClientMessages.SUMMARY);
		createClientGridDataFactory().applyTo(summaryContainer);
		Composite summaryContent = summaryCompositeFactory.createComposite(summaryContainer, labelStyle);
		createClientGridDataFactory().applyTo(summaryContainer);
		standardMarginHeight(summaryContent.getLayout());
		standardMarginWidth(summaryContent.getLayout());
	}



	private void createCalibration(Composite parent, int labelStyle) {
		Group calibrationContainer = createClientGroup(parent, SWT.NONE, 1, ClientMessages.CALIBRATION);
		createClientGridDataFactory().applyTo(calibrationContainer);
		Composite calibrationComposite = new CalibrationFileComposite().createComposite(calibrationContainer, labelStyle);
		standardMarginHeight(calibrationContainer.getLayout());
		standardMarginWidth(calibrationContainer.getLayout());
	}



	private void loadElements() {
		components.forEach(DiffractionCompositeInterface::initialiseElements);
		summaryCompositeFactory.initialiseElements();
		components.forEach(DiffractionCompositeInterface::initializeBinding);
		summaryCompositeFactory.initializeBinding();
		name.setText(getScanningAcquisition().getName());
	}

	private class LoadListener implements ApplicationListener<AcquisitionConfigurationResourceLoadEvent> {

		private final Composite composite;

		public LoadListener(Composite composite) {
			super();
			this.composite = composite;
		}

		@Override
		public void onApplicationEvent(AcquisitionConfigurationResourceLoadEvent event) {
			loadElements();
			templateHelper.updateIMappingScanRegionShape();
			rapController.updatePlotRegion();
			composite.getShell().layout(true, true);
		}
	}

	/**
	 * This method is invoked when the IMappingScanRegionShape is change in the rapController.
	 * This may happen when
	 * <ul>
	 * <li> a different radio is selected (AcquisitionTemplateTypeCompositeFactory) </li>
     * <li> when a new ScanningAcquisition is loaded (LoadListener) </li>
	 * </ul>
	 */
	private final void updateView(RegionPathState regionPathState) {
		updateScanPathBindings();
		getMap().ifPresent(pl -> pl.addTraceListener(iTraceListener));
	}

	private ITraceListener iTraceListener = new ITraceListener.Stub() {
		@Override
		public void traceAdded(TraceEvent evt) {
			super.traceAdded(evt);
			if (templateHelper.updateScannableTracksDocument()) {
				SpringApplicationContextFacade.publishEvent(
						new ScanningAcquisitionChangeEvent(this, getScanningAcquisition()));
			}
		}
	};

	/**
	 * Rewrites the bindings relating to the mapping bean's region scan path model so that the {@link Scale} and
	 * {@link Text} density controls get linked to the correct property on the correct {@link IScanPathModel} when the
	 * region shape is changed by any linked views
	 *
	 * @param newPathValue
	 *            The resulting updated default scan path
	 */
	private void updateScanPathBindings() {
		IScanPointGeneratorModel scanPointGeneratorModel = rapController.getScanPathListAndLinkPath().get(0);
		rapController.changePath(scanPointGeneratorModel);
		components.forEach(DiffractionCompositeInterface::updateScanPointBindings);
		summaryCompositeFactory.updateScanPointBindings();
	}

	private Optional<IPlottingSystem<Composite>> getMap() {
		return Optional
				.ofNullable(PlatformUI.getWorkbench().getService(IPlottingService.class).getPlottingSystem("Map"));
	}

	// At the moment is not possible to use anonymous lambda expression because it
	// generates a class cast exception
	private ApplicationListener<AcquisitionConfigurationResourceLoadEvent> listenToScanningAcquisitionChanges = new ApplicationListener<AcquisitionConfigurationResourceLoadEvent>() {
		@Override
		public void onApplicationEvent(AcquisitionConfigurationResourceLoadEvent event) {
			SpringApplicationContextFacade.publishEvent(
					new ScanningAcquisitionChangeEvent(this, getScanningAcquisition()));
		}
	};

	// ------------ UTILS ----

	private ScanningAcquisition getScanningAcquisition() {
		return controller.getAcquisition();
	}
}