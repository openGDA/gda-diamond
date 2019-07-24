package uk.ac.diamond.daq.beamline.i21.server;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Future;

import org.eclipse.january.dataset.Dataset;
import org.eclipse.january.dataset.DatasetFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.data.nexus.extractor.NexusGroupData;
import gda.data.nexus.tree.NexusTreeProvider;
import gda.device.DeviceException;
import gda.device.Scannable;
import gda.device.detector.DetectorBase;
import gda.device.detector.NXDetectorData;
import gda.device.detector.NexusDetector;
import gda.device.detector.addetector.ADDetector;
import gda.device.detector.areadetector.v17.ImageMode;
import gda.factory.FactoryException;
import uk.ac.diamond.daq.concurrent.Async;

public class I21Detector extends DetectorBase implements NexusDetector {

	private static final Logger logger = LoggerFactory.getLogger(I21Detector.class);
	private static final long serialVersionUID = 1L;

	/** The actual camera used as the detector */
	private ADDetector adDetector;

	// Scannables for moving between the sample and reference positions
	private transient Scannable manipulatorX;
	private transient Scannable manipulatorY;
	private transient Scannable manipulatorZ;

	// Sample positions
	private double sampleX;
	private double sampleY;
	private double sampleZ;

	// Reference positions
	private double referenceX;
	private double referenceY;
	private double referenceZ;

	private volatile int status;

	private int[] imageDimensions = new int[2];

	private transient CompletedPoint completedPoint;
	private transient Future<?> acquiring;

	// Acquisition parameters
	private int sampleImages = 1;
	private double sampleExposureTime = 1; // sec
	private int referenceImages = 1;
	private double referenceExposureTime = 1; // sec

	@Override
	public void configure() throws FactoryException {
		super.configure();
		setInputNames(new String[] {});
		setExtraNames(new String[] { "sample", "reference" });
		setOutputFormat(new String[] { "%5.5g", "%5.5g" });
	}

	@Override
	public void collectData() throws DeviceException {
		status = BUSY;
		acquiring = Async.submit(this::collectDataSync);
	}

	private void collectDataSync() {
		try {
			completedPoint = new CompletedPoint();

			// Sample
			logger.info("Starting sample acquisition");
			moveToSample();
			adDetector.getAdBase().setAcquireTime(sampleExposureTime);
			logger.debug("Set sample exposure time of {} secs", sampleExposureTime);
			for (int i = 0; i < sampleImages; i++) {
				completedPoint.addSampleImage(acquireImage());
				completedPoint.addSampleImageTimestamp(getAcquiredImageTimestamp());
				logger.debug("Acquired sample image {}/{}", i+1, sampleImages);
			}

			// Reference
			logger.info("Starting reference acquisition");
			moveToReference();
			adDetector.getAdBase().setAcquireTime(referenceExposureTime);
			logger.debug("Set reference exposure time of {} secs", referenceExposureTime);
			for (int i = 0; i < referenceImages; i++) {
				completedPoint.addReferenceImage(acquireImage());
				completedPoint.addReferenceImageTimestamp(getAcquiredImageTimestamp());
				logger.debug("Acquired reference image {}/{}", i+1, referenceImages);
			}

			// Change status back so isBusy will return false
			status = IDLE;
		} catch (Exception e) {
			status = FAULT;
			logger.error("Failed during collection", e);
		}
		logger.info("Completed acquiring point");
	}

	private Double getAcquiredImageTimestamp() throws Exception {
		return adDetector.getNdArray().getPluginBase().getTimeStamp_RBV();
	}

	/**
	 * Acquires one image, triggers the detector waits for the exposure to finish and then reads back the data.
	 *
	 * @return the acquired data
	 * @throws Exception
	 */
	private Dataset acquireImage() throws Exception {
		adDetector.collectData();
		adDetector.waitWhileBusy(); // Blocks during acquire
		return getImageData();
	}

	@Override
	public void prepareForCollection() throws DeviceException {
		logger.trace("prepareForCollection");
		// Ensures the array plugin is ready
		adDetector.prepareForArrayAndStatsCollection();
		try {
			// Make the AD do a single frame on each GDA request
			adDetector.getAdBase().setNumImages(1);
			adDetector.getAdBase().setNumExposures(1);
			adDetector.getAdBase().setImageMode(ImageMode.SINGLE);

			// Figure out the image dimensions
			imageDimensions[0] = adDetector.getAdBase().getArraySizeX_RBV();
			imageDimensions[1] = adDetector.getAdBase().getArraySizeY_RBV();
			logger.debug("Image dimensions: x={}, y={}", imageDimensions[0], imageDimensions[1]);
		} catch (Exception e) {
			throw new DeviceException("Failed configuring detector", e);
		}
		logger.debug("Configured detector");
	}

