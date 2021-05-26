#ifndef __IOKIT_UVC_MGR_H__
#define __IOKIT_UVC_MGR_H__

#include "UVCInterface.h"
 
#include <IOKit/IOKitLib.h>
#include <IOKit/IOCFPlugIn.h>
#include <IOKit/usb/IOUSBLib.h>
 
#include <IOKit/IOBSD.h>
#include <IOKit/storage/IOCDMedia.h>
#include <IOKit/storage/IOMedia.h>
#include <IOKit/storage/IOCDTypes.h>
#include <IOKit/storage/IOMediaBSDClient.h>
 
#include <IOKit/serial/IOSerialKeys.h>
#include <IOKit/serial/ioss.h>
#include <CoreFoundation/CFNumber.h>



class IOKitUVCMgr : public UVCInterface
{
public:
	IOKitUVCMgr();
	virtual ~IOKitUVCMgr();

public: 
	//implement the B6UVCMgr Interface
	virtual bool enumeratePanaCast(std::vector<std::string> &devPaths);
	virtual bool openPanaCast(std::string devPath);
	virtual void closePanaCast();
        virtual void releasePanaCast();
	virtual bool getPanaCastDeviceInfo(unsigned short &vid, unsigned short &pid, std::string &serial, std::string &name);
	virtual bool getProperty(unsigned int propertyId, unsigned char *data, unsigned data_size);
	virtual bool setProperty(unsigned int propertyId, unsigned char *data, unsigned data_size);

private:
	//Use this function in 2 ways:

	//1st way: if want to get the PanaCast's control interface handler for particular serial number, then
	//supply that serial number in the parameter "devSn" 
	//if found, the handle will be set to the parameter "cIf"
	//otherwise, "cIf" will be NULL
	//In this case, output parameter "allDevs" will be empty

	//2nd way: if want to return all the PanaCast devices' serial numbers, then
	//set the parameter "devSn" to empty string "",
	//all device's serial number will be return to parameter "allDevs",
	//in this case, "cIf" will be NULL 
	bool getAllDevices(std::string devSn, std::vector<std::string> &allDevs, IOUSBInterfaceInterface190 ** &cIf);

	//return the USB device's serial number
	std::string getUSBStringDescriptor(IOUSBDeviceInterface182** usbDevice, UInt8 idx);

	//return the USB's control interface
	IOUSBInterfaceInterface190** getControlInterface(IOUSBDeviceInterface182 ** usbIf);
	
private:
	IOUSBInterfaceInterface190** mControlIf;
private:
	//disable copy constructor and assignment operator
	//because we are managing our own memeory
	IOKitUVCMgr(const IOKitUVCMgr&);
	void operator=(const IOKitUVCMgr&);
};

#endif /*__IOKIT_UVC_MGR_H__*/
