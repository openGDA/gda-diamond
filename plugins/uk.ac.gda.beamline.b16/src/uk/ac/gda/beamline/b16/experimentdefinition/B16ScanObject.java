/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.b16.experimentdefinition;

import java.util.HashMap;
import java.util.Map;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IFolder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beans.BeansFactory;
import uk.ac.gda.beans.IRichBean;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.microfocus.MicroFocusScanParameters;
import uk.ac.gda.client.experimentdefinition.ExperimentObject;
import uk.ac.gda.client.experimentdefinition.IExperimentObject;
import uk.ac.gda.client.experimentdefinition.ui.handlers.XMLCommandHandler;

/**
 * This class looks a bit like a bean but it is not designed to be a bean. It is an interface to the .scan file. setting
 * the file names can also be committed to the file by calling the write() method.
 */
public class B16ScanObject extends ExperimentObject implements IExperimentObject {

	public static final String DETECTORBEANTYPE = "Detector";
	public static final String SCANBEANTYPE = "Scan";

	transient private static final Logger logger = LoggerFactory.getLogger(B16ScanObject.class);

	@Override
	public Map<String, IFile> getFilesWithTypes() {
		HashMap<String,String> typeToFiles = getTypeToFileMap();

		// with microfocus scans, do not have a sample parameters
		try {
			if (getScanParameters() instanceof MicroFocusScanParameters) {
				HashMap<String,String> mapCopy = new HashMap<String,String>();
				mapCopy.put(SCANBEANTYPE, typeToFiles.get(SCANBEANTYPE));
				mapCopy.put(DETECTORBEANTYPE, typeToFiles.get(DETECTORBEANTYPE));
				typeToFiles = mapCopy;
			}
		} catch (Exception e) {
			logger.error("Exception mapping xml files with type: " + e.getMessage(), e);
		}

		Map<String, IFile> targetFiles = new HashMap<String, IFile>(typeToFiles.size());
		for (Object fileType : typeToFiles.keySet()) {
			IFile file = getFolder().getFile(typeToFiles.get(fileType));
			targetFiles.put((String) fileType, file);
		}
		return targetFiles;
	}

	public IFile getScanFile() {
		if (getScanFileName() == null)
			return null;
		return getFolder().getFile(getScanFileName());
	}

	public IFile getDetectorFile() {
		if (getDetectorFileName() == null)
			return null;
		return getFolder().getFile(getDetectorFileName());
	}

	@Override
	public String toPersistenceString() {
		final StringBuilder buf = new StringBuilder(getRunName());
		buf.append(" ");
		buf.append(getScanFileName());
		buf.append(" ");
		buf.append(getDetectorFileName());
		buf.append(" ");
		buf.append(getNumberRepetitions());
		return buf.toString();
	}

	public String getScanFileName() {
		return getTypeToFileMap().get(SCANBEANTYPE);
	}

	public void setScanFileName(String fileName) {
		if (fileName.indexOf(' ') > -1)
			throw new RuntimeException("Scan name cannot contain a space.");
		getTypeToFileMap().put(SCANBEANTYPE, fileName);
//		notifyListeners("ScanFileName");
	}

	public String getDetectorFileName() {
		return getTypeToFileMap().get(DETECTORBEANTYPE);
	}

	public void setDetectorFileName(String fileName) {
		if (fileName.indexOf(' ') > -1)
			throw new RuntimeException("Detector name cannot contain a space.");
		getTypeToFileMap().put(DETECTORBEANTYPE, fileName);
//		notifyListeners("DetectorFileName");
	}

//	private String outputPath;

	@Override
	public String getOutputPath() {
		// not using output params
		return null;
	}

	/**
	 * @return true if xanes file, false if not xanes or if file cannot be found.
	 * @throws Exception
	 */
	public boolean isMicroFocus() throws Exception {
		return isDescribed(MicroFocusScanParameters.class);
	}

	private boolean isDescribed(Class<? extends IRichBean> beanClass) throws Exception {
		if (getScanFile() == null)
			return false;
		final IFile scanFile = getScanFile();
		if (!scanFile.exists())
			return false;
		return BeansFactory.isBean(scanFile.getLocation().toFile(), beanClass);
	}

	/**
	 * Returns a new bean. NOTE: Should not be used to get beans for editor, this is not the editors version but a
	 * representation of the current file.
	 * 
	 * @return a new bean from the file.
	 * @throws Exception
	 */
	public IScanParameters getScanParameters() throws Exception {
		if (getScanFileName() == null)
			return null;

		final IFile file = getFolder().getFile(getScanFileName());
		if (!file.exists())
			return null;
		return (IScanParameters) BeansFactory.getBean(file.getLocation().toFile());

	}

	/**
	 * Returns the name of the energy scannable being used.
	 * 
	 * @return name
	 * @throws Exception
	 */
	public String getScannableName() throws Exception {

		final Object params = getScanParameters();

		if (params instanceof MicroFocusScanParameters)
			return ((MicroFocusScanParameters) params).getXScannableName();

		return (String) BeansFactory.getBeanValue(params, "scannableName");
	}

	/**
	 * Returns a new bean. NOTE: Should not be used to get beans for editor, this is not the editors version but a
	 * representation of the current file.
	 * 
	 * @return a new bean from the file.
	 * @throws Exception
	 */
	public IDetectorParameters getDetectorParameters() throws Exception {
		if (getDetectorFileName() == null)
			return null;
		final IFile file = getFolder().getFile(getDetectorFileName());
		if (!file.exists())
			return null;
		return (IDetectorParameters) BeansFactory.getBean(file.getLocation().toFile());
	}

	@Override
	public long estimateTime() throws Exception {
		return 0;
	}

	@Override
	public void createFilesFromTemplates() {
		final IFolder folder = getFolder();
		XMLCommandHandler xmlCH = new XMLCommandHandler();

		IFile scanFile = xmlCH.doTemplateCopy(folder, "MicroFocus_Parameters.xml");
		getTypeToFileMap().put(SCANBEANTYPE, scanFile.getName());

		IFile detFile = xmlCH.doTemplateCopy(folder, "Detector_Parameters.xml");
		getTypeToFileMap().put(DETECTORBEANTYPE, detFile.getName());
	}

	@Override
	public String getCommandString() throws Exception {
		// TODO next time B16 use expt definition, this will need implementing
		return null;
	}

	@Override
	public void parseEditorFile(String fileName) throws Exception {
		// TODO next time B16 use expt definition, this will need implementing
	}
}
