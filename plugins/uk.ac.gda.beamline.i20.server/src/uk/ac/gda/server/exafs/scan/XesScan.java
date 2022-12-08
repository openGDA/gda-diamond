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

package uk.ac.gda.server.exafs.scan;

import java.util.List;

import org.apache.commons.lang.ArrayUtils;
import org.apache.commons.lang.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.Detector;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannableBase;
import gda.device.scannable.TwoDScanPlotter;
import gda.exafs.xes.IXesOffsets;
import gda.jython.scriptcontroller.logging.LoggingScriptController;
import uk.ac.gda.beans.exafs.IDetectorConfigurationParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.SignalParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.beans.exafs.i20.I20OutputParameters;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class XesScan extends XasScanBase implements XasScan {

	private static Logger logger = LoggerFactory.getLogger(XesScan.class);

	private Scannable analyserAngle;
	private Scannable xes_energy;
	private Scannable mono_energy;
	private EnergyScan xas;
	private XesScanParameters xesScanParameters;
	private Object[] xes_args;
	private TwoDScanPlotter twodplotter = new TwoDScanPlotter();
	private I20OutputParameters i20OutputParameters;
	private String monoAxisLabel = "bragg1 energy [eV]";
	private String xesAxisLabel = "XESEnergy [eV]";
	private IXesOffsets xesOffsets;

	@Override
	public String getScanType() {
		return "XES";
	}

	@Override
	public void configureCollection(ISampleParameters sampleBean, IScanParameters scanBean, IDetectorParameters detectorBean,
			IOutputParameters outputBean, IDetectorConfigurationParameters detectorConfigurationBean,
			String experimentFullPath, int numRepetitions) throws Exception {

		xesScanParameters = (XesScanParameters) scanBean;
		i20OutputParameters = (I20OutputParameters) outputBean;
		this.numRepetitions = numRepetitions;
		this.experimentFullPath = experimentFullPath;
		this.detectorConfigurationBean = detectorConfigurationBean;
		this.outputBean = outputBean;
		this.detectorBean = detectorBean;
		this.sampleBean = sampleBean;
		this.scanBean = scanBean;

		setXmlFileNames("", "", "", "", "");
		determineExperimentPath(experimentFullPath);
		scan_unique_id = LoggingScriptController.createUniqueID(getScanType());
	}

	@Override
	public void doCollection() throws Exception {
		xesScanParameters = (XesScanParameters) scanBean;
		i20OutputParameters = (I20OutputParameters) outputBean;
		String offsetStoreName = xesScanParameters.getOffsetsStoreName();
		if (StringUtils.isNotEmpty(offsetStoreName)) {
			xesOffsets.saveToTemp(); // save current offsets to temporary files, so they can be reset at the end
			xesOffsets.apply(offsetStoreName);
		}

		if (analyserAngle.isBusy()) {
			analyserAngle.waitWhileBusy();
		}

		int innerScanType = xesScanParameters.getScanType();
		if (innerScanType == XesScanParameters.FIXED_XES_SCAN_XAS ||
			innerScanType == XesScanParameters.FIXED_XES_SCAN_XANES ||
			innerScanType == XesScanParameters.SCAN_XES_REGION_FIXED_MONO) {
			doXASScan();
			return;
		}

		try {
			super.doCollection();
		} finally {
			// make sure the plotter is switched off
			twodplotter.atScanEnd();
		}
	}

	@Override
	protected void finishRepetitions() throws Exception {
		super.finishRepetitions();
		// Apply the original XES offsets
		if (StringUtils.isNotEmpty(xesScanParameters.getOffsetsStoreName())) {
			xesOffsets.applyFromTemp();
		}
	}

	// args do run a single concurrentscan
	@Override
	public Object[] createScanArguments(String sampleName, List<String> descriptions) throws Exception {

		int innerScanType = xesScanParameters.getScanType();

		if (innerScanType == XesScanParameters.SCAN_XES_FIXED_MONO) {
			xes_args = new Object[] { xes_energy, xesScanParameters.getXesInitialEnergy(),
					xesScanParameters.getXesFinalEnergy(), xesScanParameters.getXesStepSize(), mono_energy,
					xesScanParameters.getMonoEnergy(), analyserAngle };
		} else if (innerScanType == XesScanParameters.SCAN_XES_SCAN_MONO) {

			Object[] ef_args = new Object[] { xes_energy, xesScanParameters.getXesInitialEnergy(),
					xesScanParameters.getXesFinalEnergy(), xesScanParameters.getXesStepSize() };
			Object[] e0_args = new Object[] { mono_energy, xesScanParameters.getMonoInitialEnergy(),
					xesScanParameters.getMonoFinalEnergy(), xesScanParameters.getMonoStepSize() };
			if (xesScanParameters.getLoopChoice().equals(XesScanParameters.LOOPOPTIONS[0])) {
				xes_args = ArrayUtils.addAll(ef_args, e0_args);
				twodplotter.setXArgs(xesScanParameters.getMonoInitialEnergy(), xesScanParameters.getMonoFinalEnergy(),
						xesScanParameters.getMonoStepSize());
				twodplotter.setYArgs(xesScanParameters.getXesInitialEnergy(), xesScanParameters.getXesFinalEnergy(),
						xesScanParameters.getXesStepSize());
				twodplotter.setXAxisName(monoAxisLabel);
				twodplotter.setYAxisName(xesAxisLabel);
			} else { // innerScanType == XesScanParameters.SCAN_XES_FIXED_MONO
				xes_args = ArrayUtils.addAll(e0_args, ef_args);
				twodplotter.setXArgs(xesScanParameters.getXesInitialEnergy(), xesScanParameters.getXesFinalEnergy(),
						xesScanParameters.getXesStepSize());
				twodplotter.setYArgs(xesScanParameters.getMonoInitialEnergy(), xesScanParameters.getMonoFinalEnergy(),
						xesScanParameters.getMonoStepSize());
				twodplotter.setYAxisName(monoAxisLabel);
				twodplotter.setXAxisName(xesAxisLabel);
			}
			// Add XESBragg angle
			xes_args = ArrayUtils.add(xes_args, (Object)analyserAngle);
			twodplotter.setZ_colName("FFI1");
			xes_args = ArrayUtils.add(xes_args, twodplotter);
		}
		Detector[] detList = getDetectors();
		for (Detector det : detList) {
			xes_args = ArrayUtils.add(xes_args, det);
		}
		return xes_args;
	}


	/**
	 * Set name of scannable in scan bean to match the one to be moved (not essential, but useful to have it recorded in XML)
	 * @param scanParams
	 * @param nameOfScannableToMove
	 */
	private void setXasXanesScannable(IScanParameters scanParams, String nameOfScannableToMove) {
		String nameFromParams = scanParams.getScannableName();
		if (StringUtils.isEmpty(nameFromParams) || !nameFromParams.equals(nameOfScannableToMove)) {
			logger.warn("Updating name of scannable in Xas/Xanes parameter from {} to {}", nameFromParams, nameOfScannableToMove);

			if (scanParams instanceof XasScanParameters) {
				((XasScanParameters)scanParams).setScannableName(nameOfScannableToMove);
			} else if (scanParams instanceof XanesScanParameters) {
				((XanesScanParameters)scanParams).setScannableName(nameOfScannableToMove);
			}
		}
	}

	/**
	 * Scannable that delegates moves to one scannable and returns position of another.
	 * This is used to move spectrometer in SCAN_XES_XANES_FIXED_MONO scans, so that readout
	 * values are returned in the same order as during FIXED_XES_SCAN_XAS/XANES scans.
	 */
	private static class XesXanesScannable extends ScannableBase {
		private final Scannable scannableToMove;
		private final Scannable scannableToGetPositionOf;

		public XesXanesScannable(Scannable scannableToMove, Scannable scannableToGetPositionOf) {
			this.scannableToMove = scannableToMove;
			this.scannableToGetPositionOf = scannableToGetPositionOf;
			setOutputFormat(scannableToGetPositionOf.getOutputFormat());
			setExtraNames(scannableToGetPositionOf.getExtraNames());
		}

		@Override
		public boolean isBusy() throws DeviceException {
			return scannableToMove.isBusy();
		}

		@Override
		public void asynchronousMoveTo(Object position) throws DeviceException {
			scannableToMove.asynchronousMoveTo(position);
		}

		@Override
		public Object getPosition() throws DeviceException {
			return scannableToGetPositionOf.getPosition();
		}
	}

	/**
	 * Do Xas or Xanes scan moving either the mono or Xes energy scannable.
	 * The non scanning energy scannable stays fixed for the duration of the scan.
	 * @throws Exception
	 */
	private void doXASScan() throws Exception {

		Scannable fixedScannable;
		Scannable movingScannable;
		double fixedEnergy;

		// Set the scannable to be moved during scan, and non
		if (xesScanParameters.getScanType() == XesScanParameters.SCAN_XES_REGION_FIXED_MONO) {
			// Scan XES using XANES parameters, fixed mono
			movingScannable = new XesXanesScannable(xes_energy, mono_energy);
			movingScannable.setName(xes_energy.getName());
			fixedScannable = mono_energy;
			fixedEnergy = xesScanParameters.getMonoEnergy();
		} else {
			// Scan mono using Xanes/Xas parameters, fixed XES
			movingScannable = mono_energy;
			fixedScannable = xes_energy;
			fixedEnergy = xesScanParameters.getXesEnergy();
		}

		logger.info("Starting Xas/Xanes scan : fixed scannable = {}, moving scannable = {}", fixedScannable, movingScannable);
		logger.info("Moving {} to initial position {} eV", fixedScannable.getName(), fixedEnergy);
		fixedScannable.waitWhileBusy();
		fixedScannable.moveTo(fixedEnergy);

		SignalParameters xesEnergySignal = new SignalParameters(xes_energy.getName(), xes_energy.getName(), 2,
				xes_energy.getName(), xes_energy.getName());
		i20OutputParameters.addSignal(xesEnergySignal);
		SignalParameters analyserSignal = new SignalParameters(analyserAngle.getName(), analyserAngle.getName(), 2,
				analyserAngle.getName(), analyserAngle.getName());
		i20OutputParameters.addSignal(analyserSignal);

		IScanParameters xasScanParams = (IScanParameters) XMLHelpers.getBeanObject(experimentFullPath + "/",
				xesScanParameters.getScanFileName());

		logger.info("Scan parameters loaded from {}", xesScanParameters.getScanFileName());
		setXasXanesScannable(xasScanParams, movingScannable.getName());

		// Set scannable object to be moved during scan
		xas.setEnergyScannable(movingScannable);

		xas.configureCollection(sampleBean, xasScanParams, detectorBean, outputBean, detectorConfigurationBean,
				experimentFullPath, numRepetitions);

		// Set the names of the XML bean files so they get written to the 'before_scan' meta data.
		String[] filenames = getXmlFileNames();
		xas.setXmlFileNames(filenames[0], xesScanParameters.getScanFileName(), filenames[2], filenames[3], filenames[4]);

		xas.doCollection();
	}

	public Scannable getAnalyserAngle() {
		return analyserAngle;
	}

	public void setAnalyserAngle(Scannable analyserAngle) {
		this.analyserAngle = analyserAngle;
	}

	public Scannable getXes_energy() {
		return xes_energy;
	}

	public void setXes_energy(Scannable xes_energy) {
		this.xes_energy = xes_energy;
	}

	public Scannable getMono_energy() {
		return mono_energy;
	}

	public void setMono_energy(Scannable mono_energy) {
		this.mono_energy = mono_energy;
	}

	public XasScan getXas() {
		return xas;
	}

	public void setXas(EnergyScan xas) {
		this.xas = xas;
	}

	public IXesOffsets getXesOffsets() {
		return xesOffsets;
	}

	public void setXesOffsets(IXesOffsets xesOffsets) {
		this.xesOffsets = xesOffsets;
	}

	public TwoDScanPlotter getTwoDPlotter() {
		return twodplotter;
	}

	public void setTwoDPlotter(TwoDScanPlotter twodplotter) {
		this.twodplotter = twodplotter;
	}
}
