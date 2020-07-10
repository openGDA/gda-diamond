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

package uk.ac.diamond.daq.beamline.k11.diffraction.view;

import static uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeHelper.shapeFromMappingRegion;
import static uk.ac.gda.ui.tool.ClientMessages.ACQUISITION;
import static uk.ac.gda.ui.tool.ClientMessages.ACQUISITION_NAME_TP;
import static uk.ac.gda.ui.tool.ClientMessagesUtility.getMessage;

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
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.scanning.api.points.models.IScanPathModel;
import org.eclipse.scanning.api.points.models.IScanPointGeneratorModel;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Scale;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.PlatformUI;
import org.springframework.context.ApplicationListener;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.density.DensityCompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.mutator.MutatorsTemplateFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.shape.ShapesTemplateFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.summary.SummaryCompositeFactory;
import uk.ac.diamond.daq.mapping.api.IMappingExperimentBean;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanning.ShapeType;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController.RegionPathState;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController;
import uk.ac.gda.api.acquisition.AcquisitionController;
import uk.ac.gda.api.acquisition.resource.event.AcquisitionConfigurationResourceLoadEvent;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.exception.GDAClientException;
import uk.ac.gda.ui.tool.ClientBindingElements;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.spring.SpringApplicationContextProxy;

/**
 * This Composite allows to edit a {@link ScanningParameters} object.
 *
 * @author Maurizio Nagni
 */
public class DiffractionConfigurationCompositeFactory implements CompositeFactory {

	// ----- Model GUI ------//
	/** Scan prefix **/
	private Text name;

	// ----- Helper ------//
	private final ShapesTemplateFactory stf;
	protected final AcquisitionController<ScanningAcquisition> controller;
	private final TemplateDataHelper templateHelper;
	private RegionAndPathController rapController = PlatformUI.getWorkbench().getService(RegionAndPathController.class);
	private Consumer<RegionPathState> viewUpdater;

	private SelectObservableValue<IMappingScanRegionShape> selectedMSRSObservable = new SelectObservableValue<>();

	private DataBindingContext viewDBC = new DataBindingContext(); // for bindings valid for the view's lifetime
	private DataBindingContext regionDBC = new DataBindingContext(); // For bindings that refresh with the region

	private ScanManagementController smController;

	private final List<DiffractionCompositeInterface> components = new ArrayList<>();

	public DiffractionConfigurationCompositeFactory(AcquisitionController<ScanningAcquisition> controller) {
		super();
		this.controller = controller;
		this.templateHelper = new TemplateDataHelper(getTemplateData());
		// create and initialise the controller to manage updates to the selected region and path
		viewUpdater = this::updateView;
		rapController = PlatformUI.getWorkbench().getService(RegionAndPathController.class);
		rapController.initialise(Optional.of(viewUpdater), Optional.empty());
		smController = PlatformUI.getWorkbench().getService(ScanManagementController.class);
		smController.initialise();

		stf = new ShapesTemplateFactory(viewDBC, getTemplateData(), rapController);
		DiffractionCompositeInterface dcf = new DensityCompositeFactory(viewDBC, regionDBC, getTemplateData(),
				stf.getSelectedShape());
		MutatorsTemplateFactory mcf = new MutatorsTemplateFactory(viewDBC, regionDBC, getTemplateData(),
				stf.getSelectedShape(), rapController, smController);
		DiffractionCompositeInterface scf = new SummaryCompositeFactory(regionDBC,
				stf.getMappingScanRegionShapeObservableValue(), stf.getSelectedShape(), rapController);

		components.add(stf);
		components.add(dcf);
		components.add(mcf);
		components.add(scf);
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		Composite composite = ClientSWTElements.createComposite(parent, SWT.NONE, 2);

		createElements(parent, SWT.NONE, SWT.BORDER);
		bindElements();
		try {
			SpringApplicationContextProxy.addDisposableApplicationListener(composite, new LoadListener(composite));
		} catch (GDAClientException e) {
			UIHelper.showWarning("Loading a file will not refresh the gui",
					"Spring application listener not registered");
		}
		return composite;
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

	private void createElements(Composite parent, int labelStyle, int textStyle) {
		createName(parent, textStyle);
		parent.setBackground(parent.getDisplay().getSystemColor(SWT.COLOR_WIDGET_LIGHT_SHADOW));
		GridLayoutFactory.swtDefaults().margins(ClientSWTElements.defaultCompositeMargin()).applyTo(parent);
		Composite container = ClientSWTElements.createComposite(parent, SWT.NONE, 4);
		ClientSWTElements.gridMargin(container, 100, 50);
		components.forEach(c -> c.createComposite(container, SWT.NONE));
	}

	private void createName(Composite parent, int textStyle) {
		Composite container = ClientSWTElements.createComposite(parent, textStyle, 2, SWT.FILL, SWT.FILL);
		ClientSWTElements.createLabel(container, SWT.NONE).setText(getMessage(ACQUISITION));
		name = ClientSWTElements.createText(container, SWT.NONE, null, null, ACQUISITION_NAME_TP,
				GridDataFactory.fillDefaults().grab(true, false).align(SWT.FILL, SWT.FILL));
	}

	private void bindElements() {
		ClientBindingElements.bindText(viewDBC, name, String.class, "name", getController().getAcquisition());
		components.forEach(DiffractionCompositeInterface::bindControls);
	}

	private ScanningParameters getTemplateData() {
		return getController().getAcquisition().getAcquisitionConfiguration().getAcquisitionParameters();
	}

	private class LoadListener implements ApplicationListener<AcquisitionConfigurationResourceLoadEvent> {

		private final Composite composite;

		public LoadListener(Composite composite) {
			super();
			this.composite = composite;
		}

		@Override
		public void onApplicationEvent(AcquisitionConfigurationResourceLoadEvent event) {
			bindElements();
			composite.layout(true, true);
		}
	}

	/**
	 * This is triggered when a shape selection takes place to dispose of the mapping bean bindings so that they can be
	 * replaced with a new set that relate to the newly chosen shape. Thus this will be the case at startup and also if
	 * a scan is loaded and if the settings are changed by a different actor on the mapping bean.
	 *
	 * The scan path is set to the default value for the selected shape before updating the bindings for both region and
	 * path. This is done whilst the controllers region selector listener is not linked.
	 */
	private final void updateView(RegionPathState regionPathState) {
		selectedMSRSObservable.removeValueChangeListener(rapController.getRegionSelectorListener());
		updateScanPathBindings();
		selectedMSRSObservable.addValueChangeListener(rapController.getRegionSelectorListener());
		getMap().ifPresent(pl -> pl.addTraceListener(iTraceListener));
	}

	private ITraceListener iTraceListener = new ITraceListener.Stub() {
		@Override
		public void traceAdded(TraceEvent evt) {
			super.traceAdded(evt);
			templateHelper.updateTemplateData();
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
		IScanPointGeneratorModel newPathValue = rapController.getScanPathListAndLinkPath().get(0);
		regionDBC.dispose();
		rapController.changePath(newPathValue);

		Optional<ShapeType> shapeType = shapeFromMappingRegion(rapController.getScanRegionShape());
		shapeType.ifPresent(sh -> components.forEach(c -> c.updateScanPointBindings(newPathValue, sh)));
	}

	private Optional<IPlottingSystem<Composite>> getMap() {
		return Optional
				.ofNullable(PlatformUI.getWorkbench().getService(IPlottingService.class).getPlottingSystem("Map"));
	}
}
