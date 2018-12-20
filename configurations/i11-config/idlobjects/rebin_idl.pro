;==========================================================
;I11 REBIN PROGRAM -SP THOMPSON APRIL 2010
;REQUIRES THE FOLLOWING TO BE STORED ON IDL PATH
;
;    (1) READ_ASCII_SPT.PRO
;    (2) MAC_ARM_CALIBRATION_2009.txt
;    (3) MAC_CRYSTAL_OFFSETS_2009.txt
;
;ONLY WORKS FOR DATA COLLECTED AFTER CVSCAN WAS UPDATED TO
;AUTOMATICALLY START AT -7 DEG 2THETA. OTHERWISE USE OLD 
;PYTHON REBIN SCRIPT
;===========================================================

pro output_detector_chanels,x,y,out_path,file_number,ave_mon
  ;
  ;=====================================
  ;THIS PRO OUTPUTS 45 DETECTOR CHANNELS
  ;=====================================
  ;
  catch,error_status
  if error_status ne 0 then begin
     print,"***-FAILED IN output_detector_chanels"
     catch,/cancel
     return
  endif
  ;
  print,"writing detector files..."
  summed_file_stem=out_path+file_number+"_"
  ;
  for j=0,44 do begin
    if j le 8 then begin
      ds=strcompress(" 0") ;so that channel numbers in file name go from 01 to 45
    endif else begin
      ds=""
    endelse
    ;
    det_summed_file=summed_file_stem+strcompress(ds,/remove_all)+strcompress(string(j+1),/remove_all)
    openw,1,det_summed_file+".dat"
    ;
    printf,1,"NORMALISED CHANNEL DATA  AVE_MON:"+string(ave_mon)
    printf,1,file_number
    printf,1,"detector number:"+string(j+1)
    for i=0L,n_elements(x(0,*))-1 do begin
       printf,1,x(j,i),y(j,i)
    endfor
    printf,1,"END OF DATA"
    ;
    close, 1
  endfor
end

pro output_rebined_file,file_name,out_path,header,x,y,err_y,user_comment,xmin,xmax,argument
  ;
  ;=========================================
  ;THIS PRO OUTPUTS THE REBINNED/SUMMED FILE
  ;=========================================
  ;
  catch,error_status
  if error_status ne 0 then begin
     print,"***-FAILED IN output_rebined_file"
     catch,/cancel
     return
  endif
  ;
  case 1 of
     ((argument eq "-A") OR $
      (argument eq "-B")):$
                    begin
                      ;write file in format suitable for reading straight into Topaz
                      print,"writing headerless *.xye file for Topaz"
                      rebin_extension="reb"
                      file_extension=".xye"
                      write_header=0
                    end
     ((argument eq "-a") OR $
      (argument eq "-b")):$
                   begin
                      ;standard output for gda
                      rebin_extension="red"
                      file_extension=".dat"
                      write_header=1
                    end
  endcase
  case 1 of
    user_comment ne "":begin
                         appendage=rebin_extension+"_"+strcompress(user_comment,/remove_all)+file_extension
                       end
    else:begin
           appendage=rebin_extension+file_extension
         end
  endcase
  print,"writing to",out_path+file_name+appendage
  index1=where(x lt xmin, count1)
  index2=where(x ge xmax, count2)
  x=x(index1(count1-1):index2(0)-1)
  y=y(index1(count1-1):index2(0)-1)
  e=err_y(index1(count1-1):index2(0)-1)
  openw,1,out_path+file_name+appendage
  case write_header of
     1:begin
         for i=0,n_elements(header)-1 do begin
            printf,1,header(i)
         endfor
         printf,1," 2theta	Counts	Error	IoIe"
        end
     else:;continue
  endcase
  for i=0L,n_elements(x)-1 do begin
     printf,1,format='(%"%f\t%f\t%f")',x(i),y(i),e(i)
  endfor
  close, 1
end

pro output_rebinned_macs_files,file_name,out_path,x,y,err_y,user_comment
  ;
  ;=====================================================
  ;THIS PRO OUTPUTS DATA REBINNED TO 5 SEPARATE MAC ARMS
  ;=====================================================
  ;
  catch,error_status
  if error_status ne 0 then begin
     print,"***-FAILED IN output_rebined_macs"
     catch,/cancel
     return
  endif
  ;
  for i=0,4 do begin
    appendage="_mac_"+strcompress(string(i+1),/remove_all)+strcompress(user_comment,/remove_all)+".dat"
    print,"writing to",out_path+file_name+appendage
    openw,1,out_path+file_name+appendage
    printf,1,"tth ","counts "," err"
    for j=0L,n_elements(x)-1 do begin
       printf,1,x(j),y(i,j),err_y(i,j)
    endfor
    close,1
  endfor

end

pro go_for_it_dectector,mac_columns,crystal_offsets,x_raw,y_raw,y_det,m_raw,ave_mon
  ;
  ;=========================================================================
  ;THIS PRO CORRECTS TTH OFFSETS AND NORMALISES INDIVIDUAL DETECTOR CHANNELS
  ;=========================================================================
  ;
  catch,error_status
  if error_status ne 0 then begin
     print,"***-FAILED IN go_for_it_detector"
     catch,/cancel
     return
  endif
  ;
  mac_count=n_elements(mac_columns)
  ;
  ;offset tth values here
  for j=0,mac_count-1 do begin
     x_raw(j,*)=x_raw(j,*)+crystal_offsets(j)
  endfor
  ;
  ;find average monitor
  ave_m=moment(m_raw(*))
  ave_mon=ave_m(0)
  ;
  m_raw(*)=ave_mon/m_raw(*)  ;normalisation scale factor for single file sum
  ;    
  ;normalise y-axes to monitor
  for j=0,mac_count-1 do begin
     y_det(j,*)=y_raw(j,*);*m_raw(*)
  endfor
  ; 
end

