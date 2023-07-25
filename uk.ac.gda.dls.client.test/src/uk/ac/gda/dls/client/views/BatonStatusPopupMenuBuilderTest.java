/*-
 * Copyright © 2023 Diamond Light Source Ltd.
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

package uk.ac.gda.dls.client.views;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.mockito.Mockito.when;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.junit.MockitoJUnitRunner;

import gda.jython.IBatonStateProvider;
import gda.jython.batoncontrol.ClientDetails;

@RunWith(MockitoJUnitRunner.class)
public final class BatonStatusPopupMenuBuilderTest {

	private static final int NONSENSICAL_INDEX = -7893;

	@Mock
	IBatonStateProvider fakedBatonStateProvider;

	@Mock
	ClientDetails fakedUdcClientDetails;

	@Mock
	ClientDetails fakedNonUdcClientDetails1;

	@Mock
	ClientDetails fakedNonUdcClientDetails2;

	private int index = NONSENSICAL_INDEX;
	private Boolean udcClientPresent;
	private ClientDetails[] clientDetails;

	@Before
	public void setUp() {
		when(fakedUdcClientDetails.isAutomatedUser()).thenReturn(true);
		when(fakedUdcClientDetails.getIndex()).thenReturn(37);

		when(fakedNonUdcClientDetails1.isAutomatedUser()).thenReturn(false);
		when(fakedNonUdcClientDetails2.isAutomatedUser()).thenReturn(false);
	}

	@Test
	public void testUdcClientIsFound() {
		givenThatBatonProviderSeesUdcAndOtherClients();
		whenUdcClientIsSought();
		assertTrue(udcClientPresent);
	}

	@Test
	public void testUdcClientIndexIsExtractedWithoutError() {
		givenThatBatonProviderSeesUdcAndOtherClients();
		whenUdcClientIndexIsRequested();
		var expectedUdcClientIndex = 37;
		assertEquals(expectedUdcClientIndex, index);
	}

	@Test
	public void testUdcClientIsReportedAsAbsentWhenBatonProviderAbsent() {
		whenUdcClientIsSoughtFromAbsentProvider();
		assertFalse(udcClientPresent);
	}

	@Test
	public void testUdcClientIndexFromAbsentBatonProviderGivesExpectedFallbackIndex() {
		whenUdcClientIndexIsRequestedFromAbsentProvider();
		var expectedFallbackClientIndex = 0;
		assertEquals(expectedFallbackClientIndex, index);
	}

	@Test
	public void testUdcClientIsReportedAsAbsentWhenDetailsArrayIsAbsent() {
		givenClientDetailsArrayIsReplacedByNull();
		whenUdcClientIsSought();
		assertFalse(udcClientPresent);
	}

	@Test
	public void testFallbackIndexIsReturnedWhenDetailsArrayIsAbsent() {
		givenClientDetailsArrayIsReplacedByNull();
		whenUdcClientIndexIsRequested();
		var expectedFallbackClientIndex = 0;
		assertEquals(expectedFallbackClientIndex, index);
	}

	@Test
	public void testUdcClientIsReportedAsAbsentWhenBatonProviderHasNoOtherClientDetails() {
		givenNoOtherClients();
		whenUdcClientIsSought();
		assertFalse(udcClientPresent);
	}

	@Test
	public void testWhenBatonProviderHasNoOtherClientDetailsGivesExpectedFallbackIndex() {
		givenNoOtherClients();
		whenUdcClientIndexIsRequested();
		var expectedUdcClientIndex = 0;
		assertEquals(expectedUdcClientIndex, index);
	}

	@Test
	public void testUdcClientIsReportedAsAbsentWhenBatonProviderGivesNullAmidNonUdcClientDetails() {
		givenClientDetailsArrayContainsNullAndNoUdcClient();
		whenUdcClientIsSought();
		assertFalse(udcClientPresent);
	}

	@Test
	public void testFallbackIndexIsReturnedWhenBatonProviderGivesNullAmidNonUdcClientDetails() {
		givenClientDetailsArrayContainsNullAndNoUdcClient();
		whenUdcClientIndexIsRequested();
		var expectedUdcClientIndex = 0;
		assertEquals(expectedUdcClientIndex, index);
	}

	@Test
	public void testUdcClientIsFoundWhenClientDetailArrayHasNullBeforeUdc() {
		givenClientDetailsArrayContainsNullBeforeUdcClient();
		whenUdcClientIsSought();
		assertTrue(udcClientPresent);
	}

	@Test
	public void testUdcClientIndexIsExtractedWhenClientDetailArrayHasNullBeforeUdc() {
		givenClientDetailsArrayContainsNullBeforeUdcClient();
		whenUdcClientIndexIsRequested();
		var expectedUdcClientIndex = 37;
		assertEquals(expectedUdcClientIndex, index);
	}

	@Test
	public void testUdcClientIndexIsExtractedWhenClientDetailArrayHasNullAfterUdc() {
		givenClientDetailsArrayContainsNullAfterUdcClient();
		whenUdcClientIndexIsRequested();
		var expectedUdcClientIndex = 37;
		assertEquals(expectedUdcClientIndex, index);
	}

	@Test
	public void testWhenBatonProviderHasNoUdcClientDetailsGivesExpectedFallbackIndex() {
		givenNoUdcClient();
		whenUdcClientIndexIsRequested();
		var expectedUdcClientIndex = 0;
		assertEquals(expectedUdcClientIndex, index);
	}

	private void givenThatBatonProviderSeesUdcAndOtherClients() {
		clientDetails =
			new ClientDetails[] { fakedNonUdcClientDetails1,
									fakedUdcClientDetails,
									fakedNonUdcClientDetails2 };
	}

	private void givenNoOtherClients() {
		clientDetails = new ClientDetails[] { };
	}

	private void givenNoUdcClient() {
		clientDetails = new ClientDetails[] { fakedNonUdcClientDetails2, fakedNonUdcClientDetails1 };
	}

	private void givenClientDetailsArrayIsReplacedByNull() {
		// do nothing, covered in set-up
	}

	private void givenClientDetailsArrayContainsNullAndNoUdcClient() {
		clientDetails = new ClientDetails[] { fakedNonUdcClientDetails2, null, fakedNonUdcClientDetails1 };
	}

	private void givenClientDetailsArrayContainsNullBeforeUdcClient() {
		clientDetails = new ClientDetails[] { fakedNonUdcClientDetails1, null, fakedUdcClientDetails };
	}


	private void givenClientDetailsArrayContainsNullAfterUdcClient() {
		clientDetails = new ClientDetails[] { fakedUdcClientDetails, null, fakedNonUdcClientDetails2 };
	}

	private void whenUdcClientIsSought() {
		when(fakedBatonStateProvider.getOtherClientInformation()).thenReturn(clientDetails);
		udcClientPresent = BatonStatusPopupMenuBuilder.udcClientExists(fakedBatonStateProvider);
	}

	private void whenUdcClientIndexIsRequested() {
		when(fakedBatonStateProvider.getOtherClientInformation()).thenReturn(clientDetails);
		index = BatonStatusPopupMenuBuilder.getUdcClientIndex(fakedBatonStateProvider);
	}

	private void whenUdcClientIsSoughtFromAbsentProvider() {
		udcClientPresent = BatonStatusPopupMenuBuilder.udcClientExists(null);
	}

	private void whenUdcClientIndexIsRequestedFromAbsentProvider() {
		index = BatonStatusPopupMenuBuilder.getUdcClientIndex(null);
	}
}
