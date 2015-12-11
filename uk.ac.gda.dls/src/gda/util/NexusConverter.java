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

package gda.util;


import gda.analysis.ScanFileHolder;
import gda.data.nexus.extractor.NexusExtractorException;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.text.DateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.eclipse.dawnsci.analysis.dataset.impl.Dataset;
import org.eclipse.dawnsci.nexus.NexusException;

import uk.ac.diamond.scisoft.analysis.io.NexusLoader;
import uk.ac.gda.util.io.SortingUtils;
import uk.ac.gda.util.list.SortNatural;

public class NexusConverter {

	/**
	 * 
	 * Non-recursively converts nexus files in a folder to ascii
	 * 
	 * @param nexusPath   - file or folder of the nexus files to be converted
	 * @param outputPath  - folder of the ascii files to be written
	 */
	public final static void convert(final String nexusPath, final String outputPath) throws Exception {
		
		NexusConverter.convert(nexusPath, outputPath, null, null, -1);
	}
	
	public static final void concvert(final String nexusPath, final String outputPath, final List<String> dataSetNames, final String regExp) throws Exception {
		NexusConverter.convert(nexusPath, outputPath, dataSetNames, regExp, -1);
	}
	
	public final static void convert(final String nexusPath, final String outputPath, final String regExp, final int tol) throws Exception {
		NexusConverter.convert(nexusPath, outputPath, null, regExp, tol);
	}
	
	/**
	 * 
	 * Non-recursively converts nexus files in a folder to ascii
	 * 
	 * @param nexusPath   - file or folder of the nexus files to be converted
	 * @param outputPath  - folder of the ascii files to be written
	 * @param regExp      - A regular expression with the file name must match
	 * @param tol         - The first group in the regExp can be tested against this value and if larger, the file is converted.
	 */
	private final static void convert(final String nexusPath, final String outputPath, final List<String> dataSetNames, final String regExp, final int tol) throws Exception {
		
        final List<File> ns = getNexusFiles(nexusPath, regExp, tol);		
		for (File nexus : ns) {
			
			if (!nexus.isFile()) continue;
			
			final File outDir = new File(outputPath);
			if (!outDir.exists()) outDir.mkdirs();
			final File out = new File(outDir, nexus.getName().substring(0, nexus.getName().indexOf("."))+".dat");			
			convert(nexus, out, dataSetNames);
			
		}
	}
	
	
	private static List<File> getNexusFiles(final String nexusPath, final String regExp, final int tol) {
		final File nexusDirOrFile = new File(nexusPath);
		List<File> ns;
		if (nexusDirOrFile.isDirectory()) {
		    ns  = Arrays.asList(nexusDirOrFile.listFiles());
			Collections.sort(ns, SortingUtils.NATURAL_SORT);		
			ns = filter(ns, regExp, tol);
		} else {
			ns = new ArrayList<File>(1);
			ns.add(nexusDirOrFile);
		}
		return ns;
	}

	private static void convert2D(final String nexusPath, final String outDir, final String name2d, final String key2d, final String regexp, final int tol) throws Exception {
        
		final List<File> ns = getNexusFiles(nexusPath, regexp, tol);		
		for (File nexus : ns) {
			
			if (!nexus.isFile()) continue;
 
			ScanFileHolder holder = new ScanFileHolder();
			holder.load(new NexusLoader(nexus.getAbsolutePath()));
			
		    final Dataset set2d = holder.getAxis(name2d);
		    set2d.setName(name2d);
		    
		    Dataset set1d =  null;
		    if (key2d!=null){
		    	set1d = holder.getAxis(key2d);
		    	set1d.setName(key2d);
		    }
		    
			final File out = new File(outDir, nexus.getName().substring(0, nexus.getName().indexOf("."))+"_"+name2d+".dat");
			write2D(set1d, set2d, out, nexus);
		}
	}

	private static void write2D(final Dataset set1d, final Dataset set2d, final File out, final File nexus) throws Exception {
		
		final BufferedWriter writer = new BufferedWriter(new FileWriter(out));
		try {
			
			writer.write("# GDA results\n");
			writer.write("# Ascii file produced from '"+nexus.getAbsolutePath()+"' on "+DateFormat.getInstance().format(new Date())+"\n");
			writer.write("# Header data is not currently recreated by the NexusConverter\n");
			
			writer.write(getTitlesLine(set1d, set2d));
			final int[] dims = set2d.getShape();
			
			// Add columns for the second dimension.
			StringBuilder buf = new StringBuilder("# ");
			if (set1d!=null) {
				for (int i = 0; i < set1d.getName().length(); i++) buf.append(' ');
				buf.append('\t');
			}
			for (int j = 0; j < dims[1]; j++) {
				buf.append(j);
				buf.append('\t');
			}
			buf.append('\n');
			writer.write(buf.toString());
			
			if (dims.length!=2) throw new Exception("The data set "+set2d.getName()+" is not two dimensional!");
	        for (int i = 0; i < dims[0]; i++) {
				buf = new StringBuilder();
				if (set1d!=null) {
					buf.append(set1d.getDouble(i));
					buf.append('\t');
				}
				for (int j = 0; j < dims[1]; j++) {
					buf.append(set2d.getDouble(i, j));
					buf.append('\t');
				}
				buf.append('\n');
				writer.write(buf.toString());
			}
			
		} finally {
			writer.close();
		}
	}

