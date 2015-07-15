/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.printing.Printer;

import de.jaret.util.date.Interval;
import de.jaret.util.swt.SwtGraphicsHelper;
import de.jaret.util.ui.timebars.TimeBarViewerDelegate;
import de.jaret.util.ui.timebars.TimeBarViewerInterface;
import de.jaret.util.ui.timebars.swt.renderer.RendererBase;
import de.jaret.util.ui.timebars.swt.renderer.TimeBarRenderer;
import de.jaret.util.ui.timebars.swt.renderer.TimeBarRenderer2;
import uk.ac.gda.exafs.experiment.trigger.DetectorDataCollection;
import uk.ac.gda.exafs.experiment.trigger.TriggerableObject;
import uk.ac.gda.exafs.experiment.ui.ExternalTriggerDetailsTimebarComposite.TFGTriggerEvent;

/**
 * Renderer rendering a point in time as a simple diamod and a label (using extended painting area).
 *
 * @author Peter Kliem
 * @version $Id: FancyEventRenderer.java 565 2007-09-16 13:25:48Z olk $
 */
public class ExternalTriggerEventRenderer extends RendererBase implements TimeBarRenderer, TimeBarRenderer2 {
	/** size of the drawn element. */
	private static final int SIZE = 5;
	/** extend for the label. */
	private static final int MAXLABELWIDTH = 200;
	/** pixeloffset for the label drawing. */
	private static final int LABELOFFSET = -4;

	/** corrected size (for printing). */
	private int _size = SIZE;

	/** cache for the delegate supplying the orientation information. */
	protected TimeBarViewerDelegate _delegate;

	/**
	 * Create renderer for printing.
	 *
	 * @param printer printer device
	 */
	public ExternalTriggerEventRenderer(Printer printer) {
		super(printer);
		_size = scaleX(SIZE);
	}

	/**
	 * Construct renderer for screen use.
	 *
	 */
	public ExternalTriggerEventRenderer() {
		super(null);
	}

	/**
	 * {@inheritDoc}
	 */
	@Override
	public Rectangle getPreferredDrawingBounds(Rectangle intervalDrawingArea, TimeBarViewerDelegate delegate,
			Interval interval, boolean selected, boolean printing, boolean overlap) {

		boolean horizontal = delegate.getOrientation() == TimeBarViewerInterface.Orientation.HORIZONTAL;
		if (horizontal) {
			return new Rectangle(intervalDrawingArea.x - _size, intervalDrawingArea.y, intervalDrawingArea.width + 2
					* _size + scaleX(MAXLABELWIDTH), intervalDrawingArea.height);
		}
		return new Rectangle(intervalDrawingArea.x, intervalDrawingArea.y - _size, intervalDrawingArea.width,
				intervalDrawingArea.height + 2 * _size + scaleY(MAXLABELWIDTH));
	}

	/**
	 * {@inheritDoc}
	 */
	@Override
	public void draw(GC gc, Rectangle drawingArea, TimeBarViewerDelegate delegate, Interval interval, boolean selected,
			boolean printing, boolean overlap) {
		_delegate = delegate;
		defaultDraw(gc, drawingArea, delegate, interval, selected, printing, overlap);
	}

	/**
	 * {@inheritDoc}
	 */
	@Override
	public String getToolTipText(Interval interval, Rectangle drawingArea, int x, int y, boolean overlapping) {
		return getToolTipText(_delegate, interval, drawingArea, x, y, overlapping);
	}

	/**
	 * {@inheritDoc}
	 */
	@Override
	public boolean contains(Interval interval, Rectangle drawingArea, int x, int y, boolean overlapping) {
		return contains(_delegate, interval, drawingArea, x, y, overlapping);
	}

	/**
	 * {@inheritDoc}
	 */
	@Override
	public Rectangle getContainingRectangle(Interval interval, Rectangle drawingArea, boolean overlapping) {
		return getContainingRectangle(_delegate, interval, drawingArea, overlapping);
	}

	/**
	 * {@inheritDoc}. Will create print renderes for all registered renderers.
	 */
	@Override
	public TimeBarRenderer createPrintrenderer(Printer printer) {
		ExternalTriggerEventRenderer renderer = new ExternalTriggerEventRenderer(printer);
		return renderer;
	}

	/**
	 * {@inheritDoc}
	 */
	@Override
	public void dispose() {
	}

