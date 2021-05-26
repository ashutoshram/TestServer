#ifdef __APPLE__

#include "IOKitUVCMgr.h"
#include <algorithm>
#include <string> 

#define PANACAST_VENDOR_ID 0x0b0e
#define PANACAST_XU_ID 0x4
#define PANACAST_INTERFACE_NUM 0x1

#define UVC_CONTROL_INTERFACE_CLASS 14
#define UVC_CONTROL_INTERFACE_SUBCLASS 1

//      video class-specific request codes
#define UVC_SET_CUR     0x01
#define UVC_GET_CUR     0x81
#define UVC_GET_MIN     0x82
#define UVC_GET_MAX     0x83
#define UVC_GET_RES		0x84
#define UVC_GET_LEN		0x85
#define UVC_GET_INFO	0x86
#define UVC_GET_DEF		0x87


IOKitUVCMgr::IOKitUVCMgr()
{
	mControlIf = NULL;
}

IOKitUVCMgr::~IOKitUVCMgr()
{
   releasePanaCast();
}

bool IOKitUVCMgr::enumeratePanaCast(std::vector<std::string> &devPaths)
{
	IOUSBInterfaceInterface190 ** dummy = NULL;
	if (!getAllDevices("", devPaths, dummy)) {
		printf("enumeratePanaCast: getAllDevices failed\n");
		return false;
	}	
	return devPaths.size() != 0;
}

bool IOKitUVCMgr::openPanaCast(std::string devPath)
{
	closePanaCast(); //close any previously opened device first

	std::vector<std::string> dummy;
	if (!getAllDevices(devPath, dummy, mControlIf)) {
		printf("openPanaCast: getAllDevices failed\n");
		return false;
	} 
	if (mControlIf == NULL) return false;	
//Note: we found that in some OS (10.12.6), the following USBInterfaceOpen()
//will fail if video is already streaming...
//And if we commented out the USBInterfaceOpen() call, the vendor command
//is still working as expected. Therefore, we disabled the codes below.
#if 0
	kern_return_t err = (*mControlIf)->USBInterfaceOpen(mControlIf);
	if ( err != kIOReturnSuccess )
	{
		printf("openPanaCast: USBInterfaceOpenfailed\n");
		mControlIf = NULL;
		return false;
	}
#endif
	return true;
}

void IOKitUVCMgr::closePanaCast()
{
	if (mControlIf) (*mControlIf)->USBInterfaceClose(mControlIf);
	mControlIf = NULL;
}

void IOKitUVCMgr::releasePanaCast()
{
   closePanaCast(); //in our case, same as closePanaCast()
}

bool IOKitUVCMgr::getPanaCastDeviceInfo(unsigned short &vid, unsigned short &pid, std::string &serial, std::string &name)
{
	if (mControlIf == NULL) return false;

	//getting Vendor ID
	UInt16 v;
	IOReturn ret = (*mControlIf)->GetDeviceVendor(mControlIf,&v);
	if( ret != kIOReturnSuccess || v != PANACAST_VENDOR_ID) {
		printf("getPanaCastDeviceInfo: GetDeviceVendorfailed\n");
		return false;
	}
	vid = v;

	//getting Product ID
	UInt16 p;
	ret = (*mControlIf)->GetDeviceProduct(mControlIf,&p);
	if( ret != kIOReturnSuccess) {
		printf("getPanaCastDeviceInfo: GetDeviceProductfailed\n");
		return false;
	}
	pid = p;

	//getting Device Name
	io_service_t usbDevice;
	io_name_t deviceName;
	ret = (*mControlIf)->GetDevice(mControlIf,&usbDevice);
	if( ret != kIOReturnSuccess) {
		printf("getPanaCastDeviceInfo: GetDevicefailed\n");
		return false;
	}
	IORegistryEntryGetName( usbDevice, deviceName);
	name = std::string(deviceName);

	//getting device interface for serial number
	SInt32                        score;
	IOCFPlugInInterface**         plugin = NULL; 
	IOUSBDeviceInterface182**     deviceInterface = NULL;
	kern_return_t                 err;

	err = IOCreatePlugInInterfaceForService( usbDevice, 
			kIOUSBDeviceUserClientTypeID, 
			kIOCFPlugInInterfaceID, 
			&plugin, 
			&score ); 
	if( (kIOReturnSuccess != err) || !plugin ) {
		printf("getPanaCastDeviceInfo Error: IOCreatePlugInInterfaceForService returned 0x%08x.", err );
		if (plugin!=NULL) IODestroyPlugInInterface(plugin);
		return false;
	}

	HRESULT	res = (*plugin)->QueryInterface(plugin, CFUUIDGetUUIDBytes(kIOUSBDeviceInterfaceID), (LPVOID*) &deviceInterface );
	(*plugin)->Release(plugin);
	if( res || deviceInterface == NULL ) {
		printf( "getAllDevices Error: QueryInterface returned %d.\n", (int)res );
		if (plugin!=NULL) IODestroyPlugInInterface(plugin);
		return false;
	}

	//getting the serial number
	UInt8 snIdx;
	ret = (*deviceInterface)->USBGetSerialNumberStringIndex( deviceInterface, &snIdx);
	if (ret != kIOReturnSuccess) {
		printf("getAllDevices error: failed to get serial number idx\n");
		return false;
	}
	serial = getUSBStringDescriptor(deviceInterface, snIdx);

	return true;
}

