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
 * Create 'Sample details' section, with file prefix and sample description text boxes; also create
 * binding between widget and {@link ExperimentDataModel}. </p>
 * This is common code refactored from {@link SingleSpectrumCollectionView} and {@link TimeResolvedExperimentView}
 * @since 27/4/2017
 */
public class SampleDetailsSection {

	private FormToolkit toolkit;
	private Composite experimentDetailsComposite;

	final DataBindingContext dataBindingCtx = new DataBindingContext();
	private Text prefixTextbox;
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

		// File prefix and sample details
		Composite prefixNameComposite = toolkit.createComposite(experimentDetailsComposite, SWT.NONE);
		prefixNameComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		prefixNameComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		Label prefixLabel = toolkit.createLabel(prefixNameComposite, "File prefix", SWT.None);
		prefixLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		prefixTextbox = toolkit.createText(prefixNameComposite, "", SWT.BORDER);
		prefixTextbox.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));

		Composite sampleDescComposite = toolkit.createComposite(experimentDetailsComposite, SWT.NONE);
		sampleDescComposite.setLayout(UIHelper.createGridLayoutWithNoMargin(2, false));
		sampleDescComposite.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
		Label sampleDescLabel = toolkit.createLabel(sampleDescComposite, "Sample details", SWT.None);
		sampleDescLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));
		sampleDescriptionTextbox = toolkit.createText(sampleDescComposite, "", SWT.BORDER);
		sampleDescriptionTextbox.setLayoutData(new GridData(SWT.FILL, SWT.BEGINNING, true, false));
	}

	/**
	 * Create binding between 'file prefix' and 'sample description' textboxes and supplied {@link ExperimentDataModel} model.
	 * @param dataModel
	 */
	public void bindWidgetsToModel(ExperimentDataModel dataModel) {
		dataBindingCtx.bindValue(WidgetProperties.text(SWT.Modify).observe(prefixTextbox),
				BeanProperties.value(ExperimentDataModel.FILE_NAME_PREFIX_PROP_NAME).observe(dataModel));

		dataBindingCtx.bindValue(WidgetProperties.text(SWT.Modify).observe(sampleDescriptionTextbox),
				BeanProperties.value(ExperimentDataModel.SAMPLE_DETAILS_PROP_NAME).observe(dataModel));
	}

	public Text getPrefixTextbox() {
		return prefixTextbox;
	}

	public Text getSampleDescriptionTextbox() {
		return sampleDescriptionTextbox;
	}

	public Composite getMainComposite() {
		return experimentDetailsComposite;
	}
}
