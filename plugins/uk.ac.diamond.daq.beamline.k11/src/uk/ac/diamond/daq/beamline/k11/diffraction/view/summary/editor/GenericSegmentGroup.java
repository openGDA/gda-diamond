/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.summary.editor;

import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.api.acquisition.AcquisitionControllerException;
import uk.ac.gda.core.tool.spring.SpringApplicationContextFacade;
import uk.ac.gda.ui.tool.document.ScanningAcquisitionTemporaryHelper;

/**
 * Basic implementation of the {@link SegmentGroup} interface.
 *
 * @param <T> the numeric structure represented by this group
 *
 * @author Maurizio Nagni
 */
public abstract class GenericSegmentGroup<T> implements SegmentGroup<T> {
	private static final Logger logger = LoggerFactory.getLogger(GenericSegmentGroup.class);

	private final DecimalFormat decimalFormat;
	private final List<Segment<T>> segments = new ArrayList<>();
	private final boolean editable;

	private final Consumer<T> setter;

	protected GenericSegmentGroup(Consumer<T> setter, DecimalFormat decimalFormat, boolean editable) {
		this.setter = setter;
		this.decimalFormat = decimalFormat;
		this.editable = editable;
	}

	@Override
	public DecimalFormat getDecimalFormat() {
		return decimalFormat;
	}

	@Override
	public List<Segment<T>> getSegments() {
		return segments;
	}

	@Override
	public boolean isEditable() {
		return editable;
	}

	@Override
	public void persist() {
		setter.accept(getValues());

		getScanningAcquisitionTemporaryHelper()
			.getAcquisitionController()
			.ifPresent(c -> {
				try {
					c.loadAcquisitionConfiguration(c.getAcquisition());
				} catch (AcquisitionControllerException e) {
					logger.error("Cannot load the new acquisition document", e);
				}
			});
	}

	private ScanningAcquisitionTemporaryHelper getScanningAcquisitionTemporaryHelper() {
		return SpringApplicationContextFacade.getBean(ScanningAcquisitionTemporaryHelper.class);
	}
}
