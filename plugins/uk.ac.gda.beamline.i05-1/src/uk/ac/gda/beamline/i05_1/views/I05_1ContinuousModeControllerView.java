package uk.ac.gda.beamline.i05_1.views;

import java.util.List;

import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;

import gda.device.Device;
import gda.factory.Finder;
import gda.observable.IObserver;
import uk.ac.gda.devices.vgscienta.IVGScientaAnalyserRMI;

public class I05_1ContinuousModeControllerView extends ViewPart implements IObserver {

	private Device analyser;
	private Device psu;

	public I05_1ContinuousModeControllerView() {
	}

	private I05_1ContinuousModeControllerComposite continuousModeControllerComposite;

	@Override
	public void createPartControl(Composite parent) {
		List<IVGScientaAnalyserRMI> analyserRmiList = Finder.listFindablesOfType(IVGScientaAnalyserRMI.class);
		if (analyserRmiList.isEmpty()) {
			throw new RuntimeException("No analyser was found over RMI");
		}
		// TODO Might actually want to handle the case where more than one analyser
		IVGScientaAnalyserRMI analyserRMI = analyserRmiList.get(0);
		analyserRMI.addIObserver(this);

		psu = (Device) Finder.find("psu_mode");
		if (psu != null) {
			psu.addIObserver(this);
		}
		continuousModeControllerComposite = new I05_1ContinuousModeControllerComposite(parent, analyserRMI);
	}


	@Override
	public void setFocus() {
	}

	@Override
	public void update(Object source, Object arg) {
		if (continuousModeControllerComposite.getStartButton().isDisposed()) {
			analyser.deleteIObserver(this);
			return;
		}
		continuousModeControllerComposite.update(arg);
	}
}