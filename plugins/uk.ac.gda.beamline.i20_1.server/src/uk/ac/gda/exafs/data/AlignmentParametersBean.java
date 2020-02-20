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

import java.io.Serializable;

import com.google.gson.Gson;

import gda.util.exafs.AbsorptionEdge;

public class AlignmentParametersBean implements Serializable {

	private static final long serialVersionUID = 1L;

	public static String[] CrystalType = new String[] { "BRAGG", "LAUE" };

	public static String[] ME1Stripe = new String[] { "Rhodium", "Platinum", "Zero" };

	public static String[] ME2Stripe = new String[] { "Silicon", "Rhodium", "Out of beam" };

	public static String[] ATN1 = new String[] { "Empty", "pC 0.1mm", "pC 0.2mm", "pC 0.4mm", "pC 0.6mm", "pC 0.8mm" };

	public static String[] ATN1Values = new String[] { "none", "Pyro-C 0.1mm", "Pyro-C 0.2mm", "Pyro-C 0.4mm",
		"Pyro-C 0.6mm", "Pyro-C 0.8mm" };

	public static String[] ATN2 = new String[] { "Empty", "pC 0.1mm", "pC 1.0mm", "pC 2.0mm", "SiC 0.2mm", "SiC 0.4mm" };

	public static String[] ATN2Values = new String[] { "none", "Pyro-C 0.1mm", "Pyro-C 1.0mm", "Pyro-C 2.0mm",
		"SiC 0.2mm", "SiC 0.4mm" };

	public static String[] ATN3 = new String[] { "Empty", "pC 1.0mm", "pC 2.0mm", "pC 0.6mm", "SiC1.5mm" };

	public static String[] ATN3Values = new String[] { "none", "Pyro-C 1.0mm", "Pyro-C 2.0mm", "SiC 0.6mm", "SiC 1.5mm" };

	public static Double[] Q = new Double[] { 0.8, 1.0, 1.2 };

	// inputs
	private String crystalType = null;
	private String crystalCut = null;
	private Double q = null; // must be a value in Q array
	private String detector = null;
	private AbsorptionEdge edge = null; // for the moment, this should match element and edge

	private Double polychromatorLength = 250.0; // length of the polychromator crystal [mm]
	private Double sourceToPolyDistance = 45.1; // distance from source to polychromator crystal [metres]

	// outputs
	private Double wigglerGap = 18.5; // mm
	private Double primarySlitGap = null; // mrad

	private String me1stripe = null;
	private String me2stripe = null;
	private Double me2Pitch = null; // mrad
	private Double polyBend1 = 5.0; // mm
	private Double polyBend2 = 5.0; // mm
	private Double braggAngle = null; // deg
	private Double arm2Theta = null; // deg, 2*bragg [fixed]
	private Double detectorDistance = null; // m
	private Double detectorHeight = null; // mm

	private String atn1 = null;
	private String atn2 = null;
	private String atn3 = null;

	private Double energyBandwidth = null; // eV  This is Delta-E.

	private Double power = null; // W

	private Double readBackEnergyBadwidth = null;

	public AlignmentParametersBean(String crystalType, String crystalCut, Double q, String detector, AbsorptionEdge edge) {
		super();
		this.crystalType = crystalType;
		this.crystalCut = crystalCut;
		this.q = q;
		this.detector = detector;
		this.edge = edge;
	}

	@Override
	public String toString() {
		return crystalType + ", " + crystalCut+", " + q +"m, "+ detector +", "+ edge;
	}

	public String toJson() {
		return toJson(this);
	}

	public static String toJson(AlignmentParametersBean bean) {
		Gson gson = new Gson();
		return gson.toJson(bean);
	}

	public static AlignmentParametersBean fromJson(String jsonString) {
		Gson gson = new Gson();
		return gson.fromJson(jsonString, AlignmentParametersBean.class);
	}

	public String getCrystalType() {
		return crystalType;
	}

	public void setCrystalType(String crystalType) {
		this.crystalType = crystalType;
	}

	public String getCrystalCut() {
		return crystalCut;
	}

	public void setCrystalCut(String crystalCut) {
		this.crystalCut = crystalCut;
	}

	public Double getQ() {
		return q;
	}

	public void setQ(Double q) {
		this.q = q;
	}

	public String getDetector() {
		return detector;
	}

	public void setDetector(String detector) {
		this.detector = detector;
	}

	public AbsorptionEdge getEdge() {
		return edge;
	}

	public void setEdge(AbsorptionEdge edge) {
		this.edge = edge;
	}

	public Double getWigglerGap() {
		return wigglerGap;
	}

