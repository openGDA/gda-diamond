/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

import java.util.HashMap;
import java.util.Map;

import gda.configuration.properties.LocalProperties;
import gda.data.metadata.NXMetaDataProvider;
import gda.data.scan.datawriter.NexusDataWriter;
import gda.device.DeviceException;
import gda.factory.Finder;

/**
 * Scannable that adds data to Nexus file using metashop; data is removed from metashop after the
 * scan finishes so it is not added to subsequent scans unless this scannable is explicitly included in the scan.
 */
public class MetashopDataScannable extends ScannableBase {

	private Map<String, String> metaDataToAdd = new HashMap<>();

	public MetashopDataScannable() {
		setName("scannableToAddRemoveMetashopData");
		setOutputFormat(new String[]{});
		setInputNames(new String[]{});
	}

	/**
	 * Add some data to be added to meta data at beginning of scan
	 * @param key
	 * @param value
	 */
	public void addData(String key, String value) {
		metaDataToAdd.put(key, value);
	}

	public void clearData() {
		metaDataToAdd.clear();
	}

	@Override
	public void atScanStart() {
		addDataToMetashop();
	}

	@Override
	public void atScanEnd() {
		removeDataFromMetashop();
	}

	@Override
	public void atCommandFailure() {
		atScanEnd();
	}

	@Override
	public void stop() throws DeviceException {
		atScanEnd();
	}

	private void addDataToMetashop() {
		NXMetaDataProvider metashop = getMetashop();
		if (metashop != null) {
			metaDataToAdd.forEach( (key, value) -> metashop.put(key, value) );
		}
	}

	private void removeDataFromMetashop() {
		NXMetaDataProvider metashop = getMetashop();
		if (metashop != null) {
			metaDataToAdd.forEach( (key, value) -> metashop.remove(key) );
		}
	}

	public NXMetaDataProvider getMetashop() {
		String name = LocalProperties.get(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME);
		return Finder.find(name);
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

}
