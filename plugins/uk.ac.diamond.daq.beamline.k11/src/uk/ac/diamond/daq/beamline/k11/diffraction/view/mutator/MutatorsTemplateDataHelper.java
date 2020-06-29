/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.mutator;

import java.util.List;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.TemplateHelperBase;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.ui.diffraction.model.MutatorType;

public class MutatorsTemplateDataHelper extends TemplateHelperBase {

	public MutatorsTemplateDataHelper(ScanningParameters templateData) {
		super(templateData);
	}

	public void addMutator(MutatorType type, List<Number> value) {
		updateTemplate(getBuilder().addMutator(MutatorType.class.cast(type).getMscanMutator(), value));
		if (getLogger().isDebugEnabled()) {
			getLogger().debug(getTemplateData().toString());
		}
	}

	public void removeMutator(MutatorType type) {
		updateTemplate(getBuilder().removeMutator(MutatorType.class.cast(type).getMscanMutator()));
		if (getLogger().isDebugEnabled()) {
			getLogger().debug(getTemplateData().toString());
		}
	}
}
