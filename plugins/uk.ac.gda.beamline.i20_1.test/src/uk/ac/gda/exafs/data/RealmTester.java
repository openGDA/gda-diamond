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
import org.eclipse.core.runtime.AssertionFailedException;
import org.junit.Assert;
public class RealmTester {


	  /**
	   * Sets the default realm without using Realm.runWithDefault() for testing
	   * purposes.
	   *
	   * @param realm
	   */
	  public static void setDefault(Realm realm) {
	    CurrentRealm.setDefault(realm);
	  }

	  /**
	   * Runs the provided <code>runnable</code> when the realm is both current and
	   * not current. It checks for AssertionFailedExceptions and if an exception
	   * occurs or doesn't occur as expected the test fails. The realm of an
	   * observable created before the method was invoked must be of type
	   * {@link CurrentRealm}. The default realm during the runnable invocation is
	   * set to an instance of {@link CurrentRealm} when the runnable is invoked.
	   *
	   * @param runnable
	   */
	  public static void exerciseCurrent(Runnable runnable) {
	    CurrentRealm previousRealm = (CurrentRealm) Realm.getDefault();
	    CurrentRealm realm = new CurrentRealm();
	    setDefault(realm);

	    try {
	      realm.setCurrent(true);
	      if (previousRealm != null) {
	        previousRealm.setCurrent(true);
	      }

	      try {
	        runnable.run();
	      } catch (AssertionFailedException e) {
	        Assert
	            .fail("Correct realm, exception should not have been thrown");
	      }

	      realm.setCurrent(false);
	      if (previousRealm != null) {
	        previousRealm.setCurrent(false);
	      }

	      try {
	        runnable.run();
	        Assert
	            .fail("Incorrect realm, exception should have been thrown");
	      } catch (AssertionFailedException e) {
	      }
	    } finally {
	      setDefault(previousRealm);
	    }
	  }

	  /**
	   * Runs the provided <code>runnable</code> when the realm is both current and
	   * not current. It checks for AssertionFailedExceptions and if an exception
	   * occurs or doesn't occur as expected the test fails.
	   *
	   * @param runnable
	   * @param realm
	   */
	  public static void exerciseCurrent(Runnable runnable, CurrentRealm realm) {
	    realm.setCurrent(true);

	    try {
	      runnable.run();
	    } catch (AssertionFailedException e) {
	      Assert.fail("Correct realm, exception should not have been thrown");
	    }

	    realm.setCurrent(false);

	    try {
	      runnable.run();
	      Assert.fail("Incorrect realm, exception should have been thrown");
	    } catch (AssertionFailedException e) {
	    }
	  }
	}