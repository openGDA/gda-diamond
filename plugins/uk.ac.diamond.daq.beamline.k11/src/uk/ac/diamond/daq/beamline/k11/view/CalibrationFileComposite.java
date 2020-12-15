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
import static uk.ac.gda.ui.tool.ClientMessages.EMPTY_MESSAGE;
import static uk.ac.gda.ui.tool.ClientMessages.REMOVE_SELECTION_TP;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientCompositeWithGridLayout;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGridDataFactory;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientLabel;

import java.net.MalformedURLException;
import java.net.URL;
import java.util.Optional;

import org.apache.commons.io.FilenameUtils;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.FileDialog;
import org.eclipse.swt.widgets.Label;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.rcp.views.CompositeFactory;
import uk.ac.diamond.daq.experiment.structure.URLFactory;
import uk.ac.gda.client.UIHelper;
import uk.ac.gda.client.composites.ButtonGroupFactoryBuilder;
import uk.ac.gda.core.tool.spring.AcquisitionFileContext;
import uk.ac.gda.core.tool.spring.DiffractionContextFile;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.images.ClientImages;

/**
 * Selects and uploads configuration files.
 * <p>
 * Displays two buttons one for select a file from the {@link DiffractionContextFile#DIFFRACTION_CALIBRATION_DIRECTORY} another to
 * save a file in the same directory
 * </p>
 *
 * @author Maurizio Nagni
 */
public class CalibrationFileComposite implements CompositeFactory {

	private static final Logger logger = LoggerFactory.getLogger(CalibrationFileComposite.class);
	private static final String NO_FILE_SELECTED = "No File selected";

	private static final URLFactory urlFactory = new URLFactory();

	private Composite container;

	private Label calibrationFileName;

	@Override
	public Composite createComposite(Composite parent, int style) {
		container = createClientCompositeWithGridLayout(parent, style, 1);
		createClientGridDataFactory().applyTo(container);

		ButtonGroupFactoryBuilder builder = new ButtonGroupFactoryBuilder();
		builder.addButton(ClientMessages.EMPTY_MESSAGE, ClientMessages.LOAD_CALIBRATION_FILE_TP,
				widgetSelectedAdapter(this::load), ClientImages.ADD);
		builder.addButton(ClientMessages.EMPTY_MESSAGE, ClientMessages.ADD_CALIBRATION_FILE_TP,
				widgetSelectedAdapter(this::save), ClientImages.SAVE);
		builder.addButton(ClientMessages.EMPTY_MESSAGE, REMOVE_SELECTION_TP,
				widgetSelectedAdapter(this::removeDefaultCalibrationFile), ClientImages.DELETE);

		builder.build().createComposite(container, SWT.NONE);

		calibrationFileName = createClientLabel(container, style, EMPTY_MESSAGE);
		calibrationFileName.setText(NO_FILE_SELECTED);

		return container;
	}

	private void load(SelectionEvent event) {
		FileDialog fileDialog = new FileDialog(container.getShell(), SWT.OPEN);
		Optional.ofNullable(getCalibrationDirectory()).map(URL::getFile).ifPresent(fileDialog::setFilterPath);
		String[] filterExtensions = new String[] { "*.nxs" };
		fileDialog.setFilterExtensions(filterExtensions);
		Optional.ofNullable(fileDialog.open()).map(this::generateURL).ifPresent(this::setDefaultCalibrationFile);
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

	private void setDefaultCalibrationFile(URL defaultCalibrationFile) {
		getClientContext().getDiffractionContext()
			.putFileInContext(DiffractionContextFile.DIFFRACTION_DEFAULT_CALIBRATION, defaultCalibrationFile);
		updateCalibrationFileNameComponent();
	}

	private void removeDefaultCalibrationFile(SelectionEvent event) {
		getClientContext().getDiffractionContext()
			.removeFileFromContext(DiffractionContextFile.DIFFRACTION_DEFAULT_CALIBRATION);
		updateCalibrationFileNameComponent();
	}

	private void updateCalibrationFileNameComponent() {
		calibrationFileName.setText(NO_FILE_SELECTED);
		URL url = getClientContext().getDiffractionContext().getContextFile(DiffractionContextFile.DIFFRACTION_DEFAULT_CALIBRATION);
		if (url == null) {
			calibrationFileName.setText(NO_FILE_SELECTED);
		} else {
			calibrationFileName.setText(FilenameUtils.getName(url.getFile()));
		}
		calibrationFileName.getParent().layout(true, true);
	}


	private void save(SelectionEvent event) {
		UIHelper.showWarning("Not working", "Feature still not activated");
	}

	private AcquisitionFileContext getClientContext() {
		return SpringApplicationContextFacade.getBean(AcquisitionFileContext.class);
	}

	private URL getCalibrationDirectory() {
		return getClientContext().getDiffractionContext().getContextFile(DiffractionContextFile.DIFFRACTION_CALIBRATION_DIRECTORY);
	}
}
