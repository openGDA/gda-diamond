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

import java.net.URI;
import java.net.URISyntaxException;
import java.util.Objects;

import org.eclipse.scanning.api.event.EventConstants;
import org.eclipse.scanning.api.event.EventException;
import org.eclipse.scanning.api.event.IEventService;
import org.eclipse.scanning.api.event.core.AbstractLockingPausableProcess;
import org.eclipse.scanning.api.event.core.IJmsQueueReader;
import org.eclipse.scanning.api.event.core.IJobQueue;
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
 *
 *
 * Adjusted to match closer to AbstractJobQueueServlet, but without forcing a dependency on Scanning code.
 */
public class XpdfTaskConsumer {

	private static final Logger logger = LoggerFactory.getLogger(XpdfTaskConsumer.class);

	private final IEventService eventService;

	private IXpdfTaskRunner taskRunner;
	private IJobQueue<TaskBean> jobQueue;
	private IJmsQueueReader<TaskBean> jmsQueueReader;

	public XpdfTaskConsumer() {
		this.eventService = Activator.getService(IEventService.class);
	}

	public void setTaskRunner(IXpdfTaskRunner taskRunner) {
		this.taskRunner = taskRunner;
		logger.debug("taskRunner set to: {}", taskRunner);
	}

	public void startJobQueue() {
		logger.info("Starting XPDF Task Runner queue...");

		// Validate we have the required objects to work.
		Objects.requireNonNull(taskRunner, "Task runner is not set check Spring configuration");
		Objects.requireNonNull(eventService, "Could not get Event Service");

		try {
			final URI uri = new URI(LocalProperties.getActiveMQBrokerURI());

			jobQueue = eventService.createJobQueue(uri, QueueConstants.XPDF_TASK_QUEUE, EventConstants.STATUS_TOPIC);
			jobQueue.setRunner(ConsumerProcess::new);
			jobQueue.setName("XPDF Task Runner queue");
			jobQueue.start();
			// start a queue reader for the queue for beans that are still submitted to the JMS queue.
			// This reads the beans from the JMS queue and submits them to the IJobQueue.
			jmsQueueReader = eventService.createJmsQueueReader(uri, QueueConstants.XPDF_TASK_QUEUE);
			jmsQueueReader.start();
		} catch (EventException | URISyntaxException e) {
			logger.error("Failed to setup XPDF Task Runner queue", e);
		}
		logger.info("Started XPDF Task Runner queue");
	}

	private class ConsumerProcess extends AbstractLockingPausableProcess<TaskBean> {

		protected ConsumerProcess(TaskBean bean, IPublisher<TaskBean> publisher) {
			super(bean, publisher);
		}

		@Override
		public void execute() throws EventException, InterruptedException {
			logger.info("Running Task: {}", bean);

			// Call the task runner with the parameters
			taskRunner.runTask(bean.getProposalCode(), bean.getProposalNumber(), bean.getSampleId(),
					bean.getDataCollectionPlanId());

			logger.info("Finished running task: {}", bean);
		}
	}

}
