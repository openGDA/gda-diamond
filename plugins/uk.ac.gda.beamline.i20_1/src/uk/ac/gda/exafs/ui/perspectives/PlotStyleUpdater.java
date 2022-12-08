/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.ui.perspectives;

import java.util.Arrays;
import java.util.List;

import org.eclipse.dawnsci.plotting.api.jreality.impl.Plot1DStyles;
import org.eclipse.jface.preference.IPreferenceStore;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.jython.IJythonServerStatusObserver;
import gda.rcp.GDAClientActivator;
import gda.scan.Scan.ScanStatus;
import gda.scan.ScanEvent;
import gda.scan.ScanInformation;
import uk.ac.gda.preferences.PreferenceConstants;

public class PlotStyleUpdater implements IJythonServerStatusObserver {
	private static Logger logger = LoggerFactory.getLogger(PlotStyleUpdater.class);

	private final List<String> stepScanEdeDetectors = Arrays.asList("ssfrelon", "ssxh");
	private List<Plot1DStyles> plotStyleToUse = Arrays.asList(Plot1DStyles.SOLID, Plot1DStyles.DASHED, Plot1DStyles.DASHED_POINT, Plot1DStyles.SOLID_POINT);
	private String lineStyleStringFromPreferenceStore;
	private int numEdePlots;

	IPreferenceStore preferenceStore;

	public PlotStyleUpdater() {
		numEdePlots = 0;

		preferenceStore = GDAClientActivator.getDefault().getPreferenceStore();
		lineStyleStringFromPreferenceStore = preferenceStore.getString(PreferenceConstants.GDA_CLIENT_PLOT_LINESTYLES);
	}

	private boolean scanIsRunning;

	@Override
	public void update(Object source, Object changeCode) {
		if (changeCode instanceof ScanEvent) {
			ScanEvent scanEvent = (ScanEvent) changeCode;
			ScanStatus scanStatus = scanEvent.getLatestStatus();
			logger.debug("Scan status = {}", scanStatus.toString());
			switch(scanStatus) {
			case COMPLETED_AFTER_FAILURE:
			case COMPLETED_AFTER_STOP:
			case COMPLETED_EARLY:
			case NOTSTARTED:
			case FINISHING_EARLY:
			case TIDYING_UP_AFTER_FAILURE:
			case TIDYING_UP_AFTER_STOP:
			case COMPLETED_OKAY:
				setDefaultPlotStyle();
				scanIsRunning=false;
				break;
			case PAUSED:
			case RUNNING:
				if(!scanIsRunning) {
					updatePlotStyle(scanEvent);
				}
				scanIsRunning=true;
				break;
			default:
				setDefaultPlotStyle();
				scanIsRunning=false;
			}
		}
	}

	private void setDefaultPlotStyle() {
		GDAClientActivator.getDefault().getPreferenceStore().firePropertyChangeEvent(PreferenceConstants.GDA_CLIENT_PLOT_LINESTYLES, null, lineStyleStringFromPreferenceStore);
	}

	private boolean scanHasEdeDetectors(ScanEvent scanEvent) {
		ScanInformation scanInfo = scanEvent.getLatestInformation();
		String[] detNames = scanInfo.getDetectorNames();
		boolean stepScanHasEdeDetector=false;
		for(String detName : detNames) {
			if (stepScanEdeDetectors.contains(detName)) {
				stepScanHasEdeDetector=true;
			}
		}
		return stepScanHasEdeDetector;
	}

	private void updatePlotStyle(ScanEvent scanEvent) {
		boolean scanHasEdeDetectors = scanHasEdeDetectors(scanEvent);
		if (scanHasEdeDetectors) {
			int numPlotStyles = plotStyleToUse.size();
			Plot1DStyles lineStyleEnum = plotStyleToUse.get(numEdePlots%numPlotStyles);
			String lineStyleString = ""+lineStyleEnum.ordinal();

			logger.debug("Update plot style : num ede plots = {}, style = {}", numEdePlots, lineStyleString);
			GDAClientActivator.getDefault().getPreferenceStore().firePropertyChangeEvent(PreferenceConstants.GDA_CLIENT_PLOT_LINESTYLES, null, lineStyleString);
			numEdePlots++;
		}
	}
}

