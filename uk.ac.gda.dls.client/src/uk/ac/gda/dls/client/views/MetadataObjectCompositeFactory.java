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

import java.text.DecimalFormat;
import java.util.List;

import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.FocusEvent;
import org.eclipse.swt.events.FocusListener;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Scrollable;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.springframework.beans.factory.InitializingBean;

import gda.data.metadata.GDAMetadataProvider;
import gda.data.metadata.GdaMetadata;
import gda.data.metadata.IMetadataEntry;
import gda.data.metadata.Metadata;
import gda.data.metadata.StoredMetadataEntry;
import gda.observable.IObserver;
import gda.rcp.views.CompositeFactory;
import uk.ac.gda.ui.utils.SWTUtils;

/**
 * Create composites linked to a specific piece of metadata. Editable by user but should pick up if metadata changes.
 * <p>
 * This has a variety of styles depending on the nature of the data to be stored.
 * <p>
 * Outputformat should be a String acceptable either to String.format or DecimalFormat  i.e. similar to "%s" or "###.##"
 */
public class MetadataObjectCompositeFactory implements CompositeFactory, InitializingBean {
	public static final String LABEL_STYLE = "label";
	public static final String TEXTAREA_STYLE = "area";
	public static final String COMBOBOX_STYLE = "combo";

	String label;
	String metadataName;
	String outputFormat;
	String unitString = "";  // optional so default is empty String
	String styleChoice = LABEL_STYLE;
	String[] comboChoices;
	Integer columnWidth = 1;
	IMetadataEntry entry;

	@Override
	public void afterPropertiesSet() throws Exception {
		if (label == null)
			throw new IllegalArgumentException("label is null");
		if (metadataName == null)
			throw new IllegalArgumentException("metadataName is null");
		if (outputFormat == null)
			throw new IllegalArgumentException("outputFormat is null");

		if (styleChoice.equals(COMBOBOX_STYLE) && comboChoices == null) {
			throw new IllegalArgumentException("comboChoices is null when style set to " + COMBOBOX_STYLE);
		}

		List<IMetadataEntry> entries = GDAMetadataProvider.getInstance().getMetadataEntries();

		for (IMetadataEntry entry : entries) {
			if (entry.getName().equals(metadataName)) {
				this.entry = entry;
			}
		}
		if (entry == null) {
			throw new IllegalArgumentException(String.format("metadata entry named %s cannot be found!", metadataName));
		}
	}

	@Override
	public Composite createComposite(Composite parent, int style) {
		return new MetadataObjectComposite(parent, style, getLabel(),
				entry, outputFormat, unitString, styleChoice, comboChoices, columnWidth);
	}

	public String getLabel() {
		return label;
	}

	public void setLabel(String label) {
		this.label = label;
	}

	public String getMetadataName() {
		return metadataName;
	}

	public void setMetadataName(String metadataName) {
		this.metadataName = metadataName;
	}

	public String getOutputFormat() {
		return outputFormat;
	}

	public void setOutputFormat(String outputFormat) {
		this.outputFormat = outputFormat;
	}

	public String getUnitString() {
		return unitString;
	}

	public void setUnitString(String unitString) {
		this.unitString = unitString;
	}

	public String getStyle() {
		return styleChoice;
	}

	public void setStyle(String style) {
		this.styleChoice = style;
	}

	public String[] getComboChoices() {
		return comboChoices;
	}

	public void setComboChoices(String[] comboChoices) {
		this.comboChoices = comboChoices;
	}

	public Integer getColumnWidth() {
		return columnWidth;
	}

	public void setColumnWidth(Integer columnWidth) {
		this.columnWidth = columnWidth;
	}

	/*
	 * Ensure plugin containing the icons is set to be the default working folder
	 */
	public static void main(String... args) throws Exception {

		Display display = new Display();
		Shell shell = new Shell(display);
		GridLayoutFactory.fillDefaults().numColumns(1).applyTo(shell);

		StoredMetadataEntry testEntry = new StoredMetadataEntry("testing", "12.0");
		StoredMetadataEntry testEntry2 = new StoredMetadataEntry("testing2", "76.0");
		Metadata testMetadata = new GdaMetadata();
		testMetadata.addMetadataEntry(testEntry);
		testMetadata.addMetadataEntry(testEntry2);
		GDAMetadataProvider.setInstanceForTesting(testMetadata);

		final MetadataObjectComposite compo = new MetadataObjectComposite(shell, SWT.NONE, "hello", testEntry,
				"%s", null, LABEL_STYLE, new String[] {}, 1);
		GridDataFactory.fillDefaults().applyTo(compo);
		compo.setVisible(true);

		final MetadataObjectComposite compo2 = new MetadataObjectComposite(shell, SWT.NONE, "hello2",
				testEntry, "%s", "", COMBOBOX_STYLE, new String[] { "first choice", "second choice" }, 1);
		GridDataFactory.fillDefaults().applyTo(compo2);
		compo2.setVisible(true);

		final MetadataObjectComposite compo3 = new MetadataObjectComposite(shell, SWT.NONE, "hello3",
				testEntry, "%s","", TEXTAREA_STYLE, new String[] {}, 1);
		GridDataFactory.fillDefaults().applyTo(compo3);
		compo3.setVisible(true);

		final MetadataObjectComposite compo4 = new MetadataObjectComposite(shell, SWT.NONE, "hello4",
				testEntry2, "###.##","mm", LABEL_STYLE, new String[] {}, 1);
		GridDataFactory.fillDefaults().applyTo(compo4);
		compo4.setVisible(true);

		shell.pack();
		shell.setSize(400, 400);
		SWTUtils.showCenteredShell(shell);
	}

}

