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

package uk.ac.diamond.daq.beamline.i06_shared.scannables;

import java.io.Serializable;
import java.util.List;

import org.springframework.expression.BeanResolver;
import org.springframework.expression.ExpressionParser;
import org.springframework.expression.spel.standard.SpelExpressionParser;
import org.springframework.expression.spel.support.StandardEvaluationContext;

import com.google.common.base.Strings;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.PVScannable;
import gda.factory.FactoryException;
import gda.factory.Finder;
import uk.ac.diamond.daq.beamline.i06_shared.spring.spel.SpELUtils;

/**
 * A {@link Scannable} that applies the given expressions {@link #getMoveToExpression()} in {@link #asynchronousMoveTo(Object)} and
 * {@link #getGetPositionExpression()} in {@link #getPosition()} respectively if they are set, otherwise it just behaviours like its parent {@link PVScannable}.
 * <p>
 * The expression for {@link #asynchronousMoveTo(Object)} can be set with {@link #setMoveToExpression(String)}. It supports variable '#input' representing the
 * input parameter to {@link #asynchronousMoveTo(Object)}; It also supports bean reference via notation of '@bean_name' in this expression for accessing other
 * beans using {@link Finder} utility in {@link BeanResolver}. The result of the expression evaluation is sent to
 * {@link PVScannable#asynchronousMoveTo(Object)}.
 * <p>
 * The expression for {@link #getPosition()} can be set with {@link #setGetPositionExpression(String)}. if supports variable '#output' representing the return
 * of {@link PVScannable#getPosition()}. It also supports bean reference via notation of '@bean_name' in this expression for accessing other beans using
 * {@link Finder} utility in {@link BeanResolver}. The result of expression evaluation is returned by {@link #getPosition()}.
 * <p>
 * Expression can be simple - i.e. one line or complex - i.e. multiple statements. For complex one we have to extend SpEL to use functions. Any function or
 * method used to extending SpEL must be defined in {@link SpELUtils} for this class. If the function/method takes formal parameters, both function name and
 * parameter types have to be specified as Java Reflection is used to return the register function.
 * <p>
 * All expressions, including function name and function parameter types, can be defined in bean definition.
 * <p>
 * For more information on SpEL, @see <a href="https://docs.spring.io/spring/docs/4.3.10.RELEASE/spring-framework-reference/html/expressions.html">Spring
 * Expression Language (SpEL)</a>.
 *<p>
 *
 * Example using function for complex algorithm that cannot be represented by one statement
 *<pre>
 * {@code
 * <bean id="medipixAcquireTime" class="uk.ac.gda.beamline.i06.scannables.SpELExpressionScannable">
 * 	<property name="pvName" value="BL06I-EA-DET-02:CAM:AcquireTime"/>
 * 	<property name="outputFormat">
 * 		<list>
 * 			<value>%4.3f</value>
 * 		</list>
 * 	</property>
 * 	<property name="functionNameToBeCalledInAsynchronousMoveTo" value="updateAcquirePeriodWhenAcquireTimeChanges"/>
 * 	<property name="functionParameterTypesTobeCalledInAsynchronousMoveTo">
 *		<list>
 *			<value>gda.device.Scannable</value>
 *			 <value>gda.device.Scannable</value>
 *			<value>java.lang.Double</value>
 *		</list>
 *	</property>
 *	<property name="moveToExpression" value="#updateAcquirePeriodWhenAcquireTimeChanges(@medipixExposureTime, @medipixAcquirePeriod, #input)"/>
 * </bean>
 * }
 *</pre>
 *
 *<p>
 * Example for one liner expression
 * <pre>
 *{@code
 *<bean id="medipixIdleTime" class="uk.ac.gda.beamline.i06.scannables.SpELExpressionScannable">
 *	<property name="pvName" value="BL06I-EA-DET-02:CAM:AcquirePeriod"/>
 *	<property name="outputFormat">
 *		<list>
 *			<value>%4.3f</value>
 *		</list>
 *	</property>
 *	<property name="moveToExpression" value="#input > 0.002 ? @medipixExposureTime.getPosition() + #input : @medipixExposureTime.getPosition() + 0.002"/>
 *	<property name="getPositionExpression" value="(#output - @medipixExposureTime.getPosition())>0.002 : #output - @medipixExposureTime.getPosition() : 0.002"/>
 *</bean>
 *}
 *</pre>
 *
 * For a full example @see /i06-config/clients/main/live/medipix_live_controls.xml
 * @since 9.16
 */
public class SpELExpressionScannable extends PVScannable {

	private String moveToExpression;
	private String getPositionExpression;
	private ExpressionParser parser;
	private StandardEvaluationContext context;
	private String functionNameToBeCalledInAsynchronousMoveTo;
	private List<Class<?>> functionParameterTypesToBeCalledInAsynchronousMoveTo;
	private String functionNameToBeCalledInGetPosition;
	private List<Class<?>> functionParameterTypesToBeCalledInGetPosition;

