/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package gda.scan.ede.datawriters;

import gda.data.nexus.GdaNexusFile;

import org.nexusformat.NXlink;
import org.nexusformat.NexusException;
import org.nexusformat.NexusFile;

public class TimeResolvedNexusFileHelper {

	private NXlink itGroupDataLink;
	private NXlink itTimeDataLink;
	private NXlink energyDataLink;

	private final String nexusfileName;
	private GdaNexusFile nexusfile;
	private final String detectorNodeName;

	public TimeResolvedNexusFileHelper(String nexusfileName, String detectorNodeName) {
		this.nexusfileName = nexusfileName;
		this.detectorNodeName = detectorNodeName;
	}

	public void openNexusFile() throws NexusException {
		nexusfile = new GdaNexusFile(nexusfileName, NexusFile.NXACC_RDWR);
		updateEnergyAndCreateLink();
		nexusfile.openpath("/entry1");
	}

	public void close() throws NexusException {
		nexusfile.closegroup(); // entry 1
		nexusfile.close();
	}


	private void updateEnergyAndCreateLink() throws NexusException {
		nexusfile.openpath(getEnergyPath());
		energyDataLink = nexusfile.getdataID();
		// updateNexusFileEnergyWithPolynomialValue();
		nexusfile.closegroup();
	}


	void addGroupAxisDataAndCreateLink(double[][] groupAxis) throws NexusException {
		nexusfile.makedata(EdeDataConstants.TIMINGGROUP_COLUMN_NAME, NexusFile.NX_FLOAT64, 2, new int[] { groupAxis.length,
				groupAxis[0].length });
		nexusfile.opendata(EdeDataConstants.TIMINGGROUP_COLUMN_NAME);
		itGroupDataLink = nexusfile.getdataID();
		nexusfile.putdata(groupAxis);
		nexusfile.closedata();
	}

