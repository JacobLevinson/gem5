#include <stdio.h>
#include <stdlib.h>

float subtract(float in1, float in2) {
  float ret = 0.0;
  asm ("fsub %2, %0" : "=&t" (ret) : "%0" (in1), "u" (in2));
  return ret;
}

float rev_subtract(float in1, float in2) {
  float ret = 0.0;
  asm ("fsubr %2, %0" : "=&t" (ret) : "%0" (in1), "u" (in2));
  return ret;
}

int main(int argc, char** argv) {
  if(argc != 3) {
    printf("need 2 float args\n");
    return 1;
  }
  float f1= atof(argv[1]), f2=atof(argv[2]);

  printf("subtract: %f - %f -> %f\n", f1,f2,subtract(f1,f2));
  printf("rev_subtract: - %f + %f -> %f\n", f1,f2,rev_subtract(f1,f2));
  return 0;
}