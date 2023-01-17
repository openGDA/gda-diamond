/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.browser;

import java.util.Optional;

import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.StyledString;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jface.viewers.ViewerComparator;
import org.eclipse.swt.SWT;

import gda.rcp.views.Browser;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument.Axis;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanningParametersUtils;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScanpathDocument;
import uk.ac.diamond.daq.mapping.api.document.scanpath.Trajectory;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientMessagesUtility;
import uk.ac.gda.ui.tool.browser.IComparableStyledLabelProvider;
import uk.ac.gda.ui.tool.browser.ScanningAcquisitionBrowserBase;

/**
 * Provides a summary of 2D path in {@link ScanningParameters} configurations for a column in a {@link Browser}
 *
 * @author Maurizio Nagni
 */
class DetailsLabelProvider extends LabelProvider implements IComparableStyledLabelProvider {


	@Override
	public StyledString getStyledText(Object element) {
		String message = Optional.ofNullable(ScanningAcquisitionBrowserBase.getAcquisitionParameters(element))
			.map(ScanningParameters::getScanpathDocument)
			.map(this::getDetailsSummary)
			.orElseGet(() -> ClientMessagesUtility.getMessage(ClientMessages.MISSING_MESSAGE));

		return new StyledString(message);
	}

	private String getDetailsSummary(ScanpathDocument scan) {
		var trajectories = scan.getTrajectories();
		return switch (trajectories.size()) {
			case 2 -> getThreeDimensionalGridDetails(scan);
			case 1 ->
				switch (trajectories.get(0).getShape()) {
					case STATIC_POINT -> getBeamSelectorScanDetails(trajectories.get(0));
					case TWO_DIMENSION_GRID -> getGridDetails(trajectories.get(0));
					case TWO_DIMENSION_LINE -> getLineDetails(trajectories.get(0));
					case TWO_DIMENSION_POINT -> getPointDetails(trajectories.get(0));
					default -> "Details unavailable";
				};

			default -> "Details unavailable";
		};
	}

	private String getThreeDimensionalGridDetails(ScanpathDocument scan) {
		var x = ScanningParametersUtils.getAxis(scan, Axis.X);
		var y = ScanningParametersUtils.getAxis(scan, Axis.Y);
		var theta = ScanningParametersUtils.getAxis(scan, Axis.THETA);
		return String.format("%d (X) x %d (Y) x %d (θ) points", x.getPoints(), y.getPoints(), theta.getPoints());
	}

	private String getGridDetails(Trajectory trajectory) {
		ScannableTrackDocument track1 = trajectory.getAxes().get(0);
		ScannableTrackDocument track2 = trajectory.getAxes().get(1);
		String axes = getAxesString(track1, track2);
		return String.format("%s%d x %d points; (%.1f, %.1f) to (%.1f, %.1f)",
				axes,
				track1.getPoints(), track2.getPoints(),
				track1.getStart(), track2.getStart(),
				track1.getStop(), track2.getStop());
	}

	private String getLineDetails(Trajectory trajectory) {
		ScannableTrackDocument track1 = trajectory.getAxes().get(0);
		ScannableTrackDocument track2 = trajectory.getAxes().get(1);
		String axes = getAxesString(track1, track2);
		return String.format("%s%d points; (%.1f, %.1f) to (%.1f, %.1f)",
				axes,
				track1.getPoints(),
				track1.getStart(), track2.getStart(),
				track1.getStop(), track2.getStop());
	}

	private String getPointDetails(Trajectory trajectory) {
		ScannableTrackDocument track1 = trajectory.getAxes().get(0);
		ScannableTrackDocument track2 = trajectory.getAxes().get(1);
		String axes = getAxesString(track1, track2);
		return String.format("%s(%.1f, %.1f)",
				axes,
				track1.getStart(), track2.getStart());
	}

	private String getBeamSelectorScanDetails(Trajectory trajectory) {
		return String.format("%d points", trajectory.getAxes().get(0).getPoints());
	}

	private String getAxesString(ScannableTrackDocument track1, ScannableTrackDocument track2) {
		if (track1.getAxis() != null && track2.getAxis()!= null) {
			return String.format("Axes: [%s,%s],", track1.getAxis(), track2.getAxis());
		}
		return "";
	}

	/** Sorts by number of points along first axis */
	@Override
	public ViewerComparator getComparator() {
		return new ViewerComparator() {
			@Override
			public int compare(Viewer viewer, Object element1, Object element2) {

				int direction = ((TreeViewer) viewer).getTree().getSortDirection() == SWT.UP ? 1 : -1;

				ScanningParameters first = ScanningAcquisitionBrowserBase.getAcquisitionParameters(element1);
				ScanningParameters second = ScanningAcquisitionBrowserBase.getAcquisitionParameters(element2);

				return direction * (first.getScanpathDocument().getTrajectories().get(0).getAxes().get(0).getPoints()
						< second.getScanpathDocument().getTrajectories().get(0).getAxes().get(0).getPoints() ? 1 : -1);
			}
		};
	}

}
