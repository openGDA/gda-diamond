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
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.expression.AccessException;
import org.springframework.expression.BeanResolver;
import org.springframework.expression.EvaluationContext;
import org.springframework.expression.Expression;
import org.springframework.expression.ExpressionParser;
import org.springframework.expression.spel.standard.SpelExpressionParser;
import org.springframework.expression.spel.support.StandardEvaluationContext;

import com.google.common.base.Strings;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.PVScannable;
import gda.device.scannable.ScannablePositionChangeEvent;
import gda.factory.FactoryException;
import gda.factory.Finder;
import uk.ac.gda.beamline.i06.spring.spel.SpELUtils;
import uk.ac.gda.beamline.i06.utils.Either;

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
 * All expressions, including function name and funtion parameter types, can be defined in bean definition.
 * <p>
 * For more information on SpEL, @see <a href="https://docs.spring.io/spring/docs/4.3.10.RELEASE/spring-framework-reference/html/expressions.html">Spring
 * Expression Language (SpEL)</a>.
 *<p>
 * Example bean definition:
 * <pre>
 * {@code
 * 	<bean id="medipixAcquireTime" class="uk.ac.gda.beamline.i06.scannables.SpELExpressionScannable">
 * 		<property name="pvName" value="BL06I-EA-DET-02:CAM:AcquireTime"/>
 * 		<property name="outputFormat">
 * 			<list>
 * 				<value>%4.3f</value>
 * 			</list>
 * 		</property>
 * 		<property name="functionNameToBeCalledInAsynchronousMoveTo" value="updateAcquirePeriodWhenAcquireTimeChanges"/>
 * 		<property name="functionParameterTypesTobeCalledInAsynchronousMoveTo">
 * 			<list>
 * 				<value>gda.device.Scannable</value>
 * 				<value>gda.device.Scannable</value>
 *				<value>java.lang.Double</value>
 *			</list>
 *		</property>
 *		<property name="moveToExpression" value="#updateAcquirePeriodWhenAcquireTimeChanges(@medipixExposureTime, @medipixAcquirePeriod, #input)"/>
 *	</bean>
 *	<bean id="medipixIdleTime" class="uk.ac.gda.beamline.i06.scannables.SpELExpressionScannable">
 *		<property name="pvName" value="BL06I-EA-DET-02:CAM:AcquirePeriod"/>
 *		<property name="outputFormat">
 *			<list>
 *				<value>%4.3f</value>
 *			</list>
 *		</property>
 *		<property name="moveToExpression" value="#input > 0.002 ? @medipixExposureTime.getPosition() + #input : @medipixExposureTime.getPosition() + 0.002"/>
 *		<property name="getPositionExpression" value="(#output - @medipixExposureTime.getPosition())>0.002 : #output - @medipixExposureTime.getPosition() : 0.002"/>
 *	</bean>
 *}
 * </pre>
 *
 * For a full example @see /i06-config/clients/main/live/medipix_live_controls.xml
 * @since 9.16
 */
public class SpELExpressionScannable extends PVScannable {

	private static final Logger logger = LoggerFactory.getLogger(SpELExpressionScannable.class);

	private String moveToExpression;
	private String getPositionExpression;
	private ExpressionParser parser;
	private StandardEvaluationContext context;
	private String functionNameToBeCalledInAsynchronousMoveTo;
	private List<String> functionParameterTypesTobeCalledInAsynchronousMoveTo;
	private String functionNameToBeCalledInGetPosition;
	private List<String> functionParameterTypesToBeCalledInGetPosition;

