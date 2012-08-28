/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i13i;




import gda.rcp.views.CompositeFactory;

import java.util.HashMap;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.jface.viewers.ISelection;
import org.eclipse.jface.viewers.ISelectionProvider;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.CTabFolder;
import org.eclipse.swt.custom.CTabItem;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.IWorkbenchPartSite;
import org.springframework.beans.factory.InitializingBean;

import swing2swt.layout.BorderLayout;
import uk.ac.gda.ui.utils.SWTUtils;


/*
 * CompositeFactory to create a Composite used for processing files in a fileset reported by an instance of
 * HighestExistingFileMonitorDataProvider The processing is done by a FileProcessor object
 */
public class IImageModeCompositeFactory implements CompositeFactory, InitializingBean {
	// private static final Logger logger = LoggerFactory.getLogger(LatestFileNameCompositeFactory.class);
	protected IImageMode[] availableModes;

	@Override
	public Composite createComposite(Composite parent, int style, IWorkbenchPartSite iWorkbenchPartSite) {
		final IIMageModeComposite comp = new IIMageModeComposite(parent, style, iWorkbenchPartSite, availableModes);
		comp.createControls();
		return comp;
	}

	public void setAvailableModes(IImageMode[] availableModes) {
		this.availableModes = availableModes;
	}

	@Override
	public void afterPropertiesSet() throws Exception {
		if (availableModes == null) {
			throw new IllegalArgumentException("availableModes == null");
		}
	}

	/*
	 * Ensure plugin containing the icons is set to be the default working folder
	 */
	public static void main(String... args) {

		Display display = new Display();
		Shell shell = new Shell(display);
		shell.setLayout(new BorderLayout());

		final IIMageModeComposite comp = new IIMageModeComposite(shell, SWT.NONE, null, new IImageMode[]{new DummyIImageMode()});
		comp.createControls();
		comp.setLayoutData(BorderLayout.NORTH);
		comp.setVisible(true);
		shell.pack();
		shell.setSize(400, 400);
		SWTUtils.showCenteredShell(shell);
	}

}

class DummyIImageMode implements IImageMode{

	@Override
	public String getName() {
		return "Test";
	}

	@Override
	public Control getTabControl(Composite parent) {
		return null;
	}

	@Override
	public Image getTabImage() {
		return null;
	}

	@Override
	public ISelection getSelection() {
		return null;
	}

	@Override
	public boolean supportsMoveOnClick() {
		return false;
	}

	@Override
	public String getLabel() {
		return "dummy";
	}
	
}

class IIMageModeComposite extends Composite {
//	private static final Logger logger = LoggerFactory.getLogger(IIMageModeComposite.class);
	
	private CTabFolder modeControl;
	protected IImageMode[] availableModes;
	private HashMap<IImageMode, CTabItem> tabs;
	private ImageModeChangeListener imageModeChangeListener;
	private ISelectionProvider selectionProvider;

	private final IWorkbenchPartSite iWorkbenchPartSite;
	
	public IIMageModeComposite(Composite parent, int style, IWorkbenchPartSite iWorkbenchPartSite, IImageMode[] availableModes) {
		super(parent, style);
		this.iWorkbenchPartSite = iWorkbenchPartSite;
		this.availableModes = availableModes;
		selectionProvider = new ModePaneSelectionProvider();
	}	
	
	
	
	void createControls() {
		GridLayoutFactory.fillDefaults().numColumns(1).applyTo(this);
		GridDataFactory.fillDefaults().applyTo(this);		
/*		GridLayout gl = new GridLayout();
		gl.numColumns = 4;
		modeComp.setLayout(gl);
		GridData data3 = new GridData(SWT.FILL, SWT.FILL, true, true);
		data3.horizontalSpan = 4;
		modeComp.setLayoutData(data3);
*/		modeControl = new CTabFolder(this, SWT.TOP | SWT.BORDER);
		modeControl.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				int selectionIndex = modeControl.getSelectionIndex();
				IImageMode mode = availableModes[selectionIndex];
				ImageModeManager.getInstance().setMode(mode);
			}
		});
		GridLayoutFactory.fillDefaults().numColumns(1).applyTo(modeControl);
		GridDataFactory.fillDefaults().applyTo(modeControl);
		
		tabs = new HashMap<IImageMode, CTabItem>();
		for (int i = 0; i < availableModes.length; i++) {
			IImageMode mode = availableModes[i];
			CTabItem cTab = new CTabItem(modeControl, SWT.NONE);
			Image tabImage = mode.getTabImage();
			if (tabImage != null){
				cTab.setImage(tabImage);
			}
			cTab.setText(mode.getLabel());
			cTab.setToolTipText(mode.getName());
			Control control = mode.getTabControl(modeControl);
			cTab.setControl(control);
			tabs.put(mode, cTab);
			
		}
		imageModeChangeListener = new ImageModeChangeListener();
	
		// set initial tab
		final ImageModeManager imageModeManager = ImageModeManager.getInstance();
		imageModeManager.setMode(availableModes[0]);
		imageModeManager.addListener(imageModeChangeListener);
		modeControl.setSelection(0);
		if(iWorkbenchPartSite != null )
			iWorkbenchPartSite.setSelectionProvider(selectionProvider);
		setVisible(true);
		
	}

	private final class ImageModeChangeListener implements IImageModeListener {
		@Override
		public void imageModeChanged(final IImageMode mode) {
			Display display = modeControl.getDisplay();
			if (display.getThread() ==Thread.currentThread()){
				doSwitch(mode);
			} else {
				display.asyncExec(new Runnable() {				
					@Override
					public void run() {
						doSwitch(mode);	
					}
				});
			}
			
		}

		private void doSwitch(IImageMode mode) {
			modeControl.setSelection(tabs.get(mode));
			selectionProvider.setSelection(mode.getSelection());
		}
	}
}
