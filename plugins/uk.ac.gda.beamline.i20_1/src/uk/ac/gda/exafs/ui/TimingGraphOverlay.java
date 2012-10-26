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

package uk.ac.gda.exafs.ui;

import java.awt.Color;

import org.dawnsci.plotting.jreality.overlay.Overlay1DProvider;
import org.dawnsci.plotting.jreality.overlay.OverlayProvider;
import org.dawnsci.plotting.jreality.overlay.OverlayType;
import org.dawnsci.plotting.jreality.overlay.events.AbstractOverlayConsumer;
import org.dawnsci.plotting.jreality.overlay.events.OverlayDrawingEvent;
import org.dawnsci.plotting.jreality.overlay.primitives.PrimitiveType;
import org.eclipse.swt.widgets.Display;

public class TimingGraphOverlay extends AbstractOverlayConsumer {

	double[] inputTriggers = new double[0];
	double[] outputTriggers = new double[0];

	public TimingGraphOverlay(Display display) {
		super(display);
	}

	@Override
	protected int[] createDrawingParts(OverlayProvider provider) {
		// copied from ElementEdgeEditor. Dunno wot this is for. Javadoc unclear.
		final int[] lines = new int[inputTriggers.length + outputTriggers.length];
		for (int i = 0; i < lines.length; i++) {
			lines[i] = provider.registerPrimitive(PrimitiveType.LINE);
		}
		return lines;
	}

	@Override
	protected void drawOverlay(OverlayDrawingEvent evt) {
		for (int i = 0; i < inputTriggers.length; i++) {
			addTrig(inputTriggers[i], Color.RED, i);
		}
		for (int i = 0; i < outputTriggers.length; i++) {
			float[] vals = Color.RGBtoHSB(51, 158, 0, null);//
			addTrig(outputTriggers[i], Color.getHSBColor(vals[0],vals[1],vals[2]), i + inputTriggers.length);
		}
	}

	private void addTrig(double trig, Color inputColour, int lineNumber) {
		provider.begin(OverlayType.VECTOR2D);
		provider.setColour(parts[lineNumber], inputColour);
		((Overlay1DProvider) provider).drawLine(parts[lineNumber], trig, -0.25, trig, 1.25);
		provider.end(OverlayType.VECTOR2D);
	}

	public double[] getInputTriggers() {
		return inputTriggers;
	}

	public void setInputTriggers(double[] inputTriggers) {
		if (inputTriggers == null) {
			inputTriggers = new double[0];
		} else {
			this.inputTriggers = inputTriggers;
		}
	}

	public double[] getOutputTriggers() {
		return outputTriggers;
	}

	public void setOutputTriggers(double[] outputTriggers) {
		if (outputTriggers == null) {
			outputTriggers = new double[0];
		} else {
			this.outputTriggers = outputTriggers;
		}
	}

}
