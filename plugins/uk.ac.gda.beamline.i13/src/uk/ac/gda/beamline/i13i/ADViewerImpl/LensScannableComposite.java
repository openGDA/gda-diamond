/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i13i.ADViewerImpl;

import gda.device.DeviceException;
import gda.device.EnumPositioner;
import gda.jython.InterfaceProvider;
import gda.observable.IObserver;

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.MessageBox;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import uk.ac.gda.common.rcp.util.GridUtils;

public class LensScannableComposite extends Composite {
	static final Logger logger = LoggerFactory.getLogger(LensScannableComposite.class);
	private EnumPositioner lensScannable;
	private IObserver lensObserver;
	private Group group;
	private Combo pcom;

	public LensScannableComposite(Composite parent, int style) {
		super(parent, style);
		setLayout(new GridLayout(1, false));

		group = new Group(this, SWT.NONE);
		group.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, true, false, 1, 1));
		GridDataFactory.fillDefaults().applyTo(group);
		group.setText("Lens");
		GridLayout gl_group = new GridLayout(1, false);
		gl_group.marginBottom = 1;
		gl_group.marginWidth = 1;
		group.setLayout(gl_group);
		
		
		pcom = new Combo(group, SWT.SINGLE | SWT.BORDER | SWT.CENTER | SWT.READ_ONLY);
		pcom.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				String newVal = pcom.getText();
				if( newVal.equals(currentPos))
					return;
				pcom.setText(currentPos);
				MessageBox box = new MessageBox(LensScannableComposite.this.getShell(),SWT.ICON_QUESTION | SWT.YES | SWT.NO);
				box.setMessage("Are you sure you want to change the camera lens to '" + newVal +"'");
				int open = box.open();
				if(open == SWT.YES){
					Job job = new Job("tomodet.setCameraLens('" + newVal + "')"){

						@Override
						protected IStatus run(IProgressMonitor monitor) {
							InterfaceProvider.getCommandRunner().evaluateCommand(getName());
							return Status.OK_STATUS;
						}};
					job.schedule();
				} 
			}
		});
		GridDataFactory.fillDefaults().applyTo(pcom);
		pcom.setItems(new String[] {  });
		pcom.setVisible(true);
		
		addDisposeListener(new DisposeListener() {
			
			@Override
			public void widgetDisposed(DisposeEvent e) {
				if( lensScannable != null && lensObserver!=null)
					lensScannable.deleteIObserver(lensObserver);
			}
		});

	}
	private void updateLensDisplay(){
		lensObserver.update(lensScannable, null);
	}
	public void setLensScannable(EnumPositioner s){
		lensScannable =s;
		try {
			pcom.removeAll();
			for(String pos : lensScannable.getPositions()){
				if( pos.length() > 1)
					pcom.add(pos);
			}
		} catch (DeviceException e1) {
			logger.error("Error getting positions from the lens", e1);
		}

		lensObserver = new IObserver() {

			@Override
			public void update(Object source, final Object arg) {
					Display.getDefault().asyncExec(new Runnable() {

						@Override
						public void run() {
							try {
								currentPos = (String) lensScannable.getPosition();
								pcom.setText(currentPos);
								GridUtils.layout(group);
							} catch (DeviceException e) {
								logger.error("Error reading the lens position", e);
							}
						}
					});
			}
		};
		lensScannable.addIObserver(lensObserver);
		updateLensDisplay();

	}
	private String currentPos;


}
