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

import static uk.ac.gda.ui.tool.ClientMessages.CONFIGURATION_LAYOUT_ERROR;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientCompositeWithGridLayout;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGridDataFactory;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGroup;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientLabel;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientText;
import static uk.ac.gda.ui.tool.ClientSWTElements.standardMarginHeight;
import static uk.ac.gda.ui.tool.ClientSWTElements.standardMarginWidth;

import java.net.URL;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.Optional;
import java.util.function.Consumer;

import org.eclipse.core.databinding.observable.value.SelectObservableValue;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.dawnsci.plotting.api.trace.ITraceListener;
import org.eclipse.dawnsci.plotting.api.trace.TraceEvent;
import org.eclipse.scanning.api.points.models.IScanPathModel;
import org.eclipse.scanning.api.points.models.IScanPointGeneratorModel;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Scale;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.ApplicationListener;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeInterface;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.TemplateDataHelper;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.density.RegionAndPathControllerUpdater;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.mutator.MutatorsTemplateFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.shape.AcquisitionTemplateTypeCompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.summary.SummaryCompositeFactory;
import uk.ac.diamond.daq.mapping.api.IMappingExperimentBean;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController.RegionPathState;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController;
import uk.ac.gda.api.acquisition.parameters.DetectorDocument;
import uk.ac.gda.api.acquisition.resource.event.AcquisitionConfigurationResourceLoadEvent;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.exception.AcquisitionConfigurationException;
import uk.ac.gda.client.exception.GDAClientException;
import uk.ac.gda.client.properties.acquisition.AcquisitionConfigurationProperties;
import uk.ac.gda.client.properties.acquisition.AcquisitionPropertyType;
import uk.ac.gda.client.properties.acquisition.ProcessingRequestProperties;
import uk.ac.gda.core.tool.spring.AcquisitionFileContext;
import uk.ac.gda.core.tool.spring.DiffractionContextFile;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.Reloadable;
import uk.ac.gda.ui.tool.controller.AcquisitionController;
import uk.ac.gda.ui.tool.document.DocumentFactory;
import uk.ac.gda.ui.tool.document.ScanningAcquisitionTemporaryHelper;
import uk.ac.gda.ui.tool.processing.ProcessingRequestComposite;
import uk.ac.gda.ui.tool.processing.context.ProcessingRequestContext;
import uk.ac.gda.ui.tool.processing.keys.ProcessingRequestKeyFactory;
import uk.ac.gda.ui.tool.processing.keys.ProcessingRequestKeyFactory.ProcessKey;
import uk.ac.gda.ui.tool.spring.ClientRemoteServices;
import uk.ac.gda.ui.tool.spring.ClientSpringProperties;

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
	private TemplateDataHelper templateHelper;
	private RegionAndPathController rapController = PlatformUI.getWorkbench().getService(RegionAndPathController.class);
	private RegionAndPathControllerUpdater rapUpdater;
	private Consumer<RegionPathState> viewUpdater;

	private SelectObservableValue<IMappingScanRegionShape> selectedMSRSObservable = new SelectObservableValue<>();

	private ScanManagementController smController;

	private DiffractionCompositeInterface summaryCompositeFactory;

	private final List<CompositeFactory> components = new ArrayList<>();

	private Composite mainComposite;
	private ProcessingRequestComposite processingRequestComposite;

	private void prepareSupport() {
		components.clear();
		prepareSupport(getController());
	}

	private void prepareSupport(AcquisitionController<ScanningAcquisition> controller) {
		this.templateHelper = new TemplateDataHelper(controller::getAcquisition);
		// create and initialise the controller to manage updates to the selected region and path
		viewUpdater = this::updateView;
		rapController = PlatformUI.getWorkbench().getService(RegionAndPathController.class);
		rapController.initialise(Optional.of(viewUpdater), Optional.empty());
		smController = PlatformUI.getWorkbench().getService(ScanManagementController.class);
		smController.initialise();

		stf = new AcquisitionTemplateTypeCompositeFactory(controller::getAcquisition, rapController);

		rapUpdater = new RegionAndPathControllerUpdater(controller::getAcquisition, rapController);

		var mcf = new MutatorsTemplateFactory(controller::getAcquisition, rapController, smController);
		summaryCompositeFactory = new SummaryCompositeFactory();

		components.add(stf);
		components.add(mcf);
	}

	private void dispose() {
		Optional.ofNullable(viewUpdater)
			.ifPresent(rapController::detachViewUpdater);
		getMap().ifPresent(plot -> plot.removeTraceListener(traceListener));
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		logger.trace("Creating {}", this);
		mainComposite = createClientCompositeWithGridLayout(parent, style, 1);

		try {
			prepareSupport();
			createClientGridDataFactory().align(SWT.FILL, SWT.FILL).applyTo(mainComposite);

			createElements(mainComposite, SWT.NONE);
			loadElements();

			SpringApplicationContextFacade.publishEvent(new ScanningAcquisitionChangeEvent(this));
			standardMarginHeight(mainComposite.getLayout());
			standardMarginWidth(mainComposite.getLayout());

			// Releases resources before dispose
			mainComposite.addDisposeListener(event -> dispose()	);
			logger.debug("Created {}", this);
		} catch (NoSuchElementException e) {
			UIHelper.showWarning(CONFIGURATION_LAYOUT_ERROR, e);
		}
		return mainComposite;
	}

	@Override
	public void reload() {
		loadElements();
		templateHelper.updateIMappingScanRegionShape();
		rapController.updatePlotRegion();
		processingRequestComposite.reload();
		mainComposite.getShell().layout(true, true);
	}

	private final ModifyListener modifyNameListener = event -> updateAcquisitionName();

	private void updateAcquisitionName() {
		getScanningAcquisitionTemporaryHelper()
			.getScanningAcquisition()
			.ifPresent(a -> a.setName(name.getText()));
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
		return getScanningAcquisitionTemporaryHelper().getAcquisitionControllerElseThrow();
	}

	private void createElements(Composite parent, int labelStyle) {
		createConfiguration(parent, labelStyle);
		createSummary(parent, labelStyle);
		createCalibration(parent, labelStyle);

		SpringApplicationContextFacade.addDisposableApplicationListener(this, listenToScanningAcquisitionChanges);
	}

	private void createConfiguration(Composite parent, int labelStyle) {
		int columns = components.size();
		var externalContainer = createClientCompositeWithGridLayout(parent, labelStyle, columns);
		createClientGridDataFactory().align(SWT.FILL, SWT.FILL).applyTo(externalContainer);

		var label = createClientLabel(externalContainer, labelStyle, ClientMessages.NAME);
		createClientGridDataFactory().applyTo(label);

		name = createClientText(externalContainer, labelStyle, ClientMessages.NAME_TOOLTIP);
		createClientGridDataFactory().span(columns - 1,1).applyTo(name);
		name.addModifyListener(modifyNameListener);

		components.stream()
			.map(c -> c.createComposite(externalContainer, labelStyle))
			.map(Composite::getLayout)
			.forEach(ClientSWTElements::standardMarginWidth);

		var summary = summaryCompositeFactory.createComposite(externalContainer, labelStyle);
		createClientGridDataFactory().span(columns,1).applyTo(summary);
	}

	private void createSummary(Composite parent, int labelStyle) {
		if (summaryCompositeFactory == null)
			return;
		var summaryContainer = createClientGroup(parent, SWT.NONE, 1, ClientMessages.SUMMARY);
		createClientGridDataFactory().applyTo(summaryContainer);
		var summaryContent = summaryCompositeFactory.createComposite(summaryContainer, labelStyle);
		createClientGridDataFactory().applyTo(summaryContainer);
		standardMarginHeight(summaryContent.getLayout());
		standardMarginWidth(summaryContent.getLayout());
	}

	@SuppressWarnings({ "rawtypes", "unchecked" })
	private List<ProcessingRequestContext<?>> getProcessingRequestContext() {
		// The selectable process elements
		List<ProcessingRequestContext<?>> processingRequestContexts = new ArrayList<>();

		// makes available for selection a SavuProcessingRequest element
		processingRequestContexts.add(new ProcessingRequestContext(getProcessingRequestKeyFactory().getProcessingKey(ProcessKey.DIFFRACTION_CALIBRATION),
				 getDiffractionCalibrationMergeDirectory(), getDefaultDiffractionCalibrationMergeFile(), false));
		processingRequestContexts.add(new ProcessingRequestContext(getProcessingRequestKeyFactory().getProcessingKey(ProcessKey.DAWN),
				 getDiffractionCalibrationMergeDirectory(), new ArrayList<>(), false));
		processingRequestContexts.add(new ProcessingRequestContext(getProcessingRequestKeyFactory().getProcessingKey(ProcessKey.FRAME_CAPTURE),
				 null, getCaptureFrameCamera(), false));
		return processingRequestContexts;
	}

	private List<DetectorDocument> getCaptureFrameCamera() {
		List<String> cameraIds = Collections.emptyList();
		try {
			cameraIds = SpringApplicationContextFacade.getBean(ClientSpringProperties.class).getAcquisitions().stream()
					.filter(a -> a.getType().equals(AcquisitionPropertyType.DIFFRACTION))
					.findFirst()
					.map(AcquisitionConfigurationProperties::getProcessingRequest)
					.map(ProcessingRequestProperties::getFrameCapture)
					.orElseThrow(() -> new AcquisitionConfigurationException("There are no properties associated with the acqual acquisition"));
		} catch (AcquisitionConfigurationException e1) {
			logger.error("Frame Capture cannot set camera", e1);
		}

		List<DetectorDocument> cameras = new ArrayList<>();
		for(String id : cameraIds) {
			try {
				var detectorDocument = getDocumentFactory().createDetectorDocument(id)
						.orElseThrow(GDAClientException::new);
				cameras.add(detectorDocument);
			} catch (GDAClientException e) {
				logger.error("Cannot create DetectorDocument: {}", e.getMessage());
			}
		}
		return cameras;
	}

	private URL getDiffractionCalibrationMergeDirectory() {
		return getClientContext().getDiffractionContext().getContextFile(DiffractionContextFile.DIFFRACTION_CALIBRATION_DIRECTORY);
	}

	private List<URL> getDefaultDiffractionCalibrationMergeFile() {
		List<URL> urls = new ArrayList<>();
		urls.add(getClientContext().getDiffractionContext().getContextFile(DiffractionContextFile.DIFFRACTION_DEFAULT_CALIBRATION));
		return urls;
	}

	private void createCalibration(Composite parent, int labelStyle) {
		var calibrationContainer = createClientGroup(parent, SWT.NONE, 1, ClientMessages.PROCESS_REQUESTS);
		createClientGridDataFactory().applyTo(calibrationContainer);

		processingRequestComposite = new ProcessingRequestComposite(getProcessingRequestContext());
		processingRequestComposite.createComposite(calibrationContainer, labelStyle);
	}

	private void loadElements() {
		initializeElements();
		initializeBinding();
		getScanningAcquisitionTemporaryHelper().getScanningAcquisition()
			.map(ScanningAcquisition::getName)
			.ifPresent(name::setText);
	}

	private void initializeElements() {
		components.stream()
			.filter(DiffractionCompositeInterface.class::isInstance)
			.map(DiffractionCompositeInterface.class::cast)
			.forEach(DiffractionCompositeInterface::initialiseElements);
	}

	private void initializeBinding() {
		components.stream()
			.filter(DiffractionCompositeInterface.class::isInstance)
			.map(DiffractionCompositeInterface.class::cast)
			.forEach(DiffractionCompositeInterface::initializeBinding);
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
		getMap().ifPresent(pl -> pl.addTraceListener(traceListener));
	}

	private ITraceListener traceListener = new ITraceListener.Stub() {
		@Override
		public void traceAdded(TraceEvent evt) {
			super.traceAdded(evt);
			if (templateHelper.updateScannableTracksDocument()) {
				SpringApplicationContextFacade.publishEvent(new ScanningAcquisitionChangeEvent(this));
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
		updateScanPointBindings();
		summaryCompositeFactory.updateScanPointBindings();
	}

	private void updateScanPointBindings() {
		components.stream()
			.filter(DiffractionCompositeInterface.class::isInstance)
			.map(DiffractionCompositeInterface.class::cast)
			.forEach(DiffractionCompositeInterface::updateScanPointBindings);
	}

	private Optional<IPlottingSystem<Composite>> getMap() {
		return Optional.ofNullable(SpringApplicationContextFacade.getBean(ClientRemoteServices.class)
				.getIPlottingService().getPlottingSystem("Map"));
	}

	// At the moment is not possible to use anonymous lambda expression because it
	// generates a class cast exception
	private ApplicationListener<AcquisitionConfigurationResourceLoadEvent> listenToScanningAcquisitionChanges = new ApplicationListener<AcquisitionConfigurationResourceLoadEvent>() {
		@Override
		public void onApplicationEvent(AcquisitionConfigurationResourceLoadEvent event) {
			SpringApplicationContextFacade.publishEvent(new ScanningAcquisitionChangeEvent(this));
		}
	};

	// ------------ UTILS ----
	private AcquisitionFileContext getClientContext() {
		return SpringApplicationContextFacade.getBean(AcquisitionFileContext.class);
	}

	private ProcessingRequestKeyFactory getProcessingRequestKeyFactory() {
		return SpringApplicationContextFacade.getBean(ProcessingRequestKeyFactory.class);
	}

	private ScanningAcquisitionTemporaryHelper getScanningAcquisitionTemporaryHelper() {
		return SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class);
	}

	private DocumentFactory getDocumentFactory() {
		return SpringApplicationContextFacade.getBean(DocumentFactory.class);
	}
}
