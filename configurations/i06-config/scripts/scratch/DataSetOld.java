// *****************************************************************************
// Copyright (C) 2000-2009
// STFC Daresbury Laboratory, Diamond Light Source
// All Rights Reserved.
// *****************************************************************************

package gda.analysis;

import gda.analysis.functions.dataset.IDataSetFunction;
import gda.analysis.utils.DatasetMaths;
import gda.jython.InterfaceProvider;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.python.core.Py;
import org.python.core.PyException;
import org.python.core.PyFloat;
import org.python.core.PyInteger;
import org.python.core.PyNone;
import org.python.core.PyObject;
import org.python.core.PySequenceList;
import org.python.core.PySlice;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import Jama.Matrix;

/**
 * Generic container class for data
 */
public class DataSet implements Serializable {

	/**
	 * Added to remove warning, should probably be updated if there are any serious changes to what the dataset contains
	 */
	private static final long serialVersionUID = 1L;

	/**
	 * Setup the logging facilities
	 */
	transient private static final Logger logger = LoggerFactory.getLogger(DataSet.class);

	/**
	 * Limit to strings output via the disp() method
	 */
	private static final int maxDisplayLength = 1024;

	private static final float ARRAY_ALLOCTAION_EXTENTION = 0.5f;

	/**
	 * The dimensions of the dataset
	 */
	private int[] dimensions;

	/**
	 * The dimensions of the dataset memory footprint
	 */
	private int[] dataDimensions;
	
	/**
	 * The data itself, held in a single array, but the object will wrap it to appear as many
	 */
	private double[] data = null;

	private String name = "";

	/**
	 * These flags tell if functions need to be recalculated If the value is null, then recalculate, otherwise just use
	 * the value
	 */
	private Double dirtyMaxValue = null;
	private Double dirtyMinValue = null;
	private int[] dirtyMaxPos = null;
	private int[] dirtyMinPos = null;
	private Double dirtySum = null;
	private Double dirtyStandardDeviation = null;
	private Double dirtyMeanValue = null;

	/**
	 * Constructor required for serialisation.
	 */
	public DataSet() {

	}

	/**
	 * Constructor setting a name
	 * 
	 * @param name
	 */
	public DataSet(String name) {
		this();
		this.name = name;
	}

	/**
	 * @param name
	 * @param dimensions
	 */
	public DataSet(String name, int... dimensions) {
		this(dimensions);
		this.name = name;
	}

	/**
	 * Constructs an empty GenericDataSet with the specified initial capacity and capacity increment.
	 * 
	 * @param dimensions
	 */
	public DataSet(int... dimensions) {
		this((double[]) null, dimensions);
	}

	/**
	 * Constructs a DataSet with the specified capacity using the given buffer if of the correct size
	 * 
	 * @param data
	 * @param dimensions
	 */
	public DataSet(double[] data, int... dimensions) {

		if (dimensions.length > 0) {
			this.dimensions = dimensions;
			int size = 1;
			double dsize = 1.0;
			for (int i = 0; i < dimensions.length; i++) {
				// make sure the indexes isn't zero or negative
				if (dimensions[i] <= 0) {
					logger.error("Argument " + i + " is " + dimensions[i]
							+ " which is an illegal argument as it is zero or negative");
					throw new IllegalArgumentException("Argument " + i + " is " + dimensions[i]
							+ " which is an illegal argument as it is zero or negative");
				}

				size = size * dimensions[i];
				dsize = dsize * dimensions[i];
			}

			// check to see if the size is zero

			// check to see if the size is larger than an integer, i.e. we
			// can't allocate it
			if (dsize > Integer.MAX_VALUE) {
				logger.error("The size of the dataset that is being created is too large to allocate memory for.");
				throw new IllegalArgumentException("Size of the dataset is too large to allocate");
			}

			// try to allocate the memory, and see if we get an out of
			// memory error
			try {
				if (data != null && data.length == size) {
					this.data = data;
				} else {
					this.data = new double[size];
				}
			} catch (OutOfMemoryError e) {
				logger
						.error("The size of the dataset that is being created is too large and there is not enough memory to hold it.");
				throw new OutOfMemoryError("The dimentions given are too large, and there is "
						+ "not enough memory available in the Java Virtual Machine");
			}
		} else {
			this.dimensions = new int[] { 0 };
			logger.warn("Dataset should be constructed with some indexes");
			logger.warn("Set is curently empty");
		}

	}

	/**
	 * @param name
	 * @param inData
	 */
	public DataSet(String name, double[][] inData) {
		this(inData);
		this.name = name;
	}

	/**
	 * Constructor which takes a double array of arrays to make a 2D dataset object.
	 * 
	 * @param inData
	 *            The data to construct the dataset from
	 */
	public DataSet(double[][] inData) {
		this.dimensions = new int[] { inData.length, inData[0].length };
		int totalsize = inData.length * inData[0].length;

		try {
			data = new double[totalsize];
		} catch (OutOfMemoryError e) {
			logger.error("Not enough memory available to create dataset");
			throw new OutOfMemoryError("Not enough memory available to create dataset");
		}

		// store this in row-major order where we want the index to change slowest when
		// going along each row in an array
		int count = 0;
		for (int i = 0; i < inData.length; i++) {
			for (int j = 0; j < inData[0].length; j++) {
				data[count++] = inData[i][j];
			}
		}
	}

	/**
	 * @param name
	 * @param inData
	 */
	public DataSet(String name, double[] inData) {
		this(inData);
		this.name = name;
	}

	/**
	 * Constructor which takes a double Collection to make a 1D dataset object.
	 * 
	 * @param inData
	 *            The data to construct the dataset from
	 */
	public DataSet(final List<Double> inData) {
		this.dimensions = new int[] { inData.size() };
		try {
			data = new double[inData.size()];
		} catch (OutOfMemoryError e) {
			logger.error("Not enough memory available to create dataset");
			throw new OutOfMemoryError("Not enough memory available to create dataset");
		}
		for (int i = 0; i < inData.size(); i++) {
			data[i] = inData.get(i);
		}
	}
	/**
	 * Constructor which takes a double array to make a 1D dataset object.
	 * 
	 * @param inData
	 *            The data to construct the dataset from
	 */
	public DataSet(double[] inData) {
		this.dimensions = new int[] { inData.length };
		try {
			data = new double[inData.length];
		} catch (OutOfMemoryError e) {
			logger.error("Not enough memory available to create dataset");
			throw new OutOfMemoryError("Not enough memory available to create dataset");
		}
		for (int i = 0; i < inData.length; i++) {
			data[i] = inData[i];
		}
	}

	/**
	 * @param name
	 * @param height
	 * @param width
	 * @param inData
	 */
	public DataSet(String name, int height, int width, double[] inData) {
		this(height, width, inData);
		this.name = name;
	}

	/**
	 * Constructor for the dataset which creates a height x width matrix
	 * 
	 * @param height
	 *            Height of the matrix
	 * @param width
	 *            Width of the matrix
	 * @param inData
	 *            Data in the matrix, where width is fastest direction
	 */
	public DataSet(int height, int width, double[] inData) {
		// check the inputs are sensible
		if (width <= 0) {
			logger.error("width argument is " + width + " which is an illegal argument as it is zero or negative");
			throw new IllegalArgumentException("width argument is " + width
					+ " which is an illegal argument as it is zero or negative");
		}

		if (height <= 0) {
			logger.error("height argument is " + height + " which is an illegal argument as it is zero or negative");
			throw new IllegalArgumentException("height argument is " + height
					+ " which is an illegal argument as it is zero or negative");
		}

		// first check to make sure there is enough data in the data array to
		// fill the new vector
		if ((width * height) > inData.length) {
			logger.error("Not enough data provided to dataset " + inData.length + " provided but " + width * height
					+ " needed");
			throw new IllegalArgumentException("Not enough data provided to dataset " + inData.length
					+ " provided but " + width * height + " needed");
		} else if ((width * height) < inData.length) {
			logger.warn("Not all the dataset given fits into the size specified");
		}

		// store this in row-major order where we want the index to change slowest when
		// going along each row of an image
		this.dimensions = new int[] { height, width };
		try {
			data = new double[width * height];
		} catch (OutOfMemoryError e) {
			logger.error("Not enough memory available to create dataset");
			throw new OutOfMemoryError("Not enough memory available to create dataset");
		}
		for (int i = 0; i < data.length; i++) {
			data[i] = inData[i];
		}
	}

	/**
	 * @param name
	 * @param depth
	 * @param height
	 * @param width
	 * @param inData
	 */
	public DataSet(String name, int depth, int height, int width, double[] inData) {
		this(depth, height, width, inData);
		this.name = name;
	}

	/**
	 * Constructor for the dataset which will be three dimensional
	 * 
	 * @param depth
	 *            depth of the dataset (slowest)
	 * @param height
	 *            height of the dataset (fast)
	 * @param width
	 *            width of the dataset (fastest)
	 * @param inData
	 *            The data to be read in.
	 */
	public DataSet(int depth, int height, int width, double[] inData) {

		// check the inputs are sensible
		if (width <= 0) {
			logger.error("width argument is " + width + " which is an illegal argument as it is zero or negative");
			throw new IllegalArgumentException("width argument is " + width
					+ " which is an illegal argument as it is zero or negative");
		}

		if (height <= 0) {
			logger.error("height argument is " + height + " which is an illegal argument as it is zero or negative");
			throw new IllegalArgumentException("height argument is " + height
					+ " which is an illegal argument as it is zero or negative");
		}

		if (depth <= 0) {
			logger.error("depth argument is " + depth + " which is an illegal argument as it is zero or negative");
			throw new IllegalArgumentException("depth argument is " + depth
					+ " which is an illegal argument as it is zero or negative");
		}

		if ((width * height * depth) > inData.length) {
			logger.error("Not enough data provided to dataset " + inData.length + " provided but " + width * height
					* depth + " needed");
			throw new IllegalArgumentException("Not enough data provided to dataset " + inData.length
					+ " provided but " + width * height * depth + " needed");
		}

		// store this in row-major order where we want the index to change slowest when
		// going along rows of image
		this.dimensions = new int[] { depth, height, width };

		try {
			data = new double[width * height * depth];
		} catch (OutOfMemoryError e) {
			logger.error("Not enough memory available to create dataset");
			throw new OutOfMemoryError("Not enough memory available to create dataset");
		}
		for (int i = 0; i < data.length; i++) {
			data[i] = inData[i];
		}
	}

	/**
	 * @param name
	 * @param inputMatrix
	 */
	public DataSet(String name, Matrix inputMatrix) {
		this(inputMatrix);
		this.name = name;
	}

