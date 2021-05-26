#include "DeviceMonitor.h"
#include "common.h"
#include <tchar.h>
#include <algorithm>
#include <Windows.h>
#include <atlstr.h>

#pragma comment(lib,"SetupAPI")

struct devWindowParams
{
	LPCTSTR lpClassName;
	LPCTSTR lpWindowName;
	DWORD dwStyle;
	int nx;
	int ny;
	int ncell;
	int nAdapter;
	int nMaxFPS;
	int nWidth;
	int nHeight;
	HWND hWndParent;
	HMENU hMenu;
	HINSTANCE hInstance;
	LPVOID lpParam;
	bool bFullScreen; // Stretch window to full screen
};

static std::string GetLastErrorAsString()
{
	//Get the error message, if any.
	DWORD errorMessageID = ::GetLastError();
	if (errorMessageID == 0) {
		printf("no last error\n");
		return std::string(); //No error message has been recorded
	}
	LPSTR messageBuffer = nullptr;
	size_t size = FormatMessageA(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
		NULL, errorMessageID, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), (LPSTR)&messageBuffer, 0, NULL);

	std::string message(messageBuffer, size);

	//Free the buffer.
	LocalFree(messageBuffer);

	return message;
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

static CSLock deviceMonitorLock; //critical section protects the createWindow and DestroyWindow calls

DeviceMonitor::DeviceMonitor(DeviceNotificationCallback *cb, HWND hWnd) :DeviceMonitor(cb, hWnd, "Monitor Window Class", "webcam_monitor")
{
}

DeviceMonitor::DeviceMonitor(DeviceNotificationCallback *cb, HWND hWnd, std::string cName, std::string wName)
{
	deviceNotificationCallback = cb;
	m_Hwnd = hWnd;
	m_cName = "";
	if (!registerUSBDeviceNotification(cName, wName)) {
		DBG(D_ERR, "DeviceMonitor::init: cannot register for device notification\n");
		throw - 1;
	}
	allowSystemShutdown = true;
}

DeviceMonitor::~DeviceMonitor()
{
	unRegisterUSBDeviceNotification();
	if (m_cName != ""){
		deviceMonitorLock.Lock();
		if (m_Hwnd != NULL){
			if (!DestroyWindow(m_Hwnd)){
				DBG(D_ERR, "DestroyWindow Last error : %s\n", GetLastErrorAsString().c_str());
			}
		}
		if (!UnregisterClass(CA2T(m_cName.c_str()), GetModuleHandle(NULL))){
			DBG(D_ERR, "UnregisterClass Last error : %s\n", GetLastErrorAsString().c_str());
		}
		deviceMonitorLock.Unlock();
	}

}

static LRESULT CALLBACK WindowProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
	DBG(D_VERBOSE, "DeviceMonitor::WindowProc: hWnd = %p, message = 0x%x, wParam = 0x%x, lParam = 0x%x\n",
		hWnd, message, wParam, lParam);
#ifdef _WIN64
	DeviceMonitor* pSource = (DeviceMonitor*)GetWindowLongPtr(hWnd, GWLP_USERDATA);
#else
	DeviceMonitor* pSource = (DeviceMonitor*)LongToPtr(GetWindowLongPtr(hWnd, GWL_USERDATA));
#endif
	if (pSource) {
		switch (message) {
		case WM_DEVICECHANGE:
			{
				DBG(D_VERBOSE, "DeviceMonitor::WindowProc: Got a DEVICECHANGE notification\n");
				PDEV_BROADCAST_HDR pBroadCastHDR = (DEV_BROADCAST_HDR*)lParam;
				switch (wParam) 
				{
					case DBT_DEVICEREMOVECOMPLETE:
						pSource->handleUSBDeviceNotification(pBroadCastHDR, false);
						break;
					case DBT_DEVICEARRIVAL:
						pSource->handleUSBDeviceNotification(pBroadCastHDR, true);
						break;
					default:
						break;
				}
			}
			break;
		case WM_CLOSE:
			DBG(D_NORMAL, "DeviceMonitor::WindowProc: got WM_CLOSE\n");
			pSource->handleWindowClosed();
			break;
		case WM_QUERYENDSESSION:
			if (pSource->canSystemShutdown()) {
				DBG(D_NORMAL, "DeviceMonitor::WindowProc: got WM_QUERYENDSESSION: returning TRUE\n");
				return TRUE;
			}
			else {
				DBG(D_NORMAL, "DeviceMonitor::WindowProc: got WM_QUERYENDSESSION: returning FALSE\n");
				return FALSE;
			}
			break;

		default:
			break;
		}
	}

	return DefWindowProc(hWnd, message, wParam, lParam);
}

