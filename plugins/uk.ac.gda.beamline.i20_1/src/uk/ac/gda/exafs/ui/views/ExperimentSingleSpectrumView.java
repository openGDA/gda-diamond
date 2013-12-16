/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.ui.views;

import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.forms.widgets.Form;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.TableWrapLayout;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ExperimentSingleSpectrumView extends ViewPart {

	public static final String ID = "uk.ac.gda.exafs.ui.views.experimentSingleSpectrumView";

	private static Logger logger = LoggerFactory.getLogger(ExperimentSingleSpectrumView.class);

	private FormToolkit toolkit;
	private ScrolledForm scrolledform;

	@Override
	public void createPartControl(Composite parent) {
		toolkit = new FormToolkit(parent.getDisplay());
		scrolledform = toolkit.createScrolledForm(parent);
		Form form = scrolledform.getForm();
		form.getBody().setLayout(new TableWrapLayout());
		toolkit.decorateFormHeading(form);
		form.setText("Single spectrum");
		Composite formParent = form.getBody();

	}


	@Override
	public void setFocus() {
		scrolledform.setFocus();
	}

}
