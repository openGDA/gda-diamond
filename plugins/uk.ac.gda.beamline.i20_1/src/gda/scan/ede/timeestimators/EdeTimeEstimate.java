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

package gda.scan.ede.timeestimators;

/**
 * Classes which will estimate how long experiments will take to help plan the experiment with respect to top-ups.
 */
public interface EdeTimeEstimate {

	/**
	 * An estimate of the total actual time for running the experiment, to include overheads such as moving motors,
	 * programming the TFG and writing the derived ascii files.
	 * 
	 * @return - time, in seconds
	 */
	Double getTotalDuration();

	/**
	 * An estimate of the total time to run the central part of the scan where the It data is collected. This includes
	 * programmed delays but does not account for the time to wait for external hardware to send signals to continue
	 * data collection.
	 * 
	 * @return - time, in seconds
	 */
	Double getItDuration();

	/**
	 * An estimate of the time to perform the data collection before, or after, the main It data collection in the EDE
	 * scans.
	 * <p>
	 * So this includes dark, It and Iref data collection plus overheads of moving motors etc. It does not take into
	 * account any external sample environment overhead.
	 * <p>
	 * This will be an overestimation of the final data collection after the It's as darks are only collected at the
	 * start of an experiment.
	 * 
	 * @return - time, in seconds
	 */
	Double getBookendsDuration();

}
