#ifdef _WIN32

#include "WinUVCMgr.h"
#include <initguid.h>
#include <Windows.h>
#include <string>
DEFINE_GUID(GUID_PANACAST_EXTENSION_UNIT_DESCRIPTOR,
	0x6131bc65, 0x3ae8, 0x4abb, 0xa0, 0x27, 0x72, 0x97, 0x7a, 0x0c, 0x9e, 0xfc);


WinUVCMgr::WinUVCMgr()
{
	mHandle = NULL;
	mgr = new UVCExtensionUnitManager();
	if (!mgr) throw std::runtime_error("Failed to create XU mgr");
}

WinUVCMgr::~WinUVCMgr()
{
	closePanaCast();
	delete mgr;
}

bool WinUVCMgr::enumeratePanaCast(std::vector<std::string> &devPaths)
{
	return mgr->enumeratePanaCastDeviceNames(devPaths);
}
bool WinUVCMgr::openPanaCast(std::string devPath)
{
	closePanaCast();
	mHandle = mgr->openExtensionUnit(GUID_PANACAST_EXTENSION_UNIT_DESCRIPTOR, devPath);
	return mHandle != NULL;
}
void WinUVCMgr::closePanaCast()
{
	if (mHandle) UVCExtensionUnitManager::closeExtensionUnit(&mHandle, false);
	mHandle = NULL;
}

void WinUVCMgr::releasePanaCast()
{
	if (mHandle) UVCExtensionUnitManager::closeExtensionUnit(&mHandle, true);
	mHandle = NULL;
}

bool WinUVCMgr::getProperty(unsigned int propertyId, unsigned char *data, unsigned data_size)
{
	if (!mHandle) {
		printf("WinUVCMgr::getProperty - no device opened\n");
		return false;
	}
	return SUCCEEDED(UVCExtensionUnitManager::getProperty(mHandle, propertyId, data, data_size));
}

bool WinUVCMgr::setProperty(unsigned int propertyId, unsigned char *data, unsigned data_size)
{
	if (!mHandle) {
		printf("WinUVCMgr::setProperty - no device opened\n");
		return false;
	}
	return SUCCEEDED(UVCExtensionUnitManager::setProperty(mHandle, propertyId, data, data_size));
}

bool WinUVCMgr::getPanaCastDeviceInfo(unsigned short &vid, unsigned short &pid, std::string &serial, std::string &name)
{
	if (!mHandle) {
		printf("WinUVCMgr::setProperty - no device opened\n");
		return false;
	}

	vid = mHandle->vid;
	pid = mHandle->pid;
	serial = mHandle->serial;
	name = mHandle->name;
	return true;
}

#endif