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

package uk.ac.gda.beamline.b18;

import org.eclipse.ui.IFolderLayout;
import org.eclipse.ui.IPageLayout;
import org.eclipse.ui.IPerspectiveFactory;

import gda.rcp.views.JythonTerminalView;
import uk.ac.gda.client.live.stream.view.LiveStreamView;
import uk.ac.gda.client.livecontrol.LiveControlsView;

public class LiveViewPerspective implements IPerspectiveFactory {

	private static final String LIVE_STREAMS = "liveStreams";
	private static final String LIVE_STREAMS2 = "liveStreams2";
	private static final String LIVE_CONTROLS = "liveControls";

	@Override
	public void createInitialLayout(IPageLayout layout) {
		String editorArea = layout.getEditorArea();
		layout.setEditorAreaVisible(false);

		IFolderLayout left = layout.createFolder(LIVE_STREAMS, IPageLayout.LEFT, 0.3f, editorArea); //$NON-NLS-1$
		left.addView(LiveStreamView.ID+":eh_front_cam_config");
		layout.addView(LiveStreamView.ID+":sample_front_cam_config", IPageLayout.BOTTOM, 0.5f, LIVE_STREAMS);

		IFolderLayout rright = layout.createFolder(LIVE_STREAMS2, IPageLayout.RIGHT, 0.4f, editorArea); //$NON-NLS-1$
		rright.addView(LiveControlsView.ID);
		layout.addView(JythonTerminalView.ID, IPageLayout.BOTTOM, 0.7f,LIVE_STREAMS2);

		IFolderLayout right = layout.createFolder(LIVE_CONTROLS, IPageLayout.RIGHT, 0.3f, editorArea); //$NON-NLS-1$
		right.addView(LiveStreamView.ID+":eh_back_cam_config");
		layout.addView(LiveStreamView.ID+":sample_back_cam_config", IPageLayout.BOTTOM, 0.5f, LIVE_CONTROLS);
	}
}
