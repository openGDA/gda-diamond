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

package uk.ac.gda.exafs.ui.data.experiment;

import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.printing.Printer;

import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import de.jaret.util.ui.timebars.TimeBarViewerDelegate;
import de.jaret.util.ui.timebars.swt.TimeBarViewer;
import de.jaret.util.ui.timebars.swt.renderer.RendererBase;
import de.jaret.util.ui.timebars.swt.renderer.TimeScaleRenderer;


public class TimingGroupsScaleRenderer extends RendererBase implements TimeScaleRenderer {

	private static final int PREFERREDHEIGHT = 30;
	private final TimeResolvedExperimentModel model;

	public TimingGroupsScaleRenderer(TimeResolvedExperimentModel model) {
		super(null);
		this.model = model;
	}

	public TimingGroupsScaleRenderer(Printer painter, TimeResolvedExperimentModel model) {
		super(painter);
		this.model = model;
	}

	@Override
	public void draw(GC gc, Rectangle drawingArea, TimeBarViewerDelegate delegate, boolean top, boolean printing) {
		for (Object timingGroup :model.getGroupList()) {
			TimingGroupUIModel timingGroupModel = (TimingGroupUIModel) timingGroup;
			int x = delegate.xForDate(timingGroupModel.getEnd());
			int startY = drawingArea.y + drawingArea.height - PREFERREDHEIGHT + 3;
			gc.drawRectangle(x - 1, startY, 1, PREFERREDHEIGHT + 3);
			String endTimeString = DataHelper.roundDoubletoStringWithOptionalDigits(model.getUnit().getWorkingUnit().convertFromMilli(timingGroupModel.getEndTime())) + " " + model.getUnit().getWorkingUnit().getUnitText();
			Point point = gc.stringExtent(endTimeString);
			gc.drawString(endTimeString, x - point.x - 10, startY + PREFERREDHEIGHT - point.y - 10);
		}
	}

	@Override
	public String getToolTipText(TimeBarViewer tbv, Rectangle drawingArea, int x, int y) {
		return "";
	}

	@Override
	public int getHeight() {
		if (_printer == null) {
			return PREFERREDHEIGHT;
		}
		return scaleY(PREFERREDHEIGHT);
	}

	@Override
	public boolean supportsOptimizedScrolling() {
		return true;
	}

	@Override
	public void dispose() {
		// nothing to dispose
	}

	@Override
	public TimeScaleRenderer createPrintRenderer(Printer printer) {
		return new TimingGroupsScaleRenderer(printer, model);
	}
}