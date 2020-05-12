/*-
 * Copyright © 2020 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.shape;

import org.apache.commons.lang3.tuple.ImmutablePair;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;

import uk.ac.diamond.daq.mapping.ui.diffraction.model.ShapeType;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientSWTElements;
import uk.ac.gda.ui.tool.images.ClientImages;

/**
 * A base class common to all the shape GUI elements.
 * <p>
 * The GUI element is a radio button. The radio also stores into its {@code data} property, the shape type it is
 * referring to and this makes easier to retrieve the ShapeType type once the element is selected.
 * </p>
 *
 * @author Maurizio Nagni
 */
class ShapeCompositeBase implements ShapeComposite {
	private Button button;
	private final ShapeType shapeType;
	private final ClientMessages tooltip;
	private final ClientImages icon;

	/**
	 * @param shapeType
	 *            the shape represented by this GUI element
	 * @param tooltip
	 *            the GUI element tooltip
	 * @param icon
	 *            the element icon
	 */
	ShapeCompositeBase(ShapeType shapeType, ClientMessages tooltip, ClientImages icon) {
		super();
		this.shapeType = shapeType;
		this.tooltip = tooltip;
		this.icon = icon;
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		button = ClientSWTElements.createButton(parent, SWT.RADIO, ClientMessages.EMPTY_MESSAGE, tooltip, icon);
		// sets the button data (the shape it refers to)
		button.setData(shapeType);
		return parent;
	}

	@Override
	public ImmutablePair<ShapeType, Button> getShapeDefinition() {
		return new ImmutablePair<>(shapeType, button);
	}
}
