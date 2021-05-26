#ifdef _WIN32

#include "UVCExtensionUnitManager.h"
#include "DeviceMonitor.h"
#include "panacastdevices.h"
#include <algorithm>
#include <locale>
#include <thread>
#include <initguid.h>
#include <Setupapi.h>
#include <Devpkey.h>
#include <cstdlib>
#include <chrono>

#pragma comment(lib, "Mf.lib")
#pragma comment(lib, "Mfplat.lib")
#pragma comment(lib, "Ksproxy.lib")
#pragma comment(lib, "Setupapi.lib")

#define NO_KSPROP_WRAPPER //enable this to use driver API without wrapper because wrapper makes update very slow.
                          //But make sure test the driver API thoroughly during unplug & plug to ensure it doesn't forever blocked.


class NotificationCB : public DeviceNotificationCallback {
public: //DeviceNotificationCallback implementation
	virtual void onDeviceArrived(std::string id, std::string name);
	virtual void onDeviceLost(std::string id, std::string name);
	virtual void onWindowClosed();
};
void NotificationCB::onDeviceArrived(std::string id, std::string name)
{
}
void NotificationCB::onDeviceLost(std::string id, std::string name)
{
	//id is the symbolic link, name is the friendly name
	//we don't use friendly name because our devName returned by enumeratePanaCastDeviceNames()
	//appended with the serial number as well;

	//Note: we need to call shutDownMediaSource() from a new thread because the main thread
	//may be in middle of shudDownMediaSource() (e.g., reboot()) and the Window OS can pause the 
	//current execution, and let the main thread handle the device lost notification first.
	//Since both shudDownMediaSource() can be running by the same main thread, CRITICAL_SECTION does not help
	std::thread th = std::thread(UVCExtensionUnitManager::shutDownMediaSource, id);
	th.detach();
}
void NotificationCB::onWindowClosed()
{
}

class CSLock
{
public:
	CSLock() { ::InitializeCriticalSection(&m_cs); }
	~CSLock() { ::DeleteCriticalSection(&m_cs); }
	void Lock() { ::EnterCriticalSection(&m_cs); }
	void Unlock() { ::LeaveCriticalSection(&m_cs); }
private:
	CRITICAL_SECTION m_cs;
};


static CSLock tableLock; //critical section protects the lookup tables

std::map<std::string, IMFMediaSource*> UVCExtensionUnitManager::mediaSourceTable;
std::map<std::string, std::string> UVCExtensionUnitManager::devNameTable;

static std::string GetErrorAsString(DWORD errorMessageID)
{
	LPSTR messageBuffer = nullptr;
	size_t size = FormatMessageA(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
		NULL, errorMessageID, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), (LPSTR)&messageBuffer, 0, NULL);
	std::string message(messageBuffer, size);
	LocalFree(messageBuffer);
	return message;
}

static std::wstring SysMultiByteToWide(const std::string& mb, UINT32 code_page) {
	if (mb.empty())
		return std::wstring();
	int mb_length = static_cast<int>(mb.length());
	// Compute the length of the buffer.
	int charcount = MultiByteToWideChar(code_page, 0,
		mb.data(), mb_length, NULL, 0);
	if (charcount == 0)
		return std::wstring();
	std::wstring wide;
	wide.resize(charcount);
	MultiByteToWideChar(code_page, 0, mb.data(), mb_length, &wide[0], charcount);
	return wide;
}

static std::string SysWideToMultiByte(const std::wstring& wide, UINT32 code_page) {
	int wide_length = static_cast<int>(wide.length());
	if (wide_length == 0)
		return std::string();
	// Compute the length of the buffer we'll need.
	int charcount = WideCharToMultiByte(code_page, 0, wide.data(), wide_length,
		NULL, 0, NULL, NULL);
	if (charcount == 0)
		return std::string();
	std::string mb;
	mb.resize(charcount);
	WideCharToMultiByte(code_page, 0, wide.data(), wide_length,
		&mb[0], charcount, NULL, NULL);
	return mb;
}
static std::wstring SysUTF8ToWide(const std::string& utf8) {
	return SysMultiByteToWide(utf8, CP_UTF8);
}

static std::string SysWideToUTF8(const std::wstring& wide) {
	return SysWideToMultiByte(wide, CP_UTF8);
}

template <class T> static void SafeRelease(T **ppT)
{
	if (*ppT)
	{
		(*ppT)->Release();
		*ppT = NULL;
	}
}

UVCExtensionUnitManager::UVCExtensionUnitManager()
{
	std::string cName;
	std::string wName;
	getUnusedWndName(cName, wName);
	stopMonitor = false;
	resourceIdList.clear();
	monitorTh = new std::thread(&UVCExtensionUnitManager::startDeviceMonitorMessageLoop, this, cName, wName);
}

UVCExtensionUnitManager::~UVCExtensionUnitManager()
{
	stopMonitor = true;
	((std::thread*)monitorTh)->join();
	delete (std::thread*)monitorTh;

	for (std::vector<std::string>::iterator it = resourceIdList.begin(); it != resourceIdList.end(); it++) {
		shutDownMediaSource(*it); //this is OK if it has been closed through closeExtensionUnit();
	}
	resourceIdList.clear();
}

void UVCExtensionUnitManager::startDeviceMonitorMessageLoop(std::string cName, std::string wName)
{
	NotificationCB cb;
	DeviceMonitor m(&cb, NULL, cName, wName);
	while (!stopMonitor) {
		m.dispatchMessages();
		Sleep(10);
	}
}

void UVCExtensionUnitManager::addToResourceList(std::string devId)
{
	bool found = false;
	for (std::vector<std::string>::iterator it = resourceIdList.begin(); it != resourceIdList.end(); it++) {
		if (*it == devId) {
			found = true;
			break;
		}
	}
	if (!found) resourceIdList.push_back(devId);
}

