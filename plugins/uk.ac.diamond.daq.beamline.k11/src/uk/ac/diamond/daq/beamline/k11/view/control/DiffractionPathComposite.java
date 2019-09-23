/*-
 * Copyright © 2019 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.k11.view.control;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Consumer;

import org.apache.commons.lang3.tuple.MutablePair;
import org.eclipse.core.databinding.Binding;
import org.eclipse.core.databinding.DataBindingContext;
import org.eclipse.core.databinding.UpdateValueStrategy;
import org.eclipse.core.databinding.beans.BeanProperties;
import org.eclipse.core.databinding.beans.PojoProperties;
import org.eclipse.core.databinding.conversion.IConverter;
import org.eclipse.core.databinding.observable.value.IObservableValue;
import org.eclipse.core.databinding.observable.value.IValueChangeListener;
import org.eclipse.core.databinding.observable.value.SelectObservableValue;
import org.eclipse.core.databinding.observable.value.ValueChangeEvent;
import org.eclipse.core.databinding.validation.ValidationStatus;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.dawnsci.plotting.api.IPlottingService;
import org.eclipse.dawnsci.plotting.api.IPlottingSystem;
import org.eclipse.jface.databinding.swt.ISWTObservableValue;
import org.eclipse.jface.databinding.swt.WidgetProperties;
import org.eclipse.jface.fieldassist.ControlDecoration;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.resource.JFaceResources;
import org.eclipse.jface.resource.LocalResourceManager;
import org.eclipse.scanning.api.points.models.GridModel;
import org.eclipse.scanning.api.points.models.IScanPathModel;
import org.eclipse.scanning.api.points.models.SinglePointModel;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.events.KeyListener;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.events.MouseWheelListener;
import org.eclipse.swt.graphics.Color;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.RGB;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Scale;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.plugin.AbstractUIPlugin;

import com.google.common.collect.ImmutableMap;
import com.google.common.primitives.Ints;

import uk.ac.diamond.daq.beamline.k11.Activator;
import uk.ac.diamond.daq.beamline.k11.handler.CtrlClickToScanHandler;
import uk.ac.diamond.daq.beamline.k11.view.control.PathSummary.Shape;
import uk.ac.diamond.daq.mapping.api.IMappingExperimentBean;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegion;
import uk.ac.diamond.daq.mapping.api.IMappingScanRegionShape;
import uk.ac.diamond.daq.mapping.region.CentredRectangleMappingRegion;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController;
import uk.ac.diamond.daq.mapping.ui.experiment.RegionAndPathController.RegionPathState;
import uk.ac.diamond.daq.mapping.ui.experiment.ScanManagementController;

/**
 * Composite holding the region and path controls for the DIAD Point and Shoot DiffractionScanSelection view
 *
 * @since GDA 9.13
 */
public class DiffractionPathComposite extends Composite {

	private static final Map<String, String> SHAPES_MAP = ImmutableMap.of(
			"Point", "Select Point scan",
			"Centred_Rectangle", "Select centred Rectangular scan",
			"Line", "Select centred Line scan");

	private static final Map<String, List<String>> FIELDS_MAP = ImmutableMap.of(
			"Point", Arrays.asList("xPosition", "yPosition"),
			"Centred Rectangle", Arrays.asList("xCentre", "yCentre", "xRange", "yRange"),
			"Line", Arrays.asList("xStart", "yStart", "xStop", "yStop"));

	private static final Map<String, String> MODES_MAP = ImmutableMap.of(
			"Continuous", "Select Continuous scan mode",
			"Snake", "Select Snake scan mode",
			"Random", "Add random offsets to scan points");

	private static final Map<Shape, String[]> PROPERTIES_FOR_SHAPE = ImmutableMap.of(// use IObservableValues instead
			Shape.POINT, new String[] {},
			Shape.CENTRED_RECTANGLE, new String[] {"fastAxisPoints", "slowAxisPoints"},
			Shape.LINE, new String[] {"points"}
			);

	private static final UpdateValueStrategy POLICY_UPDATE = new UpdateValueStrategy(false,
			UpdateValueStrategy.POLICY_UPDATE);

	private static final UpdateValueStrategy POLICY_NEVER = new UpdateValueStrategy(false,
			UpdateValueStrategy.POLICY_NEVER);

