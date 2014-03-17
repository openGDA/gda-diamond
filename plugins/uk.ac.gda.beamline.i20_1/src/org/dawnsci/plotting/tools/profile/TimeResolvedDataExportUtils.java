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
import java.util.Arrays;

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
import org.nexusformat.NexusFile;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.scisoft.analysis.dataset.AbstractDataset;
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.diamond.scisoft.analysis.io.DataHolder;
import uk.ac.diamond.scisoft.analysis.io.LoaderFactory;
import uk.ac.gda.beamline.i20_1.utils.DataHelper;

public class TimeResolvedDataExportUtils {

	private static final Logger logger = LoggerFactory.getLogger(TimeResolvedDataExportUtils.class);
	public void exportAndAverageCycles(File nexusFile, Display display, int cycles) {
		Integer[] intArray = new Integer[cycles];
		for (int i = 0; i <cycles; i++) {
			intArray[i] = new Integer(i);
		}
		ListSelectionDialog dialog =
				new ListSelectionDialog(
						display.getActiveShell(),
						intArray,
						new ArrayContentProvider(),
						new LabelProvider(),
						"Select excluded cycles") {
			@Override
			protected Control createDialogArea(Composite parent) {
				Control clientDialogArea = super.createDialogArea(parent);
				final CheckboxTableViewer viewer = getViewer();
				viewer.addCheckStateListener(new ICheckStateListener() {
					@Override
					public void checkStateChanged(CheckStateChangedEvent event) {
						getOkButton().setEnabled((viewer.getCheckedElements().length != ((Integer[]) viewer.getInput()).length) || (viewer.getCheckedElements().length > 0));
					}
				});
				return clientDialogArea;
			}
		};
		if (dialog.open() == Window.OK) {
			DirectoryDialog dlg = new DirectoryDialog(display.getActiveShell());
			dlg.setFilterPath(nexusFile.getParent());
			dlg.setText("Select a directory to store new data files");
			String dir = dlg.open();
			if (dir == null) {
				return;
			}

			Object[] selection = dialog.getResult();
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
