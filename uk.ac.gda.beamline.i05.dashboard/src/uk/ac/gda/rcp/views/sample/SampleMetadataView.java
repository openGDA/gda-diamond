/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package uk.ac.gda.rcp.views.sample;

import org.eclipse.swt.SWT;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.ProgressBar;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.part.ViewPart;

import com.swtdesigner.SWTResourceManager;

public class SampleMetadataView extends ViewPart {
	public SampleMetadataView() {
	}
	protected Text subDirectory;
	protected Text currentDirectory;
	protected Text scanFile;
	protected Text sampleName;

	protected Label eta;
	protected Label elapsedTime;
	protected Label frameStatus;
	protected Label frameNumber;
	protected ProgressBar progressBar;


	@Override
	public void createPartControl(Composite parent) {
		createFirstHalf(parent);
	}

	private void createFirstHalf(Composite parent) {
		GridLayout gl_parent = new GridLayout(4, true);
		gl_parent.verticalSpacing = 12;
		GridData gridData = new GridData(SWT.LEFT, SWT.CENTER, true, false, 1, 1);
		parent.setLayoutData(gridData);
		parent.setLayout(gl_parent);
		{
			Group grpElapsedTime = new Group(parent, SWT.NONE);
			grpElapsedTime.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
			grpElapsedTime.setText("Scan Number");
			grpElapsedTime.setLayout(new FillLayout(SWT.HORIZONTAL));
			frameStatus = new Label(grpElapsedTime, SWT.NONE);
			frameStatus.setText("UNKNOWN");
			frameStatus.setFont(SWTResourceManager.getFont("Sans", 12, SWT.NORMAL));
			frameStatus.setBackground(SWTResourceManager.getColor(SWT.COLOR_TITLE_INACTIVE_BACKGROUND));
			frameStatus.setAlignment(SWT.CENTER);
		}
		{
			Group grpFrame = new Group(parent, SWT.NONE);
			grpFrame.setText("Iteration");
			grpFrame.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
			grpFrame.setLayout(new FillLayout(SWT.HORIZONTAL));
				frameNumber = new Label(grpFrame, SWT.NONE);
				frameNumber.setAlignment(SWT.CENTER);
				frameNumber.setFont(SWTResourceManager.getFont("Sans", 12, SWT.NORMAL));
				frameNumber.setBackground(SWTResourceManager.getColor(SWT.COLOR_TITLE_INACTIVE_BACKGROUND));
				frameNumber.setText("[0] / [0]");
		}
		{
			Group grpElapsedTime = new Group(parent, SWT.NONE);
			grpElapsedTime.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false, 1, 1));
			grpElapsedTime.setText("Elapsed");
			grpElapsedTime.setLayout(new FillLayout(SWT.HORIZONTAL));
				elapsedTime = new Label(grpElapsedTime, SWT.NONE);
				elapsedTime.setText("00:00:00");
				elapsedTime.setFont(SWTResourceManager.getFont("Sans", 12, SWT.NORMAL));
				elapsedTime.setBackground(SWTResourceManager.getColor(SWT.COLOR_TITLE_INACTIVE_BACKGROUND));
				elapsedTime.setAlignment(SWT.CENTER);
		}
		{
			Group grpElapsedTime = new Group(parent, SWT.NONE);
			grpElapsedTime.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false, 1, 1));
			grpElapsedTime.setText("Remaining");
			grpElapsedTime.setLayout(new FillLayout(SWT.HORIZONTAL));
				eta = new Label(grpElapsedTime, SWT.NONE);
				eta.setText("00:00:00");
				eta.setFont(SWTResourceManager.getFont("Sans", 12, SWT.NORMAL));
				eta.setBackground(SWTResourceManager.getColor(SWT.COLOR_TITLE_INACTIVE_BACKGROUND));
				eta.setAlignment(SWT.CENTER);
		}
		{
			Label label = new Label(parent, SWT.NONE);
			label.setText("Progress");

			progressBar = new ProgressBar(parent, SWT.NONE);
			progressBar.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false, 3, 1));
			progressBar.setMaximum(10000);
			progressBar.setMinimum(0);
		}
		{
			Label lblLastScanFile = new Label(parent, SWT.NONE);
			lblLastScanFile.setText("Last Scan File");
			lblLastScanFile.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false, 1, 1));

			scanFile = new Text(parent, SWT.NONE);
			scanFile.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 3, 1));
			scanFile.setBackground(SWTResourceManager.getColor(SWT.COLOR_WHITE));
			scanFile.setText("");
			scanFile.setEditable(false);
		}
		{
			Label label = new Label(parent, SWT.NONE);
			label.setText("Current Directory");
			label.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false, 1, 1));

			currentDirectory = new Text(parent, SWT.NONE);
			currentDirectory.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 3, 1));
			currentDirectory.setBackground(SWTResourceManager.getColor(SWT.COLOR_WHITE));
			currentDirectory.setText("");
			currentDirectory.setEditable(false);
		}
		{
			Label label = new Label(parent, SWT.NONE);
			label.setText("Subdirectory");
			label.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false, 1, 1));

			subDirectory = new Text(parent, SWT.BORDER);
			subDirectory.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 3, 1));
			subDirectory.setBackground(SWTResourceManager.getColor(SWT.COLOR_WHITE));
			subDirectory.setText("");
		}		
		{
			Label label = new Label(parent, SWT.NONE);
			label.setText("Sample Name");
			label.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false, 1, 1));

			sampleName = new Text(parent, SWT.BORDER);
			sampleName.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 3, 1));
			sampleName.setBackground(SWTResourceManager.getColor(SWT.COLOR_WHITE));
			sampleName.setText("");
		}

		new MetadataUpdater(this);
	}

	@Override
	public void setFocus() {
	}
}