/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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

import static uk.ac.gda.ui.tool.ClientMessages.MODE_TP;
import static uk.ac.gda.ui.tool.ClientSWTElements.STRETCH;
import static uk.ac.gda.ui.tool.ClientSWTElements.composite;
import static uk.ac.gda.ui.tool.ClientSWTElements.createCombo;
import static uk.ac.gda.ui.tool.ClientSWTElements.label;

import java.util.Arrays;
import java.util.stream.Stream;

import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.ui.IPerspectiveDescriptor;
import org.eclipse.ui.IPerspectiveListener;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.WorkbenchException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.daq.beamline.k11.diffraction.perspective.Diffraction;
import uk.ac.diamond.daq.beamline.k11.imaging.perspective.Imaging;
import uk.ac.diamond.daq.beamline.k11.perspective.FullyAutomated;
import uk.ac.gda.ui.tool.WidgetUtilities;

/**
 * Drop-down list to switch between different perspectives
 *
 * @author Maurizio Nagni
 */
public class PerspectiveSwitcher {

	private Combo modeCombo;

	public enum PerspectiveType {

		DIFFRACTION("Diffraction", Diffraction.ID),
		IMAGING("Imaging", Imaging.ID),
		FULLY_AUTOMATED("Fully Automated",	FullyAutomated.ID);

		private final String id;
		private final String label;

		PerspectiveType(String label, String id) {
			this.label = label;
			this.id = id;
		}

		public String getLabel() {
			return label;
		}

		public String getId() {
			return id;
		}
	}

	private static final Logger logger = LoggerFactory.getLogger(PerspectiveSwitcher.class);

	/**
	 * Build the {@link Composite} containing controls for selecting the experiment mode
	 *
	 * @param parent
	 *            The Experiment {@link Composite}
	 */
	public void create(Composite parent) {

		var composite = composite(parent, 2, false);
		label(composite, "Acquisition type");

		modeCombo = createCombo(composite, SWT.READ_ONLY, getTypes(), MODE_TP);
		STRETCH.applyTo(modeCombo);

		WidgetUtilities.addWidgetDisposableListener(modeCombo, SWT.Selection, getComboModeSelectionListener());
		setModeComboSelection(getActiveWindow().getActivePage().getPerspective().getId());

		final IPerspectiveListener perspectiveListener = new IPerspectiveListener() {
			@Override
			public void perspectiveChanged(IWorkbenchPage page, IPerspectiveDescriptor perspective, String changeId) {
				// Do nothing
			}

			/**
			 * Updates the Mode combo box when a perspective switch is triggered by another control
			 */
			@Override
			public void perspectiveActivated(IWorkbenchPage page, IPerspectiveDescriptor perspective) {
				setModeComboSelection(perspective.getId());
			}
		};

		getActiveWindow().addPerspectiveListener(perspectiveListener);
		modeCombo.addDisposeListener(dispose -> getActiveWindow().removePerspectiveListener(perspectiveListener));
	}

	private Listener getComboModeSelectionListener() {
		return selection -> {
			if (modeCombo.getSelectionIndex() > -1) {
				filterPerspectiveLabel(getTypes()[modeCombo.getSelectionIndex()])
					.findFirst()
					.ifPresent(p -> setModeComboSelection(p.getId()));
			}
		};
	}

	/**
	 * Updates the mode selector combo with the new perspective Id provided is its a DIAD one
	 *
	 * @param perspectiveId
	 *            The id of the newly activated perspective
	 */
	private void setModeComboSelection(final String perspectiveId) {
		filterPerspectiveId(perspectiveId)
			.findFirst()
			.ifPresent(this::setType);
	}

	private Stream<PerspectiveType> filterPerspectiveId(final String perspectiveId) {
		return Arrays.stream(PerspectiveType.values())
				.filter(p -> p.getId().equals(perspectiveId));
	}

	private Stream<PerspectiveType> filterPerspectiveLabel(final String perspectiveLabel) {
		return Arrays.stream(PerspectiveType.values())
				.filter(p -> p.getLabel().equals(perspectiveLabel));
	}

	private IWorkbenchWindow getActiveWindow() {
		return getWorkbench().getActiveWorkbenchWindow();
	}

	private IWorkbench getWorkbench() {
		return PlatformUI.getWorkbench();
	}

	private void setType(PerspectiveType type) {
		modeCombo.setText(type.getLabel());
		try {
			getWorkbench().showPerspective(type.getId(), getActiveWindow());
		} catch (WorkbenchException e) {
			logger.error("Cannot switch perspective", e);
		}
	}

	private String[] getTypes() {
		return Arrays.stream(PerspectiveType.values()).map(PerspectiveType::getLabel).toList()
				.toArray(new String[0]);
	}
}