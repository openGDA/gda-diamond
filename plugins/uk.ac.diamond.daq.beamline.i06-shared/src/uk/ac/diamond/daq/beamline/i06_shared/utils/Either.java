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

package uk.ac.diamond.daq.beamline.i06_shared.utils;

import java.util.Optional;
import java.util.function.Function;

/**
 * a generic wrapper with two possibilities. It can either be a Left or a Right but never both. Both left and right can be of any types.
 *
 * @param <L>
 * @param <R>
 */
public class Either<L, R> {
	private final L left;
	private final R right;

	private Either(L left, R right) {
		this.left = left;
		this.right = right;
	}

	public static <L, R> Either<L, R> Left(L value) {
		return new Either<L, R>(value, null);
	}

	public static <L, R> Either<L, R> Right(R value) {
		return new Either<L, R>(null, value);
	}

	public Optional<L> getLeft() {
		return Optional.ofNullable(left);
	}

	public Optional<R> getRight() {
		return Optional.ofNullable(right);
	}

	public boolean isLeft() {
		return left != null;
	}

	public boolean isRight() {
		return right != null;
	}

	public <T> Optional<T> mapLeft(Function<? super L, T> mapper) {
		if (isLeft()) {
			return Optional.of(mapper.apply(left));
		}
		return Optional.empty();
	}

	public <T> Optional<T> mapRight(Function<? super R, T> mapper) {
		if (isRight()) {
			return Optional.of(mapper.apply(right));
		}
		return Optional.empty();
	}

	public static <T, R> Function<T, Either> lift(CheckedFunction<T, R> function) {
		return t -> {
			try {
				return Either.Right(function.apply(t));
			} catch (Exception ex) {
				return Either.Left(ex);
			}
		};
	}

	@Override
	public String toString() {
		if (isLeft()) {
			return "Left(" + left + ")";
		}
		return "Right(" + right + ")";
	}
}
