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
import org.eclipse.scanning.api.scan.IFilePathService;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.ProgressBar;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PlatformUI;

import uk.ac.diamond.daq.beamline.k11.view.control.DiffractionPathComposite;
import uk.ac.diamond.daq.beamline.k11.view.control.PathSummary;
import uk.ac.diamond.daq.mapping.ui.experiment.MappingExperimentView;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController;
import uk.ac.diamond.daq.mapping.ui.experiment.file.DescriptiveFilenameBrowserComposite;


/**
 * A view to provide DIAD targeted simplified access to Mapping Scan definition
 * for their Diffraction detector.
 *
 * @since GDA 9.13
 */
public class DiffractionScanSelection extends LayoutUtilities {

	private Composite panelComposite;

	private DiffractionPathComposite diffractionPathComposite;
	private PathSummary summaryHolder;
	private ScanManagementController smController;

	public DiffractionScanSelection() {
		smController = PlatformUI.getWorkbench().getService(ScanManagementController.class);
		smController.initialise();
	}

	@Override
	public void createPartControl(Composite parent) {
		panelComposite = addGridComposite(parent);
		panelComposite.setBackground(parent.getDisplay().getSystemColor(SWT.COLOR_WHITE));
		buildHeaderComposite(panelComposite);
		buildDiffractionPathComposite(panelComposite);
		buildSavedComposite(panelComposite);

		horizGrab().applyTo(new Label(panelComposite, SWT.SEPARATOR | SWT.HORIZONTAL));
		buildStatusComposite(panelComposite);

		final IWorkbenchPage page = getSite().getPage();
		// Ensure all the infrastructure to initialise the plotting infrastructure is instantiated
		// even though the data view and mapping experiment view are currently hidden
		page.findView(MappedDataView.ID);
		page.findView(MappingExperimentView.ID);
	}

	private void buildHeaderComposite(final Composite parent) {
		final Composite composite = addGridComposite(parent);
		horizGrab().applyTo(composite);

		final Button freezeImageButton = new Button(composite, SWT.CHECK);
		freezeImageButton.setSelection(false);
		freezeImageButton.setToolTipText(	"Freeze the background live stream on the mapping view");
		freezeImageButton.setText("Freeze Background");
		fillGrab().applyTo(freezeImageButton);
	}

	private void buildDiffractionPathComposite(final Composite parent) {
		diffractionPathComposite = new DiffractionPathComposite(parent, SWT.NONE);
		summaryHolder = diffractionPathComposite.populate();
	}

	private void buildSavedComposite(final Composite parent) {
		new Label(parent, SWT.NONE).setText("Saved Scan Definitions");

		final DescriptiveFilenameBrowserComposite savedComposite = new DescriptiveFilenameBrowserComposite(parent, SWT.BORDER);
		savedComposite.setLayout(new GridLayout());
		fillGrab().applyTo(savedComposite);
		savedComposite.populate(smController.getService(IFilePathService.class).getVisitConfigDir(),
														diffractionPathComposite::load,
														diffractionPathComposite::save);
	}

	private void buildStatusComposite(final Composite parent) {
		new Label(parent, SWT.NONE).setText("Status");
		final Composite statusContent = addGridComposite(parent);
		statusContent.setLayout(new GridLayout(2, true));

		Label exposureTime = new Label(statusContent, SWT.LEFT);
		exposureTime.setText("ExposureTime: 50ms");
		new Label(statusContent, SWT.LEFT);

		addGrabbingCenteredLabel(statusContent,"Current Diffraction Scan");
		addGrabbingCenteredLabel(statusContent,"Overall");

		final ProgressBar innerBar = new ProgressBar(statusContent, SWT.NONE);
		fillGrab().applyTo(innerBar);
		innerBar.setSelection(20);

		final ProgressBar outerBar = new ProgressBar(statusContent, SWT.NONE);
		outerBar.setSelection(60);
		fillGrab().applyTo(outerBar);

		addGrabbingCenteredLabel(statusContent,"Point 50 of " + summaryHolder.getTotalPoints());
		addGrabbingCenteredLabel(statusContent,"Point 12 of 20");
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