	private static final int UPDATE = UpdateValueStrategy.POLICY_UPDATE;

	private static final int NO_UPDATE = UpdateValueStrategy.POLICY_NEVER;

	private static final int HALF_RANGE = 25;
	private static final int MIN_POINT_DENSITY = 1;
	private static final int MAX_POINT_DENSITY = 50;

	private PathSummary summaryHolder;

	// Composite observable values for the state of the shape selection radio buttons based on the Shape enum and
	// the IMappingScanRegionShape type. The latter is used for the controller's region select listener only
	private SelectObservableValue<Shape> selectedShapeObservable ;
	private SelectObservableValue<IMappingScanRegionShape> selectedMSRSObservable;
	private List<MutablePair<Button, IMappingScanRegionShape>> buttonToRegionShape = new ArrayList<>();

	private IObservableValue<Integer> scaleObservableValue;				// Points per side
	private IObservableValue<String> readoutObservableValue;

	private Map<String, ISWTObservableValue> mutatorObservableValues;

	private DataBindingContext viewDBC;		// for bindings valid for the view's lifetime
	private DataBindingContext regionDBC;	// For bindings that refresh with the region

	private ControlDecoration readoutTextDecoration;

	private LocalResourceManager resManager;
	private final Color armedColor;
	private final Color invalidEntryColor;
	private final Image invalidEntryImage;

	private RegionAndPathController rapController;
	private ScanManagementController smController;
	private Converters converters;
	private Composite parent;
	private final Consumer<RegionPathState> viewUpdater;
	private final IValueChangeListener<Boolean> randomOffsetListener = new IValueChangeListener<Boolean>() {
		@Override
		public void handleValueChange(ValueChangeEvent<? extends Boolean> event) {
			if (rapController.getScanRegionShape().getClass().equals(CentredRectangleMappingRegion.class)) {
				smController.updateGridModelIndex((boolean)event.getObservableValue().getValue());

				// Manually trigger the switch between GridModels
				rapController.triggerRegionUpdate(selectedMSRSObservable);
			}
		}
	};

	public DiffractionPathComposite(Composite parent, int style) {
		super(parent, style);
		this.parent = parent;
		setLayout(new GridLayout());
		GridDataFactory.fillDefaults().grab(true, false).applyTo(this);

		resManager = new LocalResourceManager(JFaceResources.getResources(), this);
		armedColor =  resManager.createColor(new RGB(255, 244, 239));
		invalidEntryColor = resManager.createColor(new RGB(255, 210, 198));
		invalidEntryImage = resManager.createImage(
				AbstractUIPlugin.imageDescriptorFromPlugin(Activator.PLUGIN_ID, "icons/exclamation-red.png"));

		selectedShapeObservable = new SelectObservableValue<>();
		selectedMSRSObservable = new SelectObservableValue<>();
		viewDBC = new DataBindingContext();
		regionDBC = new DataBindingContext();
		mutatorObservableValues = new HashMap<>();
		summaryHolder = new PathSummary();

		// create and initialise the controller to manage updates to the selected region and path
		viewUpdater = this::updateView;
		rapController = PlatformUI.getWorkbench().getService(RegionAndPathController.class);
		rapController.initialise(Optional.of(viewUpdater), Optional.empty());
		converters = new Converters(rapController, armedColor);
		smController = PlatformUI.getWorkbench().getService(ScanManagementController.class);
		smController.initialise();
	}

	/**
	 * Creates all the controls in the {@link Composite}, initialises their static and dynamic {@link Binding}s and
	 * trigger the initial draw of the plot region
	 *
	 * @return	The {@link PathSummary} object which manages display of the current scan path settings
	 */
	public PathSummary populate() {
		new Label(this, SWT.NONE).setText("Diffraction Scan Path");

		final Composite content = new Composite(this, SWT.NONE);
		GridDataFactory.fillDefaults().grab(true, true).applyTo(content);
		content.setLayout(new GridLayout(4, false));

		buildPathElementComposite(content, "Shape", SHAPES_MAP, SWT.RADIO);
		buildPointDensityElementComposite(content, "Point Density");
		buildPathElementComposite(content, "Mode(s)", MODES_MAP, SWT.CHECK);

		final Composite selectionComposite = new Composite(content, SWT.NONE);
		selectionComposite.setLayout(new GridLayout());
		GridDataFactory.fillDefaults().grab(true, true).applyTo(selectionComposite);

		final Button armedButton = new Button(selectionComposite, SWT.CHECK);
		armedButton.setToolTipText("Enable the ability to run scans by clicking on the Map view");
		armedButton.setText("Armed");
		bindArmedCheckboxWidget(armedButton);

		final StyledText summaryText = summaryHolder.getControl(selectionComposite);
		GridDataFactory.swtDefaults().align(SWT.FILL, SWT.CENTER).grab(true, false).applyTo(summaryText);

		updateScanPathBindings(rapController.getScanRegionShape(), rapController.getScanPathModel());

		rapController.updatePlotRegion();		// Plot the initial region and path
		return summaryHolder;
	}

