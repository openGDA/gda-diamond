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

package uk.ac.gda.beamline.i06.scannables;

import java.io.Serializable;

import org.springframework.expression.AccessException;
import org.springframework.expression.BeanResolver;
import org.springframework.expression.EvaluationContext;
import org.springframework.expression.Expression;
import org.springframework.expression.ExpressionParser;
import org.springframework.expression.spel.standard.SpelExpressionParser;
import org.springframework.expression.spel.support.StandardEvaluationContext;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.PVScannable;
import gda.device.scannable.ScannablePositionChangeEvent;
import gda.factory.FactoryException;
import gda.factory.Finder;

/**
 * A {@link Scannable} that its value depends on or related to other {@link Scannable}s. The dependency is defined in
 * <a href="https://docs.spring.io/spring/docs/4.3.10.RELEASE/spring-framework-reference/html/expressions.html">Spring Expression Language (SpEL)</a>.
 * {@link #setMoveToExpression(String)} defines expression for {@link #asynchronousMoveTo(Object)} method, {@link #setGetPositionExpression(String)} defines
 * expression for {@link #getPosition()} method.
 *
 * @since 9.17
 */
public class CoupledPVScannable extends PVScannable {
	private String moveToExpression;
	private String getPositionExpression;
	private ExpressionParser parser;
	private StandardEvaluationContext context;

	@Override
	public void configure() throws FactoryException {
		parser = new SpelExpressionParser();
		context = new StandardEvaluationContext();
		context.setBeanResolver(new BeanResolver() {

			@Override
			public Object resolve(EvaluationContext context, String beanName) throws AccessException {
				return Finder.getInstance().find(beanName);
			}
		});
		super.configure();
	}

	@Override
	public void asynchronousMoveTo(Object value) throws DeviceException {
		context.setVariable("input", Double.valueOf(value.toString()).doubleValue());
		Expression exp = parser.parseExpression(getMoveToExpression());
		double newValue = exp.getValue(context, Double.class);
		super.asynchronousMoveTo(newValue);
	}

	@Override
	public Object getPosition() throws DeviceException {
		return calculateNewPosition(Double.valueOf(super.getPosition().toString()).doubleValue());
	}

	@Override
	protected void notifyObserversOfNewPosition(Serializable newPosition) {
		this.notifyIObservers(this, new ScannablePositionChangeEvent(calculateNewPosition(Double.valueOf(newPosition.toString()).doubleValue())));
	}

	private double calculateNewPosition(double newPosition) {
		context.setVariable("output", newPosition);
		Expression exp = parser.parseExpression(getGetPositionExpression());
		double newValue = exp.getValue(context, Double.class);
		return newValue;
	}

	public String getMoveToExpression() {
		return moveToExpression;
	}

	public void setMoveToExpression(String moveToExpression) {
		this.moveToExpression = moveToExpression;
	}

	public String getGetPositionExpression() {
		return getPositionExpression;
	}

	public void setGetPositionExpression(String getPositionExpression) {
		this.getPositionExpression = getPositionExpression;
	}
}
