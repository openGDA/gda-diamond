/*-
 * Copyright © 2017 Diamond Light Source Ltd.
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

package uk.ac.diamond.daq.beamline.i15.database;

import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

import org.eclipse.scanning.api.database.ISampleDescriptionService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import uk.ac.diamond.ispyb.api.IspybXpdfApi;
import uk.ac.diamond.ispyb.api.IspybXpdfFactoryService;
import uk.ac.diamond.ispyb.api.Sample;
import uk.ac.diamond.ispyb.api.Schema;

/**
 * Class to provide a ISampleDescriptionService as a OSGi service it uses IspyB database.
 *
 * @author James Mudd
 */
public class XpdfDatabaseService implements ISampleDescriptionService {
	private static final Logger logger = LoggerFactory.getLogger(XpdfDatabaseService.class);

	private static final String XPDF_URL_PROP = "xpdf.server.ispyb.connector.url";
	private static final String XPDF_USER_PROP = "xpdf.server.ispyb.connector.user";
	private static final String XPDF_PASSWORD_PROP = "xpdf.server.ispyb.connector.password";
	private static final String XPDF_DATABASE_PROP = "xpdf.server.ispyb.connector.database";

	private static IspybXpdfFactoryService factoryService;

	private IspybXpdfApi api;

	@Override
	public synchronized Map<Long, String> getSampleIdNames(String proposalCode, long proposalNumber) {
		if (proposalCode.length() > 3) {
			throw new IllegalArgumentException("proposalCode mush be <=3 characters eg 'cm'");
		}

		if (api == null) {
			setupApi();
		}

		// Access the DB
		List<Sample> samples = api.retrieveSamplesAssignedForProposal(proposalCode, proposalNumber);

		// Transform to the required map
		return samples.stream().collect(Collectors.toMap(Sample::getSampleId, Sample::getSampleName));
	}

	private void setupApi() {
		String url = getUrl();
		Optional<String> username = getUsername();
		Optional<String> password = getPassword();
		Optional<String> database = getDatabase();

		try {
			api = factoryService.buildIspybApi(url, username, password, database);
		} catch (SQLException e) {
			logger.error("Failed to access IspyB", e);
			throw new RuntimeException(e);
		}
	}

	private String getUrl() {
		return LocalProperties.get(XPDF_URL_PROP);
	}

	/**
	 * The MariaDB hosting IspyB host several other databases see
	 * <a href="http://confluence.diamond.ac.uk/display/SCI/Database+Systems">Database Systems</a>
	 *
	 * @return Database name
	 */
	private Optional<String> getDatabase() {
		return Optional.of(Schema.convert(LocalProperties.get(XPDF_DATABASE_PROP)).toString());
	}

	private Optional<String> getPassword() {
		// If the password contains commas it will be split into a list which is not what is wanted here so join it
		// again.
		String password = String.join(",", LocalProperties.getStringArray(XPDF_PASSWORD_PROP));
		return Optional.ofNullable(password);
	}

	private Optional<String> getUsername() {
		return Optional.ofNullable(LocalProperties.get(XPDF_USER_PROP));
	}

	public static synchronized void setFactoryService(IspybXpdfFactoryService factoryService) {
		XpdfDatabaseService.factoryService = factoryService;
		logger.info("Set IspybXpdfFactoryService to {}", factoryService);
	}

}
