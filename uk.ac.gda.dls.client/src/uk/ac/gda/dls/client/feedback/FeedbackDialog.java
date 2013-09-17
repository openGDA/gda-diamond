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

import gda.configuration.properties.LocalProperties;

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
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSenderImpl;

import uk.ac.gda.dls.client.Activator;

public class FeedbackDialog extends TitleAreaDialog {

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
	
	private Text nameText;
	private Text emailText;
	private Text subjectText;
	private Text descriptionText;
	
	@Override
	protected Control createDialogArea(Composite parent) {
		
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
		
		return parent;
	}
	
	@Override
	protected void createButtonsForButtonBar(Composite parent) {
		
		GridLayoutFactory.swtDefaults().numColumns(2).applyTo(parent);
		
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
				
				Job job = new Job("Send feedback email") {
					@Override
					protected IStatus run(IProgressMonitor monitor) {
						
						try{
							final String recipientsProperty = LocalProperties.get("gda.feedback.recipients","dag-group@diamond.ac.uk");
							final String[] recipients = recipientsProperty.split(" ");
							for (int i=0; i<recipients.length; i++) {
								recipients[i] = recipients[i].trim();
							}
							
							final String from = String.format("%s <%s>", name, email);
							
							final String beamlineName = LocalProperties.get("gda.beamline.name.upper","Beamline Unknown");
							final String mailSubject = String.format("[GDA feedback - %s] %s", beamlineName, subject);
							
							final String smtpHost = LocalProperties.get("gda.feedback.smtp.host","localhost");
							
							JavaMailSenderImpl mailSender = new JavaMailSenderImpl();
							mailSender.setHost(smtpHost);
							
							SimpleMailMessage message = new SimpleMailMessage();
							message.setFrom(from);
							message.setTo(recipients);
							message.setSubject(mailSubject);
							message.setText(description);
							
							mailSender.send(message);
							return Status.OK_STATUS;
						} catch(Exception ex){
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
		
	}

}
