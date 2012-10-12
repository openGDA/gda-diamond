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

package uk.ac.gda.exafs.ui.data;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.Serializable;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IFolder;

import uk.ac.gda.beans.BeansFactory;
import uk.ac.gda.beans.IRichBean;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.client.experimentdefinition.ExperimentObject;
import uk.ac.gda.client.experimentdefinition.IExperimentObject;
import uk.ac.gda.client.experimentdefinition.ui.handlers.XMLCommandHandler;

public class EDEScan extends ExperimentObject implements IExperimentObject, Serializable {

	public static final String SCANBEANTYPE = "Scan";
	public static final String OPTIONSBEANTYPE = "Options";
	public static final String TFGBEANTYPE = "TFG";

	public IScanParameters getScanParameters() throws Exception {
		if (getScanFileName() == null)
			return null;

		final IFile file = getFolder().getFile(getScanFileName());
		if (!file.exists())
			return null;
		return (IScanParameters) BeansFactory.getBean(file.getLocation().toFile());

	}

	public IRichBean getUserOptions() throws Exception {
		if (getOptionsFileName() == null)
			return null;

		final IFile file = getFolder().getFile(getOptionsFileName());
		if (!file.exists())
			return null;
		return BeansFactory.getBean(file.getLocation().toFile());

	}

	@Override
	public void createFilesFromTemplates() {
		final IFolder folder = getFolder();
		XMLCommandHandler xmlCH = new XMLCommandHandler();

		IFile scanFile = xmlCH.doTemplateCopy(folder, "EdeScan_Parameters.xml");
		getTypeToFileMap().put(SCANBEANTYPE, scanFile.getName());

		IFile userOptionsFile = xmlCH.doTemplateCopy(folder, "User_Options.xml");
		getTypeToFileMap().put(OPTIONSBEANTYPE, userOptionsFile.getName());
		
		IFile tfgParametersFile = xmlCH.doTemplateCopy(folder, "TFG_Parameters.xml");
		getTypeToFileMap().put(TFGBEANTYPE, tfgParametersFile.getName());

	}

	public String getScanFileName() {
		return getTypeToFileMap().get(SCANBEANTYPE);
	}

	public String getOptionsFileName() {
		return getTypeToFileMap().get(OPTIONSBEANTYPE);
	}
	
	public String getTfgParametersFileName() {
		return getTypeToFileMap().get(TFGBEANTYPE);
	}


	public void setScanFileName(String string) {
		if (string.indexOf(' ') > -1)
			throw new RuntimeException("Scan name cannot contain a space.");
		getTypeToFileMap().put(SCANBEANTYPE, string);
//		notifyListeners("ScanFileName");
	}
	
	public void setOptionsFileName(String string) {
		if (string.indexOf(' ') > -1)
			throw new RuntimeException("Options file name cannot contain a space.");
		getTypeToFileMap().put(OPTIONSBEANTYPE, string);
//		notifyListeners("OptionsFileName");
	}
	
	public void setTfgParametersFileName(String string) {
		if (string.indexOf(' ') > -1)
			throw new RuntimeException("TFG Parameters file name cannot contain a space.");
		getTypeToFileMap().put(TFGBEANTYPE, string);
//		notifyListeners("TfgParametersFileName");
	}



	@Override
	public long estimateTime() throws Exception {
		double[] times = EdeTimingCalculator.calculateTimePoints((EdeScanParameters) getScanParameters())[0].getData();
		return Math.round(times[times.length-1]*1000);
	}

	@Override
	public String getOutputPath() {
		// TODO need to add output parameters to I20-1
		return null;
	}

	@Override
	public String toPersistenceString() {
		final StringBuilder buf = new StringBuilder(getRunName());
		buf.append(" ");
		buf.append(getArgs());
		return buf.toString();
	}

	private String getArgs() {
		String buf = "'" + getScanFileName();
		buf+= "' ' ";
		buf+=getOptionsFileName();
		buf+= "' ' ";
		buf+=getTfgParametersFileName();
		buf+= "' ";
		buf+="\"" + getFolder().getName() + "\" ";
		buf+=getNumberRepetitions();
		return buf;
	}

	@Override
	public String getCommandSummaryString(boolean hasBeenStarted) {
	
		final StringBuilder buf = new StringBuilder();
		if (!hasBeenStarted){
			buf.append(getNumberRepetitions() + " repeats: ");
		}
		buf.append(getRunName());
		buf.append(" ");
		buf.append(getScanFileName());
		buf.append(" ");
		buf.append(getOptionsFileName());
		buf.append(" ");
		buf.append(getTfgParametersFileName());
		return buf.toString();
	}
	
	@Override
	public String getCommandString() throws Exception {
		return "ede " + getArgs();

	}

//	@Override
//	public String getCommandSummaryString() {
//	
//		final StringBuilder buf = new StringBuilder(getNumberRepetitions() + " repeats: ");
//		buf.append(getRunName());
//		buf.append(" ");
//		buf.append(getScanFileName());
//		buf.append(" ");
//		buf.append(getOptionsFileName());
//		buf.append(" ");
//		buf.append(getTfgParametersFileName());
//		return buf.toString();
//	}

//	@Override
//	public String getCommandSummaryString() {
//	
//		final StringBuilder buf = new StringBuilder(getNumberRepetitions() + " repeats: ");
//		buf.append(getRunName());
//		buf.append(" ");
//		buf.append(getScanFileName());
//		buf.append(" ");
//		buf.append(getOptionsFileName());
//		buf.append(" ");
//		buf.append(getTfgParametersFileName());
//		return buf.toString();
//	}

	@Override
	public void parseEditorFile(String fileName) throws Exception {
		BufferedReader br = new BufferedReader(new FileReader(fileName));
		String line = br.readLine();
		br.close();
		String[] parts = line.split(" ");
		
		if (parts.length != 5) {
			throw new Exception("File contents incorrect! "  + fileName);
		}

		setScanFileName(parts[1]);
		setOptionsFileName(parts[2]);
		setTfgParametersFileName(parts[3]);
		setNumberRepetitions(Integer.parseInt(parts[4]));
	}	
}
