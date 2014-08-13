/*-
 * Copyright © 2009 Diamond Light Source Ltd.
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

package uk.ac.gda.dls.exafs.test;

import org.eclipse.ui.IWorkbenchWindow;
import org.eclipse.ui.PartInitException;
import org.eclipse.ui.PlatformUI;
import org.eclipse.ui.actions.ActionFactory;
import org.junit.Before;
import org.junit.Test;

import uk.ac.diamond.scisoft.analysis.dataset.Dataset;
import uk.ac.diamond.scisoft.analysis.dataset.DatasetFactory;
import uk.ac.diamond.scisoft.analysis.dataset.Maths;
import uk.ac.diamond.scisoft.analysis.optimize.GeneticAlg;
import uk.ac.diamond.scisoft.analysis.optimize.IOptimizer;
import uk.ac.diamond.scisoft.analysis.optimize.LeastSquares;
import uk.ac.diamond.scisoft.analysis.optimize.NelderMead;
import uk.ac.diamond.scisoft.analysis.plotserver.AxisMapBean;
import uk.ac.diamond.scisoft.analysis.plotserver.DataBean;
import uk.ac.diamond.scisoft.analysis.plotserver.DataSetWithAxisInformation;
import uk.ac.diamond.scisoft.analysis.plotserver.GuiBean;
import uk.ac.diamond.scisoft.analysis.plotserver.GuiParameters;
import uk.ac.diamond.scisoft.analysis.plotserver.GuiPlotMode;
import uk.ac.diamond.scisoft.analysis.rcp.views.PlotView;
import uk.ac.diamond.scisoft.spectroscopy.fitting.XafsFittingUtils;
import uk.ac.gda.ClientManager;
import uk.ac.gda.common.rcp.util.EclipseUtils;
import uk.ac.gda.util.io.TokenFileParser;

public class ExafsPlotPluginTest {
	
	private PlotView view;
	private static final Long seed = 1237L;
	private XafsFittingUtils xafsFittingUtils = new XafsFittingUtils(seed);
	
	@Before
	public void setup() throws PartInitException {
		
		ClientManager.setTestingMode(true);
		
		GuiBean guiBean = new GuiBean();
		guiBean.put(GuiParameters.PLOTMODE, GuiPlotMode.ONED);
		guiBean.put(GuiParameters.PLOTOPERATION, GuiParameters.PLOTOP_UPDATE);
		
		final IWorkbenchWindow window = PlatformUI.getWorkbench().getActiveWorkbenchWindow();
		this.view = (PlotView)window.getActivePage().showView(PlotView.ID+"1");
		window.getActivePage().activate(view);
		
		ActionFactory.IWorkbenchAction  maximizeAction = ActionFactory.MAXIMIZE.create(window);
		maximizeAction.run(); // Will maximize the active part
		
		view.processGUIUpdate(guiBean);

	}
	
	
	/**
	 * TODO FIXME Mark to get working please
	 * @throws Exception
	 */
	@Test
	public void testNormalisedDataLeastSqaures() throws Exception {
		
		testNormalisedFile("Cofoil_4_845.dat",  7650d,    new LeastSquares(1e-10));
		EclipseUtils.delay(3000);
		testNormalisedFile("Mo_1_1247.dat",     19992d,   new LeastSquares(1e-10));
		EclipseUtils.delay(3000);
		testNormalisedFile("Ptfoil3_5_570.dat", 11537.0d, new LeastSquares(1e-10));
		EclipseUtils.delay(3000);
	}

	/**
	 * TODO FIXME Mark to get working please
	 * @throws Exception
	 */
	@Test
	public void testNormalisedDataNedlerMead() throws Exception {
		
		testNormalisedFile("Cofoil_4_845.dat",  7650d,    new NelderMead(1e-10));
		EclipseUtils.delay(3000);
		testNormalisedFile("Mo_1_1247.dat",     19992d,   new NelderMead(1e-10));
		EclipseUtils.delay(3000);
		testNormalisedFile("Ptfoil3_5_570.dat", 11537.0d, new NelderMead(1e-10));
		EclipseUtils.delay(3000);
	}
	
	@Test
	public void testNormalisedDataGenetic() throws Exception {
		
		testNormalisedFile("Cofoil_4_845.dat",  7650d,    new GeneticAlg(1e-10, seed));
		EclipseUtils.delay(3000);
		testNormalisedFile("Mo_1_1247.dat",     19992d,   new GeneticAlg(1e-10, seed));
		EclipseUtils.delay(3000);
		testNormalisedFile("Ptfoil3_5_570.dat", 11537.0d, new GeneticAlg(1e-10, seed));
		EclipseUtils.delay(3000);
	}

	private void testNormalisedFile(final String fileName, final double a, @SuppressWarnings("unused") final IOptimizer optim) throws Exception {
		
		final TokenFileParser parser = new TokenFileParser(getClass().getResource(fileName));
		parser.setToken(" ");
		parser.setCommentChar("#");
		parser.parse();
		
		final Dataset energy = DatasetFactory.createFromList(parser.getColumnAsDoubleList(0));
		final Dataset lnI0It = DatasetFactory.createFromList(parser.getColumnAsDoubleList(4));
		
		final Dataset norm = xafsFittingUtils.getNormalisedIntensity(energy, lnI0It, a, 0.0);
		
		plot(energy, norm, lnI0It);
		
		for (int i = 0; a>energy.getDouble(i) ;++i) {
			final double normVal = norm.getDouble(i);
			if (normVal>0.1 || normVal<-0.1) throw new Exception("Gradient not fitted correctly! Expected it between -0.1 and 0.1, but was "+normVal);
		}
       
	}

	
	@Test
	public void testFirstDerivativeDataGenetic() throws Exception {
		
		testFirstDerivativeFile("Cofoil_4_845.dat",  7650d);
		EclipseUtils.delay(3000);
		testFirstDerivativeFile("Mo_1_1247.dat",     19992d);
		EclipseUtils.delay(3000);
		testFirstDerivativeFile("Ptfoil3_5_570.dat", 11537.0d);
		EclipseUtils.delay(3000);
	}

	private void testFirstDerivativeFile(final String fileName, final double a) throws Exception {
		
		final TokenFileParser parser = new TokenFileParser(getClass().getResource(fileName));
		parser.setToken(" ");
		parser.setCommentChar("#");
		parser.parse();
		
		final Dataset energy = DatasetFactory.createFromList(parser.getColumnAsDoubleList(0));
		final Dataset lnI0It = DatasetFactory.createFromList(parser.getColumnAsDoubleList(4));
		
		final Dataset norm = xafsFittingUtils.getNormalisedIntensity(energy, lnI0It, a, 0.0);
		final Dataset derv = Maths.derivative(energy, norm, 1);
		
		plot(energy, derv);
		       
	}

	@Test
	public void testSpline() throws Exception {
		
		testSplineFile("Cofoil_4_845.dat",  7650d,    new GeneticAlg(0.0001, seed));
		EclipseUtils.delay(5000);
		testSplineFile("Mo_1_1247.dat",     19992d,   new GeneticAlg(0.0001, seed));
		EclipseUtils.delay(5000);
		testSplineFile("Ptfoil3_5_570.dat", 11537.0d, new GeneticAlg(0.0001, seed));
		EclipseUtils.delay(5000);
	}

	private void testSplineFile(final String fileName, final double a, @SuppressWarnings("unused") final IOptimizer optim) throws Exception {
		
		final TokenFileParser parser = new TokenFileParser(getClass().getResource(fileName));
		parser.setToken(" ");
		parser.setCommentChar("#");
		parser.parse();
		
		final Dataset energy = DatasetFactory.createFromList(parser.getColumnAsDoubleList(0));
		final Dataset lnI0It = DatasetFactory.createFromList(parser.getColumnAsDoubleList(4));

		final Dataset[] exafs = xafsFittingUtils.getNormalisedIntensityAndSpline(energy, lnI0It, a, 0.0);
		
		plot(exafs[0], exafs[1], exafs[2]);
		      
	}
	
	@Test
	public void testKWeightedK1() throws Exception {
		
		testKWeightedFile("Cofoil_4_845.dat",  7650d,    new GeneticAlg(0.0001, seed), 1);
		EclipseUtils.delay(5000);
		testKWeightedFile("Mo_1_1247.dat",     19992d,   new GeneticAlg(0.0001, seed), 1);
		EclipseUtils.delay(5000);
		testKWeightedFile("Ptfoil3_5_570.dat", 11537.0d, new GeneticAlg(0.0001, seed), 1);
		EclipseUtils.delay(5000);
	}
	
	@Test
	public void testKWeightedK3() throws Exception {
		
		testKWeightedFile("Cofoil_4_845.dat",  7650d,    new GeneticAlg(0.0001, seed), 3);
		EclipseUtils.delay(5000);
		testKWeightedFile("Mo_1_1247.dat",     19992d,   new GeneticAlg(0.0001, seed), 3);
		EclipseUtils.delay(5000);
		testKWeightedFile("Ptfoil3_5_570.dat", 11537.0d, new GeneticAlg(0.0001, seed), 3);
		EclipseUtils.delay(5000);
	}

	private void testKWeightedFile(final String fileName, final double a, @SuppressWarnings("unused") final IOptimizer optim, @SuppressWarnings("unused") int kWeight) throws Exception {
		
		final TokenFileParser parser = new TokenFileParser(getClass().getResource(fileName));
		parser.setToken(" ");
		parser.setCommentChar("#");
		parser.parse();
		
		final Dataset energy = DatasetFactory.createFromList(parser.getColumnAsDoubleList(0));
		final Dataset lnI0It = DatasetFactory.createFromList(parser.getColumnAsDoubleList(4));
		
		final Dataset[] ks = xafsFittingUtils.getSubtractedBackgroundInK(energy, lnI0It, a, 0.0);
		
		plot(ks[0], ks[1]);
		      
	}

	@Test
	public void testFFT() throws Exception {
		
		testFFTFile("Cofoil_4_845.dat",  7650d,    new GeneticAlg(0.0001, seed), 1);
		EclipseUtils.delay(5000);
		testFFTFile("Mo_1_1247.dat",     19992d,   new GeneticAlg(0.0001, seed), 1);
		EclipseUtils.delay(5000);
		testFFTFile("Ptfoil3_5_570.dat", 11537.0d, new GeneticAlg(0.0001, seed), 1);
		EclipseUtils.delay(5000);
	}

	private void testFFTFile(final String fileName, final double a, @SuppressWarnings("unused") final IOptimizer optim, @SuppressWarnings("unused") int kWeight) throws Exception {
		
		final TokenFileParser parser = new TokenFileParser(getClass().getResource(fileName));
		parser.setToken(" ");
		parser.setCommentChar("#");
		parser.parse();
		
		final Dataset energy = DatasetFactory.createFromList(parser.getColumnAsDoubleList(0));
		final Dataset lnI0It = DatasetFactory.createFromList(parser.getColumnAsDoubleList(4));
		
		final Dataset[] fft = xafsFittingUtils.getFFT(energy, lnI0It, a, a+300);
		
		plot(fft[0], fft[1]);
		      
	}
	
	private void plot(final Dataset x, final Dataset... yAxes) throws Exception {
		
		
		DataBean dataBean = new DataBean();
		dataBean.addAxis(AxisMapBean.XAXIS, x);

		for (int i = 0; i < yAxes.length; i++) {
			dataBean.addData(DataSetWithAxisInformation.createAxisDataSet(yAxes[i]));
		}
		
		view.processPlotUpdate(dataBean);

	}
}
