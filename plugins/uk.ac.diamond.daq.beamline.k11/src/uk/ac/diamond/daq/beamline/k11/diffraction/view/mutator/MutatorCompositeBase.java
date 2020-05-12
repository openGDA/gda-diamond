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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.mutator;

import org.apache.commons.lang3.tuple.ImmutablePair;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;

import uk.ac.diamond.daq.mapping.ui.diffraction.base.DiffractionParameters;
import uk.ac.diamond.daq.mapping.ui.diffraction.model.MutatorType;
import uk.ac.gda.ui.tool.ClientMessages;
import uk.ac.gda.ui.tool.ClientSWTElements;

/**
 * An abstract class common to all the mutator GUI elements.
 * <p>
 * The GUI element is a check box. The check box also stores into its {@code data} property, the mutator type it is
 * referring to and this makes easier to retrieve the Mutator type once the element is selected.
 * </p>
 *
 * @author Maurizio Nagni
 */
abstract class MutatorCompositeBase implements MutatorComposite {
	private Button button;
	private final MutatorType mutatorType;
	private final ClientMessages title;
	private final ClientMessages tooltip;
	private final SelectionListener mutatorListener;

	/**
	 * @param mutatorType
	 *            the mutator represented by this GUI element
	 * @param title
	 *            the GUI element label
	 * @param tooltip
	 *            the GUI element tooltip
	 * @param mutatorListener
	 *            A listener to add/remove a this listener to the {@link DiffractionParameters} model.
	 */
	MutatorCompositeBase(MutatorType mutatorType, ClientMessages title, ClientMessages tooltip,
			SelectionListener mutatorListener) {
		super();
		this.mutatorType = mutatorType;
		this.title = title;
		this.tooltip = tooltip;
		this.mutatorListener = mutatorListener;
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		button = ClientSWTElements.createButton(parent, SWT.CHECK, title, tooltip);
		// Sets the mutator type. In this way is easier to have the type should the element be selected
		button.setData(mutatorType);
		button.addSelectionListener(mutatorListener);
		return parent;
	}

	@Override
	public ImmutablePair<MutatorType, Button> getMutatorDefinition() {
		return new ImmutablePair<>(mutatorType, button);
	}
}
