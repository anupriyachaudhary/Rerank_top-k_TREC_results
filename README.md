# SIGSEGV

<img src="https://travis-ci.com/chippermist/SIGSEGV.svg?branch=master" />

## Usage

### Mount Filesystem
To run a fuse filesystem 
1) Run mkfs on the filesystem device you want to mount the filesystem on e.g to mount on `/dev/vdd` run `$ time ./bin/mkfs -n 8388608 -f "/dev/vdd" `
2) Mount fuse filesystem on a folder. E.g to mount on `mpoint/` run `$ ./bin/fuse -n 8388608 -f "/dev/vdd" "mpoint/" `
3) Once the filesystem is mounted it you can `cd <mount point path name>` to start using it. 


### The Flags have been added to the implementation and do not need to be provided.

#### Flags
* `-d`   : Debugging mode
* `-s`   : Single thread
* `-o`   : Optional Arguments


### Unmount Filesystem
Run `fusermount -u <mount point path name>` 

