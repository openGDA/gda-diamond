/*
For more information about Large File Support:	
see "Large File Support in Linux" (http://www.suse.de/~aj/linux_lfs.html)
*/

#include "Unix.h"

#include <stdlib.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>

#ifdef LINUX
#include <sys/vfs.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#endif
#ifdef SUN
#include <sys/statfs.h>
#endif
#ifdef IRIX
#include <sys/statfs.h>
#endif
#ifdef ALPHA
#include <sys/mount.h>
#endif

static char putenvString[120];
static char xformStatusFile[120];

static jfieldID xfsfFID = NULL;

JNIEXPORT void JNICALL 
Java_gda_util_Unix_initFIDs(JNIEnv *env, jclass cls)
{
   xfsfFID = (*env)->GetFieldID(env, cls, "xformStatusFile",
				"Ljava/lang/String;");
}

/**
This runs a script called restart_pcs on the raid machine which runs the
Quantum315 detector.  The GDA server and the remote machine must have rxec
setup for the account which the GDA server process runs in (.rhosts file in
the home directory on each, with permissions 644).

The script must be located in the home directory of this account and must have
the correct env vars required to operate the Q315.

On the GDA-side, the env vars CCD_DTHOSTNAME, REXEC_USER and REXEC_PASS must 
be defined. CCD_DTHOSTNAME comes from the ADSC source file and the others must 
be set for the GDA process account.
*/
JNIEXPORT void JNICALL 
Java_gda_util_Unix_doRestartQ315(JNIEnv *env, jclass cls)
{
   char command[120];
  
  //kill processes and restart framegrabber processes
  // sprintf(command,
//	   "rexec -l $REXEC_USER -p $REXEC_PASS $CCD_DTHOSTNAME /home/$REXEC_USER/restart_pcs");
   sprintf(command,
	   "rexec $CCD_DTHOSTNAME /home/$REXEC_USER/restart_pcs");
   system(command);
   
  //start det_api_workstation
  sprintf(command,
	   "rexec $CCD_DTHOSTNAME det_api_workstation&");
   system(command);
   
   //start ccd_image_gather
   sprintf(command,
	   "rexec $CCD_DTHOSTNAME ccd_image_gather&");
   system(command);
}


void killProcess(char *process)
{
   char command[120];
  
   sprintf(command,
	   "kill -9 `ps -ef | grep \"%s\" | "
	   "grep -v grep | "
	   "awk '{print $2}'` 2>/dev/null", process);
   system(command);
}

JNIEXPORT jint JNICALL
Java_gda_util_Unix_doGetDiskMB(JNIEnv *env, jobject obj, jstring path)
{
   struct statfs buf;
   int mb = -1;
   double bytes = 0;
   
   const char *str = (*env)->GetStringUTFChars(env, path, 0);

#ifdef LINUX
   if (!statfs(str, &buf))
   {
      bytes = (double) buf.f_blocks * (double) buf.f_bsize;
      mb = (int) (bytes / 1048576.0);
   }
#endif

#ifdef IRIX
   if (!statfs(str, &buf, sizeof(struct statfs), 0))
   {
      bytes = (double) buf.f_blocks * (double) buf.f_bsize;
      mb = (int) (bytes / 1048576.0);
   }
#endif

#ifdef ALPHA
   if (!statfs((char *)str, &buf))
   {
      bytes = (double) buf.f_blocks * (double) buf.f_bsize;
      mb = (int) ((bytes / 1048576.0) / 2.0);
   }
#endif

#ifdef SUN
   if (!statfs(str, &buf, sizeof(struct statfs), 0))
   {
      bytes = (double) buf.f_blocks * (double) buf.f_bsize / 16;
      mb = (int) (bytes / 1048576.0);
   }
#endif

   (*env)->ReleaseStringUTFChars(env, path, str);

   return mb;
}

JNIEXPORT jlong JNICALL
Java_gda_util_Unix_doGetFreeMB(JNIEnv *env, jobject obj, jstring path)
{
   struct statfs buf;
   long mb = -1;
   double bytes = 0;
   
   const char *str = (*env)->GetStringUTFChars(env, path, 0);

#ifdef LINUX
   if (!statfs(str, &buf))
   {
      long long int bytes_available = buf.f_bavail * buf.f_bsize;
      mb = bytes_available / 1024 / 1024;
   } else {
      int errno_saved = errno; // save prior to invoking other system calls
      fprintf(stderr, "doGetFreeMB: statfs failed (errno=%d): %s\n", errno_saved, strerror(errno_saved));
   }
#endif

#ifdef IRIX
   if (!statfs(str, &buf, sizeof(struct statfs), 0))
   {
      bytes = (double) buf.f_bfree * (double) buf.f_bsize;
      mb = (int) ((bytes / 1048576.0) / 2.0);
   }
#endif

#ifdef ALPHA
   if (!statfs((char *)str, &buf))
   {
      bytes = (double) buf.f_bavail * (double) buf.f_bsize;
      mb = (int) ((bytes / 1048576.0) / 16.0);
   }
#endif

#ifdef SUN
   if (!statfs(str, &buf, sizeof(struct statfs), 0))
   {
      bytes = (double) buf.f_bfree * (double) buf.f_bsize / 16;
      mb = (int) (bytes / 1048576.0);
   }
#endif

   (*env)->ReleaseStringUTFChars(env, path, str);

   return mb;
}

