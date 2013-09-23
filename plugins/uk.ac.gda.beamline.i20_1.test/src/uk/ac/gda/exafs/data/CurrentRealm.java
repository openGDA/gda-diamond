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

package uk.ac.gda.exafs.data;

import org.eclipse.core.databinding.observable.Realm;

public class CurrentRealm extends Realm {
	private boolean current;

	public CurrentRealm() {
		this(false);
	}

	public CurrentRealm(boolean current) {
		this.current = current;
	}

	@Override
	public boolean isCurrent() {
		return current;
	}

	public void setCurrent(boolean current) {
		this.current = current;
	}

	@Override
	protected void syncExec(Runnable runnable) {
		super.syncExec(runnable);
	}

	@Override
	public void asyncExec(Runnable runnable) {
		throw new UnsupportedOperationException(
				"CurrentRealm does not support asyncExec(Runnable).");
	}

	protected static Realm setDefault(Realm realm) {
		return Realm.setDefault(realm);
	}
}