	/**
	 * Constructor which creates the dataset from a jama matrix.
	 * 
	 * @param inputMatrix
	 */
	public DataSet(Matrix inputMatrix) {

		// make sure the input Matrix Exists
		if (inputMatrix == null) {
			logger.error("Input matrix to the dataset is null");
			throw new IllegalArgumentException("Input matrix to the dataset is null");
		}
		int dims[] = new int[] { inputMatrix.getRowDimension(), inputMatrix.getColumnDimension() };

		// check the dimensions
		for (int i = 0; i < dims.length; i++) {
			// make sure the indices aren't zero or negative
			if (dims[i] <= 0) {
				logger.error("Argument " + i + " is " + dims[i]
						+ " which is an illegal argument as it is zero or negative");
				throw new IllegalArgumentException("Argument " + i + " is " + dims[i]
						+ " which is an illegal argument as it is zero or negative");
			}
		}
		try {
			// store this in row-major order where we want the index to change slowest when
			// going along rows of image
			data = inputMatrix.getRowPackedCopy();
		} catch (OutOfMemoryError e) {
			logger.error("Not enough memory available to create dataset");
			throw new OutOfMemoryError("Not enough memory available to create dataset");
		}
		this.dimensions = dims;
	}

	/**
	 * Constructor based on replicating a Dataset
	 * 
	 * @param inputDataSet
	 *            The dataset to be replicated.
	 */
	public DataSet(DataSet inputDataSet) {
		// make sure the input DataSet Exists
		if (inputDataSet == null) {
			logger.error("Input dataset to the dataset is null");
			throw new IllegalArgumentException("Input dataset to the dataset is null");
		}
		try {
			// first set the dimensions
			this.dimensions = new int[inputDataSet.dimensions.length];
			// now pass over the data information
			this.data = new double[inputDataSet.data.length];

		} catch (OutOfMemoryError e) {
			logger.error("Not enough memory available to create dataset");
			throw new OutOfMemoryError("Not enough memory available to create dataset");
		}

		// copy across the data
		for (int i = 0; i < inputDataSet.dimensions.length; i++) {
			this.dimensions[i] = inputDataSet.dimensions[i];
		}
		for (int i = 0; i < inputDataSet.data.length; i++) {
			this.data[i] = inputDataSet.data[i];
		}

		this.name = inputDataSet.getName();
	}

	/**
	 * Constructs a DataSet with the specified capacity using the given buffer if of the correct size
	 *
	 * @param list
	 */
	public DataSet(PySequenceList list) {
		ArrayList<Integer> ldims = new ArrayList<Integer>();
		PySequenceList ilist = list;
		// find rank and dimensions
		while (true) {
			ldims.add(ilist.size());
			Object obj = ilist.get(0);
			if (obj instanceof PySequenceList) {

			} else {
				break;
			}
			ilist = (PySequenceList) obj;
		}
		int rank = ldims.size();
		this.dimensions = new int[rank];
		for (int i = 0; i < rank; i++) {
			dimensions[i] = ldims.get(i);
		}

		int size = 1;
		double dsize = 1.0;
		for (int i = 0; i < dimensions.length; i++) {
			// make sure the indexes isn't zero or negative
			if (dimensions[i] <= 0) {
				logger.error("Argument " + i + " is " + dimensions[i]
						+ " which is an illegal argument as it is zero or negative");
				throw new IllegalArgumentException("Argument " + i + " is " + dimensions[i]
						+ " which is an illegal argument as it is zero or negative");
			}

			size = size * dimensions[i];
			dsize = dsize * dimensions[i];
		}

		// check to see if the size is zero

		// check to see if the size is larger than an integer, i.e. we
		// can't allocate it
		if (dsize > Integer.MAX_VALUE) {
			logger.error("The size of the dataset that is being created is too large to allocate memory for.");
			throw new IllegalArgumentException("Size of the dataset is too large to allocate");
		}

		// try to allocate the memory, and see if we get an out of
		// memory error
		try {
			data = new double[size];
		} catch (OutOfMemoryError e) {
			logger
					.error("The size of the dataset that is being created is too large and there is not enough memory to hold it.");
			throw new OutOfMemoryError("The dimentions given are too large, and there is "
					+ "not enough memory available in the Java Virtual Machine");
		}

		if (flatten(0, list) < 0) {
			logger.error("Wrong data type in PySlice");
			throw new IllegalArgumentException("Wrong data type in PySlice");
		}
	}


	// recursive function to flatten PySequenceList
	private int flatten(int offset, PySequenceList list) {
		int length = list.size();

		Object obj;
		obj = list.get(0);
		if (obj instanceof PySequenceList) {
			for (int i = 0; i < length; i++) {
				offset = flatten(offset, (PySequenceList) list.get(i));
			}
		} else {
			for (int i = 0; i < length; i++) {
				obj = list.get(i);
				if (obj instanceof PyInteger || obj instanceof Integer) {
					data[offset++] = ((Integer) obj).doubleValue();
				} else if (obj instanceof PyFloat || obj instanceof Double) {
					data[offset++] = ((Double) list.get(i));
				} else { // hmmm
					logger.error("Can't handle this data type in PySlice: " + ((PyObject) obj).getType());
					offset = -1;
				}
			}
		}

		return offset;
	}

	/**
	 * Function which returns the size of all the data, i.e the number of elements in the array
	 * 
	 * @return an int showing the number of data elements
	 */
	public int dataSize() {
		if (data == null) {
			logger
					.error("The data object inside the dataset has not been allocated, this sugests a failed or absent construction of the Dataset");
			throw new NullPointerException(
					"The data object inside the dataset has not been allocated, this sugests a failed or absent construction of the Dataset");
		}
		return data.length;
	}

	/**
	 * Function that gets the size in each dimension of the dataset
	 * 
	 * @return an integer array of the size of each direction of the dataset
	 */
	public int[] getDimensions() {
		// make a copy of the dimensions data, and put that out
		int[] dims = new int[dimensions.length];
		for (int i = 0; i < dimensions.length; i++) {
			dims[i] = dimensions[i];
		}
		return dims;
	}

	/**
	 * Function that uses the knowledge of the dataset to calculate the position in the data array that corresponds to
	 * the int array n dimensional position. The input values <b>Must</b> be inside the arrays, this should be ok as
	 * this function is mainly code which will be run inside the get and set functions
	 * 
	 * @param n
	 *            the integer array specifying the n-D position
	 * @return the 1D position on the dataset corresponding to that location.
	 */
	private int get1DIndex(int... n) {
		if (n.length > dimensions.length)
			throw new IllegalArgumentException("No of index parameters is different to the dimensions of data\t"
					+ n.length + " given " + dimensions.length + "required");

		// once checked return the appropriate value.
		int index = n[0];

		if(dataDimensions == null) {
		
			for (int i = 1; i < n.length; i++) {
				index = (index * dimensions[i]) + n[i];
			}
		} else {
			for (int i = 1; i < n.length; i++) {
				index = (index * dataDimensions[i]) + n[i];
			}
		}

		return index;
	}

	/**
	 * The nD position in the dataset of the inputed 1d position in the data array
	 * 
	 * @param n
	 *            The 1D position in the array
	 * @return the corresponding [a,b,...,n] position in the dataset
	 */
	public int[] getNDIndex(int n) {
		if (n >= data.length)
			throw new IllegalArgumentException("Size of data provided \t" + n
					+ "is larger then the size of the containing array" + data.length);

		// first create the array holding the result.
		int[] output = new int[dimensions.length];

		int inValue = n;
		for (int i = output.length - 1; i > 0; i--) {
			output[i] = inValue % dimensions[i];
			inValue /= dimensions[i];
		}
		output[0] = inValue;

		return output;
	}

	/**
	 * Check the index given against the dimensions to make sure it is valid
	 * 
	 * @param n
	 * @return boolean
	 */
	private boolean checkValidIndex(int... n) {
		// check the dimensionality of the request

		// if its too large then throw an exception
		if (n.length > dimensions.length) {
			throw new IllegalArgumentException("Dimensionality of request and " + "dataset are incompatible "
					+ n.length + " requested and the internal " + "dimensions are " + dimensions.length);
		}

		// if its the right size, check to see if its in bounds
		if (n.length == dimensions.length) {
			for (int i = 0; i < n.length; i++) {
				if (n[i] < 0 || n[i] >= dimensions[i]) {
					return false;
				}
			}
		}

		// if its less than the dimensionality, assume that the
		// user knows what they're doing.

		return true;
	}

	/**
	 * This function takes a dataset and checks its shape against the current dataset. If they are both of the same
	 * size, then this returns with no error, if there is a problem, then an error is thrown.
	 *
	 * @param g
	 *            The dataset to be compared
	 * @throws IllegalArgumentException
	 *             This will be thrown if there is a problem with the compatibility
	 */
	private void checkCompatibility(DataSet g) throws IllegalArgumentException {
		if (g.getDimensions().length != dimensions.length)
			throw new IllegalArgumentException("Incompatible dimensions");
		if (!Arrays.equals(g.getDimensions(), dimensions)) {
			throw new IllegalArgumentException("Incompatible dimensions");
		}
	}

	/**
	 * Gets a value from the data array of the object
	 * 
	 * @param n
	 *            the position to get out
	 * @return the value in the data array
	 */
	public double get(int n) {
		int[] array = { n };
		return get(array);
	}

	/**
	 * Function to allow other functions to get Absolute positions in the internal array. This is required and faster
	 * for some simple point by point operations
	 * 
	 * @param n
	 *            The absolute position in the array
	 * @return The double which is at the position n
	 */
	public double getAbs(int n) {
		return data[n];
	}

	/**
	 * Function to allow other functions to set Absolute positions in the internal array. This is required and faster
	 * for some simple point by point operations
	 * 
	 * @param val
	 *            The new value to set the position to
	 * @param n
	 *            The absolute position in the array
	 */
	public void setAbs(double val, int n) {
		data[n] = val;
		setDirty();
	}

	/**
	 * Sets the value at a particular point to the passed value, WARNING, this will overwrite the data currently stored
	 * there without any other warnings!!
	 * 
	 * @param value
	 *            The double value to be set
	 * @param n
	 *            the position to set the value into
	 */
	public void set(double value, int n) {
		try {
			if (checkValidIndex(n)) {
				data[n] = value;
			} else {
				// Try to reallocate the array to make it large enough to sort
				// out
				// the potential problem
				try {
					allocateArray(n + 1);
					data[n] = value;
				} catch (OutOfMemoryError me) {
					// this cannot happen, so fall back to the original plan of
					// bugging out.
					logger.error("This request is outside the array boundaries, "
							+ "and there is not enough memory to increase the dataset's size");
				}
			}
		} catch (ArrayIndexOutOfBoundsException e) {
			logger.error("Cannot get value from dataset" + this + " The index is out of bounds.");
			throw e;

		}
		setDirty();
	}

