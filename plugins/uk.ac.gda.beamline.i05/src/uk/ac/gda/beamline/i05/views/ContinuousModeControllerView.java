package uk.ac.gda.beamline.i05.views;

import java.util.List;

import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;

import com.swtdesigner.SWTResourceManager;

import gda.factory.Finder;
import uk.ac.diamond.daq.pes.api.IElectronAnalyser;

public class ContinuousModeControllerView extends ViewPart {

	public ContinuousModeControllerView() {
	}

	private ContinuousModeControllerComposite continuousModeControllerComposite;

	@Override
	public void createPartControl(Composite parent) {
		// Should be local as its already imported by Spring
		final List<IElectronAnalyser> analyserRmiList = Finder.listLocalFindablesOfType(IElectronAnalyser.class);
		if (analyserRmiList.isEmpty()) {
			throw new RuntimeException("No analyser was found over RMI");
		}
		// TODO Might actually want to handle the case where more than on
		final IElectronAnalyser analyserRmiProxy = analyserRmiList.get(0);

		parent.setBackground(SWTResourceManager.getColor(SWT.COLOR_WHITE));
		ScrolledComposite scroller = new ScrolledComposite(parent, SWT.V_SCROLL);
		scroller.setBackground(SWTResourceManager.getColor(SWT.COLOR_TRANSPARENT));
		continuousModeControllerComposite = new ContinuousModeControllerComposite(scroller, analyserRmiProxy);
		scroller.setContent(continuousModeControllerComposite);
		scroller.setExpandHorizontal(true);
		scroller.setExpandVertical(true);
		scroller.setMinSize(continuousModeControllerComposite.computeSize(SWT.DEFAULT, SWT.DEFAULT));
	}

	@Override
	public void setFocus() {
		continuousModeControllerComposite.setFocus();
	}

}