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

package uk.ac.gda.beamline.i151.xpdf.ui;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.function.Function;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import javax.inject.Inject;

import org.eclipse.e4.ui.di.Focus;
import org.eclipse.richbeans.widgets.shuffle.ShuffleConfiguration;
import org.eclipse.richbeans.widgets.shuffle.ShuffleViewer;
import org.eclipse.scanning.api.event.EventException;
import org.eclipse.scanning.api.event.IEventService;
import org.eclipse.scanning.api.event.core.ISubmitter;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.layout.RowLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import uk.ac.diamond.daq.beamline.i15.api.QueueConstants;
import uk.ac.diamond.daq.beamline.i15.api.TaskBean;
import uk.ac.diamond.daq.beamline.i15.database.IXpdfDatabaseService;
import uk.ac.diamond.ispyb.api.DataCollectionPlan;
import uk.ac.diamond.ispyb.api.Sample;

public class XpdfExperimentView {

	public static final String ID = "org.eclipse.scanning.device.ui.expr.experimentSubmissionView"; //$NON-NLS-1$

	private static final Logger logger = LoggerFactory.getLogger(XpdfExperimentView.class);

	private ShuffleConfiguration<ExperimentEntry> conf;
	private ShuffleViewer<ExperimentEntry> viewer;

	private VisitInfomation visitInfo = new VisitInfomation();

	@Inject
	private IXpdfDatabaseService database;

	@Inject
	private IEventService eventService;
	private ISubmitter<TaskBean> taskSubmitter; // Lazy initialised on first submit

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

		final Composite buttons = new Composite(container, SWT.NONE);
		buttons.setLayout(new RowLayout(SWT.HORIZONTAL));
		buttons.setLayoutData(new GridData(SWT.RIGHT, SWT.FILL, true, false));

		final Button refresh = new Button(buttons, SWT.PUSH | SWT.FLAT);
		refresh.setText("Refresh");
		refresh.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				refresh();
			}

		});

		final Button submit = new Button(buttons, SWT.PUSH | SWT.FLAT);
		submit.setText("Submit");
		submit.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				submit();
			}
		});

		refresh();
	}

	private void submit() {
		if (taskSubmitter == null) {
			URI uri;
			try {
				uri = new URI(LocalProperties.getActiveMQBrokerURI());
				taskSubmitter = eventService.createSubmitter(uri, QueueConstants.XPDF_TASK_QUEUE);
			} catch (URISyntaxException e) {
				throw new RuntimeException("Could not create submitter", e);
			}
		}

		// Loop over all the experiment to be submitted.
		for (ExperimentEntry experiment : conf.getToList()) {
			final TaskBean taskBean = new TaskBean(visitInfo.getProposalCode(), visitInfo.getProposalNumber(),
					experiment.getSampleId(), experiment.getDataCollectionPlanId());
			try {
				taskSubmitter.submit(taskBean);
			} catch (EventException e) {
				logger.error("Failed to submit: {}", experiment, e);
			}
		}

	}

	private void refresh() {
		final List<ExperimentEntry> experiments = new ArrayList<>();

		final List<Sample> samples = getSamplesForCurrentVisit();
		for (Sample sample : samples) {
			final Collection<DataCollectionPlan> dcps = getUniqueDataCollectionPlansForSample(sample);
			for (DataCollectionPlan dcp : dcps) {
				experiments.add(new ExperimentEntry(sample, dcp));
			}
		}

		conf.setFromList(experiments);
	}

	private Collection<DataCollectionPlan> getUniqueDataCollectionPlansForSample(Sample sample) {
		// From the DB you might have multiple DCPs with the same ID (to represent multiple scan axis)
		final List<DataCollectionPlan> dcps = database.retrieveDataCollectionPlansForSample(sample.getSampleId());
		// This is a trick to get unique elements by the DCP ID. Put into a map keyed by the ID and where there are
		// duplicated keys throw away the second object. Then return all the values.
		return dcps.stream()
				.collect(Collectors.toMap( // Make a Map
						DataCollectionPlan::getDcPlanId, // Key: DCP ID
						Function.identity(), // Value: the DCP itself
						(dcp1, dcp2) -> dcp1)) // If the keys are duplicated just keep the first DCP
				.values(); // Get the values i.e. the unique DCPs
	}

	private List<Sample> getSamplesForCurrentVisit() {
		return database.retrieveSamplesAssignedForProposal(visitInfo.getProposalCode(), visitInfo.getProposalNumber());
	}

	@Focus
	public void setFocus() {
		viewer.setFocus();
	}

	@PreDestroy
	public void dispose() {
		viewer.dispose();
	}

	private class ExperimentEntry {

		final Sample sample;
		final DataCollectionPlan dcp;

		public ExperimentEntry(Sample sample, DataCollectionPlan dcp) {
			this.sample = sample;
			this.dcp = dcp;
		}

		@Override
		public String toString() {
			// Note this toString is the thing used for what gets displayed in the UI. Not just for debugging!
			return sample.getSampleName() + " (" + sample.getSampleId() + ") : " + dcp.getName() + " ("
					+ dcp.getDcPlanId() + ")";
		}

		public long getSampleId() {
			return sample.getSampleId();
		}

		public long getDataCollectionPlanId() {
			return dcp.getDcPlanId();
		}
	}

	private class VisitInfomation {
		/** Split up the visit string (e.g. "ab12345-6") into groups (e.g. "ab", "12345", "6") */
		private final Pattern visitRegex = Pattern.compile("([a-z]{2})([0-9]+)-([0-9]+)");

		final String proposalCode;
		final long proposalNumber;
		final long sessionNumber;

		private VisitInfomation() {
			// Get the visit for this client; set at client startup
			final String visit = LocalProperties.get(LocalProperties.RCP_APP_VISIT);

			// Get the matcher using the visit regex
			final Matcher matcher = visitRegex.matcher(visit);

			if (matcher.matches()) {
				proposalCode = matcher.group(1);
				proposalNumber = Long.parseLong(matcher.group(2));
				sessionNumber = Long.parseLong(matcher.group(3));
			} else {
				logger.error("Failed to parse visit: {}", visit);
				throw new RuntimeException("Failed to parse visit infomation");
			}
		}

		public String getProposalCode() {
			return proposalCode;
		}

		public long getProposalNumber() {
			return proposalNumber;
		}

		@Override
		public String toString() {
			return "VisitInfomation [proposalCode=" + proposalCode + ", proposalNumber=" + proposalNumber
					+ ", sessionNumber=" + sessionNumber + "]";
		}
	}
}
