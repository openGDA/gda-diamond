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

import org.eclipse.scanning.api.event.EventException;
import org.eclipse.scanning.api.event.IEventService;
import org.eclipse.scanning.api.event.core.AbstractLockingPausableProcess;
import org.eclipse.scanning.api.event.core.IConsumer;
import org.eclipse.scanning.api.event.core.IConsumerProcess;
import org.eclipse.scanning.api.event.core.IProcessCreator;
import org.eclipse.scanning.api.event.core.IPublisher;
import org.osgi.service.component.annotations.Activate;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Reference;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import uk.ac.diamond.daq.beamline.i15.api.QueueConstants;
import uk.ac.diamond.daq.beamline.i15.api.TaskBean;

/**
 *
 * NOTE: This is using the PDE DS annotation builder to auto-generate the OSGI-INF file.
 * See: http://blog.vogella.com/2016/06/21/getting-started-with-osgi-declarative-services/
 *
 * @author James Mudd
 */
@Component(name="XpdfTaskConsumer")
public class XpdfTaskConsumer {

	private static final Logger logger = LoggerFactory.getLogger(XpdfTaskConsumer.class);

	private IEventService eventService;

	private IXpdfTaskRunner taskRunner;

	@Reference
	public void setTaskRunner(IXpdfTaskRunner taskRunner) {
		this.taskRunner = taskRunner;
		logger.debug("taskRunner set to: {}", taskRunner);
	}

	@Reference
	public void setEventService(IEventService eventService) {
		this.eventService = eventService;
		logger.debug("eventService set to: {}", eventService);
	}

	@Activate
	private void startConsumer() {
		logger.info("Starting consumer");

		try {
			final URI uri = new URI(LocalProperties.getActiveMQBrokerURI());

			IConsumer<TaskBean> consumer = eventService.createConsumer(uri);
			consumer.setSubmitQueueName(QueueConstants.XPDF_TASK_QUEUE);
			consumer.setRunner(new ProcessCreator());
			consumer.setName("Task Consmer");
			consumer.start();
		} catch (EventException | URISyntaxException e) {
			logger.error("Failed tosetup consumer", e);
		}

	}

	private class ProcessCreator implements IProcessCreator<TaskBean> {

		@Override
		public IConsumerProcess<TaskBean> createProcess(TaskBean bean, IPublisher<TaskBean> statusNotifier)
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
