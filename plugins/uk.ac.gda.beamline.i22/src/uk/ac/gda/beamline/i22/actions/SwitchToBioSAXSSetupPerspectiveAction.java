package uk.ac.gda.beamline.i22.actions;

import java.util.Properties;

import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.WorkbenchException;
import org.eclipse.ui.intro.IIntroPart;
import org.eclipse.ui.intro.IIntroSite;
import org.eclipse.ui.intro.config.IIntroAction;

public class SwitchToBioSAXSSetupPerspectiveAction implements IIntroAction {

	public SwitchToBioSAXSSetupPerspectiveAction() {
		System.out.println("SwitchPerspective");

		IWorkbench workbench = PlatformUI.getWorkbench();
		IWorkbenchWindow window = workbench.getActiveWorkbenchWindow();

		// open the BioSAXS setup perspective
		try {
			workbench.showPerspective("uk.ac.gda.devices.bssc.biosaxsresultperspective", window);
			workbench.showPerspective("uk.ac.gda.devices.bssc.biosaxsprogressperspective", window);
			workbench.showPerspective("uk.ac.gda.devices.bssc.biosaxssetupperspective", window);
		} catch (WorkbenchException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	@Override
	public void run(IIntroSite site, Properties params) {
		final IIntroPart introPart = PlatformUI.getWorkbench().getIntroManager().getIntro();
		PlatformUI.getWorkbench().getIntroManager().closeIntro(introPart);
	}
}