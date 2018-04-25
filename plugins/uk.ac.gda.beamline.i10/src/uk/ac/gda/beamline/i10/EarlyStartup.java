/*-
 * Copyright © 2018 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i10;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;

import org.eclipse.core.runtime.preferences.DefaultScope;
import org.eclipse.core.runtime.preferences.InstanceScope;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IEditorInput;
import org.eclipse.ui.IEditorPart;
import org.eclipse.ui.IEditorReference;
import org.eclipse.ui.IPartListener;
import org.eclipse.ui.IPartService;
import org.eclipse.ui.IPerspectiveDescriptor;
import org.eclipse.ui.IStartup;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.IWorkbenchPart;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PerspectiveAdapter;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.WorkbenchException;
import org.eclipse.ui.part.EditorPart;
import org.osgi.service.prefs.BackingStoreException;
import org.osgi.service.prefs.Preferences;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EarlyStartup implements IStartup {

	private static final String WORKSPACE_INITIALISED_PREF = "WORKSPACE_INITIALISED";

	private static final Logger logger = LoggerFactory.getLogger(EarlyStartup.class);

	private HashMap<String, ArrayList<IEditorReference>> perspectiveEditors = new HashMap<String, ArrayList<IEditorReference>>();
	private HashMap<String, IEditorReference> lastActiveEditors = new HashMap<String, IEditorReference>();

	@Override
	public void earlyStartup() {

		Display.getDefault().asyncExec(new Runnable() {

			@Override
			public void run() {

				setupPartListener();
				final IWorkbenchWindow workbenchWindow = PlatformUI.getWorkbench().getActiveWorkbenchWindow();
				if (workbenchWindow != null) {
					workbenchWindow.addPerspectiveListener(new PerspectiveAdapter() {

						@Override
						public void perspectiveActivated(IWorkbenchPage page, IPerspectiveDescriptor perspective) {
							super.perspectiveActivated(page, perspective);
							// refresh views in the perspective or execute command handler in views in this perspective

							/*----------------------------------------------
							 * part to hide all open editors
							 */
							// Hide all the editors
							IEditorReference[] editors = page.getEditorReferences();
							for (int i = 0; i < editors.length; i++) {
								page.hideEditor(editors[i]);
							}

							// Show the editors associated with this perspective
							ArrayList<IEditorReference> editorRefs = perspectiveEditors.get(perspective.getId());
							if (editorRefs != null) {
								for (Iterator<IEditorReference> it = editorRefs.iterator(); it.hasNext();) {
									IEditorReference editorInput = it.next();
									page.showEditor(editorInput);
								}

								// Send the last active editor to the top
								IEditorReference lastActiveRef = lastActiveEditors.get(perspective.getId());
								if (lastActiveRef != null)
									page.bringToTop(lastActiveRef.getPart(true));
							}
							/*-----Part to hide all editor**/
						}

						@Override
						public void perspectiveDeactivated(IWorkbenchPage page, IPerspectiveDescriptor perspective) {
							// updateTitle();
							IEditorPart activeEditor = page.getActiveEditor();
							if (activeEditor != null) {

								// Find the editor reference that relates to this editor input
								IEditorReference[] editorRefs = page.findEditors(activeEditor.getEditorInput(), null,
										IWorkbenchPage.MATCH_INPUT);
								if (editorRefs.length > 0) {
									lastActiveEditors.put(perspective.getId(), editorRefs[0]);
								}
							}
						}
					});

					initialiseWorkspace();
				}
			}
		});
	}

	private void setupPartListener() {
		final IWorkbenchWindow workbenchWindow = PlatformUI.getWorkbench().getActiveWorkbenchWindow();
		IPartService service = workbenchWindow.getService(IPartService.class);
		service.addPartListener(new IPartListener() {

			@Override
			public void partActivated(IWorkbenchPart part) {
			}

			@Override
			public void partBroughtToTop(IWorkbenchPart part) {
			}

			@Override
			public void partClosed(IWorkbenchPart part) {
			}

			@Override
			public void partDeactivated(IWorkbenchPart part) {
			}

			@Override
			public void partOpened(IWorkbenchPart part) {
				if (part instanceof EditorPart) {
					EditorPart editor = (EditorPart) part;
					IWorkbenchPage page = part.getSite().getPage();
					IEditorInput editorInput = editor.getEditorInput();
					IPerspectiveDescriptor activePerspective = page.getPerspective();

					ArrayList<IEditorReference> editors = perspectiveEditors.get(activePerspective.getId());
					if (editors == null)
						editors = new ArrayList<IEditorReference>();

					// Find the editor reference that relates to this editor input
					IEditorReference[] editorRefs = page.findEditors(editorInput, null, IWorkbenchPage.MATCH_INPUT);

					if (editorRefs.length > 0) {
						editors.add(editorRefs[0]);
						perspectiveEditors.put(activePerspective.getId(), editors);
					}
				}
			}
		});
	}

	/**
	 * Check the WORKSPACE_INITIALISED preference to see if the workspace is new or has been reset. If so, initialise
	 * the perspectives and set the WORKSPACE_INITIALISED preference to ensure we only do this once.
	 */
	private void initialiseWorkspace() {
		Preferences prefs = InstanceScope.INSTANCE.getNode(Activator.PLUGIN_ID);
		if (!prefs.getBoolean(WORKSPACE_INITIALISED_PREF, false)) {
			copyPerspectivePreferences();
			initialiseDefaultPerspectives();
			prefs.putBoolean(WORKSPACE_INITIALISED_PREF, true);
		}
	}

	/**
	 * Copy perspective preferences from the Default to the Instance scope. (This fixes ticket I18-62.) The problem
	 * seems to be that perspective customization preferences loaded as XML strings from the plugin_customization.ini
	 * file do not automatically trigger the ImportExportPespectiveHandler at application startup. (This is presumably
	 * because they are loaded before the handler is active, or because loading default preference values does not
	 * cause PreferenceChangeEvents to be fired.) Copying the values to the Instance scope at this point seems to
	 * trigger the events correctly and the perspective customization is then applied.
	 */
	private void copyPerspectivePreferences() {
		Preferences defaultPrefs = DefaultScope.INSTANCE.getNode("org.eclipse.ui.workbench");
		Preferences instancePrefs = InstanceScope.INSTANCE.getNode("org.eclipse.ui.workbench");
		try {
			for (String key : defaultPrefs.keys()) {
				if (key.endsWith("_persp") || key.endsWith("_e4persp")) {
					instancePrefs.put(key, defaultPrefs.get(key, null));
				}
			}
		} catch (BackingStoreException ex) {
			logger.error("Error getting default preferences", ex);
		}
	}

	/**
	 * Initialise the default perspectives. This shouldn't be necessary but the PERSPECTIVE_BAR_EXTRAS preference seems
	 * to be ignored in Eclipse 4 (see https://jira.diamond.ac.uk/browse/DAQ-694), so we do the work ourselves instead.
	 */
	private void initialiseDefaultPerspectives() {
		final IWorkbenchWindow workbenchWindow = PlatformUI.getWorkbench().getActiveWorkbenchWindow();
		String perspectiveId = null;
		try {
			Preferences instanceEclipseUiPrefs = DefaultScope.INSTANCE.getNode("org.eclipse.ui");
			String perspectiveList = instanceEclipseUiPrefs.get("PERSPECTIVE_BAR_EXTRAS", "");
			for (String perspective : perspectiveList.split(",")) {
				perspectiveId = perspective.trim();
				if (perspectiveId.length() > 0) {
					workbenchWindow.getWorkbench().showPerspective(perspectiveId, workbenchWindow);
				}
			}
			perspectiveId = instanceEclipseUiPrefs.get("defaultPerspectiveId", "");
			workbenchWindow.getWorkbench().showPerspective(perspectiveId, workbenchWindow);
			Display.getDefault().asyncExec(new Runnable() {
				@Override
				public void run() {
					workbenchWindow.getActivePage().resetPerspective();
				}
			});

		} catch (WorkbenchException ex) {
			logger.warn("Could not open perspective {}", perspectiveId, ex);
		}
	}

}