	/**
	 * List names
	 * @param nexusPath
	 */
	public static void names(final String nexusPath) throws Exception {
		NexusConverter.names(nexusPath, null, -1);
	}
	
	/**
	 * List names
	 * @param nexusPath
	 * @param regexp
	 * @param tol
	 * @throws Exception 
	 * @throws NexusExtractorException 
	 * @throws NexusException 
	 */
	public static void names(final String nexusPath, final String regexp, final int tol) throws Exception {
        
		final List<File> ns = getNexusFiles(nexusPath, regexp, tol);		
		for (File nexus : ns) {
			
			if (!nexus.isFile()) continue;
			
			final List<String> names = NexusLoader.getDatasetNames(nexus.getAbsolutePath(), null);
			Collections.sort(names, new SortNatural<String>(false));
			
			System.out.println(nexus.getAbsolutePath());
			final StringBuffer buf = new StringBuffer();
			for (String name : names) {
				buf.append(name);
				buf.append('\t');
			}
			System.out.println(buf.toString());
		}		
	}


	/**
	 * 
	 * @param nexus
	 * @param out
	 * @throws Exception
	 */
	public static void convert(File nexus, File out) throws Exception {
		NexusConverter.convert(nexus,out,null);
	}
	/**
	 * 
	 * @param nexus
	 * @param out
	 * @throws Exception
	 */
	private static void convert(File nexus, File out, List<String> names) throws Exception {

		if (names==null||names.isEmpty()) {
			names = NexusLoader.getDatasetNames(nexus.getAbsolutePath(), null);
			Collections.sort(names, new SortNatural<String>(false));
		}
		
		ScanFileHolder holder = new ScanFileHolder();
		holder.load(new NexusLoader(nexus.getAbsolutePath()));
	
		final BufferedWriter writer = new BufferedWriter(new FileWriter(out));
		try {
			
			writer.write("# GDA results\n");
			writer.write("# Ascii file produced from '"+nexus.getAbsolutePath()+"' on "+DateFormat.getInstance().format(new Date())+"\n");
			writer.write("# Header data is not currently recreated by the NexusConverter\n");
			
			final Map<String,Dataset> data = new HashMap<String, Dataset>(names.size());
			
			for (Iterator<String> iterator = names.iterator(); iterator.hasNext();) {
				
				final String name = iterator.next();
				try {
					final Dataset set = holder.getAxis(name);
					if (set.getShape().length>1) {
						// Could sum it one day.
						iterator.remove();
						continue;
					}
					data.put(name, set);
				} catch (Exception ne) {
					System.out.println(ne.getMessage());
					iterator.remove();
				}
			}
			writer.write(getTitlesLine(names, data));
			

			final int maxSize = getMaxSizeFirstDimension(data);
			for (int j = 0; j < maxSize; j++) {
				writer.write(getData(names, data, j));
			}
			writer.flush();
		} finally {
			writer.close();
		}
		
		System.out.println("Converted '"+nexus+"' to '"+out+"'");
		holder = null;
		System.gc();

	}
	
	private static List<File> filter(List<File> ns, String regExp, int tol) {
		if (regExp==null) return ns;
		
		final List<File> ret = new ArrayList<File>(ns.size());
		ret.addAll(ns);
		
		final Pattern pattern = Pattern.compile(regExp);
		for (Iterator<File> it = ret.iterator(); it.hasNext();) {
			final File file = it.next();
			final Matcher matcher = pattern.matcher(file.getName());
			if (!matcher.matches()) {
				it.remove();
				continue;
			}
			
			final String grp = matcher.group(0);
			if (tol>-1 && Integer.parseInt(grp)<tol) {
				it.remove();
				continue;
			}
		}
		
		return ret;
		
	}
	private static String getData(List<String> names, Map<String, Dataset> data, int i) {
		final StringBuilder buf = new StringBuilder();
		for (String name : names) {
			final Dataset set = data.get(name);
			if (i<set.getSize()) {
				buf.append(String.format("%9.4f", set.getDouble(i)));
			} else {
				buf.append(" -   ");
			}
			buf.append("\t");
		}
		buf.append("\n");
		return buf.toString();
	}

