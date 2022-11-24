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

package uk.ac.gda.dls.client.views;

import org.eclipse.swt.widgets.Composite;

import gda.observable.IObservable;
import gda.rcp.views.CompositeFactory;

public class BatonStatusCompositeFactory implements CompositeFactory {


	private IObservable bannerProvider = null;
	private String label;

	@Override
	public Composite createComposite(Composite parent, int style) {
		BatonStatusComposite status = new BatonStatusComposite(parent, style, parent.getDisplay(), label);
		status.setBannerProvider(bannerProvider);
		return status;
	}

	public void setBannerProvider(IObservable bannerProvider) {
		this.bannerProvider = bannerProvider;
	}

	public String getLabel() {
		return label;
	}

	public void setLabel(String label) {
		this.label = label;
	}
}
