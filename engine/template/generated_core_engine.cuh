#ifndef __GENERATED_CORE_ENGINE__
#define __GENERATED_CORE_ENGINE__

#include "generated_constants.h"

typedef float (*op_func) (float, float *, float *, float *);

{positions_functions}

{positions_functions_list}

{atoms_quantities_functions}

{atoms_quantities_functions_list}


void initialize(float *p_x, float *p_y, float *nu)
{{

{positions_initialization}

{atoms_quantities_initialization}

}}

#endif // __GENERATED_CORE_ENGINE__
