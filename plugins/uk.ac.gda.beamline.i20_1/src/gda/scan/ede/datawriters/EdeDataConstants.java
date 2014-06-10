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

package gda.scan.ede.datawriters;

import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset;
import uk.ac.gda.beamline.i20_1.utils.DataHelper;
import uk.ac.gda.exafs.calibration.data.CalibrationDetails;

public class EdeDataConstants {

	// Column names
	public static final String TIMINGGROUP_COLUMN_NAME = "group";
	public static final String FRAME_COLUMN_NAME = "frame";
	public static final String STRIP_COLUMN_NAME = "strip";
	public static final String ENERGY_COLUMN_NAME = "energy";
	public static final String I0_CORR_COLUMN_NAME = "i0_corr";
	public static final String I0_FINAL_CORR_COLUMN_NAME = "i0_final_corr";
	public static final String IT_CORR_COLUMN_NAME = "it_corr";
	public static final String I0_RAW_COLUMN_NAME = "i0_raw";
	public static final String IT_RAW_COLUMN_NAME = "it_raw";
	public static final String I0_DARK_COLUMN_NAME = "i0_dark";
	public static final String IT_DARK_COLUMN_NAME = "it_dark";
	public static final String IREF_DATA_NAME = "iref";
	public static final String IREF_DARK_DATA_NAME = "iref_dark";
	public static final String I0_IREF_DATA_NAME = "i0_iref";
	public static final String IREF_RAW_DATA_NAME = "iref_raw";
	public static final String DATA_COLUMN_NAME = "data";
	public static final String DATA_RAW_COLUMN_NAME = "data_raw";
	public static final String TIME_COLUMN_NAME = "time";
	public static final String CYCLE_COLUMN_NAME = "cycle";
	public static final String IT_COLUMN_NAME = "it";
	public static final String I0_COLUMN_NAME = "i0";
	public static final String BEAM_IN_OUT_COLUMN_NAME = "light";

	public static final String LN_I0_IT_COLUMN_NAME = "lnI0It";
	public static final String LN_I0_IT__FINAL_I0_COLUMN_NAME = "lnI0It_finalI0";
	public static final String LN_I0_IT_AVG_I0S_COLUMN_NAME = "lnI0It_avgI0s";
	public static final String IREF_FINAL_DATA_NAME = "iref_final";
	public static final String LN_I0_IREF_COLUMN_NAME = "lnI0IRef";
	public static final String LN_I0_IREF_FINAL_COLUMN_NAME = "lnI0IRef_final";
	public static final String META_DATA_NAME = "metaData";
	public static final String SCANNABLES_CONFIG_DATA_NAME = "config";

	public static final String ASCII_FILE_EXTENSION = "dat";

	public static class ItMetadata {
		private final TimingGroupMetadata[] timingGroups;
		private final RangeData[] avgSpectra;
		private final int[] excludedCycles;
		private CalibrationDetails calibrationDetails;

		public ItMetadata(TimingGroupMetadata[] timingGroups, RangeData[] avgSpectra, int[] excludedCycles) {
			this.timingGroups = timingGroups;
			this.avgSpectra = avgSpectra;
			this.excludedCycles = excludedCycles;
		}
		public TimingGroupMetadata[] getTimingGroups() {
			return timingGroups;
		}
		public RangeData[] getAvgSpectra() {
			return avgSpectra;
		}
		public int[] getExcludedCycles() {
			return excludedCycles;
		}
		public CalibrationDetails getCalibrationDetails() {
			return calibrationDetails;
		}
		public void setCalibrationDetails(CalibrationDetails calibrationDetails) {
			this.calibrationDetails = calibrationDetails;
		}
	}

	public static class TimingGroupMetadata {
		private final int index;
		private final int noOfFrames;
		private final double accumulationTime;
		private final double timePerSpectrum;
		private final double preceedingTimeDelay;
		private final int noOfAccumulations;

