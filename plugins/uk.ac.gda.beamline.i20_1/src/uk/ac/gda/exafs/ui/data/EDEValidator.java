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

package uk.ac.gda.exafs.ui.data;

import uk.ac.gda.beans.validation.AbstractValidator;
import uk.ac.gda.beans.validation.InvalidBeanException;
import uk.ac.gda.client.experimentdefinition.IExperimentObject;

public class EDEValidator extends AbstractValidator {

	private static AbstractValidator staticInstance;

	public static AbstractValidator getInstance() {
		if (staticInstance == null) staticInstance = new EDEValidator();
		return staticInstance;
	}
	
	@Override
	public void validate(IExperimentObject bean) throws InvalidBeanException {
		// pass everything for the moment.
	}

}