pro larger_rebin,x_new,y_merged,e_merged,user_step_size
  ;
  ;=============================================================================
  ;THIS PRO DOES A FINAL REBIN OF THE REBINED DATA FOR BINNING STEP SIZES >0.001
  ;=============================================================================
  ;
  catch,error_status
  if error_status ne 0 then begin
     print,"***-FAILED IN larger_rebin"
     catch,/cancel
     return
  endif
  ;
  ;-----------------------------------------------
  ;CREATE NEW x-scale AND CALCULATE SLOPE FUNCTION
  ;-----------------------------------------------
  ;
  x_min=x_new(0)-user_step_size*0.5
  x_max=x_new(n_elements(x_new)-1)+user_step_size
  n_new_steps=long((x_max-x_min)/user_step_size)
  xnew=indgen(n_new_steps,/float)*user_step_size+x_min
  slope=(n_elements(xnew)-1)/(xnew(n_elements(xnew)-1)-xnew(0))
  intercept=slope*xnew(0)*(-1.0)
  ynew=xnew*0.0
  enew=ynew
  ;e_merged=e_merged*e_merged
  ;
  ;---------------------------------------
  ;start and stop positions for rebin loop
  ;---------------------------------------
  ;
  sum_start=0L
  sum_stop=n_elements(x_new)-2
  ;
  ;-----------------
  ;do the rebin loop
  ;-----------------
  ;
  for k=sum_start,sum_stop do begin
        ;
        ;-----------------------------
        ;find position in master array
        ;-----------------------------
        ;
        x_calc=long(slope*(x_new(k))+intercept)
        if x_calc ge n_elements(xnew) then x_calc=n_elements(xnew)-1
        x_calc2=long(slope*(xnew(x_calc)+1.0)+intercept)  
        if x_calc2 ge n_elements(xnew) then x_calc2=n_elements(xnew)-1
        xdiff=where(xnew(x_calc:x_calc2) lt x_new(k),xcount)
        xpos=x_calc+max(xdiff);xcount;-1
        ;
        ;-----------------------
        ;intensity bin-splitting
        ;-----------------------
        a=1.0
        b=0.0
        xpos2=xpos+1
        if xpos2 ge n_new_steps then xpos2=xpos
        if x_new(k+1) gt xnew(xpos2) then begin
           a=(xnew(xpos2)-x_new(k))/(x_new(k+1)-x_new(k))
           b=1.0-a
        endif
        ;
        ;-----------------------------------------
        ;add current data point in to the new bins
        ;-----------------------------------------
        ;
        ynew(xpos)=ynew(xpos)+y_merged(k)*a
        ynew(xpos2)=ynew(xpos2)+y_merged(k)*b
        ;
        enew(xpos)=enew(xpos)+(e_merged(k)*a)*(e_merged(k)*a)
        enew(xpos2)=enew(xpos2)+(e_merged(k)*b)*(e_merged(k)*b)
;        enew(xpos)=enew(xpos)+(e_merged(k)*a)
;        enew(xpos2)=enew(xpos2)+(e_merged(k)*b)
  endfor
  x_new=xnew
  y_merged=ynew
  e_merged=sqrt(enew)
end

pro go_for_it_macs,mac_columns,x_raw,y_raw,m_raw,step_sizes,ave_mon,y_norm,sum_option,$
              n_x,raw_step_size,err_y,skip_n_pts,y_sum,$
              m_sum,e_sum,e_y_sum,e_m_sum,x_new,n_new_steps,e_y,e_m
  ;
  ;=================================================================================================
  ;THIS PRO REBINS THE tth CORRECTED x-y DATA FOR EACH CRYSTAL INTO SEPARATE ARRAYS FOR EACH MAC ARM
  ;=================================================================================================
  ;
  catch,error_status
  if error_status ne 0 then begin
     print,"***-FAILED IN go_for_it_macs"
     catch,/cancel
     return
  endif
  ;
  mac_count=n_elements(mac_columns) ;number of crystals!!
  ;
  ;---------------------------------------------------
  ;calculate slope function of new rebin 2theta array
  ;---------------------------------------------------
  ;
  x_min=x_new(0)
  x_max=x_new(n_elements(x_new)-1)
  slope=(n_elements(x_new)-1)/(x_new(n_elements(x_new)-1)-x_new(0))
  intercept=slope*x_new(0)*(-1.0)
  ;
  ;---------------------------------------
  ;start and stop positions for rebin loop
  ;---------------------------------------
  ;
  sum_start=0L
  sum_stop=n_elements(x_raw(0,*))-2
  ;
  ;-------------------------------------------
  ;set up indices for crystal-arm relationship
  ;-------------------------------------------
  ; 
  n=[0,9,18,27,36]     ;first crystal positions for each MAC
  m=[8,17,26,35,44]    ;last crystal positions for each MAC
  arm=intarr(45)       ;array indexed by crystal number giving which arm crystal is on
  i=0
  for j=1,5 do begin
    for k=1,9 do begin
      arm(i)=j-1
      i=i+1
    endfor
  endfor
  ;
  ;-----------------
  ;do the rebin loop
  ;-----------------
  ;
  for k=sum_start+skip_n_pts,sum_stop-skip_n_pts do begin
    for j=0,mac_count-1 do begin
       case 1 of 
         ;----------------------------------------------------------
         ;only sum those regions that are in desired summation range 
         ;----------------------------------------------------------
         (x_raw(j,k) ge x_min) AND $
         (x_raw(j,k) le x_max) AND $
         (x_raw(j,k) ge x_raw(m(arm(j)),0)) AND $
         (x_raw(j,k) le x_raw(n(arm(j)),sum_stop)): $
                                    begin
                                     ;
                                     ;-----------------------------
                                     ;find position in master array
                                     ;-----------------------------
                                     ;
                                     x_calc=long(slope*(x_raw(j,k))+intercept)
                                     if x_calc ge n_elements(x_new) then x_calc=n_elements(x_new)-1
                                     x_calc2=long(slope*(x_new(x_calc)+1.0)+intercept)  
                                     if x_calc2 ge n_elements(x_new) then x_calc2=n_elements(x_new)-1
                                     xdiff=where(x_new(x_calc-1:x_calc2+1) lt x_raw(j,k),xcount)
                                     xpos=x_calc+max(xdiff);xcount;-1
                                     ;
                                     ;-----------------------
                                     ;intensity bin-splitting
                                     ;-----------------------
                                     a=1.0
                                     b=0.0
                                     xpos2=xpos+1
                                     if xpos2 ge n_new_steps then xpos2=xpos
                                     if x_raw(j,k+1) gt x_new(xpos2) then begin
                                        a=(x_new(xpos2)-x_raw(j,k))/(x_raw(j,k+1)-x_raw(j,k))
                                        b=1.0-a
                                     endif
                                     ;
                                     ;-----------------------------------------
                                     ;add current data point in to the new bins
                                     ;-----------------------------------------
                                     ;
                                     y_sum(arm(j),xpos)=y_sum(arm(j),xpos)+y_raw(j,k)*a
                                     y_sum(arm(j),xpos2)=y_sum(arm(j),xpos2)+y_raw(j,k)*b
                                     ;
                                     m_sum(arm(j),xpos)=m_sum(arm(j),xpos)+m_raw(j,k)*a
                                     m_sum(arm(j),xpos2)=m_sum(arm(j),xpos2)+m_raw(j,k)*b
                                     ;
                                     e_y_sum(arm(j),xpos)=e_y_sum(arm(j),xpos)+(e_y(j,k)*a)*(e_y(j,k)*a)
                                     e_y_sum(arm(j),xpos2)=e_y_sum(arm(j),xpos2)+(e_y(j,k)*b)*(e_y(j,k)*b)
                                     ;
                                     e_m_sum(arm(j),xpos)=e_m_sum(arm(j),xpos)+(e_m(k)*a)*(e_m(k)*a)
                                     e_m_sum(arm(j),xpos2)=e_m_sum(arm(j),xpos2)+(e_m(k)*b)*(e_m(k)*b)
                                     ;
                                     n_x(arm,xpos)=n_x(arm,xpos)+1.0*a
                                     n_x(arm,xpos2)=n_x(arm,xpos2)+1.0*b   
                                   end
           else:;continue
        endcase
    endfor
  endfor