void DeviceMonitor::AdjustWindowRect(RECT *rect)
{
	int cxmax = GetSystemMetrics(SM_CXMAXTRACK);
	int cymax = GetSystemMetrics(SM_CYMAXTRACK);
	int cxmin = GetSystemMetrics(SM_CXMINTRACK);
	int cymin = GetSystemMetrics(SM_CYMINTRACK);
	int leftmax = cxmax - cxmin;
	int topmax = cymax - cxmin;
	if (rect->left < 0)
		rect->left = 0;
	if (rect->left > leftmax)
		rect->left = leftmax;
	if (rect->top < 0)
		rect->top = 0;
	if (rect->top > topmax)
		rect->top = topmax;

	if (rect->right < rect->left + cxmin)
		rect->right = rect->left + cxmin;
	if (rect->right - rect->left > cxmax)
		rect->right = rect->left + cxmax;

	if (rect->bottom < rect->top + cymin)
		rect->bottom = rect->top + cymin;
	if (rect->bottom - rect->top > cymax)
		rect->bottom = rect->top + cymax;
}

int DeviceMonitor::createHiddenWindow(std::string cBaseNameStr, std::string wBaseNameStr, int w, int h)
{
	//find a unique window & class name
	CString wBaseName(CA2T(wBaseNameStr.c_str()));
	CString cBaseName(CA2T(cBaseNameStr.c_str()));
	CString wName = wBaseName;
	CString cName = cBaseName;

	int nextIdx = 0;
	while (FindWindow(cName, wName) != NULL) {
		CString idxStr;
		idxStr.Format(_T("_%d"), nextIdx);
		wName = wBaseName + idxStr;
		cName = cBaseName + idxStr;
		nextIdx++;
	}

	devWindowParams windowParams;
	memset(&windowParams, 0, sizeof(windowParams));
	
	windowParams.lpWindowName = wName;
	windowParams.nx = 0;
	windowParams.ny = 0;
	windowParams.nWidth = w;
	windowParams.nHeight = h;
	windowParams.ncell = 0;
	windowParams.nAdapter = 0;
	windowParams.nMaxFPS = 0;

	windowParams.lpClassName = cName;
	windowParams.dwStyle = WS_OVERLAPPEDWINDOW;
	windowParams.hWndParent = HWND_DESKTOP;
	windowParams.hMenu = NULL;
	windowParams.hInstance = GetModuleHandle(NULL);
	windowParams.lpParam = NULL;
	windowParams.bFullScreen = FALSE;

	WNDCLASS window;
	memset(&window, 0, sizeof(WNDCLASS));

	window.lpfnWndProc = (WNDPROC)WindowProc;
	window.hInstance = GetModuleHandle(NULL);;
	window.hCursor = LoadCursor(NULL, IDC_ARROW);
	window.lpszClassName = windowParams.lpClassName;

	if (!RegisterClass(&window)) {
		DBG(D_ERR, "DeviceMonitor::createHiddenWindow: unable to register class for hidden window, Last Error %s\n", GetLastErrorAsString().c_str());
		return -1;
	}
	

	windowParams.nMaxFPS = 10000;//hypotetical maximum

	//no title window style if required
	DWORD dwStyle = NULL == windowParams.lpWindowName ? WS_POPUP | WS_BORDER | WS_MAXIMIZE : WS_OVERLAPPEDWINDOW;

	::RECT displayRegion = { 0, 0, windowParams.nWidth, windowParams.nHeight };
	AdjustWindowRect(&displayRegion);
	double aspect_w = (double)windowParams.nHeight / (double)windowParams.nWidth;
	displayRegion.bottom = (LONG)(displayRegion.right * aspect_w);

	m_Hwnd = CreateWindowEx(NULL,
		windowParams.lpClassName,
		windowParams.lpWindowName,
		!windowParams.bFullScreen ? dwStyle : (WS_POPUP),
		!windowParams.bFullScreen ? displayRegion.left : 0,
		!windowParams.bFullScreen ? displayRegion.top : 0,
		!windowParams.bFullScreen ? displayRegion.right : GetSystemMetrics(SM_CXSCREEN),
		!windowParams.bFullScreen ? displayRegion.bottom : GetSystemMetrics(SM_CYSCREEN),
		windowParams.hWndParent,
		windowParams.hMenu,
		windowParams.hInstance,
		windowParams.lpParam);

	if (!m_Hwnd) {
		DBG(D_ERR, "DeviceMonitor::createHiddenWindow: unable to create windowex\n");
		if (!UnregisterClass(cName, GetModuleHandle(NULL))){
			DBG(D_ERR, "UnregisterClass Last error : %s\n", GetLastErrorAsString().c_str());
		}
		return -1;
	}


#ifdef _WIN64
	SetWindowLongPtr(m_Hwnd, GWLP_USERDATA, (LONG_PTR)this);
#else
	SetWindowLong(m_Hwnd, GWL_USERDATA, PtrToLong(this));
#endif

	//ShowWindow(m_Hwnd, SW_SHOWDEFAULT);
	//UpdateWindow(m_Hwnd);

	//save the class name so we can unregister the class in the destructor
	m_cName = CT2CA(cName);
	 

	return 0;
}

