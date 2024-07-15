/*-
 * Copyright © 2024 Diamond Light Source Ltd.
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

package uk.ac.gda.server.exafs.scan.preparers;

import java.nio.file.Paths;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.Detector;
import gda.device.Scannable;
import gda.device.scannable.ScannableUtils;
import uk.ac.gda.beamline.i20.scannable.MonoMoveWithOffsetScannable;
import uk.ac.gda.beamline.i20.scannable.MonoOptimisation;
import uk.ac.gda.beans.exafs.DetectorConfig;
import uk.ac.gda.beans.exafs.IDetectorParameters;
import uk.ac.gda.beans.exafs.IOutputParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.SpectrometerScanParameters;
import uk.ac.gda.beans.exafs.XanesScanParameters;
import uk.ac.gda.beans.exafs.XasScanParameters;
import uk.ac.gda.beans.exafs.XesScanParameters;
import uk.ac.gda.server.exafs.scan.BeamlinePreparer;
import uk.ac.gda.server.exafs.scan.DetectorPreparer;
import uk.ac.gda.util.beans.xml.XMLHelpers;
import uk.ac.gda.util.beans.xml.XMLRichBean;

/**
 * DetectorPreparer that performs Bragg offset optimisation scan,
 * (functionality refactored from I20DetectorPreparer)
 *
 */
public class BraggOffsetPreparer implements DetectorPreparer {

	private static final Logger logger = LoggerFactory.getLogger(BraggOffsetPreparer.class);

	private MonoOptimisation monoOptimiser;

	private Scannable ionchambers; /** Ionchamber to be used for Xas/Xanes scan */
	private Scannable i1; /** Ionchamber to be used for XES scan */

	private IScanParameters scanBean;
	private IDetectorParameters detectorBean;

	/** Alternative diagnostic detector to use for Bragg offset scan instead of ionchambers/I1 */
	private Scannable diagnosticDetector;

	/** Set to true to force braggoffset scan to use detector set by {@link #diagnosticDetector} */
	private boolean useDiagnosticDetector;

	private String experimentFullPath;

	@Override
	public void configure(IScanParameters scanBean, IDetectorParameters detectorBean, IOutputParameters outputBean,
			String experimentFullPath) throws Exception {
		this.scanBean = scanBean;
		this.detectorBean = detectorBean;
		this.experimentFullPath = experimentFullPath;
	}

	@Override
	public void beforeEachRepetition() throws Exception {
		doMonoOptimisation();
	}

	@Override
	public void completeCollection() {
	}

	@Override
	public Detector[] getExtraDetectors() {
		return null;
	}

	/**
	 * Determine if the scan to be performed is XES mode by presence of medipix
	 * detector in the detectorBean. We need to do this because optimisation scans
	 * use I1 for XES scans and ionchamber for XAS/Xanes scans
	 *
	 * @return
	 */
	private boolean isXesMode() {
		// Definitely an XES scan
		if (scanBean instanceof XesScanParameters) {
			return true;
		}

		// Fixed XES use DetectorConfig list for detector configuration
		List<DetectorConfig> detConfigs = detectorBean.getDetectorConfigurations();
		if (detConfigs == null || detConfigs.isEmpty()) {
			return false;
		}

		// XES scans use Medipix detectors
		return detConfigs.stream()
					.filter(DetectorConfig::isUseDetectorInScan)
					.anyMatch(conf -> conf.getDetectorName().contains("medipix"));
	}