end

pro read_a_file,file_number,cv_tth,cv_macs,cv_n_header,cv_Io,cv_Ie,x_raw,y_raw,y_det,m_raw,e_y,e_m
  ;
  ;==================================================
  ;THIS PRO READS IN RAW DATA FROM A SINGLE DATA FILE
  ;==================================================
  ;
  catch,error_status
  if error_status ne 0 then begin
     print,"***-FAILED IN read_a_file"
     catch,/cancel
     return
  endif
  ;
  mac_count=n_elements(cv_macs) ;number of mac detectors (=45 for all)
  ;
  ;---------------------------------------------------------------------------------
  ;OBTAIN A STRUCTURE WITH ONE TAG FIELD COMPRISING AN ARRAY EG (n_columns,n_points)
  ;---------------------------------------------------------------------------------
  ;
  in_data=read_ascii_spt(file_number,count=i_lines,data_start=cv_n_header,delimiter=" ",verbose=1)
  ;
  n_lines=n_elements(in_data.(0)(0,*))-1  ;EOF gives a NaN coversion for last line of data file
  ;
  ;--------------------------------------------
  ;EXTRACT 2THETA DATA & CLEANSE OF DODGY POINTS
  ;--------------------------------------------
  temp_x=in_data.(0)(cv_tth,0:i_lines-2)
  tth_error=in_data.(0)(50,0:i_lines-2)
  ;
