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

package uk.ac.gda.exafs.data;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Properties;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.python.core.PyObject;
import org.python.util.PythonInterpreter;

import gda.TestHelpers;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.factory.Factory;
import gda.factory.Finder;
import gda.scan.EdeTestBase;
import gda.util.exafs.AbsorptionEdge;
import gda.util.exafs.Element;
import uk.ac.gda.ede.data.AlignmentParametersBean;
import uk.ac.gda.ede.data.AlignmentParametersCalculator;
import uk.ac.gda.exafs.data.AlignmentParametersModel.CrystalCut;
import uk.ac.gda.exafs.data.AlignmentParametersModel.CrystalType;
import uk.ac.gda.exafs.data.AlignmentParametersModel.QValue;


public class AlignmentParametersCalculatorTest {

	private String ALIGNMENT_PARAMETERS_INPUT_BEAN_NAME = "inputBean";
	private Scannable me2Position;
	private Scannable detZPosition;

	private static PythonInterpreter interp;
	private final double accuracy = 1e-6;

	private double minEnergy = 6500;
	private double maxEnergy = 20500;
	private double energyStep = 100;

	@BeforeClass
	public static void preparePythonInterpreter() {

		// This technique taken from AbstractJythonTest
		Properties postProperties = new Properties();
		postProperties.put("python.import.site", "false");
		PythonInterpreter.initialize(System.getProperties(), postProperties, new String[0]);

		interp = new PythonInterpreter();
		interp.exec("from uk.ac.gda.ede.data import AlignmentParametersBean;");
		interp.exec("import sys\nsys.path.append('"+getScriptDir()+"')"); // add i20-1's script directory to the path
		interp.exec("from alignment import alignment_parameters;"); // import alignment_parameters script
	}

	private static String getScriptDir() {
		// Get path to i20-1 scripts directory
		Path scriptsDir = Paths.get("").toAbsolutePath().getParent().resolve("i20-1/scripts");
		assertTrue("i20-1 scripts directory not found", Files.exists(scriptsDir));
		return scriptsDir.toString();
	}

	@Before
	public void prepare() throws Exception {
		TestHelpers.setUpTest(AlignmentParametersCalculatorTest.class, "test", false);
		CurrentRealm realm = new CurrentRealm();
		CurrentRealm.setDefault(realm);

		me2Position= EdeTestBase.createMotor("me2_y_positioner", 0);
		detZPosition = EdeTestBase.createMotor("det_z", 17.6);

		setupFinder();
	}

	private void setupFinder() {
		final Factory factory = TestHelpers.createTestFactory();
		factory.addFindable(me2Position);
		factory.addFindable(detZPosition);
		Finder.addFactory(factory);
	}

	private AlignmentParametersBean getBean() {
		double edgeEnergy = Element.getElement("Fe").getEdgeEnergy("K");
		return new AlignmentParametersBean(CrystalType.Bragg.name(), CrystalCut.Si111.name(), QValue.Q_0_8.getQValue(), "xh",
				new AbsorptionEdge("Fe", "K", edgeEnergy));
	}

	private AlignmentParametersBean getBean(double energy, CrystalCut crystalCut, QValue qvalue) {
		return new AlignmentParametersBean(CrystalType.Bragg.name(), crystalCut.name(), qvalue.getQValue(), "xh",
				new AbsorptionEdge("Fe", "K", energy));
	}

	private AlignmentParametersBean calculateBeanInPython(AlignmentParametersBean inputBean) {
		// Make json serialized string of the the input parameters
		String jsonString = inputBean.toJson();
		interp.exec(ALIGNMENT_PARAMETERS_INPUT_BEAN_NAME + " = AlignmentParametersBean.fromJson(\'"+jsonString+"\'); "); // set the input params using json string
		PyObject func =  interp.eval("alignment_parameters.calc_parameters(" + ALIGNMENT_PARAMETERS_INPUT_BEAN_NAME + ")"); // calculate the parameters
		AlignmentParametersBean calculatedBean = (AlignmentParametersBean) func.__tojava__(AlignmentParametersBean.class); // get results back to java
		return calculatedBean;
	}

	private AlignmentParametersCalculator getParametersCalculator(AlignmentParametersBean bean) throws DeviceException {
		AlignmentParametersCalculator calculator = new AlignmentParametersCalculator(bean);
		calculator.setRealDetectorDistance(0.001 * (double) detZPosition.getPosition());
		boolean inBeam = me2Position.getPosition().toString().equals("In");
		calculator.setMe2InBean(inBeam);
		return calculator;
	}

	@Test
	public void testPythonInterp() throws DeviceException {
		AlignmentParametersBean originalBean = getBean();
		AlignmentParametersBean calculatedBean = calculateBeanInPython(originalBean);
		testBean(originalBean, calculatedBean);
	}

	@Test
	public void testSi111() throws DeviceException {
		testEnergies(CrystalCut.Si111, QValue.Q_0_8);
		testEnergies(CrystalCut.Si111, QValue.Q_1_0);
		testEnergies(CrystalCut.Si111, QValue.Q_1_2);
	}

