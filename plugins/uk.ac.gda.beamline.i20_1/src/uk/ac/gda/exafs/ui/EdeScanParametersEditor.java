/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.ui;

import java.net.URL;

import uk.ac.gda.exafs.ui.data.EdeScanParameters;
import uk.ac.gda.richbeans.editors.RichBeanEditorPart;
import uk.ac.gda.richbeans.editors.RichBeanMultiPageEditorPart;

/**
 * @author rjw82
 *
 */
public final class EdeScanParametersEditor extends RichBeanMultiPageEditorPart {

	@Override
	public Class<?> getBeanClass() {
		return EdeScanParameters.class;
	}

	@Override
	public URL getMappingUrl() {
		return EdeScanParameters.mappingURL; // Please make sure this field is present and the mapping
	}

	@Override
	public RichBeanEditorPart getRichBeanEditorPart(String path,
			Object editingBean) {
		return new EdeScanParametersUIEditor(path, getMappingUrl(), this,
				editingBean);
	}

	@Override
	public URL getSchemaUrl() {
		return EdeScanParameters.schemaURL; // Please make sure this field is present and the schema
	}

}