	public void setWigglerGap(Double wigglerGap) {
		this.wigglerGap = wigglerGap;
	}

	public Double getPolyBend1() {
		return polyBend1;
	}

	public void setPolyBend1(Double polyBend1) {
		this.polyBend1 = polyBend1;
	}

	public Double getPolyBend2() {
		return polyBend2;
	}

	public void setPolyBend2(Double polyBend2) {
		this.polyBend2 = polyBend2;
	}

	public String getMe1stripe() {
		return me1stripe;
	}

	public void setMe1stripe(String me1stripe) {
		this.me1stripe = me1stripe;
	}

	public String getMe2stripe() {
		return me2stripe;
	}

	public void setMe2stripe(String me2stripe) {
		this.me2stripe = me2stripe;
	}

	/**
	 *
	 * @return Bragg angle [degrees]
	 */
	public Double getBraggAngle() {
		return braggAngle;
	}

	/**
	 * Set the bragg angle [degrees]
	 * @param braggAngle
	 */
	public void setBraggAngle(Double braggAngle) {
		this.braggAngle = braggAngle;
	}

	/**
	 * Primary slit gap size [mrad]
	 * @return primarySlitGap [mrad]
	 */
	public Double getPrimarySlitGap() {
		return primarySlitGap;
	}

	public void setPrimarySlitGap(Double primarySlitGap) {
		this.primarySlitGap = primarySlitGap;
	}

	public Double getArm2Theta() {
		return arm2Theta;
	}

	public void setArm2Theta(Double arm2Theta) {
		this.arm2Theta = arm2Theta;
	}

	public Double getDetectorDistance() {
		return detectorDistance;
	}

	public void setDetectorDistance(Double detectorDistance) {
		this.detectorDistance = detectorDistance;
	}

	public Double getMe2Pitch() {
		return me2Pitch;
	}

	public void setMe2Pitch(Double me2Pitch) {
		this.me2Pitch = me2Pitch;
	}

	public String getAtn1() {
		return atn1;
	}

	public void setAtn1(String atn1) {
		this.atn1 = atn1;
	}

	public String getAtn2() {
		return atn2;
	}

	public void setAtn2(String atn2) {
		this.atn2 = atn2;
	}

	public String getAtn3() {
		return atn3;
	}

	public void setAtn3(String atn3) {
		this.atn3 = atn3;
	}

	public Double getPower() {
		return power;
	}

	public void setPower(Double power) {
		this.power = power;
	}

	public Double getDetectorHeight() {
		return detectorHeight;
	}

	public void setDetectorHeight(Double detectorHeight) {
		this.detectorHeight = detectorHeight;
	}

	public Double getEnergyBandwidth() {
		return energyBandwidth;
	}

	public void setEnergyBandwidth(Double energyBandwidth) {
		this.energyBandwidth = energyBandwidth;
	}

	public Double getReadBackEnergyBandwidth() {
		return readBackEnergyBadwidth;
	}

	public void setReadBackEnergyBandwidth(Double value) {
		readBackEnergyBadwidth = value;
	}

	/**
	 *
	 * @return Length of polychromator crystal [mm]
	 */
	public Double getPolychromatorLength() {
		return polychromatorLength;
	}

	public void setPolychromatorLength(Double polychromatorLength) {
		this.polychromatorLength = polychromatorLength;
	}

	/**
	 * Distance from source to polychromator surface (p)
	 * @return Distance from source to polychromator crystal [metres]
	 */
	public Double getSourceToPolyDistance() {
		return sourceToPolyDistance;
	}