bool IOKitUVCMgr::getProperty(unsigned int propertyId, unsigned char *data, unsigned data_size)
{
	if (mControlIf == NULL) return false;

	kern_return_t err;
	IOUSBDevRequest request;
	request.bmRequestType = USBmakebmRequestType(kUSBIn, kUSBClass, kUSBInterface);
	request.bRequest = UVC_GET_CUR;
	request.wValue = (propertyId << 8);
	request.wIndex = (PANACAST_XU_ID << 8) | PANACAST_INTERFACE_NUM;
	request.wLength = data_size;
	request.pData = data;

	err = (*mControlIf)->ControlRequest( mControlIf, 0, &request );
	if ( err != kIOReturnSuccess )
	{
		printf("getProperty: ControlRequest failed\n");
		return false;
	}
	return true;
}

bool IOKitUVCMgr::setProperty(unsigned int propertyId, unsigned char *data, unsigned data_size)
{
	if (mControlIf == NULL) return false;

	kern_return_t err;
	IOUSBDevRequest request;
	request.bmRequestType = USBmakebmRequestType(kUSBOut, kUSBClass, kUSBInterface);
	request.bRequest = UVC_SET_CUR;
	request.wValue = (propertyId << 8);
	request.wIndex = (PANACAST_XU_ID << 8) | PANACAST_INTERFACE_NUM;
	request.wLength = data_size;
	request.pData = data;

	err = (*mControlIf)->ControlRequest( mControlIf, 0, &request );
	if ( err != kIOReturnSuccess )
	{
		printf("setProperty: ControlRequest failed\n");
		return false;
	}
	return true;
}

bool IOKitUVCMgr::getAllDevices(std::string devSn, std::vector<std::string> &allDevs, IOUSBInterfaceInterface190 ** &cIf)
{
	allDevs.clear();
	cIf = NULL;

	io_iterator_t serviceIterator;
        io_service_t usbDevice ;       
	CFMutableDictionaryRef matchingDict = IOServiceMatching(kIOUSBDeviceClassName);

	//set our vendor ID
	long usbVendor = PANACAST_VENDOR_ID;
	CFNumberRef numberRef = CFNumberCreate(kCFAllocatorDefault, kCFNumberSInt32Type, &usbVendor);
	CFDictionarySetValue(matchingDict, CFSTR(kUSBVendorID), numberRef);
	CFRelease(numberRef);

	//any PIDs
	CFDictionarySetValue(matchingDict, CFSTR(kUSBProductID), CFSTR("*"));

	//get the service iter
	kern_return_t rt =  IOServiceGetMatchingServices( kIOMasterPortDefault, matchingDict, &serviceIterator );
	if (rt != kIOReturnSuccess) {
		printf("getAllDevices error: no device found\n");
		return false;
	}

	while ( (usbDevice = IOIteratorNext(serviceIterator)) ){
		//Get Device interface
		SInt32                        score;
		IOCFPlugInInterface**         plugin = NULL; 
		IOUSBDeviceInterface182**     deviceInterface = NULL;
		kern_return_t                 err;

		err = IOCreatePlugInInterfaceForService( usbDevice, 
				kIOUSBDeviceUserClientTypeID, 
				kIOCFPlugInInterfaceID, 
				&plugin, 
				&score ); 
		if( (kIOReturnSuccess != err) || !plugin ) {
			//printf("getAllDevices Error: IOCreatePlugInInterfaceForService returned 0x%08x.\n", err );
			if (plugin!=NULL) IODestroyPlugInInterface(plugin);
			continue; //skip and check next device
		}

		HRESULT	res = (*plugin)->QueryInterface(plugin, CFUUIDGetUUIDBytes(kIOUSBDeviceInterfaceID), (LPVOID*) &deviceInterface );
		(*plugin)->Release(plugin);
		if( res || deviceInterface == NULL ) {
			//printf( "getAllDevices Error: QueryInterface returned %d.\n", (int)res );
			if (plugin!=NULL) IODestroyPlugInInterface(plugin);
			continue; //skip and check next device
		}
		
		UInt16 vid;
		IOReturn ret = (*deviceInterface)->GetDeviceVendor(deviceInterface, &vid);
		if( ret != kIOReturnSuccess || vid != PANACAST_VENDOR_ID) {
			IODestroyPlugInInterface(plugin);
			continue;
		}

		//this is a PanaCast device, get its serial number:
		UInt8 snIdx;
		ret = (*deviceInterface)->USBGetSerialNumberStringIndex( deviceInterface, &snIdx);
		if (ret != kIOReturnSuccess) {
			printf("getAllDevices error: failed to get serial number idx\n");
			IODestroyPlugInInterface(plugin);
			continue;
		}
	
		std::string sn = getUSBStringDescriptor(deviceInterface, snIdx);


		if (devSn != "" && devSn == sn) { //user wants to return the control interface for particular serial number
			cIf = getControlInterface(deviceInterface);		
			IODestroyPlugInInterface(plugin);
			return true;
		}

		if (devSn == "") { //user wants to return all PanaCast's serial number
			allDevs.push_back(sn);
		}
		IODestroyPlugInInterface(plugin);
	} 

	if (devSn == "" && allDevs.size() == 0) return false;
	if (devSn != "" && cIf == NULL) return false;
	return true;
}