	/**
	 * remember to call setDirty on the dataset, if you use this method to change any data!!!!
	 * 
	 * @return double[]
	 */
	public double[] getBuffer() {
		return data;
	}

	/**
	 * Gets a value from the data array of the object
	 * 
	 * @param n
	 *            the vector position to get out
	 * @return the value in the data array
	 */
	public double get(int... n) {
		try {
			if (checkValidIndex(n)) {
				return data[get1DIndex(n)];
			}
			throw new IllegalArgumentException("Index not valid");

		} catch (IllegalArgumentException e) {
			logger.error("Cannot get value from dataset" + this + " The number of indexes is incorrect.");
			throw e;
		} catch (ArrayIndexOutOfBoundsException e) {
			logger.error("Cannot get value from dataset" + this + " The index is out of bounds.");
			throw e;
		}
	}

	/**
	 * Sets the value at a particular point to the passed value, WARNING, this will overwrite the data currently stored
	 * there without any other warnings!!
	 * 
	 * @param value
	 *            The double value to be set
	 * @param n
	 *            the array position to set the value into
	 */
	public void set(double value, int... n) {
		try {
			if (checkValidIndex(n)) {
				data[get1DIndex(n)] = value;
			} else {
				// Try to reallocate the array to make it large enough to sort
				// out
				// the potential problem
				try {

					// allocate a new array holding the new dimensions
					int[] dims = new int[n.length];
					for (int i = 0; i < n.length; i++) {
						if(n[i] >= (dimensions[i])) {
							dims[i] = n[i]+1;
						} else {
							dims[i] = dimensions[i];
						}
					}
					allocateArray(dims);
					data[get1DIndex(n)] = value;

				} catch (OutOfMemoryError me) {
					// this cannot happen, so fall back to the original plan of
					// bugging out.
					logger.error("This request is outside the array boundaries, "
							+ "and there is not enough memory to increase the dataset's size");
				}

			}
		} catch (IllegalArgumentException e) {
			logger.error("Cannot get value from dataset" + this + " The number of indexes is incorect.");
			throw e;

		} catch (ArrayIndexOutOfBoundsException e) {
			logger.error("Index out of bounds");
			throw e;
		}
		setDirty();
	}

	/**
	 * Function that returns the jama matrix of the 2D dataset
	 * 
	 * @return The jama Matrix of the whole object
	 * @throws IllegalArgumentException
	 *             This is thrown if there are any problems, but mainly if the dataset isnt a 2D set that can be turned
	 *             into a matrix.
	 */
	public Matrix getJamaMatrix() throws IllegalArgumentException {
		try {
			return new Matrix(this.doubleMatrix());
		} catch (IllegalArgumentException e) {
			logger.error(this + " needs to be passed the a 2 dimensional dataset, you passed it a "
					+ this.dimensions.length + " size Vector");
			throw new IllegalArgumentException(this
					+ " needs to be passed the a 2 dimensional dataset, you passed it a " + this.dimensions.length
					+ " size dataset");
		}
	}

	/**
	 * Function that returns a double array of the data in the Dataset
	 * 
	 * @return The double array containing the data
	 */
	public synchronized double[] doubleArray() {

		double[] result = new double[this.data.length];
		for (int i = 0; i < result.length; i++) {
			result[i] = this.data[i];
		}
		return result;
	}

	/**
	 * Function that returns a 2D double array of the data in the dataset
	 * 
	 * @return The 2D array of doubles
	 * @throws IllegalArgumentException
	 *             This is thrown if the dataset can't be passed as a Matrix
	 */
	public synchronized double[][] doubleMatrix() throws IllegalArgumentException {

		// only return if its a 2D dataset
		if (this.dimensions.length != 2) {
			logger.error(this + " needs to be passed the a 2 dimensional dataset, you passed it a "
					+ this.dimensions.length + " size dataset");
			throw new IllegalArgumentException(this
					+ " needs to be passed the a 2 dimensional dataset, you passed it a " + this.dimensions.length
					+ " size dataset");
		}

		double[][] result = new double[this.dimensions[0]][this.dimensions[1]];
		for (int i = 0; i < this.dimensions[0]; i++) {
			for (int j = 0; j < this.dimensions[1]; j++) {
				result[i][j] = this.get(i, j);
			}
		}

		return result;
	}

	/**
	 * @param other
	 * @return DataSet
	 * @see gda.analysis.DataSet
	 */
	public Object __add__(DataSet other) {
		return DatasetMaths.sum(this, other);
	}

	/**
	 * @param other
	 * @return DataSet
	 * @see gda.analysis.DataSet
	 */
	public Object __add__(double other) {

		return DatasetMaths.sum(this, other);

	}

	/**
	 * @param other
	 * @return DataSet
	 * @see gda.analysis.DataSet
	 */
	public Object __radd__(double other) {
		return DatasetMaths.sum(this, other);
	}

	/**
	 * In-place addition
	 *
	 * @param other
	 *            dataset
	 * @return self
	 */
	public DataSet __iadd__(DataSet other) {
		checkCompatibility(other);

		for (int i = 0; i < data.length; i++) {
			data[i] += other.get(i);
		}
		setDirty();
		return this;
	}

	/**
	 * In-place addition
	 *
	 * @param other
	 *            double
	 * @return self
	 */
	public DataSet __iadd__(double other) {

		for (int i = 0; i < data.length; i++) {
			data[i] += other;
		}
		setDirty();
		return this;
	}

	/**
	 * @param other
	 * @return DataSet
	 * @see gda.analysis.DataSet
	 */
	public Object __sub__(DataSet other) {

		return DatasetMaths.sub(this, other);

	}

	/**
	 * @param other
	 * @return DataSet
	 * @see gda.analysis.DataSet
	 */
	public Object __sub__(double other) {

		return DatasetMaths.sub(this, other);
	}

	/**
	 * @param other
	 * @return DataSet
	 * @see gda.analysis.DataSet
	 */
	public Object __rsub__(double other) {

		return DatasetMaths.sub(other, this);
	}

	/**
	 * In-place subtraction
	 *
	 * @param other
	 *            dataset
	 * @return self
	 */
	public DataSet __isub__(DataSet other) {
		checkCompatibility(other);

		for (int i = 0; i < data.length; i++) {
			data[i] -= other.get(i);
		}
		setDirty();
		return this;
	}

	/**
	 * In-place subtraction
	 *
	 * @param other
	 *            double
	 * @return self
	 */
	public DataSet __isub__(double other) {

		for (int i = 0; i < data.length; i++) {
			data[i] -= other;
		}
		setDirty();
		return this;
	}

	/**
	 * @param other
	 * @return DataSet
	 * @see gda.analysis.DataSet
	 */
	public Object __div__(DataSet other) {

		return DatasetMaths.div(this, other);
	}

	/**
	 * @param other
	 * @return DataSet
	 * @see gda.analysis.DataSet
	 */
	public Object __div__(double other) {
		return DatasetMaths.div(this, other);
	}

	/**
	 * @param other
	 * @return DataSet
	 * @see gda.analysis.DataSet
	 */
	public Object __rdiv__(double other) {
		return DatasetMaths.div(other, this);
	}

	/**
	 * In-place division
	 *
	 * @param other
	 *            dataset
	 * @return self
	 */
	public DataSet __idiv__(DataSet other) {
		checkCompatibility(other);

		for (int i = 0; i < data.length; i++) {
			data[i] /= other.get(i);
			setDirty();
		}
		return this;
	}

	/**
	 * In-place division
	 *
	 * @param other
	 *            double
	 * @return self
	 */
	public DataSet __idiv__(double other) {

		for (int i = 0; i < data.length; i++) {
			data[i] /= other;
		}
		setDirty();
		return this;
	}

	/**
	 * @param other
	 * @return DataSet
	 * @see gda.analysis.DataSet
	 */
	public Object __mul__(DataSet other) {

		return DatasetMaths.mul(this, other);
	}

	/**
	 * @param other
	 * @return DataSet
	 * @see gda.analysis.DataSet
	 */
	public Object __mul__(double other) {
		return DatasetMaths.mul(this, other);
	}

	/**
	 * @param other
	 * @return DataSet
	 * @see gda.analysis.DataSet
	 */
	public Object __rmul__(double other) {
		return DatasetMaths.mul(this, other);
	}

	/**
	 * In-place multiplication
	 *
	 * @param other
	 *            dataset
	 * @return self
	 */
	public DataSet __imul__(DataSet other) {
		checkCompatibility(other);

		for (int i = 0; i < data.length; i++) {
			data[i] *= other.get(i);
		}
		setDirty();
		return this;
	}

	/**
	 * In-place multiplication
	 *
	 * @param other
	 *            double
	 * @return self
	 */
	public DataSet __imul__(double other) {

		for (int i = 0; i < data.length; i++) {
			data[i] *= other;
		}
		setDirty();
		return this;
	}

	/**
	 * @param other
	 * @return DataSet
	 * @see gda.analysis.DataSet
	 */
	public Object __pow__(double other) {
		return DatasetMaths.pow(this, other);
	}

	/**
	 * In-place raising to the power of
	 *
	 * @param other
	 * @return DataSet
	 * @see gda.analysis.DataSet
	 */
	public DataSet __ipow__(double other) {
		for (int i = 0; i < data.length; i++) {
			try {
				data[i] = Math.pow(data[i], other);
			} catch (Exception e) {
				System.out.println(e);
				throw new IllegalArgumentException("Can't raise negative number to a fractional power");
			}
		}
		setDirty();
		return this;
	}

	// Logical Operators

	/**
	 * overriding the "==" operator.<br>
	 * <br>
	 * This returns true if the magnitudes of the 2 vectors are identical <br>
	 * <br>
	 * <i><b>Warning!! as this is using floating point accuracy, two processed <br>
	 * vectors are very unlikely to be equal, so be careful using this!</b></i><br>
	 * 
	 * @param other
	 *            The DataVector1D value after the '==' sign
	 * @return PyInteger, containing 1 for true, and 0 for false.
	 */
	public Object __eq__(DataSet other) {

		double V1 = 0.0;
		double V2 = 0.0;

		for (int i = 0; i < data.length; i++) {
			V1 = V1 + this.data[i] * this.data[i];
			V2 = V2 + other.data[i] * other.data[i];

		}

		if (V1 == V2) {
			PyInteger output = new PyInteger(1);
			return output;
		}
		PyInteger out2 = new PyInteger(0);

		return out2;
	}