	/**
	 * Run mono optimisation scan (i.e. adjust bragg offset for start and end scan energies to maximise signal
	 * on the detector and set appropriate fitting parameters to be used to adjust the offset during an energy scan).<p>
	 * This is not really a 'detector preparer' type of method, but need to do it here since it should (optionally) be run
	 * at the start of each scan/repetition and there are currently no beforeRepetition methods in the {@link BeamlinePreparer} interface.
	 * @throws Exception
	 */
	private void doMonoOptimisation() throws Exception {
		if (monoOptimiser == null) {
			return;
		}

		monoOptimiser.setUseDiagnosticDetector(useDiagnosticDetector);

		if (useDiagnosticDetector) {
			monoOptimiser.setScannableToMonitor(diagnosticDetector);
		} else {
			// Set the ionchamber to use to make measurement
			if (isXesMode()) {
				monoOptimiser.setScannableToMonitor(i1);
			} else {
				monoOptimiser.setScannableToMonitor(ionchambers);
			}
		}

		logger.info("Running bragg offset scan using {} as detector", monoOptimiser.getScannableToMonitor().getName());

		MonoEnergyRange monoEnergyRange = null;
		boolean is2dScan = false;
		if (scanBean instanceof XanesScanParameters params) {
			monoEnergyRange = getMonoRange(params);
		} else if (scanBean instanceof XasScanParameters params) {
			monoEnergyRange = getMonoRange(params);
		} else if (scanBean instanceof XesScanParameters params) {
			monoEnergyRange = getMonoRange(params);
			is2dScan = params.getScanType() == XesScanParameters.SCAN_XES_SCAN_MONO;
		}

		setScanLoopType(null); // reset scan and loop type on the bragg1WIthOffset before doing optimisation scan

		if (monoEnergyRange!=null && monoOptimiser.getAllowOptimisation()) {
			if (!is2dScan) {

				if (Math.abs(monoEnergyRange.getLowEnergy() - monoEnergyRange.getHighEnergy()) < 1e-3) {
					logger.info("Running monochromator optimisation for single mono energy : low energy = high energy = {}",
							monoEnergyRange.getLowEnergy());
					monoOptimiser.optimise(monoEnergyRange.getLowEnergy(), monoEnergyRange.getLowEnergy());
				} else if (monoEnergyRange.getLowEnergy() > 0
						&& monoEnergyRange.getHighEnergy() > monoEnergyRange.getLowEnergy()) {
					logger.info("Running monochromator optimisation for XAS/XANES scan : low energy = {}, high energy = {}",
							monoEnergyRange.getLowEnergy(), monoEnergyRange.getHighEnergy());
					monoOptimiser.optimise(monoEnergyRange.getLowEnergy(), monoEnergyRange.getHighEnergy());
				}
				// move to low energy again, with optimised bragg offset
				monoOptimiser.getBraggScannable().moveTo(monoEnergyRange.getLowEnergy());
			}
			else {
				// move to near low energy, so that first moveTo also calls optimisation
				monoOptimiser.getBraggScannable().moveTo(monoEnergyRange.getLowEnergy()+0.2);
			}
		}
		// Set the scan type and inner/outer loop sizes on monoOptimiser, so that
		// optimisation can be done at correct time.
		if (scanBean instanceof XesScanParameters scanParams) {
			setScanLoopType(scanParams);
			setLoopSizes(scanParams);
		}

	}


	/**
	 * Set 2D XES num steps per inner loop on MonoMoveWithOffset scannable
	 * @param xesParams
	 */
	private void setLoopSizes(XesScanParameters xesParams) {
		if (monoOptimiser.getBraggScannable() instanceof MonoMoveWithOffsetScannable monoWithOffset) {

			SpectrometerScanParameters specParams = xesParams.getActiveSpectrometerParameters().values().iterator().next();
			int numStepsXes = getNumStepsXes(specParams);
			int numStepsMono = getNumStepsMono(xesParams);

			int numStepsPerInnerLoop = 0, numStepsPerOuterLoop = 0;
			int scanType = xesParams.getScanType();
			if (xesParams.getScanType()==XesScanParameters.SCAN_XES_SCAN_MONO) {
				String loopType = xesParams.getLoopChoice();
				if (loopType.equals(XesScanParameters.EF_OUTER_MONO_INNER)) {
					numStepsPerOuterLoop = numStepsXes;
					numStepsPerInnerLoop = numStepsMono;
				} else if (loopType.equals(XesScanParameters.MONO_OUTER_EF_INNER)) {
					numStepsPerOuterLoop = numStepsMono;
					numStepsPerInnerLoop = numStepsXes;
				}
			} else {
				if (monoMoves(scanType)) {
					numStepsPerInnerLoop = numStepsMono;
				} else if (xesMoves(scanType)) {
					numStepsPerInnerLoop = numStepsXes;
				}
			}
			// set time per step (all same length for 2d scans)
			monoWithOffset.setTimePerStepInnerLoop(specParams.getIntegrationTime());
			monoWithOffset.setNumStepsPerInnerLoop(numStepsPerInnerLoop);
		}
	}

	private int getNumStepsXes(SpectrometerScanParameters xesParams) {
		return ScannableUtils.getNumberSteps(xesParams.getInitialEnergy(), xesParams.getFinalEnergy(), xesParams.getStepSize());
	}