class MetadataObjectComposite extends Composite {

	Display display;
	String label;
	IMetadataEntry entry;
	String valueToDisplay = "";
	private Scrollable text;
	private IObserver observer;
	private String outputFormat;
	private String styleChoice;
	private String unitString = "";

	public MetadataObjectComposite(Composite parent, int style, String label,
			final IMetadataEntry entry, String outputFormat, String unitString, String styleChoice, String[] comboChoices,
			Integer columnWidth) {
		super(parent, style);
		this.label = label;
		this.entry = entry;
		this.outputFormat = outputFormat;
		if (unitString != null) {
			this.unitString = unitString;
		}
		this.styleChoice = styleChoice;

		GridLayoutFactory.fillDefaults().numColumns(2).applyTo(this);
		if (styleChoice.equals(MetadataObjectCompositeFactory.TEXTAREA_STYLE)) {
			GridData gd = new GridData(SWT.FILL, SWT.FILL, true, true, columnWidth, 1);
			this.setLayoutData(gd);
		} else {
			GridData gd = new GridData(SWT.FILL, SWT.FILL, true, false, columnWidth, 1);
			this.setLayoutData(gd);
		}

		Label lbl = new Label(this, SWT.NONE | SWT.CENTER);
		lbl.setText(this.label);

		if (styleChoice.equals(MetadataObjectCompositeFactory.LABEL_STYLE)) {
			int textStyle = SWT.SINGLE | SWT.BORDER | SWT.CENTER;
			text = new Text(this, textStyle);
			GridData gd = new GridData(SWT.FILL, SWT.FILL, true, false);
			text.setLayoutData(gd);
		} else if (styleChoice.equals(MetadataObjectCompositeFactory.TEXTAREA_STYLE)) {
			int textStyle = SWT.MULTI | SWT.BORDER | SWT.LEFT;
			text = new Text(this, textStyle);
			GridData gd = new GridData(SWT.FILL, SWT.FILL, true, true);
			text.setLayoutData(gd);
		} else if (styleChoice.equals(MetadataObjectCompositeFactory.COMBOBOX_STYLE)) {
			int textStyle = SWT.DROP_DOWN | SWT.BORDER | SWT.CENTER;
			text = new Combo(this, textStyle);
			((Combo) text).setItems(comboChoices);
			((Combo) text).setEnabled(true);
			GridData gd = new GridData(SWT.FILL, SWT.FILL, true, false);
			text.setLayoutData(gd);
		}

		if (styleChoice.equals(MetadataObjectCompositeFactory.COMBOBOX_STYLE)) {
			((Combo) text).addModifyListener(createComboModifyListener());
		} else {
			((Text) text).addFocusListener(createTextFocusListener());
		}

		observer = new IObserver() {
			@Override
			public void update(Object source, Object arg) {
				if (source instanceof IMetadataEntry) {
					if (((IMetadataEntry) source).getName().equals(entry.getName())) {
						setVal(arg.toString());
					}
				}
			}
		};

		setVal(entry.getMetadataValue());

		GDAMetadataProvider.getInstance().addIObserver(observer);
	}

	private ModifyListener createComboModifyListener() {
		return new ModifyListener() {
			@Override
			public void modifyText(ModifyEvent e) {
				int index = ((Combo) text).getSelectionIndex();
				String selection = ((Combo) text).getItem(index);
				GDAMetadataProvider.getInstance().setMetadataValue(entry.getName(), selection);
			}
		};
	}

	public FocusListener createTextFocusListener() {
		return new FocusListener() {
			@Override
			public void focusGained(FocusEvent e) {
			}

			@Override
			public void focusLost(FocusEvent e) {
				String theText = ((Text) text).getText();
				if (unitString.isEmpty()) {
					GDAMetadataProvider.getInstance().setMetadataValue(entry.getName(), theText );
				} else {
					if (theText.endsWith(unitString)) {
						GDAMetadataProvider.getInstance().setMetadataValue(entry.getName(), theText );
					} else {
						GDAMetadataProvider.getInstance().setMetadataValue(entry.getName(), theText  + unitString);
					}
				}
			}
		};
	}

	void setVal(String newVal) {
		String formattedString = "";
		if (outputFormat.contains("s")) {
			formattedString = String.format(outputFormat, newVal);
		} else if (!unitString.isEmpty() && newVal.endsWith(unitString)){
			formattedString = newVal;
		}else {
			try{
				formattedString = new DecimalFormat(outputFormat).format(Double.parseDouble(newVal));
			} catch(NumberFormatException e) {
				formattedString="not set";
			}
			if (!unitString.isEmpty()) {
				formattedString += unitString;
			}
		}

		final String newValueToDisplay = formattedString;

		if (!newValueToDisplay.equals(valueToDisplay) && !isDisposed()) {
			valueToDisplay = newValueToDisplay;
			display.asyncExec(new Runnable() {
				@Override
				public void run() {
					if (styleChoice.equals(MetadataObjectCompositeFactory.COMBOBOX_STYLE)) {
						int newindex = ((Combo) text).indexOf(valueToDisplay);
						((Combo) text).select(newindex);
					} else {
						((Text) text).setText(valueToDisplay);
					}
				}
			});
		}
	}

	@Override
	public void dispose() {
		entry.deleteIObserver(observer);
		super.dispose();
	}

}