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

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.Arrays;

import org.apache.commons.io.FilenameUtils;
import org.dawnsci.plotting.tools.profile.DataFileHelper;
import org.dawnsci.plotting.tools.profile.SpectraRegionDataNode;
import org.dawnsci.plotting.tools.profile.TimeResolvedToolPage;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.CheckStateChangedEvent;
import org.eclipse.jface.viewers.CheckboxTableViewer;
import org.eclipse.jface.viewers.ICheckStateListener;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.DirectoryDialog;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.dialogs.ListSelectionDialog;
import org.nexusformat.NXlink;
import org.nexusformat.NexusException;
import org.nexusformat.NexusFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.io.DataHolder;
import uk.ac.diamond.scisoft.analysis.io.LoaderFactory;
import uk.ac.gda.beamline.i20_1.utils.DataHelper;

public class TimeResolvedNexusFileHelper {

	private static final Logger logger = LoggerFactory.getLogger(TimeResolvedNexusFileHelper.class);

	private NXlink itGroupDataLink;
	private NXlink itTimeDataLink;
	private NXlink energyDataLink;

	private final String nexusfileName;
	private GdaNexusFile nexusfile;
	private String detectorNodeName;

	public TimeResolvedNexusFileHelper(String nexusfileName) {
		this.nexusfileName = nexusfileName;
	}

