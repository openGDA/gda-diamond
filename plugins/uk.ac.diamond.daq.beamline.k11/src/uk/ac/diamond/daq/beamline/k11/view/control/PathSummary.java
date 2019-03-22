/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.view.control;

import java.util.Arrays;
import java.util.List;

import org.eclipse.core.databinding.beans.PojoProperties;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.graphics.Font;
import org.eclipse.swt.graphics.FontData;
import org.eclipse.swt.widgets.Composite;

import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;

/**
 * An object to hold the summary of the region path selections made along with the corresponding control that displays
 * it and and enum to provide convenient typing of the region shapes.
 *
 * @since GDA 9.13
 */
public class PathSummary {
	private static final int PADDING = 15;

	private Shape shape = Shape.CENTRED_RECTANGLE;
	private double horizExtent = 10;
	private double vertExtent = 10;
	private double horizOrigin = 0;
	private double vertOrigin = 0;
	private int density = 25;
	private boolean continuous = false;
	private boolean snake = false;
	private boolean random = false;

	private IObservableValue<Integer> densityObservableValue;
	private IObservableValue<Shape> shapeObservableValue;
	private IObservableValue<Boolean> continuousObservableValue;
	private IObservableValue<Boolean> snakeObservableValue;
	private IObservableValue<Boolean> randomObservableValue;

	private List<IObservableValue<Double>> shapeCoordinateObservableValues;

	private StyledText control;


	PathSummary() {
		initaliseObservableValues();
	}

	/**
	 * Retrieves the {@link StyledText} control used to display the summary infomation
	 *
	 * @param parent	The containing {@link Composite for the control}
	 * @return			The populated {@link StyledText} control
	 */
	StyledText getControl (final Composite parent) {
		control = new StyledText(parent, SWT.BORDER);
		control.setMargins(PADDING, PADDING, PADDING, PADDING);
		control.setWordWrap(true);
		control.setFont(new Font(control.getDisplay(), new FontData("PT Sans Narrow", 13, SWT.NONE)));
		control.setCaret(null);
		control.setParent(parent);
		control.setEditable(false);
		update();
		return control;
	}

	/**
	 * Set up {@link IObservableValues} for each of the fields of the summary
	 */
	@SuppressWarnings("unchecked")
	private void initaliseObservableValues() {
		densityObservableValue = PojoProperties.value("density").observe(this);
		shapeObservableValue = PojoProperties.value("shape").observe(this);
		continuousObservableValue = PojoProperties.value("continuous").observe(this);
		snakeObservableValue = PojoProperties.value("snake").observe(this);
		randomObservableValue = PojoProperties.value("random").observe(this);
		shapeCoordinateObservableValues = Arrays.asList(
				PojoProperties.value("horizOrigin").observe(this),
				PojoProperties.value("vertOrigin").observe(this),
				PojoProperties.value("horizExtent").observe(this),
				PojoProperties.value("vertExtent").observe(this));
	}

	/**
	 * Refresh the content of the @link StyledText} control with updated text reflecting the current field values
	 */
	private void update() {
		if (control != null) {
			control.setText(getText());
		}
	}

	/**
	 * Fill in the text content based on the currently active {@link Shape}
	 *
	 * @return	The text content {@link String}
	 */
	private String getText() {

		StringBuilder text = new StringBuilder();
		switch (shape) {
			case POINT:
				text.append(String.format(
						"Point at %.1f, %.1f                                 \n\n", horizOrigin, vertOrigin));
				break;
			case CENTRED_RECTANGLE:
				text.append(String.format("Rectangle, %.1f x %.1f, centre %.1f, %.1f\n",
						horizExtent, vertExtent, horizOrigin, vertOrigin));
				text.append(String.format("%d points per side (%d total)\n",
						density, getTotalPoints()));
				text.append(String.format("%s %s %s",
						continuous ? "Continuous" : "Stepped",
						random ? " Randomised" : "",
						snake ? " Snake" : ""));
				break;
			case LINE:
				text.append(String.format("Line, %.1f x %.1f, to %.1f, %.1f\n",
						horizOrigin, vertOrigin, horizExtent, vertExtent));
				text.append(String.format("%d points \n", density));
				text.append(String.format("%s",	continuous ? "Continuous" : "Stepped"));
				break;
			default:

				break;
		}
		return text.toString();
	}

