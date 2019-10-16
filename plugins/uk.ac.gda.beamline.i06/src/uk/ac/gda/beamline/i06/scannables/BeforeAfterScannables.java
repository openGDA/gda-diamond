/*-
 * Copyright © 2016 Diamond Light Source Ltd.
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

import static com.google.common.base.Preconditions.checkArgument;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.ScannableMotionUnits;
import gda.device.scannable.ScannableMotionUnitsBase;
import io.vavr.collection.Stream;
import io.vavr.control.Either;

public class BeforeAfterScannables extends ScannableMotionUnitsBase {

	private static final Logger logger = LoggerFactory.getLogger(BeforeAfterScannables.class);

	private Scannable delegate;
	private Map<Scannable, Object> beforeScannables = new LinkedHashMap<>();
	private Map<Scannable, Object> afterScannables = new LinkedHashMap<>();
	private boolean busy=false;

	public BeforeAfterScannables() {

	}

	public BeforeAfterScannables(ScannableMotionUnits delegate,
			Map<Scannable, Object> beforeScannables, Map<Scannable, Object> afterScannables) {
		this.setDelegate(delegate);
		this.setBeforeScannables(beforeScannables);
		this.setAfterScannables(afterScannables);
	}

	// a utility method that records exceptions instead of throwing exception so it can be used in Lambda expression
	private Either<DeviceException, Object> moveMotor(Scannable scannable, Object value) {
		try {
			scannable.moveTo(value);
			return Either.right(value);
		} catch (DeviceException e) {
			logger.error("move scannable {} to {} failed with exception {}", scannable.getName(), value, e);
			return Either.left(e);
		}
	}

	@Override
	public void rawAsynchronousMoveTo(Object position) throws DeviceException {
		busy=true;
		try {
			if (!beforeScannables.isEmpty()) {
				//ensure Stream run to complete even some element throws DeviceException
				List<Either<DeviceException, Object>> collect = Stream.ofAll(io.vavr.collection.LinkedHashMap.ofAll(beforeScannables))
				.peek(e->logger.trace("moving {} to {} before", e._1.getName(), e._2))
				.map(e -> moveMotor(e._1,e._2)).collect(Collectors.toList());
				throwExceptionIfAny(collect);
			}
			// in case beforeAfter.waitWhileBusy returns before finished moving
			Thread.sleep(delayBeforeMovingDelegate);

			logger.trace("moving {} to {}", getDelegate().getName(), position);
			getDelegate().moveTo(position);
			Thread.sleep(delayBeforeMovingDelegate);
			if (!afterScannables.isEmpty()) {
				List<Either<DeviceException, Object>> collect = Stream.ofAll(io.vavr.collection.LinkedHashMap.ofAll(afterScannables))
						.peek(e->logger.trace("moving {} to {} before", e._1.getName(), e._2))
						.map(e->moveMotor(e._1, e._2)).collect(Collectors.toList());
				throwExceptionIfAny(collect);
			}
		} catch (InterruptedException e) {
			// Restore the interrupted status
			Thread.currentThread().interrupt();

			// For compatibility with ScannableBase.moveTo:
			// convert to a device exception
			throw new DeviceException(e.getMessage(), e.getCause());
		} catch (DeviceException e1) {
			throw e1;
		}
		finally {
			busy=false;
		}
	}

	private void throwExceptionIfAny(List<Either<DeviceException, Object>> collect) throws DeviceException {
		String errorMessages = Stream.ofAll(collect).filter(e->e.isLeft()).collect(StringBuilder::new,
				(response,element) -> response.append(element.getLeft().getMessage()),
				(response1, response2) -> response1.append("\n").append(response2.toString())).toString();
		//Only throw one combined DeviceException if any present in stream computation
		if (errorMessages != null && !errorMessages.isEmpty()) {
			throw new DeviceException(errorMessages);
		}
	}

	@Override
	public Object rawGetPosition() throws DeviceException {
		return getDelegate().getPosition();
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return busy;
	}

	///////////////////////////////////////////////////////////////////////////

	private long delayBeforeMovingDelegate = 0;

	public long getDelayBeforeMovingDelegate() {
		return delayBeforeMovingDelegate;
	}

	/**
	 * Minimum time to wait between initial move of 'beforeAfter' and before moving 'delegate'.
	 */
	public void setDelayBeforeMovingDelegate(long milliseconds) {
		checkArgument(milliseconds >= 0, "milliseconds must be a positive integer");
		delayBeforeMovingDelegate = milliseconds;
	}

	public Scannable getDelegate() {
		return delegate;
	}

	public void setDelegate(Scannable delegate) {
		this.delegate = delegate;
	}

	public Map<Scannable, Object> getBeforeScannables() {
		return beforeScannables;
	}

	public void setBeforeScannables(Map<Scannable, Object> beforeScannables) {
		this.beforeScannables = beforeScannables;
	}

	public Map<Scannable, Object> getAfterScannables() {
		return afterScannables;
	}

	public void setAfterScannables(Map<Scannable, Object> afterScannables) {
		this.afterScannables = afterScannables;
	}

}
