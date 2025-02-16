#include <stdio.h>
#include <stdlib.h>



float rev_subtract(float in1, float in2) {
  float ret = 0.0;
  asm ("fsubr %2, %0" : "=&t" (ret) : "%0" (in1), "u" (in2));
  return ret;
}

int main(int argc, char** argv) {

  float f1 = 5;
  float f2 = 6;

  printf("rev_subtract: - %f + %f -> %f\n", f1,f2,rev_subtract(f1,f2));
  return 0;
}