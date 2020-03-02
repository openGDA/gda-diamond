/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.ui.data;

import java.io.Serializable;

/**
 * Defines a group of equally sized data collections used in an EDE scan. To define a complex experiment where the data
 * collection time, or pause time between collections, varies then multiple Frames must be defined.
 */
public class TimingGroup implements Serializable {

	private static final long serialVersionUID = 1L;

	// basic info
	private String label; // to uniquely identify each frame in the UI
	private double timePerScan; // in s
	private int numberOfScansPerFrame = 0; // if zero then use the timePerFrame when setting up the TimingGroup in TFG
	private double timePerFrame; // in s  // use only if numberOfScansPerFrame == 0
	private int numberOfFrames = 1; // number of times to repeat the same set of scans before the EDE scan should move
	// on to the next TimingGroup

	// delays
	private double preceedingTimeDelay; // in s
	private double delayBetweenFrames; // in s

	// Input Triggers
	private boolean groupTrig;
	private boolean allFramesTrig;
	private boolean framesExclFirstTrig;
	private boolean scansTrig;

	private int groupTrigLemo = 0;
	private int allFramesTrigLemo = 0;
	private int framesExclFirstTrigLemo = 0;
	private int scansTrigLemo = 0;

	public enum InputTriggerLemoNumbers {
		ZERO(0, false, "0"),
		ZERO_FALLING(0, true, "0 Falling"),
		ONE(1, false, "1"),
		ONE_FALLING(1, true, "1 Falling"),
		TWO(2, false, "2"),
		TWO_FALLING(2, true, "2 Falling"),
		THREE(3, false, "1"),
		THREE_FALLING(3, true, "3 Falling"),
		FOUR(4, false, "1"),
		FOUR_FALLING(4, true, "4 Falling"),
		FIVE(5, false, "1"),
		FIVE_FALLING(5, true, "5 Falling"),
		SIX(6, false, "1"),
		SIX_FALLING(6, true, "6 Falling"),
		SEVEN(7, false, "1"),
		SEVEN_FALLING(7, true, "7 Falling");
		private final int lemoNumber;
		private final boolean isFallingEdge;
		private final String Label;
		private InputTriggerLemoNumbers(int lemoNumber, boolean isFallingEdge, String Label) {
			this.lemoNumber = lemoNumber;
			this.isFallingEdge = isFallingEdge;
			this.Label = Label;
		}
		public int getLemoNumber() {
			return lemoNumber;
		}
		public boolean isFallingEdge() {
			return isFallingEdge;
		}
		public String getLabel() {
			return Label;
		}
	}

	private boolean groupTrigRisingEdge = true;
	private boolean allFramesTrigRisingEdge = true;
	private boolean framesExclFirstTrigRisingEdge = true;
	private boolean scansTrigRisingEdge = true;

	// Enable Output Triggers
	private boolean outLemo0;
	private boolean outLemo1;
	private boolean outLemo2;
	private boolean outLemo3;
	private boolean outLemo4;
	private boolean outLemo5;
	private boolean outLemo6;
	private boolean outLemo7;

	private boolean useTopupChecker;

	public String getHeaderDescription() {
		String desc = "has " + numberOfFrames + " frames. Accumulations are " + timePerScan + "s long";
		if (numberOfScansPerFrame == 0){
			desc += ", to a total of " + timePerFrame +"s per frame";
		} else {
			desc += "," + numberOfScansPerFrame + " accumulations per frame";
		}
		return desc;
	}

	public int getTotalNumberScans() {

		Double scansPerFrame;
		if (numberOfScansPerFrame == 0) {

			// just an estimate
			scansPerFrame = Math.floor(timePerFrame / timePerScan);
			if (scansPerFrame.isNaN() || scansPerFrame < 1) {
				scansPerFrame = 1d;
			}
		} else {
			scansPerFrame = (double) numberOfScansPerFrame;
		}

		int numFrame = numberOfFrames;
		if (numFrame == 0){
			numFrame = 1;
		}

		return (int) Math.round(numberOfFrames * scansPerFrame);
	}

	public int getNumberOfFrames() {
		return numberOfFrames;
	}

	public void setNumberOfFrames(int numberOfRepetitions) {
		numberOfFrames = numberOfRepetitions;
	}

	public double getTimePerScan() {
		return timePerScan;
	}

	public void setTimePerScan(double timePerScan) {
		this.timePerScan = timePerScan;
	}

	public double getPreceedingTimeDelay() {
		return preceedingTimeDelay;
	}

	public void setPreceedingTimeDelay(double preceedingTimeDelay) {
		this.preceedingTimeDelay = preceedingTimeDelay;
	}

	public void setDelayBetweenFrames(double delayBetweenFrames) {
		this.delayBetweenFrames = delayBetweenFrames;
	}

	public double getDelayBetweenFrames() {
		return delayBetweenFrames;
	}

	public void setLabel(String label) {
		this.label = label;
	}

	public String getLabel() {
		return label;
	}

