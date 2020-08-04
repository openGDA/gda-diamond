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

import static uk.ac.gda.ui.tool.ClientSWTElements.createClientLabel;

import java.util.Arrays;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.IPerspectiveDescriptor;
import org.eclipse.ui.IPerspectiveListener;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.WorkbenchException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.daq.beamline.k11.perspective.FullyAutomated;
import uk.ac.diamond.daq.beamline.k11.perspective.PointAndShoot;
import uk.ac.diamond.daq.beamline.k11.perspective.Tomography;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientSWTElements;

/**
 * Drop-down list to switch between different perspectives
 *
 * @author Maurizio Nagni
 */
public class PerspectiveComposite {

	private final Composite parent;
	private Combo modeCombo;

	private PerspectiveType type;

	public enum PerspectiveType {

		TOMOGRAPHY("Plain Tomography", Tomography.ID), FULLY_AUTOMATED("Fully Automated",
				FullyAutomated.ID), POINT_AND_SHOOT("Point and Shoot", PointAndShoot.ID);

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

	private static final Logger logger = LoggerFactory.getLogger(PerspectiveComposite.class);

	private PerspectiveComposite(Composite parent, PerspectiveType type) {
		this.parent = parent;
		this.type = type;
	}

	public static final void buildModeComposite(Composite parent, PerspectiveType type) {
		PerspectiveComposite pc = new PerspectiveComposite(parent, type);
		pc.buildModeComposite();
	}

	private Composite getParent() {
		return parent;
	}

	/**
	 * Build the {@link Composite} containing controls for selecting the experiment mode
	 *
	 * @param parent
	 *            The Experiment {@link Composite}
	 */
	private void buildModeComposite() {
		Label label = createClientLabel(getParent(), SWT.NONE, ClientMessages.MODE);
		ClientSWTElements.createClientGridDataFactory().indent(5, SWT.DEFAULT).applyTo(label);

		modeCombo = ClientSWTElements.createCombo(parent, SWT.READ_ONLY, getTypes(), ClientMessages.MODE_TP);
		ClientSWTElements.createClientGridDataFactory().indent(5, SWT.DEFAULT).applyTo(modeCombo);

		comboModeSelectionListener();
		setModeComboSelection(getActiveWindow().getActivePage().getPerspective().getId());

		getActiveWindow().addPerspectiveListener(new IPerspectiveListener() {
			@Override
			public void perspectiveChanged(IWorkbenchPage page, IPerspectiveDescriptor perspective, String changeId) {
				// Do nothing
			}

			/**
			 * Updates the Mode combo box when a perspective switch is triggered by another control
			 */
			@Override
			public void perspectiveActivated(IWorkbenchPage page, IPerspectiveDescriptor perspective) {
				if (!filterPerspectiveId(perspective.getId()).findAny().isPresent()) {
					setModeComboSelection(perspective.getId());
				}
			}
		});
	}

	private void comboModeSelectionListener() {
		SelectionListener listener = new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				Combo source = Combo.class.cast(e.getSource());
				if (source.getSelectionIndex() > -1) {
					filterPerspectiveLabel(getTypes()[source.getSelectionIndex()]).findFirst()
							.ifPresent(p -> setModeComboSelection(p.getId()));
				}
			}
		};
		modeCombo.addSelectionListener(listener);
	}

	/**
	 * Updates the mode selector combo with the new perspective Id provided is its a DIAD one
	 *
	 * @param perspectiveId
	 *            The id of the newly activated perspective
	 */
	private void setModeComboSelection(final String perspectiveId) {
		filterPerspectiveId(perspectiveId).findFirst().ifPresent(this::setType);
	}

	private Stream<PerspectiveType> filterPerspectiveId(final String perspectiveId) {
		return Arrays.stream(PerspectiveType.values()).filter(p -> p.getId().equals(perspectiveId));
	}

	private Stream<PerspectiveType> filterPerspectiveLabel(final String perspectiveLabel) {
		return Arrays.stream(PerspectiveType.values()).filter(p -> p.getLabel().equals(perspectiveLabel));
	}

	private IWorkbenchWindow getActiveWindow() {
		return getWorkbench().getActiveWorkbenchWindow();
	}

	private IWorkbench getWorkbench() {
		return PlatformUI.getWorkbench();
	}

	private void setType(PerspectiveType type) {
		this.type = type;
		modeCombo.setText(type.getLabel());
		try {
			getWorkbench().showPerspective(this.type.getId(), getActiveWindow());
		} catch (WorkbenchException e) {
			logger.error("Cannot switch perspective", e);
		}
	}

	private String[] getTypes() {
		return Arrays.stream(PerspectiveType.values()).map(PerspectiveType::getLabel).collect(Collectors.toList())
				.toArray(new String[0]);
	}
}
