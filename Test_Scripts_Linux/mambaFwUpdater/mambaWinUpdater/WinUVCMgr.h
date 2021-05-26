#ifndef __WIN_UVC_MGR_H__
#define __WIN_UVC_MGR_H__

#include "UVCInterface.h"

#ifdef _WIN32
#include "UVCExtensionUnitManager.h"
#endif

class WinUVCMgr : public UVCInterface
{
public:
	WinUVCMgr();
	~WinUVCMgr();
public: //implement the UVC Interface
	virtual bool enumeratePanaCast(std::vector<std::string> &devPaths);
	virtual bool openPanaCast(std::string devPath);
	virtual void closePanaCast();
	virtual void releasePanaCast();
	virtual bool getPanaCastDeviceInfo(unsigned short &vid, unsigned short &pid, std::string &serial, std::string &name);
	virtual bool getProperty(unsigned int propertyId, unsigned char *data, unsigned data_size);
	virtual bool setProperty(unsigned int propertyId, unsigned char *data, unsigned data_size);

private:
#ifdef _WIN32
	EUHandle * mHandle;
	UVCExtensionUnitManager * mgr;
#endif

private:
	//disable copy constructor and assignment operator
	//because we are managing our own memeory
	WinUVCMgr(const WinUVCMgr&);
	void operator=(const WinUVCMgr&);
};

#endif /*__WIN_UVC_MGR_H__*/