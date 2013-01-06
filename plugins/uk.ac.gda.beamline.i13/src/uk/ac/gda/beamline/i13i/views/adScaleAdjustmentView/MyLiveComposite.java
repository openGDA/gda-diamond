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

package uk.ac.gda.beamline.i13i.views.adScaleAdjustmentView;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.FormLayout;
import org.eclipse.swt.layout.FormData;
import org.eclipse.swt.layout.FormAttachment;

public class MyLiveComposite extends Composite{

	private Composite composite;
	private LensScannableComposite lensScannableComposite;
	private AreaDetectorLiveComposite areaDetectorLiveComposite;

	public MyLiveComposite(Composite parent, int style) {
		super(parent, style);
		setLayout(new FillLayout(SWT.VERTICAL));
		Composite composite2 = new Composite(parent, SWT.NONE);
		composite2.setLayout(new GridLayout(1, false));
		
		Composite composite_1 = new Composite(composite2, SWT.NONE);
		GridDataFactory.fillDefaults().grab(true,  false).applyTo(composite_1);
		composite_1.setLayout(new GridLayout(1, false));
		
		lensScannableComposite = new LensScannableComposite(composite_1, SWT.NONE);
		GridDataFactory.fillDefaults().grab(true,  false).applyTo(lensScannableComposite);
		
		composite = new Composite(composite2, SWT.NONE);
		GridDataFactory.fillDefaults().grab(true,  false).applyTo(composite);
		composite.setLayout(new GridLayout(1, false));
		
	}

	public Composite getLiveCompositeParent() {
		return composite;
	}

	public void setADController(ADControllerImpl adControllerImpl) {
		lensScannableComposite.setLensScannable(adControllerImpl.getLensScannable());
	}

}