	/**
	 * overriding the "!=" operator.<br>
	 * <br>
	 * This returns false if the magnitudes of the 2 vectors are identical <br>
	 * <br>
	 * <i><b>Warning!! as this is using floating point accuracy, two processed <br>
	 * vectors are very unlikely to be equal, so be careful using this!</b></i><br>
	 * 
	 * @param other
	 *            The DataVector1D value after the '!=' sign
	 * @return PyInteger, containing 1 for true, and 0 for false.
	 */
	public Object __ne__(DataSet other) {

		double V1 = 0.0;
		double V2 = 0.0;

		for (int i = 0; i < data.length; i++) {
			V1 = V1 + this.data[i] * this.data[i];
			V2 = V2 + other.data[i] * other.data[i];

		}

		if (V1 != V2) {
			PyInteger output = new PyInteger(1);
			return output;
		}
		PyInteger out2 = new PyInteger(0);
		return out2;
	}

	/**
	 * overriding the unary "-" operator <br>
	 * This returns a new dataset with values of opposite sign
	 *
	 * @return negative dataset
	 */
	public Object __neg__() {
		return DatasetMaths.neg(this);
	}

	/**
	 * overriding the ">" operator.<br>
	 * <br>
	 * This returns true if the first vectors is greater than the magnitude of the second vector<br>
	 * <br>
	 * 
	 * @param other
	 *            The DataVector1D value after the '>' sign
	 * @return PyInteger, containing 1 for true, and 0 for false.
	 */
	public Object __gt__(DataSet other) {

		double V1 = 0.0;
		double V2 = 0.0;

		for (int i = 0; i < data.length; i++) {
			V1 = V1 + this.data[i] * this.data[i];
			V2 = V2 + other.data[i] * other.data[i];

		}

		if (V1 > V2) {
			PyInteger output = new PyInteger(1);
			return output;
		}
		PyInteger out2 = new PyInteger(0);
		return out2;
	}

/**
	 * overriding the "<" operator.<br>
	 * <br>
	 * This returns false if the first vectors is greater than the magnitude of the second vector<br>
	 * <br>
	 * 
	 * @param other
	 *            The DataVector1D value after the '<' sign
	 * @return PyInteger, containing 1 for true, and 0 for false.
	 */
	public Object __lt__(DataSet other) {

		double V1 = 0.0;
		double V2 = 0.0;

		for (int i = 0; i < data.length; i++) {
			V1 = V1 + this.data[i] * this.data[i];
			V2 = V2 + other.data[i] * other.data[i];

		}

		if (V1 < V2) {
			PyInteger output = new PyInteger(1);
			return output;
		}
		PyInteger out2 = new PyInteger(0);
		return out2;
	}

	/**
	 * overriding the ">=" operator.<br>
	 * <br>
	 * This returns true if the first vector is greater than or equal to the magnitude of the second vector<br>
	 * <br>
	 * 
	 * @param other
	 *            The DataVector1D value after the '>=' sign
	 * @return PyInteger, containing 1 for true, and 0 for false.
	 */
	public Object __ge__(DataSet other) {

		double V1 = 0.0;
		double V2 = 0.0;

		for (int i = 0; i < data.length; i++) {
			V1 = V1 + this.data[i] * this.data[i];
			V2 = V2 + other.data[i] * other.data[i];

		}

		if (V1 >= V2) {
			PyInteger output = new PyInteger(1);
			return output;
		}
		PyInteger out2 = new PyInteger(0);
		return out2;
	}

	/**
	 * overriding the "<=" operator.<br>
	 * <br>
	 * This returns true if the first vectors is less than or equal to the magnitude of the second vector<br>
	 * <br>
	 * 
	 * @param other
	 *            The DataVector1D value after the '<=' sign
	 * @return PyInteger, containing 1 for true, and 0 for false.
	 */
	public Object __le__(DataSet other) {

		double V1 = 0.0;
		double V2 = 0.0;

		for (int i = 0; i < data.length; i++) {
			V1 = V1 + this.data[i] * this.data[i];
			V2 = V2 + other.data[i] * other.data[i];

		}

		if (V1 <= V2) {
			PyInteger output = new PyInteger(1);
			return output;
		}
		PyInteger out2 = new PyInteger(0);
		return out2;
	}

	/**
	 * Jython overloaded function to allow for data to be obtained as a jython container
	 * 
	 * @param value
	 *            The number of the point to be interrogated
	 * @return the object containing true
	 */
	@SuppressWarnings("unused")
	public Object __contains__(Integer value) {
		return true;
	}

	/**
	 * Jython overloaded function to allow for data to be obtained as a jython container
	 * 
	 * @param index
	 *            The number of the point to be interrogated
	 * @return the object which is the result
	 */
	public Object __getitem__(Integer index) {

		if (index < -dimensions[0] || index >= dimensions[0]) {
			logger.error("The value {} is not within the dataset's bounds", index);
			throw new PyException(Py.IndexError);
		}
		if (index < 0)
			index += dimensions[0];

		// first check the dimensionality
		if (dimensions.length == 1) {
			return data[index];
		}
		// otherwise slice
		Object[] indexes = {index};
		return __getitem__(indexes);
	}

	/**
	 * @param index array
	 * @return Dataset of specifies item
	 */
	public Object __getitem__(Integer[] index) {
		int[] start = new int[dimensions.length];
		// first check the dimensionality
		int vlen;
		if (index.length > dimensions.length) {
			vlen = dimensions.length;
		} else if (index.length == dimensions.length) {
			vlen = index.length;
		} else {
			// incomplete indexes implies slice
			return __getitem__((Object[]) index);
		}
		int i;
		for (i = 0; i < vlen; i++) {
			int d = index[i];
			if (d < -dimensions[i] || d >= dimensions[i]) {
				logger.error("The value {} is not within the dataset's bounds", index);
				throw new PyException(Py.IndexError);
			}
			if (d < 0)
				d += dimensions[i];
			start[i] = d;
		}
		for (; i < dimensions.length; i++) {
			start[i] = 0;
		}
		return get(start);
	}

	/**
	 * @param slice
	 * @return Dataset of specified slice
	 */
	public DataSet __getitem__(PySlice slice) {
		int start, stop, step;

		// start
		if (slice.start instanceof PyNone) {
			start = 0;
		} else {
			start = ((PyInteger) slice.start).getValue();
		}

		// stop
		if (slice.stop instanceof PyNone) {
			stop = dimensions[0];
		} else {
			stop = ((PyInteger) slice.stop).getValue();
		}

		// step
		if (slice.step instanceof PyNone) {
			step = 1;
		} else {
			step = ((PyInteger) slice.step).getValue();
		}

		return getSlice(start, stop, step);
	}

	/**
	 * @param indexes can be a mixed array of integers or slices
	 * @return Dataset of specified sub-dataset
	 */
	public DataSet __getitem__(Object[] indexes) {
		int[] start, stop, step;
		int slen;

		// first check the dimensionality
		if (indexes.length > dimensions.length) {
			slen = dimensions.length;
		} else {
			slen = indexes.length;
		}
		start = new int[dimensions.length];
		stop = new int[dimensions.length];
		step = new int[dimensions.length];
		boolean[] rdim = new boolean[dimensions.length];
		int rank = 0;

		int i;
		for (i = 0; i < slen; i++) {
			if (indexes[i] instanceof Integer) {
				// nb specifying indexes whilst using slices will reduce rank
				rdim[i] = true;
				start[i] = (Integer) indexes[i];
				if (start[i] < -dimensions[i] || start[i] >= dimensions[i]) {
					logger.error("The value {} is not within the dataset's bounds", start);
					throw new PyException(Py.IndexError);
				}
				if (start[i] < 0)
					start[i] += dimensions[i];

				stop[i] = start[i] + 1;
				step[i] = 1;
			} else if (indexes[i] instanceof PySlice) {
				rdim[i] = false;
				rank++;
				PySlice slice = (PySlice) indexes[i];
				// start
				if (slice.start instanceof PyNone) {
					start[i] = 0;
				} else {
					start[i] = ((PyInteger) slice.start).getValue();
				}

				// stop
				if (slice.stop instanceof PyNone) {
					stop[i] = dimensions[i];
				} else {
					stop[i] = ((PyInteger) slice.stop).getValue();
				}

				// step
				if (slice.step instanceof PyNone) {
					step[i] = 1;
				} else {
					step[i] = ((PyInteger) slice.step).getValue();
				}
			}
		}
		for (; i < dimensions.length; i++) {
			rdim[i] = false;
			rank++;
			start[i] = 0;
			stop[i] = dimensions[i];
			step[i] = 1;
		}
		DataSet dataSlice = getSlice(start, stop, step);
		if (rank < dimensions.length) {
			int[] oldShape = dataSlice.getDimensions();
			int[] newShape = new int[rank];
			int j = 0;
			for (i = 0; i < dimensions.length; i++) {
				if (!rdim[i]) {
					newShape[j++] = oldShape[i];
				}
			}
			dataSlice.resize(newShape);
		}
		return dataSlice;
	}

	/**
	 * Not implemented, as you can't remove an element from this type of class
	 * 
	 * @param index
	 * @return null;
	 */
	@SuppressWarnings("unused")
	public Object __delitem__(Integer index) {
		return null;
	}

	/**
	 * @param index
	 * @param newValue
	 */
	public void __setitem__(Integer index, Double newValue) {
		if (dimensions.length > 1) {
			logger.error("Cannot set an implicit slice to a single value");
			throw new PyException(Py.NotImplementedError);
		}
		if (index < -data.length || index >= data.length) {
			logger.error("The value {} is not within the dataset's bounds", index);
			throw new PyException(Py.IndexError);
		}
		if (index < 0)
			index += data.length;

		data[index] = newValue;
	}

	/**
	 * @param index array
	 * @param newValue
	 */
	public void __setitem__(Integer[] index, Double newValue) {
		int[] start = new int[dimensions.length];
		// first check the dimensionality
		int vlen;
		if (index.length > dimensions.length) {
			vlen = dimensions.length;
		} else {
			vlen = index.length;
		}
		int i;
		for (i = 0; i < vlen; i++) {
			start[i] = index[i];
			if (start[i] < -dimensions[i] || start[i] >= dimensions[i]) {
				logger.error("The value {} is not within the dataset's bounds", start);
				throw new PyException(Py.IndexError);
			}
			if (start[i] < 0)
				start[i] += dimensions[i];
		}
		for (; i < dimensions.length; i++) {
			start[i] = 0;
		}

		set(newValue, start);
	}

