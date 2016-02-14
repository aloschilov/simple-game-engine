#ifndef __CORE_ENGINE__
#define __CORE_ENGINE__

// This method makes initialization on CPU
void initialize(float *p_x, float *p_y, float *nu);

// This method brings the system to its next state
void integrate(float delta_t,
               float4 *d_xyzw_p,
               float *&d_nu,
               float *&d_nu_out,
               float *&d_p_x,
               float *&d_p_y,
               float *&d_p_x_out,
               float *&d_p_y_out);

void free_arrays(float * &p_x,
                 float * &p_y,
                 float * &nu,
                 float * &d_p_x,
                 float * &d_p_y,
                 float * &d_nu,
                 float * &d_p_x_out,
                 float * &d_p_y_out,
                 float * &d_nu_out);

void allocate_arrays(float * &p_x,
                     float * &p_y,
                     float * &nu,
                     float * &d_p_x,
                     float * &d_p_y,
                     float * &d_nu,
                     float * &d_p_x_out,
                     float * &d_p_y_out,
                     float * &d_nu_out);

void upload_host_arrays(float *d_p_x,
			float *d_p_y,
			float *d_nu,
			float *p_x,
			float *p_y,
			float *nu);
  
void join_position_arrays(float4 *d_xyzw_p,
			  float *d_p_x,
			  float *d_p_y);

void cudaGLInit(int argc, char **argv);

void registerGLBufferObject(uint vbo, struct cudaGraphicsResource **cuda_vbo_resource);

void unregisterGLBufferObject(struct cudaGraphicsResource *cuda_vbo_resource);

void *mapGLBufferObject(struct cudaGraphicsResource **cuda_vbo_resource);

void unmapGLBufferObject(struct cudaGraphicsResource *cuda_vbo_resource);

#endif //__CORE_ENGINE__
