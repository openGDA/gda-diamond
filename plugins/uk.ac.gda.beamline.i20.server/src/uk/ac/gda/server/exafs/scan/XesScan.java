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

import gda.device.Detector;
import gda.device.Scannable;
import gda.device.scannable.TwoDScanPlotter;
import gda.exafs.xes.IXesOffsets;
import gda.jython.scriptcontroller.logging.LoggingScriptController;
import uk.ac.gda.beans.exafs.IDetectorConfigurationParameters;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.SignalParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.beans.exafs.i20.I20OutputParameters;
import uk.ac.gda.util.beans.xml.XMLHelpers;

public class XesScan extends XasScanBase implements XasScan {

	private Scannable analyserAngle;
	private Scannable xes_energy;
	private Scannable mono_energy;
	private XasScan xas;
	private XesScanParameters xesScanParameters;
	private Object[] xes_args;
	private TwoDScanPlotter twodplotter = new TwoDScanPlotter();
	private I20OutputParameters i20OutputParameters;
	private String monoAxisLabel = "bragg1 energy [eV]";
	private String xesAxisLabel = "XESEnergy [eV]";
	private IXesOffsets xesOffsets;

	public XesScan() {
	}

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
		if (innerScanType == XesScanParameters.FIXED_XES_SCAN_XAS || innerScanType == XesScanParameters.FIXED_XES_SCAN_XANES) {
			_doXASScan();
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
	protected Object[] createScanArguments(String sampleName, List<String> descriptions) throws Exception {

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
			twodplotter.setName("twoDPlotter");
			xes_args = ArrayUtils.add(xes_args, twodplotter);
		}
		Detector[] detList = getDetectors();
		for (Detector det : detList) {
			xes_args = ArrayUtils.add(xes_args, det);
		}
		return xes_args;
	}

	private void _doXASScan() throws Exception {

		double initialXESEnergy = (Double) xes_energy.getPosition();
		xes_energy.waitWhileBusy();
		xes_energy.moveTo(xesScanParameters.getXesEnergy());

		SignalParameters xesEnergySignal = new SignalParameters(xes_energy.getName(), xes_energy.getName(), 2,
				xes_energy.getName(), xes_energy.getName());
		i20OutputParameters.addSignal(xesEnergySignal);
		SignalParameters analyserSignal = new SignalParameters(analyserAngle.getName(), analyserAngle.getName(), 2,
				analyserAngle.getName(), analyserAngle.getName());
		i20OutputParameters.addSignal(analyserSignal);
		try {
			IScanParameters xasScanParams = (IScanParameters) XMLHelpers.getBeanObject(experimentFullPath + "/",
					xesScanParameters.getScanFileName());
			xas.configureCollection(sampleBean, xasScanParams, detectorBean, outputBean, detectorConfigurationBean,
					experimentFullPath, numRepetitions);

			// Set the names of the XML bean files so they get written to the 'before_scan' meta data.
			if (xas instanceof XasScanBase) {
				String[] filenames = getXmlFileNames();
				((XasScanBase)xas).setXmlFileNames(filenames[0], xesScanParameters.getScanFileName(), filenames[2], filenames[3], filenames[4]);
			}

			xas.doCollection();

		} finally {
			xes_energy.moveTo(initialXESEnergy);
		}
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

	public void setXas(XasScan xas) {
		this.xas = xas;
	}

	public IXesOffsets getXesOffsets() {
		return xesOffsets;
	}

	public void setXesOffsets(IXesOffsets xesOffsets) {
		this.xesOffsets = xesOffsets;
	}
}
