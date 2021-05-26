#ifdef __linux__

#include "V4LUVCMgr.h"
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdlib.h>
#include <algorithm>
#include <fstream>
#include <linux/videodev2.h>
#include <linux/uvcvideo.h>

#define MAMBA_VID "0b0e"
#define MAMBA_PID_AUDIO "3020"
#define MAMBA_PID_NO_AUDIO "3021"
#define MAMBA_PID_DUAL_STREAM "3022"
#define MAMBA_XU_ID 0x4

//	video class-specific request codes
#define UVC_SET_CUR	0x01
#define UVC_GET_CUR	0x81
#define UVC_GET_MIN	0x82
#define UVC_GET_MAX	0x83
#define UVC_GET_RES 0x84
#define UVC_GET_LEN 0x85
#define UVC_GET_INFO 0x86
#define UVC_GET_DEF 0x87

//#define DEBUG


V4LUVCMgr::V4LUVCMgr()
{
   mDevFd = -1;
   mDevPath = "";
}

V4LUVCMgr::~V4LUVCMgr()
{
	closePanaCast();
}

bool V4LUVCMgr::enumeratePanaCast(std::vector<std::string> &devPaths)
{
   devPaths.clear();
   DIR           *d;
   struct dirent *dir;
   std::string devDir = "/dev";
   d = opendir(devDir.c_str());
   if (d)
   {
      while ((dir = readdir(d)) != NULL)
      {
         std::string devName = devDir + "/" + dir->d_name; 
         if (devName.find("video") != std::string::npos) { //check video device only
            if (isPanaCastDev(devName)) {
               devPaths.push_back(devName);
            }
         }
      }
      closedir(d);
   }
   return devPaths.size() != 0;
}
bool V4LUVCMgr::openPanaCast(std::string devPath)
{
   int fd = openDevice(devPath);
   if (fd < 0) {
		printf("V4LUVCMgr::openPanaCast2Dev: failed to open device = %s\n", devPath.c_str());
      return false;
   }
   mDevFd = fd;
   mDevPath = devPath;
	return true;
}
void V4LUVCMgr::closePanaCast()
{
	if (mDevFd >= 0) {
      close(mDevFd);
		mDevFd = -1;
      mDevPath = "";
	}
}
void V4LUVCMgr::releasePanaCast()
{
   closePanaCast(); //in our case, same as close()
}

bool V4LUVCMgr::getProperty(unsigned int propertyId, unsigned char *data, unsigned data_size)
{
   if (mDevFd < 0) {
		printf("V4LUVCMgr::getProperty: no device opened\n");
      return false;
   }
   struct uvc_xu_control_query q;
   q.unit = MAMBA_XU_ID;//wIndex; 
   q.selector = propertyId; //wValue
   q.data = data;
   q.query = UVC_GET_CUR; //bRequest;
   q.size = data_size;
#ifdef DEBUG
   printf("V4LUVCMgr::getProperty, MAMBA_XU_ID(wIndex): 0x%x, wValue: 0x%x,"\
          "bRequest: 0x%x, wLen: 0x%x\n", q.unit,q.selector, q.query, q.size );
#endif
   if (xioctl(mDevFd, UVCIOC_CTRL_QUERY, &q) < 0) {
      printf("V4LUVCMgr::getProperty: errno = %d\n", errno);
      return false;
   }
   return true;
}

bool V4LUVCMgr::setProperty(unsigned int propertyId, unsigned char *data, unsigned data_size)
{
   if (mDevFd < 0) {
		printf("V4LUVCMgr::setProperty: no device opened\n");
      return false;
   }
   struct uvc_xu_control_query q;
   q.unit = MAMBA_XU_ID;//wIndex; 
   q.selector = propertyId; //wValue
   q.data = data;
   q.query = UVC_SET_CUR; //bRequest;
   q.size = data_size;
#ifdef DEBUG
   printf("V4LUVCMgr::setProperty, MAMBA_XU_ID = %d\n", MAMBA_XU_ID);
   printf("V4LUVCMgr::setProperty, MAMBA_XU_ID(wIndex): 0x%x, wValue: 0x%x,"\
          "bRequest: 0x%x, wLen: 0x%x\n", q.unit,q.selector, q.query, q.size );
#endif
   if (xioctl(mDevFd, UVCIOC_CTRL_QUERY, &q) < 0) {
      printf("V4LUVCMgr::setProperty: errno = %d\n", errno);
      return false;
   }
   return true;
}

int V4LUVCMgr::xioctl(int fd, int request, void *arg)
{
   int r;
   do r = ioctl (fd, request, arg);
   while (-1 == r && EINTR == errno);
   return r;
}

int V4LUVCMgr::openDevice(std::string dev) {
   return open(dev.c_str(), O_RDWR);
}

