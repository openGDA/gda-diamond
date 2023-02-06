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

import static uk.ac.gda.ui.tool.browser.ScanningAcquisitionBrowserBase.getAcquisitionParameters;

import java.util.EnumMap;
import java.util.Map;

import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.StyledString;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.jface.viewers.Viewer;
import org.eclipse.jface.viewers.ViewerComparator;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Image;

import gda.rcp.views.Browser;
import uk.ac.diamond.daq.mapping.api.document.scanning.ScanningParameters;
import uk.ac.gda.api.acquisition.TrajectoryShape;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.browser.IComparableStyledLabelProvider;
import uk.ac.gda.ui.tool.images.ClientImages;

/**
 * Extracts from the {@link ScanningParameters} a value for the shape for a {@link Browser} column.
 *
 * @author Maurizio Nagni
 */
class ShapeLabelProvider extends LabelProvider implements IComparableStyledLabelProvider {

	private static final Map<TrajectoryShape, ClientImages> ICONS = new EnumMap<>(TrajectoryShape.class);

	public ShapeLabelProvider() {
		System.out.println("ShapeLabelProvider created :-)");
	}

	static {
		ICONS.put(TrajectoryShape.TWO_DIMENSION_POINT, ClientImages.POINT);
		ICONS.put(TrajectoryShape.TWO_DIMENSION_LINE, ClientImages.LINE);
		ICONS.put(TrajectoryShape.TWO_DIMENSION_GRID, ClientImages.CENTERED_RECTAGLE);
		ICONS.put(TrajectoryShape.STATIC_POINT, ClientImages.BEAM_SELECTOR);
	}

	/**
	 * Return the standard image representing the region shape of the scan or null if there is no matching icon file
	 */
	@Override
	public Image getImage(Object element) {
		var trajectories = getAcquisitionParameters(element).getScanpathDocument().getTrajectories();
		ClientImages icon = switch (trajectories.size()) {
			case 1 -> ICONS.getOrDefault(trajectories.get(0).getShape(), ClientImages.NO_IMAGE);
			case 2 -> ClientImages.CUBE;
			default -> ClientImages.NO_IMAGE;
		};

		return ClientSWTElements.getImage(icon);
	}

	/**
	 * No text required for this column
	 */
	@Override
	public StyledString getStyledText(Object element) {
		return new StyledString();
	}

	@Override
	public ViewerComparator getComparator() {
		return new ViewerComparator() {
			@Override
			public int compare(Viewer viewer, Object element1, Object element2) {
				TrajectoryShape first = getAcquisitionParameters(element1).getScanpathDocument().getTrajectories().get(0).getShape();
				TrajectoryShape second = getAcquisitionParameters(element2).getScanpathDocument().getTrajectories().get(0).getShape();

				int direction = ((TreeViewer) viewer).getTree().getSortDirection() == SWT.UP ? 1 : -1;
				return direction * (first.ordinal() < second.ordinal() ? 1 : -1);
			}
		};
	}

}
