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

/**
 * Represents a numeric value inside a text string.
 *
 * <p>
 * This class allows an editor to update a numerical substring inside a longer text.
 * </p>
 *
 *
 * @param <T>
 *
 * @author Maurizio Nagni
 */
public class Segment<T> {
	private final SegmentGroup<T> group;

	private String originalString;
	private String actualString;

	private double numericValue;

	private int start;

	/**
	 * Creates a new instance. For example, assuming the text
	 *
	 * <p>
	 * Assuming the text <i>Pi is almost 3.14</i>, a new segment for <i>3.14</i> would look like
     * <pre>
     * var group = new SegmentDoubleGroup(....)
     * new Segment(13, 3.14, group)
     * </pre>
	 * </p>
	 *
	 * <p>
	 * At the moment this class is unable to distinguish between {@code int} and {@code double},
	 * consequently it stores the actual value as double, while it returns the most appropriate string
	 * using the format defined in the {@code group}
	 * </p>
	 *
	 * <p>
	 * The {@code group} is used when the number managed by this segment is part of a larger collection, i.e. an array.
	 * </p>
	 *
	 * @param start the position in the text where this segment starts.
	 * @param numericValue the number to edit
	 * @param group the associated group
	 *
	 * @see GenericSegmentGroup#getDecimalFormat()
	 */
	public Segment(int start, double numericValue, SegmentGroup<T> group) {
		this.start = start;
		this.group = group;
		this.originalString = group.getDecimalFormat().format(numericValue);
		this.actualString = originalString;
		this.numericValue = numericValue;
	}

	/**
	 * Verifies if this segment contains elements for the given index.
	 *
	 * <p>
	 * For example, an external method wants to verify if, for the text which generated this segment,
	 * the cursor position, that is the {@code index}, is contained in this segment.
	 * </p>
	 *
	 * @param index the external text's character position
	 * @return {@code true} if this segment contains the given {@code index}, otherwise {@code false}.
	 */
	public boolean contains(int index) {
		return index >= start && index <= start + getActualString().length();
	}

	public int getStart() {
		return start;
	}

	public String getActualString() {
		return actualString;
	}


	/**
	 * Set a new string for this segment.
	 *
	 * <p>
	 * Calling this method does not change the internal numeric value. This method is used as temporary variable for the external editor.
	 * After calling this method {@code getGroup().getDecimalFormat().format(getNumericValue())} may differs from
	 * {@link #getActualString()}.
	 * </p>
	 *
	 * @param value
	 */
	public void setActualString(String value) {
		this.actualString = value;
	}

	/**
	 * The numeric value stored in this segment.
	 *
	 * @return the segment number to edit
	 */
	public double getNumericValue() {
		return numericValue;
	}

	/**
	 * Set a new number to edit for this segment.
	 *
	 * <p>
	 * After calling this method {@code getGroup().getDecimalFormat().format(getNumericValue())} will return same as
	 * {@link #getActualString()}
	 * </p>
	 *
	 * @param numericValue the new number
	 */
	public void setNumericValue(double numericValue) {
		this.numericValue = numericValue;
		this.originalString = getGroup().getDecimalFormat().format(numericValue);
	}

	/**
	 * Restores the original value
	 *
	 * <p>
	 * After calling this method {@code getGroup().getDecimalFormat().format(getNumericValue())} will return same as
	 * {@link #getActualString()}
	 * </p>
	 */
	public void restore() {
		this.originalString = getGroup().getDecimalFormat().format(getNumericValue());
		this.actualString = this.originalString;
	}

	public SegmentGroup<T> getGroup() {
		return group;
	}
}

