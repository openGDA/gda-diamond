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

import gda.scan.ede.datawriters.EdeDataConstants.RangeData;
import gda.scan.ede.datawriters.TimeResolvedDataFileHelper;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

import org.apache.commons.io.FilenameUtils;
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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TimeResolvedToolPageHelper {

	private static final Logger logger = LoggerFactory.getLogger(TimeResolvedToolPageHelper.class);

	public void averageCyclesAndExport(File nexusFile, Display display) {
		TimeResolvedDataFileHelper timeResolvedNexusFileHelper = new TimeResolvedDataFileHelper(nexusFile.getAbsolutePath());
		int[] availableCycles = timeResolvedNexusFileHelper.getAvailableCycles();
		Integer[] intArray = new Integer[availableCycles.length];
		for (int i = 0; i <availableCycles.length; i++) {
			intArray[i] = new Integer(availableCycles[i]);
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

			Object[] selectionObj = excludedCyclesSelectionDialog.getResult();
			int[] selection = new int[selectionObj.length];
			for (int i = 0; i < selection.length; i++) {
				selection[i] = ((Integer) selectionObj[i]).intValue();
			}
			File tempFile;
			try {
				tempFile = copyAsTempFile(nexusFile);
				timeResolvedNexusFileHelper = new TimeResolvedDataFileHelper(tempFile.getAbsolutePath());
				timeResolvedNexusFileHelper.reduceCyclicData(selection);
				// TODO Refactor
				String newFilePath = dir + File.separator + FilenameUtils.getName(tempFile.getAbsolutePath());
				Files.copy(tempFile.toPath(), Paths.get(newFilePath), StandardCopyOption.REPLACE_EXISTING);
			} catch (Exception e) {
				logger.error("Unable to save the updated cyclic data", e);
			}
		}
	}

	public void applyEnergyToNexusFiles(File nexusFile, Display display, double[] value) throws Exception {
		File[] selectedFiles = DataFileHelper.showMultipleFileSelectionDialog(display.getActiveShell(), nexusFile.getParent());
		if (selectedFiles == null || selectedFiles.length < 1) {
			return;
		}
		String dirToStoreCalibratedFiles = showSaveDirectory(nexusFile, display);
		if (dirToStoreCalibratedFiles == null) {
			return;
		}
		TimeResolvedDataFileHelper timeResolvedNexusFileHelper;
		for(File file : selectedFiles) {
			String path = DataFileHelper.copyToTempFolder(file, "calibrated");
			timeResolvedNexusFileHelper = new TimeResolvedDataFileHelper(path);
			timeResolvedNexusFileHelper.replaceEnergy(value);
			Files.copy(Paths.get(path), Paths.get(dirToStoreCalibratedFiles), StandardCopyOption.REPLACE_EXISTING);
		}
	}

	public void averageSpectrumAndExport(File nexusFile, Display display, SpectraRegionDataNode[] spectraRegionDataNode) {
		String dirToStoreReducedFiles = showSaveDirectory(nexusFile, display);
		if (dirToStoreReducedFiles == null) {
			return;
		}
		RangeData[] rangeData = new RangeData[spectraRegionDataNode.length];
		for (int i = 0; i < spectraRegionDataNode.length; i++) {
			rangeData[i] = new RangeData(spectraRegionDataNode[i].getStart().getIndex(), spectraRegionDataNode[i].getEnd().getIndex());
		}
		File tempFile;
		try {
			tempFile = copyAsTempFile(nexusFile);
			TimeResolvedDataFileHelper timeResolvedNexusFileHelper = new TimeResolvedDataFileHelper(tempFile.getAbsolutePath());
			timeResolvedNexusFileHelper.averageSpectrumAndReplace(rangeData);
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

	private String showSaveDirectory(File nexusFile, Display display) {
		DirectoryDialog dlg = new DirectoryDialog(display.getActiveShell());
		dlg.setFilterPath(nexusFile.getParent());
		dlg.setText("Select a directory to store new data files");
		return dlg.open();
	}
}
