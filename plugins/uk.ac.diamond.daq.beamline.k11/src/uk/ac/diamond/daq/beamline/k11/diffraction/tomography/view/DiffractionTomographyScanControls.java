/*-
 * Copyright © 2022 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.tomography.view;

import static uk.ac.gda.ui.tool.ClientSWTElements.STRETCH;
import static uk.ac.gda.ui.tool.ClientSWTElements.composite;
import static uk.ac.gda.ui.tool.ClientSWTElements.innerComposite;
import static uk.ac.gda.ui.tool.ClientSWTElements.label;

import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.beans.typed.BeanProperties;
import org.eclipse.jface.databinding.swt.typed.WidgetProperties;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.ExposureControls;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.ProcessingRequestsControls;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.ScanningParametersUtils;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.ShapeControls;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.ShapeDescriptor;
import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.SummaryComposite;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent;
import uk.ac.diamond.daq.mapping.api.document.event.ScanningAcquisitionChangeEvent.UpdatedProperty;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument.Axis;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;
import uk.ac.gda.api.acquisition.AcquisitionTemplateType;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.Reloadable;
import uk.ac.gda.ui.tool.document.ScanningAcquisitionTemporaryHelper;

public class DiffractionTomographyScanControls implements Reloadable, CompositeFactory {

	private Text name;

	private DataBindingContext bindingContext = new DataBindingContext();

	private List<Reloadable> reloadableControls = new ArrayList<>();

	@Override
	public Composite createComposite(Composite parent, int style) {
		var composite = innerComposite(parent, 1, true);

		createNameControl(composite);
		createRotationControls(composite);
		createGridControls(composite);
		createExposureControls(composite);
		createProcessingSection(composite);
		createSummary(composite);
		return composite;
	}

	private void createNameControl(Composite parent) {
		var composite = composite(parent, 2);
		label(composite, "Acquisition name");

		name = new Text(composite, SWT.BORDER);
		STRETCH.applyTo(name);

		reloadableControls.add(this::createNameBinding);
		createNameBinding();
	}

	private void createNameBinding() {
		if (bindingContext != null) {
			bindingContext.dispose();
		}
		bindingContext = new DataBindingContext();
		bindingContext.bindValue(WidgetProperties.text(SWT.Modify).observe(name), BeanProperties.value("name").observe(getAcquisition()));
	}

	private void createRotationControls(Composite parent) {
		var base = composite(parent, 1, false);
		STRETCH.applyTo(new Label(base, SWT.HORIZONTAL | SWT.SEPARATOR));

		GridDataFactory.swtDefaults().span(3, 1).applyTo(label(base, "Rotation parameters"));

		var rotationControls = new SingleAxisPathControls(base, this::getRotationAxis);
		rotationControls.addIObserver(this::rotationAxisUpdated);
		reloadableControls.add(rotationControls);

		STRETCH.applyTo(new Label(base, SWT.HORIZONTAL | SWT.SEPARATOR));
	}

	private ScannableTrackDocument getRotationAxis() {
		return getScanningParameters().getScanpathDocument().getScannableTrackDocuments().stream()
				.filter(doc -> doc.getAxis().equals(Axis.THETA))
				.findFirst().orElseThrow();
	}

	private void rotationAxisUpdated(@SuppressWarnings("unused") Object source, Object argument) {
		if (argument instanceof ScannableTrackDocument rotationAxis) {
			var oldScanpathDocument = getScanningParameters().getScanpathDocument();
			var updatedAxes = ScanningParametersUtils.updateAxes(oldScanpathDocument, List.of(rotationAxis));
			var updatedScanpathDocument = new ScanpathDocument(AcquisitionTemplateType.DIFFRACTION_TOMOGRAPHY, updatedAxes, oldScanpathDocument.getMutators());
			getScanningParameters().setScanpathDocument(updatedScanpathDocument);

			SpringApplicationContextFacade.publishEvent(new ScanningAcquisitionChangeEvent(this, UpdatedProperty.PATH));
		}
	}

	private void createGridControls(Composite parent) {

		var controls = new ShapeControls(this::getScanningParameters, List.of(ShapeDescriptor.RECTANGLE));
		controls.createComposite(parent, 0);
		reloadableControls.add(controls);

	}

	private void createExposureControls(Composite parent) {
		var controls = new ExposureControls();
		controls.createComposite(parent, SWT.NONE);
		reloadableControls.add(controls);
	}

	private void createProcessingSection(Composite parent) {
		var controls = new ProcessingRequestsControls();
		controls.createComposite(parent, SWT.NONE);
		reloadableControls.add(controls);
	}

	private void createSummary(Composite parent) {
		var summary = new SummaryComposite();
		summary.createComposite(parent, SWT.IGNORE);
	}

	private ScanningParameters getScanningParameters() {
		return getScanningAcquisitionTemporaryHelper().getScanningParameters().orElseThrow();
	}

	@Override
	public void reload() {
		reloadableControls.forEach(Reloadable::reload);
	}

	private ScanningAcquisition getAcquisition() {
		return getScanningAcquisitionTemporaryHelper().getScanningAcquisition().orElseThrow();
	}

	private ScanningAcquisitionTemporaryHelper getScanningAcquisitionTemporaryHelper() {
		return SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class);
	}

}