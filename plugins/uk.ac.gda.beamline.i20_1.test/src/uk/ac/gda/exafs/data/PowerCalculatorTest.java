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

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

import java.io.File;

import org.junit.Assert;
import org.junit.Test;
//import org.powermock.core.classloader.annotations.PrepareForTest;
//import org.powermock.modules.junit4.PowerMockRunner;
//import org.powermock.reflect.Whitebox;

// @RunWith(PowerMockRunner.class)
public class PowerCalculatorTest {

	public static final String FOLDER_PATH = "testfiles/uk/ac/gda/exafs/data/PowerCalculatorTest";

	@Test
	public void stringTest() {
		try {
			assertEquals("1p3T", PowerCalulator.getFieldName(19.0));
			assertEquals("0p33T", PowerCalulator.getFieldName(50.0));
			assertEquals("1p0mrad", PowerCalulator.getSlitHGapName(0.96));
		} catch (Exception e) {
			Assert.fail();
		}
	}

	@Test
	public void fileTest() throws Exception {
		File file = PowerCalulator.getEnergyFieldFile(19.0, 0.96, FOLDER_PATH);
		assertEquals("1p3T-300mA-0p12x1p0mrad.dat", file.getName());
		file = PowerCalulator.getEnergyFieldFile(45.0, 1.09, FOLDER_PATH);
		assertEquals("0p33T-300mA-0p12x1p1mrad.dat", file.getName());
		try {
			file = PowerCalulator.getEnergyFieldFile(251.0, 1.09, FOLDER_PATH);
			assertTrue(false);
		} catch(Exception e) {
			// Pass through
		}
	}

	//	@Test
	//	@PrepareForTest({ScannableSetup.class})
	//	public void powerTest() throws Exception {
	//		setupMock("Empty", "Empty", "Empty", FilterMirrorElementType.Platinum.name(), FilterMirrorElementType.Rhodium.name(), 3.26);
	//		assertEquals(149, (int) PowerCalulator.getPower(FOLDER_PATH, 19.0, 0.96, 300));
	//	}

	@Test
	public void nameSplitTest() {
		String[] result = PowerCalulator.Mirrors.INSTANCE.getNameParts("pC 2.0mm");
		assertEquals(result[0], "pC");
		assertEquals(result[1], "2.0");
		assertEquals(result[2], "mm");
		result = PowerCalulator.Mirrors.INSTANCE.getNameParts("SiC1.5mm");
		assertEquals(result[0], "SiC");
		assertEquals(result[1], "1.5");
		assertEquals(result[2], "mm");
		result = PowerCalulator.Mirrors.INSTANCE.getNameParts("pC 0.6mm (Crkd)");
		assertEquals(result[0], "pC");
		assertEquals(result[1], "0.6");
		assertEquals(result[2], "mm");
		result = PowerCalulator.Mirrors.INSTANCE.getNameParts("Left Empty");
		assertNull(result);
	}

	@Test
	public void findNearestTest() {
		assertEquals(3.0,PowerCalulator.Mirrors.INSTANCE.findNearest(3.124), Double.MIN_VALUE);
		assertEquals(3.25,PowerCalulator.Mirrors.INSTANCE.findNearest(3.13), Double.MIN_VALUE);
	}

