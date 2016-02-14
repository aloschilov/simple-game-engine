// OpenGL Graphics includes
#include <GL/glew.h>
#if defined (WIN32)
#include <GL/wglew.h>
#endif
#if defined(__APPLE__) || defined(__MACOSX)
#pragma clang diagnostic ignored "-Wdeprecated-declarations"
#include <GLUT/glut.h>
#ifndef glutCloseFunc
#define glutCloseFunc glutWMCloseFunc
#endif
#else
#include <GL/freeglut.h>
#endif

#include <iostream>
#include <math.h>
#include <cuda_runtime_api.h>

#include "render_particles.h"
#include "helper_timer.h"
#include "particle_system.h"
#include "generated_constants.h"
#include "core_engine.h"

float timestep = 0.001f;

const uint width = 640, height = 480;

// view params
int ox, oy;
int buttonState = 0;
float camera_trans[] = {0, 0, -3};
float camera_rot[]   = {0, 0, 0};
float camera_trans_lag[] = {0, 0, -3};
float camera_rot_lag[] = {0, 0, 0};
const float inertia = 0.1f;
ParticleRenderer::DisplayMode displayMode = ParticleRenderer::PARTICLE_SPHERES;

ParticleSystem *psystem = 0;

// fps
static int fpsCount = 0;
static int fpsLimit = 1;
StopWatchInterface *timer = NULL;

ParticleRenderer *renderer = 0;

int mode = 0;
enum { M_VIEW = 0, M_MOVE };

float modelView[16];

GLuint VBO = 0;

unsigned int frameCount = 0;

// initialize OpenGL
void initGL(int *argc, char **argv)
{
    glutInit(argc, argv);
    glutInitDisplayMode(GLUT_RGB | GLUT_DEPTH | GLUT_DOUBLE);
    glutInitWindowSize(width, height);
    glutCreateWindow("CUDA Particles");

    glewInit();

    if (!glewIsSupported("GL_VERSION_2_0 GL_VERSION_1_5 GL_ARB_multitexture GL_ARB_vertex_buffer_object"))
    {
        fprintf(stderr, "Required OpenGL extensions missing.");
        exit(EXIT_FAILURE);
    }

#if defined (WIN32)

    if (wglewIsSupported("WGL_EXT_swap_control"))
    {
        // disable vertical sync
        wglSwapIntervalEXT(0);
    }

#endif

    glEnable(GL_DEPTH_TEST);
    glClearColor(0.25, 0.25, 0.25, 1.0);

    glutReportErrors();
}

void initParticleSystem()
{
    psystem = new ParticleSystem();
    //psystem->reset();

    renderer = new ParticleRenderer;
    //renderer->setParticleRadius(psystem->getParticleRadius());
    renderer->setColorBuffer(psystem->getColorBuffer());

    sdkCreateTimer(&timer);
}

void computeFPS()
{
    frameCount++;
    fpsCount++;

    if (fpsCount == fpsLimit)
    {
        char fps[256];
        float ifps = 1.f / (sdkGetAverageTimerValue(&timer) / 1000.f);
        sprintf(fps, "CUDA Particles (%d particles): %3.1f fps", NUMBER_OF_MATTERS, ifps);

        glutSetWindowTitle(fps);
        fpsCount = 0;

        fpsLimit = (int)MAX(ifps, 1.f);
        sdkResetTimer(&timer);
    }
}

void display()
{
    sdkStartTimer(&timer);

    psystem->update(timestep);

    if(renderer)
    {
        renderer->setVertexBuffer(psystem->getCurrentReadBuffer(), NUMBER_OF_MATTERS);
    }

    // render
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    // view transform
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

    for (int c = 0; c < 3; ++c)
    {
        camera_trans_lag[c] += (camera_trans[c] - camera_trans_lag[c]) * inertia;
        camera_rot_lag[c] += (camera_rot[c] - camera_rot_lag[c]) * inertia;
    }

    glTranslatef(camera_trans_lag[0], camera_trans_lag[1], camera_trans_lag[2]);
    glRotatef(camera_rot_lag[0], 1.0, 0.0, 0.0);
    glRotatef(camera_rot_lag[1], 0.0, 1.0, 0.0);

    glGetFloatv(GL_MODELVIEW_MATRIX, modelView);

    glColor3f(1.0, 1.0, 1.0);
    glutWireCube(2.0);

    if (renderer)
    {
        renderer->display(displayMode);
    }

    sdkStopTimer(&timer);

    glutSwapBuffers();
    glutReportErrors();

    computeFPS();
}

