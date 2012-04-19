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

package uk.ac.gda.exafs.ui.controller;

import gda.jython.gui.JythonGuiConstants;
import gda.jython.scriptcontroller.ScriptExecutor;

import java.io.Serializable;
import java.util.HashMap;
import java.util.Map;

import uk.ac.gda.client.experimentdefinition.ExperimentObjectHelper;
import uk.ac.gda.client.experimentdefinition.IExperimentObject;
import uk.ac.gda.client.experimentdefinition.ui.experimentqueue.ExperimentException;
import uk.ac.gda.exafs.ui.data.EDEScan;
import uk.ac.gda.exafs.ui.data.EDEValidator;

public class EdeQueue /*extends ExperimentQueue*/ {

//	@Override
	protected boolean process(IExperimentObject run) throws ExperimentException {

		try {

			EDEValidator.getInstance().validate(run);

			String command = "import edescan; reload(edescan); edescan.ede(edescantorun,useroptionstouse)";
			ScriptExecutor.Run("EdeScriptObserver", new ExperimentObjectHelper(run), getBeans((EDEScan) run), command,
					JythonGuiConstants.TERMINALNAME);
		} catch (Exception e) {
			throw new ExperimentException(e.getMessage(), run);
		}
		return true;
	}

	private Map<String, Serializable> getBeans(final EDEScan run) throws Exception {

		final Map<String, Serializable> beans = new HashMap<String, Serializable>(2);
		beans.put("edescantorun", run.getScanParameters());
		beans.put("useroptionstouse", run.getUserOptions());
		return beans;

	}
}
