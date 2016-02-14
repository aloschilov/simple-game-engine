cmake_minimum_required(VERSION 2.8)
project (particles-rendering)

include_directories(.)

find_package(OpenGL REQUIRED)
find_package(GLUT REQUIRED)
find_package(CUDA REQUIRED)

include_directories(${CUDA_INCLUDE_DIRS})

set(CCFILES
        main.cpp
        shaders.cpp
        render_particles.cpp
        particle_system.cpp
        )

set(HFILES
        shaders.h
        render_particles.h
        particle_system.h
        core_engine.h
        generated_constants.h)

set(CUFILES
        core_engine.cu)

set(CUHFILES
        generated_core_engine.cuh)

source_group("CUDA Header Files" FILES ${CUHFILES})

CUDA_ADD_EXECUTABLE(particles-rendering ${CCFILES} ${HFILES} ${CUHFILES} ${CUFILES})
target_link_libraries(particles-rendering ${CMAKE_SOURCE_DIR}/libGLEW.a ${OPENGL_LIBRARIES} ${GLUT_LIBRARY})