	private Dataset getImageData() throws Exception {
		// Get the data from the detector array plugin
		Object image = adDetector.getNdArray().getImageData(imageDimensions[0] * imageDimensions[1]);

		return DatasetFactory.createFromObject(image, imageDimensions);
	}

	@Override
	public void waitWhileBusy() throws DeviceException, InterruptedException {
		try {
			acquiring.get(); // Blocks while acquiring
		} catch (ExecutionException e) {
			throw new DeviceException("Acquiring failed", e);
		}
	}

	@Override
	public int getStatus() throws DeviceException {
		return status;
	}

	@Override
	public NexusTreeProvider readout() throws DeviceException {
		NXDetectorData nxdata = new NXDetectorData(this);

		// Sample
		Dataset sampleDataset = completedPoint.getSampleImagesDataset();
		NexusGroupData sampleNgd = NexusGroupData.createFromDataset(sampleDataset);
		sampleNgd.isDetectorEntryData = true; // Make true so its copied to NXData
		nxdata.addData(getName(), "sample", sampleNgd, null);
		nxdata.addElement(getName(), "sample_frames", new NexusGroupData(getSampleImages()), null, false);
		nxdata.addElement(getName(), "sample_exposure", new NexusGroupData(getSampleExposureTime()), "seconds", false);
		nxdata.addElement(getName(), "sample_image_timestamps", new NexusGroupData(completedPoint.getSampleImageTimestampsDataset()), "seconds", false);
		// This casting is a little nasty but think its always safe.
		nxdata.setPlottableValue("sample", ((Number) sampleDataset.sum()).doubleValue());

		// Reference
		Dataset referenceDataset = completedPoint.getReferenceImagesDataset();
		NexusGroupData referenceNgd = NexusGroupData.createFromDataset(referenceDataset);
		referenceNgd.isDetectorEntryData = true; // Make true so its copied to NXData
		nxdata.addData(getName(), "reference", referenceNgd, null);
		nxdata.addElement(getName(), "reference_frames", new NexusGroupData(getReferenceImages()), null, false);
		nxdata.addElement(getName(), "reference_exposure", new NexusGroupData(getReferenceExposureTime()), "seconds",
				false);
		nxdata.addElement(getName(), "reference_image_timestamps", new NexusGroupData(completedPoint.getReferenceImageTimestampsDataset()), "seconds", false);
		// This casting is a little nasty but think its always safe.
		nxdata.setPlottableValue("reference", ((Number) referenceDataset.sum()).doubleValue());

		return nxdata;
	}

	@Override
	public boolean createsOwnFiles() throws DeviceException {
		// No will write into the scan NeXus file
		return false;
	}

	private void moveManipulatorTo(double x, double y, double z) throws DeviceException, InterruptedException {
		manipulatorX.asynchronousMoveTo(x);
		manipulatorY.asynchronousMoveTo(y);
		manipulatorZ.asynchronousMoveTo(z);
		manipulatorX.waitWhileBusy();
		manipulatorY.waitWhileBusy();
		manipulatorZ.waitWhileBusy();
	}

	public void moveToSample() throws DeviceException, InterruptedException {
		logger.info("Moving to sample position: x={}, y={}, z={}", sampleX, sampleY, sampleZ);
		moveManipulatorTo(sampleX, sampleY, sampleZ);
	}

	public void moveToReference() throws DeviceException, InterruptedException {
		logger.info("Moving to reference position: x={}, y={}, z={}", referenceX, referenceY, referenceZ);
		moveManipulatorTo(referenceX, referenceY, referenceZ);
	}

	@Override
	public String toFormattedString() {
		StringBuilder sb = new StringBuilder();
		sb.append(super.toFormattedString());
		sb.append(", ");
		// Sample
		sb.append(String.format("sample=[x=%5.5g, y=%5.5g, z=%5.5g, exposure=%2.1g, images=%d], ",
				getSampleX(), getSampleY(), getSampleZ(), getSampleExposureTime(), getSampleImages()));
		// Reference
		sb.append(String.format("reference=[x=%5.5g, y=%5.5g, z=%5.5g, exposure=%2.1g, images=%d]",
				getReferenceX(), getReferenceY(), getReferenceZ(), getReferenceExposureTime(), getReferenceImages()));
		return sb.toString();
	}

	// Getters / Setters

	public ADDetector getAdDetector() {
		return adDetector;
	}

	public void setAdDetector(ADDetector adDetector) {
		this.adDetector = adDetector;
	}

	public double getSampleX() {
		return sampleX;
	}

