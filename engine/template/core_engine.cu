#include <iostream>
#include <numeric>
#include <cuda_runtime_api.h>
#include <device_launch_parameters.h>

#if defined(__APPLE__) || defined(MACOSX)
#pragma clang diagnostic ignored "-Wdeprecated-declarations"
#include <GLUT/glut.h>
#else
#include <GL/freeglut.h>
#endif

#include <cuda_runtime.h>
#include <cuda_gl_interop.h>

#include <helper_cuda.h>
#include <helper_cuda_gl.h>


#include "generated_core_engine.cuh"

static void CheckCudaErrorAux (const char *, unsigned, const char *, cudaError_t);
#define CUDA_CHECK_RETURN(value) CheckCudaErrorAux(__FILE__,__LINE__, #value, value)


//#define checkCudaErrors(val) check( (val), #val, __FILE__, __LINE__)

//template<typename T>
//void check(T err, const char* const func, const char* const file, const int line) {
//  if (err != cudaSuccess) {
//    std::cerr << "CUDA error at: " << file << ":" << line << std::endl;
//    std::cerr << cudaGetErrorString(err) << " " << func << std::endl;
//    exit(1);
//  }
//}

__global__ void update_positions_kernel(
		float *d_p_x_out,
		float *d_p_y_out,
		float delta_t,
		float *d_p_x,
		float *d_p_y,
		float *d_nu
		)
{
	int idx = blockDim.x * blockIdx.x + threadIdx.x;

	d_p_x_out[idx] = p_x_func[idx](delta_t, d_p_x, d_p_y, d_nu);
	d_p_y_out[idx] = p_y_func[idx](delta_t, d_p_x, d_p_y, d_nu);
}


__global__ void update_atoms_quantities_kernel(
		float *d_nu_out,
		float delta_t,
		float *d_p_x,
		float *d_p_y,
		float *d_nu)
{
  int idx = blockDim.x * blockIdx.x + threadIdx.x;

  d_nu_out[idx] = nu_func[idx](delta_t, d_p_x, d_p_y, d_nu);
}

__global__ void split_xyzw_to_x_and_y(float *d_p_x_out, float *d_p_y_out, float4 *d_xyzw_position_array)
{
  int idx = blockDim.x * blockIdx.x + threadIdx.x;
  d_p_x_out[idx] = d_xyzw_position_array[idx].x;
  d_p_y_out[idx] = d_xyzw_position_array[idx].y;
}

__global__ void join_x_y_to_xyzw(float4 *d_xyzw_position_out, float *d_p_x, float *d_p_y)
{
  int idx = blockDim.x * blockIdx.x + threadIdx.x;
  d_xyzw_position_out[idx].x = d_p_x[idx];
  d_xyzw_position_out[idx].y = d_p_y[idx];
}

void allocate_arrays(float * &p_x,
		     float * &p_y,
		     float * &nu,
		     float * &d_p_x,
		     float * &d_p_y,
		     float * &d_nu,
		     float * &d_p_x_out,
		     float * &d_p_y_out,
		     float * &d_nu_out)
{
  p_x = new float[NUMBER_OF_MATTERS];
  p_y = new float[NUMBER_OF_MATTERS];
  nu = new float[NUMBER_OF_MATTERS * NUMBER_OF_ATOMS];

  CUDA_CHECK_RETURN(cudaMalloc((void **) &d_p_x, sizeof(float) * NUMBER_OF_MATTERS));
  CUDA_CHECK_RETURN(cudaMalloc((void **) &d_p_y, sizeof(float) * NUMBER_OF_MATTERS));
  CUDA_CHECK_RETURN(cudaMalloc((void **) &d_nu, sizeof(float) * NUMBER_OF_MATTERS * NUMBER_OF_ATOMS));

  CUDA_CHECK_RETURN(cudaMalloc((void **) &d_p_x_out, sizeof(float) * NUMBER_OF_MATTERS));
  CUDA_CHECK_RETURN(cudaMalloc((void **) &d_p_y_out, sizeof(float) * NUMBER_OF_MATTERS));
  CUDA_CHECK_RETURN(cudaMalloc((void **) &d_nu_out, sizeof(float) * NUMBER_OF_MATTERS * NUMBER_OF_ATOMS));
}

void free_arrays(float * &p_x,
                 float * &p_y,
                 float * &nu,
                 float * &d_p_x,
                 float * &d_p_y,
                 float * &d_nu,
                 float * &d_p_x_out,
                 float * &d_p_y_out,
                 float * &d_nu_out)
{
  CUDA_CHECK_RETURN(cudaFree(d_p_x));
  CUDA_CHECK_RETURN(cudaFree(d_p_y));
  CUDA_CHECK_RETURN(cudaFree(d_nu));

  CUDA_CHECK_RETURN(cudaFree(d_p_x_out));
  CUDA_CHECK_RETURN(cudaFree(d_p_y_out));
  CUDA_CHECK_RETURN(cudaFree(d_nu_out));

  delete[] p_x;
  delete[] p_y;
  delete[] nu;
}

