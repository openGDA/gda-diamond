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

package gda.device.scannable.keyence;

import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.SocketTimeoutException;
import java.nio.ByteBuffer;
import java.nio.CharBuffer;
import java.nio.channels.SocketChannel;
import java.nio.charset.Charset;
import java.nio.charset.CharsetDecoder;
import java.nio.charset.CharsetEncoder;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.concurrent.TimeUnit;

import javax.imageio.ImageIO;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.StringUtils;

import gda.device.DeviceException;
import gda.device.scannable.ScannableBase;
import gda.factory.FactoryException;
import gda.jython.InterfaceProvider;
import uk.ac.diamond.daq.concurrent.Async;

/**
 * Provides Ethernet communications a Keyence Camera Controller
 *
 * Tested with a CV-3001P but should work with others as well.
 * Triggering is done in software. If you require hardware (external) triggering,
 * that would not be very hard to implement.
 */
public class Keyence extends ScannableBase {

	private static final Logger logger = LoggerFactory.getLogger(Keyence.class);

	private String host = "localhost";

	private int commandPort = 8500;

	private int socketTimeOut = 2000;

	private List<String> startupCommands = new ArrayList<>();


    private static Charset charset = StandardCharsets.US_ASCII;
    private static CharsetEncoder encoder = charset.newEncoder();
    private static CharsetDecoder decoder = charset.newDecoder();

	private SimpleDateFormat dateFormat = new SimpleDateFormat("yyyyMMdd-HH:mm:ss");

	private String imageFormat = "png";

	//Object used to grant a thread exclusive access to the socket, bb and connected
	private final Object socketAccessLock= new Object();

	private ByteBuffer bb = ByteBuffer.allocate(4096);
	private SocketChannel socketChannel;
	private boolean connected = false;
	/**
	 *
	 */
	public Keyence() {
		inputNames = new String[] {};
	}

	@Override
	public void configure() throws FactoryException {
		if (isConfigured()) {
			return;
		}
		try {
			connect();
		} catch (DeviceException e) {
			throw new FactoryException("Error connecting to Keyence device",e);
		}

		Async.scheduleAtFixedRate(this::emptyBuffer, 0, 21987, TimeUnit.MILLISECONDS,"%s buffer emptier", getName());
		// 21987 magic number, may be explained in the pre-git history.

		setConfigured(true);
	}

	/**
	 * Set up initial connections to socket and wrap the stream in buffered reader and writer.
	 * @throws DeviceException
	 */
	public void connect() throws DeviceException {
		try {
			synchronized (socketAccessLock) {
				if (!isConnected()){
					InetSocketAddress inetAddr = new InetSocketAddress(host, commandPort);
					socketChannel = SocketChannel.open();
					socketChannel.connect(inetAddr);

					socketChannel.socket().setSoTimeout(socketTimeOut);
					socketChannel.configureBlocking(true);
					socketChannel.finishConnect();

					cleanPipe();
					doStartupScript();

					connected = true;
				}
			}
		} catch (IOException ex) {
			logger.error("{}: connect: {}", getName(), ex.getMessage());
		}
	}

	@Override
	public void reconfigure() throws FactoryException {
		try {
			reconnect();
		} catch (DeviceException e) {
			throw new FactoryException("Error reconfiguring keyence device",e);
		}
	}

	/**
	 * Tidy existing socket streams and try to connect them again within the thread. This method is synchronized as both
	 * the main thread and run thread use this method.
	 * @throws DeviceException
	 */
	public synchronized void reconnect() throws DeviceException {
		try {
			close();
		} catch (DeviceException e) {
			// do nothing for now
		}
		connect();
	}

	@Override
	public void close() throws DeviceException {
		synchronized (socketAccessLock) {
			connected = false;
			if (socketChannel != null) {
				try {
					socketChannel.close();
					socketChannel = null;
				} catch (IOException ex) {
					throw new DeviceException(ex.getMessage(),ex);
				}
			}
		}
	}

	/**
	 * Returns the state of the socket connection
	 *
	 * @return true if connected
	 */
	public boolean isConnected() {
		return connected;
	}


