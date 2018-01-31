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

package uk.ac.diamond.daq.beamline.i15.database;

import java.util.List;
import java.util.Map;

import uk.ac.diamond.ispyb.api.Component;
import uk.ac.diamond.ispyb.api.ComponentLattice;
import uk.ac.diamond.ispyb.api.ContainerInfo;
import uk.ac.diamond.ispyb.api.DataCollectionPlan;
import uk.ac.diamond.ispyb.api.DataCollectionPlanInfo;
import uk.ac.diamond.ispyb.api.IspybXpdfApi;
import uk.ac.diamond.ispyb.api.PDB;
import uk.ac.diamond.ispyb.api.Sample;
import uk.ac.diamond.ispyb.api.SampleGroup;
import uk.ac.diamond.ispyb.api.SampleType;

/**
 * This is a OSGi service interface to encapsulate use of the XPDF ISPyB API.
 *
 * @see IspybXpdfApi
 * @author James Mudd
 */
public interface IXpdfDatabaseService {

	/////// Convenience API Wrapper methods ///////

	Map<Long, String> getSampleIdNames(String proposalCode, long proposalNumber);

	Sample getSampleInformation(String proposalCode, long proposalNumber, long sampleId);

	/////// Pure API Methods, these are thin wrappers around the same name API calls ///////

	List<Sample> retrieveSamplesAssignedForProposal(String proposalCode, long proposalNumber);

	List<DataCollectionPlan> retrieveDataCollectionPlansForSample(long sampleId);

	List<SampleGroup> retrieveSampleGroupsForSample(long sampleId);

	List<Sample> retrieveSamplesForSampleGroup(long sampleGroupId);

	List<Component> retrieveComponentsForSampleType(long sampleTypeId);

	List<ComponentLattice> retrieveComponentLatticesForComponent(long componentId);

	ContainerInfo retrieveContainerInfoForId(long containerId);

	SampleType retrieveSampleTypeForSample(long sampleId);

	List<PDB> retrievePDBsForComponent(long componentId);

	DataCollectionPlanInfo retrieveDataCollectionPlanInfoForSample(long sampleId);

}