void upload_host_arrays(float *d_p_x,
			float *d_p_y,
			float *d_nu,
			float *p_x,
			float *p_y,
			float *nu)
{
  CUDA_CHECK_RETURN(cudaMemcpy(d_p_x, p_x, sizeof(float) * NUMBER_OF_MATTERS, cudaMemcpyHostToDevice));
  CUDA_CHECK_RETURN(cudaMemcpy(d_p_y, p_y, sizeof(float) * NUMBER_OF_MATTERS, cudaMemcpyHostToDevice));
  CUDA_CHECK_RETURN(cudaMemcpy(d_nu, nu, sizeof(float) * NUMBER_OF_MATTERS * NUMBER_OF_ATOMS, cudaMemcpyHostToDevice));
}

void join_position_arrays(float4 *d_xyzw_p,
			  float *d_p_x,
			  float *d_p_y)
{
  const dim3 blockSize(NUMBER_OF_MATTERS, 1, 1);
  const dim3 gridSize( 1, 1, 1);

  join_x_y_to_xyzw<<<gridSize, blockSize>>>(d_xyzw_p, d_p_x, d_p_y);
}

void integrate(float delta_t,
               float4 *d_xyzw_p,
               float *&d_nu,
               float *&d_nu_out,
               float *&d_p_x,
               float *&d_p_y,
               float *&d_p_x_out,
               float *&d_p_y_out)
{
  // I believe that blockSize should be as large as possible
  // so we should determine that value by querying GPU
  // deviceProp.maxThreadsPerBlock
  
  const dim3 blockSize(NUMBER_OF_MATTERS, 1, 1);
  const dim3 gridSize( 1, 1, 1);
  const dim3 blockSizeAtoms(NUMBER_OF_MATTERS * NUMBER_OF_ATOMS, 1, 1);

  split_xyzw_to_x_and_y<<<gridSize, blockSize>>>(d_p_x, d_p_y, d_xyzw_p);
  cudaDeviceSynchronize(); checkCudaErrors(cudaGetLastError());
	
  update_positions_kernel<<<gridSize, blockSize>>>(d_p_x_out, d_p_y_out, delta_t, d_p_x, d_p_y, d_nu);  
  cudaDeviceSynchronize(); checkCudaErrors(cudaGetLastError());

  update_atoms_quantities_kernel<<<gridSize, blockSizeAtoms>>>(d_nu_out, delta_t, d_p_x, d_p_y, d_nu);
  cudaDeviceSynchronize(); checkCudaErrors(cudaGetLastError());

  join_x_y_to_xyzw<<<gridSize, blockSize>>>(d_xyzw_p, d_p_x_out, d_p_y_out);

  float *tmp_nu = d_nu;
  d_nu = d_nu_out;
  d_nu_out = tmp_nu;

  cudaDeviceSynchronize(); checkCudaErrors(cudaGetLastError());
}

void cudaGLInit(int argc, char **argv)
{
    // use command-line specified CUDA device, otherwise use device with highest Gflops/s
    findCudaGLDevice(argc, (const char **)argv);
}

void registerGLBufferObject(uint vbo, struct cudaGraphicsResource **cuda_vbo_resource)
{
    checkCudaErrors(cudaGraphicsGLRegisterBuffer(cuda_vbo_resource, vbo,
                                                 cudaGraphicsMapFlagsNone));
}

void unregisterGLBufferObject(struct cudaGraphicsResource *cuda_vbo_resource)
{
    checkCudaErrors(cudaGraphicsUnregisterResource(cuda_vbo_resource));
}

void *mapGLBufferObject(struct cudaGraphicsResource **cuda_vbo_resource)
{
    void *ptr;
    checkCudaErrors(cudaGraphicsMapResources(1, cuda_vbo_resource, 0));
    size_t num_bytes;
    checkCudaErrors(cudaGraphicsResourceGetMappedPointer((void **)&ptr, &num_bytes,
                                                         *cuda_vbo_resource));
    return ptr;
}

void unmapGLBufferObject(struct cudaGraphicsResource *cuda_vbo_resource)
{
    checkCudaErrors(cudaGraphicsUnmapResources(1, &cuda_vbo_resource, 0));
}

/**
 * Check the return value of the CUDA runtime API call and exit
 * the application if the call has failed.
 */
static void CheckCudaErrorAux (const char *file, unsigned line, const char *statement, cudaError_t err)
{
    if (err == cudaSuccess)
        return;
    std::cerr << statement<<" returned " << cudaGetErrorString(err) << "("<<err<< ") at "<<file<<":"<<line << std::endl;
    exit (1);
}