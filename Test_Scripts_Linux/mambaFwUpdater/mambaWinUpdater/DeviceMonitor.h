#pragma once
#include <Windows.h>
#include <ks.h>
#include <ksmedia.h>
#include <string>
#include <Dbt.h>
#include <SetupAPI.h>

class DeviceNotificationCallback {
public:
	virtual void onDeviceArrived(std::string id, std::string name) = 0;
	virtual void onDeviceLost(std::string id, std::string name) = 0;
	virtual void onWindowClosed() = 0;
};

class DeviceMonitor
{

public:

	DeviceMonitor(DeviceNotificationCallback *cb, HWND hWnd); //if hWnd == NULL, it creates a new hidden wnd
	DeviceMonitor(DeviceNotificationCallback *cb, HWND hWnd, std::string cName, std::string wName); //if hWnd == NULL, it creates a new hidden wnd
	virtual ~DeviceMonitor();
	void handleUSBDeviceNotification(PDEV_BROADCAST_HDR pBroadcastDeviceHeader, bool deviceArrived);
	void handleWindowClosed();
   // need to call dispatchMessages() to actually handle calls from WINDOWS
	bool dispatchMessages();


	// the following two methods needs to be called from the same thread that called the constructor
	// prevent system from shutdown
	bool preventSystemFromShutdown(TCHAR * msg);
	// allow system to proceed to shutdown
	bool allowSystemToShutdown();
	bool canSystemShutdown() { return allowSystemShutdown; }

	// prevent computer from going to sleep
	static bool preventSystemFromSleeping();
	// allow computer to proceed to sleep
	static bool allowSystemToSleep();
private:
	bool registerUSBDeviceNotification(std::string cName, std::string wName);
	void unRegisterUSBDeviceNotification();
	void AdjustWindowRect(RECT *rect);
	int createHiddenWindow(std::string cName, std::string wName, int w, int h);
	bool getDeviceId(DEV_BROADCAST_HDR *pHdr, std::string& id, std::wstring& wid);
	bool getDeviceName(bool deviceRemoved, std::wstring& deviceId, std::wstring& deviceName);
	bool findDevice(HDEVINFO& hDevInfo, std::wstring& szDevId, SP_DEVINFO_DATA& spDevInfoData);

	DeviceNotificationCallback * deviceNotificationCallback;
	PDEV_BROADCAST_DEVICEINTERFACE m_usbDeviceInterface;
	HWND m_Hwnd;
	HDEVNOTIFY  m_hUSBNotification;
	bool allowSystemShutdown;
	std::string m_cName;
};