	/**
	 * Saves the current mapping bean state using the supplied {@link String} to build a filename which decribes the
	 * scan content.
	 *
	 * @param body	The base name to be used for the reulting filename
	 */
	public void save(final String body) {
		smController.saveScan(smController.buildDescriptiveFilename(body));
	}

	/**
	 * Loads the content of the file identified by the fully qualified filename parameter into the mapping bean and
	 * refreshes the UI to dispay the changes. An update of any linked UIs will also be triggered by the controllers
	 *
	 * @param filename	The fully qualified filename of the file to be loaded
	 */
	public void load(final String filename) {
		// When load is called, the existing mapping bean has bindings from
		// 1. its region shape to selectedShapeObservable
		// 2. its scanpath to the corresponding mutator checkboxes and the summary text
		// 3. its fastaxis points count to the readout, scale and summary text
		// all under regionDBC which will need to be released along with the associated observable values.
		// This happens automatically in updateView i.e. when the RegionAndPathController's RegionSelector Listener is
		// triggered which in turn happens as a result of setting the value of selectedMSRSObservable. When this happens,
		// the new mapping bean needs to be in place as the observable values are regenerated then. Also,
		// updateRegionShapeBindings (which is called by updateView) uses the controller cached version of ScanRegion
		// Shape so this too must be up to date by then

		Optional<IMappingExperimentBean> bean = smController.loadScanMappingBean(filename);
		if (bean.isPresent()) {

			// after this point we have now received a newly loaded mapping bean which will need to be substituted for
			// the existing one so that all the configured bindings (that don't belong to regionDBC) can be used

			// First we must update the values of the regions referenced by the selectedMSRSObservable to include the
			// one from the newly loaded bean. These objects will be the beans that were created by Spring at startup
			// (until the first load takes place). Because you cannot change the options within a SelectObservable, the
			// update must be done by creating a new instance of the observable having already replaced the
			//  corresponding region shape object in the list of those created at startup with the new one.

			IMappingScanRegionShape loadedShape = bean.get().getScanDefinition().getMappingScanRegion().getRegion();
			boolean noShapeChange = selectedMSRSObservable.getValue().getClass().equals(loadedShape.getClass());

			// make a new observable using the new shape
			refreshSelectedMSRSObservable(Optional.of(loadedShape));

			// Now refresh the mapping bean provider and trigger the refreshed observable to propagate the update. For
			// the time being also need to update the grid model index.
			rapController.setMappingBean(bean.get());
			rapController.refreshFromMappingBean();
			smController.updateGridModelIndex();
			selectedMSRSObservable.setValue(loadedShape);

			// if the shape has not changed, the observable will not propagate the change automatically, so have to do
			// it manually. It does however update its selection state and selected index which is why we always have
			// to call it.
			if (noShapeChange) {
				rapController.triggerRegionUpdate(selectedMSRSObservable);
			}
			rapController.updatePlotRegion();
		}
	}

	/**
	 * Sets the state of the composite radio button observable used to set the region shape when this has happened by
	 * other means than clicking on of the buttons
	 *
	 * @param loadedShape	The new {@link IMappingScanRegionShape} to be reflected by the control
	 */
	private void refreshSelectedMSRSObservable(Optional<IMappingScanRegionShape> loadedShape) {
		if (selectedMSRSObservable != null) {
			selectedMSRSObservable.removeValueChangeListener(rapController.getRegionSelectorListener());
			selectedMSRSObservable.dispose();
		}
		selectedMSRSObservable = new SelectObservableValue<>();
		for (MutablePair<Button, IMappingScanRegionShape> pair : buttonToRegionShape) {
			if (loadedShape.isPresent() && pair.right.getClass().equals(loadedShape.get().getClass())) {
				pair.setRight(loadedShape.get());
			}
			selectedMSRSObservable.addOption(pair.right, getRadioButtonSelectionObservableValue(pair.left));
		}
		selectedMSRSObservable.addValueChangeListener(rapController.getRegionSelectorListener());
	}

