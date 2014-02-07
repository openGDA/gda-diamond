package uk.ac.gda.beamline.i22.actions;

import java.util.Properties;

import org.eclipse.ui.IPerspectiveDescriptor;
import org.eclipse.ui.IPerspectiveRegistry;
import org.eclipse.ui.IWorkbench;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.WorkbenchException;
import org.eclipse.ui.intro.IIntroPart;
import org.eclipse.ui.intro.IIntroSite;
import org.eclipse.ui.intro.config.IIntroAction;

public class SwitchToBioSAXSSetupPerspectiveAction implements IIntroAction {

	public SwitchToBioSAXSSetupPerspectiveAction() {
		IWorkbench workbench = PlatformUI.getWorkbench();
		IWorkbenchWindow window = workbench.getActiveWorkbenchWindow();

		// open the BioSAXS setup perspective
		try {
			workbench.showPerspective("uk.ac.gda.devices.bssc.biosaxsresultperspective", window);
			workbench.showPerspective("uk.ac.gda.devices.bssc.biosaxsprogressperspective", window);
			workbench.showPerspective("uk.ac.gda.devices.bssc.biosaxssetupperspective", window);

			IPerspectiveRegistry iPerspectiveRegistry = PlatformUI.getWorkbench().getPerspectiveRegistry();
			
			for (IPerspectiveDescriptor descriptor : iPerspectiveRegistry.getPerspectives())
			{
				System.out.println("descriptor id : " + descriptor.getId());
				System.out.println("descriptor label : " + descriptor.getLabel());
			}
			iPerspectiveRegistry.setDefaultPerspective("uk.ac.gda.devices.bssc.biosaxssetupperspective");
			IPerspectiveDescriptor perspectiveDescriptor = iPerspectiveRegistry.findPerspectiveWithLabel("Scripts");

			try {
				iPerspectiveRegistry.deletePerspective(perspectiveDescriptor);
			} catch (Exception e) {
				System.out.println("=====DELETED=====");
			}

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