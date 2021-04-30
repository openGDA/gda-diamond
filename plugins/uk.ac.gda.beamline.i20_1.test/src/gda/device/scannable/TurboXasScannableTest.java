/*-
 * Copyright © 2021 Diamond Light Source Ltd.
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

package gda.device.scannable;

import static org.junit.Assert.assertEquals;

import javax.measure.Quantity;
import javax.measure.quantity.Energy;
import javax.measure.quantity.Length;

import org.junit.Before;
import org.junit.Test;

import gda.configuration.properties.LocalProperties;
import gda.device.DeviceException;
import gda.device.motor.DummyMotor;
import gda.factory.FactoryException;
import gda.scan.TurboXasMotorParameters;
import gda.scan.TurboXasParameters;
import gda.util.QuantityFactory;
import gda.util.converters.IQuantityConverter;

public class TurboXasScannableTest {

	private TurboXasScannable turboXasScannable;
	private ConvertorScannable<Energy, Length> converterScanable;
	private double calibrationPolyMinEnergy = 1000;
	private String calibrationPoly = calibrationPolyMinEnergy+" + 1000*x + 20x^2";

	@Before
	public void setup() throws FactoryException, DeviceException {
		LocalProperties.set(LocalProperties.GDA_SCANNABLEBASE_POLLTIME, "0");
		DummyMotor dummyMotor = new DummyMotor();
		dummyMotor.setName("dummyMotor");
		dummyMotor.setMinPosition(-10000);
		dummyMotor.setMaxPosition(10000);
		dummyMotor.setPosition(0);
		dummyMotor.configure();

		ScannableMotor scnMotor = new ScannableMotor();
		scnMotor.setName("scnMotor");
		scnMotor.setMotor(dummyMotor);
		scnMotor.setSpeed(100000);
		scnMotor.configure();
		scnMotor.setUserUnits("mm");

		turboXasScannable = new TurboXasScannable();
		turboXasScannable.setName("turboXasScannable");
		TurboXasMotorParameters parameters = getMotorParams();
		turboXasScannable.setMotorParameters(parameters);

		EnergyPositionConverter<Energy, Length> converter = new EnergyPositionConverter<>();
		converter.setTurboXasScannable(turboXasScannable);

		converterScanable = new ConvertorScannable<>();
		converterScanable.setName("converterScannable");
		converterScanable.setConvertor(converter);
		converterScanable.setScannable(scnMotor);
		converterScanable.configure();
	}

	public TurboXasMotorParameters getMotorParams() {
		TurboXasParameters parameters = new TurboXasParameters();
		parameters.setEnergyCalibrationPolynomial( calibrationPoly );
		parameters.setEnergyCalibrationMinPosition(-5);
		parameters.setEnergyCalibrationMaxPosition(5);
		parameters.setUsePositionsForScan(false);
		return new TurboXasMotorParameters(parameters);
	}

	@Test
	public void testConverter() throws Exception {

		TurboXasMotorParameters parameters = turboXasScannable.getMotorParameters();
		IQuantityConverter<Energy, Length> convertor = converterScanable.getConvertor();

		for(double energy = calibrationPolyMinEnergy; energy < 2000; energy += 10) {
			Quantity<Length> position = convertor.toTarget(QuantityFactory.createFromObject(energy, "eV"));
			double expectedPositon = parameters.getPositionForEnergy(energy);
			assertEquals("Position for "+energy+" eV is not correct", expectedPositon, position.getValue().doubleValue(), 1e-6);

			Quantity<Energy> convertedEnergy = convertor.toSource(QuantityFactory.createFromObject(expectedPositon, "mm"));
			assertEquals("Energy for "+expectedPositon+" mm is not correct", energy, convertedEnergy.getValue().doubleValue(), 1e-6);

		}
	}

	@Test
	public void testScannable() throws DeviceException {
		for(double energy = calibrationPolyMinEnergy; energy < 2000; energy += 10) {
			double expectedPosition = turboXasScannable.getMotorParameters().getPositionForEnergy(energy);
			converterScanable.moveTo(energy);
			Object motorPos = converterScanable.getScannable().getPosition();
			assertEquals(expectedPosition, (double)motorPos, 1e-5);
		}
	}
}