	private int getNumStepsMono(XesScanParameters xesParams) {
		if (xesParams.getScanType() == XesScanParameters.SCAN_XES_FIXED_MONO) {
			return 1;
		} else {
			return ScannableUtils.getNumberSteps(xesParams.getMonoInitialEnergy(), xesParams.getMonoFinalEnergy(), xesParams.getMonoStepSize());
		}
	}

	private boolean monoMoves(int scanType) {
		return scanType == XesScanParameters.SCAN_XES_SCAN_MONO || scanType == XesScanParameters.FIXED_XES_SCAN_XANES
				|| scanType == XesScanParameters.FIXED_XES_SCAN_XAS;
	}

	private boolean xesMoves(int scanType) {
		return scanType == XesScanParameters.SCAN_XES_SCAN_MONO || scanType == XesScanParameters.SCAN_XES_FIXED_MONO;
	}

	/**
	 * Set loop and scan type on MonoMoveWithOffset scannable - for XES mode scans.
	 * @param scanBean , XesScanParameters; use null to set scantype = 0 and looptype="" (back to defaults)
	 */
	private void setScanLoopType(XesScanParameters scanBean) {
		if (monoOptimiser.getBraggScannable() instanceof MonoMoveWithOffsetScannable monoWithOffset) {
			if (scanBean!=null) {
				monoWithOffset.setScanType(scanBean.getScanType());
				monoWithOffset.setLoopType(scanBean.getLoopChoice());
			} else {
				monoWithOffset.setScanType(0);
				monoWithOffset.setLoopType("");
			}
		}
	}

	private static class MonoEnergyRange {
		private final double lowEnergy;
		private final double highEnergy;

		public MonoEnergyRange(double lowEnergy, double highEnergy) {
			this.lowEnergy = lowEnergy;
			this.highEnergy = highEnergy;
		}

		public double getLowEnergy() {
			return lowEnergy;
		}
		public double getHighEnergy() {
			return highEnergy;
		}
	}

	private MonoEnergyRange getMonoRange(XesScanParameters bean) throws Exception {
		int scanType = bean.getScanType();
		if (scanType == XesScanParameters.SCAN_XES_FIXED_MONO || scanType == XesScanParameters.SCAN_XES_REGION_FIXED_MONO) {
			return new MonoEnergyRange(bean.getMonoEnergy(), bean.getMonoEnergy());
		} else if (scanType == XesScanParameters.SCAN_XES_SCAN_MONO) {
			return new MonoEnergyRange(bean.getMonoInitialEnergy(), bean.getMonoFinalEnergy());
		} else{
			// XAS or XANES mono scan
			// load the xml bean of scan settings
			XMLRichBean monoScanBean = XMLHelpers.getBean(Paths.get(experimentFullPath).resolve(bean.getScanFileName()).toFile());
			if (monoScanBean instanceof XasScanParameters xasParams) {
				return getMonoRange(xasParams);
			} else if (monoScanBean instanceof XanesScanParameters xanesParams) {
				return getMonoRange(xanesParams);
			}
		}

		return null;
	}

	private MonoEnergyRange getMonoRange(XasScanParameters bean) {
		return new MonoEnergyRange(bean.getInitialEnergy(), bean.getFinalEnergy());
	}

	private MonoEnergyRange getMonoRange(XanesScanParameters bean) {
		return new MonoEnergyRange(bean.getInitialEnergy(), bean.getFinalEnergy());
	}

	@Override
	public String toString() {
		return "BraggOffsetPreparer [monoOptimiser=" + monoOptimiser.getName() + "]";
	}

	public boolean isUseDiagnosticDetector() {
		return useDiagnosticDetector;
	}

	public void setUseDiagnosticDetector(boolean useDiagnosticDetector) {
		this.useDiagnosticDetector = useDiagnosticDetector;
	}

	public Scannable getDiagnosticDetector() {
		return diagnosticDetector;
	}

	public void setDiagnosticDetector(Scannable diagnosticDetector) {
		this.diagnosticDetector = diagnosticDetector;
	}

	public MonoOptimisation getMonoOptimiser() {
		return monoOptimiser;
	}

	public void setMonoOptimiser(MonoOptimisation monoOptimiser) {
		this.monoOptimiser = monoOptimiser;
	}

	public Scannable getIonchambers() {
		return ionchambers;
	}

	public void setIonchambers(Scannable ionchambers) {
		this.ionchambers = ionchambers;
	}

	public Scannable getI1() {
		return i1;
	}

	public void setI1(Scannable i1) {
		this.i1 = i1;
	}
}
