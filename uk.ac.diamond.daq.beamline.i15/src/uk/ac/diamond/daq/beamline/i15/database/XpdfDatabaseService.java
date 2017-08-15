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


public class XpdfDatabaseService implements ISampleDescriptionService {
	private static final Logger logger = LoggerFactory.getLogger(XpdfDatabaseService.class);

	private static final String XPDF_URL_PROP = "xpdf.server.ispyb.connector.url";
	private static final String XPDF_USER_PROP = "xpdf.server.ispyb.connector.user";
	private static final String XPDF_PASSWORD_PROP = "xpdf.server.ispyb.connector.password";
	private static final String XPDF_DATABASE_PROP = "xpdf.server.ispyb.connector.database";

	private static IspybXpdfFactoryService factoryService;

	@Override
	public Map<Long, String> getSampleIdNames(String proposalCode, long proposalNumber) {

		String url = LocalProperties.get(XPDF_URL_PROP);
		Optional<String> username = Optional.ofNullable(LocalProperties.get(XPDF_USER_PROP));
		Optional<String> password = Optional.ofNullable(LocalProperties.get(XPDF_PASSWORD_PROP));
		Optional<String> schema = Optional.of(Schema.convert(LocalProperties.get(XPDF_DATABASE_PROP)).toString());

		try {
			IspybXpdfApi api = factoryService.buildIspybApi(url, username, password, schema);

			List<Sample> samples = api.retrieveSamplesAssignedForProposal(proposalCode, proposalNumber);

			return samples.stream().collect(Collectors.toMap(Sample::getSampleId, Sample::getSampleName));

		} catch (SQLException e) {
			logger.error("Failed to access IspyB", e);
			throw new RuntimeException(e);
		}
	}

	public static synchronized void setFactoryService(IspybXpdfFactoryService factoryService) {
		XpdfDatabaseService.factoryService = factoryService;
		logger.info("Set IspybXpdfFactoryService to {}", factoryService);
	}

}
