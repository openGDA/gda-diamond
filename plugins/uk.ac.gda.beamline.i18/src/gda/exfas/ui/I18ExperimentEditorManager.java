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

package gda.exfas.ui;

import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

import org.eclipse.core.resources.IFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.i18.I18SampleParameters;
import uk.ac.gda.beans.microfocus.MicroFocusScanParameters;
import uk.ac.gda.client.experimentdefinition.ExperimentEditorManager;
import uk.ac.gda.client.experimentdefinition.ExperimentFactory;
import uk.ac.gda.client.experimentdefinition.IExperimentBeanDescription;
import uk.ac.gda.client.experimentdefinition.IExperimentEditorManager;
import uk.ac.gda.client.experimentdefinition.IExperimentObject;
import uk.ac.gda.exafs.ui.data.ScanObject;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class I18ExperimentEditorManager extends ExperimentEditorManager implements IExperimentEditorManager {

	private static final Logger logger = LoggerFactory.getLogger(I18ExperimentEditorManager.class);
	
	@Override
	protected Map<String, IFile> orderMapOfTypes(IExperimentObject ob, Map<String, IFile> mapOfTypesToFiles,
			Collection<IExperimentBeanDescription> allBeanDescriptions) {
/*
		try {
			IScanParameters theScan = ((ScanObject) ob).getScanParameters();
			if ((theScan instanceof MicroFocusScanParameters)){
				((I18SampleParameters)((ScanObject) ob).getSampleParameters()).getSampleStageParameters().setDisable(true);
			}
		} catch (Exception e) {
			// TODO Auto-generated catch block
			logger.error("TODO put description of error here", e);
		}*/
		//return super.orderMapOfTypes(ob,mapOfTypesToFiles,allBeanDescriptions);
				
		String[] typesInOrder = ExperimentFactory.getManager(ob).getOrderedColumnBeanTypes();

		HashMap<String, IFile> orderedMap = new HashMap<String, IFile>();

		for (String type : typesInOrder) {

			// Vector<String> typesDone = new Vector<String>();
			for (IExperimentBeanDescription desc : allBeanDescriptions) {
				// if (!typesDone.contains(desc.getBeanType())) {
				// for (String type : mapOfTypesToFiles.keySet()) {
				if (type.equalsIgnoreCase(desc.getBeanType()) && type.equals("Sample")) {
					try {
						IScanParameters theScan = ((ScanObject) ob).getScanParameters();						
							IFile file = mapOfTypesToFiles.get(type);
							I18SampleParameters samParameters = ((I18SampleParameters)((ScanObject) ob).getSampleParameters());
							if ((theScan instanceof MicroFocusScanParameters))
								samParameters.getSampleStageParameters().setDisable(true);
							else
								samParameters.getSampleStageParameters().setDisable(false);
							XMLHelpers.saveBean(file.getLocation().toFile(), samParameters);
						}
					catch (Exception e) {
						logger.error("Error saving bean "+desc.getName()+ "to file", e);
					}
				}
				orderedMap.put(type, mapOfTypesToFiles.get(type));
				// }
			}
		}
		return orderedMap;
	}
}
