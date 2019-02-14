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

package uk.ac.gda.beamline.i20_1.utils;

import java.util.HashMap;

import javax.measure.quantity.Quantity;
import javax.measure.unit.Unit;

import org.jscience.physics.amount.Amount;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.factory.ConfigurableBase;
import gda.factory.FactoryException;
import gda.factory.Findable;
import gda.util.QuantityFactory;
import gda.util.converters.LookupTableConverterHolder;

/**
 * Holds an array of lookup tables to map a series of hardware positions to a single value, such as beamline energy.
 * <p>
 * When given a value, returns a list of the positions the listed hardware should move to using the interpolation inside
 * the lookup tables.
 * <p>
 * Does not operate any hardware.
 */
public class LookupTablesBean extends ConfigurableBase implements Findable {

	static final Logger logger = LoggerFactory.getLogger(LookupTablesBean.class);

	private HashMap<String, LookupTableConverterHolder> lookupTables = new HashMap<String, LookupTableConverterHolder>();

	private Unit<?> userUnit;

	private String initialUserUnitString;

	private String name;

	@Override
	public void configure() throws FactoryException {
		if (userUnit == null && initialUserUnitString != null) {
			userUnit = QuantityFactory.createUnitFromString(initialUserUnitString);
		}
		setConfigured(true);
	}

	@Override
	public void setName(String name) {
		this.name = name;
	}

	@Override
	public String getName() {
		return name;
	}

	public HashMap<String, Double> getPositionsForEnergy(Double energy) {
		HashMap<String, Double> returnValues = new HashMap<String, Double>();
		Amount<? extends Quantity> target = QuantityFactory.createFromObject(energy, userUnit);
		for (String tableName : lookupTables.keySet()) {
			try {
				LookupTableConverterHolder table = lookupTables.get(tableName);
				Amount<? extends Quantity> sourceQuantity = table.toSource(target);
				returnValues.put(tableName, sourceQuantity.getEstimatedValue());
			} catch (Exception e) {
				logger.error("Exception while looking up value for " + tableName, e);
			}
		}
		return returnValues;
	}

	public HashMap<String, LookupTableConverterHolder> getLookupTables() {
		return lookupTables;
	}

	public void setLookupTables(HashMap<String, LookupTableConverterHolder> lookupTables) {
		this.lookupTables = lookupTables;
	}

	public Unit<?> getUserUnit() {
		return userUnit;
	}

	public void setUserUnit(Unit<?> userUnit) {
		this.userUnit = userUnit;
	}

	public String getInitialUserUnitString() {
		return initialUserUnitString;
	}

	public void setInitialUserUnitString(String initialUserUnitString) {
		this.initialUserUnitString = initialUserUnitString;
	}
}
