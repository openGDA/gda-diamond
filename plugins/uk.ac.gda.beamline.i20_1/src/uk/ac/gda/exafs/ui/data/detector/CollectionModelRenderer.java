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

package uk.ac.gda.exafs.ui.data.detector;

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.widgets.Display;

import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.exafs.data.ClientConfig.UnitSetup;
import de.jaret.util.date.Interval;
import de.jaret.util.ui.timebars.TimeBarViewerDelegate;
import de.jaret.util.ui.timebars.TimeBarViewerInterface;
import de.jaret.util.ui.timebars.swt.renderer.DefaultRenderer;

public class CollectionModelRenderer extends DefaultRenderer {
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
			if (interval instanceof Spectrum) {
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
		if (interval instanceof CollectionModel) {
			CollectionModel collectionModel = (CollectionModel) interval;
			String str = collectionModel.getName();
			Point point = gc.stringExtent(str);
			if (point.y < iRect.height - 5 && point.x < iRect.width) {
				gc.drawText(str, iRect.x + 5, iRect.y + 3);
			}
			str = DataHelper.roundDoubletoString(collectionModel.getDuration()) + " " + UnitSetup.MILLI_SEC.getText();
			point = gc.stringExtent(str);
			if (point.y < iRect.height - 15  && point.x + 5 < iRect.width) {
				gc.drawText(str, iRect.x + 5, iRect.y + 20);
			}
			if (interval instanceof Group) {
				str = Integer.toString(((Group) interval).getNumberOfSpectrums()) + " spectrum";
				point = gc.stringExtent(str);
				if (point.y < iRect.height - 30 && point.x + 5 < iRect.width) {
					gc.drawText(str, iRect.x + 5, iRect.y + 35);
				}
			}
		}
		gc.setBackground(bg);
		gc.setForeground(fg);
	}
}
