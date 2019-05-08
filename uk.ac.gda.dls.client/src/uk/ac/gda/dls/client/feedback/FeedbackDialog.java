/*-
 * Copyright © 2013 Diamond Light Source Ltd.
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

package uk.ac.gda.dls.client.feedback;

import java.util.Arrays;

import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.jobs.Job;
import org.eclipse.jface.dialogs.TitleAreaDialog;
import org.eclipse.jface.layout.GridDataFactory;
import org.eclipse.jface.layout.GridLayoutFactory;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.ImageData;
import org.eclipse.swt.graphics.ImageLoader;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.FileDialog;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Layout;
import org.eclipse.swt.widgets.List;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.eclipse.ui.PlatformUI;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.configuration.properties.LocalProperties;
import gda.util.Email;
import uk.ac.gda.dls.client.Activator;

public class FeedbackDialog extends TitleAreaDialog {
	private static final Logger logger = LoggerFactory.getLogger(FeedbackDialog.class);
	private Text nameText;
	private Text emailText;
	private Text subjectText;
	private Text descriptionText;
	private List attachedFileList;
	private String[] fileList;
	private Composite topParent;
	private boolean hasFiles = false;
	private boolean screenshot = false;
	private Group attachments;

	public FeedbackDialog(Shell shell) {
		super(shell);
		setShellStyle(SWT.RESIZE);
	}

	@Override
	public void create() {
		super.create();
		getShell().setText("Send feedback");
		setTitle("Send feedback");
		setMessage("Enter your details below to provide feedback about GDA or the beamline.");
	}

	@Override
	protected Control createDialogArea(Composite parent) {
		topParent = parent;
		GridLayoutFactory.swtDefaults().applyTo(parent);

		Label nameLabel = new Label(parent, SWT.NONE);
		nameLabel.setText("Your name");

		nameText = new Text(parent, SWT.BORDER);
		GridDataFactory.fillDefaults().grab(true, false).applyTo(nameText);

		Label emailLabel = new Label(parent, SWT.NONE);
		emailLabel.setText("Your email address");

		emailText = new Text(parent, SWT.BORDER);
		GridDataFactory.fillDefaults().grab(true, false).applyTo(emailText);

		Label subjectLabel = new Label(parent, SWT.NONE);
		subjectLabel.setText("Subject");

		subjectText = new Text(parent, SWT.BORDER);
		GridDataFactory.fillDefaults().grab(true, false).applyTo(subjectText);

		Label descriptionLabel = new Label(parent, SWT.NONE);
		descriptionLabel.setText("Description");

		descriptionText = new Text(parent, SWT.BORDER | SWT.MULTI | SWT.WRAP | SWT.V_SCROLL);
		GridDataFactory.fillDefaults().hint(SWT.DEFAULT, 200).grab(true, true).applyTo(descriptionText);

		createAttachments(parent);

		return parent;
	}

	@Override
	protected void createButtonsForButtonBar(Composite parent) {

		GridData data = new GridData(SWT.FILL, SWT.FILL, false, true, 4, 1);
		GridLayout layout = new GridLayout(5, false);
		parent.setLayoutData(data);
		parent.setLayout(layout);

		Button attachButton = new Button(parent, SWT.TOGGLE);
		attachButton.setText("Attach File(s)");
		attachButton.setToolTipText("Add files to feedback");

		final Button screenGrabButton = new Button(parent, SWT.CHECK);
		screenGrabButton.setText("Include Screenshot");
		screenGrabButton.setToolTipText("Send screenshot with feedback");

		Label space = new Label(parent, SWT.NONE);
		space.setLayoutData(new GridData(SWT.CENTER, SWT.CENTER,true, true));

		Button sendButton = new Button(parent, SWT.PUSH);
		sendButton.setText("Send");

		Button cancelButton = new Button(parent, SWT.PUSH);
		cancelButton.setText("Cancel");

		sendButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {

				final String name = nameText.getText();
				final String email = emailText.getText();
				final String subject = subjectText.getText();
				final String description = descriptionText.getText();

				fileList = attachedFileList.getItems();

				Job job = new Job("Send feedback email") {
					@Override
					protected IStatus run(IProgressMonitor monitor) {

						try{
							final String recipientsProperty = LocalProperties.get("gda.feedback.recipients", "dag-group@diamond.ac.uk");
							final String[] recipients = Arrays.stream(recipientsProperty.split(" "))
									.map(String::trim)
									.toArray(String[]::new);

							final String beamlineName = LocalProperties.get("gda.beamline.name", "Beamline Unknown");
							final String mailSubject = String.format("[GDA feedback - %s] %s", beamlineName.toUpperCase(), subject);

							Email emailMessage = new Email().subject(mailSubject)
									.to(recipients)
									.from(name, email)
									.message(description)
									.attach(fileList);

							if (FeedbackDialog.this.screenshot) {
								PlatformUI.getWorkbench().getDisplay().syncExec(() -> {
										String fileName = "/tmp/feedbackScreenshot.png";
										captureScreen(fileName);
										emailMessage.attach(fileName);
								});
							}
							emailMessage.send();
							return Status.OK_STATUS;
						} catch(Exception ex){
							logger.error("Could not send feedback", ex);
							return new Status(IStatus.ERROR, Activator.PLUGIN_ID, 1, "Error sending email", ex);
						}
					}
				};

				job.schedule();

				setReturnCode(OK);
				close();
			}
		});

		cancelButton.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				setReturnCode(CANCEL);
				close();
			}
		});

		attachButton.addSelectionListener(new SelectionListener() {

			@Override
			public void widgetSelected(SelectionEvent e) {
				hasFiles = !hasFiles;
				GridData data = ((GridData)attachments.getLayoutData());
				data.exclude = !hasFiles;
				attachments.setVisible(hasFiles);
				topParent.layout();
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});

		screenGrabButton.addSelectionListener(new SelectionListener() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				screenshot = ((Button)e.widget).getSelection();
			}

			@Override
			public void widgetDefaultSelected(SelectionEvent e) {
			}
		});
	}

	private void createAttachments(Composite parent) {

		attachments = new Group(parent, SWT.NONE);
		attachments.setVisible(false);
		attachments.setText("Attachments");
		Layout layout = new GridLayout(2,false);
		attachments.setLayout(layout);

		GridData data = new GridData();
		data.exclude = true;
		data.horizontalAlignment = SWT.FILL;
		attachments.setLayoutData(data);

		attachedFileList = new List(attachments, SWT.V_SCROLL | SWT.H_SCROLL | SWT.MULTI);
		GridData aFLData = new GridData(SWT.FILL, SWT.FILL, true, true, 1, 2);
		aFLData.widthHint = parent.getSize().y;
		attachedFileList.setLayoutData(aFLData);

		Button addAttachment = new Button(attachments, SWT.PUSH);
		addAttachment.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		addAttachment.setText("Add");
		addAttachment.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				FileDialog fd = new FileDialog(Display.getCurrent().getActiveShell(), SWT.OPEN);
				fd.setText("Add");
				fd.setFilterPath(System.getProperty("user.home"));
				String selected = fd.open();
				attachedFileList.add(selected);
			}
		});

		Button removeAttachment = new Button(attachments, SWT.PUSH);
		removeAttachment.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, false, false));
		removeAttachment.setText("Remove");
		removeAttachment.addSelectionListener(new SelectionAdapter() {
			@Override
			public void widgetSelected(SelectionEvent e) {
				attachedFileList.remove(attachedFileList.getSelectionIndices());
			}
		});


	}

	private void captureScreen(final String filename) {
		final Display parent = PlatformUI.getWorkbench().getDisplay();
		saveShellImage(parent, filename);
	}

	private void saveShellImage(Display shell, String filename) {
		Image image = new Image(PlatformUI.getWorkbench().getDisplay(), shell.getClientArea());
		GC gc = new GC(shell);
		gc.copyArea(image, 0, 0);
		gc.dispose();
		ImageLoader loader = new ImageLoader();
		ImageData imageData = image.getImageData();
		loader.data = new ImageData[] { imageData };
		loader.save(filename, SWT.IMAGE_PNG);
		image.dispose();
	}
}