	public double getTimePerFrame() {
		return timePerFrame;
	}

	public void setTimePerFrame(double timePerFrame) {
		this.timePerFrame = timePerFrame;
	}

	public boolean isGroupTrig() {
		return groupTrig;
	}

	public void setGroupTrig(boolean groupTrig) {
		this.groupTrig = groupTrig;
	}

	public boolean isAllFramesTrig() {
		return allFramesTrig;
	}

	public void setAllFramesTrig(boolean allFramesTrig) {
		this.allFramesTrig = allFramesTrig;
	}

	public boolean isFramesExclFirstTrig() {
		return framesExclFirstTrig;
	}

	public void setFramesExclFirstTrig(boolean framesExclFirstTrig) {
		this.framesExclFirstTrig = framesExclFirstTrig;
	}

	public boolean isScansTrig() {
		return scansTrig;
	}

	public void setScansTrig(boolean scansTrig) {
		this.scansTrig = scansTrig;
	}

	public int getGroupTrigLemo() {
		return groupTrigLemo;
	}

	public void setGroupTrigLemo(int groupTrigLemo) {
		this.groupTrigLemo = groupTrigLemo;
	}

	public int getAllFramesTrigLemo() {
		return allFramesTrigLemo;
	}

	public void setAllFramesTrigLemo(int allFramesTrigLemo) {
		this.allFramesTrigLemo = allFramesTrigLemo;
	}

	public int getFramesExclFirstTrigLemo() {
		return framesExclFirstTrigLemo;
	}

	public void setFramesExclFirstTrigLemo(int framesExclFirstTrigLemo) {
		this.framesExclFirstTrigLemo = framesExclFirstTrigLemo;
	}

	public int getScansTrigLemo() {
		return scansTrigLemo;
	}

	public void setScansTrigLemo(int scansTrigLemo) {
		this.scansTrigLemo = scansTrigLemo;
	}

	public boolean isOutLemo0() {
		return outLemo0;
	}

	public void setOutLemo0(boolean outLemo0) {
		this.outLemo0 = outLemo0;
	}

	public boolean isOutLemo1() {
		return outLemo1;
	}

	public void setOutLemo1(boolean outLemo1) {
		this.outLemo1 = outLemo1;
	}

	public boolean isOutLemo2() {
		return outLemo2;
	}

	public void setOutLemo2(boolean outLemo2) {
		this.outLemo2 = outLemo2;
	}

	public boolean isOutLemo3() {
		return outLemo3;
	}

	public void setOutLemo3(boolean outLemo3) {
		this.outLemo3 = outLemo3;
	}

	public boolean isOutLemo4() {
		return outLemo4;
	}

	public void setOutLemo4(boolean outLemo4) {
		this.outLemo4 = outLemo4;
	}

	public boolean isOutLemo5() {
		return outLemo5;
	}

	public void setOutLemo5(boolean outLemo5) {
		this.outLemo5 = outLemo5;
	}

	public boolean isOutLemo6() {
		return outLemo6;
	}

	public void setOutLemo6(boolean outLemo6) {
		this.outLemo6 = outLemo6;
	}

	public boolean isOutLemo7() {
		return outLemo7;
	}

	public void setOutLemo7(boolean outLemo7) {
		this.outLemo7 = outLemo7;
	}

	public boolean[] getOutLemos() {
		return new boolean[] { outLemo0, outLemo1, outLemo2, outLemo3, outLemo4, outLemo5, outLemo6, outLemo7 };
	}

	public boolean isAllFramesTrigRisingEdge() {
		return allFramesTrigRisingEdge;
	}

	public void setAllFramesTrigRisingEdge(boolean allFramesTrigRisingEdge) {
		this.allFramesTrigRisingEdge = allFramesTrigRisingEdge;
	}

	public boolean isFramesExclFirstTrigRisingEdge() {
		return framesExclFirstTrigRisingEdge;
	}

	public void setFramesExclFirstTrigRisingEdge(boolean framesExclFirstTrigRisingEdge) {
		this.framesExclFirstTrigRisingEdge = framesExclFirstTrigRisingEdge;
	}

	public boolean isScansTrigRisingEdge() {
		return scansTrigRisingEdge;
	}

	public void setScansTrigRisingEdge(boolean scansTrigRisingEdge) {
		this.scansTrigRisingEdge = scansTrigRisingEdge;
	}

	public boolean isGroupTrigRisingEdge() {
		return groupTrigRisingEdge;
	}

	public void setGroupTrigRisingEdge(boolean groupTrigRisingEdge) {
		this.groupTrigRisingEdge = groupTrigRisingEdge;
	}

	public int getNumberOfScansPerFrame() {
		return numberOfScansPerFrame;
	}

	/**
	 * If this is 0 then the timePerFrame attribute will be used when creating the timing group. I.e. in the setup-group
	 * command the frame-time qualifier will be used when numberOfScansPerFrame == 0
	 *
	 * @param numberOfScansPerFrame
	 */
	public void setNumberOfScansPerFrame(int numberOfScansPerFrame) {
		this.numberOfScansPerFrame = numberOfScansPerFrame;
	}

