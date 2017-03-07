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

package org.dawnsci.plotting.tools.profile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.io.FileUtils;
import org.apache.commons.io.FilenameUtils;
import org.dawnsci.plotting.tools.profile.model.AvgRegionToolDataModel;
import org.dawnsci.plotting.tools.profile.model.SpectraRegionDataNode;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.CheckStateChangedEvent;
import org.eclipse.jface.viewers.CheckboxTableViewer;
import org.eclipse.jface.viewers.ICheckStateListener;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.window.Window;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.DirectoryDialog;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.FileDialog;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.dialogs.ListSelectionDialog;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.scan.ede.datawriters.EdeDataConstants.RangeData;
import gda.scan.ede.datawriters.TimeResolvedDataFileHelper;

public class TimeResolvedToolPageHelper {

	private static final Logger logger = LoggerFactory.getLogger(TimeResolvedToolPageHelper.class);

	public void averageCyclesAndExport(File nexusFile, Display display, int[] availableCycles) {
		TimeResolvedDataFileHelper timeResolvedNexusFileHelper = new TimeResolvedDataFileHelper(nexusFile.getAbsolutePath());
		Integer[] availArray = new Integer[availableCycles.length];
		List<Integer> excludedList = new ArrayList<Integer>();
		for (int i = 0; i <availArray.length; i++) {
			availArray[i] = new Integer(i);
			if (availableCycles[i] == 1) {
				excludedList.add(availArray[i]);
			}
		}
		ListSelectionDialog excludedCyclesSelectionDialog =
				new ListSelectionDialog(
						display.getActiveShell(),
						availArray,
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

		excludedCyclesSelectionDialog.setInitialElementSelections(excludedList);

		if (excludedCyclesSelectionDialog.open() == Window.OK) {
			String dir = showSaveDirectory(nexusFile, display.getActiveShell());
			if (dir == null) {
				return;
			}

			Object[] selectionObj = excludedCyclesSelectionDialog.getResult();
			int[] selection = new int[selectionObj.length];
			for (int i = 0; i < selection.length; i++) {
				selection[i] = ((Integer) selectionObj[i]).intValue();
			}
			File tempFile;
			try {
				tempFile = copyAsTempFile(nexusFile);
				timeResolvedNexusFileHelper = new TimeResolvedDataFileHelper(tempFile.getAbsolutePath());
				timeResolvedNexusFileHelper.excludeCyclesInData(selection);
				// TODO Refactor
				String newFilePath = dir + File.separator + FilenameUtils.getName(tempFile.getAbsolutePath());
				Files.copy(tempFile.toPath(), Paths.get(newFilePath), StandardCopyOption.REPLACE_EXISTING);
			} catch (Exception e) {
				logger.error("Unable to save the updated cyclic data", e);
			}
		}
	}

	public void applyEnergyCalibrationToNexusFiles(File nexusFile, Display display, String energyCalibration, double[] value) throws Exception {
		Shell shell = display.getActiveShell();
		File[] selectedFiles = showMultipleFileSelectionDialog(shell, nexusFile.getParent());
		if (selectedFiles == null || selectedFiles.length < 1) {
			return;
		}
		String dirToStoreCalibratedFiles = showSaveDirectory(nexusFile, shell);
		if (dirToStoreCalibratedFiles == null) {
			return;
		}
		TimeResolvedDataFileHelper timeResolvedNexusFileHelper;
		for(File file : selectedFiles) {
			String path = DataFileHelper.copyToTempFolder(file, "calibrated");
			timeResolvedNexusFileHelper = new TimeResolvedDataFileHelper(path);
			timeResolvedNexusFileHelper.replaceEnergy(energyCalibration, value);
			FileUtils.copyFileToDirectory(new File(path), new File(dirToStoreCalibratedFiles));
		}
	}

	public static File[] showMultipleFileSelectionDialog(Shell shell, String path) {
		FileDialog fileDialog = new FileDialog(shell, SWT.MULTI);
		fileDialog.setFilterNames(new String[] { "Nexus (*.nxs)" });
		fileDialog.setFilterExtensions(new String[] { "*.nxs" });
		fileDialog.setText("Select file to apply new energy calibration...");
		String folder = path;
		fileDialog.setFilterPath(folder);
		if (fileDialog.open() != null) {
			String[] filenames = fileDialog.getFileNames();
			String filterPath = fileDialog.getFilterPath();
			File[] selectedFiles = new File[filenames.length];
			for (int i = 0; i < filenames.length; i++) {
				if (filterPath != null && filterPath.trim().length() > 0) {
					selectedFiles[i] = new File(filterPath, filenames[i]);
				} else {
					selectedFiles[i] = new File(filenames[i]);
				}
			}
			return selectedFiles;
		}
		return null;
	}

	public void averageSpectrumAndExport(File nexusFile, Display display, SpectraRegionDataNode[] spectraRegionDataNode) {
		String dirToStoreReducedFiles = showSaveDirectory(nexusFile, display.getActiveShell());
		if (dirToStoreReducedFiles == null) {
			return;
		}
		List<RangeData> rangeDataList = new ArrayList<RangeData>();
		for (SpectraRegionDataNode node : spectraRegionDataNode) {
			if (node instanceof AvgRegionToolDataModel) {
				AvgRegionToolDataModel avgNode = (AvgRegionToolDataModel) node;
				int avg = avgNode.getNoOfSpectraToAvg();
				for (int i = avgNode.getStart().getIndex(); i  < avgNode.getEnd().getIndex() + 1; i = i + avg) {
					rangeDataList.add(new RangeData(i, i + avg -1));
				}
			} else {
				rangeDataList.add(new RangeData(node.getStart().getIndex(), node.getEnd().getIndex()));
			}
		}

		File tempFile;
		try {
			tempFile = copyAsTempFile(nexusFile);
			TimeResolvedDataFileHelper timeResolvedNexusFileHelper = new TimeResolvedDataFileHelper(tempFile.getAbsolutePath());
			timeResolvedNexusFileHelper.averageSpectrumAndReplace(rangeDataList.toArray(new RangeData[]{}));
			String newFilePath = dirToStoreReducedFiles + File.separator + FilenameUtils.getName(tempFile.getAbsolutePath());
			Files.copy(tempFile.toPath(), Paths.get(newFilePath), StandardCopyOption.REPLACE_EXISTING);
		} catch (Exception e) {
			logger.error("Unable to save the updated reduced data", e);
		}
	}

	private File copyAsTempFile(File nexusFile) throws IOException {
		String path = DataFileHelper.copyToTempFolder(nexusFile, "reduced");
		return new File(path);
	}

	private String showSaveDirectory(File nexusFile, Shell shell) {
		DirectoryDialog dlg = new DirectoryDialog(shell);
		dlg.setFilterPath(nexusFile.getParent());
		dlg.setText("Select a directory to store new data files");
		return dlg.open();
	}
}
