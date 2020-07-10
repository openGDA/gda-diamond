/*-
 * Copyright © 2009 Diamond Light Source Ltd., Science and Technology
 * Facilities Council Daresbury Laboratory
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

package gda.analysis.io;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.io.TIFFImageLoader;

/**
 * Loads TIFF images after first running them through tiff2tiff.
 */
public class ConvertedTIFFImageLoader extends TIFFImageLoader {

	private static final Logger logger = LoggerFactory.getLogger(ConvertedTIFFImageLoader.class);

	/**
	 * @param FileName
	 * @param outputFormat [float32|uint32|uint16]
	 * @param outputCompression [none|deflate|lzw]
	 * @deprecated Use {@link TIFFImageLoader}
	 */
	@SuppressWarnings("unused")
	@Deprecated
	public ConvertedTIFFImageLoader(String FileName, String outputFormat, String outputCompression) {
		super(FileName);
		logger.warn("Deprecated: use PilatusTiffLoader or TIFFImageLoader");
	}

}
