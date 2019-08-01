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

package uk.ac.diamond.daq.beamline.i151.server;

import static org.eclipse.scanning.api.event.EventConstants.STATUS_TOPIC;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.Objects;

import org.eclipse.scanning.api.event.EventException;
import org.eclipse.scanning.api.event.IEventService;
import org.eclipse.scanning.api.event.core.AbstractLockingPausableProcess;
import org.eclipse.scanning.api.event.core.IBeanProcess;
import org.eclipse.scanning.api.event.core.IJobQueue;
import org.eclipse.scanning.api.event.core.IProcessCreator;
import org.eclipse.scanning.api.event.core.IPublisher;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import uk.ac.diamond.daq.beamline.i15.api.QueueConstants;
import uk.ac.diamond.daq.beamline.i15.api.TaskBean;

/**
 * This is the ActiveMQ consumer that handles {@link TaskBean}s. It takes them off the queue defined by
 * {@link QueueConstants#XPDF_TASK_QUEUE} and passes them to a {@link XpdfTaskRunner} to be executed.
 *
 * @author James Mudd
 */
public class XpdfTaskConsumer {

	private static final Logger logger = LoggerFactory.getLogger(XpdfTaskConsumer.class);

	private IXpdfTaskRunner taskRunner;

	public void setTaskRunner(IXpdfTaskRunner taskRunner) {
		this.taskRunner = taskRunner;
		logger.debug("taskRunner set to: {}", taskRunner);
	}

	public void startJobQueue() {
		logger.info("Starting XPDF Task Runner queue...");

		// Validate we have the required objects to work.
		Objects.requireNonNull(taskRunner, "Task runner is not set check Spring configuration");
		final IEventService eventService = Activator.getService(IEventService.class);
		Objects.requireNonNull(eventService, "Could not get Event Service");

		try {
			final URI uri = new URI(LocalProperties.getActiveMQBrokerURI());

			IJobQueue<TaskBean> jobQueue = eventService.createJobQueue(uri, QueueConstants.XPDF_TASK_QUEUE, STATUS_TOPIC);
			jobQueue.setRunner(new ProcessCreator());
			jobQueue.setName("XPDF Task Runner ueue");
			jobQueue.start();
		} catch (EventException | URISyntaxException e) {
			logger.error("Failed to setup XPDF Task Runner queue", e);
		}
		logger.info("Started XPDF Task Runner queue");
	}

	private class ProcessCreator implements IProcessCreator<TaskBean> {

		@Override
		public IBeanProcess<TaskBean> createProcess(TaskBean bean, IPublisher<TaskBean> statusNotifier)
				throws EventException {
			return new ConsumerProcess(bean, statusNotifier);
		}

	}

	private class ConsumerProcess extends AbstractLockingPausableProcess<TaskBean> {

		private final TaskBean taskBean;

		public ConsumerProcess(TaskBean taskBean, IPublisher<TaskBean> publisher) {
			super(taskBean, publisher);
			this.taskBean = taskBean;
		}

		@Override
		public void execute() throws EventException, InterruptedException {
			logger.info("Running Task: {}", taskBean);

			// Call the task runner with the parameters
			taskRunner.runTask(taskBean.getProposalCode(),
					taskBean.getProposalNumber(),
					taskBean.getSampleId(),
					taskBean.getDataCollectionPlanId());

			logger.info("Finished running task: {}", taskBean);
		}
	}

}
