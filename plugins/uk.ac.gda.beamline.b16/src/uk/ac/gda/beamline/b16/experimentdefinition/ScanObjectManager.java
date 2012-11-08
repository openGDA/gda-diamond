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

import org.eclipse.core.resources.IFile;
import org.eclipse.core.runtime.CoreException;

import uk.ac.gda.client.experimentdefinition.ExperimentObjectManager;
import uk.ac.gda.client.experimentdefinition.IExperimentObject;
import uk.ac.gda.client.experimentdefinition.IExperimentObjectManager;

public final class ScanObjectManager extends ExperimentObjectManager implements IExperimentObjectManager {

	@Override
	protected IExperimentObject createNewExperimentObject(String line) {
		final String[] items = line.split(" ");
		if (items.length > 5) {
			return createNewScanObject(items[0], items[1], items[2], Integer.parseInt(items[5]));
		}
		return createNewScanObject(items[0], items[1], items[2], 1);
	}

	@SuppressWarnings("unchecked")
	@Override
	public Class<IExperimentObject> getExperimentObjectType() {
		return (Class<IExperimentObject>) B16ScanObject.class.asSubclass(IExperimentObject.class);
	}

	private B16ScanObject createNewScanObject(String runName, String scanFileName, String detFileName, int numRepetitions) {
		B16ScanObject newScan = new B16ScanObject();
		newScan.setRunName(runName);
		newScan.setFolder(getContainingFolder());
		newScan.setMultiScanName(getName());
		newScan.setScanFileName(scanFileName);
		newScan.setDetectorFileName(detFileName);
		newScan.setNumberRepetitions(numRepetitions);
		return newScan;
	}

	@Override
	public IExperimentObject cloneExperiment(IExperimentObject original) {
		B16ScanObject origAsScanObj = (B16ScanObject) original;
		return createNewScanObject(original.getRunName(), origAsScanObj.getScanFileName(),
				origAsScanObj.getDetectorFileName(), original.getNumberRepetitions());
	}

	@Override
	public IExperimentObject createCopyOfExperiment(IExperimentObject original) throws CoreException {
		B16ScanObject origAsScanObj = (B16ScanObject) original;

		final String name = getUniqueName(original.getRunName());
		IFile scanFile = createCopy(origAsScanObj.getScanFile());
		IFile detFile = createCopy(origAsScanObj.getDetectorFile());
		return createNewScanObject(name, scanFile.getName(), detFile.getName(), original.getNumberRepetitions());
	}

	@Override
	public String[] getOrderedColumnBeanTypes() {
		return new String[]{B16ScanObject.SCANBEANTYPE, B16ScanObject.DETECTORBEANTYPE};
	}
}
