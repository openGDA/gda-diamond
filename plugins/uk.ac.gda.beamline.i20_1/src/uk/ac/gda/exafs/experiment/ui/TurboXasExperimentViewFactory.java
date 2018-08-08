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

package uk.ac.gda.exafs.experiment.ui;

import java.util.List;
import java.util.Map;

import org.eclipse.ui.part.ViewPart;

import gda.rcp.views.FindableViewFactoryBase;
import gda.rcp.views.ViewUtils;

public class TurboXasExperimentViewFactory extends FindableViewFactoryBase {

		private List<String> motorNames;
		private List<String> detectorNames;
		private String viewLabel;
		private Map<String, String> detectorNamesMap;
		private Map<String, String> defaultPlottedFields;

		public String getViewLabel() {
			return viewLabel;
		}

		public void setViewLabel(String viewLabel) {
			this.viewLabel = viewLabel;
		}

		public List<String> getMotorNames() {
			return motorNames;
		}

		public void setMotorNames(List<String> motorNames) {
			this.motorNames = motorNames;
		}

		public List<String> getDetectorNames() {
			return detectorNames;
		}

		public void setDetectorNames(List<String> detectorNames) {
			this.detectorNames = detectorNames;
		}

		/**
		 * Map containing detector names and corresponding GUI labels; key = GUI label, value = detector object name
		 * @param detectorNamesMap
		 */
		public void setDetectorNameMap(Map<String, String> detectorNamesMap) {
			this.detectorNamesMap = detectorNamesMap;
		}

		public void setDefaultPlottedFields(Map<String, String> defaultPlottedFields) {
			this.defaultPlottedFields = defaultPlottedFields;
		}

		private String[] listToArray(List<String> list) {
			if (list==null) {
				return null;
			}
			String[] listAsArray = new String[list.size()];
			for(int i=0; i<list.size(); i++) {
				listAsArray[i]=list.get(i);
			}
			return listAsArray;
		}

		@Override
		public ViewPart createView() {
			TurboXasExperimentView view = new TurboXasExperimentView();
			view.setMotorNames(listToArray(motorNames));
			view.setDetectorNamesMap(detectorNamesMap);
			view.setDetectorNames(listToArray(detectorNames));
			view.setDefaultPlottedFields(defaultPlottedFields);
			ViewUtils.setViewName(view, viewLabel);
			return view;
		}
}
