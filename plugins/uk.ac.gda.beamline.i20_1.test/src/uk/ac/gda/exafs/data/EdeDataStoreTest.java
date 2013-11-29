/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;

import org.apache.commons.configuration.ConfigurationException;
import org.apache.commons.configuration.PropertiesConfiguration;
import org.eclipse.core.databinding.observable.list.WritableList;
import org.junit.Test;

import uk.ac.gda.exafs.ui.data.experiment.ExperimentModelHolder;
import uk.ac.gda.exafs.ui.data.experiment.TimingGroupUIModel;
import uk.ac.gda.exafs.ui.data.experiment.ExperimentTimingDataModel.ExperimentUnit;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import de.jaret.util.ui.timebars.model.DefaultTimeBarRowModel;

public class EdeDataStoreTest {

	@Test
	public void jsonTest() throws IOException {
		Path tempFile = Files.createTempFile(null, null);
		final GsonBuilder gsonBuilder = new GsonBuilder();
		final PropertiesConfiguration configuration = new PropertiesConfiguration();
		configuration.setDelimiterParsingDisabled(true);
		final File file = tempFile.toFile();
		configuration.setFile(file);
		RealmTester.exerciseCurrent(new Runnable() {
			@Override
			public void run() {
				WritableList groupList = new WritableList(new ArrayList<TimingGroupUIModel>(), TimingGroupUIModel.class);
				TimingGroupUIModel group = new TimingGroupUIModel(new DefaultTimeBarRowModel(), ExperimentUnit.SEC, ExperimentModelHolder.INSTANCE.getLinerExperimentModel());
				group.setTimes(0.0, 1000.0);
				group.setNumberOfSpectrum(100);
				group.setTimePerSpectrum(10);

				groupList.add(group);
				Gson gson = gsonBuilder.excludeFieldsWithoutExposeAnnotation().create();
				configuration.setProperty("test", gson.toJson(groupList));
				try {
					configuration.save();
				} catch (ConfigurationException e) {
					assertFalse(true); 
				}
			}
		});
		final PropertiesConfiguration readConfiguration = new PropertiesConfiguration();
		readConfiguration.setDelimiterParsingDisabled(true);
		readConfiguration.setFile(file);
		try {
			readConfiguration.load();
			Gson gson = gsonBuilder.excludeFieldsWithoutExposeAnnotation().create();
			TimingGroupUIModel[] test = gson.fromJson(readConfiguration.getString("test"), TimingGroupUIModel[].class);
			assertTrue(test.length == 1);
			assertTrue(test[0].getEndTime() == 1000.0);
		} catch (ConfigurationException e) {
			assertFalse(true); 
		}
		
	}
}