	public void setSampleX(double sampleX) {
		this.sampleX = sampleX;
	}

	public double getSampleY() {
		return sampleY;
	}

	public void setSampleY(double sampleY) {
		this.sampleY = sampleY;
	}

	public double getSampleZ() {
		return sampleZ;
	}

	public void setSampleZ(double sampleZ) {
		this.sampleZ = sampleZ;
	}

	public void setSamplePosition(double x, double y, double z) {
		this.sampleX = x;
		this.sampleY = y;
		this.sampleZ = z;
		logger.debug("Set sample position to: x={}, y={}, z={}", sampleX, sampleY, sampleZ);
	}

	public double getReferenceX() {
		return referenceX;
	}

	public void setReferenceX(double referenceX) {
		this.referenceX = referenceX;
	}

	public double getReferenceY() {
		return referenceY;
	}

	public void setReferenceY(double referenceY) {
		this.referenceY = referenceY;
	}

	public double getReferenceZ() {
		return referenceZ;
	}

	public void setReferenceZ(double referenceZ) {
		this.referenceZ = referenceZ;
	}

	public void setReferencePosition(double x, double y, double z) {
		this.referenceX = x;
		this.referenceY = y;
		this.referenceZ = z;
		logger.debug("Set reference position to: x={}, y={}, z={}", referenceX, referenceY, referenceZ);
	}

	public Scannable getManipulatorX() {
		return manipulatorX;
	}

	public void setManipulatorX(Scannable manipulatorX) {
		this.manipulatorX = manipulatorX;
	}

	public Scannable getManipulatorY() {
		return manipulatorY;
	}

	public void setManipulatorY(Scannable manipulatorY) {
		this.manipulatorY = manipulatorY;
	}

	public Scannable getManipulatorZ() {
		return manipulatorZ;
	}

	public void setManipulatorZ(Scannable manipulatorZ) {
		this.manipulatorZ = manipulatorZ;
	}

	public int getSampleImages() {
		return sampleImages;
	}

	public void setSampleImages(int sampleImages) {
		if (sampleImages < 1) {
			throw new IllegalArgumentException("Number of images must be >=1");
		}
		this.sampleImages = sampleImages;
	}

	public double getSampleExposureTime() {
		return sampleExposureTime;
	}

	public void setSampleExposureTime(double sampleExposureTime) {
		if (sampleExposureTime <= 0) {
			throw new IllegalArgumentException("Exposure time must be >0");
		}
		this.sampleExposureTime = sampleExposureTime;
	}

	public int getReferenceImages() {
		return referenceImages;
	}

	public void setReferenceImages(int referenceImages) {
		if (referenceImages < 1) {
			throw new IllegalArgumentException("Number of images must be >=1");
		}
		this.referenceImages = referenceImages;
	}

	public double getReferenceExposureTime() {
		return referenceExposureTime;
	}

	public void setReferenceExposureTime(double referenceExposureTime) {
		if (referenceExposureTime <= 0) {
			throw new IllegalArgumentException("Exposure time must be >0");
		}
		this.referenceExposureTime = referenceExposureTime;
	}

	private class CompletedPoint {
		private final List<Dataset> sampleImages = new ArrayList<>();
		private final List<Dataset> referenceImages = new ArrayList<>();
		private final List<Double> sampleImageTimestamps= new ArrayList<>();
		private final List<Double> referenceImageTimestamps=new ArrayList<>();

		public void addSampleImage(Dataset image) {
			sampleImages.add(image);
		}

		/**
		 * Gets all the sample data as a 3D image stack
		 *
		 * @return a 3D dataset containing all of the sample data for this point in an image stack
		 */
		public Dataset getSampleImagesDataset() {
			return DatasetFactory.createFromObject(sampleImages);
		}

		public void addSampleImageTimestamp(Double timestamp) {
			sampleImageTimestamps.add(timestamp);
		}

		public Dataset getSampleImageTimestampsDataset() {
			return DatasetFactory.createFromList(sampleImageTimestamps);
		}

		public void addReferenceImage(Dataset image) {
			referenceImages.add(image);
		}

		/**
		 * Gets all the reference data as a 3D image stack
		 *
		 * @return a 3D dataset containing all of the reference data for this point in an image stack
		 */
		public Dataset getReferenceImagesDataset() {
			return DatasetFactory.createFromObject(referenceImages);
		}

		public void addReferenceImageTimestamp(Double timestamp) {
			referenceImageTimestamps.add(timestamp);
		}

		public Dataset getReferenceImageTimestampsDataset() {
			return DatasetFactory.createFromList(referenceImageTimestamps);
		}
	}

}