	void addTimeAxisDataAndCreateLink(double[] timeAxis) throws NexusException {
		nexusfile.makedata(EdeDataConstants.TIME_COLUMN_NAME, NexusFile.NX_FLOAT64, 1, new int[] { timeAxis.length });
		nexusfile.opendata(EdeDataConstants.TIME_COLUMN_NAME);
		nexusfile.putdata(timeAxis);
		nexusfile.putattr("axis", Integer.toString(1).getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("primary", "1".getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("units", "s".getBytes(), NexusFile.NX_CHAR);
		itTimeDataLink = nexusfile.getdataID();
		nexusfile.closedata();
	}

	//	private void updateNexusFileEnergyWithPolynomialValue() throws NexusException, DeviceException {
	//		if (theDetector.getEnergyCalibration() != null) {
	//			nexusfile.putattr("long_name", theDetector.getEnergyCalibration().toString().getBytes(), NexusFile.NX_CHAR);
	//		}
	//	}

	private String getEnergyPath() {
		return "/entry1/instrument/" + detectorNodeName + "/" + EdeDataConstants.ENERGY_COLUMN_NAME;
	}

	private String deriveDatagroupName(String fileSuffix) {
		String datagroupname = "";
		switch (fileSuffix) {
		case EdeTimeResolvedExperimentDataWriter.IT_RAW_AVERAGEDI0_SUFFIX:
			datagroupname = EdeTimeResolvedExperimentDataWriter.NXDATA_LN_I0_IT_WITH_AVERAGED_I0;
			break;
		case EdeTimeResolvedExperimentDataWriter.IT_RAW_FINALI0_SUFFIX:
			datagroupname = EdeTimeResolvedExperimentDataWriter.NXDATA_LN_I0_IT_WITH_FINAL_I0;
			break;
		case EdeTimeResolvedExperimentDataWriter.IT_RAW_SUFFIX:
			datagroupname = EdeTimeResolvedExperimentDataWriter.NXDATA_LN_I0_IT;
			break;
		}
		return datagroupname;
	}

	void writeItToNexus(double[][][] normalisedItSpectra, String fileSuffix, boolean includeRepetitionColumn)
			throws NexusException {

		String datagroupname = deriveDatagroupName(fileSuffix);

		if (includeRepetitionColumn) {
			addCyclicData(normalisedItSpectra, datagroupname);
		} else {
			nexusfile.makegroup(datagroupname, "NXdata");
			nexusfile.openpath(datagroupname);
			addMultipleSpectra(normalisedItSpectra[0], getAxisText());
			addGroupLink();
			addTimeLink();
			addEnergyLink();
			nexusfile.closegroup();
		}
	}

	void writeIRefToNexus(double[] normalisedIRefSpectra, boolean isFinalSpectrum) throws NexusException {

		String datagroupname = isFinalSpectrum ? "LnI0IRef_Final" : "LnI0IRef";

		nexusfile.makegroup(datagroupname, "NXdata");
		nexusfile.openpath(datagroupname);

		addSingleSpectrum(normalisedIRefSpectra, EdeDataConstants.ENERGY_COLUMN_NAME);
		addEnergyLink();
		nexusfile.closegroup(); // For datagroupname
	}

	private void addCyclicData(double[][][] normalisedItSpectra, String datagroupname)
			throws NexusException {

		String avDataGroupName = datagroupname + "_averaged";

		int numberCycles = normalisedItSpectra.length;
		int numberOfSpectraPerCycle = normalisedItSpectra[0].length;
		int numChannelsInMCA = normalisedItSpectra[0][0].length;
		double[][] averagednormalisedItSpectra = new double[numberOfSpectraPerCycle][numChannelsInMCA]; // spectrum, mca
		for (int cycle = 0; cycle < numberCycles; cycle++) {
			for (int spectrumNum = 0; spectrumNum < numberOfSpectraPerCycle; spectrumNum++) {
				for (int channelIndex = 0; channelIndex < numChannelsInMCA; channelIndex++) {
					int absoulteSpectrumNum = channelIndex + (cycle * spectrumNum);
					averagednormalisedItSpectra[absoulteSpectrumNum][channelIndex] += normalisedItSpectra[cycle][spectrumNum][channelIndex];
				}
			}
		}

		for (int spectrumNum = 0; spectrumNum < numberOfSpectraPerCycle; spectrumNum++) {
			for (int channelIndex = 0; channelIndex < numChannelsInMCA; channelIndex++) {
				averagednormalisedItSpectra[spectrumNum][channelIndex] /= numberCycles;
			}
		}

		nexusfile.makegroup(datagroupname, "NXdata");
		nexusfile.openpath(datagroupname);
		addCycleMultipleSpectra(normalisedItSpectra, getAxisText());
		addGroupLink();
		addTimeLink();
		addEnergyLink();
		nexusfile.closegroup();

		nexusfile.makegroup(avDataGroupName, "NXdata");
		nexusfile.openpath(avDataGroupName);
		addMultipleSpectra(averagednormalisedItSpectra, getAxisText());
		addGroupLink();
		addTimeLink();
		addEnergyLink();
		nexusfile.closegroup();
	}

	private void addGroupLink() throws NexusException {
		nexusfile.makenamedlink(EdeDataConstants.TIMINGGROUP_COLUMN_NAME, itGroupDataLink);
	}

	private void addTimeLink() throws NexusException {
		nexusfile.makenamedlink(EdeDataConstants.TIME_COLUMN_NAME, itTimeDataLink);
	}

	private void addEnergyLink() throws NexusException {
		nexusfile.makenamedlink(EdeDataConstants.ENERGY_COLUMN_NAME, energyDataLink);
	}

	private void addSingleSpectrum(double[] normalisedItSpectra, String axes) throws NexusException {
		nexusfile.makedata(EdeDataConstants.DATA_COLUMN_NAME, NexusFile.NX_FLOAT64, 1,
				new int[] { normalisedItSpectra.length });
		nexusfile.opendata(EdeDataConstants.DATA_COLUMN_NAME);
		nexusfile.putdata(normalisedItSpectra);
		nexusfile.putattr("signal", "1".getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("interpretation", "1".getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("axes", axes.getBytes(), NexusFile.NX_CHAR);
		nexusfile.closedata();
	}

	private void addMultipleSpectra(double[][] normalisedItSpectra, String axes)
			throws NexusException {
		nexusfile.makedata(EdeDataConstants.DATA_COLUMN_NAME, NexusFile.NX_FLOAT64, 2, new int[] {
				normalisedItSpectra.length, normalisedItSpectra[0].length });
		nexusfile.opendata(EdeDataConstants.DATA_COLUMN_NAME);
		nexusfile.putdata(normalisedItSpectra);
		nexusfile.putattr("signal", "1".getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("interpretation", "2".getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("axes", axes.getBytes(), NexusFile.NX_CHAR);
		nexusfile.closedata();
	}

	private void addCycleMultipleSpectra(double[][][] normalisedItSpectra, String axes)
			throws NexusException {
		nexusfile.makedata(EdeDataConstants.DATA_COLUMN_NAME, NexusFile.NX_FLOAT64, 3, new int[] {
				normalisedItSpectra.length, normalisedItSpectra[0].length, normalisedItSpectra[0][0].length });
		nexusfile.opendata(EdeDataConstants.DATA_COLUMN_NAME);
		nexusfile.putdata(normalisedItSpectra);
		nexusfile.putattr("signal", "1".getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("interpretation", "2".getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("axes", axes.getBytes(), NexusFile.NX_CHAR);
		nexusfile.closedata();
	}

	private String getAxisText() {
		return EdeDataConstants.ENERGY_COLUMN_NAME + ":" + EdeDataConstants.TIME_COLUMN_NAME;
	}
}