	public void setSourceToPolyDistance(Double sourceToPolyDistance) {
		this.sourceToPolyDistance = sourceToPolyDistance;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + ((arm2Theta == null) ? 0 : arm2Theta.hashCode());
		result = prime * result + ((atn1 == null) ? 0 : atn1.hashCode());
		result = prime * result + ((atn2 == null) ? 0 : atn2.hashCode());
		result = prime * result + ((atn3 == null) ? 0 : atn3.hashCode());
		result = prime * result + ((braggAngle == null) ? 0 : braggAngle.hashCode());
		result = prime * result + ((crystalCut == null) ? 0 : crystalCut.hashCode());
		result = prime * result + ((crystalType == null) ? 0 : crystalType.hashCode());
		result = prime * result + ((detector == null) ? 0 : detector.hashCode());
		result = prime * result + ((detectorDistance == null) ? 0 : detectorDistance.hashCode());
		result = prime * result + ((detectorHeight == null) ? 0 : detectorHeight.hashCode());
		result = prime * result + ((edge == null) ? 0 : edge.hashCode());
		result = prime * result + ((me1stripe == null) ? 0 : me1stripe.hashCode());
		result = prime * result + ((me2Pitch == null) ? 0 : me2Pitch.hashCode());
		result = prime * result + ((me2stripe == null) ? 0 : me2stripe.hashCode());
		result = prime * result + ((polyBend1 == null) ? 0 : polyBend1.hashCode());
		result = prime * result + ((polyBend2 == null) ? 0 : polyBend2.hashCode());
		result = prime * result + ((power == null) ? 0 : power.hashCode());
		result = prime * result + ((primarySlitGap == null) ? 0 : primarySlitGap.hashCode());
		result = prime * result + ((q == null) ? 0 : q.hashCode());
		result = prime * result + ((energyBandwidth == null) ? 0 : energyBandwidth.hashCode());
		result = prime * result + ((wigglerGap == null) ? 0 : wigglerGap.hashCode());
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj) {
			return true;
		}
		if (obj == null) {
			return false;
		}
		if (getClass() != obj.getClass()) {
			return false;
		}
		AlignmentParametersBean other = (AlignmentParametersBean) obj;
		if (arm2Theta == null) {
			if (other.arm2Theta != null) {
				return false;
			}
		} else if (!arm2Theta.equals(other.arm2Theta)) {
			return false;
		}
		if (atn1 == null) {
			if (other.atn1 != null) {
				return false;
			}
		} else if (!atn1.equals(other.atn1)) {
			return false;
		}
		if (atn2 == null) {
			if (other.atn2 != null) {
				return false;
			}
		} else if (!atn2.equals(other.atn2)) {
			return false;
		}
		if (atn3 == null) {
			if (other.atn3 != null) {
				return false;
			}
		} else if (!atn3.equals(other.atn3)) {
			return false;
		}
		if (braggAngle == null) {
			if (other.braggAngle != null) {
				return false;
			}
		} else if (!braggAngle.equals(other.braggAngle)) {
			return false;
		}
		if (crystalCut == null) {
			if (other.crystalCut != null) {
				return false;
			}
		} else if (!crystalCut.equals(other.crystalCut)) {
			return false;
		}
		if (crystalType == null) {
			if (other.crystalType != null) {
				return false;
			}
		} else if (!crystalType.equals(other.crystalType)) {
			return false;
		}
		if (detector == null) {
			if (other.detector != null) {
				return false;
			}
		} else if (!detector.equals(other.detector)) {
			return false;
		}
		if (detectorDistance == null) {
			if (other.detectorDistance != null) {
				return false;
			}
		} else if (!detectorDistance.equals(other.detectorDistance)) {
			return false;
		}
		if (detectorHeight == null) {
			if (other.detectorHeight != null) {
				return false;
			}
		} else if (!detectorHeight.equals(other.detectorHeight)) {
			return false;
		}
		if (edge == null) {
			if (other.edge != null) {
				return false;
			}
		} else if (!edge.equals(other.edge)) {
			return false;
		}
		if (me1stripe == null) {
			if (other.me1stripe != null) {
				return false;
			}
		} else if (!me1stripe.equals(other.me1stripe)) {
			return false;
		}
		if (me2Pitch == null) {
			if (other.me2Pitch != null) {
				return false;
			}
		} else if (!me2Pitch.equals(other.me2Pitch)) {
			return false;
		}
		if (me2stripe == null) {
			if (other.me2stripe != null) {
				return false;
			}
		} else if (!me2stripe.equals(other.me2stripe)) {
			return false;
		}
		if (polyBend1 == null) {
			if (other.polyBend1 != null) {
				return false;
			}
		} else if (!polyBend1.equals(other.polyBend1)) {
			return false;
		}
		if (polyBend2 == null) {
			if (other.polyBend2 != null) {
				return false;
			}
		} else if (!polyBend2.equals(other.polyBend2)) {
			return false;
		}
		if (power == null) {
			if (other.power != null) {
				return false;
			}
		} else if (!power.equals(other.power)) {
			return false;
		}
		if (primarySlitGap == null) {
			if (other.primarySlitGap != null) {
				return false;
			}
		} else if (!primarySlitGap.equals(other.primarySlitGap)) {
			return false;
		}
		if (q == null) {
			if (other.q != null) {
				return false;
			}
		} else if (!q.equals(other.q)) {
			return false;
		}
		if (energyBandwidth == null) {
			if (other.energyBandwidth != null) {
				return false;
			}
		} else if (!energyBandwidth.equals(other.energyBandwidth)) {
			return false;
		}
		if (wigglerGap == null) {
			if (other.wigglerGap != null) {
				return false;
			}
		} else if (!wigglerGap.equals(other.wigglerGap)) {
			return false;
		}
		return true;
	}
}