void reshape(int w, int h)
{
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    gluPerspective(60.0, (float) w / (float) h, 0.1, 100.0);

    glMatrixMode(GL_MODELVIEW);
    glViewport(0, 0, w, h);

    if (renderer)
    {
        renderer->setWindowSize(w, h);
        renderer->setFOV(60.0);
    }
}

void mouse(int button, int state, int x, int y)
{
    int mods;

    if (state == GLUT_DOWN)
    {
        buttonState |= 1<<button;
    }
    else if (state == GLUT_UP)
    {
        buttonState = 0;
    }

    mods = glutGetModifiers();

    if (mods & GLUT_ACTIVE_SHIFT)
    {
        buttonState = 2;
    }
    else if (mods & GLUT_ACTIVE_CTRL)
    {
        buttonState = 3;
    }

    ox = x;
    oy = y;

//    demoMode = false;
//    idleCounter = 0;

    glutPostRedisplay();
}

void motion(int x, int y)
{
    float dx, dy;
    dx = (float)(x - ox);
    dy = (float)(y - oy);

    switch (mode)
    {
        case M_VIEW:
            if (buttonState == 3)
            {
                // left+middle = zoom
                camera_trans[2] += (dy / 100.0f) * 0.5f * fabs(camera_trans[2]);
            }
            else if (buttonState & 2)
            {
                // middle = translate
                camera_trans[0] += dx / 100.0f;
                camera_trans[1] -= dy / 100.0f;
            }
            else if (buttonState & 1)
            {
                // left = rotate
                camera_rot[0] += dy / 5.0f;
                camera_rot[1] += dx / 5.0f;
            }

            break;
    }

    ox = x;
    oy = y;

//    demoMode = false;
//    idleCounter = 0;

    glutPostRedisplay();
}

// commented out to remove unused parameter warnings in Linux
void key(unsigned char key, int /*x*/, int /*y*/)
{
    switch (key)
    {
        case '\033':
        case 'q':
#if defined(__APPLE__) || defined(MACOSX)
            exit(EXIT_SUCCESS);
#else
        glutDestroyWindow(glutGetWindow());
                return;
#endif
        case 'v':
            mode = M_VIEW;
            break;

        case 'm':
            mode = M_MOVE;
            break;

        case 'p':
            displayMode = (ParticleRenderer::DisplayMode)
                    ((displayMode + 1) % ParticleRenderer::PARTICLE_NUM_MODES);
            break;
    }

    glutPostRedisplay();
}

void freeVBO()
{
    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glDeleteBuffers(1, &VBO);
}


void cleanup()
{
    sdkDeleteTimer(&timer);

    if (psystem)
    {
        delete psystem;
    }
    // cudaDeviceReset causes the driver to clean up all state. While
    // not mandatory in normal operation, it is good practice.  It is also
    // needed to ensure correct operation when the application is being
    // profiled. Calling cudaDeviceReset causes all profile data to be
    // flushed before the application exits
    cudaDeviceReset();
    return;
}

void checkOpenGLerror()
{
    GLenum errCode;
    if((errCode=glGetError()) != GL_NO_ERROR)
        std::cout << "OpenGl error! - " << gluErrorString(errCode);
}

float4 positions[4] = {
        {0.1, 0.2, 0.3, 1},
        {0.4, 0.5, 0.6, 1},
        {0.7, 0.8, 0.9, 1},
        {1.0, 1.1, 1.2, 1}
};

void initVBO()
{
    glGenBuffers(1, &VBO);
    glBindBuffer(GL_ARRAY_BUFFER, VBO);

    glBufferData(GL_ARRAY_BUFFER, 4*4*sizeof(float), positions, GL_STATIC_DRAW);
}

void idle(void)
{
//    if ((idleCounter++ > idleDelay) && (demoMode==false))
//    {
//        demoMode = true;
//        printf("Entering demo mode\n");
//    }
//
//    if (demoMode)
//    {
//        camera_rot[1] += 0.1f;
//
//        if (demoCounter++ > 1000)
//        {
//            ballr = 10 + (rand() % 10);
//            addSphere();
//            demoCounter = 0;
//        }
//    }

    glutPostRedisplay();
}

int main(int argc, char **argv)
{
    initGL(&argc, argv);
    cudaGLInit(argc, argv);

    initParticleSystem();
    renderer = new ParticleRenderer();
//    initVBO();

    glutDisplayFunc(display);
    glutReshapeFunc(reshape);
    glutMouseFunc(mouse);
    glutMotionFunc(motion);
    glutKeyboardFunc(key);
//glutSpecialFunc(special);
    glutIdleFunc(idle);

    glutCloseFunc(cleanup);

    glutMainLoop();

    if (psystem)
    {
        delete psystem;
    }

//    freeVBO();
    delete renderer;
}
