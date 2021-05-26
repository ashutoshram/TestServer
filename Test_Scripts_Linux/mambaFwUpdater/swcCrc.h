#ifndef PC_SWCCRC_H
#define PC_SWCCRC_H

#include <stdint.h>

typedef uint8_t u8;
typedef int8_t s8;
typedef uint16_t u16;
typedef int16_t s16;
typedef uint32_t u32;
typedef int32_t s32;
typedef uint64_t u64;
typedef int64_t s64;


#ifdef __cplusplus
extern "C" {
#endif


	// BS define in order to align swcCalcCrc32() PC model prototype with myriad prototype (parameter not used for pc model)
	typedef u32 pointer_type;


	/// @brief     : swcCalcCrc32
	/// @param     : pBuffer           : pointer to u8 buffer
	/// @param     : byteLength        : buffer length
	/// @param     : pt                : pointer type (unused for PC model)
	/// @return    : void
	u32 swcCalcCrc32(u8* pBuffer, u32 byteLength);

#ifdef __cplusplus
}
#endif

#endif //PC_SWCCRC_H

