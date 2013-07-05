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

package uk.ac.gda.exafs.ui.data;

import org.eclipse.jface.viewers.ISelection;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.IWorkbenchPart;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.eclipse.ui.forms.widgets.ScrolledForm;
import org.eclipse.ui.forms.widgets.Section;
import org.eclipse.ui.views.properties.tabbed.AbstractPropertySection;
import org.eclipse.ui.views.properties.tabbed.TabbedPropertySheetPage;

public class DetectorSetupPropertySection extends AbstractPropertySection {
	private Text txtBiasVoltage;
	private Text txtExcludedStrips;

	private FormToolkit toolkit;

	@Override
	public void createControls(Composite parent, TabbedPropertySheetPage aTabbedPropertySheetPage) {
		super.createControls(parent, aTabbedPropertySheetPage);
		toolkit = new FormToolkit(parent.getDisplay());
		ScrolledForm form = toolkit.createScrolledForm(parent);
		form.getBody().setLayout(new GridLayout());
		Section section = toolkit.createSection(form.getBody(), Section.TITLE_BAR | Section.TWISTIE);
		section.setExpanded(true);
		section.setText("Default");
		toolkit.paintBordersFor(section);
		section.setLayoutData(new GridData(GridData.FILL_BOTH));
		Composite composite = toolkit.createComposite(section, SWT.NONE);
		toolkit.paintBordersFor(composite);
		composite.setLayout(new GridLayout(2, false));
		section.setClient(composite);

		Label lblBiasVoltage = toolkit.createLabel(composite, "Bias voltage:", SWT.NONE);
		lblBiasVoltage.setLayoutData(new GridData(GridData.HORIZONTAL_ALIGN_BEGINNING, GridData.CENTER, false, false));

		txtBiasVoltage = toolkit.createText(composite, "", SWT.NONE);
		txtBiasVoltage.setText("");
		txtBiasVoltage.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));

		Label lblexcludedStrips = toolkit.createLabel(composite, "Excluded strips:", SWT.NONE);
		lblexcludedStrips.setLayoutData(new GridData(GridData.HORIZONTAL_ALIGN_BEGINNING, GridData.CENTER, false, false));

		txtExcludedStrips = toolkit.createText(composite, "", SWT.NONE);
		txtExcludedStrips.setText("");
		txtExcludedStrips.setLayoutData(new GridData(GridData.FILL, GridData.CENTER, true, false));

		Composite separator = toolkit.createCompositeSeparator(section);
		toolkit.paintBordersFor(separator);
		section.setSeparatorControl(separator);
	}

	@Override
	public void setInput(IWorkbenchPart part, ISelection selection) {
		super.setInput(part, selection);
		System.out.println("Input");
	}

	@Override
	public void refresh() {
		super.refresh();
		System.out.println("refresh");
	}
}
