/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i20;

import gda.configuration.properties.LocalProperties;
import gda.jython.authenticator.UserAuthentication;
import gda.jython.authoriser.AuthoriserProvider;

import org.csstudio.sds.ui.runmode.RunModeService;
import org.eclipse.core.runtime.Path;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.exafs.ui.data.ScanObjectManager;

public abstract class SynopticControl {
	
	private static final Logger logger = LoggerFactory.getLogger(SynopticControl.class);
			
	public static final String STAFF_AND_XES = "gda.client.i20.synopticpath.staff_and_xes";
	public static final String STAFF_AND_XAS = "gda.client.i20.synopticpath.staff_and_xas";
	public static final String USER_AND_XES = "gda.client.i20.synopticpath.user_and_xes";
	public static final String USER_AND_XAS = "gda.client.i20.synopticpath.user_and_xas";
	
	private static String lastSynopticOpened = "";

	public static void showSynoptic() {
		// directly use the supplied service from SDS
		PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
			@Override
			public void run() {
//				Path sdsDisplay = new Path("/screens/synoptic.css-sds");
				String path = getSynopticPath();
				lastSynopticOpened = path;
				Path sdsDisplay = new Path(path);
				RunModeService.getInstance().openDisplayShellInRunMode(sdsDisplay);
			}
		});
	}
	
	public static void switchSynoptic() {
		// directly use the supplied service from SDS
		PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {
			@Override
			public void run() {
				String path = getSynopticPath();
				if (!path.equals(lastSynopticOpened)) {
					Path oldSdsDisplay = new Path(lastSynopticOpened);
					RunModeService.getInstance().closeDisplayShellInRunMode(oldSdsDisplay);
					Path sdsDisplay = new Path(path);
					RunModeService.getInstance().openDisplayShellInRunMode(sdsDisplay);
					lastSynopticOpened = path;
				}
			}
		});
	}
	
	

	public static String getSynopticPath() {
		try {
			// find our permission level
			String user = UserAuthentication.getUsername();
			boolean isStaff = AuthoriserProvider.getAuthoriser().isLocalStaff(user);

			// find out XES / XAS mode
			boolean isXES = ScanObjectManager.isXESOnlyMode();

			if (isStaff && isXES) {
				return LocalProperties.get(STAFF_AND_XES);
			} else if (isStaff && !isXES) {
				return LocalProperties.get(STAFF_AND_XAS);
			} else if (!isStaff && isXES) {
				return LocalProperties.get(USER_AND_XES);
			}
			return LocalProperties.get(USER_AND_XAS);
		} catch (ClassNotFoundException e) {
			logger.error("Exception trying to identify if user is staff", e);
			return LocalProperties.get(STAFF_AND_XAS);
		}
	}
}
