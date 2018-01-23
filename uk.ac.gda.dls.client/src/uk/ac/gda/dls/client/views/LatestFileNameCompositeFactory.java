/*-
 * Copyright © 2011 Diamond Light Source Ltd.
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

package uk.ac.gda.dls.client.views;

import gda.device.detectorfilemonitor.FileProcessor;
import gda.device.detectorfilemonitor.HighestExistingFileMonitorData;
import gda.device.detectorfilemonitor.HighestExistingFileMonitorDataProvider;
import gda.device.detectorfilemonitor.HighestExistingFileMonitorSettings;
import gda.device.detectorfilemonitor.impl.SimpleHighestExistingFileMonitor;
import gda.observable.IObserver;
import gda.rcp.GDAClientActivator;
import gda.rcp.views.CompositeFactory;

import java.io.File;
import java.io.IOException;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.DisposeEvent;
import org.eclipse.swt.events.DisposeListener;
import org.eclipse.swt.events.FocusEvent;
import org.eclipse.swt.events.FocusListener;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.events.KeyListener;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.events.VerifyEvent;
import org.eclipse.swt.events.VerifyListener;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.PlatformUI;
import org.springframework.beans.factory.InitializingBean;

import swing2swt.layout.BorderLayout;
import uk.ac.gda.common.rcp.util.EclipseWidgetUtils;
import uk.ac.gda.ui.utils.SWTUtils;

/*
 * CompositeFactory to create a Composite used for processing files in a fileset reported by an instance of
 * HighestExistingFileMonitorDataProvider The processing is done by a FileProcessor object
 */
public class LatestFileNameCompositeFactory implements CompositeFactory, InitializingBean {
	// private static final Logger logger = LoggerFactory.getLogger(LatestFileNameCompositeFactory.class);
	FileProcessor fileProcessor;
	String label;

	HighestExistingFileMonitorDataProvider highestExistingFileMonitorDataProvider;

	public HighestExistingFileMonitorDataProvider getHighestExistingFileMonitorDataProvider() {
		return highestExistingFileMonitorDataProvider;
	}

	public void setHighestExistingFileMonitorDataProvider(
			HighestExistingFileMonitorDataProvider highestExistingFileMonitorDataProvider) {
		this.highestExistingFileMonitorDataProvider = highestExistingFileMonitorDataProvider;
	}

	public FileProcessor getFileProcessor() {
		return fileProcessor;
	}

	public void setFileProcessor(FileProcessor fileProcessor) {
		this.fileProcessor = fileProcessor;
	}

	public String getLabel() {
		return label;
	}

	public void setLabel(String label) {
		this.label = label;
	}
	
	private boolean showButtonSeparator;
	
	public void setShowButtonSeparator(boolean showButtonSeparator) {
		this.showButtonSeparator = showButtonSeparator;
	}
	
	private boolean separatePlayPauseButtons;
	
	public void setSeparatePlayPauseButtons(boolean separatePlayPauseButtons) {
		this.separatePlayPauseButtons = separatePlayPauseButtons;
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		final Image toLatestImage = GDAClientActivator.getImageDescriptor("icons/control_end_blue.png").createImage();
		final Image toStartImage = GDAClientActivator.getImageDescriptor("icons/control_start_blue.png").createImage();
		final Image backOneImage = GDAClientActivator.getImageDescriptor("icons/control_rewind_blue.png").createImage();
		final Image forwardOneImage = GDAClientActivator.getImageDescriptor("icons/control_fastforward_blue.png").createImage();
		final Image pauseImage = GDAClientActivator.getImageDescriptor("icons/control_pause_blue.png").createImage();
		final Image runImage = GDAClientActivator.getImageDescriptor("icons/control_play_blue.png").createImage();

		final LatestFileNameComposite comp = new LatestFileNameComposite(parent, style);
		comp.setLabel(label);
		comp.setHighestExistingFileMonitorDataProvider(highestExistingFileMonitorDataProvider);
		comp.setFileProcessor(fileProcessor);
		comp.setImages(toStartImage, toLatestImage, pauseImage, runImage, backOneImage, forwardOneImage);
		comp.setShowButtonSeparator(showButtonSeparator);
		comp.setSeparatePlayPauseButtons(separatePlayPauseButtons);
		
		comp.createControls();
		
		return comp;
	}

	@Override
	public void afterPropertiesSet() throws Exception {
		if (fileProcessor == null) {
			throw new IllegalArgumentException("fileProcessor == null");
		}
		if (highestExistingFileMonitorDataProvider == null) {
			throw new IllegalArgumentException("highestExistingFileMonitorDataProvider == null");
		}
		if (label == null) {
			throw new IllegalArgumentException("label == null");
		}
	}

