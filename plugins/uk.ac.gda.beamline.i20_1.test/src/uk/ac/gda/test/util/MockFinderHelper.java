package uk.ac.gda.test.util;
import java.util.Map;

import org.junit.Ignore;
import org.junit.runner.RunWith;
import org.mockito.Matchers;
import org.mockito.Mockito;
import org.powermock.api.mockito.PowerMockito;
import org.powermock.core.classloader.annotations.PrepareForTest;
import org.powermock.modules.junit4.PowerMockRunner;

import gda.factory.Findable;
import gda.factory.Finder;

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

/**
 * @deprecated See {@link Finder} for a better way of unit testing classes which use the Finder
 */
@RunWith(PowerMockRunner.class)
@PrepareForTest(Finder.class)
@Deprecated
@Ignore
public class MockFinderHelper {

	public void setupMockForFinder(Map<String, Findable> mockedFindables) {
		Finder mockedFinder = Mockito.mock(Finder.class);
		for (Map.Entry<String, Findable> entry : mockedFindables.entrySet()) {
			Mockito.when(mockedFinder.find(entry.getKey())).thenReturn(entry.getValue());
		}
		PowerMockito.mockStatic(Finder.class);
		Mockito.when(Finder.getInstance()).thenReturn(mockedFinder);
	}

	public void setupMockForFinder(Findable mockedFindable) {
		Finder mockedFinder = Mockito.mock(Finder.class);
		Mockito.when(mockedFinder.find(Matchers.anyString())).thenReturn(mockedFindable);
		PowerMockito.mockStatic(Finder.class);
		Mockito.when(Finder.getInstance()).thenReturn(mockedFinder);
	}
}