	/***
	 * Builds a {@link Composite} containing a vertical set of buttons depending on the type of the passed in contentMap
	 *
	 * @param parent		The Parent composite
	 * @param title			The title of the button set
	 * @param contentMap	A {@link Map} of button name to tooltip
	 * @param buttonStyle	The type of {@link Button} to be used.
	 */
	private void buildPathElementComposite(	final Composite parent, final String title,
											final Map<String, String> contentMap,  final int buttonStyle) {
		final Composite shapesComposite = new Composite(parent, SWT.NONE);
		shapesComposite.setLayout(new GridLayout());
		GridDataFactory.fillDefaults().grab(true, true).applyTo(shapesComposite);
		new Label(shapesComposite, SWT.NONE).setText(title);

		for(Map.Entry<String, String> entry : contentMap.entrySet()) {
			final Button button = new Button(shapesComposite, buttonStyle);
			final String widgetName = entry.getKey();
			button.setToolTipText(entry.getValue());
			if (contentMap == SHAPES_MAP) {
				String iconName = String.format("icons/%s.png", widgetName.toLowerCase());
				Image img = resManager.createImage(AbstractUIPlugin.imageDescriptorFromPlugin(Activator.PLUGIN_ID, iconName));
				button.setImage(img);
				selectedShapeObservable.addOption(
						Shape.fromRegionName(widgetName), getRadioButtonSelectionObservableValue(button));
				buttonToRegionShape.add(MutablePair.of(button, converters.regionShapeForName(widgetName)));
			} else {
				button.setText(widgetName);
				bindMutatorCheckboxWidget(button, widgetName);
			}
			GridDataFactory.fillDefaults().grab(true, true).applyTo(button);
		}
		if (buttonStyle == SWT.RADIO) {
			updateRegionShapeBindings();

			// set up the trigger for the path re-ralculation process to update all affected views
			refreshSelectedMSRSObservable(Optional.empty());
		}
		else {
			viewDBC.bindValue(mutatorObservableValues.get("Random"), summaryHolder.getRandomOffsetObservableValue());
		}
	}

	/**
	 * Builds a {@link Composite} containing linked {@link Scale} and {@link Text} controls. The Scale is
	 * binned so that a mouse scroll (or PgUp/PgDn) on it switches between the min, middle and max values
	 * no matter what value it starts from
	 *
	 * @param parent	The Parent composite
	 * @param title		The {@link Composite} title
	 */
	private void buildPointDensityElementComposite(final Composite parent, final String title) {
		final Composite shapesComposite = new Composite(parent, SWT.NONE);
		shapesComposite.setLayout(new GridLayout());
		GridDataFactory.fillDefaults().grab(true, true).applyTo(shapesComposite);
		new Label(shapesComposite, SWT.NONE).setText(title);
		final Composite content = new Composite(shapesComposite, SWT.NONE);
		content.setLayout(new GridLayout(2, false));
		GridDataFactory.fillDefaults().grab(true, true).applyTo(content);

		final Scale densityScale = new Scale(content, SWT.VERTICAL);
		densityScale.setMinimum(1);
		densityScale.setMaximum(HALF_RANGE + HALF_RANGE);
		densityScale.setSelection(HALF_RANGE);
		densityScale.setIncrement(1);
		densityScale.setPageIncrement(HALF_RANGE);
		densityScale.setToolTipText("Set number of points per side of the region");
		scaleObservableValue = getScaleSelectionObservableValue(densityScale);

		GridDataFactory.fillDefaults().grab(true, true).applyTo(densityScale);
		final Text readoutText = new Text(content, SWT.BORDER);
		readoutText.setText(String.valueOf(densityScale.getSelection()));
		GridDataFactory.swtDefaults().align(SWT.FILL, SWT.CENTER).applyTo(readoutText);

		readoutTextDecoration = new ControlDecoration(readoutText, SWT.LEFT | SWT.TOP);
		readoutTextDecoration.setImage(invalidEntryImage);
		readoutTextDecoration.setDescriptionText("Please enter an integer value between 1 and 50 inclusive");
		readoutText.setToolTipText("Set number of points per side of the region");
		readoutObservableValue = getReadoutTextObservableValue(readoutText);

		bindPointDensityWidgetBehaviour(densityScale, readoutText);
	}

