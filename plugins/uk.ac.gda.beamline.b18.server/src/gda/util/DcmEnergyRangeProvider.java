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

package gda.util;

import java.util.EnumMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.factory.FindableBase;
import gda.util.CrystalParameters.CrystalSpacing;
import uk.ac.gda.api.remoting.ServiceInterface;

@ServiceInterface(EnergyRangeProvider.class)
public class DcmEnergyRangeProvider extends FindableBase implements EnergyRangeProvider  {

	private static final Logger logger = LoggerFactory.getLogger(DcmEnergyRangeProvider.class);

	private Scannable dcmCrystalScannable;
	private Map<CrystalSpacing, double[]> energyRangeForCrystal;
	private CrystalSpacing defaultCrystalType = CrystalSpacing.Si_111;

	public DcmEnergyRangeProvider() {
		energyRangeForCrystal = new EnumMap<>(CrystalSpacing.class);
		energyRangeForCrystal.put(CrystalSpacing.Si_111, new double[]{2050.0, 26000.0});
		energyRangeForCrystal.put(CrystalSpacing.Si_311, new double[]{4000.0, 40000.0});
	}

	/**
	 * Return {@link CrystalSpacing} enum object for the current position of the dcmCrystalScannable
	 * i.e. Si(311) or Si(111)
	 * The defaultCrystalType is returned if a DeviceException occurs or position is not valid)
	 * @return CrystalSpacing
	 */
	private CrystalSpacing getCrystalSpacingForPosition() {
		String position = "";
		try {
			position = dcmCrystalScannable.getPosition().toString();
			if ("Si(311)".equals(position)) {
				return CrystalSpacing.Si_311;
			} else if ("Si(111)".equals(position)) {
				return CrystalSpacing.Si_111;
			}
		} catch(DeviceException de) {
			logger.warn("Problem getting crystal type from {}", getName(), de);
		}
		logger.info("Position '{}' is not a recognised crystal type - assuming type is {}", position, defaultCrystalType);
		return defaultCrystalType;
	}

	@Override
	public CrystalSpacing getCrystalSpacing() {
		return getCrystalSpacingForPosition();
	}

	@Override
	public double getLowerEnergy() {
		return energyRangeForCrystal.get(getCrystalSpacingForPosition())[0];
	}

	@Override
	public double getUpperEnergy() {
		return energyRangeForCrystal.get(getCrystalSpacingForPosition())[1];
	}

	public Scannable getDcmCrystalScannable() {
		return dcmCrystalScannable;
	}

	public void setDcmCrystalScannable(Scannable dcmCrystalScannable) {
		this.dcmCrystalScannable = dcmCrystalScannable;
	}

}