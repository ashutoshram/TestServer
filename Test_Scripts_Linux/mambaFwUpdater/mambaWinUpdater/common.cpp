#include <stdarg.h>
#include <stdio.h>
#include <string>
#include <Windows.h>
#include "common.h"

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
std::wstring SysUTF8ToWide(const std::string& utf8) {
	return SysMultiByteToWide(utf8, CP_UTF8);
}

std::string SysWideToUTF8(const std::wstring& wide) {
	return SysWideToMultiByte(wide, CP_UTF8);
}

static dbg_logger * loggerRedirect = NULL;
void setMFLogger(dbg_logger * l) {
	loggerRedirect = l;
}

void
DBG(dbg_level_e level, const char * format, ...) {
	if (level <= DEFAULT_LEVEL) {
		va_list ap;
		va_start(ap, format);
		char buf[1024];
		vsnprintf_s(buf, sizeof(buf), format, ap);
		if (loggerRedirect) {
			(*loggerRedirect)(buf);
		}
		else {
			printf(buf);
		}
	}
}

