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

package uk.ac.diamond.daq.beamline.i15.api;

import org.eclipse.scanning.api.event.status.StatusBean;

public class TaskBean extends StatusBean {

	String proposalCode;
	long proposalNumber;
	long sampleId;
	long dataCollectionPlanId;

	public TaskBean() {
		// Needed for JSON deserialize
	}

	public TaskBean(String proposalCode, long proposalNumber, long sampleId, long dataCollectionPlanId) {
		super();
		this.proposalCode = proposalCode;
		this.proposalNumber = proposalNumber;
		this.sampleId = sampleId;
		this.dataCollectionPlanId = dataCollectionPlanId;
	}

	public String getProposalCode() {
		return proposalCode;
	}

	public void setProposalCode(String proposalCode) {
		this.proposalCode = proposalCode;
	}

	public long getProposalNumber() {
		return proposalNumber;
	}

	public void setProposalNumber(long proposalNumber) {
		this.proposalNumber = proposalNumber;
	}

	public long getSampleId() {
		return sampleId;
	}

	public void setSampleId(long sampleId) {
		this.sampleId = sampleId;
	}

	public long getDataCollectionPlanId() {
		return dataCollectionPlanId;
	}

	public void setDataCollectionPlanId(long dataCollectionPlanId) {
		this.dataCollectionPlanId = dataCollectionPlanId;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = super.hashCode();
		result = prime * result + (int) (dataCollectionPlanId ^ (dataCollectionPlanId >>> 32));
		result = prime * result + ((proposalCode == null) ? 0 : proposalCode.hashCode());
		result = prime * result + (int) (proposalNumber ^ (proposalNumber >>> 32));
		result = prime * result + (int) (sampleId ^ (sampleId >>> 32));
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (!super.equals(obj))
			return false;
		if (getClass() != obj.getClass())
			return false;
		TaskBean other = (TaskBean) obj;
		if (dataCollectionPlanId != other.dataCollectionPlanId)
			return false;
		if (proposalCode == null) {
			if (other.proposalCode != null)
				return false;
		} else if (!proposalCode.equals(other.proposalCode))
			return false;
		if (proposalNumber != other.proposalNumber)
			return false;
		if (sampleId != other.sampleId)
			return false;
		return true;
	}

	@Override
	public String toString() {
		return "TaskBean [proposalCode=" + proposalCode + ", proposalNumber=" + proposalNumber + ", sampleId="
				+ sampleId + ", dataCollectionPlanId=" + dataCollectionPlanId + "]";
	}

}
