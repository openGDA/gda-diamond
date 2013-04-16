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

package gda.device.detector.edxd;

import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.resource.Resource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.edxd.calibration.edxdcalibration.DocumentRoot;
import uk.ac.gda.edxd.calibration.edxdcalibration.EdxdCalibration;
import uk.ac.gda.edxd.calibration.edxdcalibration.util.EdxdCalibrationResourceHandler;
import uk.ac.gda.edxd.common.IEdxdAlignment;

public class EDXDAlignment implements IEdxdAlignment {
	private static final Logger logger = LoggerFactory.getLogger(EDXDAlignment.class);

	private EDXDController edxdController;

	private EdxdCalibrationResourceHandler edxdCalibrationResourceHandler;

	public void setEdxdCalibrationResourceHandler(EdxdCalibrationResourceHandler edxdCalibrationResourceHandler) {
		this.edxdCalibrationResourceHandler = edxdCalibrationResourceHandler;
	}

	public void setEdxdController(EDXDController edxdController) {
		this.edxdController = edxdController;
	}

	@Override
	public String getLastSavedEnergyCalibrationFile() {
		return getEdxdCalibrationConfiguration().getEnergyCalibration().getFileName();
	}

	@Override
	public String getLastSaveEnergyCalibrationDateTime() {
		return getEdxdCalibrationConfiguration().getEnergyCalibration().getLastCalibrated();
	}

	@Override
	public String getLastSavedQCalibrationFile() {
		return getEdxdCalibrationConfiguration().getQCalibration().getFileName();
	}

	@Override
	public String getLastSaveQCalibrationDateTime() {
		return getEdxdCalibrationConfiguration().getQCalibration().getLastCalibrated();
	}

	@Override
	public String getLastSavedHutch() {
		return getEdxdCalibrationConfiguration().getHutch().getName();
	}

	@Override
	public String getLastSavedCollimator() {
		return getEdxdCalibrationConfiguration().getCollimator().getName();
	}

	@Override
	public void runPreampGain() {

	}

	@Override
	public String runEnergyCalibration() {
		return null;
	}

	@Override
	public void runDetectorXYAlignment() {

	}

	@Override
	public void runCollimatorXYZAlignment() {

	}

	@Override
	public void runCollimatorAngularAlignment() {

	}

	@Override
	public String runQAxisCalibration() {
		return null;
	}

	@Override
	public void loadEnergyCalibrationFile(String fileName) {

	}

	@Override
	public void loadQCalibrationFile(String fileName) {

	}

	private EdxdCalibration getEdxdCalibrationConfiguration() {
		EdxdCalibration calibration = null;
		if (edxdCalibrationResourceHandler != null) {
			Resource resource = edxdCalibrationResourceHandler.getResource(true);

			EObject eObject = resource.getContents().get(0);
			if (eObject instanceof DocumentRoot) {
				DocumentRoot dr = (DocumentRoot) eObject;
				calibration = dr.getEdxdCalibration().get(0);
			}
		}
		return calibration;
	}

}