bool V4LUVCMgr::isPanaCastDev(std::string devPath)
{
   int fd = openDevice(devPath);
   if (fd < 0) return false;
   struct v4l2_capability cap = {0};
   //starting Linux kernel >= 4.16, camera will have 2 /dev/video nodes
   //I call the non-working one as the "dummy" node
   //cap.capabilities are for the parent device, so the streamming capability
   //will be true even for the "dummy" node.
   //Instead, we should use cap.device_caps, this is for the device specific
   if(xioctl(fd, VIDIOC_QUERYCAP, &cap) < 0 || !(cap.device_caps & V4L2_CAP_VIDEO_CAPTURE)) {
      printf("V4LUVCMgr::isPanaCastDev: %s is not a video capture device\n", devPath.c_str());
      close(fd);
      return false;
   }
   close(fd);

   std::string vidStr, pidStr, serial, name;
   if (!getVidPidNameSerial(devPath, vidStr, pidStr, serial, name)){
      printf("V4LUVCMgr::isPanaCastDev: %s failed to get info\n", devPath.c_str());
      return false;
   }
   return vidStr == MAMBA_VID && (pidStr == MAMBA_PID_AUDIO || pidStr == MAMBA_PID_NO_AUDIO || pidStr == MAMBA_PID_DUAL_STREAM);
}

bool V4LUVCMgr::getVidPidNameSerial(std::string devpath, std::string &vidStr, std::string &pidStr, std::string &serial, std::string &product)
{
   //vendor id & product id can be found in the following file(s)
   // /sys/class/video4linux/video0/device/../idVendor
   // /sys/class/video4linux/video0/device/../idProduct
   // OR
   // /sys/class/video4linux/video0/device/uevent


   //serial number & name can be found in the following files
   // /sys/class/video4linux/video0/device/../product
   // /sys/class/video4linux/video0/device/../serial

   std::size_t found = devpath.find_last_of("/");
   if (found == std::string::npos) {
      printf("V4LUVCMgr::getVendorId: invalid path %s\n", devpath.c_str());
      return "";
   }

   std::string vname = devpath.substr(found+1);
   std::string fVid = std::string("/sys/class/video4linux/") + vname + std::string("/device/../idVendor");
   std::string fPid = std::string("/sys/class/video4linux/") + vname + std::string("/device/../idProduct");
   std::string fSerial = std::string("/sys/class/video4linux/") + vname + std::string("/device/../serial");
   std::string fProduct = std::string("/sys/class/video4linux/") + vname + std::string("/device/../product");

   //vid
   if (!getLineFromFile(fVid, vidStr)) {
      printf("V4LUVCMgr::getVidPidNameSerial: failed to get vid\n");
      return false;
   }
   if (vidStr.size() != 4) {
      printf("V4LUVCMgr::getVidPidNameSerial: invalid vid %s\n", vidStr.c_str());
      return false;
   }
   std::transform(vidStr.begin(), vidStr.end(), vidStr.begin(), ::tolower);

   //pid
   if (!getLineFromFile(fPid, pidStr)) {
      printf("V4LUVCMgr::getVidPidNameSerial: failed to get pid\n");
      return false;
   }
   if (pidStr.size() != 4) {
      printf("V4LUVCMgr::getVidPidNameSerial: invalid pid %s\n", pidStr.c_str());
      return false;
   }
   std::transform(pidStr.begin(), pidStr.end(), pidStr.begin(), ::tolower);

   //serial
   if (!getLineFromFile(fSerial, serial)) {
      printf("V4LUVCMgr::getVidPidNameSerial: failed to get serial\n");
      return false;
   }

   //product name
   if (!getLineFromFile(fProduct, product)) {
      printf("V4LUVCMgr::getVidPidNameSerial: failed to get product\n");
      return false;
   }

   return true;
}

bool V4LUVCMgr::getLineFromFile(std::string file, std::string &line)
{
   std::ifstream fs(file);
   if (fs.fail()) {
      printf("V4LUVCMgr::getLineFromFile: failed to open %s\n", file.c_str());
      return false;
   }
   line = "";
   std::getline(fs, line); 
   return true;
}

bool V4LUVCMgr::getPanaCastDeviceInfo(unsigned short &vid, unsigned short &pid, std::string &serial, std::string &name)
{
   if (mDevFd < 0) {
		printf("V4LUVCMgr::getPanaCastDeviceInfo: no device opened\n");
      return false;
   }

   std::string vidStr, pidStr;
   if (!getVidPidNameSerial(mDevPath, vidStr, pidStr, serial, name)){
      printf("V4LUVCMgr::getPanaCastDeviceInfo: %s failed to get info\n", mDevPath.c_str());
      return false;
   }

   try {
      vid = std::stoi(vidStr, 0, 16);
      pid = std::stoi(pidStr, 0, 16);
   }
   catch (...) { 
      printf("V4LUVCMgr::getPanaCastDeviceInfo: %s failed to convert vid %s, pid %s\n", mDevPath.c_str(), vidStr.c_str(), pidStr.c_str());
      return false;
   }

   return true;
}

#endif
