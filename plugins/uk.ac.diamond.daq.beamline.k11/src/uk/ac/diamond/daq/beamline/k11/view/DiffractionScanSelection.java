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

package uk.ac.diamond.daq.beamline.k11.view;

import java.net.MalformedURLException;
import java.net.URL;
import java.util.Optional;

import org.apache.commons.io.FilenameUtils;
import org.dawnsci.mapping.ui.IMapClickEvent;
import org.dawnsci.mapping.ui.MappedDataView;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.dawnsci.plotting.api.IPlottingService;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;

import gda.configuration.properties.LocalProperties;
import gda.rcp.views.AcquisitionCompositeFactoryBuilder;
import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.view.control.DiffractionPathComposite;
import uk.ac.diamond.daq.experiment.api.structure.ExperimentController;
import uk.ac.diamond.daq.experiment.api.structure.ExperimentControllerException;
import uk.ac.diamond.daq.mapping.ui.browser.MapBrowser;
import uk.ac.diamond.daq.mapping.ui.diffraction.base.DiffractionParameters;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController.DiffractionAcquisitionMode;
import uk.ac.diamond.daq.mapping.ui.experiment.file.FileScanSaver;
import uk.ac.diamond.daq.mapping.ui.experiment.file.SavedScanMetaData;
import uk.ac.diamond.daq.mapping.ui.experiment.saver.PersistenceScanSaver;
import uk.ac.diamond.daq.mapping.ui.experiment.saver.ScanSaver;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.composites.AcquisitionsBrowserCompositeFactory;
import uk.ac.gda.ui.tool.ClientBindingElements;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientMessagesUtility;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.images.ClientImages;
import uk.ac.gda.ui.tool.spring.SpringApplicationContextProxy;

public class DiffractionScanSelection extends ViewPart {

	public static final String ID = "uk.ac.diamond.daq.beamline.k11.view.DiffractionScanSelection";

	private Text name;
	private DiffractionPathComposite diffractionPathComposite;
	private ScanManagementController smController;
	private ScanSaver scanSaver;
	private Button pointAndShoot;

	private DiffractionParameters acquisitionParameters;
	//private MetadataController metadataController;
	private LayoutUtilities layoutUtils = new LayoutUtilities();

	public DiffractionScanSelection() {
		smController = PlatformUI.getWorkbench().getService(ScanManagementController.class);
		smController.initialise();
	}

	@Override
	public void createPartControl(Composite parent) {
		acquisitionParameters = new DiffractionParameters();
		AcquisitionCompositeFactoryBuilder builder = new AcquisitionCompositeFactoryBuilder();
		builder.addTopArea(getTopArea());
		builder.addBottomArea(getBottomArea());
		builder.addSaveSelectionListener(getSaveListener());
		builder.addRunSelectionListener(getRunListener());
		builder.build().createComposite(parent, SWT.NONE);

		prepareMapEvents();
	}

	/**
	 * Point&Shoot depends on {@link IMapClickEvent}s firing when users click on the map. The producer of these is
	 * registered once the {@link MappedDataView} is created; here Eclipse finds it, creating it and registering all the
	 * required components.
	 */
	private void prepareMapEvents() {
		final IWorkbenchPage page = getSite().getPage();
		page.findView(MappedDataView.ID);
	}

	@Override
	public void setFocus() {
		diffractionPathComposite.setFocus();
	}

//	private void buildAcquisitionNameComposite(Composite parent) {
//		new AcquisitionNameControlFactory().createComposite(parent, SWT.NONE);
//	}

	private void buildDiffractionPathComposite(Composite parent) {
		Group group = ClientSWTElements.createGroup(parent, 1, ClientMessages.DIFFRACTION_SCAN_PATH);
		diffractionPathComposite = new DiffractionPathComposite(group, SWT.NONE);
		diffractionPathComposite.populate();
	}

	private CompositeFactory getTopArea() {
		return (parent, style) -> {
			Composite container = ClientSWTElements.createComposite(parent, style, 2, SWT.FILL, SWT.FILL);
			ClientSWTElements.createLabel(container, SWT.NONE)
					.setText(ClientMessagesUtility.getMessage(ClientMessages.ACQUISITION));
			name = ClientSWTElements.createText(container, SWT.NONE, null, null,
					ClientMessages.ACQUISITION_NAME_TP,
					GridDataFactory.fillDefaults().grab(true, false).align(SWT.FILL, SWT.FILL));
			// buildAcquisitionNameComposite(parent);
			buildDiffractionPathComposite(parent);
			Group group = ClientSWTElements.createGroup(parent, 1, ClientMessages.POINT_AND_SHOOT);
			GridLayoutFactory.fillDefaults().applyTo(group);
			GridDataFactory.swtDefaults().align(SWT.BEGINNING, SWT.BEGINNING).applyTo(group);

			pointAndShoot = ClientSWTElements.createButton(group, SWT.NONE, ClientMessages.START,
					ClientMessages.START_POINT_AND_SHOOT_TP, ClientImages.RUN);
			pointAndShoot.addListener(SWT.Selection, e -> updateStatus());

			bindElements();
			initialiseElements();
			return parent;
		};
	}

