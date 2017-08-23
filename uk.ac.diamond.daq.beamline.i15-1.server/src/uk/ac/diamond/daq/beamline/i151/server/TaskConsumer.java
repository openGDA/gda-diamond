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
import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

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
import org.python.core.PyDictionary;
import org.python.core.PyObject;
import org.python.core.PyString;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.factory.Finder;
import gda.jython.Jython;
import uk.ac.diamond.daq.beamline.i15.api.QueueConstants;
import uk.ac.diamond.daq.beamline.i15.api.TaskBean;

/**
 *
 * NOTE: This is using the PDE DS annotation builder to auto-generate the OSGI-INF file.
 * See: http://blog.vogella.com/2016/06/21/getting-started-with-osgi-declarative-services/
 *
 * @author James Mudd
 */
@Component(name="TaskConsumer")
public class TaskConsumer {

	private static final Logger logger = LoggerFactory.getLogger(TaskConsumer.class);

	private IEventService eventService;

	public IEventService getEventService() {
		return eventService;
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
			// FIXME Temp only for testing see
			String url = "tcp://localhost:61616";
			//String url = LocalProperties.getActiveMQBrokerURI();

			IConsumer<TaskBean> consumer = eventService.createConsumer(new URI(url));
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

		private TaskBean taskBean;
		private IPublisher<TaskBean> publisher;

		public ConsumerProcess(TaskBean taskBean, IPublisher<TaskBean> publisher) {
			super(taskBean, publisher);
			this.taskBean = taskBean;
			this.publisher = publisher;
		}

		@Override
		public void execute() throws EventException, InterruptedException {
			logger.info("Running Task: {}", taskBean);

			// TODO here Need to access database to retrieve sample and experiment info
			Map<String, String> taskConfig = new HashMap<>();
			taskConfig.put("proposal_code", taskBean.getProposalCode());
			taskConfig.put("proposal_number", Long.toString(taskBean.getProposalNumber()));
			taskConfig.put("sample_id", Long.toString(taskBean.getSampleId()));

			// TODO If we have lots of database beans here could use
			//Map<String, String> taskConfig = BeanUtils.describe(taskConfig);

			// TODO Might want more structure than a flat string to string map

			// Convert Map<String, String> to PyDictionary for Jython
			PyDictionary dict = new PyDictionary(taskConfig.entrySet().stream().
					collect(Collectors.toMap(
							entry -> new PyString(entry.getKey()), // Convert key String to PyString
							entry -> new PyString(entry.getValue())))); // Convert value String to PyString

			Jython jython = Finder.getInstance().find(Jython.SERVER_NAME);
			// Get the method to call
			PyObject taskRunner = jython.eval("task_runner");
			// Call the method with the dictionary of database data. This is blocking
			taskRunner.__call__(dict);

			logger.info("Finished running task: {}", taskBean);
		}
	}
}
