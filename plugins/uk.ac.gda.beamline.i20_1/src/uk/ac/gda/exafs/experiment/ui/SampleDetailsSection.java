/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.forms.widgets.ExpandableComposite;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.Section;

import uk.ac.gda.client.UIHelper;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentDataModel;

/**
 * Create 'Sample details' section, with file suffix and sample description text boxes; also create
 * binding between widget and {@link ExperimentDataModel}. </p>
 * This is common code refactored from {@link SingleSpectrumCollectionView} and {@link TimeResolvedExperimentView}
 * @since 27/4/2017
 */
public class SampleDetailsSection {

	private FormToolkit toolkit;
	private Composite experimentDetailsComposite;

	final DataBindingContext dataBindingCtx = new DataBindingContext();
	private Text suffixTextbox;
	private Text sampleDescriptionTextbox;
	private Composite parent;

	public SampleDetailsSection(Composite parent, FormToolkit toolkit) {
		this.parent = parent;
		this.toolkit = toolkit;
		createWidgets();
	}

	private void createWidgets() {
		final Section experimentDetailsSection = toolkit.createSection(parent, ExpandableComposite.NO_TITLE);
		experimentDetailsSection.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false));
		experimentDetailsComposite = toolkit.createComposite(experimentDetailsSection, SWT.NONE);
		experimentDetailsComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, true));
		experimentDetailsSection.setClient(experimentDetailsComposite);

		// File suffix and sample details
		Composite suffixNameComposite = toolkit.createComposite(experimentDetailsComposite, SWT.NONE);
		suffixNameComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		suffixNameComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		Label suffixLabel = toolkit.createLabel(suffixNameComposite, "File suffix", SWT.None);
		suffixLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		suffixTextbox = toolkit.createText(suffixNameComposite, "", SWT.BORDER);
		suffixTextbox.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));

		Composite sampleDescComposite = toolkit.createComposite(experimentDetailsComposite, SWT.NONE);
		sampleDescComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		sampleDescComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		Label sampleDescLabel = toolkit.createLabel(sampleDescComposite, "Sample details", SWT.None);
		sampleDescLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		sampleDescriptionTextbox = toolkit.createText(sampleDescComposite, "", SWT.BORDER);
		sampleDescriptionTextbox.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
	}

	/**
	 * Create binding between 'file suffix' and 'sample description' textboxes and supplied {@link ExperimentDataModel} model.
	 * @param dataModel
	 */
	public void bindWidgetsToModel(ExperimentDataModel dataModel) {
		dataBindingCtx.bindValue(WidgetProperties.text(SWT.Modify).observe(suffixTextbox),
				BeanProperties.value(ExperimentDataModel.FILE_NAME_SUFFIX_PROP_NAME).observe(dataModel));

		dataBindingCtx.bindValue(WidgetProperties.text(SWT.Modify).observe(sampleDescriptionTextbox),
				BeanProperties.value(ExperimentDataModel.SAMPLE_DETAILS_PROP_NAME).observe(dataModel));
	}

	public Text getSuffixTextbox() {
		return suffixTextbox;
	}

	public Text getSampleDescriptionTextbox() {
		return sampleDescriptionTextbox;
	}

	public Composite getMainComposite() {
		return experimentDetailsComposite;
	}
}
