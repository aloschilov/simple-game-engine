#ifndef __PARTICLESYSTEM_H__
#define __PARTICLESYSTEM_H__

#include <helper_functions.h>
#include <vector_functions.h>
#include <sys/types.h>

// Particle system class
class ParticleSystem
{
public:
    ParticleSystem();
    ~ParticleSystem();

    void update(float deltaTime);
    void reset();

    unsigned int getCurrentReadBuffer() const
    {
        return m_posVbo;
    }
    unsigned int getColorBuffer()       const
    {
        return m_colorVBO;
    }

protected: // methods
    uint createVBO(uint size);

    void _initialize();
    void _finalize();

protected: // data
    bool m_bInitialized;

    // CPU data

    float *p_x;
    float *p_y;
    float *nu;

    // GPU data

    float * d_p_x, * d_p_y, * d_nu, *d_p_x_out, *d_p_y_out, * d_nu_out;

    uint   m_posVbo;            // vertex buffer object for particle positions
    uint   m_colorVBO;          // vertex buffer object for colors

    struct cudaGraphicsResource *m_cuda_posvbo_resource; // handles OpenGL-CUDA exchange
    struct cudaGraphicsResource *m_cuda_colorvbo_resource; // handles OpenGL-CUDA exchange

    StopWatchInterface *m_timer;

    //    uint m_solverIterations;
};

#endif // __PARTICLESYSTEM_H__
