/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.view;

import static org.eclipse.swt.events.SelectionListener.widgetSelectedAdapter;

import java.net.MalformedURLException;
import java.net.URL;
import java.util.Optional;

import org.apache.commons.io.FilenameUtils;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.FileDialog;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.experiment.structure.URLFactory;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.composites.ButtonGroupFactoryBuilder;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.images.ClientImages;
import uk.ac.gda.ui.tool.spring.ClientContext;
import uk.ac.gda.ui.tool.spring.ClientContext.ContextFile;
import uk.ac.gda.ui.tool.spring.SpringApplicationContextProxy;

/**
 * Selects and uploads configuration files.
 * <p>
 * Displays two buttons one for select a file from the {@link ContextFile#DIFFRACTION_CALIBRATION_DIRECTORY} another to
 * save a file in the same directory
 * </p>
 *
 * @author Maurizio Nagni
 */
public class CalibrationFileComposite implements CompositeFactory {

	private static final Logger logger = LoggerFactory.getLogger(CalibrationFileComposite.class);

	private static final URLFactory urlFactory = new URLFactory();

	private Composite container;

	@Override
	public Composite createComposite(Composite parent, int style) {
		ButtonGroupFactoryBuilder builder = new ButtonGroupFactoryBuilder();

		builder.addButton(ClientMessages.LOAD_CALIBRATION_FILE, ClientMessages.LOAD_CALIBRATION_FILE_TP,
				widgetSelectedAdapter(this::load), ClientImages.ADD);
		builder.addButton(ClientMessages.ADD_CALIBRATION_FILE, ClientMessages.ADD_CALIBRATION_FILE_TP,
				widgetSelectedAdapter(this::save), ClientImages.SAVE);
		container = builder.build().createComposite(parent, SWT.NONE);
		return container;
	}

	private void load(SelectionEvent event) {
		load();
	}

	private void load() {
		FileDialog fileDialog = new FileDialog(container.getShell(), SWT.OPEN);
		Optional.ofNullable(getCalibrationDirectory()).map(URL::getFile).ifPresent(fileDialog::setFilterPath);
		String[] filterExtensions = new String[] { "*.nxs" };
		fileDialog.setFilterExtensions(filterExtensions);
		Optional.ofNullable(fileDialog.open()).map(this::generateURL).ifPresent(this::updateCalibrationFileReference);
	}

	/**
	 * Generates a URL from a {@code String}
	 *
	 * @param path
	 *            the location to convert
	 * @return the converted string to URL, otherwise {@code null}
	 */
	private URL generateURL(String path) {
		try {
			return urlFactory.generateUrl(path);
		} catch (MalformedURLException e) {
			return null;
		}
	}

	private void updateCalibrationFileReference(URL calibrationFile) {
		if (FilenameUtils.getPath(calibrationFile.getPath())
				.equals(FilenameUtils.getPath(getCalibrationDirectory().getPath()))) {
			getClientContext().putCalibrationFile(calibrationFile);
		} else {
			UIHelper.showError("File invalid", "You selected a file out of the specified directory");
			logger.warn("Calibration file {} update failed", calibrationFile);
		}
	}

	private void save(SelectionEvent event) {
		UIHelper.showWarning("Not working", "Feature still not activated");
	}

	private ClientContext getClientContext() {
		return SpringApplicationContextProxy.getBean(ClientContext.class);
	}

	private URL getCalibrationDirectory() {
		return getClientContext().getContextFile(ContextFile.DIFFRACTION_CALIBRATION_DIRECTORY);
	}
}