	/**
	 * This is triggered when a shape selection takes place to dispose of the mapping bean bindings so that
	 * they can be replaced with a new set that relate to the newly chosen shape. Thus this will be the case at startup
	 * and also if a scan is loaded and if the settings are changed by a different actor on the mapping bean.
	 *
	 * The scan path is set to the default value for the selected shape before updating the bindings for both region
	 * and path. This is done whilst the controllers region selector listener is not linked.
	 */
	private final void updateView(RegionPathState updated) {
		selectedMSRSObservable.removeValueChangeListener(rapController.getRegionSelectorListener());
		int index = updated.scanRegionShape().getName().equals(Shape.CENTRED_RECTANGLE.getMappingScanRegionName())
				? smController.getGridModelIndex()
				: 0;
		updateScanPathBindings(updated.scanRegionShape(), updated.scanPathList().get(index));
		updateRegionShapeBindings();
		selectedMSRSObservable.addValueChangeListener(rapController.getRegionSelectorListener());
	}

	/**
	 * Rewrites the bindings relating to the mapping bean's region scan path model so that the {@link Scale} and
	 * {@link Text} density controls get linked to the correct property on the correct {@link IScanPathModel} when
	 * the region shape is changed by any linked views
	 *
	 * @param newRegionValue	The updated region that has been chosen
	 * @param newPathValue		The resulting updated default scan path
	 */
	private void updateScanPathBindings(final IMappingScanRegionShape newRegionValue, final IScanPathModel newPathValue) {
		regionDBC.dispose();

		rapController.changePath(newPathValue);
		updatePathMutatorBindings(newPathValue);
		doRandomOffsetSpecialHandling();
		boolean alreadyBound = false;

		for (String propertyName : PROPERTIES_FOR_SHAPE.get(Shape.fromRegionName(newRegionValue.getName()))) {
			IObservableValue<Integer>pointsObservableValue = getMappingBeanScanPathPointsObservableValue(propertyName, newPathValue);

			if (!alreadyBound) {
				regionDBC.bindValue(readoutObservableValue, pointsObservableValue,
						validatedReadoutToPointsStrategy(),	validatedPointsToReadoutStrategy());
				regionDBC.bindValue(scaleObservableValue, pointsObservableValue,
						POLICY_UPDATE, validatedPointsToScaleStrategy());
				regionDBC.bindValue(pointsObservableValue, summaryHolder.getDensityObservableValue(),
						POLICY_UPDATE, POLICY_NEVER);
			} else {
				regionDBC.bindValue(readoutObservableValue, pointsObservableValue, validatedReadoutToPointsStrategy(),
						POLICY_NEVER);
				regionDBC.bindValue(scaleObservableValue, pointsObservableValue, POLICY_UPDATE, POLICY_NEVER);
			}
			alreadyBound = true;
		}
	}

	/**
	 * Rewrites the bindings relating to the mapping bean's region shape so that the {@link Button}s and
	 * {@link StyledText} summary controls get linked to the correct property on the correct {@link IMappingScanRegion}
	 * when the region shape is changed by any linked views
	 */
	@SuppressWarnings("unchecked")
	private void updateRegionShapeBindings() {

		IObservableValue<IMappingScanRegionShape> mbShapeObservableValue = getMappingBeanRegionShapeObservableValue();
		regionDBC.bindValue(selectedShapeObservable, mbShapeObservableValue,
				UpdateValueStrategy.create(converters.shapeToMappingRegionShape),
				UpdateValueStrategy.create(converters.mappingRegionShapeToShape));
		regionDBC.bindValue(mbShapeObservableValue, summaryHolder.getShapeObservableValue(),
				UpdateValueStrategy.create(converters.mappingRegionShapeToShape), POLICY_NEVER);

		List<IObservableValue<Double>> summaryObservableValues = summaryHolder.getShapeCoordinateObservableValues();

		List<String> fields = FIELDS_MAP.get(rapController.getScanRegionShape().getName());
		for (int index = 0; index < summaryObservableValues.size(); index++) {
			if (index < fields.size()) {
				bindFromModelToTarget(regionDBC, summaryObservableValues.get(index),
						BeanProperties.value(fields.get(index)).observe(rapController.getScanRegionShape()));
			}
		}
	}