	/*
	 * Ensure plugin containing the icons is set to be the default working folder
	 */
	public static void main(String... args) throws Exception {

		Display display = new Display();
		Shell shell = new Shell(display);
		shell.setLayout(new BorderLayout());
		final Image toLatestImage = new Image(display, "icons/control_end_blue.png");
		final Image toStartImage = new Image(display, "icons/control_start_blue.png");
		final Image pauseImage = new Image(display, "icons/control_pause_blue.png");
		final Image runImage = new Image(display, "icons/control_play_blue.png");
		final Image backOneImage = new Image(display, "icons/control_rewind_blue.png");
		final Image forwardOneImage = new Image(display, "icons/control_fastforward_blue.png");

		SimpleHighestExistingFileMonitor simpleDetectorFileMonitor = new SimpleHighestExistingFileMonitor();
		int startNumber = 5;
		String prefix = "/tmp";
		String fileTemplate = "/file_%04d.tif";
		HighestExistingFileMonitorSettings settings = new HighestExistingFileMonitorSettings(prefix, fileTemplate,
				startNumber);
		simpleDetectorFileMonitor.setHighestExistingFileMonitorSettings(settings);
		int delay = 1000;
		simpleDetectorFileMonitor.setDelayInMS(delay);
		simpleDetectorFileMonitor.afterPropertiesSet();
		simpleDetectorFileMonitor.setRunning(true);
		final SimpleFileProcessor simpleFileMonitor = new SimpleFileProcessor(shell, settings);

		final LatestFileNameComposite comp = new LatestFileNameComposite(shell, SWT.NONE);
		comp.setLabel("Latest Detector Images");
		comp.setHighestExistingFileMonitorDataProvider(simpleDetectorFileMonitor);
		comp.setFileProcessor(simpleFileMonitor);
		comp.setImages(toStartImage, toLatestImage, pauseImage, runImage, backOneImage, forwardOneImage);
		comp.createControls();
		comp.setLayoutData(BorderLayout.NORTH);
		comp.setVisible(true);
		shell.pack();
		shell.setSize(400, 400);
		SWTUtils.showCenteredShell(shell);
		simpleDetectorFileMonitor.setRunning(false);
	}

}

/**
 * Test class
 */
class SimpleFileProcessor extends Composite implements FileProcessor {

	private Text text;
	private int nextFileNumber;

	public SimpleFileProcessor(Composite parent, final HighestExistingFileMonitorSettings settings) {
		super(parent, SWT.NONE);
		setLayout(new GridLayout(1, false));
		text = new Text(this, SWT.BORDER);
		GridDataFactory.fillDefaults().grab(true, false).applyTo(text);
		final Button btnMakeFiles = new Button(this, SWT.PUSH);
		btnMakeFiles.setText("MakeFiles");
		nextFileNumber = settings.startNumber;
		btnMakeFiles.addSelectionListener(new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				int numberOfFilesToMake = nextFileNumber;
				for (int i = 0; i < numberOfFilesToMake; i++) {
					String newFilename = String.format(settings.fileTemplatePrefix + settings.fileTemplate,
							nextFileNumber);
					nextFileNumber++;
					File file = new File(newFilename);
					try {
						file.createNewFile();
					} catch (IOException e1) {
					}
				}
				btnMakeFiles.setText(Integer.toString(nextFileNumber));

			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});
	}

	@Override
	public void processFile(String filename) {
		text.setText(filename);
	}

}

class LatestFileNameComposite extends Composite {

	private static final String AUTO_SKIP_TO_LATEST = "Auto skip to latest";

	private static final String WAITING = "Waiting...";

	public static final String EMPTY = "";

	private Text fileNameText;
	private Text textIndex;
	private FileProcessor fileProcessor;
	private IObserver observer;
	private Button btnSkipToStart;
	private Button btnSkipToLatest;
	private Button btnBackOne;
	private Button btnForwardOne;
	
	// Used when there's just one combined play/pause button
	private Button btnShowLatest;
	
	// Used when there are separate play/pause buttons
	private Button playButton;
	private Button pauseButton;

	private HighestExistingFileMonitorDataProvider highestExistingFileMonitorDataProvider;

	private HighestExistingFileMonitorData highestExistingFileMonitorData = null;
	private HighestExistingFileMonitorSettings latestSettings;
	private Integer latestFoundIndex = null;

	boolean selectLatestFoundIndex = true;

	Integer lastSelectedIndex = null;

	private Group group;

	private String label;
	
