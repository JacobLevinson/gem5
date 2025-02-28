#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 64 // Adjust this value for larger matrices

void initialize_matrix(float **matrix, int size)
{
        for (int i = 0; i < size; i++)
        {
                for (int j = 0; j < size; j++)
                {
                        matrix[i][j] = (float)rand() / RAND_MAX;
                }
        }
}

void multiply_matrices(float **A, float **B, float **C, int size)
{
        for (int i = 0; i < size; i++)
        {
                for (int j = 0; j < size; j++)
                {
                        C[i][j] = 0.0;
                        for (int k = 0; k < size; k++)
                        {
                                C[i][j] += A[i][k] * B[k][j];
                        }
                }
        }
}

float **allocate_matrix(int size)
{
        float **matrix = (float **)malloc(size * sizeof(float *));
        for (int i = 0; i < size; i++)
        {
                matrix[i] = (float *)malloc(size * sizeof(float));
        }
        return matrix;
}

void free_matrix(float **matrix, int size)
{
        for (int i = 0; i < size; i++)
        {
                free(matrix[i]);
        }
        free(matrix);
}

int main()
{
        srand(time(NULL));

        printf("Allocating matrices...\n");
        float **A = allocate_matrix(N);
        float **B = allocate_matrix(N);
        float **C = allocate_matrix(N);

        printf("Initializing matrices...\n");
        initialize_matrix(A, N);
        initialize_matrix(B, N);

        printf("Performing matrix multiplication...\n");
        multiply_matrices(A, B, C, N);


        free_matrix(A, N);
        free_matrix(B, N);
        free_matrix(C, N);

        printf("Done.\n");
        return 0;
}