	/**
	 * Send command to the server.
	 *
	 * @param msg
	 *            an unterminated command
	 * @return the reply string.
	 * @throws DeviceException
	 */
	public String processCommand(String msg) throws DeviceException {
		String command = msg + '\r';
		String reply = null;
		logger.debug("{}: sent command: |{}|", getName(), msg);
		synchronized (socketAccessLock) {
			if (!isConnected()) {
				throw new DeviceException("not connected");
			}
			try{
				cleanPipe();
				socketChannel.write(encoder.encode(CharBuffer.wrap(command)));
				bb.clear();
				socketChannel.read(bb);
				bb.flip();
				reply = decoder.decode(bb).toString();
				logger.debug("{}: got reply: |{}|", getName(), reply.trim());
			} catch (SocketTimeoutException ex) {
				throw new DeviceException("sendCommand read timeout " + ex.getMessage(),ex);
			} catch (IOException ex) {
				connected = false;
				throw new DeviceException("sendCommand: " + ex.getMessage(),ex);
			}
		}
		return reply;
	}

	private String writeImage(BufferedImage image) throws IOException {
		String fileName = InterfaceProvider.getPathConstructor().createFromDefaultProperty()+"/"+getName()+"-"+dateFormat.format(new Date())+"."+imageFormat;
		File imageFile = new File(fileName );
		ImageIO.write(image, imageFormat, imageFile);
		return fileName;
	}
	/**
	 *
	 * @return the filename
	 * @throws IOException
	 * @throws DeviceException
	 */
	public String saveLastMeasurementImage() throws IOException, DeviceException {
		return writeImage(getLastMeasurementImage());
	}
	/**
	 *
	 * @return the camera shot of the last measurement
	 * @throws DeviceException
	 * @throws IOException
	 */
	public BufferedImage getLastMeasurementImage() throws DeviceException, IOException {
		byte[] image = (byte[]) processImageRequest("BR,CM,1,0,NW", 5)[5];
		return ImageIO.read(new ByteArrayInputStream(image));
	}


	/**
	 *
	 * @throws IOException
	 * @throws DeviceException
	 */
	public void saveScreenShot(String fileName) throws IOException, DeviceException {
		File imageFile = new File(fileName );
		ImageIO.write(getScreenShot(), imageFormat, imageFile);
	}

	/**
	 *
	 * @return the filename
	 * @throws IOException
	 * @throws DeviceException
	 */
	public String saveScreenShot() throws IOException, DeviceException {
		return writeImage(getScreenShot());

	}
	/**
	 *
	 * @return a screenshot
	 * @throws DeviceException
	 * @throws IOException
	 */
	public BufferedImage getScreenShot() throws DeviceException, IOException {
		byte[] image = (byte[]) processImageRequest("BC,CM", 2)[2];
		return ImageIO.read(new ByteArrayInputStream(image));
	}
	/**
	 * Send command to the server.
	 *
	 * @param msg
	 *            an unterminated command
	 * @param expectedReplyItems
	 * @return the reply string.
	 * @throws DeviceException
	 */
	public Object[] processImageRequest(String msg, int expectedReplyItems) throws DeviceException {
		if (expectedReplyItems < 2) throw new IllegalArgumentException("need at least two values for images (length definition and data)");
		String command = msg + '\r';
		Object[] reply = new Object[expectedReplyItems+1];
		logger.debug("{}: sent command: {}", getName(), msg);
		synchronized (socketAccessLock) {
			try{
				if (!isConnected()) {
					throw new DeviceException("not connected");
				}
				cleanPipe();
				socketChannel.write(encoder.encode(CharBuffer.wrap(command)));

				ByteBuffer singleByte = ByteBuffer.allocate(1);

				StringBuilder sb = new StringBuilder();
				int argCounter = 0;
				while(argCounter < expectedReplyItems) {
					singleByte.clear();
					socketChannel.socket().setSoTimeout(socketTimeOut);
					socketChannel.configureBlocking(true);
					while (singleByte.position() == 0)
						socketChannel.read(singleByte);
					singleByte.flip();
					String c = decoder.decode(singleByte).toString();
					logger.debug(c);
					if (c.equals(",")) {
						reply[argCounter] = sb.toString();
						sb = new StringBuilder();
						argCounter++;
					} else if (c.equals("\r")) {
						throw new DeviceException("sendCommand: not enough data for image received - suspect an error");
					} else {
						sb.append(c);
					}
				}

				int imageLength = Integer.parseInt(reply[expectedReplyItems-1].toString());

				byte[] imageData = new byte[imageLength];
				ByteBuffer bybu = ByteBuffer.wrap(imageData);

				while(bybu.remaining() != 0) {
						socketChannel.read(bybu);
					}

				reply[expectedReplyItems] = imageData;
			} catch (SocketTimeoutException ex) {
				throw new DeviceException("sendCommand read timeout " + ex.getMessage(),ex);
			} catch (IOException ex) {
				// treat as fatal
				connected = false;
				throw new DeviceException("sendCommand: " + ex.getMessage(),ex);
			}
		}
		return reply;
	}

