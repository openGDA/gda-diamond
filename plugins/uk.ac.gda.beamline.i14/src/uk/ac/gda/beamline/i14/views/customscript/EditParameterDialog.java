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

package uk.ac.gda.beamline.i14.views.customscript;

import static org.eclipse.jface.dialogs.IMessageProvider.INFORMATION;

import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.beans.typed.PojoProperties;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.jface.databinding.swt.typed.WidgetProperties;
import org.eclipse.jface.dialogs.TitleAreaDialog;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;

/**
 * Dialog to allow editing of a script parameter or input of a new one
 * <p>
 * The dialog consists of two text fields, which are bound to the name and value properties of a
 * {@link ScriptParameter} object.
 */
class EditParameterDialog extends TitleAreaDialog {

	private final DataBindingContext bindingContext = new DataBindingContext();

	private ScriptParameter parameter = new ScriptParameter("", "");

	public EditParameterDialog(Shell parentShell) {
		super(parentShell);
	}

	@Override
	protected Control createContents(Composite parent) {
		final Control contents = super.createContents(parent);
		setTitle("Add or edit a parameter");
		setMessage("Enter parameter name and value", INFORMATION);
		return contents;
	}

	@Override
	protected Control createDialogArea(Composite parent) {
		final Composite dialogComposite = (Composite) super.createDialogArea(parent);

		final Composite parameterComposite = new Composite(dialogComposite, SWT.NONE);
		GridDataFactory.swtDefaults().applyTo(parameterComposite);
		GridLayoutFactory.swtDefaults().numColumns(2).applyTo(parameterComposite);

		createLabel(parameterComposite, "Name:");
		final Text nameText = createText(parameterComposite, parameter.getName());
		final IObservableValue<String> nameTextObs = WidgetProperties.text(SWT.Modify).observe(nameText);
		final IObservableValue<String> nameParamObs = PojoProperties.value("name", String.class).observe(parameter);
		bindingContext.bindValue(nameTextObs, nameParamObs);

		createLabel(parameterComposite, "Value:");
		final Text valueText = createText(parameterComposite, parameter.getValue());
		final IObservableValue<String> valueTextObs = WidgetProperties.text(SWT.Modify).observe(valueText);
		final IObservableValue<String> valueParamObs = PojoProperties.value("value", String.class).observe(parameter);
		bindingContext.bindValue(valueTextObs, valueParamObs);

		return dialogComposite;
	}

	private Label createLabel(Composite parent, String text) {
		final Label label = new Label(parent, SWT.NONE);
		GridDataFactory.swtDefaults().applyTo(label);
		label.setText(text);
		return label;
	}

	private Text createText(Composite parent, String text) {
		final Text textBox = new Text(parent, SWT.BORDER);
		GridDataFactory.swtDefaults().hint(300, SWT.DEFAULT).applyTo(textBox);
		textBox.setText(text == null ? "" : text);
		return textBox;
	}

	public ScriptParameter getParameter() {
		return parameter;
	}

	public void setParameter(ScriptParameter parameter) {
		this.parameter = parameter;
	}

	@Override
	public boolean close() {
		bindingContext.dispose();
		return super.close();
	}
}