	//	public void setupMock(final String atn1, final String atn2, final String atn3, final String me1, final String me2, final double me2Angle) throws Exception {
	//		final String atn1ScannableName = ScannableSetup.ATN1.getScannableName();
	//		ScannableSetup atn1ScannableSetup = Mockito.mock(ScannableSetup.class);
	//		Whitebox.setInternalState(ScannableSetup.class, ScannableSetup.ATN1.name(), atn1ScannableSetup);
	//		Mockito.when(atn1ScannableSetup.getScannable()).thenReturn(new ScannableBase() {
	//			@Override
	//			public Object getPosition() throws DeviceException {
	//				return atn1;
	//			}
	//			@Override
	//			public String getName() {
	//				return atn1ScannableName;
	//			}
	//			@Override
	//			public boolean isBusy() throws DeviceException {
	//				return false;
	//			}
	//		});
	//
	//		final String atn2ScannableName = ScannableSetup.ATN2.getScannableName();
	//		ScannableSetup atn2ScannableSetup = Mockito.mock(ScannableSetup.class);
	//		Whitebox.setInternalState(ScannableSetup.class, ScannableSetup.ATN2.name(), atn2ScannableSetup);
	//		Mockito.when(atn2ScannableSetup.getScannable()).thenReturn(new ScannableBase() {
	//			@Override
	//			public Object getPosition() throws DeviceException {
	//				return atn2;
	//			}
	//			@Override
	//			public String getName() {
	//				return atn2ScannableName;
	//			}
	//			@Override
	//			public boolean isBusy() throws DeviceException {
	//				return false;
	//			}
	//		});
	//
	//		final String atn3ScannableName = ScannableSetup.ATN3.getScannableName();
	//		ScannableSetup atn3ScannableSetup = Mockito.mock(ScannableSetup.class);
	//		Whitebox.setInternalState(ScannableSetup.class, ScannableSetup.ATN3.name(), atn3ScannableSetup);
	//		Mockito.when(atn3ScannableSetup.getScannable()).thenReturn(new ScannableBase() {
	//			@Override
	//			public Object getPosition() throws DeviceException {
	//				return atn3;
	//			}
	//			@Override
	//			public String getName() {
	//				return atn3ScannableName;
	//			}
	//			@Override
	//			public boolean isBusy() throws DeviceException {
	//				return false;
	//			}
	//		});
	//
	//		final String me1ScannableName = ScannableSetup.ME1_STRIPE.getScannableName();
	//		ScannableSetup me1ScannableSetup = Mockito.mock(ScannableSetup.class);
	//		Whitebox.setInternalState(ScannableSetup.class, ScannableSetup.ME1_STRIPE.name(), me1ScannableSetup);
	//		Mockito.when(me1ScannableSetup.getScannable()).thenReturn(new ScannableBase() {
	//			@Override
	//			public Object getPosition() throws DeviceException {
	//				return me1;
	//			}
	//			@Override
	//			public String getName() {
	//				return me1ScannableName;
	//			}
	//			@Override
	//			public boolean isBusy() throws DeviceException {
	//				return false;
	//			}
	//		});
	//		Mockito.when(me1ScannableSetup.getScannableName()).thenReturn(me1ScannableName);
	//
	//		final String me2ScannableName = ScannableSetup.ME2_STRIPE.getScannableName();
	//		ScannableSetup me2ScannableSetup = Mockito.mock(ScannableSetup.class);
	//		Whitebox.setInternalState(ScannableSetup.class, ScannableSetup.ME2_STRIPE.name(), me2ScannableSetup);
	//		Mockito.when(me2ScannableSetup.getScannable()).thenReturn(new ScannableBase() {
	//			@Override
	//			public Object getPosition() throws DeviceException {
	//				return me2;
	//			}
	//			@Override
	//			public String getName() {
	//				return me2ScannableName;
	//			}
	//			@Override
	//			public boolean isBusy() throws DeviceException {
	//				return false;
	//			}
	//		});
	//		Mockito.when(me2ScannableSetup.getScannableName()).thenReturn(me2ScannableName);
	//
	//		final String me1PitchScannableName = ScannableSetup.ME2_PITCH_ANGLE.getScannableName();
	//		ScannableSetup me2PitchScannableSetup = Mockito.mock(ScannableSetup.class);
	//		Whitebox.setInternalState(ScannableSetup.class, ScannableSetup.ME2_PITCH_ANGLE.name(), me2PitchScannableSetup);
	//		Mockito.when(me2PitchScannableSetup.getScannable()).thenReturn(new ScannableBase() {
	//			@Override
	//			public Object getPosition() throws DeviceException {
	//				return me2Angle;
	//			}
	//			@Override
	//			public String getName() {
	//				return me1PitchScannableName;
	//			}
	//			@Override
	//			public boolean isBusy() throws DeviceException {
	//				return false;
	//			}
	//		});
	//	}
}