bool UVCExtensionUnitManager::enumeratePanaCastDeviceNames(std::vector<std::string> &devNames)
{
	devNames.clear();
	IMFActivate** ppDevices = NULL;
	UINT32 count = 0;
	if (!enumerateSources(ppDevices, count)) {
		//printf("enumeratePanaCastDeviceNames: enumerateSources failed\n");
		return false;
	}
	for (UINT32 i = 0; i < count; i++) {
		IMFActivate *device = ppDevices[i];
		std::string name;
		if (getMFActivateName(device, name)) {
			devNames.push_back(name);
		}
	}
	releaseIMFActivates(ppDevices, count);
	return devNames.size() != 0;
}

EUHandle* UVCExtensionUnitManager::openExtensionUnit(GUID guidEU, std::string devName)
{
	IMFActivate** ppDevices = NULL;
	UINT32 count = 0;
	if (!enumerateSources(ppDevices, count)) {
		printf("enumerateSources failed\n");
		return NULL;
	}

	UINT32 index;
	if (!getMFActivateIdxByName(ppDevices, count, devName, &index)) {
		printf("No device with friendly name %s found\n", devName.c_str());
		releaseIMFActivates(ppDevices, count);
		return NULL;
	}

	std::string devId = getDeviceSymbolicLink(ppDevices[index]);
	if (devId == "") {
		printf("No device ID with name %s found\n", devName.c_str());
		releaseIMFActivates(ppDevices, count);
		return NULL;
	}
	unsigned short vid, pid;
	std::string camName, camSerial;
	if (!getPanaCastVidPidNameSerial(ppDevices[index], vid, pid, camName, camSerial)){
		printf("Dev %s failed to get vid, pid, name or serial\n", devName.c_str());
		releaseIMFActivates(ppDevices, count);
		return NULL;
	}

	IMFMediaSource *pSource = getMFMediaSource(ppDevices[index], devName, devId);
	if (pSource == NULL)
	{
		printf("Failed to get Media Source for the device %s\n", devName.c_str());
		releaseIMFActivates(ppDevices, count);
		return NULL;
	}
	releaseIMFActivates(ppDevices, count);

	DWORD dwNodeId;
	IKsControl* pControl = NULL;
	bool r = findAndOpenEUControl(pSource, guidEU, &dwNodeId, &pControl);
	if (!r) {
		printf("failed to find or open EU\n");
		shutDownMediaSource(devId);
		SafeRelease(&pControl);
		return NULL;
	}

	EUHandle* rh = new EUHandle();
	if (!rh) {
		printf("no memory for handle\n");
		shutDownMediaSource(devId);
		SafeRelease(&pControl);
		return NULL;
	}

	//set up the handle and return it
	rh->name = camName;
	rh->serial = camSerial;
	rh->_devIdStr = devId;
	rh->vid = vid;
	rh->pid = pid;

	rh->guidEU = guidEU;
	rh->nodeId = dwNodeId;
	rh->pKsControl = pControl;
	rh->referenceCounter = 1;

	//keep track of the devId opened, in case its MFSource has not been shutdown, we shutdown those in the destructor
	addToResourceList(rh->_devIdStr);
	return rh;
}

void UVCExtensionUnitManager::closeExtensionUnit(EUHandle** pHandle, bool shutDownSource)
{
	if (!(*pHandle)) return;
	if (shutDownSource) {
		shutDownMediaSource((*pHandle)->_devIdStr);
	}
	if ((*pHandle)->referenceCounter.fetch_sub(1, std::memory_order::memory_order_relaxed) == 1) {
		//printf("releasing EUHandle...\n");
		SafeRelease(&((*pHandle)->pKsControl));
		delete *pHandle;
	}
	*pHandle = NULL;
}
void UVCExtensionUnitManager::releaseIMFActivates(IMFActivate **ppDevices, UINT32 count)
{
	for (UINT32 i = 0; i < count; i++) {
		SafeRelease(&ppDevices[i]);
	}
	CoTaskMemFree(ppDevices);
}

bool UVCExtensionUnitManager::enumerateSources(IMFActivate** &ppDevices, UINT32 &count)
{
	ppDevices = NULL;
	count = 0;
	IMFAttributes *pAttributes = NULL;

	HRESULT hr = MFCreateAttributes(&pAttributes, 1);
	if (FAILED(hr))
	{
		printf("MFCreateAttributes failed\n");
		return false;
	}

	hr = pAttributes->SetGUID(MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE,
		MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE_VIDCAP_GUID); //ask for video capture devices
	if (FAILED(hr))
	{
		printf("SetGUID() failed\n");
		SafeRelease(&pAttributes);
		return false;
	}

	//Enumerate all uvc devices.
	hr = MFEnumDeviceSources(pAttributes, &ppDevices, &count);
	if (FAILED(hr))
	{
		printf("MFEnumDeviceSources() failed\n");
		SafeRelease(&pAttributes);
		return false;
	}
	if (count == 0) {
		//printf("No Video device found\n");
		SafeRelease(&pAttributes);
		return false;
	}
	SafeRelease(&pAttributes);
	return true;
}

bool UVCExtensionUnitManager::getMFActivateIdxByName(IMFActivate **ppDevices, UINT32 count, std::string friendlyname, UINT32 *pIndex)
{
	bool found = false;
	for (UINT32 i = 0; i < count; i++) {
		IMFActivate *device = ppDevices[i];
		std::string name_;
		if (!getMFActivateName(device, name_)) continue;
		//printf("checking the uvc device %s\n", name_.c_str());
		if (name_ == friendlyname) {
			//printf("found our device: %s\n", name_.c_str());
			*pIndex = i;
			found = true;
			break;
		}
	}
	return found;
}