IOUSBInterfaceInterface190** IOKitUVCMgr::getControlInterface(IOUSBDeviceInterface182 ** usbIf)
{
	IOUSBInterfaceInterface190 **controlInterface;
	
	io_iterator_t interfaceIterator;
	IOUSBFindInterfaceRequest interfaceRequest;
	interfaceRequest.bInterfaceClass = kUSBVideoInterfaceClass; //UVC_CONTROL_INTERFACE_CLASS; 
	interfaceRequest.bInterfaceSubClass = kUSBVideoControlSubClass; //UVC_CONTROL_INTERFACE_SUBCLASS; 
	interfaceRequest.bInterfaceProtocol = kIOUSBFindInterfaceDontCare;
	interfaceRequest.bAlternateSetting = kIOUSBFindInterfaceDontCare;
	
	IOReturn success = (*usbIf)->CreateInterfaceIterator( usbIf, &interfaceRequest, &interfaceIterator );
	if( success != kIOReturnSuccess ) {
		printf("getControlInterface: failed to create if iterator\n");
		return NULL;
	}
	
	io_service_t usbInterface = IOIteratorNext(interfaceIterator);
	if (!usbInterface) {
		printf("getControlInterface error: no inteface next found\n");
		return NULL;
	}

	//Create an intermediate plug-in
	SInt32 score;
	IOCFPlugInInterface **plugInInterface = NULL;
   //Note: there might be other constant values for kIOCFPlugInInterfaceID in the new Mojave OS...
	kern_return_t kr = IOCreatePlugInInterfaceForService( usbInterface, kIOUSBInterfaceUserClientTypeID, kIOCFPlugInInterfaceID, &plugInInterface, &score );

	//Release the usbInterface object after getting the plug-in
	IOObjectRelease(usbInterface);

	if( (kr != kIOReturnSuccess) || !plugInInterface ) {
		printf("getControlInterface Error: Unable to create a plug-in (%08x)\n", kr );
		return NULL;
	}

	//Now create the device interface for the interface
	HRESULT result = (*plugInInterface)->QueryInterface( plugInInterface, CFUUIDGetUUIDBytes(kIOUSBInterfaceInterfaceID), (LPVOID *) &controlInterface );

	//No longer need the intermediate plug-in
	(*plugInInterface)->Release(plugInInterface);

	if( result || !controlInterface ) {
		printf("getControlInterface Error: Couldn’t create a device interface for the interface (%08x)", (int) result );
		return NULL;
	}

	return controlInterface;
}

std::string IOKitUVCMgr::getUSBStringDescriptor(IOUSBDeviceInterface182** usbDevice, UInt8 idx)
{
   if (!usbDevice) return "";

   UInt16 buffer[64];
   IOUSBDevRequest request;

   request.bmRequestType = USBmakebmRequestType(kUSBIn, kUSBStandard, kUSBDevice);
   request.bRequest = kUSBRqGetDescriptor;
   request.wValue = (kUSBStringDesc << 8) | idx;
   request.wIndex = 0x409; // english
   request.wLength = sizeof( buffer );
   request.pData = buffer;

   kern_return_t err = (*usbDevice)->DeviceRequest( usbDevice, &request );
   if ( err != 0 )
   {
      return "";
   }

   char stringBuf[128];
   int count = ( request.wLenDone - 1 ) / 2;
   int i;
   for ( i = 0; i < count; i++ ) {
      stringBuf[i] = buffer[i+1];
   }
   stringBuf[i] = '\0';  

   return stringBuf;
}

#endif