	public Shape getShape() {
		return shape;
	}

	public void setShape(final Shape selectedShape) {
		shape = selectedShape;
		update();
	}

	public double getHorizExtent() {
		return horizExtent;
	}

	public void setHorizExtent(double horizExtent) {
		this.horizExtent = horizExtent;
		update();
	}

	public double getVertExtent() {
		return vertExtent;
	}

	public void setVertExtent(double vertExtent) {
		this.vertExtent = vertExtent;
		update();
	}

	public double getHorizOrigin() {
		return horizOrigin;
	}

	public void setHorizOrigin(double horizOrigin) {
		this.horizOrigin = horizOrigin;
		update();
	}

	public double getVertOrigin() {
		return vertOrigin;
	}

	public void setVertOrigin(double vertOrigin) {

		this.vertOrigin = vertOrigin;
		update();
	}

	public int getDensity() {
		return density;
	}

	public void setDensity(final int selecteddensity) {
		density = (selecteddensity > 0) ? selecteddensity : 0;
		update();
	}

	public boolean getContinuous() {
		return continuous;
	}

	public void setContinuous(boolean continuous) {
		this.continuous = continuous;
		update();
	}

	public boolean getRandom() {
		return random;
	}

	public void setRandom(boolean random) {
		this.random = random;
		update();
	}

	public boolean getSnake() {
		return snake;
	}

	public void setSnake(boolean snake) {
		this.snake = snake;
		update();
	}

	public List<IObservableValue<Double>> getShapeCoordinateObservableValues() {
		return shapeCoordinateObservableValues;
	}

	public IObservableValue<Integer> getDensityObservableValue() {
		return densityObservableValue;
	}


	public IObservableValue<Boolean> getContinuousObservableValue() {
		return continuousObservableValue;
	}

	public  IObservableValue<Boolean> getSnakeObservableValue() {
		return snakeObservableValue;
	}

	public  IObservableValue<Boolean> getRandomOffsetObservableValue() {
		return randomObservableValue;
	}

	public int getTotalPoints() {
		return density * density;
	}

	public final StyledText getControl() {
		return control;
	}

	public IObservableValue<Shape> getShapeObservableValue() {
		return shapeObservableValue;
	}

	public void dispose() {
		control.dispose();
		control = null;
		densityObservableValue.dispose();
		densityObservableValue = null;
		shapeObservableValue.dispose();
		shapeObservableValue = null;
		continuousObservableValue.dispose();
		continuousObservableValue = null;
		snakeObservableValue.dispose();
		snakeObservableValue = null;
		randomObservableValue.dispose();
		randomObservableValue = null;

		shapeCoordinateObservableValues.forEach(o -> {o.dispose(); o = null;});
	}

	enum Shape {
		POINT("Point"),
		CENTRED_RECTANGLE("Centred Rectangle"),
		LINE("Line");

		private String mappingScanRegionName;

		private Shape(final String name) {
			mappingScanRegionName = name;
		}

		public static final Shape fromRegionName(String name) {
			name = name.replace(' ', '_');
			try {
				return  valueOf(name.toUpperCase());
			} catch (IllegalArgumentException e) {
				return POINT;
			}
		}

		public static final Shape fromMappingScanRegion(IMappingScanRegionShape regionShape) {
			return fromRegionName(regionShape.getName());
		}

		public final String getMappingScanRegionName() {
			return mappingScanRegionName;
		}
	}
}
