#include "particle_system.h"

#include <GL/glew.h>

#include "generated_constants.h"
#include "core_engine.h"

ParticleSystem::ParticleSystem() :
        m_bInitialized(false)
{
    _initialize();
}

ParticleSystem::~ParticleSystem()
{
    _finalize();
}

uint
ParticleSystem::createVBO(uint size)
{
    GLuint vbo;
    glGenBuffers(1, &vbo);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferData(GL_ARRAY_BUFFER, size, 0, GL_DYNAMIC_DRAW);
    glBindBuffer(GL_ARRAY_BUFFER, 0);
    return vbo;
}

inline float lerp(float a, float b, float t)
{
    return a + t*(b-a);
}

// create a color ramp
void colorRamp(float t, float *r)
{
    const int ncolors = 7;
    float c[ncolors][3] =
            {
                    { 1.0, 0.0, 0.0, },
                    { 1.0, 0.5, 0.0, },
                    { 1.0, 1.0, 0.0, },
                    { 0.0, 1.0, 0.0, },
                    { 0.0, 1.0, 1.0, },
                    { 0.0, 0.0, 1.0, },
                    { 1.0, 0.0, 1.0, },
            };
    t = t * (ncolors-1);
    int i = (int) t;
    float u = (float) (t - floor(t));
    r[0] = lerp(c[i][0], c[i+1][0], u);
    r[1] = lerp(c[i][1], c[i+1][1], u);
    r[2] = lerp(c[i][2], c[i+1][2], u);
}

void
ParticleSystem::_initialize()
{
    assert(!m_bInitialized);

    allocate_arrays(p_x, p_y, nu, d_p_x, d_p_y, d_nu, d_p_x_out, d_p_y_out, d_nu_out);
    
    initialize(p_x, p_y, nu);

    // allocate VBO

    unsigned int memSize = (unsigned int) (sizeof(float) * 4 * NUMBER_OF_MATTERS);

    m_posVbo = createVBO(memSize);
    registerGLBufferObject(m_posVbo, &m_cuda_posvbo_resource);

    m_colorVBO = createVBO(NUMBER_OF_MATTERS * 4 * sizeof(float));
    registerGLBufferObject(m_colorVBO, &m_cuda_colorvbo_resource);

    // fill color buffer
    glBindBufferARB(GL_ARRAY_BUFFER, m_colorVBO);
    float *data = (float *) glMapBufferARB(GL_ARRAY_BUFFER, GL_WRITE_ONLY);
    float *ptr = data;

    for (uint i=0; i < NUMBER_OF_MATTERS; i++)
    {
        float t = i / (float) NUMBER_OF_MATTERS;
#if 0
            *ptr++ = rand() / (float) RAND_MAX;
            *ptr++ = rand() / (float) RAND_MAX;
            *ptr++ = rand() / (float) RAND_MAX;
#else
            colorRamp(t, ptr);
            ptr+=3;
#endif
            *ptr++ = 1.0f;
        }

    glUnmapBufferARB(GL_ARRAY_BUFFER);

    sdkCreateTimer(&m_timer);

    reset();

    m_bInitialized = true;
}

void
ParticleSystem::_finalize()
{
    assert(m_bInitialized);

    free_arrays(p_x, p_y, nu, d_p_x, d_p_y, d_nu, d_p_x_out, d_p_y_out, d_nu_out);

    unregisterGLBufferObject(m_cuda_colorvbo_resource);
    unregisterGLBufferObject(m_cuda_posvbo_resource);
    glDeleteBuffers(1, (const GLuint *)&m_posVbo);
    glDeleteBuffers(1, (const GLuint *)&m_colorVBO);
}

void
ParticleSystem::update(float deltaTime)
{
    assert(m_bInitialized);

    float *d_xyzw_position_array;

    d_xyzw_position_array = (float *) mapGLBufferObject(&m_cuda_posvbo_resource);

    integrate(deltaTime, (float4 *) d_xyzw_position_array, d_nu, d_nu_out, d_p_x, d_p_y, d_p_x_out, d_p_y_out);

    unmapGLBufferObject(m_cuda_posvbo_resource);
}

void
ParticleSystem::reset()
{
  upload_host_arrays(d_p_x, d_p_y, d_nu, p_x, p_y, nu);

  float *d_xyzw_position_array;

  d_xyzw_position_array = (float *) mapGLBufferObject(&m_cuda_posvbo_resource);

  join_position_arrays((float4 *)d_xyzw_position_array, d_p_x, d_p_y);

  unmapGLBufferObject(m_cuda_posvbo_resource);
}
