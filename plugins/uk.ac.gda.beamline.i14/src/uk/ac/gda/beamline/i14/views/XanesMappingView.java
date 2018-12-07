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

package uk.ac.gda.beamline.i14.views;

import java.util.Arrays;
import java.util.List;

import javax.inject.Inject;

import uk.ac.diamond.daq.mapping.api.IMappingExperimentBeanProvider;
import uk.ac.diamond.daq.mapping.ui.experiment.AbstractMappingSection;
import uk.ac.diamond.daq.mapping.ui.experiment.AbstractSectionsView;
import uk.ac.diamond.daq.mapping.ui.experiment.DetectorsSection;
import uk.ac.diamond.daq.mapping.ui.experiment.ProcessingSection;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathSection;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanMetadataSection;

/**
 * Version of the Mapping view tailored to XANES scanning
 */
public class XanesMappingView extends AbstractSectionsView {

	@Inject
	public XanesMappingView(IMappingExperimentBeanProvider beanProvider) {
		super(beanProvider);
	}

	@Override
	protected List<Class<? extends AbstractMappingSection>> getScrolledSectionClasses() {
		return Arrays.asList(
			// a section for choosing the detectors (or malcolm device) to include in the scan
			DetectorsSection.class,
			// a section for configuring the path of the mapping scan
			RegionAndPathSection.class,
			// a section for configuring XANES scans (I14-specific)
			XanesEdgeParametersSection.class,
			// a section for configuring metadata to add to the scan
			ScanMetadataSection.class,
			// a section for configuring live processing to run
			ProcessingSection.class);
	}

	@Override
	protected List<Class<? extends AbstractMappingSection>> getUnscrolledSectionClasses() {
		return Arrays.asList(
			// a section for submitting the scan to the queue
			XanesSubmitScanSection.class);
	}

	@Override
	public void handleSetFocus() {
		updateControls();
		super.handleSetFocus();
	}

	@Override
	protected void disposeInternal() {
		// Edge parameters section must be disposed so that any scan path editors are properly disposed
		final AbstractMappingSection paramsSection = getSection(XanesEdgeParametersSection.class);
		if (paramsSection != null) {
			paramsSection.dispose();
		}
		super.disposeInternal();
	}
}