	// TODO Refactor this
	public void openNexusFile(String detectorNodeName) throws NexusException {
		this.detectorNodeName = detectorNodeName;
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


	void createGroupAxisDataAndLink(double[][] groupAxis) throws NexusException {
		nexusfile.makedata(EdeDataConstants.TIMINGGROUP_COLUMN_NAME, NexusFile.NX_FLOAT64, 2, new int[] { groupAxis.length,
				groupAxis[0].length });
		nexusfile.opendata(EdeDataConstants.TIMINGGROUP_COLUMN_NAME);
		itGroupDataLink = nexusfile.getdataID();
		nexusfile.putdata(groupAxis);
		nexusfile.closedata();
	}

	void createTimeAxisDataAndLink(double[] timeAxis) throws NexusException {
		nexusfile.makedata(EdeDataConstants.TIME_COLUMN_NAME, NexusFile.NX_FLOAT64, 1, new int[] { timeAxis.length });
		nexusfile.opendata(EdeDataConstants.TIME_COLUMN_NAME);
		nexusfile.putdata(timeAxis);
		nexusfile.putattr("axis", Integer.toString(1).getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("primary", "1".getBytes(), NexusFile.NX_CHAR);
		nexusfile.putattr("units", "s".getBytes(), NexusFile.NX_CHAR);
		itTimeDataLink = nexusfile.getdataID();
		nexusfile.closedata();
	}

	// TODO Calibration polynomial

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

	void updateItDataToNexusFile(double[][][] normalisedItSpectra, String fileSuffix, boolean includeRepetitionColumn)
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
					averagednormalisedItSpectra[spectrumNum][channelIndex] += normalisedItSpectra[cycle][spectrumNum][channelIndex];
				}
			}
		}

		for (int spectrumNum = 0; spectrumNum < numberOfSpectraPerCycle; spectrumNum++) {
			for (int channelIndex = 0; channelIndex < numChannelsInMCA; channelIndex++) {
				averagednormalisedItSpectra[spectrumNum][channelIndex] /= numberCycles;
			}
		}
		nexusfile.getpath();
		nexusfile.makegroup(datagroupname, "NXdata");
		nexusfile.openpath(datagroupname);
		addCycleMultipleSpectra(normalisedItSpectra, getAxisText());
		addGroupLink();
		addTimeLink();
		addEnergyLink();
		nexusfile.closegroup();

		// Adding average
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


	public void averageCyclesAndExport(File nexusFile, Display display, int cycles) {
		Integer[] intArray = new Integer[cycles];
		for (int i = 0; i <cycles; i++) {
			intArray[i] = new Integer(i);
		}
		ListSelectionDialog excludedCyclesSelectionDialog =
				new ListSelectionDialog(
						display.getActiveShell(),
						intArray,
						new ArrayContentProvider(),
						new LabelProvider(),
						"Select excluded cycles") {
			@Override
			protected void createButtonsForButtonBar(Composite parent) {
				super.createButtonsForButtonBar(parent);
				getOkButton().setEnabled(false);
			}

			@Override
			protected Control createDialogArea(Composite parent) {
				Control clientDialogArea = super.createDialogArea(parent);
				final CheckboxTableViewer viewer = getViewer();
				viewer.addCheckStateListener(new ICheckStateListener() {
					@Override
					public void checkStateChanged(CheckStateChangedEvent event) {
						getOkButton().setEnabled((viewer.getCheckedElements().length != ((Integer[]) viewer.getInput()).length) && (viewer.getCheckedElements().length > 0));
					}
				});
				return clientDialogArea;
			}
		};
		if (excludedCyclesSelectionDialog.open() == Window.OK) {
			String dir = showSaveDirectory(nexusFile, display);
			if (dir == null) {
				return;
			}

			Object[] selection = excludedCyclesSelectionDialog.getResult();
			Integer[] integerArray = Arrays.copyOf(selection, selection.length, Integer[].class);
			File tempFile;
			try {
				tempFile = copyAsTempFile(nexusFile);
				replaceData(integerArray, tempFile);
				// TODO Refactor
				String newFilePath = dir + File.separator + FilenameUtils.getName(tempFile.getAbsolutePath());
				Files.copy(tempFile.toPath(), Paths.get(newFilePath), StandardCopyOption.REPLACE_EXISTING);
			} catch (IOException e) {
				logger.error("Unable to save the updated cyclic data", e);
			}
		}
	}

	private String showSaveDirectory(File nexusFile, Display display) {
		DirectoryDialog dlg = new DirectoryDialog(display.getActiveShell());
		dlg.setFilterPath(nexusFile.getParent());
		dlg.setText("Select a directory to store new data files");
		return dlg.open();
	}

	public void averageSpectrumAndExport(File nexusFile, Display display, SpectraRegionDataNode[] spectraRegionDataNodes) {
		String dir = showSaveDirectory(nexusFile, display);
		if (dir == null) {
			return;
		}
		File tempFile;
		try {
			tempFile = copyAsTempFile(nexusFile);

		} catch (IOException e) {
			logger.error("Unable to save the data", e);
		}
	}

	private File copyAsTempFile(File nexusFile) throws IOException {
		String path = DataFileHelper.copyToTempFolder(nexusFile, "reduced");
		return new File(path);
	}

	private void replaceData(Integer[] excludedCycles, File nexusFile) {
		try {
			DataHolder holder = LoaderFactory.getData(nexusFile.getAbsolutePath());
			DoubleDataset dataset = (DoubleDataset) holder.getLazyDataset(TimeResolvedToolPage.DATA_PATH).getSlice();
			int allCycleIndex = dataset.getShape()[0];
			int[] includedCyclesIndices = new int[allCycleIndex - excludedCycles.length];
			int j = 0;
			for (int i = 0; i < allCycleIndex && j < excludedCycles.length; i++) {
				if (excludedCycles[j] == i) {
					includedCyclesIndices[j++] = i;
				}
			}
			AbstractDataset reducedAbstractData = dataset.take(includedCyclesIndices, 0);
			DoubleDataset reducedDataset = (DoubleDataset) reducedAbstractData;
			double[][] reducedAverageData = new double[reducedDataset.getShape()[1]][reducedDataset.getShape()[2]];
			if (reducedDataset.getShape()[0] > 1) {
				for (int i = 0; i < reducedDataset.getShape()[1]; i++) {
					AbstractDataset tempDataset = reducedDataset.getSlice(new int[]{0,i,0}, new int[]{reducedDataset.getShape()[0], reducedDataset.getShape()[1], reducedDataset.getShape()[2]}, new int[]{1,reducedDataset.getShape()[1],1});
					tempDataset.squeeze();
					tempDataset = tempDataset.sum(0);
					reducedAverageData[i] = ((DoubleDataset) tempDataset.idivide(reducedDataset.getShape()[0])).getData();
				}
			} else {
				reducedDataset.squeeze();
				for (int i = 0; i < reducedDataset.getShape()[0]; i++) {
					reducedAverageData[i] = ((DoubleDataset) reducedDataset.getSlice(new int[] {i, 0}, new int[] {i + 1, reducedDataset.getShape()[1]}, null)).getData();
				}
			}
			NexusFile nexusFileHandle = new NexusFile(nexusFile.getAbsolutePath(), NexusFile.NXACC_RDWR);
			String excludedStrg = DataHelper.toString(excludedCycles, ':');

			nexusFileHandle.openpath(TimeResolvedToolPage.CYCLE_AVERAGE_DATA_PATH);
			nexusFileHandle.putdata(reducedAverageData);
			nexusFileHandle.putattr("excluded", excludedStrg.getBytes(), NexusFile.NX_CHAR);
			nexusFileHandle.closedata();
			nexusFileHandle.closegroup();
			nexusFileHandle.close();

		} catch (Exception e) {
			logger.error("");
		}
	}
}
