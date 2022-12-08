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

package gda.exafs.ui.composites;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableUtils;
import gda.factory.Finder;

import org.apache.commons.lang.ArrayUtils;
import org.eclipse.richbeans.widgets.FieldBeanComposite;
import org.eclipse.swt.widgets.Composite;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class I20SampleParametersComposite  extends FieldBeanComposite {
	private static Logger logger = LoggerFactory.getLogger(I20SampleParametersComposite.class);

	public I20SampleParametersComposite(Composite parent, int style, String listenerName) {
		super(parent, style, listenerName);
	}

	public I20SampleParametersComposite(Composite parent, int style) {
		super(parent, style);
	}

	protected String getValueAsString(String scannableName) {
		Scannable scannable = (Scannable) Finder.find(scannableName);
		if (scannable == null) {
			logger.error("Scannable " + scannableName + " cannot be found");
			return "";
		}
		String[] position;
		try {
			position = ScannableUtils.getFormattedCurrentPositionArray(scannable);
		} catch (DeviceException e) {
			logger.error("Scannable " + scannableName + " position cannot be resolved.");
			return "";
		}
		String strPosition = ArrayUtils.toString(position);
		strPosition = strPosition.substring(1, strPosition.length() - 1);
		return strPosition;
	}

}