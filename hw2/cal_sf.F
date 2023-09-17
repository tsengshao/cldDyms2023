PROGRAM sub
USE netcdf
USE mpi
IMPLICIT NONE

INTEGER, PARAMETER :: nx=512, ny=128, nz=45, nt=1201
REAL, PARAMETER :: dx=2000., dy=2000., dz0=500.
INTEGER :: err, ncid1, varid1
INTEGER :: i,j,k,m,n,o,t
INTEGER :: idxt
REAL, DIMENSION(nx,ny,nz)  :: eta, th, qv
REAL, DIMENSION(nx,nz)     :: eta_bar, hm_bar
REAL, DIMENSION(nx,nz,2)   :: sf
REAL, DIMENSION(nz+1) :: zz, zc, rho, rhoz, thbar, thvbar, pbar, pibar&
                       , q1, q2, fnz, fnu
REAL, DIMENSION(nz) :: dz, an, bn, cn
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

dz(1)=0.
DO k=2,nz
  dz(k)=zz(k)-zz(k-1)
ENDDO
DO k=2,nz-1
  an(k)=-fnz(k)*fnu(k)/(dz0**2)
  !cn(k)=-fnz(k+1)*fnu(k+1)/(dz0**2)
  cn(k)=-fnz(k)*fnu(k+1)/(dz0**2)
  bn(k)=-(an(k)+cn(k))
ENDDO

sf(:,:,:) = 0.
idxt=1

idum2=nt/nproc
ts=idum2*cpu ! start from 0
te=idum2*(cpu+1)
if(cpu+1==nproc) te=te+mod(nt,nproc)-1
print*, 'cpu=',cpu,'ts=',ts,'te=',te

!DO t=0,1200
DO t=ts,te
!if(cpu==nproc-1) print*, '======','cpuid=',cpu,'t=',t,'======'

! read 3-D data field
WRITE(filename,114) trim(path), "/", trim(run),"/",&
"archive/exp",".L.Dynamic-",t,".nc"
114 FORMAT(6A,I6.6,A)

err = nf90_open(trim(filename),NF90_NOWRITE,ncid1)
IF (err/=nf90_noerr) WRITE(*,*) "open fail"
err = nf90_inq_varid(ncid1,"eta",varid1)
IF (err/=nf90_noerr) WRITE(*,*) "var_inq fail"
err = nf90_get_var(ncid1,varid1,eta,start=(/ 1,1,1,1 /),count=(/ nx,ny,nz,1 /))
IF (err/=nf90_noerr) WRITE(*,*) "read fail"
o=0
IF (err/=nf90_noerr) o=1
err = nf90_close(ncid1)

WRITE(filename,114) trim(path), "/", trim(run),"/",&
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

if (o==1) then
  sf(:,:,idxt) = -999000.
  hm_bar(:,:)  = -999000.
  eta_bar(:,:) = -999000.
  goto 5555
endif


eta_bar=sum(eta,2)/real(ny)

DO k=1,nz
  eta_bar(:,k)=eta_bar(:,k)*rhoz(k)
  hm_bar(:,k)=1004.5*sum(th(:,:,k),2)/real(ny)*pibar(k)+9.8*zc(k)&
              +2.5e6*sum(qv(:,:,k),2)/real(ny) 
ENDDO

if (t==0) then
  sf (:,:,idxt)=0.
else
  call elliptic(nx,nz,dx,an,bn,cn,eta_bar,sf(:,:,3-idxt),sf(:,:,idxt))
endif

! write data
5555 continue
WRITE(filename,112) "/data/C.shaoyu/CD2023/dat/vvmYmean/sfhm/",trim(run),&
                    "/sfhm-",t,".dat"
112 FORMAT(3A,I6.6,A)
OPEN(10,FILE=trim(filename),ACCESS="direct",RECL=nx*nz)
WRITE(10,REC=1) sf(:,:,idxt)
WRITE(10,REC=2) hm_bar(:,:)
WRITE(10,REC=3) eta_bar(:,:) 
CLOSE(10)

! transform idxt 1->2, 2->1
idxt = 3-idxt
ENDDO

call MPI_FINALIZE(ierr)

END PROGRAM sub



!===========================================================================================

subroutine elliptic(nx,nz,dx,an,bn,cn,eta, psi_ini, psi)

integer, intent(in) :: nx, nz
integer :: i,j,k, im,ip
real, dimension(nz), intent(in) :: an, bn, cn
real :: dn, en, fn
real :: dum1,dum2,dum3,dum4
real, dimension(nx,nz), intent(in)    :: psi_ini
real, dimension(nx,nz), intent(inout) :: eta
real, dimension(nx,nz), intent(out)   :: psi

dn=-1./(dx**2)
en=-(dn+dn)

psi=psi_ini
dum1=1.
dum4=0.9

eta=-1*eta

j=0
do while(dum1>1e-8)
j=j+1
dum1=-1

do k=2, nz-1
do i=1, nx
ip = i+1
im = i-1
if(i==1) im = nx
if(i==nx) ip = 1

dum2 = eta(i,k) - (dn*psi(ip,k) + dn*psi(im,k) + an(k)*psi(i,k-1) + cn(k)*psi(i,k+1))
dum3 = psi(i,k)
psi(i,k) = (1-dum4)*psi(i,k) + dum4/(bn(k)+en)*dum2
dum1 = max(dum1, abs((dum3-psi(i,k))/psi(i,k)))

enddo
enddo

!print*, 'counter=',j,dum1,psi(200,20)
enddo

! der
!! do k=2,nz-1
!! do i=1,nx
!!   im=i-1
!!   ip=i+1
!!   IF (i==1) im=nx
!!   IF (i==nx) ip=1
!!   dum2=(eta(i,k)-(dn*psi(ip,k)+fn*psi(im,k)+an(k)*psi(i,k-1)+cn(k)*psi(i,k+1)))/(en+bn(k))
!!   dum3=psi(i,k)
!!   psi(i,k)=(1-dum4)*psi(i,k)+dum4*dum2
!!   dum1=max(dum1,abs((dum3-psi(i,k))/psi(i,k)))
!! enddo
!! enddo
!! 
!! j=j+1
!! !write(*,*) dum1, j
!! enddo

end subroutine elliptic




