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

package uk.ac.gda.beamline.i13i.views;

import org.eclipse.core.runtime.IConfigurationElement;
import org.eclipse.swt.widgets.Composite;

import uk.ac.gda.beamline.i13i.ADViewerImpl.I13ADControllerImpl;
import uk.ac.gda.beamline.i13i.ADViewerImpl.I13MJPEGViewComposite;
import uk.ac.gda.epics.adviewer.ADController;
import uk.ac.gda.epics.adviewer.composites.MJPeg;
import uk.ac.gda.epics.adviewer.views.MJPegView;

public class I13MJPegView extends MJPegView {
	public I13MJPegView(ADController config, IConfigurationElement configurationElement) {
		super(config, configurationElement);
		i13ADControllerImpl = (I13ADControllerImpl) config;
	}

	I13ADControllerImpl i13ADControllerImpl;
	@Override
	protected MJPeg createPartControlEx(Composite parent) throws Exception {

		I13MJPEGViewComposite i13MJPEGViewComposite = new I13MJPEGViewComposite(parent, i13ADControllerImpl.getStagesCompositeFactory() );
		i13MJPEGViewComposite.setADController(i13ADControllerImpl, this);
		return i13MJPEGViewComposite.getMJPeg();
	}

}