		public TimingGroupMetadata(int index, int noOfFrames, double accumulationTime, double timePerSpectrum,
				double preceedingTimeDelay, int noOfAccumulations) {
			super();
			this.index = index;
			this.noOfFrames = noOfFrames;
			this.accumulationTime = accumulationTime;
			this.timePerSpectrum = timePerSpectrum;
			this.preceedingTimeDelay = preceedingTimeDelay;
			this.noOfAccumulations = noOfAccumulations;
		}

		public int getIndex() {
			return index;
		}

		// FIXME Change to spectrum
		public int getNoOfFrames() {
			return noOfFrames;
		}

		public double getAccumulationTime() {
			return accumulationTime;
		}

		public double getTimePerSpectrum() {
			return timePerSpectrum;
		}

		public double getPreceedingTimeDelay() {
			return preceedingTimeDelay;
		}

		public int getNoOfAccumulations() {
			return noOfAccumulations;
		}

		public static DoubleDataset toDataset(TimingGroupMetadata[] metaData) {
			DoubleDataset metaDataset = new DoubleDataset(new int[]{metaData.length, 6});
			for (int i = 0; i < metaData.length; i++) {
				TimingGroupMetadata metaDataItem = metaData[i];
				metaDataset.set(metaDataItem.getIndex(), i, 0);
				metaDataset.set(metaDataItem.getNoOfFrames(), i, 1);
				metaDataset.set(metaDataItem.getAccumulationTime(), i, 2);
				metaDataset.set(metaDataItem.getTimePerSpectrum(), i, 3);
				metaDataset.set(metaDataItem.getPreceedingTimeDelay(), i, 4);
				metaDataset.set(metaDataItem.getNoOfAccumulations(), i, 5);
			}
			return metaDataset;
		}

		public static String toMetadataString(DoubleDataset data) {
			StringBuilder metadataStr = new StringBuilder();
			int noOfGroups = data.getShape()[0];
			for (int i = 0; i < noOfGroups; i++) {
				metadataStr.append(String.format("Group: %d\t", (int) data.get(i, 0)));
				metadataStr.append(String.format("Number of spectra: %d\t", (int) data.get(i, 1)));
				metadataStr.append(String.format("Accumulation time: %.4fs\t", data.get(i, 2)));
				metadataStr.append(String.format("Time per spectrum: %.4fs\t", data.get(i, 3)));
				metadataStr.append(String.format("Preceding delay: %.4f\t", data.get(i, 4)));
				metadataStr.append(String.format("Number of accumulations: %d", (int) data.get(i, 5)));
				metadataStr.append("\n");
			}
			return DataHelper.removeLastChar(metadataStr).toString();
		}

		public static TimingGroupMetadata[] toTimingGroupMetaData(DoubleDataset data) {
			TimingGroupMetadata[] groups =  new TimingGroupMetadata[data.getShape()[0]];
			for (int i = 0; i < groups.length; i++) {
				groups[i] = new TimingGroupMetadata((int) data.get(i, 0), (int) data.get(i, 1), data.get(i, 2), data.get(i, 3), data.get(i, 4), (int) data.get(i, 5));
			}
			return groups;
		}

		public static int getNoOfSpectra(int groupIndex, DoubleDataset metadata) {
			return metadata.getInt(groupIndex, 1);
		}

		public static double getTimePerSpectrum(int groupIndex, DoubleDataset metadata) {
			return metadata.get(groupIndex, 2);
		}
	}

	public static class RangeData {
		private final int startIndex;
		private final int endIndex;

		public RangeData(int startIndex, int endIndex) {
			this.startIndex = startIndex;
			this.endIndex = endIndex;
		}

		public int getStartIndex() {
			return startIndex;
		}

		public int getEndIndex() {
			return endIndex;
		}

		@Override
		public String toString() {
			return startIndex + ":" + endIndex;
		}

		public static RangeData[] toRangeDataList(String commaSepString) {
			String[] rangesStr = commaSepString.split(",");
			RangeData[] rangeData = new RangeData[rangesStr.length];
			for (int i = 0; i < rangesStr.length; i++) {
				String[] rangeStartEnd = rangesStr[i].split(":");
				rangeData[i] = new RangeData(Integer.parseInt(rangeStartEnd[0]), Integer.parseInt(rangeStartEnd[1]));
			}
			return rangeData;
		}
	}

}