	/**
	 * @param slice
	 * @param newValue
	 */
	public void __setitem__(PySlice slice, Double newValue) {
		int start, stop, step;

		// start
		if (slice.start instanceof PyNone) {
			start = 0;
		} else {
			start = ((PyInteger) slice.start).getValue();
		}

		// stop
		if (slice.stop instanceof PyNone) {
			stop = dimensions[0];
		} else {
			stop = ((PyInteger) slice.stop).getValue();
		}

		// step
		if (slice.step instanceof PyNone) {
			step = 1;
		} else {
			step = ((PyInteger) slice.step).getValue();
		}

		setSlice(start, stop, step, newValue);
	}

	/**
	 * @param slice
	 * @param newValues
	 */
	public void __setitem__(PySlice slice, DataSet newValues) {
		int start, stop, step;

		// start
		if (slice.start instanceof PyNone) {
			start = 0;
		} else {
			start = ((PyInteger) slice.start).getValue();
		}

		// stop
		if (slice.stop instanceof PyNone) {
			stop = dimensions[0];
		} else {
			stop = ((PyInteger) slice.stop).getValue();
		}

		// step
		if (slice.step instanceof PyNone) {
			step = 1;
		} else {
			step = ((PyInteger) slice.step).getValue();
		}

		setSlice(start, stop, step, newValues);
	}

	/**
	 * @param slice
	 * @param newValue
	 */
	public void __setitem__(PySlice[] slice, Double newValue) {
		int[] start, stop, step;
		int slen;
		// first check the dimensionality
		if (slice.length > dimensions.length) {
			slen = dimensions.length;
		} else {
			slen = slice.length;
		}
		start = new int[dimensions.length];
		stop = new int[dimensions.length];
		step = new int[dimensions.length];
		int i;
		for (i = 0; i < slen; i++) {
			// start
			if (slice[i].start instanceof PyNone) {
				start[i] = 0;
			} else {
				start[i] = ((PyInteger) slice[i].start).getValue();
			}

			// stop
			if (slice[i].stop instanceof PyNone) {
				stop[i] = dimensions[i];
			} else {
				stop[i] = ((PyInteger) slice[i].stop).getValue();
			}

			// step
			if (slice[i].step instanceof PyNone) {
				step[i] = 1;
			} else {
				step[i] = ((PyInteger) slice[i].step).getValue();
			}
		}
		for (; i < dimensions.length; i++) {
			start[i] = 0;
			stop[i] = dimensions[i];
			step[i] = 1;
		}
		setSlice(start, stop, step, newValue);
	}

	/**
	 * @param slice
	 * @param newValues
	 */
	public void __setitem__(PySlice[] slice, DataSet newValues) {
		int[] start, stop, step;
		int slen;
		// first check the dimensionality
		if (slice.length > dimensions.length) {
			slen = dimensions.length;
		} else {
			slen = slice.length;
		}
		start = new int[dimensions.length];
		stop = new int[dimensions.length];
		step = new int[dimensions.length];
		int i;
		for (i = 0; i < slen; i++) {
			// start
			if (slice[i].start instanceof PyNone) {
				start[i] = 0;
			} else {
				start[i] = ((PyInteger) slice[i].start).getValue();
			}

			// stop
			if (slice[i].stop instanceof PyNone) {
				stop[i] = dimensions[i];
			} else {
				stop[i] = ((PyInteger) slice[i].stop).getValue();
			}

			// step
			if (slice[i].step instanceof PyNone) {
				step[i] = 1;
			} else {
				step[i] = ((PyInteger) slice[i].step).getValue();
			}
		}
		for (; i < dimensions.length; i++) {
			start[i] = 0;
			stop[i] = dimensions[i];
			step[i] = 1;
		}
		setSlice(start, stop, step, newValues);
	}

	/**
	 * Gets the number of objects in the class
	 * 
	 * @return An object integer containing the number of elements.
	 */
	public Object __len__() {
		return dataSize();
	}

	/**
	 * Converts a string buffer to a printable string (work-around current limitation of using a String)
	 *
	 * @param displayString
	 * @return sanitized string
	 */
	private String sanitizeLine(StringBuffer displayString) {
		if (displayString.length() > maxDisplayLength) {
			int excess = displayString.length() - maxDisplayLength + 5;
			String out = displayString.substring(0, (displayString.length() - excess) / 2);
			out += "\t...\t";
			out += displayString.substring((displayString.length() + excess) / 2, displayString.length());
			return out;
		}
		return displayString.toString();
	}

	/**
	 * Simple function that displays the information inside the dataset to the Jython terminal. All the data found here
	 * can be replicated with other functions and this is simply to display the data.
	 */
	public void disp() {
		StringBuffer Out = new StringBuffer();

		int Dimensions[] = this.getDimensions();

		Out.append("DataSet Dimensions are [" + Dimensions[0]);

		for (int i = 1; i < Dimensions.length; i++) {
			Out.append(", " + Dimensions[i]);
		}

		Out.append("]");

		InterfaceProvider.getTerminalPrinter().print(Out.toString());
		Out.delete(0, Out.length());

		int outputDimensions[] = new int[Dimensions.length];
		for (int i = 0; i < Dimensions.length; i++) {
			outputDimensions[i] = Dimensions[i];
		}

		// if the dataset is too big, clip the size of the data so its
		// possible to display it on the screen easily

		/*
		 * int clipped = 0; for (int i = 0; i < Dimensions.length; i++) { if (Dimensions[i] > 6) { clipped = 1;
		 * outputDimensions[i] = 6; } else { outputDimensions[i] = Dimensions[i]; } } if (clipped == 1) { Out = Out +
		 * "DataVector Output clipped in size\n"; }
		 */

		// First get the dimensionality of the vector
		if (outputDimensions.length == 1) {

			Out.append(String.format("[\t%.4e", get(0)));

			for (int i = 1; i < outputDimensions[0]; i++) {
				Out.append(String.format(",\t%.4e", get(i)));
			}

			Out.append("\t]");
			InterfaceProvider.getTerminalPrinter().print(sanitizeLine(Out));
		}

		if (outputDimensions.length == 2) {

			for (int x = 0; x < outputDimensions[0]; x++) {
				Out.append(String.format("|\t%.4e", get(x, 0)));

				for (int y = 1; y < outputDimensions[1]; y++) {
					Out.append(String.format(",\t%.4e", get(x, y)));
				}

				Out.append("\t|");
				InterfaceProvider.getTerminalPrinter().print(sanitizeLine(Out));
				Out.delete(0, Out.length());

			}

		}

		if (outputDimensions.length == 3) {

			for (int z = 0; z < outputDimensions[2]; z++) {

				Out.append("\t----------");
			}
			InterfaceProvider.getTerminalPrinter().print(Out.toString());
			Out.delete(0, Out.length());

			for (int x = 0; x < outputDimensions[0]; x++) {

				for (int y = 0; y < outputDimensions[1]; y++) {

					Out.append(String.format("|\t%.4e", get(x, y, 0)));

					for (int z = 1; z < outputDimensions[2]; z++) {

						Out.append(String.format(",\t%.4e", get(x, y, z)));
					}

					Out.append("\t|");
					InterfaceProvider.getTerminalPrinter().print(sanitizeLine(Out));
					Out.delete(0, Out.length());
				}

				for (int z = 0; z < outputDimensions[2]; z++) {
					Out.append("\t----------");
				}
				InterfaceProvider.getTerminalPrinter().print(Out.toString());
				Out.delete(0, Out.length());
			}
		}

		if (outputDimensions.length > 3) {
			Out.append("<" + outputDimensions[0]);

			for (int i = 1; i < outputDimensions.length; i++) {
				Out.append(outputDimensions[i] + ",");
			}

			Out.append(">");
			InterfaceProvider.getTerminalPrinter().print(Out.toString());
			Out.delete(0, Out.length());

			Out.append("[" + get(0));

			for (int i = 1; i < data.length; i++) {
				Out.append("," + get(i));
			}

			Out.append("]");
			InterfaceProvider.getTerminalPrinter().print(sanitizeLine(Out));
		}

	}

	/**
	 * Append dataset with another dataset along n-th axis
	 * 
	 * @param other
	 * @param axis
	 *            number of axis or -1 for last one
	 * @return appended dataset
	 */
	public DataSet append(DataSet other, int axis) {
		int[] olddims = getDimensions();
		int[] othdims = other.getDimensions();
		if (olddims.length != othdims.length) {
			throw new IllegalArgumentException("Incompatible number of dimensions");
		}
		if (axis >= olddims.length)
			throw new IllegalArgumentException("Axis specified exceeds array dimensions");
		else if (axis == -1)
			axis = olddims.length - 1;
		else if (axis < -1)
			throw new IllegalArgumentException("Axis specified is less than -1");

		for (int i = 0; i < olddims.length; i++) {
			if (i != axis && olddims[i] != othdims[i])
				throw new IllegalArgumentException("Incompatible dimensions");
		}

		int[] newdims = new int[olddims.length];
		for (int i = 0; i < olddims.length; i++) {
			newdims[i] = olddims[i];
		}
		newdims[axis] += othdims[axis];
		DataSet ds = new DataSet(newdims);
		for (int l = 0; l < ds.dataSize(); l++) {
			int[] n = ds.getNDIndex(l);
			boolean isold = true;
			for (int m = 0; m < newdims.length; m++) {
				if (n[m] >= olddims[m]) { // check which array is loop passing through
					isold = false;
					n[m] -= olddims[m];
					break;
				}
			}
			if (isold) {
				ds.set(this.get(n), l);
			} else {
				ds.set(other.get(n), l);
			}
		}

		return ds;
	}

	/**
	 * Fill dataset with given value
	 * 
	 * @param value
	 *            fill value
	 */
	public void fill(double value) {
		for (int i = 0; i < data.length; i++) {
			data[i] = value;
		}
	}

	/**
	 * @param start
	 *            begin
	 * @param stop
	 *            end
	 * @param step
	 *            interval
	 * @return Evenly spaced values in semi-open interval given by parameters
	 */
	public static DataSet arange(double start, double stop, double step) {
		if (start >= stop) {
			throw new IllegalArgumentException("Start value greater than or equal stop value");
		}
		int dlength = (int) Math.floor((stop - start) / step);
		DataSet ds = new DataSet(dlength);
		double value = start;

		for (int i = 0; i < dlength; i++) {
			ds.set(value, i);
			value += step;
		}
		return ds;
	}

	/**
	 * @param start
	 *            begin
	 * @param stop
	 *            end
	 * @return Values spaced by 1.0 in semi-open interval given by parameters
	 */
	public static DataSet arange(double start, double stop) {
		return arange(start, stop, 1.0);
	}

	/**
	 * @param stop
	 *            end
	 * @return Values from 0.0 spaced by 1.0 in semi-open interval up to (but not including) parameter
	 */
	public static DataSet arange(double stop) {
		return arange(0.0, stop, 1.0);
	}

