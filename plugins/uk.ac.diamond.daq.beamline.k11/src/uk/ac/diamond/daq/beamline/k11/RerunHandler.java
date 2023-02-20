/*-
 * Copyright © 2023 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11;

import static uk.ac.gda.ui.tool.ClientSWTElements.label;
import static uk.ac.gda.ui.tool.ClientSWTElements.spinner;

import java.util.List;
import java.util.UUID;
import java.util.stream.IntStream;

import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.window.Window;
import org.eclipse.scanning.api.event.scan.ScanBean;
import org.eclipse.scanning.api.event.status.Status;
import org.eclipse.scanning.api.event.status.StatusBean;
import org.eclipse.scanning.api.ui.IRerunHandler;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Shell;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.diamond.daq.experiment.api.ExperimentException;
import uk.ac.diamond.daq.mapping.api.IScanBeanSubmitter;
import uk.ac.diamond.daq.mapping.ui.services.MappingRemoteServices;
import uk.ac.gda.client.exception.GDAClientRestException;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.rest.ClientRestServices;


/**
 * This rerun handler asks the user to specify number of repetitions,
 * and generates new filepaths for each repetition to avoid overwriting data
 * (a small but important K11 quirk!).
 */
public class RerunHandler implements IRerunHandler<ScanBean> {

	private static final Logger logger = LoggerFactory.getLogger(RerunHandler.class);

	@Override
	public boolean isHandled(StatusBean bean) {
		return bean instanceof ScanBean;
	}

	@Override
	public boolean handleRerun(List<ScanBean> scans) throws Exception {

		var dialog = new RepeatsDialog(Display.getDefault().getActiveShell());
		if (dialog.open() == Window.OK) {
			repeat(scans, dialog.getNumberOfRepeats());
		}
		return true;
	}

	private void repeat(List<ScanBean> scans, int repeats) {
		IntStream.range(0, repeats).forEach(repeat -> {
			for (var scan : scans) {
				submit(duplicate(scan));
			}
		});
	}

	private ScanBean duplicate(ScanBean bean) {
		var duplicate = new ScanBean();
		duplicate.merge(bean);
		duplicate.setUniqueId(UUID.randomUUID().toString());
		duplicate.setFilePath(null);
		duplicate.getScanRequest().setFilePath(requestFilePath(duplicate.getName()));
		duplicate.setMessage("Rerun of " + bean.getName());
		duplicate.setStatus(Status.SUBMITTED);
		duplicate.setPercentComplete(0.0);
		return duplicate;
	}

	private void submit(ScanBean bean) {
		bean.setSubmissionTime(System.currentTimeMillis());
		try {
			getSubmitter().submitScan(bean);
		} catch (Exception e) {
			throw new ExperimentException(e);
		}
	}

	private String requestFilePath(String name) {
		try {
			return ClientRestServices.getExperimentController().prepareAcquisition(name).getPath();
		} catch (GDAClientRestException e) {
			logger.error("Error generating experiment-compatible file path - experiment file will not link to this measurement!", e);
			return null;
		}
	}

	private class RepeatsDialog extends Dialog {

		private int repeats = 1;

		protected RepeatsDialog(Shell parentShell) {
			super(parentShell);
		}

		@Override
		protected Control createDialogArea(Composite parent) {
			var composite = (Composite) super.createDialogArea(parent);

			label(composite, "Number of repeats:");
			var spinner = spinner(composite);
			spinner.setMinimum(1);
			spinner.setMaximum(Integer.MAX_VALUE);
			spinner.setSelection(repeats);
			spinner.addModifyListener(modify -> repeats = spinner.getSelection());

			return composite;
		}

		@Override
		protected void configureShell(Shell newShell) {
			super.configureShell(newShell);
			newShell.setText("Repeat scans");
		}

		public int getNumberOfRepeats() {
			return repeats;
		}
	}

	private IScanBeanSubmitter getSubmitter() {
		return SpringApplicationContextFacade.getBean(MappingRemoteServices.class).getIScanBeanSubmitter();
	}

}
