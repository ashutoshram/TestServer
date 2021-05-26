#ifndef __VENDOR_CMD_H__
#define __VENDOR_CMD_H__

#include "UVCInterface.h"

#ifdef __cplusplus
extern "C" {
#endif
bool sendVendorCommand(UVCInterface* uvcMgr, bool needRead, unsigned char b_request, unsigned short w_value, unsigned short w_index, 
   unsigned char *data, unsigned short data_size, unsigned short read_bytes);
#ifdef __cplusplus
}
#endif

#endif /*__VENDOR_CMD_H__*/
