/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.ui.data;

import org.eclipse.core.databinding.observable.list.IListChangeListener;
import org.eclipse.core.databinding.observable.list.ListChangeEvent;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.swt.widgets.ToolItem;
import org.eclipse.ui.ISharedImages;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.forms.widgets.Section;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableStatus;
import gda.observable.IObserver;
import uk.ac.gda.client.UIHelper;

public class ScannableMotorMoveObserver implements IObserver {

	private static final Logger logger = LoggerFactory.getLogger(ScannableMotorMoveObserver.class);

	private final WritableList movingScannables;
	public ScannableMotorMoveObserver(WritableList movingScannables) {
		this.movingScannables = movingScannables;
	}

	@Override
	public void update(final Object source,final Object arg) {
		if (arg instanceof ScannableStatus) {
			movingScannables.getRealm().asyncExec(new Runnable() {
				@Override
				public void run() {
					ScannableStatus status = (ScannableStatus) arg;
					if (status == ScannableStatus.BUSY) {
						if (!movingScannables.contains(source)) {
							movingScannables.add(source);
						}
					}
					else {
						movingScannables.remove(source);
					}
				}
			});
		}
	}

	public static IListChangeListener getStopButtonListener(final Composite motorSection, final ToolItem stopMotorsBarItem) {
		return new IListChangeListener() {
			@Override
			public void handleListChange(ListChangeEvent event) {
				if (event.getObservableList().isEmpty()) {
					stopMotorsBarItem.setEnabled(false);
					stopMotorsBarItem.setToolTipText("");
				} else {
					stopMotorsBarItem.setEnabled(true);
					if (event.getObservableList().size() == 1) {
						stopMotorsBarItem.setToolTipText("Stop " + ((Scannable) event.getObservableList().get(0)).getName());
					} else {
						stopMotorsBarItem.setToolTipText("Stop");
					}
				}
				motorSection.layout(true);
				motorSection.getParent().layout(true);
			}
		};
	}

	public static ToolItem setupStopToolItem(ToolBar toolBar, final WritableList movingScannables) {
		ToolItem stopMotorsBarItem = new ToolItem(toolBar, SWT.NULL);
		stopMotorsBarItem.setImage(PlatformUI.getWorkbench().getSharedImages().getImage(ISharedImages.IMG_ELCL_STOP));
		stopMotorsBarItem.addListener(SWT.Selection, new Listener() {
			@Override
			public void handleEvent(Event event) {
				for (Object scannable : movingScannables) {
					try {
						((Scannable) scannable).stop();
					} catch (DeviceException e) {
						String errorMessage = "Unable to stop motor " + ((Scannable) scannable).getName();
						UIHelper.showError(errorMessage, e.getMessage());
						logger.error(errorMessage, e);
					}
				}
			}
		});
		return stopMotorsBarItem;
	}

	/**
	 * Create 'motor stop' button on toolbar of a composite section.
	 * Refactored to avoid code duplication.
	 * @param section
	 * @param movingScannables
	 * @since 1/3/2016
	 */
	public static void setupStopToolbarButton(Section section, final WritableList movingScannables) {
		final ToolBar motorSectionTbar = new ToolBar(section, SWT.FLAT | SWT.HORIZONTAL);
		@SuppressWarnings("unused")
		ToolItem separator = new ToolItem(motorSectionTbar, SWT.SEPARATOR);
		final ToolItem stopMotorsBarItem = ScannableMotorMoveObserver.setupStopToolItem(motorSectionTbar, movingScannables);
		section.setTextClient(motorSectionTbar);
		movingScannables.addListChangeListener(ScannableMotorMoveObserver.getStopButtonListener(section, stopMotorsBarItem));
		stopMotorsBarItem.setEnabled(!movingScannables.isEmpty());
	}
}
