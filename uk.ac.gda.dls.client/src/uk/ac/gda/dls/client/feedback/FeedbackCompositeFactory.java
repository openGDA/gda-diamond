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

package uk.ac.gda.dls.client.feedback;

import org.eclipse.swt.widgets.Composite;

import gda.rcp.views.CompositeFactory;

public class FeedbackCompositeFactory implements CompositeFactory {

	@Override
	public Composite createComposite(Composite parent, int style) {
		FeedbackComposite fc = new FeedbackComposite(parent);
		Composite c = fc.createComponents();
		return c;
	}

}
