package uk.ac.diamond.daq.beamline.i06_2;

import org.dawnsci.plotting.views.ToolPageView;
import org.eclipse.swt.widgets.Display;
import org.eclipse.ui.IStartup;
import org.eclipse.ui.IWorkbenchPage;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EarlyStartup implements IStartup {

	private static final Logger logger = LoggerFactory.getLogger(EarlyStartup.class);

	@Override
	public void earlyStartup() {

		Display.getDefault().asyncExec(new Runnable() {

			@Override
			public void run() {
				try {
					// make sure 'Region editor' view Title is shown at start without making the view either in focus or visible
					PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView(ToolPageView.FIXED_VIEW_ID, "org.dawb.workbench.plotting.tools.region.editor",IWorkbenchPage.VIEW_CREATE);
					// ensure the Medipix Stream View has focus so the 'Region Editor' above is linked to this image

					PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().showView("uk.ac.gda.beamline.i06.medipix.live.stream.view.LiveStreamViewWithHistogram","medipix#EPICS_ARRAY",IWorkbenchPage.VIEW_ACTIVATE);

					//make the dynamic toolbar items visible, not just inside drop-down menu.
					PlatformUI.getWorkbench().getActiveWorkbenchWindow().getActivePage().resetPerspective();
				} catch (PartInitException e) {
					logger.warn("showView calls failed in {}", getClass().getName());
				}
			}
		});
	}

}
