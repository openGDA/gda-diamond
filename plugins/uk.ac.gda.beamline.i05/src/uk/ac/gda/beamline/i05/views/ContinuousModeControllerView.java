package uk.ac.gda.beamline.i05.views;

import java.util.List;

import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;

import gda.factory.Finder;
import uk.ac.gda.devices.vgscienta.IVGScientaAnalyserRMI;

public class ContinuousModeControllerView extends ViewPart {

	public ContinuousModeControllerView() {
	}

	private ContinuousModeControllerComposite continuousModeControllerComposite;

	@Override
	public void createPartControl(Composite parent) {
		// Should be local as its already imported by Spring
		final List<IVGScientaAnalyserRMI> analyserRmiList = Finder.listLocalFindablesOfType(IVGScientaAnalyserRMI.class);
		if (analyserRmiList.isEmpty()) {
			throw new RuntimeException("No analyser was found over RMI");
		}
		// TODO Might actually want to handle the case where more than on
		final IVGScientaAnalyserRMI analyserRmiProxy = analyserRmiList.get(0);

		continuousModeControllerComposite = new ContinuousModeControllerComposite(parent, analyserRmiProxy);
	}

	@Override
	public void setFocus() {
		continuousModeControllerComposite.setFocus();
	}

}