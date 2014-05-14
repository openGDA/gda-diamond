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

package uk.ac.gda.dls.client.views;

import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.scannable.ScannablePositionChangeEvent;
import gda.observable.IObserver;
import gda.rcp.util.BrowserUtil;
import gda.rcp.views.CompositeFactory;

import java.net.URI;
import java.net.URISyntaxException;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.events.MouseListener;
import org.eclipse.swt.events.PaintEvent;
import org.eclipse.swt.events.PaintListener;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Canvas;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class HealthCheckCompositeFactory implements CompositeFactory {
	// private static final Logger logger = LoggerFactory.getLogger(HealthCheckCompositeFactory.class);

	Scannable healthScannable, heartBeatScannable;

	String label;

	public Scannable getHealthScannable() {
		return healthScannable;
	}

	public void setHealthScannable(Scannable healthScannable) {
		this.healthScannable = healthScannable;
	}

	public Scannable getHeartBeatScannable() {
		return heartBeatScannable;
	}

	public void setHeartBeatScannable(Scannable heartBeatScannable) {
		this.heartBeatScannable = heartBeatScannable;
	}

	public String getLabel() {
		return label;
	}

	public void setLabel(String label) {
		this.label = label;
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		return new HealthCheckComposite(parent, style, label,
				healthScannable, heartBeatScannable);
	}
}

class HealthCheckComposite extends Composite {
	private static final Logger logger = LoggerFactory.getLogger(HealthCheckComposite.class);

	private final Color COLOR_UNKNOWN;
	private final Color COLOR_BAD;
	private final Color COLOR_GOOD;
	private final Color COLOR_POOR;
	Color color;

	/**
	 * heartBeatScannable switches between on and something else
	 */
	public static final String ON = "on";
	/**
	 * value of healthScannable when the state is bad - RED light
	 */
	public static final String BAD = "bad";
	/**
	 * value of healthScannable when the state is poor - AMBER light
	 */
	public static final String POOR = "poor";
	/**
	 * value of healthScannable when the state is good - GREEN light
	 */
	public static final String GOOD = "good";

	final Scannable healthScannable, heartBeatScannable;

	Display display;
	private IObserver healthObserver;
	private Canvas healthCanvas;

	/**
	 * @return URI attribute of the healthScannable to be displayed in a browser
	 * @throws URISyntaxException
	 * @throws DeviceException
	 */
	public URI getUri() throws URISyntaxException, DeviceException {
		URI uri = new URI((String) healthScannable.getAttribute("uri"));
		return uri;
	}

	HealthCheckComposite(Composite parent, int style, String label, Scannable healthScannable,
			Scannable heartBeatScannable) {
		super(parent, style);
		GridLayoutFactory.swtDefaults().numColumns(1).applyTo(this);
		GridDataFactory.fillDefaults().applyTo(this);
		Group grp = new Group(this, style);
		GridLayoutFactory.swtDefaults().numColumns(1).applyTo(grp);
		GridDataFactory.fillDefaults().applyTo(grp);
		grp.setText(label);

		this.display = parent.getDisplay();
		this.healthScannable = healthScannable;
		this.heartBeatScannable = heartBeatScannable;
		GridLayoutFactory.swtDefaults().numColumns(1).applyTo(this);
		GridDataFactory.fillDefaults().applyTo(this);

		COLOR_UNKNOWN = display.getSystemColor(SWT.COLOR_DARK_GRAY);
		COLOR_BAD = display.getSystemColor(SWT.COLOR_RED);
		COLOR_GOOD = display.getSystemColor(SWT.COLOR_GREEN);
		COLOR_POOR = display.getSystemColor(SWT.COLOR_YELLOW);
		color = COLOR_UNKNOWN;

		healthCanvas = new Canvas(grp, SWT.NONE);
		GridData gridData = new GridData(GridData.VERTICAL_ALIGN_FILL);
		gridData.heightHint = 40;
		gridData.widthHint = 40;
		healthCanvas.setLayoutData(gridData);
		healthCanvas.addPaintListener(new PaintListener() {
			@Override
			public void paintControl(PaintEvent e) {
				GC gc = e.gc;
				gc.setAntialias(SWT.ON);
				gc.setBackground(color);
				// gc.setForeground(COLOR_BAD)
				gc.setLineWidth(1);
				Rectangle clientArea = healthCanvas.getClientArea();
				final int margin = 4;
				final Point topLeft = new Point(margin, margin);
				final Point size = new Point(clientArea.width - margin * 2, clientArea.height - margin * 2);
				gc.fillOval(topLeft.x, topLeft.y, size.x, size.y);
				gc.drawOval(topLeft.x, topLeft.y, size.x, size.y);
			}
		});
		healthCanvas.addMouseListener(new MouseListener() {

			@Override
			public void mouseDoubleClick(MouseEvent e) {
			}

			@Override
			public void mouseDown(MouseEvent e) {
			}

			@Override
			public void mouseUp(MouseEvent e) {
				try {
					URI uri = getUri();
					BrowserUtil.openBrowserAsView(uri.toURL().toString(), null, "", "");
				} catch (Exception e1) {
					HealthCheckComposite.logger.error("Error viewing health check report", e1);
				}
			}

		});

		healthObserver = new IObserver() {

			@Override
			public void update(Object source, Object arg) {
				if (arg instanceof ScannablePositionChangeEvent) {
					String s = (String) ((ScannablePositionChangeEvent) arg).newPosition;
					updateHealthIndicator(s);
				}

			}
		};
		healthScannable.addIObserver(healthObserver);
		
		try {
			updateHealthIndicator((String) healthScannable.getPosition());
		} catch (DeviceException e) {
			logger.error("Unable to get initial beamline health state", e);
		}
	}
	
	private void updateHealthIndicator(String newState) {
		if (newState.equals(GOOD)) {
			color = COLOR_GOOD;
		} else if (newState.equals(POOR)) {
			color = COLOR_POOR;
		} else if (newState.equals(BAD)) {
			color = COLOR_BAD;
		} else {
			color = COLOR_UNKNOWN;
		}
		reDraw();
	}

	void reDraw() {
		display.asyncExec(new Runnable() {

			@Override
			public void run() {
				healthCanvas.redraw();
				healthCanvas.update();
			}

		});
	}

	@Override
	public void dispose() {
		super.dispose();
		healthScannable.deleteIObserver(healthObserver);
	}

}