bool UVCExtensionUnitManager::getMFActivateName(IMFActivate *pDevice, std::string &name)
{
	name = "";
	std::string serial = "";
	if (!getPanaCastNameAndSerial(pDevice, name, serial)) {
		return false;
	}
	name = name + "__" + serial; //also appending serial number to the name
	return true;
}

bool UVCExtensionUnitManager::getPanaCastVidPidNameSerial(IMFActivate *pDevice, unsigned short &vid, unsigned short &pid, std::string &name, std::string &serial)
{
	name = "";
	serial = "";
	if (!pDevice) {
		printf("getPanaCastNameAndSerial: invalid device pointer\n");
		return false;
	}
	UINT32 w_name_size;
	wchar_t * w_name;
	HRESULT hr = pDevice->GetAllocatedString(
		MF_DEVSOURCE_ATTRIBUTE_FRIENDLY_NAME,
		&w_name,
		&w_name_size
		);
	if (!SUCCEEDED(hr)) {
		printf("getPanaCastNameAndSerial: GetAllocatedString failed\n");
		return false;
	}
	name = SysWideToUTF8(std::wstring(w_name, w_name_size));
	CoTaskMemFree(w_name);

	std::string vidStr;
	std::string pidStr;
	if (!getVidPidFromDevicePath(getDeviceSymbolicLink(pDevice), vidStr, pidStr)) return false; //ignore camera without vid & pid


	//returned vid & pid are in lower case
	//ignore non Alita vid & pid
	if (vidStr != ALTIA_VENDOR_ID && vidStr != JABRA_PYTHON_VID) return false;
	if (vidStr == ALTIA_VENDOR_ID) {
		if ((pidStr != P2_VIDEO_AUDIO_PID) &&
			(pidStr != P2_VIDEO_ONLY_PID) &&
			(pidStr != P2s_VIDEO_AUDIO_PID) &&
			(pidStr != P2s_VIDEO_ONLY_PID) &&
			(pidStr != P3_VIDEO_AUDIO_PID) &&
			(pidStr != P3_VIDEO_ONLY_PID) &&
			(pidStr != P3s_VIDEO_AUDIO_PID) &&
			(pidStr != P3s_VIDEO_ONLY_PID) &&
			(pidStr != PANACAST_MISSION_PID)) {
			printf("Altia vendor id %s with invalid pid %s\n", vidStr.c_str(), pidStr.c_str());
			return false;
		}
	}
	else {
		//We accept all PIDs for the JABRA_PYTHON_VID for now
	}

	//for python device sku with dual cameras
	//since there can be two devices with the same vid pid
	//1. Jabra PanaCast 50
	//2. Jabra Whiteboard
	//we need to filter by friendly name
	if (vidStr == JABRA_PYTHON_VID && pidStr == JABRA_PYTHON_PID_2) {
		std::string tmp = name;
		transform(tmp.begin(), tmp.end(), tmp.begin(), ::tolower);
		if (tmp.compare("jabra panacast 50") != 0)
			return false;
	}


	//convert vid pid string to unsigned short
	vid = std::stoi(vidStr, 0, 16);
	pid = std::stoi(pidStr, 0, 16);

	if (!getPanaCastSerialNumber(pDevice, serial)) {
		printf("failed to get serial number for PanaCast device\n");
		return false;
	}
	return true;
}

bool UVCExtensionUnitManager::getPanaCastNameAndSerial(IMFActivate *pDevice, std::string &name, std::string &serial)
{
	unsigned short _vid, _pid;
	return getPanaCastVidPidNameSerial(pDevice, _vid, _pid, name, serial);
}

bool UVCExtensionUnitManager::getPanaCastSerialNumber(IMFActivate *pDevice, std::string &serial) {
	serial = "";
	UINT32 id_size;
	wchar_t * id = NULL;

	HDEVINFO info = SetupDiCreateDeviceInfoList(NULL, NULL);
	if (info == INVALID_HANDLE_VALUE) {
		printf("SetupDiCreateDeviceInfoList failed\n");
		return false;
	}

	HRESULT hr = pDevice->GetAllocatedString(
		MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE_VIDCAP_SYMBOLIC_LINK, &id,
		&id_size);
	if (FAILED(hr)) {
		printf("GetAllocatedString failed with VIDCAP symbolic link\n");
		SetupDiDestroyDeviceInfoList(info);
		return false;
	}

	SP_DEVICE_INTERFACE_DATA ifdata = { sizeof(SP_DEVICE_INTERFACE_DATA) };
	if (!SetupDiOpenDeviceInterface(info, id, 0, &ifdata)) {
		printf("SetupDiOpenDeviceInterface failed\n");
		CoTaskMemFree(id);
		SetupDiDestroyDeviceInfoList(info);
		return false;
	}
	CoTaskMemFree(id);

	SP_DEVINFO_DATA did = { sizeof(SP_DEVINFO_DATA) };
	if (!SetupDiGetDeviceInterfaceDetail(info, &ifdata, NULL, 0, NULL, &did)) {
		DWORD errNo = GetLastError();
		if (errNo != ERROR_INSUFFICIENT_BUFFER) {
			std::string errStr = GetErrorAsString(errNo);
			printf("SetupDiGetDeviceInterfaceDetail failed. error = %s\n", errStr.c_str());
			SetupDiDestroyDeviceInfoList(info);
			return false;
		}
	}

	wchar_t pname[256];
	memset(pname, 0, sizeof(pname));
	DEVPROPTYPE ptype;
	if (!SetupDiGetDeviceProperty(info, &did, &DEVPKEY_Device_Parent, &ptype, (PBYTE)pname, sizeof(pname), NULL, 0)) {
		printf("SetupDiGetDeviceProperty failed\n");
		SetupDiDestroyDeviceInfoList(info);
		return false;
	}
	SetupDiDestroyDeviceInfoList(info);

	pname[255] = 0;
	std::wstring pWStr = std::wstring(pname);
	std::string pStr(pWStr.begin(), pWStr.end()); //pStr will be a string like "USB\VID_2B93&PID_0002\P00501538194"

	size_t pos = pStr.find_last_of("\\");
	if (pos == std::string::npos) {
		printf("failed to find '\\' at pname = %s\n", pStr.c_str());
		return false;
	}
	serial = pStr.substr(pos + 1);
	return true;
}