	public boolean getUseTopChecker() {
		return useTopupChecker;
	}

	public void setUseTopupChecker(boolean useTopupChecker) {
		this.useTopupChecker = useTopupChecker;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + (allFramesTrig ? 1231 : 1237);
		result = prime * result + allFramesTrigLemo;
		result = prime * result + (allFramesTrigRisingEdge ? 1231 : 1237);
		long temp;
		temp = Double.doubleToLongBits(delayBetweenFrames);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		result = prime * result + (framesExclFirstTrig ? 1231 : 1237);
		result = prime * result + framesExclFirstTrigLemo;
		result = prime * result + (framesExclFirstTrigRisingEdge ? 1231 : 1237);
		result = prime * result + (groupTrig ? 1231 : 1237);
		result = prime * result + groupTrigLemo;
		result = prime * result + (groupTrigRisingEdge ? 1231 : 1237);
		result = prime * result + ((label == null) ? 0 : label.hashCode());
		result = prime * result + numberOfFrames;
		result = prime * result + numberOfScansPerFrame;
		result = prime * result + (outLemo0 ? 1231 : 1237);
		result = prime * result + (outLemo1 ? 1231 : 1237);
		result = prime * result + (outLemo2 ? 1231 : 1237);
		result = prime * result + (outLemo3 ? 1231 : 1237);
		result = prime * result + (outLemo4 ? 1231 : 1237);
		result = prime * result + (outLemo5 ? 1231 : 1237);
		result = prime * result + (outLemo6 ? 1231 : 1237);
		result = prime * result + (outLemo7 ? 1231 : 1237);
		temp = Double.doubleToLongBits(preceedingTimeDelay);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		result = prime * result + (scansTrig ? 1231 : 1237);
		result = prime * result + scansTrigLemo;
		result = prime * result + (scansTrigRisingEdge ? 1231 : 1237);
		temp = Double.doubleToLongBits(timePerFrame);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		temp = Double.doubleToLongBits(timePerScan);
		result = prime * result + (int) (temp ^ (temp >>> 32));
		result = prime * result + (useTopupChecker ? 1231 : 1237);
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
		TimingGroup other = (TimingGroup) obj;
		if (allFramesTrig != other.allFramesTrig) {
			return false;
		}
		if (allFramesTrigLemo != other.allFramesTrigLemo) {
			return false;
		}
		if (allFramesTrigRisingEdge != other.allFramesTrigRisingEdge) {
			return false;
		}
		if (Double.doubleToLongBits(delayBetweenFrames) != Double.doubleToLongBits(other.delayBetweenFrames)) {
			return false;
		}
		if (framesExclFirstTrig != other.framesExclFirstTrig) {
			return false;
		}
		if (framesExclFirstTrigLemo != other.framesExclFirstTrigLemo) {
			return false;
		}
		if (framesExclFirstTrigRisingEdge != other.framesExclFirstTrigRisingEdge) {
			return false;
		}
		if (groupTrig != other.groupTrig) {
			return false;
		}
		if (groupTrigLemo != other.groupTrigLemo) {
			return false;
		}
		if (groupTrigRisingEdge != other.groupTrigRisingEdge) {
			return false;
		}
		if (label == null) {
			if (other.label != null) {
				return false;
			}
		} else if (!label.equals(other.label)) {
			return false;
		}
		if (numberOfFrames != other.numberOfFrames) {
			return false;
		}
		if (numberOfScansPerFrame != other.numberOfScansPerFrame) {
			return false;
		}
		if (outLemo0 != other.outLemo0) {
			return false;
		}
		if (outLemo1 != other.outLemo1) {
			return false;
		}
		if (outLemo2 != other.outLemo2) {
			return false;
		}
		if (outLemo3 != other.outLemo3) {
			return false;
		}
		if (outLemo4 != other.outLemo4) {
			return false;
		}
		if (outLemo5 != other.outLemo5) {
			return false;
		}
		if (outLemo6 != other.outLemo6) {
			return false;
		}
		if (outLemo7 != other.outLemo7) {
			return false;
		}
		if (Double.doubleToLongBits(preceedingTimeDelay) != Double.doubleToLongBits(other.preceedingTimeDelay)) {
			return false;
		}
		if (scansTrig != other.scansTrig) {
			return false;
		}
		if (scansTrigLemo != other.scansTrigLemo) {
			return false;
		}
		if (scansTrigRisingEdge != other.scansTrigRisingEdge) {
			return false;
		}
		if (Double.doubleToLongBits(timePerFrame) != Double.doubleToLongBits(other.timePerFrame)) {
			return false;
		}
		if (Double.doubleToLongBits(timePerScan) != Double.doubleToLongBits(other.timePerScan)) {
			return false;
		}
		if (useTopupChecker != other.useTopupChecker) {
			return false;
		}
		return true;
	}
}
