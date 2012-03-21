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

import java.util.Map;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.runtime.CoreException;

import uk.ac.gda.client.experimentdefinition.ExperimentObjectManager;
import uk.ac.gda.client.experimentdefinition.IExperimentObject;
import uk.ac.gda.client.experimentdefinition.IExperimentObjectManager;

public class EDEObjectManager extends ExperimentObjectManager implements IExperimentObjectManager {

	@Override
	protected IExperimentObject createNewExperimentObject(String line) {

		final String[] items = line.split(" ");
		if (items.length > 3) {
			return createNewExperimentObject(items[0], items[1], items[2], items[3], Integer.parseInt(items[4]));
		}
		return createNewExperimentObject(items[0], items[1], items[2], items[3], 1);
	}

	@SuppressWarnings("unchecked")
	@Override
	public Class<IExperimentObject> getExperimentObjectType() {
		return (Class<IExperimentObject>) EDEScan.class.asSubclass(IExperimentObject.class);
	}

	@Override
	public IExperimentObject createCopyOfExperiment(IExperimentObject original) throws CoreException {

		String exptName = getUniqueName(original.getRunName());

		Map<String, IFile> bidimap = original.getFilesWithTypes();
		IFile scanFile = createCopy(bidimap.get(EDEScan.SCANBEANTYPE));
		IFile optionsFile = createCopy(bidimap.get(EDEScan.OPTIONSBEANTYPE));
		IFile tfgFile = createCopy(bidimap.get(EDEScan.TFGBEANTYPE));

		return createNewExperimentObject(exptName, scanFile.getName(), optionsFile.getName(), tfgFile.getName(),
				original.getNumberRepetitions());
	}

	@Override
	public String[] getOrderedColumnBeanTypes() {
		return new String[] { EDEScan.SCANBEANTYPE, EDEScan.OPTIONSBEANTYPE, EDEScan.TFGBEANTYPE };
	}

	@Override
	public IExperimentObject cloneExperiment(IExperimentObject original) {
		EDEScan originalAsEDEScan = (EDEScan) original;
		return createNewExperimentObject(original.getRunName(), originalAsEDEScan.getScanFileName(),
				originalAsEDEScan.getOptionsFileName(), originalAsEDEScan.getTfgParametersFileName(),
				original.getNumberRepetitions());
	}

	private IExperimentObject createNewExperimentObject(String runName, String scanFileName, String optionsFileName,
			String tfgParametersFileName, int numRepetitions) {
		EDEScan newObject = new EDEScan();
		newObject.setRunFileManager(this);
		newObject.setRunName(runName);
		newObject.setScanFileName(scanFileName);
		newObject.setOptionsFileName(optionsFileName);
		newObject.setTfgParametersFileName(tfgParametersFileName);
		newObject.setNumberRepetitions(numRepetitions);
		return newObject;
	}

}
