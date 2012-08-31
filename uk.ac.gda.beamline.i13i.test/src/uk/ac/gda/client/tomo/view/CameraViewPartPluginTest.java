/*-
 * Copyright © 2010 Diamond Light Source Ltd.
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

package uk.ac.gda.client.tomo.view;
import static org.mockito.Mockito.mock;
import gda.TestHelpers;
import gda.device.detector.areadetector.v17.FfmpegStream;
import gda.device.detector.areadetector.v17.impl.ADBaseSimulator;
import gda.device.detector.areadetector.v17.impl.NDArraySimulator;
import gda.device.detector.areadetector.v17.impl.NDPluginBaseSimulator;
import gda.device.detector.areadetector.v17.impl.NDProcessSimulator;
import gda.rcp.util.OSGIServiceRegister;

import org.eclipse.draw2d.geometry.Point;
import org.eclipse.ui.IViewPart;
import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.mockito.Mockito;

import uk.ac.gda.beamline.i13i.views.cameraview.BeamCenterProvider;
import uk.ac.gda.beamline.i13i.views.cameraview.CameraViewPart;
import uk.ac.gda.beamline.i13i.views.cameraview.CameraViewPartConfig;
import uk.ac.gda.beamline.i13i.views.cameraview.CameraViewPartConfigImpl;
import uk.ac.gda.client.PluginTestHelpers;

/**
 *
 */
public class CameraViewPartPluginTest {

	static final long MAX_TIMEOUT_MS = 500;
	
	
	/**
	 */
	@BeforeClass
	public static void setUpBeforeClass() {
		
	}

	/**
	 */
	@AfterClass
	public static void tearDownAfterClass() {
	}

	@SuppressWarnings("unused")
	private String scratchFolder;

	/**
	 * @throws java.lang.Exception
	 */
	@Before
	public void setUp() throws Exception {
		scratchFolder=TestHelpers.setUpTest(CameraViewPartPluginTest.class, "setUp", true);

		CameraViewPartConfigImpl configImpl = new CameraViewPartConfigImpl();
		
		NDArraySimulator ndArray = new NDArraySimulator();
		ndArray.setPluginBase(new NDPluginBaseSimulator());
		configImpl.setNdArray(ndArray);

		NDProcessSimulator ndProcess = new NDProcessSimulator();
		ndProcess.setPluginBase(new NDPluginBaseSimulator());
		configImpl.setNdProcess(ndProcess);
		FfmpegStream stream = mock(FfmpegStream.class);
		Mockito.when(stream.getMJPG_URL_RBV()).thenReturn("DummySwtVideoReceiver");
		configImpl.setFfmpegStream(stream);
		configImpl.setSetExposureTimeCmd("test");
		configImpl.setAdBase(new ADBaseSimulator());
		BeamCenterProvider mock2 = mock(BeamCenterProvider.class);
		Mockito.when(mock2.getBeamCenter()).thenReturn(new Point(300,600));
		configImpl.setBeamCenterProvider(mock2);
		
		
		configImpl.afterPropertiesSet();
		
		OSGIServiceRegister register = new OSGIServiceRegister();
		register.setClass(CameraViewPartConfig.class);
		register.setService(configImpl);
		register.afterPropertiesSet();

	}

	/**
	 */
	@After
	public void tearDown() {
		
	}

	/**
	 * Test method for {@link uk.ac.gda.client.CommandQueueView#createPartControl(org.eclipse.swt.widgets.Composite)}.
	 * @throws Exception 
	 */
	@Test
	public final void testShowView() throws Exception {
		
		
		
		final IWorkbenchWindow window = PlatformUI.getWorkbench().getActiveWorkbenchWindow();
		IViewPart part = window.getActivePage().showView(CameraViewPart.ID);
		if( !(part instanceof CameraViewPart)){
			throw new PartInitException("View is not a CameraViewPart");
		}
		PluginTestHelpers.delay(10000); //time to 'play with the graph if wanted
	}

}