bool UVCExtensionUnitManager::findAndOpenEUControl(IMFMediaSource *pSource, GUID devGuid, DWORD *pNodeId, IKsControl **ppControl)
{
	if (!pSource) return false;

	IKsTopologyInfo * pKsTopologyInfo = NULL;
	HRESULT hr = pSource->QueryInterface(IID_PPV_ARGS(&pKsTopologyInfo));
	
	if (!SUCCEEDED(hr))
	{
		printf("Unable to obtain IKsTopologyInfo %x\n", hr);
		return false;
	}

	bool ret = true;
	hr = findExtensionNode(pKsTopologyInfo, devGuid, pNodeId);
	if (FAILED(hr))
	{
		ret = false;
		printf("Unable to find extension node : %x\n", hr);
	}
	else {
		//printf("Found Node ID = %u\n", *pNodeId);
		//open the pKsControl for the EU
		hr = pKsTopologyInfo->CreateNodeInstance(*pNodeId, IID_PPV_ARGS(ppControl));
		if (FAILED(hr))
		{
			printf("Unable to create extension node instance : %x\n", hr);
			ret = false;
		}
	}
	SafeRelease(&pKsTopologyInfo);
	return ret;
}

HRESULT UVCExtensionUnitManager::findExtensionNode(IKsTopologyInfo * pKsTopologyInfo, GUID devGuid, DWORD* pNodeId)
{
	HRESULT hr = E_FAIL;
	DWORD dwNumNodes = 0;
	GUID guidNodeType;
	ULONG ulBytesReturned = 0;
	KSP_NODE ExtensionProp;

	if (!pKsTopologyInfo || !pNodeId)
		return E_POINTER;

	// Retrieve the number of nodes
	hr = pKsTopologyInfo->get_NumNodes(&dwNumNodes);
	if (!SUCCEEDED(hr))
		return hr;
	if (dwNumNodes == 0) {
		printf("Error no nodes\n");
		return E_FAIL;
	}

	// Find the extension unit node that corresponds to the given GUID
	//printf("found # nodes = %u\n", dwNumNodes);
	for (unsigned int i = 0; i < dwNumNodes; i++)
	{
		hr = E_FAIL;
		pKsTopologyInfo->get_NodeType(i, &guidNodeType);
		if (IsEqualGUID(guidNodeType, KSNODETYPE_DEV_SPECIFIC))
		{
			IKsControl *pKsControl = NULL;
			hr = pKsTopologyInfo->CreateNodeInstance(i, IID_PPV_ARGS(&pKsControl));
			if (SUCCEEDED(hr))
			{
				ExtensionProp.Property.Set = devGuid;
				ExtensionProp.Property.Id = 0;
				ExtensionProp.Property.Flags = KSPROPERTY_TYPE_SETSUPPORT | KSPROPERTY_TYPE_TOPOLOGY;
				ExtensionProp.NodeId = i;
				ExtensionProp.Reserved = 0;
				hr = pKsControl->KsProperty((PKSPROPERTY)&ExtensionProp, sizeof(ExtensionProp), NULL, 0, &ulBytesReturned);
				pKsControl->Release();
				if (SUCCEEDED(hr))
				{
					*pNodeId = i;
					break;
				}
			}
		}
	}
	return hr;
}

HRESULT UVCExtensionUnitManager::getProperty(EUHandle* handle, ULONG propertyID, BYTE *value, ULONG valueSize)
{
	HRESULT hr = E_FAIL;
	ULONG ulBytesReturned = 0;

	if (!handle) {
		printf("invalid handle\n");
		return E_HANDLE;
	}
	if (!handle->pKsControl) {
		printf("invalid control ptr\n");
		return E_POINTER;
	}

	hr = KsPropertyProc(handle, handle->guidEU, propertyID, true, handle->nodeId, value, valueSize, &ulBytesReturned);

	if (ulBytesReturned != valueSize) {
		printf("byte returned %lu != value size %lu\n", ulBytesReturned, valueSize);
		hr = E_FAIL;
	}

	return hr;
}

HRESULT UVCExtensionUnitManager::setProperty(EUHandle* handle, ULONG propertyID, BYTE *value, ULONG valueSize)
{
	HRESULT hr = E_FAIL;
	ULONG ulBytesReturned = 0;

	if (!handle) {
		printf("invalid handle\n");
		return E_HANDLE;
	}
	if (!handle->pKsControl) {
		printf("invalid control ptr\n");
		return E_POINTER;
	}

	hr = KsPropertyProc(handle, handle->guidEU, propertyID, false, handle->nodeId, value, valueSize, &ulBytesReturned);

	return hr;
}

