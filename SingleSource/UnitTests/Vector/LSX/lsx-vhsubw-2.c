#include "lsx_test_util.h"
#include <lsxintrin.h>

int
main ()
{
  __m128i __m128i_out, __m128i_result;
  __m128  __m128_out, __m128_result;
  __m128d __m128d_out, __m128d_result;
  v2u64 v2u64_op0, v2u64_op1, v2u64_op2;
  v4i32 v4i32_op0, v4i32_op1, v4i32_op2;

  int int_op0, int_op1, i = 1, fail;
  long int long_op0, long_op1;
  long int long_int_out, long_int_result;
  unsigned int unsigned_int_out, unsigned_int_result;
  unsigned long int unsigned_long_int_out, unsigned_long_int_result;

  v2u64_op0 = (v2u64){0xffffff0000010000, 0xffffffff00000001};
  v2u64_op1 = (v2u64){0xfe00fffefe0100f6, 0xfe00fe00fe00fd01};
  __m128i_result = (__m128i){0x00ff0001ffffff0a, 0x00ff00ff0000ffff};
  __m128i_out = __lsx_vhsubw_hu_bu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000000095141311, 0x0000000017161515};
  v2u64_op1 = (v2u64){0x76f424887fffffff, 0x0000000000000001};
  __m128i_result = (__m128i){0xff0cff78ff96ff14, 0x0000000000170014};
  __m128i_out = __lsx_vhsubw_hu_bu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x67eb85afb2ebb000, 0x0000000000000000};
  v2u64_op1 = (v2u64){0x67eb85afb2ebb000, 0x0000000000000000};
  __m128i_result = (__m128i){0xff7cffd6ffc700b0, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_hu_bu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000000000000000, 0x0000000000000000};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x0000000000000000};
  __m128i_result = (__m128i){0x0000000000000000, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_hu_bu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0xffffffffffffffff, 0x0000000000000000};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x0000000000000000};
  __m128i_result = (__m128i){0x00ff00ff00ff00ff, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_hu_bu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0xffffffffffffffff, 0xffffffffffffffff};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x0000000000000000};
  __m128i_result = (__m128i){0x0000ffff0000ffff, 0x0000ffff0000ffff};
  __m128i_out = __lsx_vhsubw_wu_hu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x00ffff0000000000, 0x00ffff0000000000};
  v2u64_op1 = (v2u64){0x7f80000000000000, 0x7f8000007f800000};
  __m128i_result = (__m128i){0x000000ff00000000, 0x000000ff00000000};
  __m128i_out = __lsx_vhsubw_wu_hu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000000000000020, 0x0000000000000000};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x0000000000000000};
  __m128i_result = (__m128i){0x0000000000000000, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_wu_hu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0xffffffffffffffff, 0xffffffffffffffff};
  v2u64_op1 = (v2u64){0xffffffffffffffff, 0xffffffffffffffff};
  __m128i_result = (__m128i){0x0000000000000000, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_wu_hu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000000000000000, 0x0000000000000000};
  v2u64_op1 = (v2u64){0xffffffffffffffff, 0xffffffffffffffff};
  __m128i_result = (__m128i){0xffff0001ffff0001, 0xffff0001ffff0001};
  __m128i_out = __lsx_vhsubw_wu_hu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0101010101010101, 0x0101010101010101};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x0000000000000000};
  __m128i_result = (__m128i){0x0000010100000101, 0x0000010100000101};
  __m128i_out = __lsx_vhsubw_wu_hu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0xfefeff00fefeff00, 0xfefeff00fefeff00};
  v2u64_op1 = (v2u64){0x8080808080808080, 0x8080808080808080};
  __m128i_result = (__m128i){0x00007e7e00007e7e, 0x00007e7e00007e7e};
  __m128i_out = __lsx_vhsubw_wu_hu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0xa2e3a36463636363, 0xa2e3a36363636363};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x7f8000007f800000};
  __m128i_result = (__m128i){0x0000a2e300006363, 0x0000a2e300006363};
  __m128i_out = __lsx_vhsubw_wu_hu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000000000000000, 0x0000000000000000};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x0000000000000000};
  __m128i_result = (__m128i){0x0000000000000000, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_du_wu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x52527d7d52527d7d, 0x52527d7d52527d7d};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x0000000000000000};
  __m128i_result = (__m128i){0x0000000052527d7d, 0x0000000052527d7d};
  __m128i_out = __lsx_vhsubw_du_wu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000002400180004, 0x0000000000000000};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x0000000000000000};
  __m128i_result = (__m128i){0x0000000000000024, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_du_wu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x00000000ffffff02, 0x0000000000000000};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x0000000000000000};
  __m128i_result = (__m128i){0x0000000000000000, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_du_wu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0xffffff0000010000, 0xffffffff00000001};
  v2u64_op1 = (v2u64){0xa5f7458b000802ff, 0xabff54f1ffffffff};
  __m128i_result = (__m128i){0x00000000fff7fc01, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_du_wu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000000000000000, 0x0000000000000000};
  v2u64_op1 = (v2u64){0xfffffffffffffffe, 0xfffffffffffffffe};
  __m128i_result = (__m128i){0xffffffff00000002, 0xffffffff00000002};
  __m128i_out = __lsx_vhsubw_du_wu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000000000000000, 0x0000000000000000};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x0000000000000000};
  __m128i_result = (__m128i){0x0000000000000000, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_du_wu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000000000000000, 0x0000000000000000};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x0000000000000000};
  __m128i_result = (__m128i){0x0000000000000000, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_du_wu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000000000000000, 0x0000000000000000};
  v2u64_op1 = (v2u64){0x0000800000000000, 0x0000800000000000};
  __m128i_result = (__m128i){0x0000000000000000, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_du_wu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x14eb6a002a406a00, 0x0000000014eb54ab};
  v2u64_op1 = (v2u64){0x0a7535006af05cf9, 0xffff80008a7555aa};
  __m128i_result = (__m128i){0xffffffffa9fb0d07, 0xffffffff758aaa56};
  __m128i_out = __lsx_vhsubw_du_wu((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0xffffffff00000000, 0xffffffff00000000};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x0000000000000000};
  __m128i_result = (__m128i){0xffffffff00000000, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_qu_du((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0xffffffffff01ff01, 0xffffffffffffffff};
  v2u64_op1 = (v2u64){0xffffffffffffffff, 0x0f180000ffe00000};
  __m128i_result = (__m128i){0x0000000000000000, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_qu_du((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000000000000000, 0x0000000000000000};
  v2u64_op1 = (v2u64){0xffffffffffffffff, 0xffffffffffffffff};
  __m128i_result = (__m128i){0x0000000000000001, 0xffffffffffffffff};
  __m128i_out = __lsx_vhsubw_qu_du((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000000100013fa0, 0x00000001ca02f854};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x0000000000000000};
  __m128i_result = (__m128i){0x00000001ca02f854, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_qu_du((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000000100013fa0, 0x0000000000000000};
  v2u64_op1 = (v2u64){0x0000000000004b01, 0x0000000000000000};
  __m128i_result = (__m128i){0xffffffffffffb4ff, 0xffffffffffffffff};
  __m128i_out = __lsx_vhsubw_qu_du((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000000000000000, 0x0000000000000000};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x0000000000000000};
  __m128i_result = (__m128i){0x0000000000000000, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_qu_du((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000000000000000, 0x0000000000000000};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x0000000000000000};
  __m128i_result = (__m128i){0x0000000000000000, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_qu_du((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000000000000000, 0x0000000000000000};
  v2u64_op1 = (v2u64){0x00001b4a00007808, 0x0000000000000000};
  __m128i_result = (__m128i){0xffffe4b5ffff87f8, 0xffffffffffffffff};
  __m128i_out = __lsx_vhsubw_qu_du((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x7f7f1fd800000004, 0x3fc03fc000000003};
  v2u64_op1 = (v2u64){0xffffffffffffffff, 0xffffffffffffffff};
  __m128i_result = (__m128i){0x3fc03fc000000004, 0xffffffffffffffff};
  __m128i_out = __lsx_vhsubw_qu_du((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000000000000000, 0x0000000000000000};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x0000000000000000};
  __m128i_result = (__m128i){0x0000000000000000, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_qu_du((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0xc080800000000000, 0xc080800000000000};
  v2u64_op1 = (v2u64){0x7efefefe82010201, 0x0000000000000000};
  __m128i_result = (__m128i){0x418181017dfefdff, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_qu_du((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0xc8847ef6ed3f2000, 0x67eb85afb2ebb000};
  v2u64_op1 = (v2u64){0x0000000000000000, 0x0000000000000000};
  __m128i_result = (__m128i){0x67eb85afb2ebb000, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_qu_du((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0xe593c8c4e593c8c4, 0xff800000ff800000};
  v2u64_op1 = (v2u64){0x0000ff8000010f78, 0x0000ffff0000ffff};
  __m128i_result = (__m128i){0xff7f0080ff7ef088, 0x0000000000000000};
  __m128i_out = __lsx_vhsubw_qu_du((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  v2u64_op0 = (v2u64){0x0000000000000155, 0x0000000000000000};
  v2u64_op1 = (v2u64){0x00000000000f0000, 0x0000000000000000};
  __m128i_result = (__m128i){0xfffffffffff10000, 0xffffffffffffffff};
  __m128i_out = __lsx_vhsubw_qu_du((__m128)v2u64_op0, (__m128)v2u64_op1);
  check_lsx_out(&__m128i_result, &__m128i_out, sizeof(__m128i_out), __FILE__, __LINE__);

  return 0;
}
