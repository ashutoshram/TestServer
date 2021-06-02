#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <Windows.h>
#else //Linux
#include <unistd.h>
#include <sys/time.h>
#endif

#include "swcCrc.h"
#include "vendorCmd.h"

#ifdef _WIN32
#include "mambaWinUpdater/WinUVCMgr.h"
#elif __APPLE__
#include "mambaMacUpdater/IOKitUVCMgr.h"
#else //Linux
#include "mambaLinuxUpdater/V4LUVCMgr.h"
#endif

#ifdef _WIN32
DWORD beginMs;
DWORD endMs;
#else //Linux
static struct timeval beginTv;
static struct timeval endTv;
#endif
static void markBeginTime()
{
#ifdef _WIN32
    beginMs = GetTickCount();
#else //Linux
   gettimeofday(&beginTv, NULL);
#endif
}
static void markEndTime()
{
#ifdef _WIN32
    endMs = GetTickCount();
#else //Linux
   gettimeofday(&endTv, NULL);
#endif
}
static int getTimeDiffMs()
{
#ifdef _WIN32
    return endMs - beginMs;
#else //Linux
   return (((endTv.tv_sec - beginTv.tv_sec) * 1000000) + (endTv.tv_usec - beginTv.tv_usec))/1000;
#endif
} 

#define IMAGE_TYPE_LEN  6
#define FILE_NAME_LEN   32
typedef enum
{
   BOOTLOADER=0,
   MAIN_APP
} MambaImgType_T;
typedef struct {
	uint32_t flash_offset;
	uint32_t image_size;		
	uint32_t max_image_size;
	uint32_t app_crc;
	uint16_t page_size;
	char image_type[IMAGE_TYPE_LEN];
	char image_name[FILE_NAME_LEN];
} packetData_t;


static void printUsageAndExit(char* name) {
   // printf("Usage: %s <\"boot\"/\"main\"> <path to mamba mvcmd>\n", name);
   exit(-1);
}

   
static unsigned char* readImage(const char* path, u32 *fsize){
   *fsize = 0;
#ifdef _WIN32
   FILE* f = NULL;
   fopen_s(&f, path, "rb");
#else //Linux
   FILE *f = fopen(path, "rb");
#endif
   if (f == NULL) {
      // printf("%s not exist!\n", path);
      return NULL;
   }
   fseek(f, 0, SEEK_END);
   *fsize = (u32)ftell(f);
   fseek(f, 0, SEEK_SET);

   unsigned char *buf = (unsigned char*)malloc(*fsize);
   if (buf == NULL) {
      // printf("no mem for %u\n", *fsize);
      *fsize = 0;
      fclose(f);
      return NULL;
   }
   fread(buf, 1, *fsize, f);
   fclose(f);
   return buf;
}

static bool fillUpdateHeader(unsigned char* tempBuf, u32 flashAddress, u32 fileLength, u32 crc, int pageSize, MambaImgType_T type)
{
   const int maxImageSize = 64 * 1024 * 1024; //must be 64MB
   if (fileLength > maxImageSize) {
      // printf("Error - file size %d > max %d\n", fileLength, maxImageSize); 
      return false;
   }

   packetData_t pData; //we assume OS will fill data in LE.
   pData.max_image_size = maxImageSize;
   pData.page_size = pageSize;
   pData.image_size = fileLength;
   pData.flash_offset = flashAddress;
   pData.app_crc = crc;

   if (type == BOOTLOADER) {
#ifdef _WIN32
      strcpy_s(pData.image_type, sizeof(pData.image_type), "app");
      strcpy_s(pData.image_name, sizeof(pData.image_name), "boot");
#else //Linux
      strcpy(pData.image_type, "app");
      strcpy(pData.image_name, "boot");
#endif
   } else { //MAIN_APP
#ifdef _WIN32
      strcpy_s(pData.image_type, sizeof(pData.image_type), "app");
      strcpy_s(pData.image_name, sizeof(pData.image_name), "main");
#else //Linux
      strcpy(pData.image_type, "app");
      strcpy(pData.image_name, "main");
#endif
   }
   memcpy(&tempBuf[0], &pData, sizeof(packetData_t));

   // printf("pData.app_crct: 0x%X\n", pData.app_crc);
   // printf("pData.flash_offset: 0x%X\n", pData.flash_offset);
   // printf("pData.image_size: %d (0x%X)\n", pData.image_size, pData.image_size);
   // printf("pData.page_size: %d\n", pData.page_size);
   // printf("pData.max_image_size: %d, (0x%X)\n", pData.max_image_size, pData.max_image_size);
   // printf("pData.image_type: %s\n", pData.image_type);
   // printf("pData.image_name: %s\n", pData.image_name);
   return true;
}

static bool writeUpdateImage(UVCInterface* uvcMgr, unsigned char* fileData, u32 flashAddress, u32 filesize, u32 pageSize)
{
   u16 tmp1 = flashAddress >> 16;
   u16 tmp2 = flashAddress & 0xffff;
   u32 bytesRemaining = filesize;
   for (u32 i = 0; i < filesize; i = i + pageSize) {
      // if (i % (500*pageSize*4) == 0) printf("%d/%d programed\n", i, filesize);
      u16 wVal = tmp1 + (i / 0x10000);
      u16 wIdx = tmp2 + (i % 0x10000); // tmp2+i will just work as well?
      u32 bytesToWrite = bytesRemaining;
      if (bytesRemaining >= pageSize) {
         bytesToWrite = pageSize;
         bytesRemaining -= pageSize;
      }
      bool status = sendVendorCommand(uvcMgr, false, 0xC2, wVal, wIdx, fileData+i, bytesToWrite, 0/*unused*/);
      if (!status) {
         // printf("error on C2, i %d\n", i);
         return false;
      }
   }
   return true;
}