bool DeviceMonitor::dispatchMessages()
{
	MSG Msg;
	if (PeekMessage(&Msg, m_Hwnd, 0, 0, PM_REMOVE)) {
		DBG(D_VERBOSE, "DeviceMonitor::monitorFunc:processing a message %u\n", Msg.message);
		TranslateMessage(&Msg);
		DispatchMessage(&Msg);
		return true;
	}
	return false;
}

bool DeviceMonitor::registerUSBDeviceNotification(std::string cName, std::string wName)
{
	if (m_Hwnd == NULL) {

		deviceMonitorLock.Lock();
		int ret = createHiddenWindow(cName, wName, 100, 100);
		deviceMonitorLock.Unlock();

		if (ret < 0){
			DBG(D_ERR, "DeviceMonitor::registerUSBDeviceNotification: unable to create hidden window\n");
			return false;
		}
		DBG(D_VERBOSE, "DeviceMonitor::registerUSBDeviceNotification: created a hidden window for device notifications (Hwnd = %p)\n", m_Hwnd);

	}

	m_usbDeviceInterface = new DEV_BROADCAST_DEVICEINTERFACE;
	m_usbDeviceInterface->dbcc_size = sizeof(DEV_BROADCAST_DEVICEINTERFACE);
	m_usbDeviceInterface->dbcc_devicetype = DBT_DEVTYP_DEVICEINTERFACE;
	m_usbDeviceInterface->dbcc_classguid = KSCATEGORY_CAPTURE;

	m_hUSBNotification = RegisterDeviceNotification(m_Hwnd, m_usbDeviceInterface,
		DEVICE_NOTIFY_WINDOW_HANDLE | DEVICE_NOTIFY_ALL_INTERFACE_CLASSES);
	if (m_hUSBNotification == NULL) {
		DBG(D_ERR, "DeviceMonitor::registerUSBDeviceNotification: unable to register device notification\n");
		return false;
	}

	return true;
}

void DeviceMonitor::unRegisterUSBDeviceNotification()
{
	if (m_hUSBNotification) {
		UnregisterDeviceNotification(m_hUSBNotification);
		m_hUSBNotification = NULL;
	}

	if (m_usbDeviceInterface) {
		delete m_usbDeviceInterface;
		m_usbDeviceInterface = NULL;
	}
	deviceNotificationCallback = NULL;
}

bool DeviceMonitor::getDeviceId(DEV_BROADCAST_HDR *pHdr, std::string& id, std::wstring& wid)
{
	DEV_BROADCAST_DEVICEINTERFACE *pDi = NULL;

	if (pHdr == NULL) {
		return false;
	}
	if (pHdr->dbch_devicetype != DBT_DEVTYP_DEVICEINTERFACE) {
		return false;
	}

	pDi = (DEV_BROADCAST_DEVICEINTERFACE*)pHdr;
	wid = std::wstring(pDi->dbcc_name, wcslen(pDi->dbcc_name));

	id = SysWideToUTF8(wid);
	return true;
}


void DeviceMonitor::handleUSBDeviceNotification(PDEV_BROADCAST_HDR pBroadcastDeviceHeader, bool deviceArrived)
{
	if (deviceNotificationCallback == NULL) return;
	std::string deviceId;
	std::wstring wDeviceId;
	if (getDeviceId(pBroadcastDeviceHeader, deviceId, wDeviceId)) {
		std::wstring wDeviceName;
		getDeviceName(!deviceArrived, wDeviceId, wDeviceName);
		std::string deviceName = SysWideToUTF8(wDeviceName);
		if (deviceArrived) {
			deviceNotificationCallback->onDeviceArrived(deviceId, deviceName);
		}
		else {
			deviceNotificationCallback->onDeviceLost(deviceId, deviceName);
		}
	}
	else {
		printf("DeviceMonitor::handleUSBDeviceNotification: could not determine device id\n");
	}
}

