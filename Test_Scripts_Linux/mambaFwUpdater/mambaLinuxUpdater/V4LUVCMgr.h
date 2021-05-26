#ifndef __V4L_UVC_MGR_H__
#define __V4L_UVC_MGR_H__

#include "UVCInterface.h"

class V4LUVCMgr : public UVCInterface
{
public:
	V4LUVCMgr();
	~V4LUVCMgr();
public: //implements the UVC Interface
	virtual bool enumeratePanaCast(std::vector<std::string> &devPaths);
	virtual bool openPanaCast(std::string devPath);
	virtual void closePanaCast();
   virtual void releasePanaCast();
	virtual bool getPanaCastDeviceInfo(unsigned short &vid, unsigned short &pid, std::string &serial, std::string &name);
	virtual bool getProperty(unsigned int propertyId, unsigned char *data, unsigned data_size);
	virtual bool setProperty(unsigned int propertyId, unsigned char *data, unsigned data_size);

private:
   int xioctl(int fd, int request, void *arg);
   int openDevice(std::string dev);
   bool isPanaCastDev(std::string devpath);

   //return vid & pid in hex string (lower case), and serial number and product name
   bool getVidPidNameSerial(std::string devpath, std::string &vidStr, std::string &pidStr, std::string &serial, std::string &product);
   bool getLineFromFile(std::string file, std::string &line);

private:
   int mDevFd;
   std::string mDevPath;

private:
	//disable copy constructor and assignment operator
	//because we are managing our own memeory
	V4LUVCMgr(const V4LUVCMgr&);
	void operator=(const V4LUVCMgr&);
};

#endif /*__V4L_UVC_MGR_H__*/
