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

package uk.ac.diamond.daq.beamline.k11.diffraction.view.summary;

import static uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeHelper.POLICY_NEVER;
import static uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeHelper.mappingRegionShapeToShape;

import java.lang.reflect.Field;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

import org.apache.commons.beanutils.PropertyUtils;
import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.databinding.observable.value.SelectObservableValue;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.scanning.api.points.models.IScanPointGeneratorModel;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.graphics.Font;
import org.eclipse.swt.graphics.FontData;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;

import uk.ac.diamond.daq.beamline.k11.diffraction.view.DiffractionCompositeInterface;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegion;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.ui.diffraction.model.ShapeType;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.gda.ui.tool.ClientSWTElements;

/**
 * Components representing the GUI summary element per {@link ShapeType}. As not all the elements are available through
 * the update {@link IScanPointGeneratorModel}, some properties are binded/retrieved using
 * {@link RegionAndPathController}. In both cases to simplify the code specific {@link ShapeSummaryBase} property
 * names match the ones in {@link IScanPointGeneratorModel} or {@link RegionAndPathController}.
 *
 * @author Maurizio Nagni
 */
public class SummaryCompositeFactory implements DiffractionCompositeInterface {

	private final DataBindingContext regionDBC;

	private final IObservableValue<IMappingScanRegionShape> mbShapeObservableValue;
	private final SelectObservableValue<ShapeType> selectedShape;

	private final RegionAndPathController rapController;

	private static final int PADDING = 15;
	private StyledText summaryText;
	private Composite container;
	private final Map<ShapeType, ShapeSummaryBase> summaryMap = new HashMap<>();

	public SummaryCompositeFactory(DataBindingContext regionDBC,
			IObservableValue<IMappingScanRegionShape> mbShapeObservableValue,
			SelectObservableValue<ShapeType> selectedShape, RegionAndPathController rapController) {
		super();
		this.regionDBC = regionDBC;
		this.mbShapeObservableValue = mbShapeObservableValue;
		this.selectedShape = selectedShape;
		this.rapController = rapController;
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		container = ClientSWTElements.createComposite(parent, SWT.NONE, 1);
		createControl(container);
		GridDataFactory.swtDefaults().align(SWT.FILL, SWT.CENTER).grab(true, false).applyTo(container);
		return parent;
	}

	@Override
	public void bindControls() {
		update();
		container.getParent().layout(true, true);
	}

	@Override
	public void updateScanPointBindings(final IScanPointGeneratorModel newPathValue, ShapeType shapeType) {
		updateRegionShapeBindings(shapeType);
		updateBinding(shapeType);
	}

	/**
	 * Retrieves the {@link StyledText} control used to display the summary infomation
	 *
	 * @param parent
	 *            The containing {@link Composite for the control}
	 */
	private void createControl(Composite parent) {
		summaryText = new StyledText(parent, SWT.BORDER);
		summaryText.setMargins(PADDING, PADDING, PADDING, PADDING);
		summaryText.setWordWrap(true);
		summaryText.setFont(new Font(parent.getDisplay(), new FontData("PT Sans Narrow", 13, SWT.NONE)));
		summaryText.setCaret(null);
		summaryText.setEditable(false);
		summaryMap.put(ShapeType.POINT, new PointSummary(summaryText::setText));
		summaryMap.put(ShapeType.LINE, new LineSummary(summaryText::setText));
		summaryMap.put(ShapeType.CENTRED_RECTANGLE, new CentredRectangleSummary(summaryText::setText));
	}

	/**
	 * Refresh the content of the @link StyledText} control with updated text reflecting the current field values
	 */
	private void update() {
		if (summaryText != null) {
			summaryText.setText(getText());
		}
	}

	/**
	 * Fill in the text content based on the currently active {@link ShapeType}
	 *
	 * @return The text content {@link String}
	 */
	private String getText() {
		return summaryMap.get(selectedShape.getValue()).toString();
	}

	/**
	 * Rewrites the bindings relating to the mapping bean's region shape so that the {@link Button}s and
	 * {@link StyledText} summary controls get linked to the correct property on the correct {@link IMappingScanRegion}
	 * when the region shape is changed by any linked views
	 */
	private void updateRegionShapeBindings(ShapeType shapeType) {
		// SUMMARY
		regionDBC.bindValue(mbShapeObservableValue, selectedShape,
				UpdateValueStrategy.create(mappingRegionShapeToShape), POLICY_NEVER);
		updateBinding(shapeType);
	}

	private void updateBinding(ShapeType shapeType) {
		ShapeSummaryBase st = summaryMap.get(shapeType);
		Class<?> cls = st.getClass();
		Field[] fieldlist = cls.getDeclaredFields();
		Arrays.stream(fieldlist).filter(f -> PropertyUtils.isReadable(st, f.getName())).forEach(f -> {
			if (PropertyUtils.isReadable(rapController.getScanRegionShape(), f.getName())) {
				bindFromModelToTarget(regionDBC, BeanProperties.value(f.getName()).observe(st),
						BeanProperties.value(f.getName()).observe(rapController.getScanRegionShape()));
			}
		});
	}

	private Binding bindFromModelToTarget(final DataBindingContext dbc, final IObservableValue<?> target,
			final IObservableValue<?> model) {
		return dbc.bindValue(target, model, new UpdateValueStrategy(UpdateValueStrategy.POLICY_NEVER),
				new UpdateValueStrategy(UpdateValueStrategy.POLICY_UPDATE));
	}
}
