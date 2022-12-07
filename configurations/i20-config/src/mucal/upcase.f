      subroutine upcase(line)
c     convert lower-case characters to upper case:
      character line*(*)
      do 100 n=1,len(line)
        ic=ichar(line(n:n))
        if(ic.ge.97.and.ic.le.122) line(n:n)=char(ic-32)
100    continue
      end