static int mambaFwUpdate(UVCInterface* uvcMgr, const char* fwFilePath, int pageSize, MambaImgType_T type)
{
   u32 fileLengthActual = 0;
   unsigned char* imgBuf = readImage(fwFilePath, &fileLengthActual);
   if (imgBuf == NULL) return -2;

   u32 fileLength = fileLengthActual;
   if (fileLengthActual % pageSize) { //make sure flashing size always multiple of pageSize.
       int n = fileLengthActual / pageSize;
       fileLength = pageSize * (n + 1);
   }

   unsigned char* buf = (unsigned char*)malloc(fileLength);
   if (buf == NULL) {
       free(imgBuf);
       return -2;
   }
   memset(buf, 0xff, fileLength);
   memcpy(buf, imgBuf, fileLengthActual);
   free(imgBuf);

   //swcCalcCrc32() in WinApp/AltiaToolBox/AltiaToolBox/swcCrc.c
   u32 crc = swcCalcCrc32((u8*)buf, fileLengthActual);
   // printf("get crc %u\n", crc);

   unsigned char data[256];
   const int flashAddress = type == BOOTLOADER ? 0x0 : 0x4000000;
   if (!fillUpdateHeader(data, flashAddress, fileLengthActual, crc, pageSize, type)) {
      free(buf);
      return -3;
   }

   markBeginTime();

   //send update header
   // printf("programming header\n");
   bool status = sendVendorCommand(uvcMgr, true, 0xC1, 0, 0, data, sizeof(data), 1);
   if (!status) {
      // printf("Error - Device not ready or invalisd start up command\n");
      free(buf); 
      return -4;
   }
#ifdef _WIN32
   Sleep(100);
#else //Linux
   usleep(100*1000);
#endif

   // now write the firmware 
   // printf("programming firmware %u bytes, flashing %u bytes\n", fileLengthActual, fileLength);
   writeUpdateImage(uvcMgr, buf, flashAddress, fileLength, pageSize);

   markEndTime();
   // printf("Update Mamba done, take %d sec\n", getTimeDiffMs()/1000);
   
   free(buf); 
   return 0;
}

static int getMambaPageSize(UVCInterface* uvcMgr)
{
   int pageSize = 256;
   uint16_t update_version = 0;
   unsigned char data[256];
   data[0] = 1;
   bool status = sendVendorCommand(uvcMgr, true, 0xC0, 0, 0, data, 0, 3);
   if (!status || data[0] != 0x00) {
      // printf("version: %d %d\n", status, data[0]);
      update_version = 1;
   }
   else{
      memcpy((uint8_t*)&update_version, &data[1], 2); //assume OS is LE.
   }
   // printf("FW update version: %d\n", update_version);
   if (update_version == 1) {
      pageSize = 256;
   }
   else {
      pageSize = 1024;
   }
   return pageSize;
}

static void reboot(UVCInterface* uvcMgr)
{
   unsigned char data[256];
   sendVendorCommand(uvcMgr, true, 0xD7, 0, 0, data, 0, 1);
}

static void checkFW(UVCInterface* uvcMgr)
{
   unsigned char data[256];
   sendVendorCommand(uvcMgr, true, 0xFE, 0xFF, 0, data, 0, 8);
   printf("\n\nFW version: %x.%x.%x\n\n", data[2], data[1], data[0]);
}

int main(int argc, char* argv[]) {
#ifdef _WIN32
   CoInitialize(NULL);
   WinUVCMgr mgr;
#elif __APPLE__
   IOKitUVCMgr mgr;
#else //Linux
   V4LUVCMgr mgr;
#endif

   std::vector<std::string> devs;
   if (!mgr.enumeratePanaCast(devs)) {
      // printf("failed to find camera!\n");
      return -1;
   }
   // printf("found %d cameras\n", (int)(devs.size()));

   //optional to dump all camera info
   unsigned short vid, pid;
   std::string serial, name;
   bool found = false;
   for (const auto dev : devs) {
      if (!mgr.openPanaCast(dev)) {
         // printf("failed to open cam %s\n", dev.c_str());
         continue;
      }
      if (!mgr.getPanaCastDeviceInfo(vid, pid, serial, name)) {
         // printf("failed to get camera info for %s\n", dev.c_str());
         mgr.closePanaCast();
         continue;
      }
      // printf("cam %s has vid 0x%x pid 0x%x serial %s, name %s\n",
            // dev.c_str(), vid, pid, serial.c_str(), name.c_str());
      found = true;
      break;
   }
   //
   if (!found) exit(0);

   //update Mamba: 
   UVCInterface* uvcMgr = (UVCInterface*)&mgr;

   // reboot(uvcMgr);
   checkFW(uvcMgr);

   mgr.closePanaCast();
   return 0;
}
