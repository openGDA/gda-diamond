/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package uk.ac.gda.beamline.i20;

import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;

import org.eclipse.core.runtime.Platform;
import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.swt.SWT;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.Font;
import org.eclipse.swt.graphics.FontData;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.RGB;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.ui.preferences.ScopedPreferenceStore;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import uk.ac.gda.exafs.ExafsActivator;
import uk.ac.gda.exafs.ui.data.ScanObjectManager;

public class I20IntroDialog extends Dialog {

	private static final Logger logger = LoggerFactory.getLogger(I20IntroDialog.class);

	protected I20IntroDialog(Shell parentShell) {
		super(parentShell);
	}

	@Override
	public Control createDialogArea(Composite parent) {
        Composite container = (Composite) super.createDialogArea(parent);
        container.setLayout(new GridLayout(2, false));
		applyBackground(container);
		createFullWidthMessage(container, "Welcome to I20.", 24);
		createFullWidthMessage(container, "You will collect data under experiment " + LocalProperties.get(LocalProperties.RCP_APP_VISIT), 20);
		createFullWidthMessage(container, "Choose the type of experiment you wish to perform:", 20);
		createExperimentTypeButton(container, "EXAFS\\XANES", createImage("icons/link_obj.gif"), false);
		createExperimentTypeButton(container, "XES", createImage("icons/link_obj.gif"), true);
		return container;
	}

	/**
	 * Don't create the button bar - already has custom buttons
	 */
	@Override
	protected void createButtonsForButtonBar(final Composite parent) {
		GridLayout layout = (GridLayout) parent.getLayout();
		layout.marginHeight = 0;
	}

	@Override
	protected void configureShell(Shell newShell) {
		super.configureShell(newShell);
		newShell.setText("Experiment mode selection");
	}

	@Override
	protected Point getInitialSize() {
		return new Point(700, 280);
	}

	private void applyBackground(Composite parent) {
		Color color = getI20Color(parent);
		parent.setBackground(color);
		Image newImage = new Image(parent.getDisplay(), 1920, 1600);
		GC gc = new GC(newImage);
		gc.setBackground(parent.getDisplay().getSystemColor(SWT.COLOR_WHITE));
		gc.setForeground(color);
		gc.fillGradientRectangle(0, 0, 1920, 1400, true);
		gc.dispose();
		parent.setBackgroundImage(newImage);
	}

	protected Color getI20Color(Composite parent) {
		RGB rgbColor = new RGB(248f, 0.27f, 0.94f);
		Color color = new Color(parent.getDisplay(), rgbColor);
		return color;
	}

	public static Image createImage(String imagePath) {
		try {
			URL url = Platform.getBundle(I20BeamlineActivator.PLUGIN_ID).getEntry(imagePath);
			if(url!=null)
				return new Image(null, url.openStream());
		} catch (MalformedURLException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return null;
	}

	protected void createFullWidthMessage(Composite parent, String message, int fontSize) {
		Label theLabel = new Label(parent, SWT.LEFT);
		theLabel.setText(message);
		theLabel.setBackground(getI20Color(parent));
		GridData labelGD = new GridData(SWT.FILL, SWT.DEFAULT, true, false);
		labelGD.horizontalSpan = 2;
		labelGD.widthHint = 500;
		theLabel.setLayoutData(labelGD);
		FontData fd = theLabel.getFont().getFontData()[0];
		fd.setHeight(fontSize);
		Font newFont = new Font(parent.getDisplay(), fd);
		theLabel.setFont(newFont);
	}

	protected void createExperimentTypeButton(Composite parent, String experimentType, Image displayImage, final boolean isXES) {
		Button theLabel = new Button(parent, SWT.LEFT);
		theLabel.setText(experimentType);
		theLabel.setImage(displayImage);
		GridData labelGD = new GridData(SWT.FILL, SWT.DEFAULT, true, false);
		labelGD.widthHint = 100;
		labelGD.heightHint = 100;
		theLabel.setLayoutData(labelGD);

		theLabel.addListener(SWT.Selection, event -> {
			ScanObjectManager.setXESOnlyMode(isXES);
			// Try to write XAS/XES mode preference to disk immediately.
			try {
				ScopedPreferenceStore store = (ScopedPreferenceStore) ExafsActivator.getDefault().getPreferenceStore();
				store.save();
			} catch (IOException ioException) {
				logger.error("Problem saving XES/XAS mode preference to disk : ", ioException);
			}
			close();
		});
	}
}
