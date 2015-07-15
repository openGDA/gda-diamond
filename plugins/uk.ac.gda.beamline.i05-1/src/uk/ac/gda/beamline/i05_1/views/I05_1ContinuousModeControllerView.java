package uk.ac.gda.beamline.i05_1.views;

import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;

import gda.device.Device;
import gda.factory.Finder;
import gda.observable.IObserver;
import uk.ac.gda.devices.vgscienta.AnalyserCapabilties;

public class I05_1ContinuousModeControllerView extends ViewPart implements IObserver {

	private Device analyser;
	private Device psu;
	private AnalyserCapabilties capabilities;

	public I05_1ContinuousModeControllerView() {
	}

	private I05_1ContinuousModeControllerComposite continuousModeControllerComposite;

	@Override
	public void createPartControl(Composite parent) {
		capabilities = (AnalyserCapabilties) Finder.getInstance().listAllLocalObjects(AnalyserCapabilties.class.getCanonicalName()).get(0);
		analyser = (Device) Finder.getInstance().find("analyser");
		if (analyser != null) {
			analyser.addIObserver(this);
		}
		psu = (Device) Finder.getInstance().find("psu_mode");
		if (psu != null) {
			psu.addIObserver(this);
		}
		continuousModeControllerComposite = new I05_1ContinuousModeControllerComposite(parent, capabilities);
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