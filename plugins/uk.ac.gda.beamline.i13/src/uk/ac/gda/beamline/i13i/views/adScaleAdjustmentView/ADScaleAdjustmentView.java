/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

import org.dawb.common.ui.plot.tool.IToolPageSystem;
import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.InitializingBean;

public class ADScaleAdjustmentView extends ViewPart implements InitializingBean{
	private static final Logger logger = LoggerFactory.getLogger(ADScaleAdjustmentView.class);

	private ADScaleAdjustmentComposite adScaleAdjustmentComposite;
	ADController config;
	
	public ADScaleAdjustmentView(ADController config) {
		this.config = config;
	}

	@Override
	public void afterPropertiesSet() throws Exception {
	}

	@Override
	public void createPartControl(Composite parent) {
		parent.setLayout(new FillLayout());
		adScaleAdjustmentComposite = new ADScaleAdjustmentComposite(this, parent, SWT.NONE, config);
		try {
			adScaleAdjustmentComposite.start();
		} catch (Exception e) {
			logger.error("Error starting  adScaleAdjustmentComposite", e);
		}

	}

	@Override
	public void setFocus() {
		adScaleAdjustmentComposite.setFocus();
	}

	@Override
	public void dispose() {
		super.dispose();
		adScaleAdjustmentComposite.dispose();
	}

	@Override
	public Object getAdapter(@SuppressWarnings("rawtypes") Class clazz) {
		if (clazz == IToolPageSystem.class) {
			return this.adScaleAdjustmentComposite.getPlottingSystem();
		}
		return super.getAdapter(clazz);
	}
	
	
}
