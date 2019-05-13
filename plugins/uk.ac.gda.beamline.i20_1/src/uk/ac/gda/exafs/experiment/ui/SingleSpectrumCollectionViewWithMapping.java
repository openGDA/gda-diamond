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

package uk.ac.gda.exafs.experiment.ui;

import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.SashForm;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentModelHolder;

/**
 * Same as SingleSpectrumCollectionView apart from
 * <li> Has its own copy of SingleSpectrumCollectionModel
 * <li> Has Gui controls for setting scannable positions for multiple spectra collections.
 */
public class SingleSpectrumCollectionViewWithMapping extends SingleSpectrumCollectionView {
	private static Logger logger = LoggerFactory.getLogger(SingleSpectrumCollectionViewWithMapping.class);
	public static final String ID = "uk.ac.gda.exafs.ui.views.experimentSingleSpectrumViewWithMapping";

	private FormToolkit toolkit;
	private ScrolledForm scrolledform;
	private SingleSpectrumCollectionWidgets singleSpectrumWidgets;

	@Override
	public void createPartControl(Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());

		final SashForm parentComposite = new SashForm(parent, SWT.VERTICAL);
		parentComposite.SASH_WIDTH = 7;

		Composite composite = new Composite(parentComposite, SWT.None);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		composite.setLayout(UIHelper.createGridLayoutWithNoMargin(1,false));
		scrolledform = toolkit.createScrolledForm(composite);
		scrolledform.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		Form form = scrolledform.getForm();
		form.getBody().setLayout(new GridLayout(1, true));

		toolkit.decorateFormHeading(form);
		form.setText("Single spectrum with Mapping");
		Composite formParent = form.getBody();

		singleSpectrumWidgets = new SingleSpectrumCollectionWidgets();
		singleSpectrumWidgets.setModel(ExperimentModelHolder.INSTANCE.getSingleSpectrumExperimentMappingModel());
		singleSpectrumWidgets.setToolkit(toolkit);
		try {
			singleSpectrumWidgets.createSampleDetailsSection(formParent);
			singleSpectrumWidgets.createSampleStageSections(formParent);
			singleSpectrumWidgets.createSpectrumParametersSection(formParent);
			singleSpectrumWidgets.createEnergyCalibrationSection(formParent);
			singleSpectrumWidgets.createScannablePositionsSection(formParent);
			singleSpectrumWidgets.createStartStopScanSection(formParent);
			form.layout();
		} catch (Exception e) {
			UIHelper.showError("Unable to create controls", e.getMessage());
			logger.error("Unable to create controls", e);
		}
	}

	@Override
	public void dispose() {
		singleSpectrumWidgets.dispose();
		toolkit.dispose();
		super.dispose();
	}

	@Override
	public void setFocus() {
		scrolledform.setFocus();
	}
}