	/**
	 * Jython method to create a DataSet
	 *
	 * @param list
	 * @return dataset populated by items in list
	 */
	public static DataSet array(PySequenceList list) {
		return new DataSet(list);
	}

	@Override
	public DataSet clone() {
		return new DataSet(this);
	}

	/**
	 * Makes new dataset based on current dataset with new shape
	 * NB API change: use resize for old behaviour
	 *
	 * @param dimensions
	 * @return reshaped new DataSet
	 */
	public DataSet reshape(int... dimensions) {
		DataSet newData = new DataSet(this);
		newData.resize(dimensions);
		return newData;
	}

	/**
	 * Set new shape to existing dataset
	 * 
	 * @param dimensions
	 *            new shape
	 */
	public void resize(int... dimensions) {
		int size = 1;
		for (int i = 0; i < dimensions.length; i++) {
			// make sure the indexes isn't zero or negative
			if (dimensions[i] <= 0) {
				logger.error("Argument " + i + " is " + dimensions[i]
						+ " which is an illegal argument as it is zero or negative");
				throw new IllegalArgumentException("Argument " + i + " is " + dimensions[i]
						+ " which is an illegal argument as it is zero or negative");
			}

			size = size * dimensions[i];
		}
		if (size != data.length) {
			logger.error("New shape (" + dimensions + ") is not compatible with old shape (" + this.dimensions + ")");
			throw new IllegalArgumentException("New shape (" + dimensions + ") is not compatible with old shape ("
					+ this.dimensions + ")");
		}
		this.dimensions = dimensions;
	}

	/**
	 * @param start
	 *            begin
	 * @param stop
	 *            end
	 * @param length
	 *            number of points
	 * @return Values in closed interval given by parameters
	 */
	public static DataSet linspace(double start, double stop, int length) {
		if (length < 1 || start > stop) {
			throw new IllegalArgumentException("Length is less than one or start is greater than stop");
		} else if (length == 1) {
			double[] d = { start };
			return new DataSet(d);
		} else {
			DataSet ds = new DataSet(length);
			double step = (stop - start) / (length - 1);
			double value;

			for (int i = 0; i < length; i++) {
				value = start + i * step;
				ds.set(value, i);
			}
			return ds;
		}
	}

	/**
	 * New dataset filled with ones
	 * @param shape
	 * @return one-filled dataset
	 */
	public static DataSet ones(int... shape) {
		DataSet ds = new DataSet(shape);
		ds.fill(1.);
		return ds;
	}

	/**
	 * New dataset filled with zeros
	 * @param shape
	 * @return zero-filled dataset
	 */
	public static DataSet zeros(int... shape) {
		DataSet ds = new DataSet(shape);
		ds.fill(0.);
		return ds;
	}

	/**
	 * @return DataSet
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public DataSet log10() {
		return DatasetMaths.log10(this);
	}

	/**
	 * @return DataSet
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public DataSet ln() {
		return DatasetMaths.ln(this);
	}

	/**
	 * @param power
	 * @return DataSet
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public DataSet pow(double power) {
		return DatasetMaths.pow(this, power);
	}

	/**
	 * @return DataSet
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public DataSet abs() {
		return DatasetMaths.abs(this);
	}

	/**
	 * @return DataSet
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public DataSet cos() {
		return DatasetMaths.cos(this);
	}

	/**
	 * @return DataSet
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public DataSet sin() {
		return DatasetMaths.sin(this);
	}

	/**
	 * @return DataSet
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public DataSet exp() {
		return DatasetMaths.exp(this);
	}

	/**
	 * @return double
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public double min() {
		if (dirtyMinValue == null) {
			calculateMinMaxMeanSumDeviation();
		}

		return dirtyMinValue;
	}

	/**
	 * @return integer
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public int[] minPos() {
		if (dirtyMinPos == null) {
			calculateMinMaxMeanSumDeviation();
		}

		return dirtyMinPos;
	}

	/**
	 * @return double
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public double max() {
		if (dirtyMaxValue == null) {
			calculateMinMaxMeanSumDeviation();
		}

		return dirtyMaxValue;

	}

	/**
	 * @return integer
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public int[] maxPos() {
		if (dirtyMaxPos == null) {
			calculateMinMaxMeanSumDeviation();
		}

		return dirtyMaxPos;
	}

	/**
	 * @return DataSet
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public double mean() {
		if (dirtyMeanValue == null) {
			calculateMinMaxMeanSumDeviation();
		}

		return dirtyMeanValue;
	}
	
	/**
	 * @return the range of the values in the dataset, i.e. the max - the min
	 */
	public double range() {
		if ((dirtyMaxValue == null)||(dirtyMinValue == null)) {
			calculateMinMaxMeanSumDeviation();
		}

		return (dirtyMaxValue - dirtyMinValue);
	}

	/**
	 * @return DataSet
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public double sum() {
		if (dirtySum == null) {
			calculateMinMaxMeanSumDeviation();
		}

		return dirtySum;
	}

	/**
	 * @return DataSet
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public double rms() {
		if (dirtyStandardDeviation == null) {
			calculateMinMaxMeanSumDeviation();
		}

		return dirtyStandardDeviation;
	}

	/**
	 * @return DataSet
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public double averageDeviation() {
		return DatasetMaths.getAverageDeviation(this);
	}

	/**
	 * @return DataSet
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public double skew() {
		return DatasetMaths.skew(this);
	}

	/**
	 * @return DataSet
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public double kurtosis() {
		return DatasetMaths.kurtosis(this);
	}

	/**
	 * @return DataSet
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public double[] centroid() {
		return DatasetMaths.centroid(this);
	}

	/**
	 * @param Comparison
	 * @return DataSet
	 * @see gda.analysis.utils.DatasetMaths
	 */
	public double chiSquared(DataSet Comparison) {
		return DatasetMaths.chiSquared(this, Comparison);
	}

	/**
	 * Function that gets the Datasets name i.e. the value in its name string. This can be useful for Axis information
	 * etc.
	 * 
	 * @return The name string
	 */
	public String getName() {
		return name;
	}

	/**
	 * Function that sets the String name of the class
	 * 
	 * @param name
	 *            The new name
	 */
	public void setName(String name) {
		this.name = name;
	}

	/**
	 * Function that returns a normalised dataset which is bounded between 0 and 1
	 * 
	 * @return the full dataset
	 */
	public DataSet norm() {
		DataSet temp = DatasetMaths.sub(this, this.min());
		temp = DatasetMaths.div(temp, temp.max());
		return temp;
	}

	/**
	 * Function that returns a normalised dataset which is bounded between 0 and 1 and has been distributed on a log10
	 * scale
	 * 
	 * @return the full dataset
	 */
	public DataSet lognorm() {
		DataSet temp = DatasetMaths.sub(this, this.min());
		temp = DatasetMaths.sum(temp, 1.0);
		temp = temp.log10();
		temp = DatasetMaths.div(temp, temp.max());
		return temp;
	}

	/**
	 * Function that returns a normalised dataset which is bounded between 0 and 1 and has been distributed on a ln
	 * scale
	 * 
	 * @return the full dataset
	 */
	public DataSet lnnorm() {
		DataSet temp = DatasetMaths.sub(this, this.min());
		temp = DatasetMaths.sum(temp, 1.0);
		temp = temp.ln();
		temp = DatasetMaths.div(temp, temp.max());
		return temp;
	}

	/**
	 * Most basic form, assumes the points are equally spaced and calculates the derivative based on that. Very rough
	 * and ready, but could be useful
	 * 
	 * @return The dataset containing the derivative.
	 */
	public DataSet diff() {
		return diff(1);
	}

	/**
	 * More interactive form of getting the derivative, which allows the user to select the amount of smoothing they
	 * want to use.
	 * 
	 * @param n
	 *            The spread on either side of the derivative calculation
	 * @return The dataset containing the derivative.
	 */
	public DataSet diff(int n) {
		// first make the x value dataset
		DataSet xValues = new DataSet(dataSize());
		for (int i = 0; i < dataSize(); i++) {
			xValues.set(i, i);
		}
		return DatasetMaths.derivative(xValues, this, n);
	}

	/**
	 * This calculates the derivative, based on the associated x coordinates passed to the function
	 * 
	 * @param xValues
	 *            the associated x values.
	 * @return The dataset containing the derivative
	 */
	public DataSet diff(DataSet xValues) {
		return DatasetMaths.derivative(xValues, this, 1);
	}

	/**
	 * This calculates the derivative, based on the associated x coordinates passed to the function
	 * 
	 * @param xValues
	 *            the associated x values.
	 * @param n
	 *            The spread on either side of the derivative calculation
	 * @return The dataset containing the derivative
	 */
	public DataSet diff(DataSet xValues, int n) {
		return DatasetMaths.derivative(xValues, this, n);
	}

	/**
	 * @param n
	 *            a list of all the starting points first, then all the end points
	 * @return The dataset of the subset of the data.
	 */
	@Deprecated
	public DataSet getSubset(int... n) {
		int nl = n.length;
		int m = n.length / 2;
		if (nl % 2 != 0) {
			logger.error(this + " needs an even number of arguments to get a subset of the data");
			throw new IllegalArgumentException("Need even no. of arguments to get a subset of the data");
		}
		if (m != this.dimensions.length) {
			logger.error(this + " need to be passed the corect number of indexes, you passed it " + m
					+ " pairs of bounds, and it needs " + this.dimensions.length + " pairs");
			throw new IllegalArgumentException("No of indexes does not match data dimensions you passed it " + m
					+ " pairs of bounds, and it needs " + this.dimensions.length + " pairs");
		}
		int[] startIndices = new int[m];
		int[] endIndices = new int[m];
		for (int i = 0; i < m; i++) {
			startIndices[i] = n[i];
			endIndices[i] = n[i + m] + 1;
		}
		return getSlice(startIndices, endIndices);
	}

	/**
	 * @param start
	 * @return slice
	 */
	public DataSet getSlice(int start) {
		return getSlice(new int[] { start }, null, null);
	}

	/**
	 * @param start
	 *            specifies the starting index
	 * @param stop
	 *            specifies the stopping index (nb, this is <b>not</b> included in the slice)
	 * @return The dataset of the sliced data.
	 */
	public DataSet getSlice(int start, int stop) {
		return getSlice(new int[] { start }, new int[] { stop }, null);
	}

	/**
	 * @param start
	 *            specifies the starting index
	 * @param stop
	 *            specifies the stopping index (nb, this is <b>not</b> included in the slice)
	 * @param step
	 *            specifies the step size
	 * @return The dataset of the sliced data.
	 */
	public DataSet getSlice(int start, int stop, int step) {
		return getSlice(new int[] { start }, new int[] { stop }, new int[] { step });
	}