JNIEXPORT jint JNICALL
Java_gda_util_Unix_doSystem(JNIEnv *env, jobject obj, jstring command)
{
   int ret = -1;

   const char *str = (*env)->GetStringUTFChars(env, command, 0);
   ret = system(str);
   (*env)->ReleaseStringUTFChars(env, command, str);

   return ret;
}

JNIEXPORT jint JNICALL
Java_gda_util_Unix_doStartBLDaemon(JNIEnv *env, jobject obj)
{
   int ret = -1;
   char *daemon;
   char *portSwap;
   char blhost[160];
   char host[160];
   char command[160];
   char *user = getenv("USER");

   daemon =  (char *) getenv("CCD_BLSERVER");
   
   sprintf(blhost, "%s\0", getenv("CCD_BLHOSTNAME"));
   sprintf(host, "%s\0", getenv("HOST"));
  
   if ((strstr(host, blhost)) == NULL)
   {
      /* BLHOST is a remote machine, start daemon there */
      sprintf(
	 command,
	 "xterm -n \"ccd_bl log\" -T \"ccd_bl log\" -iconic "
	 "-e rsh pxws3 "
	 "'source ~adsc/ccd_dist/LOGIN_files/log_pxws3_api_421_mar_pxgen; "
	 "/usr/people/adsc/ccd_dist/bin/sgi/ccd_bl_mar' &");
      ret = system(command); 
   }
   else
   {
      /* BLHOST is this machine, start daemon here */
      portSwap = (char *) getenv("CCD_DCPORT_SWAP");

      if (portSwap != NULL)
      {
	 sprintf(putenvString, "CCD_DCPORT=%s", portSwap);
	 putenv(putenvString);
      }
      
      sprintf(command, "%s >/tmp/bl.log", daemon);
      if (user == NULL)
	 sprintf(command, "%s 2>&1 &", command);
      else
	 sprintf(command, "%s_%s 2>&1 &", command, user);
      ret = system(command);
   }
   
   return ret;
}

JNIEXPORT jint JNICALL Java_gda_util_Unix_doStart345Daemon
(JNIEnv *env, jobject obj, jstring hostName, jstring port)
{
   int ret = -1;
   char *daemon = "scan345";

   killProcess(daemon);

   /* Start the daemon. */
   ret = system(getenv("PXGEN_SCAN345_COMMAND"));

   sleep(2);

   return ret;
}

JNIEXPORT jint JNICALL Java_gda_util_Unix_doEnd345Daemon
  (JNIEnv *env, jobject obj)
{
   int ret = 0;

   killProcess("scan345");
   sleep(2);

   return ret;
}

JNIEXPORT jint JNICALL
Java_gda_util_Unix_doStartMarDaemon(JNIEnv *env, jobject obj)
{
   int ret = -1;

   char *daemon = "mardc -h";
   char command[120];
   char *user = getenv("USER");

   killProcess(daemon);

   sprintf(command, "xterm -n \"mardc\" -T \"mardc\" -iconic "
	   "-e %s", daemon);
   if (user == NULL)
      sprintf(command, "%s >/tmp/marLog 2>&1 &", command);
   else
      sprintf(command, "%s >/tmp/marLog_%s 2>&1 &", command, user);

   ret = system(command);

   return ret;
}

JNIEXPORT jint JNICALL
Java_gda_util_Unix_doStartMarSimulator(JNIEnv *env, jobject obj)
{
   int ret = -1;

   char *daemon = "mardc -s";
   char command[120];
   char *user = getenv("USER");

   killProcess(daemon);

   sprintf(command, "xterm -n \"mardc\" -T \"mardc\" -iconic "
	   "-e %s", daemon);
   if (user == NULL)
      sprintf(command, "%s >/tmp/marLog 2>&1 &", command);
   else
      sprintf(command, "%s >/tmp/marLog_%s 2>&1 &", command, user);
	
   ret = system(command);

   return ret;
}

JNIEXPORT jint JNICALL
Java_gda_util_Unix_doEndMarDaemon(JNIEnv *env, jobject obj)
{
   int ret = 0;

   killProcess("mardc -h");

   return ret;
}