	/**
	 * Rewrites the bindings that link the mutator checkbox controls to the appropriate properties on the mapping bean's
	 * path model
	 *
	 * @param newPathValue	The {@link IScanPathModel} currently selected on the mapping bean
	 */
	@SuppressWarnings("unchecked")
	private void updatePathMutatorBindings(final IScanPathModel newPathValue) {
		if (!newPathValue.getClass().equals(SinglePointModel.class)) {
			IObservableValue<Boolean> pathContinuousObservableValue = BeanProperties.value("continuous").observe(newPathValue);
			regionDBC.bindValue(mutatorObservableValues.get("Continuous"), pathContinuousObservableValue);

			bindFromModelToTarget(regionDBC,
					PojoProperties.value("continuous").observe(summaryHolder), pathContinuousObservableValue);
			// would have handling for random offset here were it a proper mutator instead of a separate model
		}
		if (newPathValue instanceof GridModel) {
			IObservableValue<Boolean> pathSnakeObservableValue = BeanProperties.value("snake").observe(newPathValue);
			regionDBC.bindValue(mutatorObservableValues.get("Snake"), pathSnakeObservableValue);
			bindFromModelToTarget(regionDBC, summaryHolder.getSnakeObservableValue(), pathSnakeObservableValue);
		}
	}

	/** This handling needs to exist in this form whilst the Random offset grid is not GridModel with a Random
	 *  Offset mutator applied but a separate RandomOffsetGridModel class.
	 */
	@SuppressWarnings("unchecked")
	private void doRandomOffsetSpecialHandling() {
		// Because of this, changes to the scan
		// path (when the selected region is rectangular) need to be reflected by the Random Offset checkbox.

		IObservableValue<IScanPathModel> mbPathObservableValue = getMappingBeanPathObservableValue();
		UpdateValueStrategy strategy = UpdateValueStrategy.create(converters.scanPathToRandomised)
				.setAfterGetValidator(this::changeGridModelValidator);
		regionDBC.bindValue(mutatorObservableValues.get("Random"), mbPathObservableValue,
				POLICY_NEVER, strategy);

		// In addition selection of the Random Offset checkbox needs to manually trigger a RegionSelectorListener
		// update without changing the actual shape, hence this nasty bit of code.
		mutatorObservableValues.get("Random").addValueChangeListener(randomOffsetListener);
	}

	/**
	 * Creates the static bindings that control whether the point density controls are enabled based on the selected
	 * {@link Shape}. Listeners are also added to make mouse wheeel and pgUp/pgDn event move the scale to the min, max
	 * or centre point values.
	 *
	 * @param densityScale	The number of points scale control
	 * @param readoutText	The number of points text box
	 */
	private void bindPointDensityWidgetBehaviour(final Scale densityScale, final Text readoutText) {
		viewDBC.bindValue(selectedShapeObservable, WidgetProperties.enabled().observe(densityScale),
				UpdateValueStrategy.create(converters.hideControlForPoint), POLICY_NEVER);
		viewDBC.bindValue(selectedShapeObservable, WidgetProperties.enabled().observe(readoutText),
				UpdateValueStrategy.create(converters.hideControlForPoint), POLICY_NEVER);

		densityScale.addKeyListener(new KeyListener() {
			@Override
			public void keyReleased(KeyEvent e) {
			}

			@Override
			public void keyPressed(KeyEvent e) {
				if (e.keyCode == SWT.PAGE_UP || e.keyCode == SWT.PAGE_DOWN) {
					adjustPageIncrement(densityScale, e.keyCode == SWT.PAGE_UP);
				}
			}
		});

		densityScale.addMouseWheelListener(new MouseWheelListener() {
			@Override
			public void mouseScrolled(MouseEvent e) {
				adjustPageIncrement(densityScale, e.count > 0);
			}
		});
	}