	@Override
	public void configure() throws FactoryException {
		parser = new SpelExpressionParser();
		context = new StandardEvaluationContext();
		context.setBeanResolver(new BeanResolver() {

			@Override
			public Object resolve(EvaluationContext context, String beanName) throws AccessException {
				return Finder.find(beanName);
			}
		});
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
			context.setVariable("input", Double.valueOf(value.toString()).doubleValue());
			if (Strings.isNullOrEmpty(getFunctionNameToBeCalledInAsynchronousMoveTo())) {
				// support simple SpEL expression
				Expression exp = parser.parseExpression(getMoveToExpression());
				double newValue = exp.getValue(context, Double.class);
				super.asynchronousMoveTo(newValue);
			} else {
				// support complex algorithm implemented as method in SpELUtils class
				Class<?>[] parameterTypes = getParameterTypes(functionParameterTypesTobeCalledInAsynchronousMoveTo);
				try {
					context.registerFunction(getFunctionNameToBeCalledInAsynchronousMoveTo(),
							SpELUtils.class.getDeclaredMethod(getFunctionNameToBeCalledInAsynchronousMoveTo(), parameterTypes));
					parser.parseExpression(getMoveToExpression()).getValue(context);
				} catch (NoSuchMethodException | SecurityException e) {
					logger.error("Cannot find the given method {}", getFunctionNameToBeCalledInAsynchronousMoveTo(), e);
					throw new DeviceException(e.getMessage(), e);
				}
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
		return calculateNewPosition(Double.valueOf(super.getPosition().toString()).doubleValue());
	}

	@Override
	protected void notifyObserversOfNewPosition(Serializable newPosition) {
		try {
			this.notifyIObservers(this, new ScannablePositionChangeEvent(calculateNewPosition(Double.valueOf(newPosition.toString()).doubleValue())));
		} catch (NumberFormatException | DeviceException e) {
			logger.error("Exception throw in notifyObserversOfNewPosition(Serializable)", e);
		}
	}

	private double calculateNewPosition(double newPosition) throws DeviceException {
		if (Strings.isNullOrEmpty(getGetPositionExpression())) {
			return newPosition;
		} else {
			double value;
			context.setVariable("output", newPosition);
			if (Strings.isNullOrEmpty(getFunctionNameToBeCalledInGetPosition())) {
				// support simple SpEL expression
				Expression exp = parser.parseExpression(getGetPositionExpression());
				value = exp.getValue(context, Double.class);

			} else {
				// support complex algorithm implemented as method in SpELUtils class
				Class<?>[] parameterTypes = getParameterTypes(functionParameterTypesToBeCalledInGetPosition);
				try {
					context.registerFunction(getFunctionNameToBeCalledInGetPosition(),
							SpELUtils.class.getDeclaredMethod(getFunctionNameToBeCalledInGetPosition(), parameterTypes));
				} catch (NoSuchMethodException | SecurityException e) {
					logger.error("Cannot find the given method {}", getFunctionNameToBeCalledInGetPosition(), e);
				}
				value = parser.parseExpression(getGetPositionExpression()).getValue(context, Double.class);
			}
			return value;
		}
	}

	private Class<?> getClassForName(String clazz) throws ClassNotFoundException {
		return Class.forName(clazz);
	}

	private void logError(Exception e) {
		logger.error(e.getMessage(), e);
	}

	private Class<?>[] getParameterTypes(List<String> functionParameterTypes) throws DeviceException {
		Class<?>[] parameterTypes;
		Supplier<Stream<Either<Exception, Class<?>>>> streamSupplier = () -> Optional.ofNullable(functionParameterTypes).map(Collection::stream).orElseGet(Stream::empty)
				.map(Either.lift(this::getClassForName));
		if (streamSupplier.get().anyMatch(e -> e.isLeft())) {
			// handle any exception thrown inside stream
			String message = streamSupplier.get().filter(e -> e.isLeft()).map(e -> e.getLeft().get()).peek(this::logError).map(e -> e.getMessage())
					.collect(Collectors.joining(","));
			throw new DeviceException(message);
		} else {
			// No Exception in the stream
			parameterTypes = streamSupplier.get().map(e -> e.getRight()).filter(e -> e.isPresent()).map(e -> e.get()).toArray(Class[]::new);
		}
		return parameterTypes;
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

	public List<String> getFunctionParameterTypesTobeCalledInAsynchronousMoveTo() {
		return functionParameterTypesTobeCalledInAsynchronousMoveTo;
	}

	public void setFunctionParameterTypesTobeCalledInAsynchronousMoveTo(List<String> functionParameterTypesTobeCalledInAsynchronousMoveTo) {
		this.functionParameterTypesTobeCalledInAsynchronousMoveTo = functionParameterTypesTobeCalledInAsynchronousMoveTo;
	}

	public List<String> getFunctionParameterTypesToBeCalledInGetPosition() {
		return functionParameterTypesToBeCalledInGetPosition;
	}

	public void setFunctionParameterTypesToBeCalledInGetPosition(List<String> functionParameterTypesToBeCalledInGetPosition) {
		this.functionParameterTypesToBeCalledInGetPosition = functionParameterTypesToBeCalledInGetPosition;
	}

}
