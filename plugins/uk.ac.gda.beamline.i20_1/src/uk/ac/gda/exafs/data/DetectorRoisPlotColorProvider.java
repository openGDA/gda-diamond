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

import java.awt.Color;

import uk.ac.gda.client.liveplot.IPlotLineColorService;

public class DetectorRoisPlotColorProvider implements IPlotLineColorService {
	private final Color[] colors = {Color.RED, Color.BLUE, Color.GREEN, Color.BLACK, Color.ORANGE, Color.CYAN};

	private DetectorRoisPlotColorProvider() {}

	@Override
	public Color getColorForPlotLine(String yLabel) {
		// TODO This is a quick fix!
		if (yLabel.equals("Total")) {
			return Color.MAGENTA;
		}
		else if (yLabel.equals(ClientConfig.ScannableSetup.SLIT_3_HORIZONAL_GAP.getScannableName())) {
			return Color.PINK;
		}
		else {
			if (yLabel.matches("ROI_\\d")) {
				try {
					int index = Integer.parseInt(yLabel.split("_")[1]);
					if (index < colors.length) {
						return colors[index -1];
					}
				} catch (Exception e) {
					return null;
				}
			}
		}
		return null;
	}
}