HRESULT UVCExtensionUnitManager::getPropertyInfo(EUHandle* handle, ULONG propertyID, EU_PROPERTY_INFO *pInfo)
{
	if (!pInfo) {
		printf("invalid EU_PROPERTY_INFO pointer\n");
		return E_POINTER;
	}

	KSPROPERTY_MEMBERSHEADER mh;
	BYTE* members = NULL;
	HRESULT hr;
	bool getOpSupported = false;
	bool setOpSupported = false;

	//first, get the default value, and the length of the default value is the length of this property
	hr = getKSPropDesc(handle, propertyID, KSPROPERTY_TYPE_DEFAULTVALUES, &mh, &members, &getOpSupported, &setOpSupported);
	if (FAILED(hr)) {
		printf("Failed to get KS prop desc for default value\n");
		return hr;
	}
	if (mh.MembersFlags != KSPROPERTY_MEMBER_VALUES) {
		printf("ks prop default value do not return member flag KSPROPERTY_MEMBER_VALUES\n");
		free(members);
		return E_FAIL;
	}
	if (mh.MembersCount != 1) {
		printf("ks prop default value return more than 1 members, # member = %u\n", mh.MembersCount);
		free(members);
		return E_FAIL;
	}
	ULONG propLen = mh.MembersSize;
	if (!mallocPropInfo(pInfo, propLen)) { //this will set pInfo->lenBytes
		printf("failed to allocate memorgy for EU_PROPERTY_INFO, prop len = %u\n", propLen);
		free(members);
		return E_FAIL;
	}
	memcpy(pInfo->defVal, members, propLen); //copy default value
	free(members);
	members = NULL;

	//second, get property range
	hr = getKSPropDesc(handle, propertyID, KSPROPERTY_TYPE_BASICSUPPORT, &mh, &members, &getOpSupported, &setOpSupported);
	if (FAILED(hr)) {
		printf("Failed to get KS prop desc for basic support value\n");
		freePropertyInfo(pInfo);
		return hr;
	}
	if (mh.MembersFlags != KSPROPERTY_MEMBER_RANGES) {
		printf("ks prop basic support value do not return member flag KSPROPERTY_MEMBER_RANGES\n");
		free(members);
		freePropertyInfo(pInfo);
		return E_FAIL;
	}
	if (mh.MembersCount != 1) {
		printf("ks prop basic support value do not return 1 members, # member = %u\n", mh.MembersCount);
		free(members);
		freePropertyInfo(pInfo);
		return E_FAIL;
	}
	if (mh.MembersSize != propLen * 3) {
		printf("ks prop basic support value member size %u != prop len %u x 3\n", mh.MembersSize, propLen);
		free(members);
		freePropertyInfo(pInfo);
		return E_FAIL;
	}

	//ksProperty() now returned 1 member with size 3 * "propLen": step, min, max
	memcpy(pInfo->stepVal, members, propLen);
	memcpy(pInfo->minVal, members + propLen, propLen);
	memcpy(pInfo->maxVal, members + (2 * propLen), propLen);
	pInfo->getSupported = getOpSupported;
	pInfo->setSupported = setOpSupported;

	free(members);
	return NOERROR;
}

HRESULT UVCExtensionUnitManager::getKSPropDesc(EUHandle* handle, ULONG propertyID, ULONG propFlag, KSPROPERTY_MEMBERSHEADER *pMemberHeader, BYTE** pMembers, bool *pGetSupported, bool *pSetSupported)
{
	HRESULT hr = E_FAIL;
	KSP_NODE ExtensionProp;
	KSPROPERTY_DESCRIPTION desc;
	ULONG ulBytesReturned = 0;

	if (!handle) {
		printf("invalid handle\n");
		return E_HANDLE;
	}
	if (!handle->pKsControl) {
		printf("invalid control ptr\n");
		return E_POINTER;
	}

	ExtensionProp.Property.Set = handle->guidEU;
	ExtensionProp.Property.Id = propertyID;
	ExtensionProp.Property.Flags = propFlag | KSPROPERTY_TYPE_TOPOLOGY;
	ExtensionProp.NodeId = handle->nodeId;
	hr = handle->pKsControl->KsProperty(
		(PKSPROPERTY)&ExtensionProp,
		sizeof(ExtensionProp),
		(PVOID)&desc,
		sizeof(desc),
		&ulBytesReturned
		);
	if (FAILED(hr)) {
		printf("failed to get ks property %lu\n", propFlag);
		return hr;
	}
	if (ulBytesReturned != sizeof(desc)) {
		printf("ksProperty bytes returned %lu != size of ks desc %u\n", ulBytesReturned, sizeof(desc));
		return E_FAIL;
	}

	const ULONG descSize = desc.DescriptionSize;
	BYTE * fulldesc = (BYTE*)malloc(descSize);
	if (!fulldesc){
		printf("no memory for full description\n");
		return E_FAIL;
	}

	hr = handle->pKsControl->KsProperty(
		(PKSPROPERTY)&ExtensionProp,
		sizeof(ExtensionProp),
		(PVOID)fulldesc,
		descSize,
		&ulBytesReturned
		);
	if (FAILED(hr)) {
		printf("failed to get desc with full size %lu\n", descSize);
		free(fulldesc);
		return hr;
	}
	if (ulBytesReturned != descSize) {
		printf("KS bytes returned %lu != full size %lu\n", ulBytesReturned, descSize);
		free(fulldesc);
		return E_FAIL;
	}
	memcpy(&desc, fulldesc, sizeof(desc));
	*pGetSupported = (desc.AccessFlags & KSPROPERTY_TYPE_GET) != 0;
	*pSetSupported = (desc.AccessFlags & KSPROPERTY_TYPE_SET) != 0;

	if (desc.MembersListCount != 1) {
		printf("Not supported proptery info that has more than 1 KSPROPERTY_MEMBERSHEADER, # of member = %lu\n", desc.MembersListCount);
		free(fulldesc);
		return E_FAIL;
	}

	BYTE* memberHeader = fulldesc + sizeof(KSPROPERTY_DESCRIPTION);
	memcpy(pMemberHeader, memberHeader, sizeof(KSPROPERTY_MEMBERSHEADER));
	if (pMemberHeader->MembersCount == 0 || pMemberHeader->MembersSize == 0) {
		printf("invalid member count %u or size %u\n", pMemberHeader->MembersCount, pMemberHeader->MembersSize);
		free(fulldesc);
		return E_FAIL;
	}

	const ULONG totalSize = pMemberHeader->MembersSize * pMemberHeader->MembersCount;
	if (sizeof(KSPROPERTY_DESCRIPTION) + sizeof(KSPROPERTY_MEMBERSHEADER) + totalSize != desc.DescriptionSize) {
		printf("invalid # of bytes returned\n");
		free(fulldesc);
		return E_FAIL;
	}
	BYTE* m = memberHeader + sizeof(KSPROPERTY_MEMBERSHEADER);
	*pMembers = (BYTE*)malloc(totalSize);
	if (!(*pMembers)) {
		printf("no memory for members\n");
		free(fulldesc);
		return E_FAIL;
	}
	memcpy(*pMembers, m, totalSize);
	free(fulldesc);
	return NOERROR;
}

