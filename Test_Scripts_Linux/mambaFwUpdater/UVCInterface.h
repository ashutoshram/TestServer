#ifndef __UVC_INTERFACE_H__
#define __UVC_INTERFACE_H__

#include <string>
#include <vector>

/* This interface class defines all the UVC Extension Unit (XU) control APIs
that are necessary to perform all of the PanaCast2 supported tasks
*/
class UVCInterface {
public:
   virtual ~UVCInterface() {}

	//return a list of existing PanaCast that can be openned
	virtual bool enumeratePanaCast(std::vector<std::string> &devPaths) = 0;

	//open PanaCast through UVC
	virtual bool openPanaCast(std::string devPath) = 0;

	//close the opened PanaCast, but some resource maybe re-used later
	virtual void closePanaCast() = 0;

	//close the opened PanaCast, and fully release all resources
	virtual void releasePanaCast() = 0;

	//get device's VID, PID, Serial Number and Camera Name
	virtual bool getPanaCastDeviceInfo(unsigned short &vid, unsigned short &pid, std::string &serial, std::string &name) = 0;

	//get the current value of the given property ID
	virtual bool getProperty(unsigned int propertyId, unsigned char *data, unsigned data_size) = 0;

	//set the current value of the given property ID
	virtual bool setProperty(unsigned int propertyId, unsigned char *data, unsigned data_size) = 0;
};


#endif /*__UVC_INTERFACE_H__*/
