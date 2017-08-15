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

import org.dawnsci.ede.DataHelper;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.Font;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.widgets.Display;

import de.jaret.util.date.Interval;
import de.jaret.util.ui.timebars.TimeBarViewerDelegate;
import de.jaret.util.ui.timebars.TimeBarViewerInterface;
import de.jaret.util.ui.timebars.swt.renderer.DefaultRenderer;

public class CollectionModelRenderer extends DefaultRenderer {

	private final Font titleFont;
	private final TimeResolvedExperimentModel model;

	@Override
	protected Rectangle getIRect(boolean horizontal, Rectangle drawingArea, boolean overlap) {
		int height = drawingArea.height;
		int y = drawingArea.y;
		return new Rectangle(drawingArea.x, y, drawingArea.width - 1, height - 1);
	}

	public CollectionModelRenderer(TimeResolvedExperimentModel model) {
		titleFont = new Font(Display.getCurrent(), "Arial", 12, SWT.BOLD);
		this.model = model;
	}

	@Override
	public void draw(GC gc, Rectangle drawingArea, TimeBarViewerDelegate delegate, Interval interval, boolean selected,
			boolean printing, boolean overlap) {
		_delegate = delegate;
		// draw focus
		drawFocus(gc, drawingArea, delegate, interval, selected, printing, overlap);
		boolean horizontal = delegate.getOrientation() == TimeBarViewerInterface.Orientation.HORIZONTAL;
		Rectangle iRect = getIRect(horizontal, drawingArea, overlap);

		Color bg = gc.getBackground();

		if (!selected) {
			if (interval instanceof SpectrumModel) {
				gc.setBackground(Display.getCurrent().getSystemColor(SWT.COLOR_BLUE));
			} else {
				gc.setBackground(Display.getCurrent().getSystemColor(SWT.COLOR_DARK_GRAY));
			}
		} else {
			gc.setBackground(Display.getCurrent().getSystemColor(SWT.COLOR_DARK_CYAN));
		}
		gc.fillRectangle(iRect);
		gc.drawRectangle(iRect);
		Color fg = gc.getForeground();
		gc.setForeground((Display.getCurrent().getSystemColor(SWT.COLOR_WHITE)));
		if (interval instanceof TimeIntervalDataModel) {
			TimeIntervalDataModel collectionModel = (TimeIntervalDataModel) interval;
			StringBuilder name = new StringBuilder(collectionModel.getName());

			Font currentFont = gc.getFont();
			if (interval instanceof TimingGroupUIModel) {
				gc.setFont(titleFont);
			}
			Point point = gc.stringExtent(name.toString());
			if (point.y < iRect.height - 5 && point.x < iRect.width) {
				gc.drawText(name.toString(), iRect.x + 5, iRect.y + 3);
			}
			gc.setFont(currentFont);
			if (interval instanceof TimingGroupUIModel) {
				TimingGroupUIModel groupModel = (TimingGroupUIModel) interval;
				int numberOfSpectrums = groupModel.getNumberOfSpectrum();
				String spectra = "No. of Spectra: " + numberOfSpectrums;
				point = gc.stringExtent(spectra);
				if (point.y < iRect.height - 30  && point.x + 5 < iRect.width) {
					gc.drawText(spectra, iRect.x + 5, iRect.y + 20);
				}
				String timeResolution = DataHelper.roundDoubletoStringWithOptionalDigits(model.getUnit().getWorkingUnit().convertFromDefaultUnit(groupModel.getTimeResolution())) + " " + model.getUnit().getWorkingUnit().getUnitText();
				String noOfSpectrum = "Time per spectrum: " +  timeResolution;
				point = gc.stringExtent(noOfSpectrum);
				if (point.y < iRect.height - 45 && point.x + 5 < iRect.width) {
					gc.drawText(noOfSpectrum, iRect.x + 5, iRect.y + 35);
				}
			}
		}
		gc.setBackground(bg);
		gc.setForeground(fg);
	}
}
