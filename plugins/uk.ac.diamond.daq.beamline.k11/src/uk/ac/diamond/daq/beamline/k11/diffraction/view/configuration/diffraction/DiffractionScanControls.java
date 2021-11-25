/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

import java.util.ArrayList;
import java.util.List;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.beans.typed.BeanProperties;
import org.eclipse.jface.databinding.swt.typed.WidgetProperties;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningAcquisition;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.gda.client.AcquisitionManager;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.Reloadable;
import uk.ac.gda.ui.tool.document.ScanningAcquisitionTemporaryHelper;

public class DiffractionScanControls implements CompositeFactory, Reloadable {

	private GridDataFactory stretch = GridDataFactory.swtDefaults().align(SWT.FILL, SWT.CENTER).grab(true, false);

	private Text name;

	private DataBindingContext bindingContext = new DataBindingContext();

	private List<Reloadable> reloadableControls = new ArrayList<>();

	private AcquisitionManager acquisitionManager;


	public DiffractionScanControls(AcquisitionManager acquisitionManager) {
		this.acquisitionManager = acquisitionManager;
	}

	@Override
	public Composite createComposite(Composite parent, int style) {

		var composite = new Composite(parent, SWT.NONE);
		GridLayoutFactory.fillDefaults().applyTo(composite);
		stretch.applyTo(composite);

		createNameControl(composite);
		createShapeControls(composite);
		createSummary(composite);
		createProcessingSection(composite);
		return composite;
	}

	private void createNameControl(Composite parent) {
		var composite = new Composite(parent, SWT.NONE);
		stretch.applyTo(composite);
		GridLayoutFactory.swtDefaults().numColumns(2).equalWidth(true).applyTo(composite);
		new Label(composite, SWT.NONE).setText("Acquisition name");
		name = new Text(composite, SWT.BORDER);
		stretch.applyTo(name);

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

	private void createShapeControls(Composite parent) {
		var controls = new ShapeControls(this::getScanningParameters, acquisitionManager);
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

	private ScanningAcquisitionTemporaryHelper getScanningAcquisitionTemporaryHelper() {
		return SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class);
	}

	private ScanningAcquisition getAcquisition() {
		return getScanningAcquisitionTemporaryHelper().getScanningAcquisition().orElseThrow();
	}

	private ScanningParameters getScanningParameters() {
		return getScanningAcquisitionTemporaryHelper().getScanningParameters().orElseThrow();
	}

	@Override
	public void reload() {
		if (name.isDisposed()) return;
		reloadableControls.forEach(Reloadable::reload);
	}

}
