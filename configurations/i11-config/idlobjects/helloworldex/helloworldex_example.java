/*
'  Copyright (c) 2005-2009, ITT Visual Information Solutions. All
'       rights reserved. Unauthorized reproduction is prohibited.
'
'+
'  FILE:
'       helloworldex_example.java
'
'  CALLING SEQUENCE: None.
'
'  PURPOSE:
'       Demonstrates how to access features of a custom IDL object in a
'       Java application once the IDL object has been exported by the IDL
'       Bridge Export Assistant. This object prints a simple Hello World message
'       to the console window. For instructions on using this Java file, search
'       the Online Help index for the name of this file..
'
'  MAJOR TOPICS: Bridges
'
'  EXTERNAL FUNCTIONS, PROCEDURES, and FILES:
'       Use the Export Bridge Assistant to export helloworldex__define.pro
'       Classpath must reference javaidlb.jar
'
'  NAMED STRUCTURES:
'       none.
'
'  COMMON BLOCS:
'       none.
'
'  MODIFICATION HISTORY:
'       1/06,   SM - written
'-
'-----------------------------------------------------------------
*/
package helloworldex;
import com.idl.javaidl.*;
public class helloworldex_example extends helloworldex
{
   private helloworldex hwObj;

   // Constructor
   public helloworldex_example() {
      hwObj = new helloworldex();
      hwObj.createObject();
      JIDLString result =
         hwObj.HELLOFROM
         (new JIDLString("Opus of Bloom County"));
      System.out.println(result.stringValue());
   }

   public static void main(String[] argv) {
      helloworldex_example example =
         new helloworldex_example();
   }
}
