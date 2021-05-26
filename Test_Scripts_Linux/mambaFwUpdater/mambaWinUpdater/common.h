#pragma once
#include <string>

template <class T> void SafeRelease(T **ppT)
{
	if (*ppT)
	{
		(*ppT)->Release();
		*ppT = NULL;
	}
}

template <class T> void SafeReleaseAllCount(T **ppT)
{
	if (*ppT)
	{
		ULONG e = (*ppT)->Release();

		while (e)
		{
			e = (*ppT)->Release();
		}

		*ppT = NULL;
	}
}

#define arraySize(a) ( sizeof(a) / sizeof(*(a)) )
typedef enum {
	D_ERR=0,
	D_NORMAL,
	D_VERBOSE,
	D_LOQACIOUS
} dbg_level_e;
#define DEFAULT_LEVEL D_ERR
typedef void (dbg_logger)(const char * msg);
void setMFLogger(dbg_logger *);

void DBG(dbg_level_e level, const char * format, ...);
std::string SysWideToUTF8(const std::wstring& wide);
std::wstring SysUTF8ToWide(const std::string& lean);