	/**
	 * Resets the paging increment of the density scale so that wherever the thumb is a page increment will move it to
	 * the min. max or middle value
	 *
	 * @param densityScale
	 * @param up
	 */
	private void adjustPageIncrement(final Scale densityScale, final boolean up) {
		int adjustment = HALF_RANGE;
		if ((up && densityScale.getSelection() > HALF_RANGE) || (!up && densityScale.getSelection() < HALF_RANGE)) {
			adjustment = Math.abs(densityScale.getSelection() - HALF_RANGE);
		}
		densityScale.setPageIncrement(adjustment);
	}

	/**
	 * Creates the ststic {@link Binding}s that control the visibility of the mutator checkbox controls based on which
	 * {@link Shape} is currently selected
	 * @param button		The {@link Button} to be bound
	 * @param widgetName	The name of the {@link Button}
	 */
	private void bindMutatorCheckboxWidget(final Button button, final String widgetName) {
		ISWTObservableValue buttonCheckedObservable = WidgetProperties.selection().observe(button);
		mutatorObservableValues.put(widgetName, buttonCheckedObservable);
		@SuppressWarnings("unchecked")
		IObservableValue<Shape> disableButtonIObservableValue = WidgetProperties.visible().observe(button);
		IConverter converter = !widgetName.equalsIgnoreCase("continuous")
				? converters.hideControlForPointOrLine
				: converters.hideControlForPoint;

		viewDBC.bindValue(selectedShapeObservable, disableButtonIObservableValue,
				UpdateValueStrategy.create(converter), POLICY_NEVER);
	}

	/**
	 * Creates the static bindings from the armed control. It is linked to the {@link CtrlClickToScanHandler} which
	 * initiates scans using the current mapping bean settings when triggered. Additionally cosmetic UI bindings are
	 * made so that it is easily apparent that armed mode is active.
	 *
	 * @param armedButton	The armed checkbox {@link Button}
	 */
	@SuppressWarnings("unchecked")
	private void bindArmedCheckboxWidget(final Button armedButton) {
		viewDBC.bindValue(WidgetProperties.selection().observe(armedButton),
				smController.getClickToScanArmedObservableValue());

		IPlottingService plottingService = rapController.getService(IPlottingService.class);
		IPlottingSystem<Object> mapPlottingSystem = plottingService.getPlottingSystem("Map");
		Map<Object, String> sourceToColourBoundField = ImmutableMap.of(
				mapPlottingSystem, "titleColor",
				mapPlottingSystem.getAxes().get(0), "foregroundColor",
				mapPlottingSystem.getAxes().get(1), "foregroundColor");
		for (Map.Entry<Object, String> entry : sourceToColourBoundField.entrySet()) {
			viewDBC.bindValue(WidgetProperties.selection().observe(armedButton),
					PojoProperties.value(entry.getValue()).observe(entry.getKey()),
					UpdateValueStrategy.create(converters.armedStatusToTextColour), POLICY_NEVER);
		}
		viewDBC.bindValue(WidgetProperties.selection().observe(armedButton),
				PojoProperties.value("title").observe(mapPlottingSystem),
				UpdateValueStrategy.create(converters.armedStatusToTextTitleText), POLICY_NEVER);
		viewDBC.bindValue(WidgetProperties.selection().observe(armedButton),
				PojoProperties.value("background").observe(parent),
				UpdateValueStrategy.create(converters.armedStatusToBackgroundColour), POLICY_NEVER);
	}

	private UpdateValueStrategy validatedReadoutToPointsStrategy() {
		return UpdateValueStrategy.create(converters.stringToInteger)
				.setAfterGetValidator(this::densityReadoutValidator);
	}

	private UpdateValueStrategy validatedPointsToReadoutStrategy() {
		return UpdateValueStrategy.create(converters.integerToString)
				.setAfterConvertValidator(this::densityReadoutValidator);
	}

	private UpdateValueStrategy validatedPointsToScaleStrategy() {
		return new UpdateValueStrategy(UPDATE).setAfterConvertValidator(this::densityRangeValidator);
	}

	private IStatus changeGridModelValidator(Object stringContent) {
		return rapController.getScanRegionShape().getName().equalsIgnoreCase(Shape.CENTRED_RECTANGLE.getMappingScanRegionName())
				? ValidationStatus.ok()
				: ValidationStatus.error("");
	}