	private void bindElements() {
		DataBindingContext dbc = new DataBindingContext();

		ClientBindingElements.bindText(dbc, name, String.class, "name", getTemplateData());
	}

	private void initialiseElements() {

	}

	private void buildSavedComposite(Composite parent) {
		Group group = ClientSWTElements.createGroup(parent, 1, ClientMessages.SAVED_SCAN_DEFINITION);
		CompositeFactory cf = new AcquisitionsBrowserCompositeFactory<SavedScanMetaData>(
				new MapBrowser(getScanSaver()));
		layoutUtils.fillGrab().applyTo(cf.createComposite(group, SWT.BORDER));
	}

	private CompositeFactory getBottomArea() {
		return (parent, style) -> {
			buildSavedComposite(parent);
			return parent;
		};
	}

	private SelectionListener getSaveListener() {
		return new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				getScanSaver().save();
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				// not needed
			}
		};
	}

	private SelectionListener getRunListener() {
		return new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				if (isPointAndShootActive()) {
					UIHelper.showWarning("Cannot run Acquisition", "Point and Shoot mode is active");
					return;
				}
				if (getExperimentController().isPresent()) {
					applyExperimentProtocol();
				} else {
					smController.submitScan(getAcquisitionName(), getTemplateData());
				}
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
				// not needed
			}
		};
	}

	private void applyExperimentProtocol() {
		getExperimentController().ifPresent(this::consumeExperiment);
	}

	private void consumeExperiment(ExperimentController exController) {
		if (!exController.isStarted()) {
			UIHelper.showError("Cannot start acquisition", "You have to start first the experiment");
			return;
		}
		URL acquisitionFolder;
		try {
			acquisitionFolder = exController
					.createAcquisitionLocation(getAcquisitionName().orElse(exController.getDefaultAcquisitionName()));
		} catch (ExperimentControllerException e) {
			UIHelper.showError("Cannot create acquisition folder", e);
			return;
		}
		URL acquisitionFile;
		try {
			String fileName = extractBase(acquisitionFolder);
			acquisitionFile = new URL(acquisitionFolder, fileName + ".nxs");
		} catch (MalformedURLException e) {
			UIHelper.showError("Cannot run acquisition", e);
			return;
		}
		smController.submitScan(acquisitionFile, getTemplateData());
	}

	private String extractBase(URL url) {
		return FilenameUtils.getBaseName(FilenameUtils.getFullPathNoEndSeparator(url.getPath()));
	}

	private ScanSaver getScanSaver() {
		if (scanSaver == null) {
			if (LocalProperties.isPersistenceServiceAvailable()) {
				scanSaver = new PersistenceScanSaver(diffractionPathComposite::load, smController);
			} else {
				scanSaver = new FileScanSaver(diffractionPathComposite::load, smController);
			}
		}
		return scanSaver;
	}

	private void updateStatus() {
		IPlottingService plottingService = PlatformUI.getWorkbench().getService(IPlottingService.class);
		IPlottingSystem<Object> mapPlottingSystem = plottingService.getPlottingSystem("Map");

		if (isPointAndShootActive()) {
			ClientSWTElements.updateButton(pointAndShoot, ClientMessages.START, ClientMessages.START_POINT_AND_SHOOT_TP,
					ClientImages.RUN);
			mapPlottingSystem.setTitle(" ");
			smController.setAcquisitionMode(null);
		} else {
			ClientSWTElements.updateButton(pointAndShoot, ClientMessages.STOP, ClientMessages.STOP_POINT_AND_SHOOT_TP,
					ClientImages.STOP);
			mapPlottingSystem.setTitle("Point and Shoot: Ctrl+Click to scan");
			smController.setAcquisitionMode(DiffractionAcquisitionMode.POINT_AND_SHOOT);
		}
	}

	private boolean isPointAndShootActive() {
		return pointAndShoot.getText().equals(ClientMessagesUtility.getMessage(ClientMessages.STOP));
	}

	private Optional<ExperimentController> getExperimentController() {
		return SpringApplicationContextProxy.getOptionalBean(ExperimentController.class);
	}

	private Optional<String> getAcquisitionName() {
		return Optional.ofNullable(getTemplateData().getName());
//		if (metadataController == null) {
//			metadataController = smController.getService(MetadataController.class);
//		}
//		if (metadataController.getAcquisitionName() == null
//				|| metadataController.getAcquisitionName().trim().length() == 0) {
//			return Optional.empty();
//		}
//		return Optional.ofNullable(metadataController.getAcquisitionName());
	}

	private DiffractionParameters getTemplateData() {
		return acquisitionParameters;
	}
}
