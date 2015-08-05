/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package gda.exafs.ui.preferencepages;

import org.eclipse.richbeans.widgets.wrappers.TextWrapper;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;

public class PositionerLabelComposite extends Composite {
	private TextWrapper label;

	public PositionerLabelComposite(Composite parent, int style) {
		super(parent, style);
		GridLayout gridLayout = new GridLayout();
		gridLayout.numColumns = 2;
		setLayout(gridLayout);
		Label elementNameLabel = new Label(this, SWT.NONE);
		elementNameLabel.setText("Name");
		label = new TextWrapper(this, SWT.BORDER);
		label.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false));
	}

	public TextWrapper getLabel() {
		return label;
	}

	public void selectionChanged(PositionerLabelBean selectedBean) {
		if (selectedBean != null) {
			String labelValue = (String) label.getValue();
			selectedBean.setLabel(labelValue);
		}
	}

}