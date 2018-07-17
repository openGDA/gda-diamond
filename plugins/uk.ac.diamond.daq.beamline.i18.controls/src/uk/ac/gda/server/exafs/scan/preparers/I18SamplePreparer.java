package uk.ac.gda.server.exafs.scan.preparers;

import java.util.HashMap;

import gda.device.Scannable;
import gda.gui.RCPController;
import gda.jython.InterfaceProvider;
import uk.ac.gda.beans.exafs.ISampleParameters;
import uk.ac.gda.beans.exafs.IScanParameters;
import uk.ac.gda.beans.exafs.i18.I18SampleParameters;
import uk.ac.gda.server.exafs.scan.SampleEnvironmentPreparer;
import uk.ac.gda.server.exafs.scan.iterators.SampleEnvironmentIterator;

public class I18SamplePreparer implements SampleEnvironmentPreparer {

	private final RCPController rcpController;
	/*
	 * private final Scannable sc_MicroFocusSampleX; private final Scannable sc_MicroFocusSampleY; private final Scannable sc_sample_z;
	 */

	private Scannable stageSelected_x;
	private Scannable stageSelected_y;
	private Scannable stageSelected_z;
	private int stageSelected;
	private final HashMap<String, Scannable> stageScannableMap;
	private final Scannable kb_vfm_x;

	private I18SampleParameters parameters;
	private IScanParameters scanParameters;

	public I18SamplePreparer(RCPController rcpController, Scannable kb_vfm_x) {
		this.rcpController = rcpController;
		this.stageScannableMap = new HashMap<String, Scannable>();
		this.kb_vfm_x = kb_vfm_x;
	}

	public void setStage1(Scannable sc_MicroFocusSampleX, Scannable sc_MicroFocusSampleY, Scannable sc_sample_z) {
		stageScannableMap.put("stage1_x", sc_MicroFocusSampleX);
		stageScannableMap.put("stage1_y", sc_MicroFocusSampleY);
		stageScannableMap.put("stage1_z", sc_sample_z);
	}

	public void setStage3(Scannable table_x, Scannable table_y, Scannable table_z) {
		stageScannableMap.put("stage3_x", table_x);
		stageScannableMap.put("stage3_y", table_y);
		stageScannableMap.put("stage3_z", table_z);
	}

	public void setStage(int stageNumber) {
		stageSelected = stageNumber;
		switch (stageNumber) {
		case 1:
			stageSelected_x = stageScannableMap.get("stage1_x");
			stageSelected_y = stageScannableMap.get("stage1_y");
			stageSelected_z = stageScannableMap.get("stage1_z");
			break;
		case 3:
			stageSelected_x = stageScannableMap.get("stage3_x");
			stageSelected_y = stageScannableMap.get("stage3_y");
			stageSelected_z = stageScannableMap.get("stage3_z");
			break;
		default:
			InterfaceProvider.getTerminalPrinter().print("only stages 1 or 3 may be selected");
		}
	}

	public int getStage() {
		return stageSelected;
	}

	@Override
	public void configure(IScanParameters scanParameters, ISampleParameters parameters) throws Exception {
		this.scanParameters = scanParameters;
		this.parameters = (I18SampleParameters) parameters;
	}

	@Override
	public SampleEnvironmentIterator createIterator(String experimentType) {
		if (stageSelected_x == null || stageSelected_y == null || stageSelected_z == null)
			throw new NullPointerException();
		return new I18SampleEnvironmentIterator(scanParameters, parameters, rcpController, stageSelected_x, stageSelected_y, stageSelected_z,
				kb_vfm_x);
	}
}