/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.math3.util.Pair;

public class AlignmentParametersCalculator {

	private AlignmentParametersBean parameterBean;
	private double realDetectorDistance;
	private boolean me2InBeam;

	// Link to ATN1, ATN2, ATN3 in AlignmentParametersBean - for covenience, to save typing.
	private static final String[] ATN1 = AlignmentParametersBean.ATN1;
	private static final String[] ATN2 = AlignmentParametersBean.ATN2;
	private static final String[] ATN3 = AlignmentParametersBean.ATN3;
	private static final String SI_111 = "Si111";
	private static final String SI_311 = "Si311";

	private static class PitchAtn {
		private final double minE;
		private final double maxE;
		private final double pitch;
		private final String atn1;
		private final String atn2;
		private final String atn3;

		public PitchAtn(double minE, double maxE, double pitch, String atn1, String atn2, String atn3) {
			this.minE = minE;
			this.maxE = maxE;
			this.pitch = pitch;
			this.atn1 = atn1;
			this.atn2 = atn2;
			this.atn3 = atn3;
		}
		public boolean inRange(double energy) {
			return energy >= minE && energy < maxE;
		}
		public void applyToBean(AlignmentParametersBean bean) {
			bean.setMe2Pitch(pitch);
			bean.setAtn1(atn1);;
			bean.setAtn2(atn2);
			bean.setAtn3(atn3);
		}
	}

	private static List<PitchAtn> pitchAttenuatorsSi111;
	static {
		pitchAttenuatorsSi111 = new ArrayList<>();
		pitchAttenuatorsSi111.add(new PitchAtn(    0,  7000, 4.0, ATN1[0], ATN2[0], ATN3[0]));
		pitchAttenuatorsSi111.add(new PitchAtn( 7000,  8000, 3.5, ATN1[1], ATN2[0], ATN3[0]));
		pitchAttenuatorsSi111.add(new PitchAtn( 8000,  9600, 3.0, ATN1[2], ATN2[0], ATN3[0]));
		pitchAttenuatorsSi111.add(new PitchAtn( 9600, 12200, 5.0, ATN1[4], ATN2[0], ATN3[0]));
		pitchAttenuatorsSi111.add(new PitchAtn(12200, 99999, 4.0, ATN1[4], ATN2[0], ATN3[0]));
	}

	private static List<PitchAtn> pitchAttenuatorsSi311;
	static {
		pitchAttenuatorsSi311 = new ArrayList<>();
		pitchAttenuatorsSi311.add(new PitchAtn(    0,  8000, 3.5, ATN1[1], ATN2[0], ATN3[0]));
		pitchAttenuatorsSi311.add(new PitchAtn( 8000,  9600, 3.0, ATN1[1], ATN2[0], ATN3[0]));
		pitchAttenuatorsSi311.add(new PitchAtn( 9600, 12200, 5.0, ATN1[4], ATN2[0], ATN3[0]));
		pitchAttenuatorsSi311.add(new PitchAtn(12200, 13500, 4.5, ATN1[0], ATN2[2], ATN3[0]));
		pitchAttenuatorsSi311.add(new PitchAtn(13500, 15200, 4.0, ATN1[4], ATN2[2], ATN3[0]));
		pitchAttenuatorsSi311.add(new PitchAtn(15200, 17400, 3.5, ATN1[3], ATN2[2], ATN3[1]));
		pitchAttenuatorsSi311.add(new PitchAtn(17400, 20300, 3.0, ATN1[0], ATN2[4], ATN3[1]));
		pitchAttenuatorsSi311.add(new PitchAtn(20300, 99999,-1.0, ATN1[0], ATN2[5], ATN3[1]));
	}

	/**
	 * Values to calculate displacement for polychromator benders
	 */
	private static final double POLY_BEND_1_OFFSET = -0.31833;
	private static final double POLY_BEND_2_OFFSET = 0.90130;
	private static Map<Double, Pair<Double, Double>> kValues;
	static {
		kValues = new HashMap<>();
		kValues.put(0.8, Pair.create(11.55945, 10.65425));
		kValues.put(1.0, Pair.create( 9.2847 ,  8.55763));
		kValues.put(1.2, Pair.create( 7.77129,  7.16274));
	}

	/**
	 * Detector surface sizes for each detector [mm]
	 */
	private static Map<String, Double> detectorSizes;
	static {
		detectorSizes = new HashMap<>();
		detectorSizes.put("xh", 51.2);
		detectorSizes.put("xstrip", 25.6);
		detectorSizes.put("frelon", 28.672); //2048 * 14 micron
	}