	private static int getMaxSizeFirstDimension(Map<String, Dataset> data) {
		int ret = Integer.MIN_VALUE;
		for (Dataset set : data.values()) {
			final int[] dims = set.getShape();
			ret = Math.max(dims[0], ret);
		}
		return ret;
	}

	private static String getTitlesLine(List<String> names, Map<String, Dataset> data) {
		final StringBuilder buf = new StringBuilder("# ");
		for (String name : names) {
			buf.append("  ");
			buf.append(name);
			
			final Dataset set = data.get(name);
			int     len = String.format("%9.4f", set.getDouble(0)).length();
			len = len-name.length()-2;
			for (int i = 0; i < len; i++) buf.append(" ");
				
			buf.append("\t");
		}
		buf.append("\n");
		return buf.toString();
	}
	
	private static String getTitlesLine(Dataset... data) {
		final StringBuilder buf = new StringBuilder("# ");
		for (Dataset set : data) {
			
			if (set==null) continue;
			buf.append("  ");
			buf.append(set.getName());
			
			int     len = String.format("%9.4f", set.getDouble(0)).length();
			len = len-set.getName().length()-2;
			for (int i = 0; i < len; i++) buf.append(" ");
				
			buf.append("\t");
		}
		buf.append("\n");
		return buf.toString();
	}
	
	/**
	 * This main method is used as a command line tool in the nexus-converter application
	 * which can be used to convert files and named data sets to ascii
	 * 
	 * @param args
	 */
	public static void main(String[] args) {
		try {
			List<String> arguments = Arrays.asList(args);
			boolean listNames = false;
			String name2D=null, key2D=null;
			
			// Process arguments, not standard arguments algorithm as options are simple.
			if (arguments.isEmpty()||arguments.contains("-h")||arguments.contains("-help")) {
				printHelp();
				return;
			} else if (arguments.isEmpty()||arguments.contains("-v")||arguments.contains("-version")) {
				System.out.println(getVersion());
				return;
			} else if (arguments.get(0).equals("-n")||arguments.get(0).equals("-names")) {
				listNames = true;
				List<String> tmp = new ArrayList<String>();
				tmp.addAll(arguments);
				tmp.remove(0);
				arguments = tmp;
			} else if (arguments.contains("-2D")) {
				int index = arguments.indexOf("-2D");
				name2D    = arguments.get(index+1);
				if (arguments.contains("-2Dkey")) {
					index = arguments.indexOf("-2Dkey");
					key2D = arguments.get(index+1);
				}
			}
			
			if (arguments.contains("-n")||arguments.contains("-names")) {
				printHelp();
				return;
			}
			
			final List<String> names = new ArrayList<String>(7);
			
			final Iterator<String> it = arguments.iterator();
			final String input  = it.next();
			final String output = it.hasNext() ? it.next() : null;
			String regexp = null;
			
			while (it.hasNext()) {
				final String arg = it.next();
				if (arg.equals("-r")) {
					regexp = it.next();
					continue;
				}
				names.add(arg);	
			}
			
			if (listNames) {
			    NexusConverter.names(input, regexp, -1);
			} else if (name2D!=null){
				NexusConverter.convert2D(input, output, name2D, key2D, regexp, -1);
			} else {
				// Main convert line
			    NexusConverter.convert(input, output, names, regexp, -1);
			}
			System.out.println(">> Completed");
			
		} catch (Exception ne) {
			ne.printStackTrace();
			printHelp();
		}
	}

	private static void printHelp() {
		System.out.println(getVersion());
		System.out.println("Usage:");
		System.out.println("./nexus-converter.sh (-n) <input (file or folder)> <output (folder)> (-2D <...>,-2DKey <...>) (<Data Set Name 1>  <Data Set Name1> ...) (-r <input file name regular expression>)");
		System.out.println();
		System.out.println("The input file name regular expression can be used to filter files if the input is a folder.");
		System.out.println("Data set names can be specified, default is that all data 1D sets are added as columns if no data set names are defined.");
		System.out.println("Two dimensional data sets are not included but can be extracted using the -2D command.");
		System.out.println("Other options:\n");
		System.out.println("-n <input (file or folder)>        - lists dataset names in file(s)  (also -names ) \n");
		System.out.println("-h                                 - list help                       (also -help  ) \n");
		System.out.println("-v                                 - print version                   (also -version ) \n");
		System.out.println("-2D <Data Set Name>                - list 2D data set                \n");
		System.out.println("-2Dkey <Data Set Name>             - An optional 1D set that can be used to list with the 2D one, you must specify -2D in this case. \n");
	}

	private static String getVersion() {
		return "Nexus Converter 0.9.1";
	} 
}