	@Test
	public void testSi311() throws DeviceException {
		testEnergies(CrystalCut.Si311, QValue.Q_0_8);
		testEnergies(CrystalCut.Si311, QValue.Q_1_0);
		testEnergies(CrystalCut.Si311, QValue.Q_1_2);
	}

	/** Json string of Jython calculation result that should be produced by testBenchMarkFromJython */
	private final String benchmarkJython = "{\"crystalType\":\"Bragg\",\"crystalCut\":\"Si111\",\"q\":0.8,\"detector\":\"xh\",\"edge\":{\"elementSymbol\":\"Fe\",\"edgeType\":\"K\",\"energy\":7112.0},\"polychromatorLength\":250.0,\"sourceToPolyDistance\":45.1,\"wigglerGap\":18.5,\"primarySlitGap\":1.5408932065219476,\"me1stripe\":\"Rhodium\",\"me2stripe\":\"Silicon\",\"me2Pitch\":3.5,\"polyBend1\":2.8949327868938743,\"polyBend2\":3.862937884783797,\"braggAngle\":16.139510802142418,\"arm2Theta\":32.279021604284836,\"detectorDistance\":0.5894009963096586,\"detectorHeight\":-4.9056,\"attenuatorPositions\":[\"pC 0.1mm\",\"Empty\",\"Empty\"],\"energyBandwidth\":1048.5182059597207,\"power\":0.0,\"readBackEnergyBadwidth\":1048.5182059597207}";

	@Test
	public void testBenchmarkFromJython() {
		AlignmentParametersBean jythonCalculatedBean = calculateBeanInPython(getBean());
		String jsonString = jythonCalculatedBean.toJson();
		System.out.println(jsonString);
		assertEquals(benchmarkJython.trim(), jsonString.trim());
	}

	@Test
	public void testBenchmarkFromJava() throws DeviceException {
		AlignmentParametersBean bean = getBean();
		testBean(bean, AlignmentParametersBean.fromJson(benchmarkJython));
	}

	/**
	 * Loop over range of energies, compare calculation in java with same calculation using python script
	 * @param crystalCut
	 * @param qvalue
	 * @throws DeviceException
	 */
	public void testEnergies(CrystalCut crystalCut, QValue qvalue) throws DeviceException {
		System.out.println("Crystal cut : "+crystalCut.name()+" QValue : "+qvalue.getQValue());
		for (double energy = minEnergy; energy <= maxEnergy; energy += energyStep) {
			System.out.println("Testing energy "+energy);
			AlignmentParametersBean originalBean = getBean(energy, crystalCut, qvalue);
			AlignmentParametersBean calculatedBean = calculateBeanInPython(originalBean);
			testBean(originalBean, calculatedBean);
		}
	}

	/**
	 * Check that {@link AlignmentParametersCalculator} produces same results as the alignment_parameters Jython script
	 * @param originalBean
	 * @param beanFromScript
	 * @throws DeviceException
	 */
	private void testBean(AlignmentParametersBean originalBean, AlignmentParametersBean beanFromScript) throws DeviceException {
		AlignmentParametersCalculator calculator = getParametersCalculator(originalBean);

		calculator.setStripes();
		assertEquals("Me1 stripe", beanFromScript.getMe1stripe(), originalBean.getMe1stripe());
		assertEquals("Me2 stripe", beanFromScript.getMe2stripe(), originalBean.getMe2stripe());

		calculator.setPitchAndAttenuators();
		assertEquals("Me2 pitch", beanFromScript.getMe2Pitch(), originalBean.getMe2Pitch(), accuracy);
		assertEquals("Attenuator positions", beanFromScript.getAttenuatorPositions(), originalBean.getAttenuatorPositions());

		calculator.setBraggAngle();
		assertEquals("Bragg angle", beanFromScript.getBraggAngle(), originalBean.getBraggAngle(), accuracy);
		assertEquals("Arm 2theta", beanFromScript.getArm2Theta(), originalBean.getArm2Theta(), accuracy);

		calculator.setBenders();
		assertEquals("Poly bend 1", beanFromScript.getPolyBend1(), originalBean.getPolyBend1(), accuracy);
		assertEquals("Poly bend 2", beanFromScript.getPolyBend2(), originalBean.getPolyBend2(), accuracy);

		calculator.setPrimarySlits();
		assertEquals("Slit gap", beanFromScript.getPrimarySlitGap(), originalBean.getPrimarySlitGap(), accuracy);

		calculator.setDetectorPosition();
		assertEquals("Detector distance", beanFromScript.getDetectorDistance(), originalBean.getDetectorDistance(), accuracy);
		assertEquals("Detector height", beanFromScript.getDetectorHeight(), originalBean.getDetectorHeight(), accuracy);

		calculator.setEnergyBandwidth();
		assertEquals("Readback energy bandwidth", beanFromScript.getReadBackEnergyBandwidth(), originalBean.getReadBackEnergyBandwidth(), accuracy);
		assertEquals("Energy bandwidth", beanFromScript.getEnergyBandwidth(), originalBean.getEnergyBandwidth(), accuracy);

		calculator.setPower();
		assertEquals("Power", beanFromScript.getPower(), originalBean.getPower(), accuracy);
	}
}