	/**
	 * Crystal lattice constants, 'd' spacing [Angstroms].
	 */
	private static Map<String, Double> latticeConstants;
	static {
		latticeConstants = new HashMap<>();
		latticeConstants.put(SI_111, 3.1357017);
		latticeConstants.put(SI_311, 1.6375668);
	}

	public AlignmentParametersCalculator(AlignmentParametersBean bean) {
		parameterBean = bean;
	}

	public AlignmentParametersBean getParameterBean() {
		return parameterBean;
	}

	public void setParameterBean(AlignmentParametersBean parameterBean) {
		this.parameterBean = parameterBean;
	}

	public void calculateParameters() {
		setStripes();
		setPitchAndAttenuators();
		setBraggAngle();
		setBenders();
		setPrimarySlits();
		setDetectorPosition();
		setEnergyBandwidth();
		setPower();
	}

	public void setStripes() {
		parameterBean.setMe1stripe(getMe1Strip(getEnergy()));
		parameterBean.setMe2stripe(getMe2Stripe(getEnergy()));
	}

	public void setPitchAndAttenuators() {
		double energy = getEnergy();
		PitchAtn pitchAttenuator = null;
		if (parameterBean.getCrystalCut().equals(SI_111)) {
			pitchAttenuator = getPitchAtnForEnergy(energy, pitchAttenuatorsSi111);
		} else {
			pitchAttenuator = getPitchAtnForEnergy(energy, pitchAttenuatorsSi311);
		}
		if (pitchAttenuator != null) {
			pitchAttenuator.applyToBean(parameterBean);
		}
	}

	public void setBraggAngle() {
		double bragg = calcBragg(getEnergy());
		parameterBean.setBraggAngle(Math.toDegrees(bragg));
		parameterBean.setArm2Theta(Math.toDegrees(bragg) * 2);
	}

	public void setBenders() {
		Double qValue = parameterBean.getQ();
		if (qValue == null) {
			throw new RuntimeException("Q value not set, so cannot calculate bender values");
		}
		if (kValues.containsKey(qValue)) {
			// get sine of bragg angle (convert from degrees to radians)
			double sineBragg = Math.sin( Math.toRadians(parameterBean.getBraggAngle()));
			Pair<Double, Double> values = kValues.get(qValue);
			parameterBean.setPolyBend1(POLY_BEND_1_OFFSET + values.getFirst()*sineBragg);
			parameterBean.setPolyBend2(POLY_BEND_2_OFFSET + values.getSecond()*sineBragg);
		} else {
			throw new RuntimeException("Q value not valid!. Must be 0.8, 1.0 or 1.2");
		}
	}

	public void setPrimarySlits() {
		double slitGap = getPrimarySlitGap(parameterBean.getBraggAngle());
		parameterBean.setPrimarySlitGap(Math.min(1.6, slitGap));  // limit to 1.6 mradians
	}

	public void setDetectorPosition() {
	    parameterBean.setDetectorDistance(getDetectorDistance());
	    parameterBean.setDetectorHeight(calcDetectorHeight(me2InBeam()));
	}

	public void setEnergyBandwidth() {
		double calculatedDetDistance = getDetectorDistance();
		double currentDetectorDistance = getRealDetectorDistance();
		double deltaE = calcBandwidth(Math.max(calculatedDetDistance, currentDetectorDistance));
		parameterBean.setReadBackEnergyBandwidth(deltaE);

		deltaE = calcBandwidth(calculatedDetDistance);
		parameterBean.setEnergyBandwidth(deltaE);
	}

	public void setPower() {
	    parameterBean.setPower(0.0);
	}

	/**
	 * Detector distance from sample position to get full spectrum on the detector
	 * @return distance [metres]
	 */
	public double getDetectorDistance() {
	    double alpha_mrad = parameterBean.getPrimarySlitGap();
	    double dist_poly_to_source = parameterBean.getSourceToPolyDistance();
	    double q_m = parameterBean.getQ();
	    double s_mm = getDetectorSize(parameterBean.getDetector());
	    return (s_mm * q_m) / (alpha_mrad * dist_poly_to_source);
	}

	public boolean me2InBeam() {
		return me2InBeam;
	}

	public void setMe2InBean(boolean inBeam) {
		me2InBeam = inBeam;
	}

	private static double cot(double angle) {
		return 1.0/Math.tan(angle);
	}

