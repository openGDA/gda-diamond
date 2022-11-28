/*-
 * Copyright © 2022 Diamond Light Source Ltd.
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

import static uk.ac.gda.ui.tool.ClientSWTElements.STRETCH;
import static uk.ac.gda.ui.tool.ClientSWTElements.composite;

import java.util.List;
import java.util.Map;

import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.TabFolder;
import org.eclipse.swt.widgets.TabItem;

import gda.factory.Finder;
import gda.rcp.views.StageCompositeDefinition;
import gda.rcp.views.StageCompositeFactory;

public class StageControls {

	private final StagesConfiguration config;

	public StageControls() {
		config = Finder.findLocalSingleton(StagesConfiguration.class);
	}

	public Control create(Composite parent) {
		var composite = composite(parent, 1);

		TabFolder stages = new TabFolder(composite, SWT.TOP);
		STRETCH.applyTo(stages);

		for (var stage : config.getStageConfiguration().entrySet()) {
			TabItem tab = new TabItem(stages, SWT.NULL);
			tab.setText(stage.getKey());
			tab.setControl(createStageControls(stages, stage.getValue()));
		}

		return composite;
	}

	private Control createStageControls(Composite parent, Map<String, String> value) {
		var composite = composite(parent, 1);

		List<StageCompositeDefinition> axes = value.entrySet().stream()
				.map(axis -> axis(axis.getKey(), axis.getValue()))
				.toList();

		var controls = new StageCompositeFactory();
		controls.setStageCompositeDefinitions(axes.toArray(new StageCompositeDefinition[0]));
		controls.createComposite(composite, SWT.NONE);

		return composite;
	}

	private StageCompositeDefinition axis(String displayName, String scannableName) {
		var axis = new StageCompositeDefinition();
		axis.setLabel(displayName);
		axis.setScannable(Finder.find(scannableName));
		return axis;
	}

}
