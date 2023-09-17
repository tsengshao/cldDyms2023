PROGRAM sub
USE netcdf
USE mpi
IMPLICIT NONE

INTEGER, PARAMETER :: nx=512, ny=128, nz=45, nt=1201
REAL, PARAMETER :: dx=2000., dy=2000., dz0=500.
INTEGER :: err, ncid1, varid1
INTEGER :: i,j,k,m,n,o,t
REAL, DIMENSION(nx,ny,nz)  :: qv
REAL, DIMENSION(nx,nz)     :: qv_bar
REAL, DIMENSION(nx,ny)     :: sst
REAL, DIMENSION(nx)        :: sst_bar
REAL, DIMENSION(nz+1) :: zz, zc, rho, rhoz, thbar, thvbar, pbar, pibar&
                       , q1, q2, fnz, fnu
CHARACTER(300) :: path, filename, run
INTEGER :: ierr, cpu, nproc
INTEGER :: ts, te, idum1, idum2

call MPI_INIT(ierr)
call MPI_COMM_SIZE(MPI_COMM_WORLD, nproc, ierr)
call MPI_COMM_RANK(MPI_COMM_WORLD, cpu, ierr)

path="/data/mog/rce"
!run="runname"
call GETARG(1,run)

WRITE(filename,111) trim(path),'/',trim(run),"/fort.98"
111 FORMAT(A,A,A,A)

! read mean profiles
OPEN(10,FILE=trim(filename), ACTION='read')
DO i=1,188
  READ(10,*)
ENDDO
DO i=1,nz+1
  READ(10,*) j, zz(i), zc(i), fnz(i), fnu(i)
ENDDO
DO i=1,3
  READ(10,*)
ENDDO
DO i=1,nz+1
  READ(10,*) j, rho(i), thbar(i), pbar(i), pibar(i)
ENDDO
DO i=1,3
  READ(10,*)
ENDDO
DO i=1,nz+1
  READ(10,*) j, rhoz(i), rhoz(i), q1(i), q2(i)
ENDDO
DO i=1,3
  READ(10,*)
ENDDO
DO i=2,nz+1
  READ(10,*) j, rhoz(i)
ENDDO
CLOSE(10)

idum2=nt/nproc
ts=idum2*cpu ! start from 0
te=idum2*(cpu+1)
if(cpu+1==nproc) te=te+mod(nt,nproc)-1
print*, 'cpu=',cpu,'ts=',ts,'te=',te

!DO t=0,1200
DO t=ts,te
print*, '======',t,'======'

! read 3-D data field
WRITE(filename,114) trim(path), "/", trim(run),"/",&
"archive/exp",".L.Thermodynamic-",t,".nc"
114 FORMAT(6A,I6.6,A)

err = nf90_open(trim(filename),NF90_NOWRITE,ncid1)
IF (err/=nf90_noerr) WRITE(*,*) "open fail"
err = nf90_inq_varid(ncid1,"qv",varid1)
IF (err/=nf90_noerr) WRITE(*,*) "var_inq fail"
err = nf90_get_var(ncid1,varid1,qv,start=(/ 1,1,1,1 /),count=(/ nx,ny,nz,1 /))
IF (err/=nf90_noerr) WRITE(*,*) "read fail"
o=0
IF (err/=nf90_noerr) o=1
err = nf90_close(ncid1)

! read 2-D data field
WRITE(filename,114) trim(path), "/", trim(run),"/",&
"archive/exp",".C.Surface-",t,".nc"

err = nf90_open(trim(filename),NF90_NOWRITE,ncid1)
IF (err/=nf90_noerr) WRITE(*,*) "open fail"
err = nf90_inq_varid(ncid1,"tg",varid1)
IF (err/=nf90_noerr) WRITE(*,*) "var_inq fail"
err = nf90_get_var(ncid1,varid1,sst,start=(/ 1,1,1 /),count=(/ nx,ny,1 /))
IF (err/=nf90_noerr) WRITE(*,*) "read fail"
err = nf90_close(ncid1)

if (o==1) then
  qv_bar(:,:)  = -999000.
  sst_bar(:) = -999000.
  goto 5555
endif

qv_bar=sum(qv,2)/real(ny)
sst_bar=sum(sst,2)/real(ny)

! write data
5555 continue
WRITE(filename,112) "/data/C.shaoyu/CD2023/dat/vvmYmean/qvtg/",trim(run),&
                    "/qvtg-",t,".dat"
112 FORMAT(3A,I6.6,A)
OPEN(10,FILE=trim(filename),ACCESS="direct",RECL=nx)
do i=1,nz
WRITE(10,REC=i) qv_bar(:,i)
enddo
WRITE(10,REC=nz+1) sst_bar
CLOSE(10)

enddo

END PROGRAM sub