void UVCExtensionUnitManager::freePropertyInfo(EU_PROPERTY_INFO *pInfo)
{
	if (pInfo) {
		if (pInfo->defVal) free(pInfo->defVal); //check mallocPropInfo()
		memset(pInfo, 0, sizeof(EU_PROPERTY_INFO));
	}
}

bool UVCExtensionUnitManager::mallocPropInfo(EU_PROPERTY_INFO* pInfo, ULONG len)
{
	memset(pInfo, 0, sizeof(EU_PROPERTY_INFO));
	pInfo->defVal = (BYTE*)malloc(len * 4); //default, min, max, step, each with "len" # of bytes
	if (!pInfo->defVal) {
		printf("no memory for property info\n");
		return false;
	}
	pInfo->minVal = pInfo->defVal + len;
	pInfo->maxVal = pInfo->defVal + (2*len);
	pInfo->stepVal = pInfo->defVal + (3*len);
	pInfo->lenBytes = len;
	return true;
}

IMFMediaSource* UVCExtensionUnitManager::getMFMediaSource(IMFActivate* device, std::string devName, std::string devId)
{
	//Since IMFMediaSource::ActivateObject() has memory leak (even after calling IMFMediaSource::ShutDown() on the object)
	//we want to limit the number of calls to ActivateObject()
	//we cache the IMFMediaSource object for each device, so that it can be reused.
	//Also, this can eliminate the needs of calling IMFMediaSource::ShutDown() in closeExtensionUnit()
	//because ShutDown() can take up to 250ms
	IMFMediaSource *pSource = NULL;

	tableLock.Lock();

	auto search = mediaSourceTable.find(devName);
	if (search != mediaSourceTable.end()) {
		pSource = search->second;
	}

	if (pSource) {

		tableLock.Unlock();
		return pSource;
	}

	//Create the MF source object.
	printf("creating new MF source for dev %s\n", devName.c_str());
	HRESULT hr = device->ActivateObject(IID_PPV_ARGS(&pSource));
	if (FAILED(hr) || pSource == NULL)
	{
		printf("ActivateObject() failed. Did CoInitialize(NULL) called at the start of this thread?\n");

		tableLock.Unlock();
		return NULL;
	}

	//cache media source & its id
	mediaSourceTable[devName] = pSource;
	//when deal with devID, always uses lower case by convention
	std::transform(devId.begin(), devId.end(), devId.begin(), ::tolower);
	devNameTable[devId] = devName;

	tableLock.Unlock();
	return pSource;
}

//This will be called when device is lost
void UVCExtensionUnitManager::shutDownMediaSource(std::string devId)
{
	//when deal with devID, always uses lower case by convention
	std::transform(devId.begin(), devId.end(), devId.begin(), ::tolower);

	tableLock.Lock();
	auto s = devNameTable.find(devId);
	if (s != devNameTable.end()) {
		auto search = mediaSourceTable.find(s->second);
		if (search != mediaSourceTable.end()) {

			std::promise<void> readyProimse;
			auto ready = readyProimse.get_future();
			bool * isThreadExited = (bool*)malloc(sizeof(bool));
			CSLock *csLock = new CSLock();

			if (isThreadExited && csLock && search->second) {
				*isThreadExited = false;
				std::thread th(shutdownMFSourceThreadProc, search->second, csLock, isThreadExited, std::ref(readyProimse));
				bool isTimeOut = true;
#define SHUTDOWN_TIMEOUT_MS 1000
				if (ready.wait_for(std::chrono::milliseconds(SHUTDOWN_TIMEOUT_MS)) == std::future_status::ready) isTimeOut = false;
				
				csLock->Lock();
				*isThreadExited = true;
				csLock->Unlock();
				
				if (!isTimeOut) {
					th.join();
				}
				else {
					printf("shutDownMediaSource: shutdown timeout in %d ms !!!\n", SHUTDOWN_TIMEOUT_MS);
					th.detach();
				}
			}
			else {
				printf("shutDownMediaSource: we have no memory or invalid ptr %p !!!\n", search->second);

				//we cannot call ShutDown() as it can be blocked forever
				SafeRelease(&(search->second));
				if (csLock) delete csLock;
				if (isThreadExited) delete isThreadExited;
			}

			mediaSourceTable.erase(search);
		}
		devNameTable.erase(s);
	}
	tableLock.Unlock();
}

std::string UVCExtensionUnitManager::getDeviceSymbolicLink(IMFActivate* device)
{
	UINT32 wid_size;
	wchar_t * wid = NULL;
	HRESULT hr = device->GetAllocatedString(MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE_VIDCAP_SYMBOLIC_LINK, &wid, &wid_size);
	if (FAILED(hr) || wid == NULL) {
		printf("GetAllocatedString failed with VIDCAP symbolic link\n");
		return "";
	}
	std::string link = SysWideToUTF8(std::wstring(wid, wid_size));
	CoTaskMemFree(wid);
	return link;
}

