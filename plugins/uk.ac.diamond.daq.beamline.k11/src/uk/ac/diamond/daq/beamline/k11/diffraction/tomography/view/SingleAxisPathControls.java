/*-
 * Copyright © 2022 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.tomography.view;

import static uk.ac.gda.ui.tool.ClientSWTElements.composite;
import static uk.ac.gda.ui.tool.ClientSWTElements.innerComposite;
import static uk.ac.gda.ui.tool.ClientSWTElements.label;
import static uk.ac.gda.ui.tool.ClientSWTElements.numericTextBox;
import static uk.ac.gda.ui.tool.ClientSWTElements.spinner;

import java.util.function.Supplier;
import java.util.stream.Stream;

import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Spinner;
import org.eclipse.swt.widgets.Text;

import gda.observable.IObservable;
import gda.observable.IObserver;
import gda.observable.ObservableComponent;
import uk.ac.diamond.daq.mapping.api.document.scanpath.ScannableTrackDocument;
import uk.ac.gda.ui.tool.Reloadable;

public class SingleAxisPathControls implements Reloadable, IObservable {

	private ObservableComponent observableComponent = new ObservableComponent();

	private Supplier<ScannableTrackDocument> axis;

	private Text start;
	private Text stop;
	private Spinner points;

	private boolean handlingReload;

	public SingleAxisPathControls(Composite parent, Supplier<ScannableTrackDocument> axis) {

		this.axis = axis;

		var inner = innerComposite(parent, 1, false);
		var composite = composite(inner, 3);

		label(composite, "Start");
		label(composite, "Stop");
		label(composite, "Points");

		start = numericTextBox(composite);
		stop = numericTextBox(composite);
		points = spinner(composite);

		Stream.of(start, stop, points).forEach(widget -> widget.addListener(SWT.Modify, modification -> controlsToModel()));

		reload();
	}

	private void controlsToModel() {
		if (handlingReload) return;
		var updatedModel = new ScannableTrackDocument(axis.get());
		updatedModel.setStart(Double.parseDouble(start.getText()));
		updatedModel.setStop(Double.parseDouble(stop.getText()));
		updatedModel.setPoints(points.getSelection());

		observableComponent.notifyIObservers(this, updatedModel);
	}

	@Override
	public void reload() {
		handlingReload = true;
		var model = axis.get();
		try {
			start.setText(String.valueOf(model.getStart()));
			stop.setText(String.valueOf(model.getStop()));
			points.setSelection(model.getPoints());
		} finally {
			handlingReload = false;
		}
	}

	@Override
	public void addIObserver(IObserver observer) {
		observableComponent.addIObserver(observer);

	}

	@Override
	public void deleteIObserver(IObserver observer) {
		observableComponent.deleteIObserver(observer);
	}

	@Override
	public void deleteIObservers() {
		observableComponent.deleteIObservers();
	}

}