;  for q=n_elements(temp_x)-2,0,-1 do begin
;    ;if temp_x(q) ge temp_x(q+1) then temp_x(q)=temp_x(q+1)-0.00075  ;actual value to subtract really depends on collection sampling rate
;    dif=abs(temp_x(q)-temp_x(q+1))
;    if ((dif ge 0.01) OR (dif eq 0.0)) then begin
;       print,dif
;       temp_x(q)=temp_x(q+1)-0.0008 ; best hope that the first two points aren't dodgey!!!!
;       print, "fixed dodgy point...",temp_x(q),temp_x(q+1)
;    endif
;  endfor
  ;
  e_tth=where(abs(tth_error) gt 0.01,tth_err_count)
  print,"fixing "+string(tth_err_count)+" bad tth values"
  if tth_err_count gt 0 then begin
      temp_x(e_tth)=temp_x(e_tth)-tth_error(e_tth)
  endif
  ;
  ;----------------------------------------------------
  ;PREPARE 2THETA, DATA, MONITOR AND ERROR INPUT ARRAYS
  ;----------------------------------------------------
  ;
  x_raw=dblarr(mac_count,n_elements(temp_x))
  y_raw=fltarr(mac_count,n_elements(temp_x))
  y_det=x_raw
  e_y=x_raw
  m_raw=fltarr(mac_count,n_elements(temp_x))
  e_m=m_raw
  ; 
  ;-----------------------------------
  ;EXTRACT MONITOR COLUMN - JUST DO Io
  ;-----------------------------------
  temp_m=in_data.(0)(cv_Io,0:i_lines-2)
  ;
  ;--------------------------------------------------------------------------------------
  ;NOW SET ALL 2THETA TO SAME UNCORRECTED VALUES AND EXTRACT ALL CRYSTAL & MONITOR COUNTS
  ;--------------------------------------------------------------------------------------
  ;
  ;a small offset is added to both data & monitor to stop div by 0 when calculating 
  ;errors, but if offset is large relative to counts (eg in 120min scans where
  ;counts ~1, then this could introduce a higher background level making fits look
  ;unrealistically good - so make it very small (unlike ESRF!)
  for j=0,mac_count-1 do begin
     x_raw(j,*)=temp_x(0,*)
     temp_y=in_data.(0)(cv_macs(j),0:i_lines-2)
     y_raw(j,*)=temp_y(0,*)+0.0001  
     e_y(j,*)=sqrt(y_raw(j,*))
     m_raw(j,*)=temp_m(0,*)+0.0001
     e_m(j,*)=sqrt(m_raw(j,*))
     ;
  endfor
  ;
end

pro calculate_errors_and_normalize,e_sum,e_m_sum,m_sum,y_sum,e_y_sum,ave_mon
  ;
  ;=================================================================================
  ;THIS PRO DOES THE FINAL ERROR CALCULATIONS & NORMALIZATION ONCE REBIN IS COMPLETE
  ;=================================================================================
  ;
  catch,error_status
  if error_status ne 0 then begin
     print,"***-FAILED IN calculate_errors_and_normalize"
     catch,/cancel
     return
  endif
  ;
  for w=0,4 do begin
    e_sum(w,*)=e_sum(w,*)+e_m_sum(w,*)/(m_sum(w,*)*m_sum(w,*))
    e_sum(w,*)=e_sum(w,*)+e_y_sum(w,*)/(y_sum(w,*)*y_sum(w,*))
    ;
    e_sum(w,*)=sqrt(e_sum(w,*))
    ;
    y_sum(w,*)=y_sum(w,*)/m_sum(w,*)
    ;
    e_sum(w,*)=e_sum(w,*)*y_sum(w,*)
    ;
    y_sum(w,*)=y_sum(w,*)*ave_mon
    e_sum(w,*)=e_sum(w,*)*ave_mon
    ;
    ;remove the first & last non-zero spike points
    index=where(e_sum(w,*) gt 0.0,count)
    e_sum(w,index(0:10))=0.0
    e_sum(w,index(count-10:count-1))=0.0
    y_sum(w,index(0:10))=0.0
    y_sum(w,index(count-10:count-1))=0.0
  endfor
end

pro merge_macs,x,y,merged1,err,merged2
  ;
  ;==========================================================================
  ;THIS PRO MERGES THE FIVE REBINNED & CORRECTED MAC ARMS INTO A SINGLE TRACE
  ;==========================================================================
  ;
  catch,error_status
  if error_status ne 0 then begin
     print,"***-FAILED IN merge_macs"
     catch,/cancel
     return
  endif
  ;
  merged1=x*0.0
  merged2=x*0.0
  ;
  ;merge in to single y and error arrays
  ;
  for i=0L,n_elements(x)-1 do begin
     dy=y(0:4,i)
     de=err(0:4,i)
     de=de*de
     index=where(dy gt 0.0,count)
     case 1 of
       count ge 1:begin
                    merged1(i)=total(dy)/count
                    merged2(i)=sqrt(total(de))/count  
                  end
       else:;continue
     endcase
  endfor
end


pro correct_per_mac,x_new,y,err
  ;
  ;==========================================================================
  ;THIS PRO CORRECTS THE REBINNED PER MAC SIGNALS AND THEIR CALCULATED ERRORS
  ;==========================================================================
  ;
  catch,error_status
  if error_status ne 0 then begin
     print,"***-FAILED IN correct_per_mac"
     catch,/cancel
     return
  endif
  ;
  index4=where(y(4,*) gt 0.0)
  index3=where(y(3,*) gt 0.0,count3)
  index2=where(y(2,*) gt 0.0,count2)
  index1=where(y(1,*) gt 0.0,count1)
  index0=where(y(0,*) gt 0.0,count0)
  ;
  ;=============================================================================
  ;SUCCESSIVELY ADJUST MAC4 TO MAC5, MAC3 TO MAC4, MAC2 TO MAC3 AND MAC1 TO MAC2
  ;=============================================================================
  ;
  ib=total(y(4,index4(0):index4(0)+1000))
  ia=total(y(3,index3(count3-1001):index3(count3-1)))
  jb=total(err(4,index4(0):index4(0)+1000))                ;<--- Do unto errors what
  ja=total(err(3,index3(count3-1001):index3(count3-1)))    ;<--- is done unto counts
  e=ib/ia
  ee=jb/ja
  y(3,*)=y(3,*)*e
  err(3,*)=err(3,*)*ee
  ;
  ib=total(y(3,index3(0):index3(0)+1000))
  ia=total(y(2,index2(count2-1001):index2(count2-1)))
  jb=total(err(3,index3(0):index3(0)+1000))
  ja=total(err(2,index2(count2-1001):index2(count2-1)))
  e=ib/ia
  ee=jb/ja
  e=ib/ia
  y(2,*)=y(2,*)*e
  err(2,*)=err(2,*)*ee
  ;
  ib=total(y(2,index2(0):index2(0)+1000))
  ia=total(y(1,index1(count1-1001):index1(count1-1)))
  jb=total(err(2,index2(0):index2(0)+1000))
  ja=total(err(1,index1(count1-1001):index1(count1-1)))
  e=ib/ia
  ee=jb/ja
  e=ib/ia
  y(1,*)=y(1,*)*e
  err(1,*)=err(1,*)*ee
  ;
  ib=total(y(1,index1(0):index1(0)+1000))
  ia=total(y(0,index0(count0-1001):index0(count0-1)))
  jb=total(err(1,index1(0):index1(0)+1000))
  ja=total(err(0,index0(count0-1001):index0(count0-1)))
  e=ib/ia
  ee=jb/ja
  e=ib/ia
  y(0,*)=y(0,*)*e
  err(0,*)=err(0,*)*ee
  ;
end

pro calculate_ave_mon, m_sum,ave_mon
  ;
  ;================================================================
  ;THIS PRO CALCULATES THE AVERAGE MONITOR FROM THE REBINED MONITOR
  ;================================================================
  ;
  catch,error_status
  if error_status ne 0 then begin
     print,"***-FAILED IN calculate_ave_mon"
     catch,/cancel
     return
  endif
  ;
  for w=0,4 do begin
     ;only use those entries in m_sum where monitor counts are present 
     m_9_or_more=where(m_sum(w,*) ge 0.0)
     ave_m=moment(m_sum(w,m_9_or_more))
     ave_mon=ave_mon+ave_m(0)
  endfor
  ;
end

pro rebin_it,path,out_path,file_list,user_step_size,argument,user_comment,offsets_path
  ;
  catch,error_status
  if error_status ne 0 then begin
     print,"***-FAILED IN rebin_it"
     catch,/cancel
     return
  endif
  ;
  ;-----------------
  ;GENERAL VARIABLES
  ;-----------------
  ;
  months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  days_Per_month=[31,28,31,30,31,30,31,31,30,31,30,31]
  leap_years=[8,12,16,20,24,28]                            ;covers next 20 years!!!! <--searching for offsets by file creation date is no longer used
  n=[0,9,18,27,36]                                         ;first crystal positions for each MAC
  m=[8,17,26,35,44]                                        ;last crystal positions for each MAC
  crystal_offsets=dblarr(45)                               ;holds the crystal+arm offsets for all 1..45 crystals
  mac_arm_offsets=dblarr(5)*0.0                            ;holds the offsets for each MAC arm
  mac_calibration_path="u:\progs\dev\"                     ;holds the path to the mac offsets calibration files (2-off)
  arm_file="mac_arm_calibration_"                          ;arm calibration file name - will have year added below, eg "mac_calibration_file_2009.dat"
  crystal_file="mac_crystal_offsets_"                      ;same but for crystal offsets
  offset_files_extention=".txt"                            ;extension for offsets calibration files
  year=""                                                  ;will hold 4-digit year string for appending to calibration file names
  file_date=[0,0,0]                                        ;will hold date of creation in dd,mm,yy format of data file to be rebinned
  skip_n_pts=20                                            ;number of data points to ignore at start and end of each detector channel
  cv_n_header=18                                           ;will hold the number of header lines to skip
  header=strarr(cv_n_header+100)                           ;will hold data file header data hopefully large enough for future, is cut to size later on
  cv_tth=1                                                 ;tth data file column number
  cv_Io=49                                                 ;monitor columns number
  cv_Ie=50                                                 ;other monitor column number
  ;
  cv_macs=[3,4,5,6,7,8,9,10,11,$
          12,13,14,15,16,17,18,19,20,$
          21,22,23,24,25,26,27,28,29,$
          30,31,32,34,35,36,37,38,39,$
          40,41,42,43,44,45,46,47,48]                      ;column numbers of mac_nm
  ;
  cv_col_headers=["tth","mac11","mac12","mac13","mac14","mac15","mac16","mac17","mac18","mac19",$
                        "mac21","mac22","mac23","mac24","mac25","mac26","mac27","mac28","mac29",$
                        "mac31","mac32","mac33","mac34","mac35","mac36","mac37","mac38","mac39",$
                        "mac41","mac42","mac43","mac44","mac45","mac46","mac47","mac48","mac49",$
                        "mac51","mac52","mac53","mac54","mac55","mac56","mac57","mac58","mac59","Io","Ie"]  ;column headers in data file
  ;
  cv_col_index=intarr(n_elements(cv_col_headers))          ;list of column headers extracted from data file
  det1_columns=3                                           ;
  end_string="####"                                        ;string that denotes end of mac calibration files header
  end_header="&END"                                        ;string that denotes end of data file header - only supports those files with a header
  y_det=0.0                                                ;will become and array of detector intensities
  e_chan=fltarr(45)                                        ;channel efficiencies
  e_arm=fltarr(5)                                          ;arm efficiencies
  e_chan(*)=1.0
  e_arm(*)=1.0
  ave_mon=0.0                                              ;will hold average monitor counts
  raw_step_size=0.001                                      ;nominal sampling rate (actually ~0.00075) used only for %increase in scale factor larger rebin step has
  Int_crystal_5=fltarr(5)                                  ;will hold integrated intensity of 5th crystal in each arm
  y_merged=0.0                                             ;will become an array holding merged Y-axis data from the 5 arms
  e_merged=0.0                                             ;same as merged1 but for the error signal
  summed_file_name=""                                      ;will hold name of summation rebin file
  step_size=0.001                                          ;auto rebin to this step size any/much larger and matching up the mac arms becomes unstable
  ;
  ;assume that all files to be summed have same structure and interrogate 1st file in list for structure
  ;
  file_number=file_list(0)
  ;print,file_number
  ;
  ;-------------------------------------------------------------------------------------------------
  ;THIS SECTION MATCHES DATA FILE RUN NUMBER WITH OFFSET DATE AND READS IN APPROPRIATE OFFSET VALUES
  ;-------------------------------------------------------------------------------------------------
  ;
  ;obtain file creation date from system
  ;
;  file_data=file_info(path+file_number+".dat")
;  creation_time=file_data.ctime
  ;
  ;convert to something humans can comprehend
;  a=systime(0,creation_time)
;  c_time=strsplit(a,/extract)
  ;
;  year=strcompress(c_time(4),/remove_all)
  ;
;  file_date(2)=long(c_time(4))-2000     ;yy
;  file_date(0)=long(c_time(2))          ;dd
;  index=where(c_time(1) eq months(*))
;  file_date(1)=index+1                  ;mm
  ;
  ;check number of days in FEB for leap year
;  index2=where(file_date(2) eq leap_years(*),count)
;  if count ge 1 then days_per_month(1)=29
  ;
  ;convert dd mm to fractional mm.%dd
;  fractional_file_date=float(file_date(0))/float(days_per_month(index))+float(file_date(1))
  ;
  ;get arm offsets
  ;
  case argument of
    "-o":begin
           ;nominal values for finding real offsets from rebinned mac arms
           mac_arm_offsets(0)=0.0
           mac_arm_offsets(1)=30.0
           mac_arm_offsets(2)=60.0
           mac_arm_offsets(3)=90.0
           mac_arm_offsets(4)=120.0
           argument="-m"
         end
    else:begin
           ;
           openr,1,offsets_path+"mac_arm_calibration_2009.txt"
           line=""
           ;
           ;read header lines until "####" is found
           while line ne end_string do begin
             readf,1,line
             ;print, line
           endwhile
           ;
           found=0
           while found ne 1 do begin
             ;read date line
             readf,1,line
             ;
             ;extract date - no longer used
             ;entry_date=long(strsplit(line,/extract))
             ;
             ;read comment line
             readf,1,line
             entry=strsplit(line,/extract)
             ;
             ;read offset values
             for i=0,4 do begin
               readf,1,line
               c_time=strsplit(line,/extract)
               mac_arm_offsets(i)=double(c_time(2))
             endfor
             ;
             ;read spacer line
             readf,1,line
             ;
             ;check entry date with file date - no longer used
             ;convert entry date to fractional entry date
             ;fractional_entry_date=float(entry_date(0))/float(days_per_month(entry_date(1)-1))+float(entry_date(1))
             ;if fractional_file_date ge fractional_entry_date then found=1
             ;
             ;check entry run num with file data
             if long(file_number) ge long(entry(5)) then found=1
             print, entry(5)
           endwhile
           ;print, entry_date
           ;
           close,1
         end
  endcase
  ;
  ;get crystal offsets
  ;  
  openr,1,offsets_path+"mac_crystal_offsets_2009.txt"
  line=""
  ;
  ;read header lines until "####" is found
  while line ne end_string do begin
     readf,1,line
     ;print, line
  endwhile
  for i=0,44 do begin
     readf,1,line
     c_time=strsplit(line,/extract)
     crystal_offsets(i)=double(c_time(2))
  endfor
  close, 1
  ;
  ;combine arm & crystal offsets
  ;
  for i=0,4 do begin
     crystal_offsets(n(i):m(i))=crystal_offsets(n(i):m(i))+mac_arm_offsets(i)
  endfor
  print,"total offsets"
  print, crystal_offsets
  ;print,"arm only offsets"
  ;print,mac_arm_offsets
  ;
  ;-------------------------------------------------------------------------
  ;THIS SECTION INTERROGATES THE DATA FILE TO FIND THE CVSCAN FILE STRUCTURE
  ;-------------------------------------------------------------------------
  ;
  ;assume that all files to be summed have same structure
  ;
  line=""
  cv_n_header=0
  openr,1,path+file_number+".dat"
  ;
  ;read header "info"
  while line ne end_header do begin
     readf,1,line
     ;line=strcompress(line,/remove_all)
     header(cv_n_header)=line
     cv_n_header=cv_n_header+1
  endwhile 
  header=header(0:cv_n_header-1)
  ;
  ;read columns header line
  readf,1,line
  cv_cols=strcompress(strsplit(line,/extract),/remove_all)
  cv_n_header=cv_n_header+1
  ;print,line
  for i=0,n_elements(cv_col_headers)-1 do begin
     index=where(cv_col_headers(i) eq cv_cols(*))
     case 1 of
       i eq 0:cv_tth=index
       (i ge 1) AND (i le 45):cv_macs(i-1)=index
       i eq 46:cv_Io=index
       i eq 47:cv_Ie=index
       else:;should never get here
     endcase
     ;print, index
  endfor
  close,1
  ;
  ;---------------------------------------------------------------------------
  ;THIS SECTION CONTROLS THE REBIN PROCESS BASED ON THE COMMAND LINE ARGUMENTS
  ;---------------------------------------------------------------------------
  ;
  case 1 of
     ((argument eq "-a") or $
      (argument eq "-A") or $
      (argument eq "")   or $
      (argument eq "-b") or $
      (argument eq "-B") or $
      (argument eq "-m") or $
     (argument eq "-o")):begin
                          ;mac rebin
                            n_files=n_elements(file_list)
                            ;
                            ;read in data
                            for i=0,n_files-1 do begin
                               print,"processing file: ",string(i+1) 
                               ;
                               ;-----------------
                               ;READ IN DATA FILE
                               ;-----------------
                               ;
                               read_a_file,path+file_list(i)+".dat",cv_tth,cv_macs,cv_n_header,cv_Io,cv_Ie,x_rw,y_rw,y_det,m_rw,e_y,e_m
                               ;
                               ;---------------------------------
                               ;CORRECT tth's FOR CRYSTAL OFFSETS
                               ;---------------------------------
                               ;
                               for j=0,44 do begin
                                   x_rw(j,*)=x_rw(j,*)+crystal_offsets(j)
                               endfor
                               ;
                               ;
                               case 1 of
                                  ((i eq 0) or $
                                  (argument eq "-b") or $
                                  (argument eq "-B")): $
                                    begin
                                      ;
                                      ;----------------------------------------------
                                      ;SET UP NEW tth ARRAY & RANGE FOR 1st FILE ONLY
                                      ;----------------------------------------------
                                      ;
                                      x_min=min(x_rw(*,*))-0.5*step_size
                                      x_max=max(x_rw(*,*))+0.5*step_size
                                      ;
                                      ;create new x-scale and y_sum, m_sum & e_summ arrays
                                      ;
                                      n_new_steps=long((x_max-x_min)/step_size)
                                      x_new=indgen(n_new_steps,/double)*step_size+x_min
                                      ;
                                      slope=(n_elements(x_new)-1)/(x_new(n_elements(x_new)-1)-x_new(0))
                                      intercept=slope*x_new(0)*(-1.0)
                                      ;
                                      ;------------------------------------------------------------------
                                      ;ALSO SET UP y-axis, MONITOR AND ERROR ARRAYS FOR EACH MAC ARM HERE
                                      ;------------------------------------------------------------------
                                      ;
                                      y_sum=fltarr(5,n_new_steps)  
                                      ;
                                      m_sum=fltarr(5,n_new_steps)  
                                      ;
                                      n_x=fltarr(5,n_new_steps)    
                                      ;
                                      e_sum=fltarr(5,n_new_steps)
                                      e_y_sum=fltarr(5,n_new_steps)
                                      e_m_sum=fltarr(5,n_new_steps)
                                      ;
                                      ave_mon=0
                                      ;
                                    end
                                  else:;continue
                               endcase
                               ;
                               ;--------------------------------
                               ;REBIN EACH FILE IN THE FILE LIST 
                               ;--------------------------------
                               ;
                               ;-----------------------------------------------
                               ;REBIN PER 5 ARMS, ONLY WHERE 9 CRYSTALS OVERLAP
                               ;-----------------------------------------------
                               go_for_it_macs,cv_macs,x_rw,y_rw,m_rw,step_size,ave_mon,y_norm,sum_option,n_x,raw_step_size,err_y,skip_n_pts,$
                                              y_sum,m_sum,e_sum,e_y_sum,e_m_sum,x_new,n_new_steps,e_y,e_m
                               ;
                               ;-------------------------------------------------------------
                               ;NEXT TEST WHICH SORT OF REBIN IS REQUIRED AND ACT ACCORDINGLY
                               ;------------------------------------------------------------- 
                               ;
                               case 1 of
                                 ((argument eq "-a") OR $
                                  (argument eq "-A")):begin
                                                        ;build output file name
                                                        summed_file_name=summed_file_name+file_list(i)+"_"
                                                      end
                                   (argument eq "-m" ): $
                                           begin
                                             ;print, "m or o"
                                             ;
                                             ;-----------------------------------------------------------------
                                             ;CALCULATE AVERAGE MONITOR ONLY WHERE ~9 CRYSTALS ARE CONTRIBUTING
                                             ;-----------------------------------------------------------------
                                             ;
                                             calculate_ave_mon,m_sum,ave_mon
                                             ;print, "average monitor ",ave_mon
                                             ; 
                                             ;------------------------------------------
                                             ;CALCULATE TOTAL ERROR SIGNALS FOR EACH ARM
                                             ;------------------------------------------                                    
                                             calculate_errors_and_normalize,e_sum,e_m_sum,m_sum,y_sum,e_y_sum,ave_mon
                                             ;
                                             ;--------------------------------------------
                                             ;MATCH UP INTENSITY LEVELS FOR THE 5 MAC ARMS
                                             ;--------------------------------------------
                                             correct_per_mac,x_new,y_sum,e_sum
                                             ;
                                             ;--------------------------------------------------
                                             ;REMOVE infty' AND -NaN's FROM INTENSITIES & ERRORS
                                             ;--------------------------------------------------
                                             for j=0,4 do begin
                                                b=where(~finite(y_sum(j,*)), bcount)
                                                if bcount ge 1 then y_sum(j,b)=0.0
                                                ;
                                                b=where(~finite(e_sum(j,*)), bcount)
                                                if bcount ge 1 then e_sum(j,b)=0.0
                                             endfor
                                             ;
                                             ;---------------------------------------
                                             ;OUTPUT MAC ARM DATA TO 5 SEPARATE FILES
                                             ;---------------------------------------
                                             output_rebinned_macs_files,file_list(i),out_path,x_new,y_sum,e_sum,user_comment
                                           end
                                 ((argument eq "-b") OR $
                                  (argument eq "-B")):$
                                                begin
                                                  ;
                                                  ;=================================================================
                                                  ;CALCULATE AVERAGE MONITOR ONLY WHERE ~9 CRYSTALS ARE CONTRIBUTING
                                                  ;=================================================================
                                                  ;
                                                  calculate_ave_mon, m_sum,ave_mon
                                                  ;print, "average monitor ",ave_mon
                                                  ; 
                                                  ;==========================================
                                                  ;CALCULATE TOTAL ERROR SIGNALS FOR EACH ARM
                                                  ;==========================================                                    
                                                  calculate_errors_and_normalize,e_sum,e_m_sum,m_sum,y_sum,e_y_sum,ave_mon
                                                  ;
                                                  ;============================================
                                                  ;MATCH UP INTENSITY LEVELS FOR THE 5 MAC ARMS
                                                  ;============================================
                                                  correct_per_mac,x_new,y_sum,e_sum
                                                  ;
                                                  ;==================================================
                                                  ;REMOVE infty' AND -NaN's FROM INTENSITIES & ERRORS
                                                  ;==================================================
                                                  ;
                                                  for j=0,4 do begin
                                                     b=where(~finite(y_sum(j,*)), bcount)
                                                     if bcount ge 1 then y_sum(j,b)=0.0
                                                     ;
                                                     b=where(~finite(e_sum(j,*)), bcount)
                                                     if bcount ge 1 then e_sum(j,b)=0.0
                                                  endfor
                                                  ;
                                                  ;=======================
                                                  ;MERGE THE 5 ARMS INTO 1
                                                  ;=======================
                                                  ;
                                                  merge_macs,x_new,y_sum,y_merged,e_sum,e_merged
                                                  ;
                                                  ;===========================================================
                                                  ;IF USER SPECIFIED A LARGER REBIN SIZE NOW REBIN MERGED DATA
                                                  ;===========================================================
                                                  ;
                                                  case 1 of
                                                    (user_step_size gt step_size):begin
                                                                                    larger_rebin,x_new,y_merged,e_merged,user_step_size
                                                                                  end
                                                    else:;continue
                                                  endcase
                                                  ;
                                                  ;plot it out for all to see - THIS LOT WILL GO
                                                  ;
                                              ;   window,1,title="SUMMED DATA"
                                                  ;trim off the two points either end
                                              ;   x=x_new(1:n_elements(x_new)-2) 
                                              ;   y=y_merged(1:n_elements(x_new)-2)
                                              ;   err_y=e_merged(1:n_elements(x_new)-2)
                                              ;   n_x=n_x(1:n_elements(x_new)-2)
                                              ;   plot,x,y;,xrange=[xmin,xmax],yrange=[ymin,ymax],xstyle=1
                                              ;   window,2
                                              ;   plot,x,e_merged(1:n_elements(x_new)-2)
                                              ;
                                              ;   window,4,title="points per bin"
                                                ; plot,x,n_x(0,*)
                                                ; oplot,x,n_x(1,*)
                                                ; oplot,x,n_x(2,*)
                                                ; oplot,x,n_x(3,*)
                                                ; oplot,x,n_x(4,*)
                                              ;
                                              ;   window,5,title="binned monitor"
                                              ;   plot, x,m_sum(1:n_elements(x_new)-2)  
                                              ;
                                              ;
                                                  ;===========================
                                                  ;OUTPUT REBINED DATA TO FILE
                                                  ;===========================
                                                  ;
                                                  summed_file_name=file_list(i)+"_"
                                                  output_rebined_file,summed_file_name,out_path,header,x_new,y_merged,e_merged,user_comment,$
                                                                      x_rw(m(0),0),x_rw(n(4),n_elements(x_rw(0,*))-1),argument
                                                  ;
                                                end 
                                   else:;continue                                      
                               endcase
                            endfor
                            case 1 of
                              ((argument eq "-a") OR $
                               (argument eq "-A")):$
                                   begin
                                     ;
                                     ;==========================
                                     ;MULTI-FILE SUMMATION REBIN
                                     ;==========================
                                     ;
                                     ;=================================================================
                                     ;CALCULATE AVERAGE MONITOR ONLY WHERE ~9 CRYSTALS ARE CONTRIBUTING
                                     ;=================================================================
                                     ;
                                     calculate_ave_mon, m_sum,ave_mon
                                     ;print, "average monitor ",ave_mon
                                     ; 
                                     ;==========================================
                                     ;CALCULATE TOTAL ERROR SIGNALS FOR EACH ARM
                                     ;==========================================                                    
                                     calculate_errors_and_normalize,e_sum,e_m_sum,m_sum,y_sum,e_y_sum,ave_mon
                                     ;
                                     ;============================================
                                     ;MATCH UP INTENSITY LEVELS FOR THE 5 MAC ARMS
                                     ;============================================
                                     correct_per_mac,x_new,y_sum,e_sum
                                     ;
                                     ;==================================================
                                     ;REMOVE infty' AND -NaN's FROM INTENSITIES & ERRORS
                                     ;==================================================
                                     for j=0,4 do begin
                                        b=where(~finite(y_sum(j,*)), bcount)
                                        if bcount ge 1 then y_sum(j,b)=0.0
                                        ;
                                        b=where(~finite(e_sum(j,*)), bcount)
                                        if bcount ge 1 then e_sum(j,b)=0.0
                                     endfor
                                     ;
                                     ;=======================
                                     ;MERGE THE 5 ARMS INTO 1
                                     ;=======================
                                     merge_macs,x_new,y_sum,y_merged,e_sum,e_merged
                                     ;
                                     ;=====================================
                                     ;REBIN TO LARGER STEP SIZE IF REQUIRED
                                     ;=====================================
                                     ;
                                     case 1 of
                                       (user_step_size gt step_size):begin
                                                                       larger_rebin,x_new,y_merged,e_merged,user_step_size
                                                                     end
                                       else:;continue
                                     endcase
                                     ;
                                     ;===========================
                                     ;OUTPUT REBINED DATA TO FILE
                                     ;===========================
                                     ;
                                     output_rebined_file,summed_file_name,out_path,header,x_new,y_merged,e_merged,user_comment,$
                                                         x_rw(m(0),0),x_rw(n(4),n_elements(x_rw(0,*))-1),argument
                                     ;
                                   end
                                else:;continue
                            endcase
                            ;
                        end
     (argument eq "-d"):begin
                          ;
                          ;==========================================================
                          ;DETECTOR REBIN OUTPUT INDIVIDUAL DETECTOR/CRYSTAL PATTERNS
                          ;==========================================================
                          ;
                          ;output file names will be file_numer_det_n.dat where n=detector/channel number
                          ;only does batch not summing so far
                          ;
                          for i=0,n_elements(file_list)-1 do begin
                             read_a_file,path+file_list(i)+".dat",cv_tth,cv_macs,cv_n_header,cv_Io,cv_Ie,x_raw,y_raw,y_det,m_raw,e_y,e_m
                             go_for_it_dectector,cv_macs,crystal_offsets,x_raw,y_raw,y_det,m_raw,ave_mon
                             output_detector_chanels,x_raw,y_det,out_path,file_list(i),ave_mon
                          endfor
                        end
  endcase
end

pro rebin_idl,arg1_string,arg2_string,arg3_string,arg4_string,arg5_string,return_string
  ;
  catch,error_status
  if error_status ne 0 then begin
     rebin_idl
     catch,/cancel
     return
  endif
  ;
  ;supported format: rebin_idl, <switch>, <space_separated_file_list>, <path_to_file>, <user_step_size>, <user_comment>, <return_string>
  ;
  ;supported switch arguments
  ;
  ;-d action = output separate file for each crystal-detector, rebinned and normalised
  ;-m action = output separate file for each mac arm 1..5, rebinned and normalised
  ;-o action = output separate file for each mac arm 1..5, rebinned and normalised but using nominal 0, 30, 60, 90, 120 deg offsets
  ;-a action = output a single xye rebin file for all files in list, e.g "3610,3612,3700"
  ;-A action = same as -a but does not write header and extension is .xye
  ;-b action = output separate xye rebin files for each file in list
  ;-B action = same as -A but for -b
  ;<nulll>   = output xye file for only 1st file in file_list - catch all default
  ;
  ;this is the permant components list
  ;
  ;
  offsets_path="/dls/i11/software/gda/config/idlobjects/"
  ;
  argument=strcompress(arg1_string,/remove_all)
  index=where(argument eq ["-d","-m","-o","-a","-A","-B","-b",""])
  case index of
    -1:begin
         ;unidentified argument, return error
         return_string=" 0"
       end
    else:begin
           print," "
           print,"================== I-11 DATA REBIN v2 =================="
           t_start=systime(2)
           ;
           ;next extract run_numbers
           file_list=strcompress(strsplit((arg2_string),/extract),/remove_all)
           ;then add file path
           path=strcompress(arg3_string,/remove_all)
           step_size=float(arg4_string)
           user_comment=arg5_string
           out_path=path+"processing/"  
           ;
           rebin_it,path,out_path,file_list,step_size,argument,user_comment,offsets_path
           ;
           t_stop=systime(2)
           print,"rebin complete",t_stop-t_start," seconds"
           print,"========================================================="
           return_string=" 1"
         end
  endcase
  !except=0  ;turn off maths error reporting so as not to frighten users!!!!!
             ;actually a division by zero occurs when normalising because
             ;new binning arrays are longer than data, consequently the bins 
             ;at either end do not get filled and remain set to 0.
end
