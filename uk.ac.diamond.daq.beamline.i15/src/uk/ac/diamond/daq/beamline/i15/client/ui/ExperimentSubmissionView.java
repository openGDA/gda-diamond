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

package uk.ac.diamond.daq.beamline.i15.client.ui;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Scanner;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import javax.inject.Inject;

import org.eclipse.e4.ui.di.Focus;
import org.eclipse.richbeans.widgets.shuffle.ShuffleConfiguration;
import org.eclipse.richbeans.widgets.shuffle.ShuffleViewer;
import org.eclipse.scanning.api.database.ISampleDescriptionService;
import org.eclipse.scanning.api.event.EventException;
import org.eclipse.scanning.api.event.IEventService;
import org.eclipse.scanning.api.event.core.ISubmitter;
import org.eclipse.scanning.api.scan.IFilePathService;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import uk.ac.diamond.daq.beamline.i15.api.QueueConstants;
import uk.ac.diamond.daq.beamline.i15.api.TaskBean;

public class ExperimentSubmissionView {

	public static final String ID = "org.eclipse.scanning.device.ui.expr.experimentSubmissionView"; //$NON-NLS-1$
	private static final Logger logger = LoggerFactory.getLogger(ExperimentSubmissionView.class);
	private ShuffleConfiguration<SampleEntry> conf;
	private ShuffleViewer<SampleEntry> viewer;
	private String proposalCode;
	private long proposalNumber;
	private Map<Long, String> sampleIdNames;
	private ISampleDescriptionService sampleDescriptionService = new MockSampleDescriptionService();

	@Inject
	private IEventService eventService;

	@Inject
	private IFilePathService filePathService;

	/**
	 * Create contents of the view part.
	 *
	 * @param parent
	 */
	@PostConstruct
	public void createView(Composite parent) {

		conf = new ShuffleConfiguration<>();
		conf.setFromLabel("Available Experiments");
		conf.setToLabel("Submission List");
		conf.setFromReorder(true);
		conf.setToReorder(true);

		Composite container = new Composite(parent, SWT.NONE);
		container.setLayout(new GridLayout(1, false));

		viewer = new ShuffleViewer<>(conf);
		viewer.createPartControl(container);
		viewer.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, true));

		final Color white = Display.getCurrent().getSystemColor(SWT.COLOR_WHITE);

		final Composite buttons = new Composite(container, SWT.NONE);
		buttons.setBackground(white);
		buttons.setLayout(new RowLayout(SWT.HORIZONTAL));
		buttons.setLayoutData(new GridData(SWT.RIGHT, SWT.FILL, true, false));

		Button refresh = new Button(buttons, SWT.PUSH | SWT.FLAT);
		refresh.setText("Refresh");
		refresh.setBackground(white);
		refresh.setImage(new Image(Display.getCurrent(), getClass().getResourceAsStream("/icons/recycle.png")));
		refresh.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				refresh();
			}
		});

		Button submit = new Button(buttons, SWT.PUSH | SWT.FLAT);
		submit.setText("Submit");
		submit.setBackground(white);
		submit.setImage(new Image(Display.getCurrent(), getClass().getResourceAsStream("/icons/shoe--arrow.png")));
		submit.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				submit();
			}
		});

		processVisitID();
		refresh();
	}

	private void submit() {
		if (proposalCode == null) {
			logger.error("Absent or invalid visit ID");
			return;
		}
		submitExperiments();
		conf.setToList(new ArrayList<SampleEntry>());
		refresh();
	}

	private void refresh() {
		getSampleIdNamesForView();
	}

	@Focus
	public void setFocus() {
		viewer.setFocus();
	}

	@PreDestroy
	public void dispose() {
		viewer.dispose();
	}

	public void processVisitID() {
		String visitID;
		try {
			visitID = filePathService.getVisit();
		} catch (Exception e) {
			logger.error("Cannot get visit ID", e);
			return;
		}
		try (Scanner scanner = new Scanner(visitID)) {
			proposalCode = scanner.findInLine("\\D+");
			if (proposalCode == null) {
				logger.error("Error while parsing visit ID: invalid proposal code");
				return;
			}
			String lineProposalNumber = scanner.findInLine("\\d+");
			if (lineProposalNumber == null) {
				proposalCode = null;
				logger.error("Error while parsing visit ID: invalid proposal number");
				return;
			}
			proposalNumber = Long.parseLong(lineProposalNumber);
		} catch (Exception e) {
			logger.error("Cannot parse visit ID", e);
		}
	}

	/**
	 * Get the samples information and show it in the UI
	 */
	private void getSampleIdNamesForView() {
		if (proposalCode == null) {
			logger.error("Absent or invalid visit ID");
			return;
		}
		sampleIdNames = sampleDescriptionService.getSampleIdNames(proposalCode, proposalNumber);
		ArrayList<SampleEntry> fromList = new ArrayList<>();
		HashSet<SampleEntry> shuffleToList = new HashSet<>(conf.getToList());
		sampleIdNames.forEach((k, v) -> {
			SampleEntry sampleEntry = new SampleEntry(k, v);
			if (!shuffleToList.contains(sampleEntry)) {
				fromList.add(sampleEntry);
			}
		});
		conf.setFromList(fromList);
	}

	private void submitExperiments() {
		List<SampleEntry> samples = conf.getToList();
		logger.info("Submitting for proposal: {}-{}", proposalCode, proposalNumber);
		logger.info("Submitting samples: {}", samples);

		ISubmitter<TaskBean> submitter = createScanSubmitter();

		for (SampleEntry sampleEntry : samples) {
			TaskBean bean = new TaskBean(proposalCode, proposalNumber, sampleEntry.getSampleId());
			try {
				submitter.submit(bean);
			} catch (EventException e) {
				logger.error("Failed to submit task: {}", bean, e);
			}
		}
	}

	private ISubmitter<TaskBean> createScanSubmitter() {
		if (eventService != null) {
			try {
				URI queueServerURI = new URI(LocalProperties.getActiveMQBrokerURI());
				return eventService.createSubmitter(queueServerURI, QueueConstants.XPDF_TASK_QUEUE);
			} catch (URISyntaxException e) {
				logger.error("URI syntax problem", e);
				throw new RuntimeException(e);
			}
		}
		throw new NullPointerException("Event service is not set - check OSGi settings");
	}
}