std::string UVCExtensionUnitManager::toLower(const std::string& s)
{
	std::string result = "";
	std::locale loc;

	for (unsigned int i = 0; i < s.length(); ++i) {
		result += std::tolower(s.at(i), loc);
	}
	return result;
}

bool UVCExtensionUnitManager::getStringAfter(std::string deviceId, std::string type, size_t len, std::string& returnId)
{
	std::string ltype = toLower(type);
	std::string ldevId = toLower(deviceId);
	int idx = ldevId.find(ltype);
	if (idx == std::string::npos) {
		//printf("getStringAfter: no \"%s\" id in matching device %s\n", type.c_str(), deviceId.c_str());
		return false;
	}
	if (ldevId.length() < (idx + type.length() + len)) {
		//printf("getStringAfter: no \"%s\" id in matching device %s\n", type.c_str(), deviceId.c_str());
		return false;
	}
	returnId = ldevId.substr(idx + type.length(), len);
	return true;
}

bool UVCExtensionUnitManager::getVidPidFromDevicePath(std::string deviceId, std::string& vendor_id, std::string& product_id)
{
#define VIDPID_LEN 4
	if (deviceId == "") return false;
	if (!getStringAfter(deviceId, "vid_", VIDPID_LEN, vendor_id)) return false;
	if (!getStringAfter(deviceId, "pid_", VIDPID_LEN, product_id)) return false;
	return true;
}
#endif /*_WIN32*/

void UVCExtensionUnitManager::KsPropertyThreadProc(bool* isThreadExitedPtr, void* csLock, std::promise<HRESULT> &resultReady, std::promise<void> &setupReady,
	EUHandle *handle, GUID kspNodePropSet, ULONG kspNodePropId, bool isGet, ULONG kspNodeId,
	PVOID pPropData, ULONG pPropDataLen, ULONG* bytesReturn)
{
	//we need to wait for the thread that started us to finish, then we will free isThreadExitedPtr & csLock, and close handle if its reference count drop to 0
	//before we set the "setupReady" promise, local variables "resultReady", "setupReady", "pPropData", "bytesReturn" will not go out of scope.

	//first, do some sanity checks
	if (!isThreadExitedPtr || !csLock ||!handle || !handle->pKsControl ||!pPropData ||!bytesReturn) {
		resultReady.set_value(E_POINTER);
		setupReady.set_value();
		ksPropThreadWaitAndCleanup(isThreadExitedPtr, csLock, handle);
		return;
	}
	BYTE *buf = (BYTE*)malloc(pPropDataLen);
	if (!buf) {
		printf("KsPropertyThreadProc: exit as no memory\n");
		resultReady.set_value(E_OUTOFMEMORY);
		setupReady.set_value();
		ksPropThreadWaitAndCleanup(isThreadExitedPtr, csLock, handle);
		return;
	}

	HRESULT hr = NOERROR;

	//set up the variables
	*bytesReturn = 0;
	if (!isGet) memcpy(buf, pPropData, pPropDataLen); //if this is set property, we copy the data to our local buffer

	
	ULONG ulBytesReturned = 0;
	KSP_NODE ExtensionProp;
	ExtensionProp.Property.Set = kspNodePropSet;
	ExtensionProp.Property.Id = kspNodePropId;
	ExtensionProp.Property.Flags = (isGet ? KSPROPERTY_TYPE_GET : KSPROPERTY_TYPE_SET) | KSPROPERTY_TYPE_TOPOLOGY;
	ExtensionProp.NodeId = kspNodeId;


	//set up is done, signal the other thread
	setupReady.set_value();

	//the KsProperty() API is wrapper of some IOCTL call to the driver, and in some old version of the usbvideo.sys, it can be blocked forever when device got unplugged.
	hr = handle->pKsControl->KsProperty((PKSPROPERTY)&ExtensionProp, sizeof(ExtensionProp), buf, pPropDataLen, &ulBytesReturned);

	//now we are done, we need to check if the other thread has already exited, and if so, all local variables will not be valid
	((CSLock*)csLock)->Lock();
	if (!(*isThreadExitedPtr)) { //other thread has not exited yet...
		*bytesReturn = ulBytesReturned;
		resultReady.set_value(hr);

		//if this is get property, we copy the data from local buffer to output buffer
		if (SUCCEEDED(hr)) {
			if (isGet && ulBytesReturned == pPropDataLen) memcpy(pPropData, buf, pPropDataLen);
		}
	}
	((CSLock*)csLock)->Unlock();

	//we are finished, wait and clean up
	ksPropThreadWaitAndCleanup(isThreadExitedPtr, csLock, handle);
	free(buf);
	return;
}

void UVCExtensionUnitManager::ksPropThreadWaitAndCleanup(bool * isThreadExitedPtr, void * csLock, EUHandle *handle)
{
	//wait for the threadExitedPtr = true
	while (true) {
		((CSLock*)csLock)->Lock();
		if (*isThreadExitedPtr) {
			free(isThreadExitedPtr);
			isThreadExitedPtr = NULL;
		}
		((CSLock*)csLock)->Unlock();
		if (isThreadExitedPtr == NULL) break;
		Sleep(10);
	}
	
	//free resouce
	delete (CSLock*)csLock;
	UVCExtensionUnitManager::closeExtensionUnit(&handle, false); //close the handle only if the reference count is at 0
	return;
}

