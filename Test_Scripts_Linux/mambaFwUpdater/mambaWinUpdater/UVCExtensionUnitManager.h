#ifndef __UVC_EXTENSION_UNIT_MGR_H__
#define __UVC_EXTENSION_UNIT_MGR_H__

#ifdef _WIN32

#include <vidcap.h>
#include <mfapi.h>
#include <mfidl.h>
#include <mferror.h>
#include <Ks.h>
#include <Ksproxy.h>
#include <KsMedia.h>
#include <string>
#include <vector>
#include <map>
#include <future>
#include <atomic>

typedef struct {
	GUID guidEU;
	DWORD nodeId;
	IKsControl *pKsControl;
	std::atomic<int> referenceCounter;
	std::string _devIdStr;

	//additional device's info
	unsigned short vid;
	unsigned short pid;
	std::string serial;
	std::string name;

} EUHandle;

typedef struct {
	BYTE * defVal; //default value, "lenBytes" # of bytes
	BYTE * minVal; //min value, "lenBytes" # of bytes
	BYTE * maxVal; //max value, "lenBytes" # of bytes
	BYTE * stepVal; //step value (resolution), "lenBytes" # of bytes
	bool getSupported; //whether get current is supported
	bool setSupported; //whether set current is supported
	ULONG lenBytes; //# of bytes for this property
} EU_PROPERTY_INFO;

class UVCExtensionUnitManager {
public:
	UVCExtensionUnitManager();
	virtual ~UVCExtensionUnitManager();
	bool enumeratePanaCastDeviceNames(std::vector<std::string> &devNames); //return a list of current connected PanaCast device names
	EUHandle* openExtensionUnit(GUID guidEU, std::string devName); //open a PanaCast device XU by its name
	
	static void closeExtensionUnit(EUHandle** pHandle, bool shutDownSource=false);

	//On success, return the info of the EU property. Needed to free by freePropertyInfo() 
	static HRESULT getPropertyInfo(EUHandle* handle, ULONG propertyID, EU_PROPERTY_INFO *pInfo);
	static void freePropertyInfo(EU_PROPERTY_INFO *pInfo);

	//On success, return the current property value, the "valueSize" should be equal to the EU_PROPERTY_INFO.len
	//Not supported if EU_PROPERTY_INFO.getSupported = false
	static HRESULT getProperty(EUHandle* handle, ULONG propertyID, BYTE *value, ULONG valueSize);

	//On success, set the current property value, the "valueSize" should be equal to the EU_PROPERTY_INFO.len
	//Not supported if EU_PROPERTY_INFO.setSupported = false
	static HRESULT setProperty(EUHandle* handle, ULONG propertyID, BYTE *value, ULONG valueSize);

public:
	static void shutDownMediaSource(std::string devId);
	static bool getPanaCastNameAndSerial(IMFActivate *pDevice, std::string &name, std::string &serial);
	static bool getPanaCastVidPidNameSerial(IMFActivate *pDevice, unsigned short &vid, unsigned short &pid, std::string &name, std::string &serial);

private:
	static bool enumerateSources(IMFActivate** &ppDevices, UINT32 &count);
	static bool getMFActivateIdxByName(IMFActivate **ppDevices, UINT32 count, std::string friendlyname, UINT32 *pIndex);
	static bool getMFActivateName(IMFActivate *pDevice, std::string &name);
	static bool getPanaCastSerialNumber(IMFActivate *pDevice, std::string &serial);
	static bool findAndOpenEUControl(IMFMediaSource *pSource, GUID devGuid, DWORD *pNodeId, IKsControl **ppControl);
	static HRESULT findExtensionNode(IKsTopologyInfo * pKsTopologyInfo, GUID devGuid, DWORD* pNodeId);
	static void releaseIMFActivates(IMFActivate **ppDevices, UINT32 count);
	static bool mallocPropInfo(EU_PROPERTY_INFO* pInfo, ULONG len);
	static HRESULT getKSPropDesc(EUHandle* handle, ULONG propertyID, ULONG propFlag, KSPROPERTY_MEMBERSHEADER *pMemberHeader, BYTE** pMembers, bool *pGetSupported, bool *pSetSupported); //members needed to be free()
	static IMFMediaSource* getMFMediaSource(IMFActivate* device, std::string devName, std::string devId);
	static std::string getDeviceSymbolicLink(IMFActivate* device);
	static std::string toLower(const std::string& s);
	static bool getStringAfter(std::string deviceId, std::string type, size_t len, std::string& returnId);
	static bool getVidPidFromDevicePath(std::string deviceId, std::string& vendor_id, std::string& product_id);
	static void getUnusedWndName(std::string &cName, std::string &wName);
	void startDeviceMonitorMessageLoop(std::string cName, std::string wName);
	void addToResourceList(std::string devId);

private:
	static void KsPropertyThreadProc(bool* isThreadExitedPtr, void* csLock, std::promise<HRESULT> &resultReady, std::promise<void> &setupReady, 
		EUHandle *handle, GUID kspNodePropSet, ULONG kspNodePropId, bool isGet, ULONG kspNodeId,
		 PVOID pPropData, ULONG pPropDataLen, ULONG* bytesReturn);
	static void ksPropThreadWaitAndCleanup(bool* isThreadExitedPtr, void* csLock, EUHandle *handle);
	static HRESULT KsPropertyProc(EUHandle *handle, GUID kspNodePropSet, ULONG kspNodePropId, bool isGet, ULONG kspNodeId,
		PVOID pPropData, ULONG pPropDataLen, ULONG* bytesReturn);

private:
	static void shutdownMFSourceThreadProc(IMFMediaSource *source, void* csLock, bool * isThreadExitedPtr, std::promise<void> &ready);
	static void shutdownMFSourceThreadWaitAndCleanup(void* csLock, bool * isThreadExitedPtr);

private:
	static std::map<std::string, IMFMediaSource*> mediaSourceTable;
	static std::map<std::string, std::string> devNameTable;

private:
	//variables need to init/destroy
	std::vector<std::string> resourceIdList;
	void* monitorTh;
	volatile bool stopMonitor;
};

#endif /*_WIN32*/

#endif /*__UVC_EXTENSION_UNIT_MGR_H__*/
