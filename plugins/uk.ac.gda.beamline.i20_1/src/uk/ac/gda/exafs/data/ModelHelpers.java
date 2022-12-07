/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.data;

public class ModelHelpers {

	private ModelHelpers() {
	}

	/**
	 * Generate a class import line for use in Jython from a class object. The import string takes
	 * the format : <p>
	 * {@code from <package name> import <simple class name}
	 * @param <T>
	 * @param classObj
	 * @return import string
	 */
	public static <T> String getJythonImportCommand(Class<T> classObj) {
		return "from "+classObj.getPackageName()+" import "+classObj.getSimpleName()+"\n";
	}

}