	/**
	 * @param start
	 * @return slice
	 */
	public DataSet getSlice(int[] start) {
		return getSlice(start, null, null);
	}

	/**
	 * @param start
	 *            specifies the starting indexes
	 * @param stop
	 *            specifies the stopping indexes (nb, these are <b>not</b> included in the slice)
	 * @return The dataset of the sliced data.
	 */
	public DataSet getSlice(int[] start, int[] stop) {
		return getSlice(start, stop, null);
	}

	/**
	 * This is modelled after the NumPy array slice
	 *
	 * @param start
	 *            specifies the starting indexes
	 * @param stop
	 *            specifies the stopping indexes (nb, these are <b>not</b> included in the slice)
	 * @param step
	 *            specifies the steps in the slice
	 * @return The dataset of the sliced data.
	 */
	public DataSet getSlice(int[] start, int[] stop, int[] step) {
		int m = start.length;

		if (stop == null) {
			stop = new int[m];
			for (int i = 0; i < m; i++) {
				stop[i] = dimensions[i];
			}
		}
		if (step == null) {
			step = new int[m];
			for (int i = 0; i < m; i++) {
				step[i] = 1;
			}
		}
		if (m != dimensions.length || stop.length != dimensions.length || step.length != dimensions.length) {
			logger.error(this + " needs to be passed the correct number of indexes, you passed it start=" + m
					+ ", stop=" + stop.length + ", step=" + step.length + ", and it needs " + dimensions.length);
			throw new IllegalArgumentException("No of indexes does not match data dimensions you passed it start="
					+ start.length + ", stop=" + stop.length + ", step=" + step.length
					+ " pairs of bounds, and it needs " + this.dimensions.length + " pairs");
		}

		// sanitise input
		int[] difference = new int[m];
		for (int i = 0; i < m; i++) {
			if (step[i] == 0) {
				logger.error(this + " needs to be passed an array of steps which are all non-zero");
				throw new IllegalArgumentException("The step array is not allowed any zero entries: " + i
						+ "-th entry is zero");
			}
			if (start[i] < 0) {
				start[i] += dimensions[i];
			}
			if (start[i] > dimensions[i]) {
				start[i] = dimensions[i];
			}
			if (start[i] < 0) {
				logger.error(this + " has been passed start=" + start[i] + "that is outside valid range of [0, "
						+ dimensions[i] + "]");
				throw new IllegalArgumentException("A start index, " + start[i] + ", is outside valid range of [0, "
						+ dimensions[i] + "]");
			}
			if (stop[i] < 0) {
				stop[i] += dimensions[i];
			}
			if (stop[i] > dimensions[i]) {
				stop[i] = dimensions[i];
			}
			if (stop[i] < 0) {
				logger.error(this + " has been passed stop=" + stop[i] + "that is outside valid range of [0, "
						+ dimensions[i] + "]");
				throw new IllegalArgumentException("A stop index, " + stop[i] + ", is outside valid range of [0, "
						+ dimensions[i] + "]");
			}
			if (start[i] == stop[i]) {
				logger.error(this + " has been passed the same start=stop=" + start[i] + " indexes");
				throw new IllegalArgumentException("Same indexes in start and stop");
			}
			if ((step[i] > 0) != (start[i] < stop[i])) {
				logger.error(this + " has been passed start=" + start[i] + " and stop=" + stop[i]
						+ " indexes that are incompatible with step=" + step[i]);
				throw new IllegalArgumentException("Start=" + start[i] + " and stop=" + stop[i]
						+ " indexes are incompatible with step=" + step[i]);
			}
			if (step[i] > 0) {
				difference[i] = (stop[i] - start[i] + step[i] - 1) / step[i];
			} else {
				difference[i] = (stop[i] - start[i] + step[i] + 1) / step[i];
			}
		}
		DataSet result = new DataSet(difference);

		// set up the vectors needed to do this
		int relative[] = new int[m];
		int absolute[] = new int[m];

		for (int i = 0; i < m; i++) {
			relative[i] = start[i];
			absolute[i] = 0;
		}

		// now perform the loop
		while (true) {
			// write the value from the relative position of this dataset
			// to the actual position in the final vector.
			result.set(this.get(relative), absolute);

			// now move the count on one position
			int j = 0;
			for (; j < m; j++) {
				relative[j] += step[j];
				absolute[j]++;
				if (absolute[j] >= difference[j]) {
					relative[j] = start[j];
					absolute[j] = 0;
				} else {
					break;
				}
			}
			if (j == m)
				break;
		}

		return result;
	}

	/**
	 * @param start
	 * @param value
	 */
	public void setSlice(int start, double value) {
		setSlice(new int[] { start }, null, null, value);
	}

	/**
	 * @param start
	 * @param stop
	 * @param value
	 */
	public void setSlice(int start, int stop, double value) {
		setSlice(new int[] { start }, new int[] { stop }, null, value);
	}

	/**
	 * @param start
	 * @param stop
	 * @param step
	 * @param value
	 */
	public void setSlice(int start, int stop, int step, double value) {
		setSlice(new int[] { start }, new int[] { stop }, new int[] { step }, value);
	}

	/**
	 * @param start
	 * @param value
	 */
	public void setSlice(int[] start, double value) {
		setSlice(start, null, null, value);
	}

	/**
	 * @param start
	 * @param stop
	 * @param value
	 */
	public void setSlice(int[] start, int[] stop, double value) {
		setSlice(start, stop, null, value);
	}

	/**
	 * This is modelled after the NumPy array slice
	 *
	 * @param start
	 *            specifies the starting indexes
	 * @param stop
	 *            specifies the stopping indexes (nb, these are <b>not</b> included in the slice)
	 * @param step
	 *            specifies the steps in the slice
	 * @param value
	 */
	public void setSlice(int[] start, int[] stop, int[] step, double value) {
		int m = start.length;

		if (stop == null) {
			stop = new int[m];
			for (int i = 0; i < m; i++) {
				stop[i] = dimensions[i];
			}
		}
		if (step == null) {
			step = new int[m];
			for (int i = 0; i < m; i++) {
				step[i] = 1;
			}
		}
		if (m != dimensions.length || stop.length != dimensions.length || step.length != dimensions.length) {
			logger.error(this + " needs to be passed the correct number of indexes, you passed it start=" + m
					+ ", stop=" + stop.length + ", step=" + step.length + ", and it needs " + dimensions.length);
			throw new IllegalArgumentException("No of indexes does not match data dimensions you passed it start="
					+ start.length + ", stop=" + stop.length + ", step=" + step.length
					+ " pairs of bounds, and it needs " + this.dimensions.length + " pairs");
		}

		// sanitise input
		for (int i = 0; i < m; i++) {
			if (step[i] == 0) {
				logger.error(this + " needs to be passed an array of steps which are all non-zero");
				throw new IllegalArgumentException("The step array is not allowed any zero entries: " + i
						+ "-th entry is zero");
			}
			if (start[i] < 0) {
				start[i] += dimensions[i];
			}
			if (start[i] > dimensions[i]) {
				start[i] = dimensions[i];
			}
			if (start[i] < 0) {
				logger.error(this + " has been passed start=" + start[i] + "that is outside valid range of [0, "
						+ dimensions[i] + "]");
				throw new IllegalArgumentException("A start index, " + start[i] + ", is outside valid range of [0, "
						+ dimensions[i] + "]");
			}
			if (stop[i] < 0) {
				stop[i] += dimensions[i];
			}
			if (stop[i] > dimensions[i]) {
				stop[i] = dimensions[i];
			}
			if (stop[i] < 0) {
				logger.error(this + " has been passed stop=" + stop[i] + "that is outside valid range of [0, "
						+ dimensions[i] + "]");
				throw new IllegalArgumentException("A stop index, " + stop[i] + ", is outside valid range of [0, "
						+ dimensions[i] + "]");
			}
			if (start[i] == stop[i]) {
				logger.error(this + " has been passed the same start=stop=" + start[i] + " indexes");
				throw new IllegalArgumentException("Same indexes in start and stop");
			}
			if ((step[i] > 0) != (start[i] < stop[i])) {
				logger.error(this + " has been passed start=" + start[i] + " and stop=" + stop[i]
						+ " indexes that are incompatible with step=" + step[i]);
				throw new IllegalArgumentException("Start=" + start[i] + " and stop=" + stop[i]
						+ " indexes are incompatible with step=" + step[i]);
			}
		}

		// set up the vectors needed to do this
		int relative[] = new int[m];

		for (int i = 0; i < m; i++) {
			relative[i] = start[i];
		}

		// now perform the loop
		while (true) {
			// write the value to the relative position of this dataset
			set(value, relative);

			// now move the count on one position
			int j = 0;
			for (; j < m; j++) {
				relative[j] += step[j];
				if (step[j] > 0) {
					if (relative[j] >= stop[j]) {
						relative[j] = start[j];
					} else {
						break;
					}
				} else {
					if (relative[j] <= stop[j]) {
						relative[j] = start[j];
					} else {
						break;
					}
				}
			}
			if (j == m)
				break;
		}

	}

	/**
	 * @param start
	 * @param values
	 */
	public void setSlice(int start, DataSet values) {
		setSlice(new int[] { start }, null, null, values);
	}

	/**
	 * @param start
	 * @param stop
	 * @param values
	 */
	public void setSlice(int start, int stop, DataSet values) {
		setSlice(new int[] { start }, new int[] { stop }, null, values);
	}

	/**
	 * @param start
	 * @param stop
	 * @param step
	 * @param values
	 */
	public void setSlice(int start, int stop, int step, DataSet values) {
		setSlice(new int[] { start }, new int[] { stop }, new int[] { step }, values);
	}

	/**
	 * @param start
	 * @param values
	 */
	public void setSlice(int[] start, DataSet values) {
		setSlice(start, null, null, values);
	}

	/**
	 * @param start
	 * @param stop
	 * @param values
	 */
	public void setSlice(int[] start, int[] stop, DataSet values) {
		setSlice(start, stop, null, values);
	}

