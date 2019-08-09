/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.resource.FontDescriptor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.FontData;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.IPerspectiveDescriptor;
import org.eclipse.ui.IPerspectiveListener;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.WorkbenchException;
import org.eclipse.ui.part.ViewPart;
import org.eclipse.ui.plugin.AbstractUIPlugin;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.common.collect.ImmutableMap;

import uk.ac.gda.tomography.model.TomographyAcquisition;
import uk.ac.gda.tomography.model.TomographyExperiment;
import uk.ac.gda.tomography.scan.editor.TomographyAcquisitionController;
import uk.ac.gda.tomography.scan.editor.TomographyResourceManager;
import uk.ac.gda.tomography.scan.editor.TomographySWTElements;
import uk.ac.gda.tomography.scan.editor.view.TomographyExperimentComposite;
import uk.ac.gda.tomography.scan.editor.view.TomographyMessages;

/**
 * The main Experiment configuration view visible in all k11 perspectives
 */
public class TomographySetup extends ViewPart {
	private static final Logger logger = LoggerFactory.getLogger(TomographySetup.class);

	private TomographyExperimentComposite experimentCompose;

	private TomographyAcquisitionController tomographyConfigurationController;

	private static final String pointAndShoot = "Point and Shoot";
	private static final String particleTracking = "Particle Tracking";
	private static final String fullyAutomated = "Fully Automated";
	private static final String tomography = "Plain Tomography";
	private static final String[] modes = new String[] { pointAndShoot, particleTracking, fullyAutomated, tomography };

	private static final Map<String, String> PERSPECTIVES_MAP = ImmutableMap.of(pointAndShoot,
			"uk.ac.diamond.daq.beamline.k11.perspective.PointAndShootPerspective", particleTracking,
			"uk.ac.diamond.daq.beamline.k11.perspective.PointAndShootPerspective", fullyAutomated,
			"uk.ac.diamond.daq.beamline.k11.perspective.FullyAutomatedPerspective", tomography,
			"uk.ac.diamond.daq.beamline.k11.perspective.TomographyPerspective");

	private static final int NOTES_BOX_LINES = 7;
	private static final int NOTES_BOX_HEIGHT = NOTES_BOX_LINES * 20;
	private static final int REDUCED_BUTTON_HEIGHT = 22;
	private static final int SCROLLABLE_WIDTH = 270;
	private static final int SCROLLABLE_HEIGHT = 900;
	private static final FontData BANNER_FONT_DATA = new FontData("Impact", 20, SWT.NONE);
	private static final int HEADING_SIZE = 14;

	private static final String ENVIRONMENT_STAGE = "TR6";
	private static final String TOMOGRAPHY_STAGE = "Tomography";
	private static final String TABEL_STAGE = "Platform";

	private final DataBindingContext dbc = new DataBindingContext();
	private final IWorkbench workbench = PlatformUI.getWorkbench();
	private final IWorkbenchWindow activeWindow = workbench.getActiveWorkbenchWindow();

	private Composite panelComposite;
	private Text nameText;
	private String mode = tomography;

	/**
	 * Creates the overall container for all things in the Experiment View tab
	 */
	@Override
	public void createPartControl(Composite parent) {
		parent.setBackground(parent.getDisplay().getSystemColor(SWT.COLOR_WIDGET_LIGHT_SHADOW));
		final Composite composite = TomographySWTElements.createComposite(parent, SWT.NONE, 1);
		TomographySWTElements.createLabel(composite, SWT.NONE, "DIAD",
				FontDescriptor.createFrom(TomographyResourceManager.getDefaultFont(), 14, SWT.BOLD));

		buildModeComposite(composite);

		experimentCompose = new TomographyExperimentComposite(composite, getExperiment());
	}

	private TomographyExperiment getExperiment() {
		// For now is just a dummy method
		TomographyExperiment experiment = new TomographyExperiment();
		experiment.setName("Default Experiment");
		List<TomographyAcquisition> acquisitions = new ArrayList<TomographyAcquisition>();

		TomographyAcquisition acquisition = TomographyAcquisitionController.createNewAcquisition();
		acquisition.setName("First Acquisition");
		acquisition.getConfiguration().setName("First Acquisition Configuraition");

		try {
			acquisition.setScript(new URL("http://goolge.com"));
		} catch (MalformedURLException e) {
			// TODO Auto-generated catch block
			logger.error("TODO put description of error here", e);
		}
		acquisitions.add(acquisition);


		acquisition = TomographyAcquisitionController.createNewAcquisition();
		acquisition.setName("Second Acquisition");
		acquisitions.add(acquisition);
		experiment.setAcquisitions(acquisitions);

		experiment.setLogs(new ArrayList<>());
		return experiment;
	}

	/**
	 * Build the {@link Composite} containing controls for selecting the experiment mode
	 *
	 * @param parent
	 *            The Experiment {@link Composite}
	 */
	private void buildModeComposite(final Composite parent) {
		TomographySWTElements.createLabel(parent, SWT.NONE, TomographyMessages.MODE);
		Combo modeCombo = TomographySWTElements.createCombo(parent, SWT.READ_ONLY, modes, TomographyMessages.MODE_TP);

		bindModeCombo(modeCombo);

		String perspectiveID = activeWindow.getActivePage().getPerspective().getId();
		setModeComboSelection(perspectiveID, modeCombo);

		activeWindow.addPerspectiveListener(new IPerspectiveListener() {
			@Override
			public void perspectiveChanged(IWorkbenchPage page, IPerspectiveDescriptor perspective, String changeId) {
				// Do nothing
			}

			/**
			 * Updates the Mode combo box when a perspective switch is triggered by another control
			 */
			@Override
			public void perspectiveActivated(IWorkbenchPage page, IPerspectiveDescriptor perspective) {
				if (!PERSPECTIVES_MAP.get(mode).equals(perspective.getId())) {
					setModeComboSelection(perspective.getId(), modeCombo);
				}
			}
		});
	}

	@SuppressWarnings("unchecked")
	private void bindModeCombo(final Combo modeCombo) {
		dbc.bindValue(WidgetProperties.selection().observe(modeCombo), BeanProperties.value("mode").observe(this));
	}

	/**
	 * Updates the mode selector combo with the new perspective Id provided is its a DIAD one
	 *
	 * @param perspectiveId
	 *            The id of the newly activated perspective
	 */
	private void setModeComboSelection(final String perspectiveId, final Combo modeCombo) {
		if (PERSPECTIVES_MAP.containsValue(perspectiveId)) {
			for (Entry<String, String> entry : PERSPECTIVES_MAP.entrySet()) {
				if (perspectiveId.equals(entry.getValue())) {
					mode = entry.getKey();
					modeCombo.setText(mode);
					break;
				}
			}
		}
	}

	@Override
	public void setFocus() {
		experimentCompose.setFocus();
	}

	public String getMode() {
		return mode;
	}

	public void setMode(String mode) {
		this.mode = mode;
		try {
			String id = PERSPECTIVES_MAP.get(mode);
			workbench.showPerspective(id, activeWindow);
		} catch (WorkbenchException e) {
			logger.error("Could get get perspective for mode {} ", mode, e);
		}
	}

	/**
	 * Retrieves and {@link Image} using the specified path
	 *
	 * @param path
	 *            The path to the image file
	 * @return The retrieved {@link Image}
	 */
	Image getImage(final String path) {
		return AbstractUIPlugin.imageDescriptorFromPlugin("uk.ac.diamond.daq.beamline.k11", path).createImage();
	}
}
