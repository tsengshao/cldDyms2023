PROGRAM sub
USE netcdf
IMPLICIT NONE

INTEGER, PARAMETER :: nx=512, ny=128, nz=45
REAL, PARAMETER :: dx=2000., dy=2000., dz0=500.
REAL :: tarray(2), time, dtime
REAL :: dum1,dum2,dum3,dum4,dum5
REAL :: dum6,dum7,dum8,dum9,dum0
REAL :: qv_sat
INTEGER :: dum11,dum22,dum33,n_out
INTEGER :: err, ncid1, varid1, ncid2, varid2, ncid3, varid3, ncid4, varid4
INTEGER :: i,j,k,m,n,o,t
REAL, DIMENSION(nx,ny,nz) :: eta, th, qv
REAL, DIMENSION(nx,nz) :: eta_bar, hm_bar
REAL, DIMENSION(nx,nz,1201) :: sf, hm
REAL, DIMENSION(nx) :: tmp2, vol2
REAL, DIMENSION(nz+1) :: zz, zc, rho, rhoz, thbar, thvbar, pbar, pibar&
                       , q1, q2, fnz, fnu
REAL, DIMENSION(nz) :: dz, an, bn, cn
REAL, DIMENSION(nx,nz,1201) :: var
CHARACTER(300) :: path, filename, run, readline
integer(kind=selected_int_kind(5)) :: ierr

path="/data/mog/rce/"
run="rce_walker_15k_1m_p3"

WRITE(filename,111) trim(path),"/",trim(run),"/fort.98"
111 FORMAT(A,A,A,A)

! read mean profiles
OPEN(10,FILE=filename)
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
dz(1)=0.
DO k=2,nz
  dz(k)=zz(k)-zz(k-1)
ENDDO
CLOSE(10)

DO k=2,nz-1
  an(k)=-fnz(k)*fnu(k)/(dz0**2)
  cn(k)=-fnz(k+1)*fnu(k+1)/(dz0**2)
  bn(k)=-(an(k)+cn(k))
ENDDO

n=1
DO t=1200,1200

! read 3-D data field
WRITE(filename,112) trim(path), "/", trim(run),"/",&
"archive/exp",".L.Dynamic-",t,".nc"
112 FORMAT(6A,I6.6,A)

err = nf90_open(trim(filename),NF90_NOWRITE,ncid1)
IF (err/=nf90_noerr) WRITE(*,*) "open fail"
err = nf90_inq_varid(ncid1,"eta",varid1)
IF (err/=nf90_noerr) WRITE(*,*) "var_inq fail"
err = nf90_get_var(ncid1,varid1,eta,start=(/ 1,1,1,1 /),count=(/ nx,ny,nz,1 /))
IF (err/=nf90_noerr) WRITE(*,*) "read fail"
o=0
IF (err/=nf90_noerr) o=1
err = nf90_close(ncid1)

WRITE(filename,112) trim(path), "/", trim(run),"/",&
"archive/exp",".L.Thermodynamic-",t,".nc"

err = nf90_open(trim(filename),NF90_NOWRITE,ncid1)
IF (err/=nf90_noerr) WRITE(*,*) "open fail"
err = nf90_inq_varid(ncid1,"th",varid1)
IF (err/=nf90_noerr) WRITE(*,*) "var_inq fail"
err = nf90_get_var(ncid1,varid1,th,start=(/ 1,1,1,1 /),count=(/ nx,ny,nz,1 /))
IF (err/=nf90_noerr) WRITE(*,*) "read fail"
err = nf90_inq_varid(ncid1,"qv",varid1)
IF (err/=nf90_noerr) WRITE(*,*) "var_inq fail"
err = nf90_get_var(ncid1,varid1,qv,start=(/ 1,1,1,1 /),count=(/ nx,ny,nz,1 /))
IF (err/=nf90_noerr) WRITE(*,*) "read fail"
err = nf90_close(ncid1)

eta_bar=sum(eta,2)/real(ny)

!sf(:,:,t)=eta_bar
DO k=1,nz
  eta_bar(:,k)=eta_bar(:,k)*rhoz(k)
  hm_bar(:,k)=1004.5*sum(th(:,:,k),2)/real(ny)*pibar(k)+9.8*zc(k)&
              +2.5e6*sum(qv(:,:,k),2)/real(ny) 
ENDDO

hm(:,:,t+1)=hm_bar

if (t==0) then
  sf (:,:,t+1)=0.
else
  call elliptic(nx,nz,dx,an,bn,cn,eta_bar,sf(:,:,t+1))
endif
if (o==1) then
  sf(:,:,t)=-1
  hm(:,:,t)=-1
endif


write(*,*) t
ENDDO

WRITE(filename,111) "/data/der0318/work/","p3_agg/data/",trim(run),&
                     "_sf_hourly.dat"
WRITE(filename,*) "./"//trim(run)//"_sf_hourly.dat"
OPEN(10,FILE=trim(filename),ACCESS="direct",RECL=nx*nz)
DO i=1201,1201
  WRITE(10,REC=1) sf(:,:,i)
  WRITE(10,REC=2) hm(:,:,i) 
  WRITE(10,REC=3) eta_bar
ENDDO
CLOSE(10)

END PROGRAM sub



!===========================================================================================

subroutine elliptic(nx,nz,dx,an,bn,cn,eta,psi)

integer, intent(in) :: nx, nz
integer :: i,j,k, im,ip
real, dimension(nz), intent(in) :: an, bn, cn
real :: dn, en, fn
real :: dum1,dum2,dum3,dum4
real, dimension(nx,nz), intent(inout) :: eta, psi

dn=-1./(dx**2)
fn=-1./(dx**2)
en=-(dn+fn)

psi=0.
dum1=1.
dum4=0.9

eta=-eta

j=0
do

if (dum1<1.E-8) GOTO 951
dum1=0.
do k=2,nz-1
do i=1,nx
  im=i-1
  ip=i+1
  IF (i==1) im=nx
  IF (i==nx) ip=1
  dum2=(eta(i,k)-(dn*psi(ip,k)+fn*psi(im,k)+an(k)*psi(i,k-1)+cn(k)*psi(i,k+1)))/(en+bn(k))
  dum3=psi(i,k)
  psi(i,k)=(1-dum4)*psi(i,k)+dum4*dum2
  dum1=max(dum1,abs((dum3-psi(i,k))/psi(i,k)))
enddo
enddo

j=j+1
write(*,*) dum1, j
enddo
951 continue

end subroutine elliptic




