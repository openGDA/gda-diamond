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
import java.util.Objects;

import org.python.core.PyJavaType;
import org.python.core.PyObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.jython.Jython;
import uk.ac.diamond.daq.beamline.i15.database.IXpdfDatabaseService;
import uk.ac.diamond.ispyb.api.DataCollectionPlan;
import uk.ac.diamond.ispyb.api.Sample;

/**
 * Runs XPDF experiments by querying the database for the information and then calling into a Jython function to allow
 * the experimental logic to be scripted.
 *
 * @author James Mudd
 */
public class XpdfTaskRunner implements IXpdfTaskRunner {
	private static final Logger logger = LoggerFactory.getLogger(XpdfTaskRunner.class);

	/** The name of the Jython function to call to start the experiment */
	private static final String JYTHON_FUNCTION_NAME = "xpdf_runner";

	private IXpdfDatabaseService databaseService;

	private Jython jythonServer;

	public void initalize() {
		databaseService = Activator.getService(IXpdfDatabaseService.class);
		Objects.requireNonNull(databaseService, "Could not get ISPyB database. Are properties set correctly?");
		Objects.requireNonNull(jythonServer, "No Jython server set. Check Spring config");
		logger.info("Initalized task runner");
	}

	/**
	 * Looks up the experimental parameters, sample and data collection plans specified and calls into a Jython function with them.
	 */
	// TODO would be nice to remove the need for proposalCode and proposalNumber number I think sampleId and
	// dataCollectionPlanId should be sufficient if the API is improved.
	@Override
	public void runTask(String proposalCode, long proposalNumber, long sampleId, long dataCollectionPlanId) {
		logger.trace("runTask({},{},{},{})", proposalCode, proposalNumber, sampleId, dataCollectionPlanId);
		if (databaseService == null) {
			throw new IllegalStateException("No databaseService is avaliable");
		}

		// Lookup the sample from the DB
		final Sample sample = databaseService.getSampleInformation(proposalCode, proposalNumber, sampleId);
		if (sample == null) {
			throw new IllegalArgumentException("No sample found for proposal: " + proposalCode + "-" + proposalNumber + " with ID: " + sampleId);
		}

		// Get DataCollectionPlans for the sample
		final List<DataCollectionPlan> dataCollectionPlans = databaseService.retrieveDataCollectionPlansForSample(sampleId);
		if (dataCollectionPlans.isEmpty()) {
			throw new IllegalArgumentException("No data collection plans found for sample ID: " + sampleId);
		}

		// Remove the DCPs with other IDs
		dataCollectionPlans.removeIf(dcp -> !dcp.getDcPlanId().equals(dataCollectionPlanId));

		if(dataCollectionPlans.isEmpty()) {
			throw new IllegalArgumentException("No data collection plans found with ID: " + dataCollectionPlanId);
		}

		// Build the arguments to call the Jython function with
		final PyObject[] jythonArgs = new PyObject[]{PyJavaType.wrapJavaObject(sample), PyJavaType.wrapJavaObject(dataCollectionPlans)};

		// Get the function to call
		final PyObject taskRunner = jythonServer.eval(JYTHON_FUNCTION_NAME);

		logger.info("Calling '{}'", JYTHON_FUNCTION_NAME);
		logger.info("Args: {}", (Object[]) jythonArgs);
		// Call the function arguments blocking
		taskRunner.__call__(jythonArgs);
		logger.info("Finished running: {}", (Object[]) jythonArgs);
	}

	public void setJythonServer(Jython jythonServer) {
		this.jythonServer = jythonServer;
	}

}
