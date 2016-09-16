package uk.ac.gda.beamline.i05.views;

import java.util.List;

import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;

import gda.device.Device;
import gda.factory.Finder;
import gda.observable.IObserver;
import uk.ac.gda.devices.vgscienta.IVGScientaAnalyserRMI;

public class ContinuousModeControllerView extends ViewPart implements IObserver {

	private Device analyser;
	private Device psu;

	public ContinuousModeControllerView() {
	}

	private ContinuousModeControllerComposite continuousModeControllerComposite;

	@Override
	public void createPartControl(Composite parent) {
		List<IVGScientaAnalyserRMI> analyserRmiList = Finder.getInstance().listFindablesOfType(IVGScientaAnalyserRMI.class);
		if (analyserRmiList.isEmpty()) {
			throw new RuntimeException("No analyser was found over RMI");
		}
		// TODO Might actually want to handle the case where more than on
		IVGScientaAnalyserRMI analyserRMI = analyserRmiList.get(0);
		analyser = (Device) Finder.getInstance().find("analyser");
		if (analyser != null) {
			analyser.addIObserver(this);
		}
		psu = (Device) Finder.getInstance().find("psu_mode");
		if (psu != null) {
			psu.addIObserver(this);
		}
		continuousModeControllerComposite = new ContinuousModeControllerComposite(parent, analyserRMI);
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