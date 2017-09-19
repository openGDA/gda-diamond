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

import org.eclipse.ui.part.ViewPart;

import gda.rcp.views.FindableViewFactoryBase;
import gda.rcp.views.ViewUtils;

public class TurboXasExperimentViewFactory extends FindableViewFactoryBase {

		private List<String> motorNames;
		private List<String> detectorNames;
		private String viewLabel;

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

		private String[] listToArray(List<String> list) {
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
			view.setDetectorNames(listToArray(detectorNames));
			ViewUtils.setViewName(view, viewLabel);
			return view;
		}
}
