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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction;

import static org.eclipse.swt.events.SelectionListener.widgetSelectedAdapter;
import static uk.ac.gda.ui.tool.ClientSWTElements.getImage;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.CopyOnWriteArraySet;
import java.util.function.Consumer;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.ToolBar;
import org.eclipse.swt.widgets.ToolItem;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.configuration.diffraction.ShapeSelectionButtons.ShapeSelectionEvent.SelectionType;
import uk.ac.gda.api.acquisition.TrajectoryShape;
import uk.ac.gda.ui.tool.images.ClientImages;

public class ShapeSelectionButtons {

	public record ShapeSelectionEvent(SelectionType type, TrajectoryShape selection, Optional<TrajectoryShape> previousSelection) {
		enum SelectionType { REDRAW, SHAPE_CHANGE }
	}

	private Map<ToolItem, TrajectoryShape> buttonToShape = new HashMap<>();
	private Set<Consumer<ShapeSelectionEvent>> listeners = new CopyOnWriteArraySet<>();

	private Optional<ToolItem> previousSelection = Optional.empty();

	public ShapeSelectionButtons(Composite parent, List<ShapeDescriptor> shapes) {
		ToolBar toolBar = new ToolBar(parent, SWT.FLAT | SWT.VERTICAL);
		GridDataFactory.swtDefaults().align(SWT.LEFT, SWT.TOP).applyTo(toolBar);

		shapes.forEach(descriptor -> addShape(toolBar, descriptor.shape(), descriptor.icon()));

		divider(toolBar);

		var redraw = new ToolItem(toolBar, SWT.PUSH);
		var icon = getImage(ClientImages.MAP_REDRAW);
		redraw.setImage(icon);
		redraw.setToolTipText("Redraw region in map");
		redraw.addSelectionListener(widgetSelectedAdapter(selection -> sendRedrawShapeEvent()));
		redraw.addDisposeListener(dispose -> icon.dispose());
	}

	public void addListener(Consumer<ShapeSelectionEvent> listener) {
		listeners.add(listener);
	}

	public void setSelection(TrajectoryShape shape) {
		buttonToShape.keySet().forEach(button -> button.setSelection(false));

		ToolItem button = buttonToShape.entrySet().stream()
			.filter(entry -> entry.getValue().equals(shape))
			.map(Map.Entry::getKey)
			.findFirst().orElseThrow(() -> new IllegalArgumentException("Unknown shape: " + shape));

		button.setSelection(true);
		var selectionEvent = new Event();
		selectionEvent.widget = button;
		button.notifyListeners(SWT.Selection, selectionEvent);
	}

	public Optional<TrajectoryShape> getSelection() {
		return getSelectedButton().map(buttonToShape::get);
	}

	private void addShape(ToolBar toolBar, TrajectoryShape shape, ClientImages image) {
		var button = new ToolItem(toolBar, SWT.RADIO);
		var icon = getImage(image);
		button.setImage(icon);
		button.addDisposeListener(dispose -> icon.dispose());
		buttonToShape.put(button, shape);
		button.addSelectionListener(widgetSelectedAdapter(this::sendShapeChangeEvent));
	}

	@SuppressWarnings("unused")
	private void divider(ToolBar toolBar) {
		new ToolItem(toolBar, SWT.SEPARATOR);
	}

	private void sendShapeChangeEvent(SelectionEvent selectionEvent) {
		var button = (ToolItem) selectionEvent.widget;
		if (button.getSelection()) {
			var event = new ShapeSelectionEvent(SelectionType.SHAPE_CHANGE, buttonToShape.get(button), previousSelection.map(buttonToShape::get));
			sendEvent(event);
		} else {
			previousSelection = Optional.of(button);
		}
	}

	private void sendRedrawShapeEvent() {
		var selection = getSelectedButton();
		if (selection.isPresent()) {
			var event = new ShapeSelectionEvent(SelectionType.REDRAW, buttonToShape.get(selection.get()), Optional.empty());
			sendEvent(event);
		}
	}

	private void sendEvent(ShapeSelectionEvent event) {
		listeners.forEach(listener -> listener.accept(event));
	}

	private Optional<ToolItem> getSelectedButton() {
		return buttonToShape.keySet().stream()
				.filter(ToolItem::getSelection).findFirst();
	}
}
