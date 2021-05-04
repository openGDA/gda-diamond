package uk.ac.gda.beamline.i05.views;

import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.ScrolledComposite;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.ui.part.ViewPart;

import com.swtdesigner.SWTResourceManager;

import gda.factory.Finder;
import uk.ac.diamond.daq.pes.api.IElectronAnalyser;

public class ContinuousModeControllerView extends ViewPart {

	private ContinuousModeControllerComposite continuousModeControllerComposite;

	@Override
	public void createPartControl(Composite parent) {

		final IElectronAnalyser analyserRmiProxy = Finder.listLocalFindablesOfType(IElectronAnalyser.class)
				.stream()
				.findFirst()
				.orElseThrow(() -> new RuntimeException("No analyser was found over RMI"));

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