JNIEXPORT jint JNICALL
Java_gda_util_Unix_doEndMarSimulator(JNIEnv *env, jobject obj)
{
   int ret = 0;

   killProcess("mardc -s");

   return ret;
}

JNIEXPORT jint JNICALL
Java_gda_util_Unix_doStart345Simulator(JNIEnv *env, jobject obj, jstring port)
{
   int ret = -1;
   char *daemon;
   char command[120];

   const char *str = (*env)->GetStringUTFChars(env, port, 0);

   daemon = "marsim";

   killProcess(daemon);
   
   sprintf(command,"xterm -n \"Marsim\" -T \"Marsim\" -iconic "
	   "-e %s -port %s >/tmp/mar.log 2>&1 &",
	   daemon, str);
   ret = system(command);

   sleep(2);

   (*env)->ReleaseStringUTFChars(env, port, str);

   return ret;
}

JNIEXPORT jint JNICALL
Java_gda_util_Unix_doStopQ4Xform(JNIEnv *env, jobject obj)
{
   int ret = 0;

   killProcess("ccd_xform_new_api");

   return ret;
}

JNIEXPORT jint JNICALL
Java_gda_util_Unix_doStartQ4Xform(JNIEnv *env, jobject obj)
{
   int ret = -1;
   char command[120];

   char *xform = getenv("Q4_XFORM");
   killProcess(xform);

   sprintf(command, "xterm -n \"Xform log\" -T \"Xform log\" -iconic "	  
	   "-e %s &", xform);
   ret = system(command);

   return ret;
}

JNIEXPORT jint JNICALL
Java_gda_util_Unix_doStartPXGEN(JNIEnv *env, jobject obj)
{
   int ret = -1;
   char command[120];

   sprintf(command, getenv("PXGEN_COMMAND"));
   ret = system(command);
  
   return ret;
}

JNIEXPORT jint JNICALL
Java_gda_util_Unix_doStartAdxv(JNIEnv *env, jobject obj)
{
   int ret = -1;
   char command[120];

   killProcess("adxv");
   
   sprintf(command, "adxv -autoload &");
   ret = system(command);
  
   return ret;
}

JNIEXPORT jint JNICALL
Java_gda_util_Unix_doEndAdxv(JNIEnv *env, jobject obj)
{
  int ret = 0;

  killProcess("adxv");

  return ret;
}

JNIEXPORT jint JNICALL
Java_gda_util_Unix_doResetXformStatusFile(JNIEnv *env, jobject obj)
{
   int ret = -1;
   char newXformStatusFile[120] = "";
   jstring jstr;
  
   sprintf(newXformStatusFile, "%s_pxgen", getenv("XFORMSTATUSFILE"));
   sprintf(putenvString, "XFORMSTATUSFILE=%s", newXformStatusFile);
   putenv(putenvString);
   
   /*
    * Sets the instance variable xformStatusFile in the invoking instance
    * of Unix.java.
    * See initFIDs routine above.
    */
   
   jstr = (*env)->NewStringUTF(env, newXformStatusFile);
   (*env)->SetObjectField(env, obj, xfsfFID, jstr);
}

JNIEXPORT jint JNICALL Java_gda_util_Unix_doGetSocketState(JNIEnv *env, jobject this, jint fd, jobject ret) {

#ifndef LINUX
	return 1;

#else
	jclass cls;
	jfieldID state_field;
	jfieldID errno_field;
	jfieldID errmsg_field;
	int result;
	
	struct tcp_info info;
	int infolen;
	
	/* Get references to the GetSocketStateReturn (GSSR) class... */
	cls = (*env)->GetObjectClass(env, ret);
	
	/* ...and its fields */
	state_field = (*env)->GetFieldID(env, cls, "state", "I");
	if (state_field == NULL) {
		return 2;
	}
	errno_field = (*env)->GetFieldID(env, cls, "errno", "I");
	if (errno_field == NULL) {
		return 3;
	}
	errmsg_field = (*env)->GetFieldID(env, cls, "errmsg", "Ljava/lang/String;");
	if (errmsg_field == NULL) {
		return 4;
	}
	
	/* Attempt to get the socket's state */
	infolen = sizeof(struct tcp_info);
	result = getsockopt(fd, IPPROTO_TCP, TCP_INFO, &info, &infolen);
	
	if (result == -1) {
		/* Failed. Put error details in the GSSR object */
		int errno_copy = errno;
		(*env)->SetIntField(env, ret, errno_field, errno_copy);
		if (errno_copy < sys_nerr) {
			jstring errmsg_str = (*env)->NewStringUTF(env, sys_errlist[errno_copy]);
			(*env)->SetObjectField(env, ret, errmsg_field, errmsg_str);
		}
	}
	
	else {
		/* Succeeded. Put state into the GSSR object */
		(*env)->SetIntField(env, ret, state_field, info.tcpi_state);
	}
	
	return 0;

#endif
}
