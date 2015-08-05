/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.ui.composites;

import gda.device.detector.Roi;

import org.eclipse.richbeans.widgets.scalebox.IntegerBox;
import org.eclipse.richbeans.widgets.scalebox.ScaleBox;
import org.eclipse.richbeans.widgets.wrappers.TextWrapper;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;

/**
 * may not need - do not commit yet!
 */
public class XHROIComposite extends Composite {

	private final TextWrapper name;
	private final IntegerBox lowerLevel;
	private final IntegerBox upperLevel;

	public XHROIComposite(Composite parent, int style) {
		super(parent, style);
		this.setLayout(new GridLayout(2, true));

		Label label = new Label(this, SWT.NONE);
		label.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		label.setText("Name");
		name = new TextWrapper(this, SWT.NONE);
		name.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		//		name.addModifyListener(new ModifyListener() {
		//			@Override
		//			public void modifyText(ModifyEvent e) {
		//			}
		//		});

		label = new Label(this, SWT.NONE);
		label.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		label.setText("Min");
		lowerLevel = new IntegerBox(this, SWT.NONE);
		lowerLevel.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		lowerLevel.setMinimum(0);
		lowerLevel.setMaximum(1022);


		label = new Label(this, SWT.NONE);
		label.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		label.setText("Max");
		upperLevel = new IntegerBox(this, SWT.NONE);
		upperLevel.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		upperLevel.setMaximum(1023);
		upperLevel.setMinimum(1);
	}

	public TextWrapper getLabel(){
		return name;
	}

	public ScaleBox getLowerLevel() {
		return lowerLevel;
	}

	public ScaleBox getUpperLevel() {
		return upperLevel;
	}

	public void selectionChanged(Roi xhroi) {
		name.setValue(xhroi.getName());
		lowerLevel.setValue(xhroi.getLowerLevel());
		upperLevel.setValue(xhroi.getUpperLevel());
	}

}
