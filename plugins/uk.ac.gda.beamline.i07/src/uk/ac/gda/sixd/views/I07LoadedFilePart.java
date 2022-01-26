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

package uk.ac.gda.sixd.views;

import org.dawnsci.datavis.view.parts.LoadedFilePart;

import uk.ac.gda.sixd.perspectives.I07ScanPerspective;

public class I07LoadedFilePart extends LoadedFilePart {

	private static final String ID = "uk.ac.gda.sixd.views.I07LoadedFilePart";


	public static String getId() {
		return ID;
	}

	@Override
	protected String getPerspectiveID() {
		return I07ScanPerspective.getId();
	}

}
