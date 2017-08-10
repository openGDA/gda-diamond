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

package uk.ac.gda.exafs.experiment.ui;

import org.dawnsci.ede.herebedragons.DataHelper;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.printing.Printer;

import de.jaret.util.date.Interval;
import de.jaret.util.ui.timebars.TimeBarViewerDelegate;
import de.jaret.util.ui.timebars.swt.TimeBarViewer;
import de.jaret.util.ui.timebars.swt.renderer.RendererBase;
import de.jaret.util.ui.timebars.swt.renderer.TimeScaleRenderer;
import uk.ac.gda.exafs.experiment.ui.data.CyclicExperimentDataModel;
import uk.ac.gda.exafs.experiment.ui.data.CyclicExperimentModel;
import uk.ac.gda.exafs.experiment.ui.data.ExperimentUnit;

public class CyclesTimebarScaleRenderer extends RendererBase implements TimeScaleRenderer {

	private static final int PREFERREDHEIGHT = 30;
	private final CyclicExperimentModel model;

	public CyclesTimebarScaleRenderer(CyclicExperimentModel model) {
		super(null);
		this.model = model;
	}

	public CyclesTimebarScaleRenderer(Printer painter, CyclicExperimentModel model) {
		super(painter);
		this.model = model;
	}

	@Override
	public void draw(GC gc, Rectangle drawingArea, TimeBarViewerDelegate delegate, boolean top, boolean printing) {
		// FIXME This could be slow!
		for (Interval interval : delegate.getRow(0).getIntervals()) {
			int x = delegate.xForDate(interval.getEnd());
			int startY = drawingArea.y + drawingArea.height - PREFERREDHEIGHT + 3;
			gc.drawRectangle(x - 1, startY, 1, PREFERREDHEIGHT + 3);
			String endTimeString = DataHelper.roundDoubletoStringWithOptionalDigits(ExperimentUnit.DEFAULT_EXPERIMENT_UNIT.convertTo((((CyclicExperimentDataModel) interval).getEndTime()), model.getUnit())) + " " + model.getUnit().getUnitText();
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
		return new CyclesTimebarScaleRenderer(printer, model);
	}
}