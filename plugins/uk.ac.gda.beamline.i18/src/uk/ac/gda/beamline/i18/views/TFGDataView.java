/*-
 * Copyright © 2023 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i18.views;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.VerifyEvent;
import org.eclipse.swt.events.VerifyListener;
import org.eclipse.swt.graphics.Font;
import org.eclipse.swt.graphics.FontData;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.part.ViewPart;

import gda.jython.InterfaceProvider;

public class TFGDataView extends ViewPart {
	public static final String ID = "uk.ac.gda.beamline.i18.views.tfgdataview";
	private Text cycleTxtBox;
	private Text energyTxtBox;
	private Text cycleFrameTxtBox;
	private Text frameCollectionTxtBox;
	private Text frameDeadTxtBox;
	private Button runScanBtn;
	// Set the fonts
	private Font titleFont;
	private Font boldFont;
	private Font italicFont;

	@Override
	public void createPartControl(Composite parent) {

		Composite comp = new Group(parent, SWT.NONE);
		comp.setLayout(new GridLayout(2, false));
		comp.setBackground(Display.getDefault().getSystemColor(SWT.COLOR_WHITE));

		titleFont = new Font(parent.getDisplay(), new FontData("Arial", 14, SWT.BOLD));
		boldFont = new Font(parent.getDisplay(), new FontData("Arial", 12, SWT.BOLD));
		italicFont = new Font(parent.getDisplay(), new FontData("Arial", 12, SWT.ITALIC));

		addTitle(comp, "TFG SCAN");

		addLabel(comp, "Cycle Repetitions",4);
		cycleTxtBox = addNumberTextBox(comp, "1", false);

		addLabel(comp, "Energy Value Cycles",4);
		energyTxtBox = addNumberTextBox(comp, "200000", false);

		addLabel(comp, "Cycle Frames",4);
		cycleFrameTxtBox = addNumberTextBox(comp, "38", false);

		addLabel(comp, "Frame Collection Time",4);
		frameCollectionTxtBox = addNumberTextBox(comp, "200e-9", true);

		addLabel(comp, "Frame Dead Time",4);
		frameDeadTxtBox = addNumberTextBox(comp, "0.0", true);

		runScanBtn = addButton(comp, "Run Scan");
		runScanBtn.addListener(SWT.Selection, event -> runTFGScan());
		runScanBtn.setToolTipText("Run the TFG Scan");

		addTfgInfo(comp, "Cycle Repetitions:", "Number of Repetitions per cycle.");
		addTfgInfo(comp, "Energy Value Cycles:", "Number of cycles at each energy value (laser pulses).");
		addTfgInfo(comp, "Cycle Frames:", "Number of frames in a cycle.");
		addTfgInfo(comp, "Frame Collection Time:", "Data collection time for each frame in seconds.");
		addTfgInfo(comp, "Frame Dead Time:", "Dead time between frames in seconds.");

	}

	private void addTitle(Composite parent, String title) {
		Label titleLbl = new Label(parent, SWT.NONE);
		titleLbl.setFont(titleFont);
		titleLbl.setText(title);
		titleLbl.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, true, false, 2,1));
	}

	private void addTfgInfo(Composite parent, String subject, String value) {
		Label subjectLabel = new Label(parent, SWT.NONE);
		subjectLabel.setFont(boldFont);
		subjectLabel.setText(subject);
		subjectLabel.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, true, false, 1,1));

		Label valueLabel = new Label(parent, SWT.NONE);
		valueLabel.setFont(italicFont);
		valueLabel.setText(value);
		valueLabel.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, true, false, 1,1));
	}

	@Override
	public void setFocus() {
		runScanBtn.setFocus();
	}

	private Button addButton(Composite parent, String text) {
		Button button = new Button(parent, SWT.PUSH);
		button.setText(text);
		button.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 4, 2));
		return button;
	}

	private Text addNumberTextBox(Composite comp, String content, boolean allowDecimals) {
		Text txtBox = new Text(comp, SWT.BORDER);
		txtBox.setBackground(Display.getDefault().getSystemColor(SWT.COLOR_WHITE));
		txtBox.setLayoutData(new GridData(SWT.FILL, SWT.LEFT_TO_RIGHT,true, false, 4,2));
		txtBox.setText(content);
		// Verify that the user input is numeric and if it isn't then don't allow the text to be input
		txtBox.addVerifyListener(new VerifyListener() {
			@Override
			public void verifyText(VerifyEvent e) {
				String currentText=((Text) e.widget).getText();
				String userTxt = currentText.substring(0, e.start)+e.text+currentText.substring(e.end);
				try {
					if(allowDecimals) {
						float userNum = Float.parseFloat(userTxt);
						if(userNum<0) {
							e.doit=false;
						}
					}
					else {
						int userNum = Integer.parseInt(userTxt);
						if(userNum <0) {
							e.doit = false;
						}
					}
				}catch(NumberFormatException ex) {
					if(!userTxt.equals("")) {
						e.doit = false;
					}
					else {
						((Text)e.widget).setText("0");
					}
				}
			}
		});
		return txtBox;
	}

	private Label addLabel(Composite parent, String labelText, int width) {
		Label label = new Label(parent, SWT.NONE);
		label.setForeground(label.getDisplay().getSystemColor(SWT.COLOR_BLACK));
		label.setText(labelText);
		label.setLayoutData(new GridData(SWT.LEFT, SWT.CENTER, true, false, width, 1));
		return label;
	}

	private void runTFGScan() {
		String cycles = cycleTxtBox.getText();
		String energy = energyTxtBox.getText();
		String frame = cycleFrameTxtBox.getText();
		String frameCollection = frameCollectionTxtBox.getText();
		String deadTime = frameDeadTxtBox.getText();
		InterfaceProvider.getCommandRunner().runCommand(String.format("run_tfg(%s,%s,%s,%s,%s)", cycles, energy, frame, frameCollection, deadTime));
	}

	@Override
	public void dispose() {
		titleFont.dispose();
		boldFont.dispose();
		italicFont.dispose();

		super.dispose();
	}
}