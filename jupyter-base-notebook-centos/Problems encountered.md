# Jupyter notebook on centos 7
The original task was to create a centos 7 image with jupyter notebook installed on it. Centos 7 official images was a base image for this project, and juypter notebook was taken from official base jupyter notebook image. Docker is used to build images and to run contaienrs. 
## First image
The first image that was made was very simple base notebook image with little to no modification. The only difference were package manager, as the original jupyter image is based on ubuntu it used ubuntu image and therefore apt was used as a package manager. For centos 7 yum is used as a package manager, becuase of this a first set of instuctions was changed. Another small difference was in required packages, some of the packages that ubuntu image reuqired are not required in centos 7 image, therefore they were taken away.
## Sudo for jovyan user
Jupyter creates a jovyan user as a defualut user it does not have sudo permission. However, for our purposes jovyan needed to have sudo access, therefore it was granted this access by injecting a file to sudoers.d directory to grant access to all sudo commands.

## Systemd 
Another reqirement for the image for the abbility to run systemd service by using systemctl commands. The test example was `systemctl start httpd`, however, this task was not complete as a few problems were encountered. All of them are documented below.

### D-Bus problem
The main problem encountered comes up when trying to run systemd. `systemctl` results in error `Failed to get D-Bus connection: opperation not permitted.` When trying to find about this error online there is an [article](https://developers.redhat.com/blog/2016/09/13/running-systemd-in-a-non-privileged-container#) about how to run systemd in the container. The main take was to run `/usr/sbin/init` as well as mounting some volumes on the containaer. However, doing so also does not help as it results in `Failed to create root chroup hierarchy: permissions denied` and `Faield to allocate manager object: Permissions denied`. When looking up these problems I found out about centos 8 and that it can resolves these issues.

### Centos 8 issues
So the next step was to use centos 8 as a base image for notebook. Running systemd on centos 8 didn't work either, however, it gave a bit of insight of why it is not working. So errors were looking like `cannot write /run/machine-id: Permissions denied` `Failed to write /run/systemd/container, ignoring: No such file or directory` and `Assertion 'getuid)_ == 0' failed at ../src/core/main.c@1174, function bump_rlimit_memlock(). Aborting.` After that I could find any resource on how to resolve such errors.

### Using sudo to start containter.
Even when all these errors are present there is a way to run systemd inside the contaijner, however, the container must be started as a root user so it the command must look like this `docker run ..... --user root ...`. This allows contaienr to start `/usr/sbin/init` with PID of 1 and therefore, systemd can be used inside the container. However, this means that using `docker exec -it <contaienr name> bash` will always give root user. To overcome this a command such as `docker exec -it --user jovyan <container name> bash` can be used.