HRESULT UVCExtensionUnitManager::KsPropertyProc(EUHandle *handle, GUID kspNodePropSet, ULONG kspNodePropId, bool isGet, ULONG kspNodeId,
	PVOID pPropData, ULONG pPropDataLen, ULONG* bytesReturn)
{
	if (!handle || !handle->pKsControl) return E_POINTER;

	tableLock.Lock();
	auto s = devNameTable.find(handle->_devIdStr);
	if (s == devNameTable.end() || mediaSourceTable.find(s->second) == mediaSourceTable.end()) {
		tableLock.Unlock();
		printf("Invalid handle\n");
		return E_FAIL;
	}
	tableLock.Unlock();

#ifdef NO_KSPROP_WRAPPER
	KSP_NODE ExtensionProp;
	ExtensionProp.Property.Set = kspNodePropSet;
	ExtensionProp.Property.Id = kspNodePropId;
	ExtensionProp.Property.Flags = (isGet ? KSPROPERTY_TYPE_GET : KSPROPERTY_TYPE_SET) | KSPROPERTY_TYPE_TOPOLOGY;
	ExtensionProp.NodeId = kspNodeId;
	//the KsProperty() API is wrapper of some IOCTL call to the driver, and in some old version of the usbvideo.sys, it can be blocked forever when device got unplugged.
	return handle->pKsControl->KsProperty((PKSPROPERTY)&ExtensionProp, sizeof(ExtensionProp), pPropData, pPropDataLen, bytesReturn);
#endif

#define KS_PROPERTY_TIMEOUT_MS 5000 //vendor command that returns FPGA checksum can take ~ 4 secs
	std::promise<HRESULT> resultPromise;
	std::promise<void> setupPromise;
	auto isResultReady = resultPromise.get_future();
	auto isSetupReady = setupPromise.get_future();

	bool * isThreadExitedPtr = (bool*)malloc(sizeof(bool)); //thread will free me when it finished
	if (!isThreadExitedPtr) return E_OUTOFMEMORY;
	*isThreadExitedPtr = false;

	CSLock *csLock = new CSLock();
	if (!csLock) {
		free(isThreadExitedPtr);
		return E_OUTOFMEMORY;
	}

	//wow... in some legacy Windows OS (Win 7 & Win 8), the behavior of the API IKsControl::KsProperty is very buggy
	//it could be blocked forever if the device got unplugged.
	//So we run it in a seperate thread, and if the KS property thread does not return in some time duration,
	//we just detach the thread (this will cause some resource leak but it is better than causing the application to be freeze)
	//and hopefully it rare for user to do this kind of plug & unplug frequently...
	handle->referenceCounter.fetch_add(1, std::memory_order::memory_order_relaxed); //increment the reference count for the handle so that as the object is now also owned by the thread
	std::thread th(UVCExtensionUnitManager::KsPropertyThreadProc, isThreadExitedPtr, csLock, std::ref(resultPromise),  std::ref(setupPromise),
		handle, kspNodePropSet, kspNodePropId, isGet, kspNodeId, pPropData, pPropDataLen, bytesReturn);
	
	//wait for other thread to setup first
	isSetupReady.get();

	//wait for the other thread to finish or timeout
	HRESULT hr = E_ABORT;
	bool timeOut = true;
	if (isResultReady.wait_for(std::chrono::milliseconds(KS_PROPERTY_TIMEOUT_MS)) == std::future_status::ready) {
		hr = isResultReady.get();
		timeOut = false;
	}

	//signal the thread that runs the KsProperty() API that,
	//we are exiting, and so, the local variables will go out of scope
	csLock->Lock();
	*isThreadExitedPtr = true; //the other thread will wait for this variable set to true first
	csLock->Unlock();

	if (!timeOut) {
		th.join();
	}
	else {
		printf("Warning: KsProperty Timeout at %d ms, detaching the thread...\n", KS_PROPERTY_TIMEOUT_MS);
		th.detach();
	}
	return hr;
}

void UVCExtensionUnitManager::shutdownMFSourceThreadProc(IMFMediaSource * source, void* csLock, bool * isThreadExitedPtr, std::promise<void>& ready)
{
	//Note: Even with Shutdown() called, there is still small memory leak.
	//In our case, this memory leak will happen only when device is unplugged.
	//Assume user won't frequently unplug/plug & reboot the device, so this is OK.

	//Note: during device unplug, Shutdown() can be blocked forever, so we are running this in a thread
	//otherwise, application may be blocked forever.
	source->Shutdown();
	SafeRelease(&source);

	((CSLock*)csLock)->Lock();
	if (!(*isThreadExitedPtr)) { //other thread has not exited yet...
		ready.set_value();
	}
	((CSLock*)csLock)->Unlock();

	shutdownMFSourceThreadWaitAndCleanup(csLock, isThreadExitedPtr);
	return;
}

void UVCExtensionUnitManager::shutdownMFSourceThreadWaitAndCleanup(void * csLock, bool * isThreadExitedPtr)
{
	//wait for the threadExitedPtr = true
	while (true) {
		((CSLock*)csLock)->Lock();
		if (*isThreadExitedPtr) {
			free(isThreadExitedPtr);
			isThreadExitedPtr = NULL;
		}
		((CSLock*)csLock)->Unlock();
		if (isThreadExitedPtr == NULL) break;
		Sleep(10);
	}

	//free resouce
	delete (CSLock*)csLock;
	return;
}

void UVCExtensionUnitManager::getUnusedWndName(std::string &cName, std::string &wName)
{
	DWORD now = GetTickCount();
	int nameIdx = rand();

	std::string wBaseName = "XUMgr_Wnd_Name";
	std::string cBaseName = "XUMgr_Class_Name";
	wName = wBaseName + std::to_string(now) + std::string("_") + std::to_string(nameIdx);
	cName = cBaseName + std::to_string(now) + std::string("_") + std::to_string(nameIdx);
}