	public double calcBandwidth(double detectorDistance) {
	    double energy = getEnergy();
	    double detSize = getDetectorSize(parameterBean.getDetector());
	    double braggRad = Math.toRadians(parameterBean.getBraggAngle());

	    double polySourceDist = parameterBean.getSourceToPolyDistance();
	    double q_m = parameterBean.getQ();

	    // Energy bandwidth formaula from Jython script.
	    return energy * cot(braggRad) * (detSize/detectorDistance) * (polySourceDist-q_m)/(2*polySourceDist*1000); // in jython script

	    // Formulae as given in i20_EDE_GDA doc; jython script one is different. Which is correct?
//	    double deltaE = 0.0;
//	    double slitGap = getPrimarySlitGap(parameterBean.getBraggAngle());
//	    double realDetDist = getRealDetectorDistance();
//	    if (realDetDist > getDetectorDistance()) {
//	        deltaE = energy * 1.0/Math.tan(braggRad * (detSize/realDetDist) * (polySourceDist-q_m)/(2*polySourceDist*1000));
//	    } else {
//	    	deltaE = energy * 1.0/Math.tan(braggRad * slitGap * (polySourceDist-q_m)/(2*q_m*1000));
//	    }
//	    return deltaE;
	}

	public double calcDetectorHeight(boolean inBeam) {
		// # TODO beam is going upwards at an angle of 6mrad, so based on
		// # detector z values, their height needs to be calculated
		double offset = 0.0;
		double detHeightMm = offset - 6 * (parameterBean.getQ() + getRealDetectorDistance());
		if (inBeam) {
			detHeightMm += 3.0;
		}
		return detHeightMm;
	}

	private PitchAtn getPitchAtnForEnergy(double energyEv, List<PitchAtn> pitchAtns) {
		return pitchAtns.stream().filter(p -> p.inRange(energyEv)).findFirst().orElse(null);
	}

	public double getEnergy() {
		return parameterBean.getEdge().getEnergy();
	}

	/**
	 * Calculate primary slit gap for a given bragg angle (alpha)
	 * @param braggAngle [degrees]
	 * @return slit gap [mrad]
	 */
	public double getPrimarySlitGap(double braggAngle) {
		return 1000.0*Math.sin(Math.toRadians(braggAngle))*parameterBean.getPolychromatorLength()/(1000.0*parameterBean.getSourceToPolyDistance());
	}

	/**
	 * Get ME1 stripe for given energy (eV)
	 * @param energyEv [eV]
	 * @return ME1Stripe
	 */
	public String getMe1Strip(double energyEv) {
	    if (energyEv > 20300) {
	        return AlignmentParametersBean.ME1Stripe[1];
	    } else {
	        return AlignmentParametersBean.ME1Stripe[0];
	    }
	}

	/**
	 * Get ME2 stripe for given energy (eV)
	 * @param energyEv [eV]
	 * @return ME2Stripe
	 */
	public String getMe2Stripe(double energyEv) {
	    if (energyEv < 9600) {
	        return AlignmentParametersBean.ME2Stripe[0];
		} else if (energyEv >= 9600 && energyEv < 20300) {
	    	return AlignmentParametersBean.ME2Stripe[1];
	    } else {
	        return AlignmentParametersBean.ME2Stripe[2];
	    }
	}

	/**
	 *
	 * @param crystalCut either "Si 111" or "Si 311"
	 * @return Crystal lattice spacing for given crystal cut [Angstrom]
	 */
	public double getLatticeConstant(String crystalCut) {
	    return latticeConstants.getOrDefault(crystalCut, latticeConstants.get(SI_311));
	}

	/**
	 * Size of the detector surface (s)
	 * @param detectorName
	 * @return detector size [mm]
	 */
	public double getDetectorSize(String detectorName) {
		return detectorSizes.getOrDefault(detectorName, detectorSizes.get("xh"));
	}

	/**
	 * Calculate bragg angle [radians] for given energy [eV]
	 * @param braggEnergy
	 * @return
	 */
	public double calcBragg(double braggEnergy) {
        double dSpacing = getLatticeConstant(parameterBean.getCrystalCut());
        return Math.asin(6199.0 / (braggEnergy * dSpacing));
	}

	/**
	 *
	 * @return Real detector distance [metres]
	 */
	public double getRealDetectorDistance() {
	    return realDetectorDistance;
	}

	/**
	 * Set the real distance from sample (focu) to detector [metres]
	 * @param distance
	 */
	public void setRealDetectorDistance(double distance) {
		realDetectorDistance = distance;
	}
}
