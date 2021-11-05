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

import gda.jython.JythonServerFacade;
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

	private JythonServerFacade jythonServerFacade;

	public void initalize() {
		databaseService = Activator.getService(IXpdfDatabaseService.class);
		Objects.requireNonNull(databaseService, "Could not get ISPyB database. Are properties set correctly?");
		Objects.requireNonNull(jythonServerFacade, "No Jython server facade set. Check Spring config");
		logger.info("Initalized task runner");
	}

	/**
	 * Looks up the experimental parameters, sample and data collection plans specified and calls into a Jython function with them.
	 */
	// TODO would be nice to remove the need for proposalCode and proposalNumber number I think sampleId and
	// dataCollectionPlanId should be sufficient if the API is improved.
	@Override
	public void runTask(String proposalCode, long proposalNumber, long sampleId, long dataCollectionPlanId) {
		logger.trace("runTask(proposalCode={},proposalNumber={}, sampleId={}, dataCollectionPlanId={})",
								proposalCode, proposalNumber, sampleId, dataCollectionPlanId);

		if (databaseService == null) {
			throw new IllegalStateException("No databaseService is avaliable");
		}

		if (jythonServerFacade.getFromJythonNamespace(JYTHON_FUNCTION_NAME) == null) {
			throw new IllegalStateException("No '"+JYTHON_FUNCTION_NAME+"' function in the Jython namespace");
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
		final PyObject wrappedSample = PyJavaType.wrapJavaObject(sample);
		final PyObject wrappedDataCollectionPlans = PyJavaType.wrapJavaObject(dataCollectionPlans);
		final PyObject[] jythonArgs = new PyObject[]{wrappedSample, wrappedDataCollectionPlans};

		logger.trace("Calling {}({}, {})", JYTHON_FUNCTION_NAME, wrappedSample, wrappedDataCollectionPlans);
		logger.info("Calling {} for runTask(proposalCode={},proposalNumber={}, sampleId={}, dataCollectionPlanId={})",
				JYTHON_FUNCTION_NAME, proposalCode, proposalNumber, sampleId, dataCollectionPlanId);

		final PyObject taskRunner = jythonServerFacade.eval(JYTHON_FUNCTION_NAME);

		// Call the function arguments blocking
		taskRunner.__call__(jythonArgs);

		logger.trace("Finished running {}({}, {})", JYTHON_FUNCTION_NAME, wrappedSample, wrappedDataCollectionPlans);
		logger.info("Finished running  {} for runTask(proposalCode={},proposalNumber={}, sampleId={}, dataCollectionPlanId={})",
				JYTHON_FUNCTION_NAME, proposalCode, proposalNumber, sampleId, dataCollectionPlanId);
	}

	public void setJythonServerFacade(JythonServerFacade jythonServer) {
		this.jythonServerFacade = jythonServer;
	}
}
