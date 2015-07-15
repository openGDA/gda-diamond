/*-
 * Copyright © 2014 Diamond Light Source Ltd.
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

package gda.scan;

import java.util.List;

import org.eclipse.dawnsci.analysis.dataset.impl.DoubleDataset;

import gda.device.detector.EdeDetector;
import gda.observable.IObserver;
import gda.scan.ede.EdeScanType;
import uk.ac.gda.exafs.ui.data.EdeScanParameters;

public interface EnergyDispersiveExafsScan extends Scan {

	public void setProgressUpdater(IObserver progressUpdater);

	public List<ScanDataPoint> getData();

	public EdeScanParameters getScanParameters();

	public void setScanParameters(EdeScanParameters scanParameters);

	public EdeScanType getScanType();

	public void setScanType(EdeScanType scanType);

	public DoubleDataset extractEnergyDetectorDataSet();

	public DoubleDataset extractDetectorDataSet(int i);

	public String getHeaderDescription();

	public EdeDetector getDetector();
}