	/**
	 * Validator for use with the point density {@link Text} control; it will accept numeric textual values between the
	 * specified min and max values
	 *
	 * @param stringContent		The {@link String} to be checked
	 * @return					Success if the value is  numeric and  between the required min and max otherwise error
	 */
	private IStatus densityReadoutValidator(Object stringContent) {
		return densityRangeValidator(Ints.tryParse((String)stringContent));
	}

	/**
	 * Validator for use with the point density {@link Scale} control; it will accept numeric values between the
	 * specified min and max values
	 *
	 * @param integerContent	The {@link Integer} value to be checked
	 * @return					Success if the value is  numeric and  between the required min and max otherwise error
	 */
	private IStatus densityRangeValidator(Object integerContent) {
		IStatus result = ValidationStatus.error("");
		Integer value = (Integer)integerContent;
		Control readoutText = readoutTextDecoration.getControl();

		if (value != null && value.intValue() >=  MIN_POINT_DENSITY && value.intValue() <= MAX_POINT_DENSITY) {
			readoutText.setBackground(readoutText.getDisplay().getSystemColor(SWT.COLOR_WHITE));
			readoutTextDecoration.hide();
			result = ValidationStatus.ok();
		} else {
			readoutText.setBackground(invalidEntryColor);
			readoutTextDecoration.show();
			readoutTextDecoration.showHoverText(readoutTextDecoration.getDescriptionText());
		}
		return result;
	}

	@SuppressWarnings("unchecked")
	private IObservableValue<Boolean> getRadioButtonSelectionObservableValue(final Button button) {
		return WidgetProperties.selection().observe(button);
	}

	@SuppressWarnings("unchecked")
	private IObservableValue<Integer> getScaleSelectionObservableValue(final Scale scale) {
		return WidgetProperties.selection().observe(scale);
	}

	@SuppressWarnings("unchecked")
	private IObservableValue<String> getReadoutTextObservableValue(final Text text) {
		return  WidgetProperties.text(SWT.Modify).observe(text);
	}

	@SuppressWarnings("unchecked")
	private IObservableValue<Integer> getMappingBeanScanPathPointsObservableValue(final String propertyName,
			final IScanPathModel pathValue) {
		return BeanProperties.value(propertyName).observe(pathValue);
	}

	@SuppressWarnings("unchecked")
	private IObservableValue<IMappingScanRegionShape> getMappingBeanRegionShapeObservableValue() {
		return BeanProperties.value("region").observe(rapController.getScanRegionFromBean());
	}

	@SuppressWarnings("unchecked")
	private IObservableValue<IScanPathModel> getMappingBeanPathObservableValue() {
		return BeanProperties.value("scanPath").observe(rapController.getScanRegionFromBean());
	}

	private Binding bindFromTargetToModel(final DataBindingContext dbc, final IObservableValue<?> target, final IObservableValue<?> model) {
		return dbc.bindValue(target, model, new UpdateValueStrategy(UPDATE), new UpdateValueStrategy(NO_UPDATE));
	}

	private Binding bindFromModelToTarget(final DataBindingContext dbc, final IObservableValue<?> target, final IObservableValue<?> model) {
		return dbc.bindValue(target, model, new UpdateValueStrategy(NO_UPDATE), new UpdateValueStrategy(UPDATE));
	}

	@SuppressWarnings("unchecked")
	@Override
	public void dispose() {
		rapController.detachViewUpdater(viewUpdater);
		regionDBC.dispose();
		regionDBC.getBindings().forEach(o -> regionDBC.removeBinding((Binding)o));
		regionDBC = null;
		viewDBC.dispose();
		viewDBC.getBindings().forEach(o -> viewDBC.removeBinding((Binding)o));
		viewDBC = null;
		summaryHolder.dispose();
		summaryHolder = null;
		scaleObservableValue.dispose();
		scaleObservableValue = null;
		readoutObservableValue.dispose();
		readoutObservableValue = null;
		mutatorObservableValues.values().forEach(o -> {o.dispose(); o = null;});
		mutatorObservableValues.clear();
		mutatorObservableValues = null;
		selectedMSRSObservable.removeValueChangeListener(rapController.getRegionSelectorListener());
		selectedMSRSObservable.dispose();
		selectedMSRSObservable = null;
		selectedShapeObservable.dispose();
		selectedShapeObservable = null;
		resManager.dispose();
		resManager = null;
		readoutTextDecoration.dispose();
		readoutTextDecoration = null;
	}

}
