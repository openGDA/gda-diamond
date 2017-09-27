/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.i151.server;

import java.util.List;

import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Reference;
import org.osgi.service.component.annotations.ReferenceCardinality;
import org.python.core.PyJavaType;
import org.python.core.PyObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.factory.Finder;
import gda.jython.Jython;
import uk.ac.diamond.daq.beamline.i15.database.IXpdfDatabaseService;
import uk.ac.diamond.ispyb.api.DataCollectionPlan;
import uk.ac.diamond.ispyb.api.Sample;

/**
 * The service for starting XPDF experiments by querying the database for the information and then calling into a Jython
 * function to allow the experimental logic to be scripted.
 *
 * @author James Mudd
 */
@Component(name="XpdfTaskRunner")
public class XpdfTaskRunner implements IXpdfTaskRunner {
	private static final Logger logger = LoggerFactory.getLogger(XpdfTaskRunner.class);

	/** The name of the Jython function  to call to start the experiment */
	private static final String JYTHON_FUNCTION_NAME = "xpdf_runner";

	// @Reference // TODO when we upgrade the TP should be able to use field injection
	private IXpdfDatabaseService databaseService;

	/**
	 * Looks up the experimental parameters, sample and data collection plans specified and calls into a Jython function with them.
	 */
	// TODO would be nice to remove the need for proposalCode and proposalNumber number I think sampleId and
	// dataCollectionPlanId should be sufficient if the API is improved.
	@Override
	public void runTask(String proposalCode, long proposalNumber, long sampleId, long dataCollectionPlanId) {
		if (databaseService == null) {
			throw new IllegalStateException("No databaseService is avaliable");
		}

		// Lookup the sample from the DB
		Sample sample = databaseService.getSampleInformation(proposalCode, proposalNumber, sampleId);
		if (sample == null) {
			throw new IllegalArgumentException("No sample found for proposal: " + proposalCode + "-" + proposalNumber + " with ID: " + sampleId);
		}

		// Get DataCollectionPlans for the sample
		List<DataCollectionPlan> dataCollectionPlans = databaseService.getDataCollectionPlanForSample(sampleId);
		if (dataCollectionPlans.isEmpty()) {
			throw new IllegalArgumentException("No data collection plans found for sample ID: " + sampleId);
		}

		// Remove the DCPs with other IDs
		dataCollectionPlans.removeIf(dcp -> !dcp.getDcPlanId().equals(dataCollectionPlanId));

		if(dataCollectionPlans.isEmpty()) {
			throw new IllegalArgumentException("No data collection plans found with ID: " + dataCollectionPlanId);
		}

		// Build the arguments to call the Jython function with
		PyObject[] jythonArgs = new PyObject[]{PyJavaType.wrapJavaObject(sample), PyJavaType.wrapJavaObject(dataCollectionPlans)};

		Jython jython = Finder.getInstance().find(Jython.SERVER_NAME);
		// Get the function to call
		PyObject taskRunner = jython.eval(JYTHON_FUNCTION_NAME);

		logger.info("Calling '{}' with {}", JYTHON_FUNCTION_NAME, jythonArgs);
		// Call the function arguments blocking
		taskRunner.__call__(jythonArgs);
	}

	@Reference(cardinality=ReferenceCardinality.MANDATORY)
	public void setDatabaseService(IXpdfDatabaseService databaseService) {
		this.databaseService = databaseService;
	}

}
