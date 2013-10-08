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

import java.util.ArrayList;

import org.eclipse.swt.graphics.Rectangle;

import de.jaret.util.date.JaretDate;
import de.jaret.util.date.iterator.DateIterator;
import de.jaret.util.date.iterator.DayIterator;
import de.jaret.util.date.iterator.HourIterator;
import de.jaret.util.date.iterator.IIteratorFormatter;
import de.jaret.util.date.iterator.MillisecondIterator;
import de.jaret.util.date.iterator.MinuteIterator;
import de.jaret.util.date.iterator.MonthIterator;
import de.jaret.util.date.iterator.SecondIterator;
import de.jaret.util.date.iterator.WeekIterator;
import de.jaret.util.date.iterator.YearIterator;
import de.jaret.util.ui.timebars.swt.TimeBarViewer;
import de.jaret.util.ui.timebars.swt.renderer.BoxTimeScaleRenderer;


public class MilliScale extends BoxTimeScaleRenderer {

	public MilliScale() {
		super();
		_numberOfStrips = 2;
		initIterators();
	}

	@Override
	public String getToolTipText(TimeBarViewer tbv, Rectangle drawingArea, int x, int y) {
		return "";
	}

	private static class CustomSecondIterator extends SecondIterator {
		public CustomSecondIterator(int secondStep) {
			super(secondStep);
			_defaultFormatter = new IIteratorFormatter() {

				@Override
				public String getLabel(JaretDate date, Format format) {
					return NF.format(date.getMinutes()) + "m " + NF.format(date.getSeconds()) + "s";
				}
			};
		}
	}

	private static class CustomMilliSecondIterator extends MillisecondIterator {
		public CustomMilliSecondIterator(long millisecondStep) {
			super(millisecondStep);
			_defaultFormatter = new IIteratorFormatter() {
				@Override
				public String getLabel(JaretDate date, Format format) {
					return NF.format(date.getSeconds()) +"s " + date.getMillis() + "ms";
				}
			};
		}
	}

	private void initIterators() {
		_iterators = new ArrayList<DateIterator>();
		_formats = new ArrayList<DateIterator.Format>();
		_enable = new ArrayList<Boolean>();

		_iterators.add(new CustomMilliSecondIterator(10));
		_formats.add(DateIterator.Format.SHORT);
		_enable.add(true);


		_iterators.add(new CustomMilliSecondIterator(20));
		_formats.add(DateIterator.Format.SHORT);
		_enable.add(true);

		_iterators.add(new CustomMilliSecondIterator(50));
		_formats.add(DateIterator.Format.SHORT);
		_enable.add(true);

		_iterators.add(new CustomMilliSecondIterator(100));
		_formats.add(DateIterator.Format.SHORT);
		_enable.add(true);

		_iterators.add(new CustomMilliSecondIterator(500));
		_formats.add(DateIterator.Format.SHORT);
		_enable.add(true);

		_iterators.add(new CustomSecondIterator(1));
		_formats.add(DateIterator.Format.SHORT);
		_enable.add(true);

		_iterators.add(new CustomSecondIterator(5));
		_formats.add(DateIterator.Format.SHORT);
		_enable.add(true);

		_iterators.add(new CustomSecondIterator(30));
		_formats.add(DateIterator.Format.SHORT);
		_enable.add(true);

		_iterators.add(new MinuteIterator(1));
		_formats.add(DateIterator.Format.LONG);
		_enable.add(true);

		_iterators.add(new MinuteIterator(10));
		_formats.add(DateIterator.Format.LONG);
		_enable.add(true);

		_iterators.add(new MinuteIterator(30));
		_formats.add(DateIterator.Format.LONG);
		_enable.add(true);

		_iterators.add(new HourIterator(3));
		_formats.add(DateIterator.Format.LONG);
		_enable.add(true);

		_iterators.add(new HourIterator(12));
		_formats.add(DateIterator.Format.LONG);
		_enable.add(true);

		_iterators.add(new DayIterator());
		_formats.add(DateIterator.Format.LONG);
		_enable.add(true);

		_iterators.add(new WeekIterator());
		_formats.add(DateIterator.Format.LONG);
		_enable.add(true);

		_iterators.add(new MonthIterator());
		_formats.add(DateIterator.Format.LONG);
		_enable.add(true);

		_iterators.add(new YearIterator());
		_formats.add(DateIterator.Format.LONG);
		_enable.add(true);
	}
}