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

package gda.device.detector;

import gda.factory.FactoryException;
import gda.factory.Finder;
import gda.jython.scriptcontroller.event.ScriptProgressEvent;
import gda.observable.ObservableComponent;

import java.io.File;
import java.net.URL;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.ui.data.EdeScanParameters;

/**
 * Follows same pattern for configuring Xspress2System and Xmap detectors from xml files.
 * <p>
 * The difference for this detector is that its template is a copy of the last scan file to be run as its the scan which
 * sets the detector parameters.
 * 
 */
public class XHDetectorConfiguration extends DetectorConfiguration {

	private static final Logger logger = LoggerFactory.getLogger(XHDetectorConfiguration.class);

	private ObservableComponent controller;
	private Object edeScanParameters;

	public XHDetectorConfiguration(final ObservableComponent controller, final String path,
			final EdeScanParameters beanName) throws Exception {
		this.controller = controller;
		this.edeScanParameters = getBean(path, beanName);
	}

	@Override
	public void configure() throws FactoryException {
		try {
			// Warning concrete class used here. This code must be called on the server.
			final XHDetector xhDetector = Finder.getInstance().find(((XHDetector) edeScanParameters).getDetectorName());

			// 1. Save bean - place a copy of the scan file into the template location so on GDA restart the detector
			// goes back to the same state
			saveBeanToTemplate(edeScanParameters, new File(xhDetector.getTemplateFileName()));
			logger.info("Wrote new Ede Parameters to: " + xhDetector.getTemplateFileName());

			// 2. Tell detector to configure
			xhDetector.configure();

			String message = " The XHDetector detector configuration updated.";
			controller.notifyIObservers("Message", new ScriptProgressEvent(message));
		} catch (Exception ne) {
			logger.error("Cannot configure XHDetector", ne);
			throw new FactoryException("Cannot configure XHDetector", ne);
		}
	}

	@Override
	protected Class<? extends Object> getBeanClass() {
		return EdeScanParameters.class;
	}

	@Override
	protected URL getMappingURL() {
		return EdeScanParameters.mappingURL;
	}

	@Override
	protected URL getSchemaURL() {
		return EdeScanParameters.schemaURL;
	}

}
