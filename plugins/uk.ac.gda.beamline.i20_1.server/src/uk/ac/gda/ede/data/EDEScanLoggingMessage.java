/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package uk.ac.gda.ede.data;

import gda.jython.scriptcontroller.logging.ScriptControllerLogColumn;
import gda.jython.scriptcontroller.logging.ScriptControllerLoggingMessage;

public class EDEScanLoggingMessage implements ScriptControllerLoggingMessage {

	private static final long serialVersionUID = 1L;

	private final String visitID;
	private final String statusMessage;
	private final String id;
	private final String scriptName;
	private final String percentComplete;
	// private Integer frameNum;
	// private Integer scanNum;
	// private Integer groupNum;
	private final String elaspedTime;

	public EDEScanLoggingMessage(String visitID, String id, String scriptName, String statusMessage, String percentComplete,
			String elaspedTime) {
		super();
		this.visitID = visitID;
		this.statusMessage = statusMessage;
		this.id = id;
		this.scriptName = scriptName;
		this.percentComplete = percentComplete;
		// this.frameNum = frameNum;
		// this.scanNum = scanNum;
		// this.groupNum = groupNum;
		this.elaspedTime = elaspedTime;
	}

	@Override
	public float getPercentDone() {
		// if (theScan == null){
		// return 0;
		// }
		// List<TimingGroup> groups = theScan.getGroups();
		// Integer numFramesComplete = 0;
		// for (int i = 0; i < groupNum; i++){
		// TimingGroup group = groups.get(i);
		// numFramesComplete += group.getNumberOfFrames();
		// }
		// numFramesComplete += frameNum;
		// if (numFramesComplete > 0 && totalNumFrames > 0){
		// return (numFramesComplete / totalNumFrames) * 100;
		// }
		// return 0;

		String percent = percentComplete.replace("%", "").trim();
		return Float.parseFloat(percent);

	}

	@Override
	@ScriptControllerLogColumn(columnName = "Status", refresh = true, columnIndex = 1)
	public String getMsg() {
		return statusMessage;
	}

	@Override
	public String getUniqueID() {
		return id;
	}

	@Override
	public String getName() {
		return scriptName;
	}

	@ScriptControllerLogColumn(columnName = "Percent Complete", refresh = true, columnIndex = 2)
	public String getPercentComplete() {
		return percentComplete;
	}

	@ScriptControllerLogColumn(columnName = "Elapsed Time", refresh = true, columnIndex = 3)
	public String getElaspedTime() {
		return elaspedTime;
	}

	@Override
	@ScriptControllerLogColumn(columnName = "Visit ID", refresh = false, columnIndex = 0)
	public String getVisitID() {
		return visitID;
	}
}
