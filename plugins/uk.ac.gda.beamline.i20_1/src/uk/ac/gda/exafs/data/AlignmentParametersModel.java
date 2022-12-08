/*-
 * Copyright © 2012 Diamond Light Source Ltd.
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

package uk.ac.gda.exafs.data;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.gson.annotations.Expose;

import gda.jython.InterfaceProvider;
import gda.util.exafs.AbsorptionEdge;
import gda.util.exafs.Element;
import uk.ac.gda.beans.ObservableModel;
import uk.ac.gda.ede.data.AlignmentParametersBean;
import uk.ac.gda.ede.data.AlignmentParametersCalculator;
import uk.ac.gda.ede.data.ClientConfig;

public class AlignmentParametersModel extends ObservableModel implements Serializable {

	private static final Logger logger = LoggerFactory.getLogger(AlignmentParametersModel.class);

	public static final AlignmentParametersModel INSTANCE = new AlignmentParametersModel();

	private boolean useAtn45 = true;

	public enum QValue {
		Q_0_8(0.8),
		Q_1_0(1.0),
		Q_1_2(1.2);
		private double value;
		private QValue(double value) {
			this.value = value;
		}
		public double getQValue() {
			return value;
		}
	}

	// inputs
	public static final String CRYSTAL_TYPE_PROP_NAME = "crystalType";
	@Expose
	private CrystalType crystalType;

	public static final String CRYSTAL_CUT_PROP_NAME = "crystalCut";
	@Expose
	private CrystalCut crystalCut;

	public static final String Q_PROP_NAME = "q";
	@Expose
	private QValue q = null;

	public static final String ELEMENT_EDGE_PROP_NAME = "edge";
	private AbsorptionEdge edge = null; // for the moment, this should match element and edge
	@Expose
	private String absorptionEdgeString;

	public static final String ELEMENT_PROP_NAME = "element";
	private Element element = null;

	@Expose
	private String elementSymbol;

	public static final String ELEMENT_ENERGY_PROP_NAME = "energy";

	private static final String POWER_PROP_NAME = "power";
	private Double power = null; // W

	public static final String ELEMENT_EDGES_NAMES_PROP_NAME = "elementEdges";
	public static final String SUGGESTED_PARAMETERS_PROP_KEY = "alignmentSuggestedParameters";

	private AlignmentParametersBean alignmentSuggestedParameters;

	private static boolean parametersLoaded = false;

	private static final String ALIGNMENT_PARAMETERS_DATA_STORE_KEY = "ALIGNMENT_PARAMETERS_DATA_STORE_KEY";

	public enum CrystalType {
		Bragg, Laue;
		public static final String UI_LABEL = "Crystal type:";
	}

	private enum Edge{K, L1, L2, L3}

	public enum CrystalCut {
		// See requirement spec for assigned values
		Si111(5.7 * 1000, 14 * 1000),
		Si311(7 * 1000, 26 * 1000);

		private final double min;
		private final double max;

		public static final String UI_LABEL = "Crystal cut:";

		private final Map<Element, List<String>> elementsInEnergyRange;

		private CrystalCut(double min, double max) {
			this.min = min;
			this.max = max;
			elementsInEnergyRange = createElementList();
		}

		private Map<Element, List<String>> createElementList() {
			Map<Element, List<String>> includedElements = new TreeMap<Element, List<String>>(new Comparator<Element>() {
				@Override
				public int compare(Element o1, Element o2) {
					return (o1.getName().compareTo(o2.getName()));
				}
			});
			Collection<Element> elements = Element.getAllElements();
			for (Element element: elements) {
				List<String> edges = element.getAllowedEdges();
				for (Edge edge : Edge.values()) {
					if (edges.contains(edge.name())) {
						if (min <= element.getEdgeEnergy(edge.name()) & max >= element.getEdgeEnergy(edge.name())) {
							if (!includedElements.containsKey(element)) {
								includedElements.put(element, new ArrayList<String>());
							}
							includedElements.get(element).add(edge.name());
						}
					}
				}
			}
			return includedElements;
		}

		public  Map<Element, List<String>> getElementsInEnergyRange() {
			return elementsInEnergyRange;
		}

		public double getMax() {
			return max;
		}

		public double getMin() {
			return min;
		}
	}
	private final PropertyChangeListener listener = new PropertyChangeListener() {
		List<String> paramsToSave = Arrays.asList(CRYSTAL_TYPE_PROP_NAME, CRYSTAL_CUT_PROP_NAME, Q_PROP_NAME, ELEMENT_EDGE_PROP_NAME, ELEMENT_PROP_NAME);
		@Override
		public void propertyChange(PropertyChangeEvent evt) {
			String eventPropertyName = evt.getPropertyName();
			if(evt.getNewValue() != null && !eventPropertyName.equals(SUGGESTED_PARAMETERS_PROP_KEY)) {
				getCalculations();
			}
			if ( paramsToSave.contains(eventPropertyName) ) {
				saveAlignmentParametersToStore();
			}
		}
	};

	protected AlignmentParametersModel() {
		this.setCrystalType(CrystalType.Bragg);
		this.setCrystalCut(CrystalCut.Si111);
		this.setQ(QValue.Q_0_8);
		this.addPropertyChangeListener(listener);
		DetectorModel.INSTANCE.addPropertyChangeListener(DetectorModel.DETECTOR_CONNECTED_PROP_NAME, listener);
		getCalculations();
	}

	public CrystalType getCrystalType() {
		return crystalType;
	}

	public void setCrystalType(CrystalType crystalType) {
		this.firePropertyChange(CRYSTAL_TYPE_PROP_NAME, this.crystalType, this.crystalType = crystalType);
	}

	public CrystalCut getCrystalCut() {
		return crystalCut;
	}

	public void setCrystalCut(CrystalCut crystalCut) {
		Element current = element;
		this.firePropertyChange(ELEMENT_PROP_NAME, element, element = null);
		this.firePropertyChange(CRYSTAL_CUT_PROP_NAME, this.crystalCut, this.crystalCut = crystalCut);
		this.firePropertyChange(ELEMENTS_IN_ENERGY_RANGE_PROP_NAME, null, getElementsInEnergyRange());
		if (current == null || !this.crystalCut.getElementsInEnergyRange().keySet().contains(current)) {
			this.setElement(this.crystalCut.getElementsInEnergyRange().keySet().iterator().next());
		} else {
			this.setElement(current);
		}
	}

	public static final String ELEMENTS_IN_ENERGY_RANGE_PROP_NAME = "elementsInEnergyRange";
	public  Set<Element> getElementsInEnergyRange() {
		if (crystalCut == null) {
			return null;
		}
		return crystalCut.getElementsInEnergyRange().keySet();
	}

	public Element getElement() {
		return element;
	}

	public void setElement(Element element) {
		AbsorptionEdge currentEdge = edge;
		this.firePropertyChange(ELEMENT_PROP_NAME, null, this.element = element);
		this.firePropertyChange(ELEMENT_EDGES_NAMES_PROP_NAME, null, getElementEdges());
		List<String> elementNames = crystalCut.getElementsInEnergyRange().get(element);
		if (currentEdge == null || !elementNames.contains(currentEdge.getEdgeType())) {
			this.setEdge(element.getEdge(elementNames.iterator().next()));
		} else {
			this.setEdge(element.getEdge(currentEdge.getEdgeType()));
		}
	}

	public AbsorptionEdge getEdge() {
		return edge;
	}

	public void setEdge(AbsorptionEdge edge) {
		this.firePropertyChange(ELEMENT_EDGE_PROP_NAME, this.edge, this.edge = edge);
		this.firePropertyChange(ELEMENT_ENERGY_PROP_NAME, null, getEnergy());
	}

	public  List<String> getElementEdges() {
		if (element == null | crystalCut == null) {
			return null;
		}
		return crystalCut.getElementsInEnergyRange().get(element);
	}

	public QValue getQ() {
		return q;
	}

	public void setQ(QValue q) {
		this.firePropertyChange(Q_PROP_NAME, this.q, this.q = q);
	}

	public double getEnergy() {
		if (element != null & edge != null) {
			return element.getEdgeEnergy(edge.getEdgeType());
		}
		return 0.0;
	}

	public Double getPower() {
		return power;
	}

	public void setPower(Double power) {
		this.firePropertyChange(POWER_PROP_NAME, this.power, this.power = power);
	}

	private void getCalculations() {
		if (DetectorModel.INSTANCE.getCurrentDetector() == null || edge == null || element == null) {
			this.firePropertyChange(SUGGESTED_PARAMETERS_PROP_KEY, alignmentSuggestedParameters, null);
			return;
		}
		try {
			AlignmentParametersBean bean = new AlignmentParametersBean(crystalType.name(), crystalCut.name(), q.getQValue(), DetectorModel.INSTANCE.getCurrentDetector().getName(), edge);
			AlignmentParametersCalculator parametersCalculator = new AlignmentParametersCalculator(bean);
			double detectorDistanceMm = (double)ScannableSetup.DETECTOR_DISTANCE.getScannable().getPosition();
			parametersCalculator.setRealDetectorDistance(detectorDistanceMm*0.001);
			parametersCalculator.setUseAtn45(useAtn45);
			parametersCalculator.calculateParameters();
			AlignmentParametersBean result = parametersCalculator.getParameterBean();

			// Update the bean on the server
			String jsonString = AlignmentParametersBean.toJson(result);
			String className = AlignmentParametersBean.class.getSimpleName();
			String importString = ModelHelpers.getJythonImportCommand(AlignmentParametersBean.class);
			InterfaceProvider.getCommandRunner().runCommand(importString + ClientConfig.ALIGNMENT_PARAMETERS_RESULT_BEAN_NAME + " = "+className+".fromJson(\'"+jsonString+"\'); ");

			this.firePropertyChange(SUGGESTED_PARAMETERS_PROP_KEY, alignmentSuggestedParameters, alignmentSuggestedParameters = result);
		} catch (Exception e) {
			this.firePropertyChange(SUGGESTED_PARAMETERS_PROP_KEY, alignmentSuggestedParameters, null);
			logger.error("Problem running power calculation", e);
		}
	}

	public AlignmentParametersBean getAlignmentSuggestedParameters() {
		return alignmentSuggestedParameters;
	}

	/**
	 * Duplicate the model parameters from another object.
	 * @param model
	 * @since 11/4/2016
	 */
	public void setFromModel( AlignmentParametersModel model ) {
		if ( model == null )
			return;

		crystalType = model.getCrystalType();
		crystalCut = model.getCrystalCut();
		q = model.getQ();

		if ( model.absorptionEdgeString != null ) {
			edge = new AbsorptionEdge(model.absorptionEdgeString);
		}

		if ( model.elementSymbol != null ) {
			element = Element.getElement(model.elementSymbol);
		}
		setCrystalType( crystalType );
		setCrystalCut( crystalCut );
		setElement( element );
		setEdge( edge );
	}

	/**
	 * Save AlignmentParameters to preference store.
	 * @since 8/4/2016
	 */
	public void saveAlignmentParametersToStore() {
		if ( parametersLoaded == true ) {
			if ( element != null )
				elementSymbol = element.getSymbol();

			if ( edge != null )
				absorptionEdgeString = edge.toString();

			EdeDataStore.INSTANCE.getPreferenceDataStore().saveConfiguration(ALIGNMENT_PARAMETERS_DATA_STORE_KEY, this);
		}
	}

	/**
	 * Load AlignmentParameters from preference store
	 * @since 8/4/2016
	 */
	public void loadAlignmentParametersFromStore() {
		AlignmentParametersModel paramModel = EdeDataStore.INSTANCE.getPreferenceDataStore().loadConfiguration(ALIGNMENT_PARAMETERS_DATA_STORE_KEY, AlignmentParametersModel.class);
		setFromModel( paramModel );
		parametersLoaded = true;
	}

	public void setUseAtn45(boolean useAtn45) {
		this.useAtn45 = useAtn45;
	}

	public boolean isUseAtn45() {
		return useAtn45;
	}
}
