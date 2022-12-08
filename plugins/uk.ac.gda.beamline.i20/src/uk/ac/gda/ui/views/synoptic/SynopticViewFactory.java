/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

package uk.ac.gda.ui.views.synoptic;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.IConfigurationElement;
import org.eclipse.core.runtime.IExecutableExtension;
import org.eclipse.core.runtime.IExecutableExtensionFactory;
import org.eclipse.ui.part.ViewPart;

/**
 * Class to allow a specific Synoptic view to be created from a 'org.eclipse.ui.views' extension point.
 * The view to be opened is specified by either appending to the class id either :
 * <li> The name of the client side SynopticViewConfiguration object defining the view setup
 * <li> The name of the {@link HardwareDisplayComposite} class implementation that generates the view.
 * e.g. :
 * <pre>{@code
<view
    class="uk.ac.gda.ui.views.synoptic.SynopticViewFactory:uk.ac.gda.ui.views.synoptic.XesStageView"
    id="uk.ac.gda.ui.views.synoptic.xesStageView"
    name="XES Stage view"
    restorable="true">
</view>
}</pre>

   * <pre>{@code
<view
    class="uk.ac.gda.ui.views.synoptic.SynopticViewFactory:xesAnalysersView"
    id="uk.ac.gda.ui.views.synoptic.SynopticViewFactory.xesAnalysersView"
    name="XES Crystal Analyser view (new)"
    restorable="true">
</view>
}</pre>
 * The view id can then be used in a showView command in usual way.
 */
public class SynopticViewFactory implements IExecutableExtensionFactory, IExecutableExtension {

	private String classOrConfigName = "";

	@Override
	public void setInitializationData(IConfigurationElement config, String propertyName, Object data) throws CoreException {
		if (propertyName.equals("class") && data instanceof String) {
			classOrConfigName = (String) data;
		}
	}

	@Override
	public ViewPart create() {
		SynopticView synopticView = new SynopticView();
		synopticView.setClassName(classOrConfigName);
		return synopticView;
	}

}