	/**
	 * Drawing method for default rendering.
	 *
	 * @param gc GC
	 * @param drawingArea drawingArea
	 * @param delegate delegate
	 * @param interval interval to draw
	 * @param selected true for selected drawing
	 * @param printing true for printing
	 * @param overlap true if the interval overlaps with other intervals
	 */
	private void defaultDraw(GC gc, Rectangle drawingArea, TimeBarViewerDelegate delegate, Interval interval,
			boolean selected, boolean printing, boolean overlap) {

		TFGTriggerEvent event = (TFGTriggerEvent) interval;
		TriggerableObject triggerable = event.getTriggerableObject();

		boolean horizontal = delegate.getOrientation() == TimeBarViewerInterface.Orientation.HORIZONTAL;
		Rectangle da = getDrawingRect(drawingArea, horizontal);

		// draw focus
		drawFocus(gc, da, delegate, interval, selected, printing, overlap);

		Color bg = gc.getBackground();

		// draw the duration if the event has one

		if (triggerable instanceof DetectorDataCollection) {
			gc.setBackground(gc.getDevice().getSystemColor(SWT.COLOR_CYAN));
			event.getSeconds();
		} else {
			gc.setBackground(gc.getDevice().getSystemColor(SWT.COLOR_DARK_YELLOW));
		}
		gc.fillRectangle(drawingArea);

		// draw the diamond
		gc.setBackground(gc.getDevice().getSystemColor(SWT.COLOR_GRAY));
		//		if (event.getColor() != null && event.getColor().equals("red")) {
		//			gc.setBackground(gc.getDevice().getSystemColor(SWT.COLOR_RED));
		//		}


		int[] points = new int[] {da.x, da.y + da.height / 2, da.x + da.width / 2, da.y, da.x + da.width,
				da.y + da.height / 2, da.x + da.width / 2, da.y + da.height};

		gc.fillPolygon(points);
		gc.drawPolygon(points);

		if (selected) {
			gc.setBackground(gc.getDevice().getSystemColor(SWT.COLOR_BLUE));
			gc.setAlpha(60);
			gc.fillPolygon(points);
			gc.setAlpha(255);
		}
		gc.setBackground(bg);

		String label = event.getTriggerableObject().getTriggerDelay() + " s, pulse width " + event.getTriggerableObject().getTriggerPulseLength() + " s";
		if (triggerable instanceof DetectorDataCollection) {
			label = label + ", collection time " + ((DetectorDataCollection) triggerable).getCollectionDuration() + " s";
		}
		// draw the label
		if (horizontal) {
			SwtGraphicsHelper.drawStringVCentered(gc, label, da.x + da.width + scaleX(LABELOFFSET), da.y + 12, da.y + 12
					+ da.height);
		} else {
			SwtGraphicsHelper.drawStringCentered(gc, label, da.x + da.width / 2, da.y + da.height
					+ scaleY(LABELOFFSET) + gc.textExtent(label).y);
		}

	}

	/**
	 * Calculate the drawing area for the marking symbol.
	 *
	 * @param drawingArea drawing area as given for the time
	 * @return Rectangle for drawing the main symbol
	 */
	private Rectangle getDrawingRect(Rectangle drawingArea, boolean horizontal) {
		if (horizontal) {
			int y = drawingArea.y + (drawingArea.height - 2 * _size) / 2;
			return new Rectangle(drawingArea.x - _size, y, 2 * _size, 2 * _size);
		}
		int x = drawingArea.x + (drawingArea.width - 2 * _size) / 2;
		return new Rectangle(x, drawingArea.y - _size, 2 * _size, 2 * _size);
	}

	@Override
	public String getToolTipText(TimeBarViewerDelegate delegate, Interval interval, Rectangle drawingArea, int x,
			int y, boolean overlapping) {
		if (contains(delegate, interval, drawingArea, x, y, overlapping)) {
			return "Pulse width " + ((TFGTriggerEvent) interval).getTriggerableObject().getTriggerPulseLength() + " s";
		}
		return null;
	}

	@Override
	public boolean contains(TimeBarViewerDelegate delegate, Interval interval, Rectangle drawingArea, int x, int y,
			boolean overlapping) {
		boolean horizontal = delegate.getOrientation() == TimeBarViewerInterface.Orientation.HORIZONTAL;
		Rectangle da = getDrawingRect(drawingArea, horizontal);
		return da.contains(drawingArea.x + x, drawingArea.y + y);
	}

	@Override
	public Rectangle getContainingRectangle(TimeBarViewerDelegate delegate, Interval interval, Rectangle drawingArea,
			boolean overlapping) {
		boolean horizontal = delegate.getOrientation() == TimeBarViewerInterface.Orientation.HORIZONTAL;
		Rectangle da = getDrawingRect(drawingArea, horizontal);
		return da;
	}

}