	private void doStartupScript() throws DeviceException {
		for (String command : startupCommands) {
			String reply = processCommand(command);
			if (reply.startsWith("ER")) {
				logger.error("error sending command {} received error reply from device: {}", command, reply);
			}
		}
	}

	/**
	 * Set the keyence host
	 *
	 * @param host
	 */
	public void setHost(String host) {
		this.host = host;
	}

	/**
	 * @return the keyence host name
	 */
	public String getHost() {
		return host;
	}

	/**
	 * Set the command port
	 *
	 * @param port
	 */
	public void setPort(int port) {
		this.commandPort = port;
	}

	/**
	 * @return the command port
	 */
	public int getPort() {
		return commandPort;
	}

	/**
	 * @param startupCommands
	 */
	public void setStartupCommands(List<String> startupCommands) {
		this.startupCommands = startupCommands;
	}

	/**
	 * @return an array list of startup commands to be processed by da.server on startup
	 */
	public List<String> getStartupCommands() {
		return startupCommands;
	}

	@Override
	public double[] getPosition() throws DeviceException {

		String reply = processCommand("T1");
		String[] posStrings = reply.split(",");
		if (!"T1".equals(posStrings[0])) {
			throw new DeviceException("communication or measurement error (device not in run mode?): " + StringUtils.quote(reply));
		}

		int positionsRead = posStrings.length-1;
		if (extraNames.length>0 && extraNames.length != positionsRead) throw new DeviceException("unexpected number of measurements, are we running the right program? expected <"+extraNames.length+"> got <"+positionsRead+">. Reply was " + StringUtils.quote(reply.replace("\n", "\\n").replace("\r", "\\r")));

		double[] positions = new double[positionsRead];
		for (int i = 1; i < posStrings.length; i++) {
			positions[i - 1] = Double.parseDouble(posStrings[i]);
		}
		return positions;
	}

	@Override
	public void asynchronousMoveTo(Object position) throws DeviceException {
	}

	@Override
	public boolean isBusy() throws DeviceException {
		return false;
	}

	@Override
	public void setInputNames(String[] names) {
	}

	private void emptyBuffer() {
		try {
			cleanPipe();
		} catch (IOException e) {
			logger.error("Exception while cleaning pipe of {}", getName(), e);
		}
		if (isConfigured() && !isConnected()) {
			try {
				reconnect();
			} catch (DeviceException e) {
				logger.error("Exception while reconnecting after cleaning pipe of {}", getName(), e);
			}
		}
	}

	private void cleanPipe() throws IOException {
		synchronized (socketAccessLock) {
			if(isConnected()){
				try{
					socketChannel.configureBlocking(false);
					while (socketChannel.read(bb) > 0) {
						bb.clear();
					}
					socketChannel.configureBlocking(true);
				} catch (IOException ex) {
					try {
						close();
					} catch (DeviceException e) {
						// we know that already
					}
					throw ex;
				}
			}
		}
	}
}