	private Image toStartImage;
	private Image toLatestImage;
	private Image pauseImage;
	private Image runImage;
	private Image backOneImage;
	private Image forwardOneImage;
	
	private boolean showButtonSeparator;
	
	private boolean separatePlayPauseButtons;
	
	public void setLabel(String label) {
		this.label = label;
	}
	
	public void setHighestExistingFileMonitorDataProvider(HighestExistingFileMonitorDataProvider highestExistingFileMonitorDataProvider) {
		this.highestExistingFileMonitorDataProvider = highestExistingFileMonitorDataProvider;
	}
	
	public void setFileProcessor(FileProcessor fileProcessor) {
		this.fileProcessor = fileProcessor;
	}
	
	public void setShowButtonSeparator(boolean showButtonSeparator) {
		this.showButtonSeparator = showButtonSeparator;
	}
	
	public void setSeparatePlayPauseButtons(boolean separatePlayPauseButtons) {
		this.separatePlayPauseButtons = separatePlayPauseButtons;
	}
	
	public void setImages(Image toStartImage, Image toLatestImage, Image pauseImage, Image runImage, Image backOneImage, Image forwardOneImage) {
		this.toStartImage = toStartImage;
		this.toLatestImage = toLatestImage;
		this.pauseImage = pauseImage;
		this.runImage = runImage;
		this.backOneImage = backOneImage;
		this.forwardOneImage = forwardOneImage;
	}

	public LatestFileNameComposite(Composite parent, int style) {
		super(parent, style);
	}
	
	public LatestFileNameComposite(Composite parent, int style, String label,
			HighestExistingFileMonitorDataProvider highestExistingFileMonitorDataProvider,
			final FileProcessor fileProcessor, Image toStartImage, Image toLatestImage, final Image pauseImage,
			final Image runImage, Image backOneImage, Image forwardOneImage) {
		super(parent, style);
		setLabel(label);
		setHighestExistingFileMonitorDataProvider(highestExistingFileMonitorDataProvider);
		setFileProcessor(fileProcessor);
		setImages(toStartImage, toLatestImage, pauseImage, runImage, backOneImage, forwardOneImage);
		createControls();
	}
	
	public void createControls() {
		GridLayoutFactory.fillDefaults().numColumns(1).applyTo(this);
		GridDataFactory.fillDefaults().applyTo(this);

		int numColumns = 5 + (showButtonSeparator ? 1 : 0) + (separatePlayPauseButtons ? 2 : 1);
		
		group = new Group(this, SWT.NONE);
		group.setText(label);
		GridLayoutFactory.swtDefaults().numColumns(numColumns).applyTo(group);
		GridDataFactory.fillDefaults().applyTo(group);

		group.setToolTipText("The latest detector filename is displayed. Press pause to scrolling back through all filenames in the current collection");
		fileNameText = new Text(group, SWT.SINGLE | SWT.BORDER);
		fileNameText.setText(WAITING);
		fileNameText.setEditable(false);
		GridDataFactory.fillDefaults().span(numColumns, 1).grab(true, false).applyTo(fileNameText);

		btnSkipToStart = new Button(group, SWT.PUSH);
		btnSkipToStart.setToolTipText("Skip to first");
		btnSkipToStart.setImage(toStartImage);
		GridDataFactory.fillDefaults().grab(false, false).applyTo(btnSkipToStart);
		
		btnSkipToStart.addSelectionListener(new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				setSelectLatestFoundIndex(false);
				setSelectedIndex(latestSettings.startNumber);
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});

		btnBackOne = new Button(group, SWT.PUSH);
		btnBackOne.setToolTipText("Back One Image");
		btnBackOne.setImage(backOneImage);
		GridDataFactory.fillDefaults().grab(false, false).applyTo(btnBackOne);
		
