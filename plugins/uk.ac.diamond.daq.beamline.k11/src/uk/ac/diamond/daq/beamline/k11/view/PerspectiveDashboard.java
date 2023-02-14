/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

import static uk.ac.gda.ui.tool.ClientSWTElements.composite;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientGridDataFactory;
import static uk.ac.gda.ui.tool.ClientSWTElements.createClientLabel;

import org.eclipse.jface.resource.FontDescriptor;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.ui.part.ViewPart;
import org.springframework.context.ApplicationListener;

import uk.ac.gda.client.properties.mode.TestModeToggled;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientResourceManager;
import uk.ac.gda.ui.tool.spring.ClientSpringProperties;

/**
 * The main Experiment configuration view visible in all k11 perspectives
 */
public class PerspectiveDashboard extends ViewPart {

	public static final String ID = "uk.ac.diamond.daq.beamline.k11.view.PerspectiveDashboard";

	private static final String TITLE = "DIAD";
	private static final String TEST_MODE_PREFIX = "[Test Mode]";

	private Label label;

	@Override
	public void createPartControl(Composite parent) {

		final var composite = composite(parent, 1);
		composite.setBackground(Display.getCurrent().getSystemColor(SWT.COLOR_WIDGET_BACKGROUND));


		label = createClientLabel(composite, SWT.NONE, ClientMessages.DIAD,
				FontDescriptor.createFrom(ClientResourceManager.getDefaultFont(), 14, SWT.BOLD));
		createClientGridDataFactory().align(SWT.CENTER, SWT.END).indent(5, 5).applyTo(label);

		var labelUpdater = new LabelUpdater();
		SpringApplicationContextFacade.addApplicationListener(labelUpdater);
		label.addDisposeListener(dispose -> SpringApplicationContextFacade.removeApplicationListener(labelUpdater));

		labelUpdater.update();

		new PerspectiveDashboardCompositeFactory().createComposite(composite, SWT.NONE);
	}

	private class LabelUpdater implements ApplicationListener<TestModeToggled> {

		@Override
		public void onApplicationEvent(TestModeToggled event) {
			update();
		}

		private void update() {
			var testModeActive = getClientProperties().getModes().getTest().isActive();
			if (testModeActive) {
				label.setText(String.format("%s %s", TITLE, TEST_MODE_PREFIX));
			} else {
				label.setText(TITLE);
			}
			label.getParent().layout(true, true);
		}

		private ClientSpringProperties getClientProperties() {
			return SpringApplicationContextFacade.getBean(ClientSpringProperties.class);
		}

	}

	@Override
	public void setFocus() {
		// do nothing
	}

}
