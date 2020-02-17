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

import org.dawnsci.mapping.ui.MappedDataView;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.ProgressBar;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.part.ViewPart;

import gda.configuration.properties.LocalProperties;
import uk.ac.diamond.daq.beamline.k11.view.control.DiffractionPathComposite;
import uk.ac.diamond.daq.beamline.k11.view.control.PathSummary;
import uk.ac.diamond.daq.mapping.ui.experiment.MappingExperimentView;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController;
import uk.ac.diamond.daq.mapping.ui.experiment.file.DescriptiveFilenameBrowserComposite;
import uk.ac.diamond.daq.mapping.ui.experiment.saver.FileScanSaver;
import uk.ac.diamond.daq.mapping.ui.experiment.saver.PersistenceScanSaver;
import uk.ac.diamond.daq.mapping.ui.experiment.saver.ScanSaver;


/**
 * A view to provide DIAD targeted simplified access to Mapping Scan definition
 * for their Diffraction detector.
 *
 * @since GDA 9.13
 */
public class DiffractionScanSelection extends ViewPart {

	private Composite panelComposite;

	private DiffractionPathComposite diffractionPathComposite;
	private PathSummary summaryHolder;
	private ScanManagementController smController;

	private LayoutUtilities layoutUtils = new LayoutUtilities();

	public DiffractionScanSelection() {
		smController = PlatformUI.getWorkbench().getService(ScanManagementController.class);
		smController.initialise();
	}

	@Override
	public void createPartControl(Composite parent) {

		GridLayoutFactory.fillDefaults().applyTo(parent);
		GridDataFactory.fillDefaults().applyTo(parent);
		parent.setBackground(Display.getDefault().getSystemColor(SWT.COLOR_WHITE));
		parent.setBackgroundMode(SWT.INHERIT_FORCE);

		ScrolledComposite scrolledComposite = new ScrolledComposite(parent, SWT.H_SCROLL | SWT.V_SCROLL);
		scrolledComposite.setExpandHorizontal(true);
		scrolledComposite.setExpandVertical(true);

		GridLayoutFactory.fillDefaults().applyTo(scrolledComposite);
		GridDataFactory.fillDefaults().grab(true, true).applyTo(scrolledComposite);

		panelComposite = layoutUtils.addGridComposite(scrolledComposite);
		panelComposite.setBackground(parent.getDisplay().getSystemColor(SWT.COLOR_WHITE));
		buildAcquisitionNameComposite();
		buildDiffractionPathComposite();
		buildExecutionComposite();
		buildSavedComposite();

		layoutUtils.horizGrab().applyTo(new Label(panelComposite, SWT.SEPARATOR | SWT.HORIZONTAL));
		buildStatusComposite();

		scrolledComposite.setContent(panelComposite);
		scrolledComposite.setMinSize(panelComposite.computeSize(SWT.DEFAULT, SWT.DEFAULT));


		final IWorkbenchPage page = getSite().getPage();
		// Ensure all the infrastructure to initialise the plotting infrastructure is instantiated
		// even though the data view and mapping experiment view are currently hidden
		page.findView(MappedDataView.ID);
		page.findView(MappingExperimentView.ID);
	}

	private void buildDiffractionPathComposite() {
		diffractionPathComposite = new DiffractionPathComposite(panelComposite, SWT.NONE);
		summaryHolder = diffractionPathComposite.populate();
	}

	private void buildAcquisitionNameComposite() {
		new AcquisitionNameControlFactory().createComposite(panelComposite, SWT.NONE);
	}

	private void buildExecutionComposite() {
		new Label(panelComposite, SWT.NONE).setText("Execution mode");

		Composite executionControl = new DiffractionExecutionControl(panelComposite, SWT.NONE, smController);
		GridLayoutFactory.fillDefaults().applyTo(executionControl);
		GridDataFactory.swtDefaults().align(SWT.FILL, SWT.TOP).applyTo(executionControl);

		addSpace(panelComposite);
	}

	private void buildSavedComposite() {
		new Label(panelComposite, SWT.NONE).setText("Saved Scan Definitions");

		final DescriptiveFilenameBrowserComposite savedComposite = new DescriptiveFilenameBrowserComposite(panelComposite, SWT.BORDER);
		savedComposite.setLayout(new GridLayout());
		layoutUtils.fillGrab().applyTo(savedComposite);
		ScanSaver scanSaver = null;
		if (LocalProperties.isPersistenceServiceAvailable()) {
			scanSaver = new PersistenceScanSaver(diffractionPathComposite::load, smController);
		} else {
			scanSaver = new FileScanSaver(diffractionPathComposite::load, smController);
		}
		savedComposite.populate(scanSaver);
	}

	private void buildStatusComposite() {
		new Label(panelComposite, SWT.NONE).setText("Status");
		final Composite statusContent = layoutUtils.addGridComposite(panelComposite);
		statusContent.setLayout(new GridLayout(2, true));

		Label exposureTime = new Label(statusContent, SWT.LEFT);
		exposureTime.setText("ExposureTime: 50ms");
		addSpace(statusContent);

		layoutUtils.addGrabbingCenteredLabel(statusContent,"Current Diffraction Scan");
		layoutUtils.addGrabbingCenteredLabel(statusContent,"Overall");

		final ProgressBar innerBar = new ProgressBar(statusContent, SWT.NONE);
		layoutUtils.fillGrab().applyTo(innerBar);
		innerBar.setSelection(20);

		final ProgressBar outerBar = new ProgressBar(statusContent, SWT.NONE);
		outerBar.setSelection(60);
		layoutUtils.fillGrab().applyTo(outerBar);

		layoutUtils.addGrabbingCenteredLabel(statusContent,"Point 50 of " + summaryHolder.getTotalPoints());
		layoutUtils.addGrabbingCenteredLabel(statusContent,"Point 12 of 20");
	}

	private Label addSpace(Composite composite) {
		return new Label(composite, SWT.NONE);
	}

	@Override
	public void setFocus() {
		panelComposite.setFocus();
	}

	@Override
	public void dispose() {
		summaryHolder = null;
		diffractionPathComposite.dispose();
		diffractionPathComposite = null;
	}
}
