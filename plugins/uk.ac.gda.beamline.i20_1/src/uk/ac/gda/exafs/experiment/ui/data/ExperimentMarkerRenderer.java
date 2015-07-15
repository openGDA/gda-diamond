/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.experiment.ui.data;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.widgets.Display;

import de.jaret.util.ui.timebars.TimeBarMarker;
import de.jaret.util.ui.timebars.TimeBarViewerDelegate;
import de.jaret.util.ui.timebars.swt.renderer.DefaultTimeBarMarkerRenderer;
import uk.ac.gda.beamline.i20_1.utils.ExperimentTimeHelper;

public class ExperimentMarkerRenderer extends DefaultTimeBarMarkerRenderer {
	// This class should be created when display is ready :-)
	private static final Color TOP_UP_MARKER_COLOR = Display.getCurrent().getSystemColor(SWT.COLOR_GREEN);
	private static final Color SCANNING_MARKER_COLOR = Display.getCurrent().getSystemColor(SWT.COLOR_RED);

	@Override
	public void draw(GC gc, TimeBarViewerDelegate tbv, TimeBarMarker marker, boolean isDragged, boolean printing) {
		Color oldFgCol = gc.getForeground();
		Color oldBgCol = gc.getBackground();
		int startY = Math.min(tbv.getXAxisRect().y, tbv.getDiagramRect().y);
		int x = tbv.xForDate(marker.getDate());
		int height = tbv.getXAxisRect().height + tbv.getDiagramRect().height;
		if (marker instanceof TimeResolvedExperimentModel.Topup) {
			gc.setBackground(TOP_UP_MARKER_COLOR);
			int x1 = tbv.xForDate(marker.getDate().copy().advanceSeconds(TimeResolvedExperimentModel.TOP_UP_DURATION_IN_SECONDS));
			int width = x1 - x;
			gc.fillRectangle(x, startY, width, height);
			int x2 = tbv.xForDate(ExperimentTimeHelper.getTime());
			gc.fillRectangle(x2 - width, startY, width, height);
		} else {
			gc.setForeground(SCANNING_MARKER_COLOR);
			gc.drawLine(x, startY, x, startY + height);
		}
		gc.setLineWidth(1);
		gc.setForeground(oldFgCol);
		gc.setBackground(oldBgCol);
	}

	@Override
	public int getWidth(TimeBarMarker marker) {
		return super.getWidth(marker);
	}

}