	/**
	 * @param start
	 * @param stop
	 * @param step
	 * @param values
	 */
	public void setSlice(int[] start, int[] stop, int[] step, DataSet values) {
		int m = start.length;

		if (stop == null) {
			stop = new int[m];
			for (int i = 0; i < m; i++) {
				stop[i] = dimensions[i];
			}
		}
		if (step == null) {
			step = new int[m];
			for (int i = 0; i < m; i++) {
				step[i] = 1;
			}
		}
		if (m != dimensions.length || stop.length != dimensions.length || step.length != dimensions.length) {
			logger.error(this + " needs to be passed the correct number of indexes, you passed it start=" + m
					+ ", stop=" + stop.length + ", step=" + step.length + ", and it needs " + dimensions.length);
			throw new IllegalArgumentException("No of indexes does not match data dimensions you passed it start="
					+ start.length + ", stop=" + stop.length + ", step=" + step.length
					+ " pairs of bounds, and it needs " + this.dimensions.length + " pairs");
		}

		// sanitise input
		int[] difference = new int[m];
		for (int i = 0; i < m; i++) {
			if (step[i] == 0) {
				logger.error(this + " needs to be passed an array of steps which are all non-zero");
				throw new IllegalArgumentException("The step array is not allowed any zero entries: " + i
						+ "-th entry is zero");
			}
			if (start[i] < 0) {
				start[i] += dimensions[i];
			}
			if (start[i] > dimensions[i]) {
				start[i] = dimensions[i];
			}
			if (start[i] < 0) {
				logger.error(this + " has been passed start=" + start[i] + "that is outside valid range of [0, "
						+ dimensions[i] + "]");
				throw new IllegalArgumentException("A start index, " + start[i] + ", is outside valid range of [0, "
						+ dimensions[i] + "]");
			}
			if (stop[i] < 0) {
				stop[i] += dimensions[i];
			}
			if (stop[i] > dimensions[i]) {
				stop[i] = dimensions[i];
			}
			if (stop[i] < 0) {
				logger.error(this + " has been passed stop=" + stop[i] + "that is outside valid range of [0, "
						+ dimensions[i] + "]");
				throw new IllegalArgumentException("A stop index, " + stop[i] + ", is outside valid range of [0, "
						+ dimensions[i] + "]");
			}
			if (start[i] == stop[i]) {
				logger.error(this + " has been passed the same start=stop=" + start[i] + " indexes");
				throw new IllegalArgumentException("Same indexes in start and stop");
			}
			if ((step[i] > 0) != (start[i] < stop[i])) {
				logger.error(this + " has been passed start=" + start[i] + " and stop=" + stop[i]
						+ " indexes that are incompatible with step=" + step[i]);
				throw new IllegalArgumentException("Start=" + start[i] + " and stop=" + stop[i]
						+ " indexes are incompatible with step=" + step[i]);
			}
			if (step[i] > 0) {
				difference[i] = (stop[i] - start[i] + step[i] - 1) / step[i];
			} else {
				difference[i] = (stop[i] - start[i] + step[i] + 1) / step[i];
			}
		}

		// check input dataset
		int[] vdims = values.getDimensions();
		if (vdims.length != m) {
			logger.error(this + " has been passed an input dataset that has incompatible rank");
			throw new IllegalArgumentException("Incompatible rank for input dataset");
		}
		for (int i = 0; i < m; i++) {
			if (vdims[i] < difference[i]) {
				logger
						.error(this + " has been passed an input dataset with a dimension that is too short: "
								+ vdims[i]);
				throw new IllegalArgumentException("Dimension of input dataset too short: " + vdims[i]);
			}
		}

		// set up the vectors needed to do this
		int relative[] = new int[m];
		int absolute[] = new int[m];

		for (int i = 0; i < m; i++) {
			relative[i] = start[i];
			absolute[i] = 0;
		}

		// now perform the loop
		while (true) {
			// write the value from the relative position of this dataset
			// to the actual position in the final vector.
			set(values.get(absolute), relative);

			// now move the count on one position
			int j = 0;
			for (; j < m; j++) {
				relative[j] += step[j];
				absolute[j]++;
				if (absolute[j] >= difference[j]) {
					relative[j] = start[j];
					absolute[j] = 0;
				} else {
					break;
				}
			}
			if (j == m)
				break;
		}

	}

	/**
	 * @return An index dataset of the current dataset
	 */
	public DataSet getIndexDataSet() {
		// now create another dataset to plot against.
		DataSet x = new DataSet(this);
		for (int i = 0; i < x.dataSize(); i++) {
			x.set(i, i);
		}
		return x;
	}

	private void allocateArray(int... dims) {

		int totalSize = 1;
		for (int i = 0; i < dims.length; i++) {
			totalSize *= dims[i];
		}

		if (data == null) {
			// allocate the area, and fill it with NaN's
			try {
				this.data = new double[totalSize];
			} catch (OutOfMemoryError e) {
				logger
						.error("The size of the dataset that is being created is too large and there is not enough memory to hold it.");
				throw new OutOfMemoryError("The dimensions given are too large, and there is "
						+ "not enough memory available in the Java Virtual Machine");
			}

			for (int i = 0; i < data.length; i++) {
				data[i] = Double.NaN;
			}
		} else {
			// if there is existing data there. we need to resize the data
			// but hold all the new data there too.
			
			// first allocate the dataDimesions if neccessary
			if(dataDimensions == null) {
				dataDimensions = new int[dims.length];
			} 
			
			// check to see if the array is within the datasize
			boolean ok = true;
			for(int i = 0; i < dims.length; i++) {
				if(dims[i] > dataDimensions[i]) {
					ok = false;
				}
			}
			
			// the existing memory is enough so do nothing
			if(ok) {
				
				// now this object has the new dimensions so specify them correctly
				for (int i = 0; i < dims.length; i++) {
					dimensions[i] = dims[i];
				}
				
				// end of story for this
				return;	
			} 
			
			// if there isnt enough room, then we need to expand the allocated memory,
			// by the ammount specified in ARRAY_ALLOCTAION_EXTENTION
			
			DataSet oldData = new DataSet(this);
			
			totalSize = 1;
			
			// now check to see where the additional space is required
			for( int i = 0; i < dims.length; i++){
				int change = dims[i]-dimensions[i];
				if((change > 0) && (change < (int)(dimensions[i]*0.1)+1)) {
					change = (int)(dimensions[i]*ARRAY_ALLOCTAION_EXTENTION)+1;				
				}
				dataDimensions[i] = dimensions[i] + change;
				totalSize *= dataDimensions[i];
			}
			
			try {
				this.data = new double[totalSize];
			} catch (OutOfMemoryError e) {
				logger
						.error("The size of the DataSet that is being created is too large and there is not enough memory to hold it.");
				throw new OutOfMemoryError("The dimentions given are too large, and there is "
						+ "not enough memory available in the Java Virtual Machine");
			}

			// now this object has the new dimensions so specify them correctly
			for (int i = 0; i < dims.length; i++) {
				dimensions[i] = dims[i];
			}
			
			// make sure that all the data is set to NaN
			for (int i = 0; i < data.length; i++) {
				data[i] = Double.NaN;
			}

			// now copy the data back in in the correct positions
			int[] pos = new int[dims.length];

			int[] odims = oldData.getDimensions();
			for (int i = 0; i < oldData.dataSize(); i++) {
				int carry = 0;
				for (int j = 0; j < odims.length; j++) {
					pos[j] += carry;
					carry = 0;
					if (pos[j] >= odims[j]) {
						pos[j] = 0;
						carry = 1;
					}
				}

				if (carry > 0) {
					// this means that the loop has ended, it should never
					// happen
					logger.warn("things may be going wrong in the dataset allocate Array function");
				}
				set(oldData.get(pos), pos);
				pos[0]++;
			}

		}

	}

	/**
	 * Function to subsample a dataset to a smaller dimensions by the mean value of a set of points
	 * 
	 * @param numberOfPoints
	 * @return DataSet
	 */
	public DataSet subSampleMean(int numberOfPoints) {

		int size = this.dataSize();
		int numberOfSegments = size / numberOfPoints;

		DataSet result = new DataSet(numberOfSegments);

		for (int i = 0; i < numberOfSegments; i++) {
			double newvalue = get(i * numberOfPoints);
			for (int j = 1; j < numberOfPoints; j++) {
				newvalue += get((i * numberOfPoints) + j);
			}
			result.set(newvalue / numberOfPoints, i);
		}
		return result;
	}

	/**
	 * @param numberOfPoints
	 * @return DataSet
	 */
	public DataSet subSampleMax(int numberOfPoints) {

		int size = this.dataSize();
		int numberOfSegments = size / numberOfPoints;

		DataSet result = new DataSet(numberOfSegments);

		for (int i = 0; i < numberOfSegments; i++) {
			double newvalue = get(i * numberOfPoints);
			for (int j = 1; j < numberOfPoints; j++) {
				double point = get((i * numberOfPoints) + j);
				if (point > newvalue) {
					newvalue = point;
				}
			}
			result.set(newvalue / numberOfPoints, i);
		}
		return result;
	}

	/**
	 * This command runs the function that is input into it, defined by the IDataSetFunction Interface It then calls the
	 * execute method on that object and returns the result in the form of a list
	 * 
	 * @param function
	 *            The IDataSetFunction that describes the operator to be performed.
	 * @return A list of DataSets which is obtained from the functions execute method.
	 */
	public List<DataSet> exec(IDataSetFunction function) {

		return function.execute(this);

	}

	/**
	 * This function allows anything that dirties the dataset to return all the dirty flags to true, so that the other
	 * functions can work correctly.
	 */
	public void setDirty() {

		dirtyMaxValue = null;
		dirtyMinValue = null;
		dirtyMaxPos = null;
		dirtyMinPos = null;
		dirtySum = null;
		dirtyStandardDeviation = null;
		dirtyMeanValue = null;

	}

	private void calculateMinMaxMeanSumDeviation() {
		double max = data[0];
		double min = data[0];
		int maxpos = 0;
		int minpos = 0;
		double sum = data[0];
		double standardDeviation = data[0] * data[0];

		for (int i = 1; i < data.length; i++) {
			double val = data[i];
			sum += val;
			standardDeviation = val * val;
			if (val > max) {
				max = val;
				maxpos = i;
			}

			if (val < min) {
				min = val;
				minpos = i;
			}
		}

		double mean = sum / data.length;
		standardDeviation = Math.sqrt(standardDeviation / (data.length));

		// now all the calculations are done, add the values into the appropriate holders
		dirtyMaxValue = max;
		dirtyMinValue = min;
		dirtyMaxPos = getNDIndex(maxpos);
		dirtyMinPos = getNDIndex(minpos);
		dirtyMeanValue = mean;
		dirtyStandardDeviation = standardDeviation;
		dirtySum = sum;
	}

	/**
	 * @return data
	 */
	@Deprecated
	public double[] toArray() {
		logger.warn("DataSet.toArray() is deprecated and will be removed by gda v8.");
		logger.warn("Use .getBuffer() instead.");
		InterfaceProvider.getTerminalPrinter().print("DataSet.toArray() is deprecated and will be removed by gda v8.");
		InterfaceProvider.getTerminalPrinter().print("Use .getBuffer() instead.");

		return getBuffer();
	}
}
