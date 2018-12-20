; Method returns message based on presence or  
; absence of argument. 
FUNCTION helloworldex::HelloFrom, who 
      IF (N_ELEMENTS(who) NE 0) THEN BEGIN 
      message = "Hello World from " + who 
      RETURN, message 
   ENDIF ELSE BEGIN 
      message = 'Hello World' 
      RETURN, message 
   ENDELSE 
END 
 
; Init returns object reference on successful 
; initialization. 
FUNCTION helloworldex::INIT 
   RETURN, 1 
END 
 
; Object definition. 
PRO helloworldex__define 
  struct = {helloworldex, $ 
     who: '' , $ 
     message: ' ' $ 
  } 
END 
