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

package uk.ac.gda.exafs.experiment.ui;

import java.io.File;
import java.nio.file.Paths;

import org.apache.commons.io.FilenameUtils;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.FileDialog;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.forms.widgets.FormToolkit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.swtdesigner.ResourceManager;

import gda.util.VisitPath;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.util.beans.BeansFactory;

/**
 * Class to add 'load' and 'save' to xml buttons to the parent composite - to allow a user to save a set of parameters currently displayed in GUI
 * into an xml file, and to load a previously saved set of parameters and set up the GUI appropriately.
 * The abstract functions {@link #saveParametersToFile} and {@link #loadParametersFromFile} handle implementation details of the of the
 * file saving and loading, as well as setup of the GUI.
 * This is used in @link {@link TimeResolvedExperimentView}, {@link SingleSpectrumCollectionView}.
 *
 */
public abstract class SaveLoadButtonsComposite {

	private static Logger logger = LoggerFactory.getLogger(SaveLoadButtonsComposite.class);

	private String lastLoadedSettingsFile = "";
	private String lastSavedSettingsFile = "";

	private FormToolkit toolkit;

	private Composite parent;

	public SaveLoadButtonsComposite(Composite parent, FormToolkit toolkit) {
		this.parent = parent;
		this.toolkit = toolkit;
		createWidgets();
	}

	/**
	 * Add buttons to :
	 * <li>Save current scan settings in gui to an xml file</li>
	 * <li>Load settings from xml and update the gui</li>
	 * @param parent parent composite
	 * @since 7/4/2017
	 */
	private void createWidgets() {
		Label spacer = toolkit.createLabel(parent, "", SWT.None);

		Composite composite = toolkit.createComposite(parent, SWT.None);
		composite.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));
		composite.setLayout(UIHelper.createGridLayoutWithNoMargin(4, true));

		//Load, save buttons
		Label loadLabel = toolkit.createLabel(composite, "Load settings", SWT.None);
		loadLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		Button loadFromXmlButton = toolkit.createButton(composite, "", SWT.PUSH);
		loadFromXmlButton.setImage(ResourceManager.getImageDescriptor(TimeResolvedExperimentView.class,	"/icons/IMG_OPEN_MARKER.png").createImage());
		loadFromXmlButton.setToolTipText("Load settings from an XML file");
		loadFromXmlButton.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, false, false));
		loadFromXmlButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				showLoadParametersDialog();
			}
		});

		Label saveLabel = toolkit.createLabel(composite, "Save settings", SWT.None);
		saveLabel.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false, false));

		Button saveToXmlButton = toolkit.createButton(composite, "", SWT.PUSH);
		saveToXmlButton.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, false, false));
		saveToXmlButton.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ETOOL_SAVE_EDIT));
		saveToXmlButton.setToolTipText("Save current GUI settings to an XML file");
		saveToXmlButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				showSaveParametersDialog();
			}
		});
	}

	private void setupFileDialog(FileDialog fileDialog, String filename) {
		// Set filename filters
		fileDialog.setFilterNames(new String[] { "xml files", "All Files (*.*)" });
		fileDialog.setFilterExtensions(new String[] { "*.xml", "*.*" });

		// Set path to file, use visit directory is filename is empty
		if (filename!=null && !filename.isEmpty()) {
			fileDialog.setFileName(filename);
			if ( (fileDialog.getStyle()&SWT.SAVE) >0) {
				fileDialog.setFilterPath(FilenameUtils.getFullPath(filename));
				fileDialog.setFileName(FilenameUtils.getName(filename));
			} else {
				fileDialog.setFileName(filename);
			}
		} else {
			fileDialog.setFilterPath(VisitPath.getVisitPath());
		}
	}

	/**
	 * Display dialog to allow parameters to be loaded from xml file and used
	 * to setup current gui.
	 */
	private void showLoadParametersDialog() {
		Display display = PlatformUI.getWorkbench().getDisplay();
		FileDialog fileDialog = new FileDialog(display.getActiveShell(), SWT.OPEN);
		setupFileDialog(fileDialog, lastLoadedSettingsFile);
		fileDialog.setText("Load scan settings");
		String filename = fileDialog.open();
		if (filename != null && !filename.isEmpty()) {
			File file = new File(filename);
			if (!file.isFile() || !file.canRead()) {
				MessageDialog.openWarning(display.getActiveShell(), "Problem loading settings from XML file",
						"Could not load settings from "+filename+" - file could not be accessed");
				return;
			}
			logger.info("Loading settings from xml file {}", filename);
			try {
				loadParametersFromFile(filename);
				lastLoadedSettingsFile = filename;
			} catch (Exception e) {
				// This would normally be caused by deserialization problem
				logger.error("Problem loading scan settings from {}", filename, e);
				MessageDialog.openWarning(display.getActiveShell(), "Problem loading settings from XML file",
						"Problem loading settings from XML file "+filename+". See log panel for more details.");
			}
		}
	}

	/**
	 * Display dialog to save current gui settings to to an xml file.
	 */
	private void showSaveParametersDialog() {
		Display display = PlatformUI.getWorkbench().getDisplay();
		try {
			FileDialog fileDialog = new FileDialog(display.getActiveShell(), SWT.SAVE);
			setupFileDialog(fileDialog, lastSavedSettingsFile);
			fileDialog.setText("Save scan settings");
			String filename = fileDialog.open();
			if (filename != null && !filename.isEmpty()) {
				logger.info("Saving scan settings to xml file {} ...", filename);
				saveParametersToFile(filename);
				lastSavedSettingsFile = filename;
				logger.info("Settings saved OK");
			}
		} catch (Exception e1) {
			logger.error("Problem saving scan settings", e1);
		}
	}

	protected boolean beanIsCorrectType(String filename, Class<?> clazz) throws Exception {
		if (!BeansFactory.isBean(Paths.get(filename).toFile(), clazz)) {
			MessageDialog.openWarning(PlatformUI.getWorkbench().getDisplay().getActiveShell(), "Problem reading from file",
					"Could not load parameters from "+filename+" - it does not contain "+clazz.getSimpleName()+" data");
			return false;
		}
		return true;
	}

	/**
	 * This function should get the parameters from the gui and save them to the named file.
	 * @param filename
	 * @throws Exception
	 */
	protected abstract void saveParametersToFile(String filename) throws Exception;

	/**
	 * This function should load the parameters from the named file and setup the gui appropriately.
	 * @param filename
	 * @throws Exception
	 */
	protected abstract void loadParametersFromFile(String filename) throws Exception;

}