		btnBackOne.addSelectionListener(new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				setSelectLatestFoundIndex(false);
				setSelectedIndex(Math.max(latestSettings.startNumber, getSelectedIndex() - 1));
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});

		textIndex = new Text(group, SWT.SINGLE | SWT.BORDER);
		GridDataFactory.fillDefaults().grab(true, false).applyTo(textIndex);
		
		textIndex.addFocusListener(new FocusListener() {

			@Override
			public void focusLost(FocusEvent e) {
				processTextIndex();
			}

			@Override
			public void focusGained(FocusEvent e) {
				textIndex.selectAll();
			}
		});

		textIndex.addVerifyListener(new VerifyListener() {

			@Override
			public void verifyText(VerifyEvent e) {
				if (latestSettings == null || latestFoundIndex == null) {
					e.doit = false;
				} else {
					e.doit = e.text.isEmpty() || e.text.matches("[0-9]+");
				}
			}
		});

		textIndex.addKeyListener(new KeyListener() {

			@Override
			public void keyReleased(KeyEvent e) {
				if (e.keyCode == SWT.CR) {
					processTextIndex();
				}
			}

			@Override
			public void keyPressed(KeyEvent e) {
			}
		});

		btnForwardOne = new Button(group, SWT.PUSH);
		btnForwardOne.setToolTipText("Forward One Image");
		btnForwardOne.setImage(forwardOneImage);
		GridDataFactory.fillDefaults().grab(false, false).applyTo(btnForwardOne);
		
		btnForwardOne.addSelectionListener(new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				setSelectLatestFoundIndex(false);
				setSelectedIndex(Math.min(latestFoundIndex, getSelectedIndex() + 1));
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});

		btnSkipToLatest = new Button(group, SWT.PUSH);
		btnSkipToLatest.setToolTipText("Skip to latest");
		btnSkipToLatest.setImage(toLatestImage);
		GridDataFactory.fillDefaults().grab(false, false).applyTo(btnSkipToLatest);
		
		btnSkipToLatest.addSelectionListener(new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				setSelectLatestFoundIndex(false);
				setSelectedIndex(latestFoundIndex);
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});

		if (showButtonSeparator) {
			final Label separator = new Label(group, SWT.SEPARATOR | SWT.VERTICAL);
			GridDataFactory.fillDefaults().hint(SWT.DEFAULT, 0).grab(false, false).applyTo(separator);
		}
		
		if (!separatePlayPauseButtons) {
			btnShowLatest = new Button(group, SWT.TOGGLE);
			btnShowLatest.setToolTipText(AUTO_SKIP_TO_LATEST);
			btnShowLatest.setImage(pauseImage);
			GridDataFactory.fillDefaults().grab(false, false).applyTo(btnShowLatest);
			
			btnShowLatest.addSelectionListener(new SelectionListener() {
				
				@Override
				public void widgetSelected(SelectionEvent e) {
					boolean selection = btnShowLatest.getSelection();
					// selected means pause
					setPlaying(!selection);
				}
				
				@Override
				public void widgetDefaultSelected(SelectionEvent e) {
				}
			});
		}
		
		else {
			playButton = new Button(group, SWT.TOGGLE);
			playButton.setToolTipText(AUTO_SKIP_TO_LATEST);
			playButton.setImage(runImage);
			GridDataFactory.fillDefaults().grab(false, false).applyTo(playButton);
			
			pauseButton = new Button(group, SWT.TOGGLE);
			pauseButton.setToolTipText("Manual selection");
			pauseButton.setImage(pauseImage);
			GridDataFactory.fillDefaults().grab(false, false).applyTo(pauseButton);
			
			playButton.setSelection(true);
			
			playButton.addSelectionListener(new SelectionAdapter() {
				@Override
				public void widgetSelected(SelectionEvent e) {
					final boolean playSelected = playButton.getSelection();
					setPlaying(playSelected);
				}
			});
			
			pauseButton.addSelectionListener(new SelectionAdapter() {
				@Override
				public void widgetSelected(SelectionEvent e) {
					final boolean pauseSelected = pauseButton.getSelection();
					setPlaying(!pauseSelected);
				}
			});
		}

		setSelectedIndex(0);

		setVisible(true);
		setHighestExistingFileMonitorData(highestExistingFileMonitorDataProvider.getHighestExistingFileMonitorData());
		observer = new IObserver() {

			@Override
			public void update(Object source, final Object arg) {
				if (arg instanceof HighestExistingFileMonitorData) {
					PlatformUI.getWorkbench().getDisplay().asyncExec(new Runnable() {

						@Override
						public void run() {
							setHighestExistingFileMonitorData((HighestExistingFileMonitorData) arg);
						}

					});
				}

			}
		};
		highestExistingFileMonitorDataProvider.addIObserver(observer);
		
		addDisposeListener(new DisposeListener() {
			@Override
			public void widgetDisposed(DisposeEvent e) {
				highestExistingFileMonitorDataProvider.deleteIObserver(observer);
			}
		});
	}
	
	private void setPlaying(boolean playing) {
		setSelectLatestFoundIndex(playing);
		
		if (!separatePlayPauseButtons) {
			btnShowLatest.setImage(selectLatestFoundIndex ? pauseImage : runImage);
			btnShowLatest.setToolTipText(selectLatestFoundIndex ? "Manual selection" : AUTO_SKIP_TO_LATEST);
		}
		
		else {
			playButton.setSelection(playing);
			pauseButton.setSelection(!playing);
		}
	}

	private void processSelectedIndex() {
		if (latestSettings == null || latestFoundIndex == null)
			return;
		int index = getSelectedIndex();
		if (latestSettings != null) {
			
			String filename;
			String text;
			
			if (latestSettings.isEmpty()) {
				filename = "";
				text = WAITING;
			}
			
			else {
				filename = String.format(latestSettings.getFullTemplate(), index);
				text = String.format(latestSettings.fileTemplate, index);
				if( text.length() == 0)
					text = filename;
			}

			int currentLength = fileNameText.getText().length();
			int diff = text.length() - currentLength;
			boolean forceLayout = (diff > 0 || diff < -3);

			fileNameText.setText(text);
			if (forceLayout)
				EclipseWidgetUtils.forceLayoutOfTopParent(LatestFileNameComposite.this);

			fileProcessor.processFile(filename);

		}
	}

	protected void setSelectLatestFoundIndex(boolean selectLatestFoundIndex) {
		if (this.selectLatestFoundIndex != selectLatestFoundIndex) {
			this.selectLatestFoundIndex = selectLatestFoundIndex;
			if (selectLatestFoundIndex && latestFoundIndex != null) {
				setSelectedIndex(latestFoundIndex);
			}
			enableBtns();
		}
	}

	void setSelectedIndex(int selected) {
		lastSelectedIndex = selected;
		int newLength = Integer.toString(selected).length();
		int currentLength = textIndex.getText().length();
		textIndex.setText(Integer.toString(selected));
		int diff = newLength - currentLength;
		boolean forceLayout = (diff > 0 || diff < -3);

		if (forceLayout)
			EclipseWidgetUtils.forceLayoutOfTopParent(LatestFileNameComposite.this);
		processSelectedIndex();
		enableBtns();

	}

	int getSelectedIndex() {
		return lastSelectedIndex;
	}

	void enableBtns() {
		boolean fileFound = latestFoundIndex != null && latestSettings != null;
		boolean doNotShowLatestAndFileFound = !selectLatestFoundIndex && fileFound;
		if (doNotShowLatestAndFileFound) {
			int selectedIndex = getSelectedIndex();
			btnSkipToStart.setEnabled(selectedIndex > latestSettings.startNumber);
			btnBackOne.setEnabled(selectedIndex > latestSettings.startNumber);
			btnForwardOne.setEnabled(selectedIndex < latestFoundIndex);
			btnSkipToLatest.setEnabled(selectedIndex < latestFoundIndex);
		} else {
			btnSkipToStart.setEnabled(false);
			btnBackOne.setEnabled(false);
			btnForwardOne.setEnabled(false);
			btnSkipToLatest.setEnabled(false);

		}
		textIndex.setEnabled(doNotShowLatestAndFileFound);

	}

	private void setHighestExistingFileMonitorData(HighestExistingFileMonitorData data) {
		latestFoundIndex = null;
		highestExistingFileMonitorData = data;
		HighestExistingFileMonitorSettings settings = highestExistingFileMonitorData
				.getHighestExistingFileMonitorSettings();
		if (settings != null) {
			if (latestSettings == null || !latestSettings.equals(settings)) {
				latestSettings = settings;
				group.setText(label + " - " + latestSettings.fileTemplate);
				fileNameText.setToolTipText(String.format(latestSettings.fileTemplatePrefix
						+ latestSettings.fileTemplate, latestSettings.startNumber)
						+ " ...");
				btnSkipToStart.setToolTipText("Skip to first - " + latestSettings.startNumber);
				EclipseWidgetUtils.forceLayoutOfTopParent(LatestFileNameComposite.this);

			}
			latestFoundIndex = highestExistingFileMonitorData.getFoundIndex();
			if (latestFoundIndex != null)
				btnSkipToLatest.setToolTipText("Skip to latest - " + latestFoundIndex);

		} else {
			latestSettings = null;
		}
		if (selectLatestFoundIndex) {
			if (latestSettings != null && latestFoundIndex != null) {
				setSelectedIndex(latestFoundIndex);
			} else {
				fileNameText.setText(WAITING);
			}
		}
		enableBtns();
	}

	private void processTextIndex() {
		if (latestFoundIndex != null) {
			try {
				Integer input = new Integer(textIndex.getText());
				if (!(input >= latestSettings.startNumber && input <= latestFoundIndex))
					throw new Exception("Out of range");
				setSelectedIndex(input);
			} catch (Exception ex) {
				textIndex.setText(lastSelectedIndex != null ? lastSelectedIndex.toString() : "");
			}
		}
	}

}