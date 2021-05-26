#include <string.h>
#include "vendorCmd.h"

static void fillUVCGenericControlHeader(unsigned char b_request, unsigned short w_value, unsigned short w_index, unsigned short w_length, unsigned char* header)
{
/*
Byte 0 = bRequest
Byte1: LB(wValue) 
Byte2: HB(wValue)
Byte3: LB(wIndex)
Byte4: HB(wIndex)
Byte5: LB(wLength)
Byte6: HB(wLength)
*/
	header[0] = b_request;
	header[1] = w_value & 0xFF;
	header[2] = w_value >> 8;
	header[3] = w_index & 0xFF;
	header[4] = w_index >> 8;
	header[5] = w_length & 0xFF;
	header[6] = w_length >> 8;
}

#define XU_CTRL_GENERIC_7B_XFER        9
#define XU_CTRL_GENERIC_256B_XFER		10
#define XU_CTRL_GENERIC_263B_XFER		11 
#define XU_CTRL_GENERIC_1031B_XFER		23
#define MAX_UVC_PROP_LEN 1024 //max # bytes for UVC XU property length

#define UVC_CONTROL_HEADER_LEN 7 //uvc control header size
bool sendVendorCommand(UVCInterface* uvcMgr, bool needRead, unsigned char b_request, unsigned short w_value, unsigned short w_index, 
   unsigned char *data, unsigned short data_size, unsigned short read_bytes)
{
   if (uvcMgr == NULL) {
      printf("ERROR vcmd: invalid uvc interface!\n");
      return false;
   }
	if (data_size > MAX_UVC_PROP_LEN || read_bytes > MAX_UVC_PROP_LEN) {
		printf("ERROR vcmd: maximum supported length = %d, requested data_size = %d,%d\n", MAX_UVC_PROP_LEN, data_size, read_bytes);
		return false;
	}

   unsigned char mdata[UVC_CONTROL_HEADER_LEN + MAX_UVC_PROP_LEN];
   memset(mdata, 0, sizeof(mdata));
   unsigned short wLen = data_size == 0 ? read_bytes : data_size;
   fillUVCGenericControlHeader(b_request, w_value, w_index, wLen, mdata);
   if (data_size > 0) memcpy(mdata+UVC_CONTROL_HEADER_LEN, data, data_size);

   int pId = (data_size == 1024 ? XU_CTRL_GENERIC_1031B_XFER : (data_size == 0 ? XU_CTRL_GENERIC_7B_XFER : XU_CTRL_GENERIC_263B_XFER));
   int pdSize = (data_size == 1024 ? 1031 : (data_size == 0 ? 7 : 263));
   if (!uvcMgr->setProperty(pId, mdata, pdSize)) {
      printf("ERROR vcmd: set failed at bRequest 0x%x\n", b_request);
      return false;
   }

   if (needRead && read_bytes > 0) {
      unsigned char d[256];
      if (!uvcMgr->getProperty(XU_CTRL_GENERIC_256B_XFER, d, sizeof(d))) {
         printf("ERROR vcmd: Read get failed at bRequest 0x%x\n", b_request);
         return false;
      }
      memcpy(data, d, read_bytes);
   }
   return true;
}