void DeviceMonitor::handleWindowClosed()
{
	if (deviceNotificationCallback == NULL) return;
	deviceNotificationCallback->onWindowClosed();
}




bool DeviceMonitor::getDeviceName(bool deviceRemoved, std::wstring& deviceId, std::wstring& deviceName)
{
	// pDevInf->dbcc_name: 
	// \\?\USB#Vid_04e8&Pid_503b#0002F9A9828E0F06#{a5dcbf10-6530-11d2-901f-00c04fb951ed}
	// szDevId: USB\Vid_04e8&Pid_503b\0002F9A9828E0F06
	// szClass: USB
	deviceName = _T("");
	if (deviceId.length() < 4) return false;

	std::wstring szDeviceId = deviceId.substr(4);
	int idx = (int) szDeviceId.rfind(_T("#"));
	if (idx == std::string::npos) return false;
	szDeviceId = szDeviceId.substr(0, idx);
	std::replace(szDeviceId.begin(), szDeviceId.end(), _T('#'), _T('\\'));

	idx = (int) szDeviceId.find(_T("\\"));
	if (idx == std::string::npos) return false;
	std::wstring szDeviceClass = szDeviceId.substr(0, idx);

   
	DWORD dwFlag = deviceRemoved ? DIGCF_ALLCLASSES : (DIGCF_ALLCLASSES | DIGCF_PRESENT);
	HDEVINFO hDevInfo = SetupDiGetClassDevs(NULL, szDeviceClass.c_str(), NULL, dwFlag);
	if (INVALID_HANDLE_VALUE == hDevInfo || NULL == hDevInfo) {
		return false;
	}

	SP_DEVINFO_DATA spDevInfoData;
	if (findDevice(hDevInfo, szDeviceId, spDevInfoData)) {
		// OK, device found
		DWORD DataT;
		TCHAR buf[MAX_PATH] = _T("");
		DWORD nSize = 0;

		// get Friendly Name or Device Description
		if (SetupDiGetDeviceRegistryProperty(hDevInfo, &spDevInfoData, SPDRP_FRIENDLYNAME, &DataT, (PBYTE)buf, sizeof(buf), &nSize)) {
			;
		}
		else if (SetupDiGetDeviceRegistryProperty(hDevInfo, &spDevInfoData, SPDRP_DEVICEDESC, &DataT, (PBYTE)buf, sizeof(buf), &nSize)) {
			;
		}
		else {
			lstrcpy(buf, _T("Unknown"));
		}
		deviceName = std::wstring(buf);
	}

	SetupDiDestroyDeviceInfoList(hDevInfo);
	return true;
}



bool DeviceMonitor::findDevice(HDEVINFO& hDevInfo, std::wstring& szDevId, SP_DEVINFO_DATA& spDevInfoData)
{
	std::string szDevIdStr = SysWideToUTF8(szDevId);
	spDevInfoData.cbSize = sizeof(SP_DEVINFO_DATA);
	for (int i = 0; SetupDiEnumDeviceInfo(hDevInfo, i, &spDevInfoData); i++) {
		DWORD nSize = 0;
		TCHAR buf[MAX_PATH];

		if (!SetupDiGetDeviceInstanceId(hDevInfo, &spDevInfoData, buf, sizeof(buf), &nSize)) {
			return false;
		}
		std::string bufStr = SysWideToUTF8(std::wstring(buf));
		if (_stricmp(szDevIdStr.c_str(), bufStr.c_str()) == 0) {
			// OK, device found
			DBG(D_VERBOSE, "DeviceMonitor::findDevice: match: szDevId = %s, buf = %s\n",
				szDevIdStr.c_str(), bufStr.c_str());
			return true;
		}
	}
	return false;
}

bool DeviceMonitor::preventSystemFromShutdown(TCHAR * msg)
{
	bool ret = ShutdownBlockReasonCreate(m_Hwnd, msg) != 0;
	if (ret) {
		allowSystemShutdown = false;
		preventSystemFromSleeping();
	}
	return ret;
}

bool DeviceMonitor::allowSystemToShutdown()
{
	allowSystemShutdown = true;
	allowSystemToSleep();
	return ShutdownBlockReasonDestroy(m_Hwnd) != 0;
}

// prevent computer from going to sleep
// static
bool DeviceMonitor::preventSystemFromSleeping()
{
	if (SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED) == NULL)
	{
		return SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED) != NULL;
	}
	return true;
}

// allow computer to proceed to sleep
// static
bool DeviceMonitor::allowSystemToSleep()
{
	return SetThreadExecutionState(ES_CONTINUOUS) != NULL;
}