	@Override
	public void configure() throws FactoryException {
		parser = new SpelExpressionParser();
		context = new StandardEvaluationContext();
		context.setBeanResolver((ec,name) -> Finder.find(name));
		if (!Strings.isNullOrEmpty(getFunctionNameToBeCalledInAsynchronousMoveTo())) {
			// register function in SpELUtils class to be used inside asynchronuousMoveTo method of this class
			Class<?>[] parameterTypes = new Class[functionParameterTypesToBeCalledInAsynchronousMoveTo.size()];
			functionParameterTypesToBeCalledInAsynchronousMoveTo.toArray(parameterTypes);
			try {
				context.registerFunction(getFunctionNameToBeCalledInAsynchronousMoveTo(),
						SpELUtils.class.getDeclaredMethod(getFunctionNameToBeCalledInAsynchronousMoveTo(), parameterTypes));
			} catch (NoSuchMethodException | SecurityException e) {
				throw new FactoryException(e.getMessage(), e);
			}
		}
		if (!Strings.isNullOrEmpty(getFunctionNameToBeCalledInGetPosition())) {
			// register function in SpELUtils class to be used inside getPosition method of this class
			Class<?>[] parameterTypes = new Class[functionParameterTypesToBeCalledInGetPosition.size()];
			functionParameterTypesToBeCalledInGetPosition.toArray(parameterTypes);
			try {
				context.registerFunction(getFunctionNameToBeCalledInGetPosition(),
						SpELUtils.class.getDeclaredMethod(getFunctionNameToBeCalledInGetPosition(), parameterTypes));
			} catch (NoSuchMethodException | SecurityException e) {
				throw new FactoryException(e.getMessage(), e);
			}
		}
		super.configure();
	}

	/**
	 * {@inheritDoc}
	 * <p>
	 * This method transforms the given input using the SpEL expression if present before sending the result to PV.
	 */
	@Override
	public void asynchronousMoveTo(Object value) throws DeviceException {
		if (Strings.isNullOrEmpty(getMoveToExpression())) {
			super.asynchronousMoveTo(value);
		} else {
			context.setVariable("input", Double.parseDouble(value.toString()));
			if (Strings.isNullOrEmpty(getFunctionNameToBeCalledInAsynchronousMoveTo())) {
				super.asynchronousMoveTo(parser.parseExpression(getMoveToExpression()).getValue(context, Double.class));
			} else {
				// move call is done inside registered function
				parser.parseExpression(getMoveToExpression()).getValue(context);
			}
		}
	}

	/**
	 * {@inheritDoc}
	 * <p>
	 * This method transforms the return from PV using SpEL expression before returning the result.
	 */
	@Override
	public Object getPosition() throws DeviceException {
		return calculateNewPosition(super.getPosition());
	}

	@Override
	protected void notifyObserversOfNewPosition(Serializable newPosition) {
		Double calculateNewPosition = calculateNewPosition(newPosition);
		super.notifyObserversOfNewPosition(calculateNewPosition);
	}

	private Double calculateNewPosition(Object newPosition) {
		Double position = Double.parseDouble(newPosition.toString());
		if (Strings.isNullOrEmpty(getGetPositionExpression())) {
			return position;
		} else {
			context.setVariable("output", position);
			return parser.parseExpression(getGetPositionExpression()).getValue(context, Double.class);
		}
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

	public String getFunctionNameToBeCalledInAsynchronousMoveTo() {
		return functionNameToBeCalledInAsynchronousMoveTo;
	}

	public void setFunctionNameToBeCalledInAsynchronousMoveTo(String functionNameToBeCalledInAsynchronousMoveTo) {
		this.functionNameToBeCalledInAsynchronousMoveTo = functionNameToBeCalledInAsynchronousMoveTo;
	}

	public String getFunctionNameToBeCalledInGetPosition() {
		return functionNameToBeCalledInGetPosition;
	}

	public void setFunctionNameToBeCalledInGetPosition(String functionNameToBeCalledInGetPosition) {
		this.functionNameToBeCalledInGetPosition = functionNameToBeCalledInGetPosition;
	}

	public List<Class<?>> getFunctionParameterTypesTobeCalledInAsynchronousMoveTo() {
		return functionParameterTypesToBeCalledInAsynchronousMoveTo;
	}

	public void setFunctionParameterTypesTobeCalledInAsynchronousMoveTo(List<Class<?>> functionParameterTypesTobeCalledInAsynchronousMoveTo) {
		this.functionParameterTypesToBeCalledInAsynchronousMoveTo = functionParameterTypesTobeCalledInAsynchronousMoveTo;
	}

	public List<Class<?>> getFunctionParameterTypesToBeCalledInGetPosition() {
		return functionParameterTypesToBeCalledInGetPosition;
	}

	public void setFunctionParameterTypesToBeCalledInGetPosition(List<Class<?>> functionParameterTypesToBeCalledInGetPosition) {
		this.functionParameterTypesToBeCalledInGetPosition = functionParameterTypesToBeCalledInGetPosition;
	}

}
